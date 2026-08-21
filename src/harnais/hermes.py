"""Invocation d'Hermes en un coup : `hermes -z` (PRD 2 §3, décision D1).

Une décision de jeu = une invocation, un prompt en entrée, la réponse finale
seule sur stdout. C'est le **seul** point de contact entre l'arène et le
modèle, et il est identique pour les trois conditions mémoire : si le harnais
différait d'une condition à l'autre, l'expérience mesurerait « harnais ×
mémoire » au lieu de « mémoire » (spec §0).

Options posées à chaque appel :

- `HERMES_HOME` = le store isolé du run (§6), et **aucune** autre variable
  `HERMES_*` héritée du shell : une variable oubliée (`HERMES_MODEL`,
  `HERMES_KANBAN_*`…) rerouterait silencieusement le run ;
- `-t <toolset>` — `context_engine` (vide) pendant les manches, `memory` à la
  seule réflexion AE ;
- `-m` / `--provider` — modèle figé, identique aux 27 runs (`--provider` sans
  `--model` est refusé par Hermes : les deux vont ensemble) ;
- `--usage-file` — rapport JSON par appel (tokens entrée/sortie, modèle
  réellement servi, coût estimé), écrit même en cas d'échec. C'est la source
  des champs `tokens` des logs (PRD 4 §2) et du suivi de budget.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Protocol

from .stores import ParametresModele, Store, TOOLSET_SANS_OUTIL

#: Timeout d'une invocation. Généreux : une manche est un aller-retour court,
#: mais le premier appel d'un store paie l'initialisation d'Hermes.
TIMEOUT_DEFAUT = 180

#: Relances sur échec (réseau, timeout, sortie vide). Au-delà, la manche est
#: marquée `erreur_harnais` et rejouée par l'arbitre avec la même donne —
#: jamais silencieusement sautée (PRD 2 §3).
RELANCES_DEFAUT = 2

#: Échecs de fournisseur qu'Hermes rend **sur stdout avec un code retour 0**.
#: Découvert le 2026-08-21 en basculant sur un modèle payant sans crédits :
#: `hermes -z` a imprimé « API call failed after 3 retries: HTTP 404… » et
#: s'est terminé normalement. Sans ce filet, l'arène prend le message d'erreur
#: pour une réponse du modèle : le parsing échoue, l'action passive est
#: imposée, et la série se remplit de manches `action_par_defaut` **loguées
#: comme des données**. Un run entier peut ainsi passer pour valide.
#:
#: Les motifs sont ancrés en tête de sortie : le modèle, lui, ne commence
#: jamais sa réponse par « API call failed ».
_MOTIFS_ECHEC_FOURNISSEUR = (
    re.compile(r"^\s*API call failed", re.IGNORECASE),
    re.compile(r"^\s*(?:Error|Erreur)\s*:\s*HTTP\s+\d{3}", re.IGNORECASE),
    re.compile(r"requires available credits", re.IGNORECASE),
    re.compile(r"^\s*Rate limit(?:ed| exceeded)", re.IGNORECASE),
)


def echec_fournisseur(texte: str) -> str | None:
    """Rend le message d'erreur si la sortie est un échec de fournisseur déguisé."""
    for motif in _MOTIFS_ECHEC_FOURNISSEUR:
        if motif.search(texte or ""):
            return (texte or "").strip().splitlines()[0][:300]
    return None


@dataclass(frozen=True)
class Reponse:
    """Résultat d'une invocation, tel qu'il part dans les logs."""

    texte: str
    code_retour: int
    latence_ms: int
    tentatives: int
    tokens_entree: int | None = None
    tokens_sortie: int | None = None
    #: Part de `tokens_sortie` consommée par la chaîne de pensée interne du
    #: modèle — facturée, jamais rendue sur stdout, donc jamais loguée en
    #: texte. Mesurée à 87–94 % de la sortie au pilote du 2026-08-21 : c'est
    #: la quantité qui commande le coût **et** la durée de la campagne, et
    #: elle serait invisible sans ce champ.
    tokens_raisonnement: int | None = None
    #: Entrée servie depuis le cache de préfixe du fournisseur, facturée ~10x
    #: moins cher. Une série d'arène rejoue 200 fois le même préfixe
    #: `[RÈGLES] + [SLOT]` : c'est le principal levier de coût de la campagne,
    #: et il serait invisible sans ce champ.
    tokens_cache_lus: int | None = None
    tokens_cache_ecrits: int | None = None
    #: Appels réellement émis par la boucle d'agent pour cette invocation.
    #: Vaut 1 en configuration d'arène ; au-delà, la boucle aurait rebouclé
    #: et la manche coûterait plus que prévu.
    appels_api: int | None = None
    modele: str | None = None
    cout_usd: float | None = None
    erreur: str | None = None

    @property
    def ok(self) -> bool:
        return self.erreur is None and bool(self.texte.strip())

    def tokens(self) -> Mapping[str, int | None]:
        return {
            "in": self.tokens_entree,
            "out": self.tokens_sortie,
            "raisonnement": self.tokens_raisonnement,
            "cache_lus": self.tokens_cache_lus,
        }


class Invocateur(Protocol):
    """Contrat minimal attendu par le harnais.

    Les tests substituent un invocateur en mémoire : rien dans
    `conditions.py` ne suppose un sous-processus, et la suite tourne sans le
    moindre appel API.
    """

    def __call__(self, prompt: str, toolset: str = TOOLSET_SANS_OUTIL) -> Reponse: ...


def _executable(chemin: str | None) -> str:
    if chemin:
        return chemin
    trouve = shutil.which("hermes")
    if not trouve:
        raise FileNotFoundError(
            "exécutable `hermes` introuvable sur le PATH — "
            "passer `executable=` explicitement"
        )
    return trouve


def _environnement(store: Store) -> Mapping[str, str]:
    """Env du sous-processus : celui du shell, purgé de tout `HERMES_*`."""
    env = {cle: val for cle, val in os.environ.items() if not cle.startswith("HERMES_")}
    env.update(store.variables_env())
    return env


#: Répertoire de travail neutre, créé sous le store et laissé **vide**.
DOSSIER_TRAVAIL = "cwd-neutre"


def repertoire_neutre(store: Store) -> Path:
    """Répertoire de travail servi à Hermes — vide, et il doit le rester.

    ⚠️ Faille de validité découverte le 2026-08-21, la plus grave du projet.
    Hermes explore le répertoire courant à la recherche de consignes d'agent
    (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`…) et **les injecte dans son
    prompt système**. Or l'arène était lancée depuis le dépôt : `CLAUDE.md`
    y décrit le jeu réel, la constante d'équilibre, et l'exploitation de
    chaque bot, nommément. Mesuré par `hermes prompt-size` : 11 633 octets de
    consignes du dépôt dans le prompt système, contre 0 depuis un répertoire
    vide.

    Autrement dit, l'agent recevait le corrigé de l'expérience à chaque
    manche. Tout ce qui a été joué avant ce correctif est à rejouer, et les
    « reconnaissances du jeu » observées ne prouvaient rien : il lisait.

    Le répertoire vit sous le store du run, donc il est isolé comme lui, et
    l'arbitre ne doit jamais y écrire.
    """
    chemin = store.chemin / DOSSIER_TRAVAIL
    chemin.mkdir(parents=True, exist_ok=True)
    return chemin


@dataclass
class InvocateurHermes:
    """Invocateur réel, lié au store d'un run."""

    store: Store
    parametres: ParametresModele = field(default_factory=ParametresModele)
    executable: str | None = None
    timeout: int = TIMEOUT_DEFAUT
    relances: int = RELANCES_DEFAUT

    def __call__(self, prompt: str, toolset: str = TOOLSET_SANS_OUTIL) -> Reponse:
        commande_base = [
            _executable(self.executable),
            "-z",
            prompt,
            "-t",
            toolset,
            "-m",
            self.parametres.modele,
            "--provider",
            self.parametres.fournisseur,
        ]
        env = _environnement(self.store)
        travail = repertoire_neutre(self.store)
        derniere: Reponse | None = None

        for tentative in range(1, self.relances + 2):
            with tempfile.TemporaryDirectory(prefix="arene-usage-") as tmp:
                rapport = Path(tmp) / "usage.json"
                commande = commande_base + ["--usage-file", str(rapport)]
                reponse = self._executer(commande, env, rapport, tentative, travail)
            if reponse.ok:
                return reponse
            derniere = reponse

        assert derniere is not None  # la boucle tourne au moins une fois
        return derniere

    def _executer(
        self,
        commande: list[str],
        env: Mapping[str, str],
        rapport: Path,
        tentative: int,
        travail: Path,
    ) -> Reponse:
        debut = time.monotonic()
        try:
            acheve = subprocess.run(
                commande,
                env=dict(env),
                cwd=str(travail),  # jamais le dépôt : cf. `repertoire_neutre`
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired:
            return Reponse(
                texte="",
                code_retour=-1,
                latence_ms=int((time.monotonic() - debut) * 1000),
                tentatives=tentative,
                erreur=f"timeout après {self.timeout} s",
                **_usage(rapport),
            )
        except OSError as exc:  # exécutable absent, droits, etc.
            return Reponse(
                texte="",
                code_retour=-1,
                latence_ms=int((time.monotonic() - debut) * 1000),
                tentatives=tentative,
                erreur=f"lancement impossible : {exc}",
            )

        latence = int((time.monotonic() - debut) * 1000)
        texte = acheve.stdout or ""
        erreur = None
        if acheve.returncode != 0:
            erreur = f"code retour {acheve.returncode} : {(acheve.stderr or '').strip()[:400]}"
        elif not texte.strip():
            erreur = "sortie vide"
        elif (message := echec_fournisseur(texte)) is not None:
            # Code retour 0, sortie non vide, et pourtant rien du modèle.
            erreur = f"échec fournisseur rendu sur stdout : {message}"

        return Reponse(
            texte=texte,
            code_retour=acheve.returncode,
            latence_ms=latence,
            tentatives=tentative,
            erreur=erreur,
            **_usage(rapport),
        )


def _usage(rapport: Path) -> Mapping[str, object]:
    """Lit le rapport `--usage-file`. Absent ou illisible → champs à `None`.

    Best-effort assumé : un rapport de coût manquant ne doit jamais faire
    échouer une manche par ailleurs valide, il laisse juste un trou visible
    dans les logs.
    """
    vide: dict[str, object] = {
        "tokens_entree": None,
        "tokens_sortie": None,
        "tokens_raisonnement": None,
        "tokens_cache_lus": None,
        "tokens_cache_ecrits": None,
        "appels_api": None,
        "modele": None,
        "cout_usd": None,
    }
    try:
        donnees = json.loads(rapport.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return vide
    return {
        "tokens_entree": donnees.get("input_tokens"),
        "tokens_sortie": donnees.get("output_tokens"),
        "tokens_raisonnement": donnees.get("reasoning_tokens"),
        "tokens_cache_lus": donnees.get("cache_read_tokens"),
        "tokens_cache_ecrits": donnees.get("cache_write_tokens"),
        "appels_api": donnees.get("api_calls"),
        "modele": donnees.get("model"),
        "cout_usd": donnees.get("estimated_cost_usd"),
    }


__all__ = [
    "RELANCES_DEFAUT",
    "TIMEOUT_DEFAUT",
    "Invocateur",
    "InvocateurHermes",
    "Reponse",
]
