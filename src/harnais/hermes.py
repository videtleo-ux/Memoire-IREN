"""Invocation d'Hermes en un coup : le chemin `-z`, par pilote fichier (D1).

Une décision de jeu = une invocation, un prompt en entrée, la réponse finale
seule sur stdout. C'est le **seul** point de contact entre l'arène et le
modèle, et il est identique pour les trois conditions mémoire : si le harnais
différait d'une condition à l'autre, l'expérience mesurerait « harnais ×
mémoire » au lieu de « mémoire » (spec §0).

⚠️ Transport (audit 2026-08-22, C2) : le prompt ne part **jamais en argv**.
CreateProcess plafonne la ligne de commande Windows à 32 767 caractères, et le
prompt ICL de campagne (3 séries de K = 150 en fenêtre) fait ~51 000 : en
`hermes -z <prompt>`, les 9 runs ICL mourraient en série 3 (`WinError 206`).
L'invocation passe donc par `pilote_oneshot.py`, exécuté avec le python du
venv d'Hermes : le prompt est écrit dans un fichier temporaire (à côté de
`usage.json`, jamais dans `cwd-neutre` qui doit rester vide) et le pilote
appelle `_run_and_exit_oneshot` — la fonction même que l'exécutable
`hermes -z` habille, mêmes nettoyages, mêmes codes retour, même stdout.

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
#: L'audit du 2026-08-22 a relevé dans `agent/conversation_loop.py` **toutes**
#: les formes de `final_response` d'échec que la boucle d'Hermes peut rendre
#: ainsi ; elles sont couvertes une à une ci-dessous. Ce filet textuel est
#: désormais une défense en profondeur : le verdict qui fait foi est celui du
#: rapport `--usage-file` (`_echec_usage`), écrit par Hermes lui-même à chaque
#: appel, y compris en échec. Les motifs restent utiles quand le rapport
#: manque (crash avant écriture, disque plein).
#:
#: Les motifs sont ancrés en tête de sortie quand le texte d'Hermes l'est :
#: le modèle, lui, ne commence jamais sa réponse par « API call failed ».
_MOTIFS_ECHEC_FOURNISSEUR = (
    re.compile(r"^\s*API call failed", re.IGNORECASE),
    re.compile(r"^\s*(?:Error|Erreur)\s*:\s*HTTP\s+\d{3}", re.IGNORECASE),
    re.compile(r"requires available credits", re.IGNORECASE),
    re.compile(r"^\s*Rate limit(?:ed| exceeded)", re.IGNORECASE),
    # Relevés à l'audit du 2026-08-22 (conversation_loop.py, un motif par
    # `final_response` d'échec rendu avec le code retour 0) :
    re.compile(r"^\s*Billing or credits exhausted", re.IGNORECASE),
    re.compile(r"^\s*Invalid API response after", re.IGNORECASE),
    re.compile(r"^\s*Context length exceeded", re.IGNORECASE),
    re.compile(r"^\s*Request payload too large", re.IGNORECASE),
    re.compile(r"^\s*(?:First )?response truncated due to output length", re.IGNORECASE),
    # « ⚠️ **Thinking Budget Exhausted** » : préfixé d'emoji/gras, non ancrable.
    re.compile(r"Thinking Budget Exhausted", re.IGNORECASE),
    re.compile(r"^\s*Model generated invalid tool call", re.IGNORECASE),
    re.compile(r"^\s*Incomplete REASONING_SCRATCHPAD", re.IGNORECASE),
    re.compile(r"^\s*Codex response remained incomplete", re.IGNORECASE),
    # Limite de débit du compte, annoncée avec un délai de reset (campagne du
    # 2026-08-22) : « ⏳ Nous Portal rate limit active — resets in 7m 39s. »
    re.compile(r"rate limit active", re.IGNORECASE),
)

#: Limite de débit **du compte**, distincte d'un échec définitif : Hermes
#: annonce le délai de reset. Rencontrée en campagne avec cinq exécutions en
#: parallèle — elle a arrêté cinq runs de plusieurs heures pour une
#: indisponibilité de sept minutes. Une limite de débit n'est pas une panne :
#: c'est une file d'attente, et le harnais doit patienter, pas renoncer.
_MOTIF_DELAI_RATE_LIMIT = re.compile(
    r"rate limit active.{0,40}?resets? in\s*(?:(\d+)\s*m)?\s*(?:(\d+)\s*s)?",
    re.IGNORECASE | re.DOTALL,
)

#: Plafond d'une attente : au-delà, ce n'est plus une limite de débit passagère
#: et il vaut mieux rendre la main que d'immobiliser un run sans le dire.
ATTENTE_MAX_RATE_LIMIT = 900

#: Marge ajoutée au délai annoncé — repartir à la seconde près retomberait sur
#: la même limite.
MARGE_RATE_LIMIT = 10

#: Nombre d'attentes par invocation. Bornées : trois resets consécutifs
#: signalent une campagne trop parallèle, un fait qui doit remonter.
ATTENTES_MAX = 3


def delai_rate_limit(texte: str) -> int | None:
    """Secondes à attendre avant de réessayer, si la sortie est une limite de
    débit annonçant son reset. `None` si ce n'en est pas une."""
    correspondance = _MOTIF_DELAI_RATE_LIMIT.search(texte or "")
    if correspondance is None:
        return None
    minutes = int(correspondance.group(1) or 0)
    secondes = int(correspondance.group(2) or 0)
    return min(minutes * 60 + secondes + MARGE_RATE_LIMIT, ATTENTE_MAX_RATE_LIMIT)


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
    #: ⚠️ Sémantique du fournisseur, pas la nôtre : `input_tokens` est **net
    #: du cache** (`prompt_total − cache_lus − cache_ecrits`). Nous Portal
    #: écrivant tout le préfixe en cache à chaque appel, ce champ vaut ~3 en
    #: pratique (constaté à l'audit du 2026-08-22 sur 540 tours réels).
    #: L'entrée réellement servie se reconstruit :
    #: `tokens_entree + tokens_cache_lus + tokens_cache_ecrits` — raison pour
    #: laquelle les trois champs partent dans les logs de tour.
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
            "cache_ecrits": self.tokens_cache_ecrits,
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


#: Le pilote qui rejoue le chemin `-z` avec le prompt lu d'un fichier (C2).
#: Il vit dans le paquet mais n'est jamais importé : il est exécuté par le
#: python du venv d'Hermes, seul interpréteur où `hermes_cli` existe.
PILOTE_ONESHOT = Path(__file__).with_name("pilote_oneshot.py")


def _python_du_venv(executable_hermes: str) -> str:
    """Le python du venv d'Hermes, voisin de l'exécutable `hermes`.

    Un venv range son interpréteur à côté de ses entry points — `Scripts/`
    sous Windows, `bin/` ailleurs — donc le python qui sait importer
    `hermes_cli` est le voisin direct de `hermes`. Introuvable → on échoue
    **avant** le premier appel, bruyamment : il n'y a pas de repli vers
    `hermes -z <prompt>` en argv, qui réintroduirait silencieusement le
    plafond de 32 767 caractères (C2).
    """
    chemin = Path(executable_hermes)
    if not chemin.exists():
        resolu = shutil.which(executable_hermes)
        if resolu:
            chemin = Path(resolu)
    for nom in ("python.exe", "python"):
        candidat = chemin.parent / nom
        if candidat.is_file():
            return str(candidat)
    raise FileNotFoundError(
        f"python du venv d'Hermes introuvable à côté de {chemin} — "
        "le pilote fichier (C2) exige l'interpréteur du venv, pas un python quelconque"
    )


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
        python = _python_du_venv(_executable(self.executable))
        env = _environnement(self.store)
        travail = repertoire_neutre(self.store)
        derniere: Reponse | None = None
        attentes = 0

        tentative = 0
        while tentative < self.relances + 1:
            tentative += 1
            with tempfile.TemporaryDirectory(prefix="arene-usage-") as tmp:
                rapport = Path(tmp) / "usage.json"
                # Le prompt part par fichier, jamais en argv (C2) — et jamais
                # dans `cwd-neutre` : Hermes fouille son répertoire courant.
                fichier_prompt = Path(tmp) / "prompt.txt"
                fichier_prompt.write_text(prompt, encoding="utf-8")
                commande = [
                    python,
                    str(PILOTE_ONESHOT),
                    str(fichier_prompt),
                    toolset,
                    self.parametres.modele,
                    self.parametres.fournisseur,
                    str(rapport),
                ]
                reponse = self._executer(commande, env, rapport, tentative, travail)
            if reponse.ok:
                return reponse
            derniere = reponse

            # Limite de débit du compte : ce n'est pas une panne, c'est une
            # file d'attente. On patiente le temps annoncé et on rejoue la
            # tentative **sans la consommer** — sinon un reset de sept minutes
            # emporte un run de plusieurs heures (constaté en campagne le
            # 2026-08-22 : cinq runs arrêtés d'un coup). Les attentes sont
            # bornées : au-delà, la campagne est trop parallèle, et c'est un
            # fait qui doit remonter plutôt que d'être absorbé en silence.
            attente = delai_rate_limit(reponse.texte)
            if attente is not None and attentes < ATTENTES_MAX:
                attentes += 1
                time.sleep(attente)
                tentative -= 1

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
        elif (declare := _echec_usage(rapport)) is not None:
            # Le rapport d'usage est le verdict d'Hermes lui-même : `failed`
            # et `completed` y sont écrits à chaque appel, échec compris
            # (`hermes_cli/oneshot.py`). C'est lui qui attrape ce que les
            # motifs textuels ne connaissent pas encore.
            erreur = f"échec déclaré par le rapport d'usage : {declare}"

        return Reponse(
            texte=texte,
            code_retour=acheve.returncode,
            latence_ms=latence,
            tentatives=tentative,
            erreur=erreur,
            **_usage(rapport),
        )


def _echec_usage(rapport: Path) -> str | None:
    """Échec déclaré par le rapport `--usage-file` lui-même (audit 2026-08-22).

    Le défaut n°2 du pilote — « la panne prise pour une réponse » — avait été
    colmaté par des motifs textuels sur stdout, forcément incomplets :
    `conversation_loop.py` rend une douzaine de `final_response` d'échec
    différents avec le code retour 0 (« Billing or credits exhausted »,
    « Context length exceeded », refus de politique de contenu…), et la liste
    peut changer à chaque version d'Hermes. Or le signal fiable existait déjà
    sur le disque : le rapport d'usage porte `failed`, `completed` et
    `failure`, écrits précisément pour les pipelines. C'est lui qu'on lit.

    - `failed` vaut toujours un booléen dans le rapport → vrai = échec ;
    - `completed` à `False` couvre les fins **partielles** non marquées
      `failed` (sortie tronquée, budget de raisonnement épuisé, compression
      différée) — sur le chemin nominal, Hermes le pose à `True`
      (`agent/turn_finalizer.py`) ;
    - rapport absent ou illisible → `None` : pas de verdict, les motifs
      textuels restent seuls juges.
    """
    try:
        donnees = json.loads(rapport.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if donnees.get("failed"):
        return f"failed=true : {str(donnees.get('failure') or 'sans détail')[:300]}"
    if donnees.get("completed") is False:
        return "completed=false (réponse partielle, jamais un tour nominal)"
    return None


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
    "ATTENTES_MAX",
    "ATTENTE_MAX_RATE_LIMIT",
    "RELANCES_DEFAUT",
    "TIMEOUT_DEFAUT",
    "Invocateur",
    "InvocateurHermes",
    "Reponse",
    "delai_rate_limit",
]
