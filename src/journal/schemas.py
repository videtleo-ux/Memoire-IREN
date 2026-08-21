"""Schémas des événements logués (PRD 4 §2 et §3).

Le JSONL est la **source de vérité** : une ligne = un événement, append-only.
Tout doit pouvoir être reconstruit à partir des seuls logs — c'est ce que
vérifie `journal.rejouer` (PRD 4 §7.1), et c'est la raison pour laquelle
`vue_servie` (le prompt exact) et `sortie_brute` (le texte intégral du modèle)
y figurent en entier.

Deux écarts assumés au regard des exemples du PRD 4, notés ici pour que
personne n'ait à les redécouvrir dans le code :

- **Clé d'info-set** : le PRD écrit `"J1-haut-face-mise"` ; on logue la clé
  canonique du moteur, `"J1/C1/face_mise"` (PRD 1 §3), plus son numéro 1–12.
  « haut » est justement le genre de label ordinal que l'obfuscation proscrit,
  et dupliquer l'énumération des info-sets dans les logs contredirait la
  source unique du PRD 1 §9.
- **Mesures exactes** : les mesures partent en flottants (JSON n'a rien
  d'autre) *et* en fractions exactes sous forme de chaînes (`"7/9"`). Le
  projet revendique un écart d'exploitation calculé exactement ; un log qui
  n'en garde qu'un arrondi rendrait la revérification impossible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any, Mapping, Sequence

from harnais.gabarits import HASH_REGLES

#: Version du code d'arène, logué à chaque ligne : deux runs produits par deux
#: versions différentes doivent être distinguables sans archéologie Git.
VERSION_ARENE = "0.2.0"


def horodatage() -> str:
    """Instant UTC, ISO 8601 — comparable entre machines."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


@dataclass(frozen=True)
class ContexteRun:
    """Champs communs estampillés sur **chaque** ligne (PRD 4 §1)."""

    run_id: str
    condition: str  # SM | ICL | AE
    bot: str  # GTO | Station | Over-folder
    replication: int
    machine: str
    modele: str
    hash_regles: str = HASH_REGLES
    version_arene: str = VERSION_ARENE

    def en_json(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "condition": self.condition,
            "bot": self.bot,
            "replication": self.replication,
            "machine": self.machine,
            "modele": self.modele,
            "hash_regles": self.hash_regles,
            "version_arene": self.version_arene,
        }


# --------------------------------------------------------------------------
# Tour (une décision de l'agent)
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class EtatReel:
    """État canonique, non obfusqué (PRD 1 §2) — le pendant de `vue_servie`.

    Le couple des deux permet de vérifier après coup que la vue servie était
    légale et fidèle : c'est le contrôle qui protège contre un bug de rendu
    donnant à l'agent une information qu'il n'aurait pas dû avoir.
    """

    carte_agent: int
    carte_bot: int
    carte_ecartee: int
    position_agent: str  # J1 | J2
    historique: Sequence[str]  # actions canoniques déjà jouées, dans l'ordre

    def en_json(self) -> dict[str, Any]:
        return {
            "carte_agent": self.carte_agent,
            "carte_bot": self.carte_bot,
            "carte_ecartee": self.carte_ecartee,
            "position_agent": self.position_agent,
            "historique": list(self.historique),
        }


@dataclass(frozen=True)
class EvenementTour:
    """Une décision de l'agent, du prompt servi au résultat (PRD 4 §2)."""

    session: int
    manche: int
    decision: int  # rang de la décision dans la manche, à partir de 1
    etat_reel: EtatReel
    infoset: str
    infoset_numero: int
    vue_servie: str
    sortie_brute: str
    action_parsee: str
    parsing: str  # ok | repli | relance | defaut
    resultat_manche: int | None = None  # renseigné sur la dernière décision
    #: Séquence complète des actions de la manche, **bot compris**, posée sur
    #: la dernière décision. `etat_reel.historique` s'arrête à ce que l'agent
    #: voyait au moment de décider : quand le bot répond *après* la dernière
    #: décision de l'agent, sa réponse ne figure nulle part ailleurs, et la
    #: manche ne serait pas re-règlable depuis les seuls logs (PRD 4 §7.1).
    historique_final: Sequence[str] | None = None
    flags: Sequence[str] = ()
    tokens: Mapping[str, int | None] = field(default_factory=lambda: {"in": None, "out": None})
    latence_ms: int = 0

    def en_json(self) -> dict[str, Any]:
        return {
            "session": self.session,
            "manche": self.manche,
            "decision": self.decision,
            "etat_reel": self.etat_reel.en_json(),
            "infoset": self.infoset,
            "infoset_numero": self.infoset_numero,
            "vue_servie": self.vue_servie,
            "sortie_brute": self.sortie_brute,
            "action_parsee": self.action_parsee,
            "parsing": self.parsing,
            "resultat_manche": self.resultat_manche,
            "historique_final": (
                None if self.historique_final is None else list(self.historique_final)
            ),
            "flags": list(self.flags),
            "tokens": dict(self.tokens),
            "latence_ms": self.latence_ms,
        }


# --------------------------------------------------------------------------
# Session (une série close)
# --------------------------------------------------------------------------


def _fraction_json(valeur: Fraction | float | None) -> float | None:
    return None if valeur is None else float(valeur)


def _fraction_exacte(valeur: Fraction | float | None) -> str | None:
    if valeur is None:
        return None
    return str(Fraction(valeur).limit_denominator(10**9))


@dataclass(frozen=True)
class Mesures:
    """Les quantités de la spec §4, calculées exactement par le moteur."""

    ecart_exploitation: Fraction
    reference_recite: Fraction
    ev_pi_hat: Fraction
    ev_br: Fraction
    ev_realisee: float  # gains effectifs par manche — contrôle, pas une EV exacte

    def en_json(self) -> dict[str, Any]:
        return {
            "ecart_exploitation": _fraction_json(self.ecart_exploitation),
            "reference_recite": _fraction_json(self.reference_recite),
            "ev_pi_hat": _fraction_json(self.ev_pi_hat),
            "ev_br": _fraction_json(self.ev_br),
            "ev_realisee": self.ev_realisee,
            "exact": {
                "ecart_exploitation": _fraction_exacte(self.ecart_exploitation),
                "reference_recite": _fraction_exacte(self.reference_recite),
                "ev_pi_hat": _fraction_exacte(self.ev_pi_hat),
                "ev_br": _fraction_exacte(self.ev_br),
            },
        }


@dataclass(frozen=True)
class EvenementSession:
    """Une série close : mémoire, π̂, mesures, défauts, drapeaux (PRD 4 §3)."""

    session: int
    K: int
    positions: Mapping[str, int]
    memoire: Mapping[str, Any]
    pi_hat: Mapping[str, Any]
    mesures: Mesures
    defauts: Mapping[str, int]
    drapeaux_deobfuscation: Sequence[Mapping[str, Any]] = ()
    plateau: Mapping[str, Any] = field(default_factory=dict)
    hash_donnes: str = ""
    cout_session_tokens: Mapping[str, int | None] = field(
        default_factory=lambda: {"in": None, "out": None}
    )

    def en_json(self) -> dict[str, Any]:
        return {
            "session": self.session,
            "K": self.K,
            "positions": dict(self.positions),
            "memoire": dict(self.memoire),
            "pi_hat": dict(self.pi_hat),
            "mesures": self.mesures.en_json(),
            "defauts": dict(self.defauts),
            "drapeaux_deobfuscation": [dict(d) for d in self.drapeaux_deobfuscation],
            "plateau": dict(self.plateau),
            "hash_donnes": self.hash_donnes,
            "cout_session_tokens": dict(self.cout_session_tokens),
        }


# --------------------------------------------------------------------------
# Validation en écriture (PRD 4 §7.5 : aucune ligne invalide sur un run)
# --------------------------------------------------------------------------

CHAMPS_COMMUNS = (
    "run_id",
    "condition",
    "bot",
    "replication",
    "machine",
    "modele",
    "hash_regles",
    "version_arene",
    "horodatage",
)

CHAMPS_TOUR = (
    "session",
    "manche",
    "decision",
    "etat_reel",
    "infoset",
    "vue_servie",
    "sortie_brute",
    "action_parsee",
    "parsing",
    "flags",
    "tokens",
)

CHAMPS_SESSION = (
    "session",
    "K",
    "positions",
    "memoire",
    "pi_hat",
    "mesures",
    "defauts",
)

CONDITIONS = ("SM", "ICL", "AE")
PARSINGS = ("ok", "repli", "relance", "defaut")


class LigneInvalide(ValueError):
    """Une ligne ne respecte pas son schéma — l'écriture est refusée.

    Un log invalide se découvre en général au moment de l'analyse, des
    semaines et 27 runs plus tard. On échoue donc à l'écriture, bruyamment.
    """


def _exiger(ligne: Mapping[str, Any], champs: Sequence[str], quoi: str) -> None:
    manquants = [c for c in champs if c not in ligne]
    if manquants:
        raise LigneInvalide(f"{quoi} : champs manquants {manquants}")


def valider_tour(ligne: Mapping[str, Any]) -> None:
    _exiger(ligne, CHAMPS_COMMUNS, "tour")
    _exiger(ligne, CHAMPS_TOUR, "tour")
    if ligne["condition"] not in CONDITIONS:
        raise LigneInvalide(f"condition inconnue : {ligne['condition']!r}")
    if ligne["parsing"] not in PARSINGS:
        raise LigneInvalide(f"statut de parsing inconnu : {ligne['parsing']!r}")
    etat = ligne["etat_reel"]
    cartes = {etat["carte_agent"], etat["carte_bot"], etat["carte_ecartee"]}
    if cartes != {0, 1, 2}:
        raise LigneInvalide(f"donne incohérente : {sorted(cartes)} au lieu de [0, 1, 2]")
    if not str(ligne["vue_servie"]).strip():
        raise LigneInvalide("vue_servie vide : le tour ne serait pas rejouable")


def valider_session(ligne: Mapping[str, Any]) -> None:
    _exiger(ligne, CHAMPS_COMMUNS, "session")
    _exiger(ligne, CHAMPS_SESSION, "session")
    if ligne["condition"] not in CONDITIONS:
        raise LigneInvalide(f"condition inconnue : {ligne['condition']!r}")
    positions = ligne["positions"]
    if positions.get("J1", 0) + positions.get("J2", 0) != ligne["K"]:
        raise LigneInvalide(
            f"positions {dict(positions)} incompatibles avec K = {ligne['K']}"
        )
    if float(ligne["mesures"]["ecart_exploitation"]) < 0:
        raise LigneInvalide("écart d'exploitation négatif : la meilleure réponse est un maximum")


__all__ = [
    "CHAMPS_COMMUNS",
    "CHAMPS_SESSION",
    "CHAMPS_TOUR",
    "CONDITIONS",
    "PARSINGS",
    "VERSION_ARENE",
    "ContexteRun",
    "EtatReel",
    "EvenementSession",
    "EvenementTour",
    "LigneInvalide",
    "Mesures",
    "horodatage",
    "valider_session",
    "valider_tour",
]
