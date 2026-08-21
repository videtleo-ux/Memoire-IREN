"""Stores Hermes isolés par run, et canari d'isolation (PRD 2 §3 et §6, D3).

Le piège de la spec §7 : `MEMORY.md` vit sous `~/.hermes/memories/`. Deux runs
lancés en parallèle sur la même machine s'écrasent silencieusement la mémoire
l'un l'autre — et un run contaminé ne se voit pas dans les résultats, il se
lit comme de l'adaptation. D'où : un `HERMES_HOME` par run, et une
**vérification** de l'isolation, jamais une supposition.

Ce module fabrique ce store : une arborescence minimale (`memories/`,
`config.yaml`, l'authentification recopiée) dont la config neutralise tous les
canaux d'apprentissage annexes repérés à l'audit d'environnement — outils,
`USER.md`, revue d'auto-amélioration d'arrière-plan, création de skills,
recherche dans les sessions passées.

Les clés de config posées ici ont été relevées **dans le code d'Hermes**, pas
supposées : `memory.memory_enabled` / `memory.user_profile_enabled` /
`memory.nudge_interval` (agent/agent_init.py), `skills.creation_nudge_interval`
(idem), la revue d'arrière-plan étant conditionnée à `nudge_interval > 0` et à
la présence de l'outil (agent/turn_context.py, agent/turn_finalizer.py). Le
canari les vérifie ensuite sur pièces.
"""

from __future__ import annotations

import shutil
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .gel import DOSSIER_MEMOIRE, FICHIER_NOTES, dossier_memoire, lire_notes

#: Toolset servi pendant les manches. `context_engine` est un toolset
#: *légitime* d'Hermes qui ne contient aucun outil tant qu'aucun greffon de
#: moteur de contexte n'en enregistre — c'est le « zéro outil » propre. Le
#: mode `-z` refuse une liste de toolsets vide ou inconnue
#: (`hermes_cli/oneshot.py`), passer une chaîne bidon n'est donc pas une
#: option. Le canari vérifie qu'aucun outil n'a effectivement été exposé.
TOOLSET_SANS_OUTIL = "context_engine"

#: Toolset servi à la seule étape de réflexion (condition AE) : l'agent doit
#: pouvoir écrire ses notes avec son outil natif.
TOOLSET_MEMOIRE = "memory"

#: Modèle de campagne, arrêté au pilote du 2026-08-21 (cf. `CONTEXT.md`).
#:
#: `tencent/hy3:free` a servi à déboguer le harnais à coût nul, mais il
#: **ignore le contrôle d'effort de raisonnement** : ~4 000 tokens de chaîne
#: de pensée par manche, non réductibles, invisibles dans les journaux. Luna
#: l'honore (`none` … `max`), coûte 0,20 $/1,20 $ par million, et reste à
#: 2-3 points de la tête de la famille GPT-5.6 sur les tâches agentiques.
#:
#: ⚠️ Ce défaut est **payant**. Le modèle gratuit reste accessible pour la
#: mise au point : `--modele tencent/hy3:free`.
MODELE_DEFAUT = "openai/gpt-5.6-luna"
MODELE_GRATUIT = "tencent/hy3:free"
FOURNISSEUR_DEFAUT = "nous"
BASE_URL_DEFAUT = "https://inference-api.nousresearch.com/v1"

#: Limite de caractères de `MEMORY.md` (spec §6 : cap dur, pas de compaction
#: automatique, l'agent doit élaguer lui-même).
LIMITE_NOTES = 2200


@dataclass(frozen=True)
class ParametresModele:
    """Paramètres d'inférence figés, identiques aux 27 runs et logués.

    L'effort de raisonnement est **découplé entre la manche et la frontière**,
    et ce n'est pas un réglage de confort. Le mini-run du 2026-08-21 a montré
    que 94 % des tokens de sortie sont du raisonnement interne jamais logué,
    et que la latence suit le volume généré : c'est le seul levier sérieux sur
    le coût **et** sur la durée de la campagne. Or les deux moments n'ont pas
    les mêmes besoins :

    - une **manche** demande une décision binaire sur un arbre de profondeur
      3, répétée K fois — l'essentiel du raisonnement interne y est du gras ;
    - une **frontière** demande de synthétiser 200 manches en huit à quinze
      notes, une fois par série. C'est le geste que l'expérience mesure, et
      il coûte 1/200ᵉ du budget : il n'y a aucune raison de l'économiser.

    Le découpage ne casse pas la comparabilité inter-conditions : SM et ICL
    n'ont pas d'étape de réflexion, et les trois conditions jouent leurs
    manches au même niveau. Les deux valeurs sont figées avant la campagne et
    loguées à chaque appel.
    """

    modele: str = MODELE_DEFAUT
    fournisseur: str = FOURNISSEUR_DEFAUT
    base_url: str = BASE_URL_DEFAUT
    #: Niveau servi aux K manches d'une série. Mesuré au pilote du
    #: 2026-08-21 sur 200 manches à donnes identiques : `low` et `medium`
    #: donnent le même volume de sortie (445 vs 427 tokens), la même latence
    #: et le même coût sur Luna. `medium` jouant marginalement mieux
    #: (écart 0,227 vs 0,248), il n'y a aucune raison d'économiser ici — et
    #: cela retire l'objection « le modèle a été bridé ».
    reasoning_effort: str = "medium"
    #: Niveau servi à l'unique réflexion de frontière (condition AE).
    reasoning_reflexion: str = "medium"

    def pour_logs(self) -> Mapping[str, str]:
        return {
            "modele": self.modele,
            "fournisseur": self.fournisseur,
            "reasoning_effort": self.reasoning_effort,
            "reasoning_reflexion": self.reasoning_reflexion,
        }


# --------------------------------------------------------------------------
# Émission YAML (sous-ensemble suffisant)
# --------------------------------------------------------------------------


def _yaml(valeur: Any, indent: int = 0) -> str:
    """Sérialise dicts / listes / scalaires en YAML.

    Sous-ensemble volontairement minuscule : le dépôt est sans dépendance
    (PRD 1) et la config d'arène n'a besoin ni d'ancres, ni de multi-lignes,
    ni de types exotiques. On n'a jamais à *relire* du YAML : la config est
    régénérée en entier à chaque écriture.
    """
    marge = "  " * indent
    if isinstance(valeur, Mapping):
        if not valeur:
            return "{}"
        lignes = []
        for cle, sous in valeur.items():
            rendu = _yaml(sous, indent + 1)
            if isinstance(sous, (Mapping, list, tuple)) and sous:
                lignes.append(f"{marge}{cle}:\n{rendu}")
            else:
                lignes.append(f"{marge}{cle}: {rendu}")
        return "\n".join(lignes)
    if isinstance(valeur, (list, tuple)):
        if not valeur:
            return "[]"
        return "\n".join(f"{marge}- {_yaml(v, 0)}" for v in valeur)
    if isinstance(valeur, bool):
        return "true" if valeur else "false"
    if valeur is None:
        return "null"
    if isinstance(valeur, (int, float)):
        return str(valeur)
    return f'"{str(valeur)}"'


def config_arene(
    parametres: ParametresModele = ParametresModele(),
    memoire_native: bool = False,
    max_turns: int = 2,
    reasoning: str | None = None,
) -> Mapping[str, Any]:
    """Config du store d'un run.

    Deux choses basculent au cours d'un run, et seulement à la frontière de
    série en condition AE : `memoire_native` (fausse pendant les manches pour
    les trois conditions — le slot est posé par l'arbitre dans le prompt,
    PRD 2 §5.3, c'est ce qui rend les prompts octet-pour-octet comparables) et
    `reasoning`, qui laisse la réflexion travailler à un autre niveau que les
    manches (cf. `ParametresModele`). Hors frontière, les deux reviennent à
    leur valeur de manche.
    """
    return {
        "model": {
            "default": parametres.modele,
            "provider": parametres.fournisseur,
            "base_url": parametres.base_url,
        },
        "agent": {
            "max_turns": max_turns,
            "verbose": False,
            "reasoning_effort": reasoning or parametres.reasoning_effort,
        },
        "memory": {
            "memory_enabled": memoire_native,
            "user_profile_enabled": False,  # USER.md : canal annexe, neutralisé
            "memory_char_limit": LIMITE_NOTES,
            "user_char_limit": LIMITE_NOTES,
            # 0 = aucune revue d'auto-amélioration d'arrière-plan (piège n°1 de
            # l'audit : elle écrit la mémoire après un tour, hors de tout gel).
            "nudge_interval": 0,
            "flush_min_turns": 0,
        },
        "skills": {"creation_nudge_interval": 0},  # pas de skills auto-créées
        "compression": {"enabled": False},  # contexte d'une manche : minuscule
        "streaming": {"enabled": False},
        "telemetry": {"shared_metrics": {"enabled": False}},
        "session_reset": {"mode": "none"},
        "display": {"streaming": False, "show_reasoning": False},
        # Le toolset de plateforme est de toute façon écrasé par `-t` à chaque
        # invocation ; le poser ici ferme la porte en cas d'oubli.
        "platform_toolsets": {"cli": [TOOLSET_SANS_OUTIL]},
    }


# --------------------------------------------------------------------------
# Création d'un store de run
# --------------------------------------------------------------------------

#: Fichiers d'authentification recopiés depuis le home global de la machine.
#: Rien d'autre n'est cloné : ni `state.db` (sessions passées), ni `skills/`,
#: ni `SOUL.md` — chaque run part d'une mémoire réellement vierge (spec §6 :
#: reset complet entre runs).
FICHIERS_AUTH = ("auth.json",)


@dataclass(frozen=True)
class Store:
    """Un `HERMES_HOME` dédié à un run."""

    chemin: Path
    parametres: ParametresModele = field(default_factory=ParametresModele)

    @property
    def notes(self) -> Path:
        return dossier_memoire(self.chemin) / FICHIER_NOTES

    @property
    def config(self) -> Path:
        return self.chemin / "config.yaml"

    def ecrire_config(
        self,
        memoire_native: bool = False,
        max_turns: int = 2,
        reasoning: str | None = None,
    ) -> None:
        contenu = _yaml(config_arene(self.parametres, memoire_native, max_turns, reasoning))
        self.config.write_text(contenu + "\n", encoding="utf-8")

    def variables_env(self) -> Mapping[str, str]:
        return {"HERMES_HOME": str(self.chemin)}


def creer_store(
    chemin: Path | str,
    parametres: ParametresModele = ParametresModele(),
    home_source: Path | str | None = None,
    notes_initiales: str = "",
) -> Store:
    """Crée le store isolé d'un run (`M_0` vide par défaut).

    `home_source` est le `HERMES_HOME` global de la machine, d'où l'on recopie
    la seule authentification. Absent → store sans auth : utilisable en test,
    pas pour un vrai run.
    """
    chemin = Path(chemin)
    if chemin.exists() and any(chemin.iterdir()):
        raise ValueError(f"store déjà peuplé, un run part toujours d'un store neuf : {chemin}")
    dossier_memoire(chemin).mkdir(parents=True, exist_ok=True)

    store = Store(chemin=chemin, parametres=parametres)
    store.ecrire_config()
    store.notes.write_text(notes_initiales, encoding="utf-8")

    if home_source is not None:
        for nom in FICHIERS_AUTH:
            origine = Path(home_source) / nom
            if origine.is_file():
                shutil.copy2(origine, chemin / nom)

    return store


# --------------------------------------------------------------------------
# Canari d'isolation (PRD 2 §6)
# --------------------------------------------------------------------------


class EchecCanari(RuntimeError):
    """L'isolation n'est pas prouvée — le run doit être refusé."""


def marqueur_canari(run_id: str) -> str:
    """Marqueur unique, reconnaissable dans n'importe quel `MEMORY.md`."""
    return f"canari-isolation {run_id} {uuid.uuid4().hex[:12]}"


def verifier_isolation(
    store: Store,
    marqueur: str,
    autres_stores: Iterable[Path | str] = (),
    home_global: Path | str | None = None,
) -> None:
    """Vérifie qu'un marqueur écrit dans ce store n'a fui nulle part.

    Trois assertions, dans l'ordre du PRD 2 §6 : le marqueur est (a) présent
    dans le store du run, (b) absent du `HERMES_HOME` global de la machine,
    (c) absent de tout autre store de run actif. Lève `EchecCanari` sinon —
    un run dont l'isolation n'est pas prouvée ne doit pas démarrer.
    """
    if marqueur not in lire_notes(store.chemin):
        raise EchecCanari(
            f"marqueur absent du store du run ({store.notes}) : "
            "l'écriture mémoire n'a pas atterri là où le run la lira"
        )

    suspects: list[Path] = [Path(p) for p in autres_stores if Path(p) != store.chemin]
    if home_global is not None and Path(home_global) != store.chemin:
        suspects.append(Path(home_global))

    for suspect in suspects:
        for fichier in _fichiers_memoire(suspect):
            if marqueur in fichier.read_text(encoding="utf-8", errors="replace"):
                raise EchecCanari(
                    f"marqueur du run retrouvé hors de son store, dans {fichier} : "
                    "les runs ne sont pas isolés"
                )


def _fichiers_memoire(home: Path) -> Sequence[Path]:
    dossier = Path(home) / DOSSIER_MEMOIRE
    if not dossier.is_dir():
        return ()
    return [c for c in sorted(dossier.rglob("*")) if c.is_file()]


__all__ = [
    "BASE_URL_DEFAUT",
    "FICHIERS_AUTH",
    "FOURNISSEUR_DEFAUT",
    "LIMITE_NOTES",
    "MODELE_DEFAUT",
    "TOOLSET_MEMOIRE",
    "TOOLSET_SANS_OUTIL",
    "EchecCanari",
    "ParametresModele",
    "Store",
    "config_arene",
    "creer_store",
    "marqueur_canari",
    "verifier_isolation",
]
