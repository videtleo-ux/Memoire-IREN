"""Ensembles d'information — source de vérité unique (PRD 1 §3).

Ce module définit l'énumération canonique des 12 info-sets et le type
`Politique`. Tous les autres modules (arbitre, harnais, logging, analyse)
importent d'ici et ne redéfinissent JAMAIS cette énumération
(PRD 1 §9, critère d'acceptation 3).

Représentation strictement canonique et non obfusquée (PRD 1 §2) : les
jetons sont des entiers ordonnés, les actions portent leurs noms de théorie
des jeux. L'obfuscation est une couche de rendu séparée (`lexique.py` pour
le vocabulaire, PRD 2 pour les gabarits de prompt).
"""

from __future__ import annotations

from enum import Enum, IntEnum
from fractions import Fraction
from typing import Mapping, MutableMapping, NamedTuple


class Carte(IntEnum):
    """Les trois jetons, ordonnés : C0 < C1 < C2.

    Noms volontairement neutres (et non `BASSE/MOYENNE/HAUTE`) : si un nom
    d'énumération fuitait par mégarde dans un texte servi à l'agent, un label
    ordinal évocateur violerait l'obfuscation (PRD 1 §2). Ici, rien à fuiter.
    """

    C0 = 0
    C1 = 1
    C2 = 2


CARTES: tuple[Carte, ...] = (Carte.C0, Carte.C1, Carte.C2)


class Position(Enum):
    """Position à la table. J1 parle en premier."""

    J1 = "J1"
    J2 = "J2"

    @property
    def adverse(self) -> "Position":
        return Position.J2 if self is Position.J1 else Position.J1


POSITIONS: tuple[Position, ...] = (Position.J1, Position.J2)


class Contexte(Enum):
    """Le nœud de décision, indépendamment de la carte détenue."""

    OUVERTURE = "ouverture"  # J1 ouvre
    FACE_MISE_APRES_CHECK = "face_mise_apres_check"  # J1 a checké, J2 a misé
    APRES_CHECK = "apres_check"  # J2 après un check de J1
    FACE_MISE = "face_mise"  # J2 face à la mise d'ouverture de J1


class Action(Enum):
    CHECK = "check"
    BET = "bet"
    CALL = "call"
    FOLD = "fold"


#: Actions légales par contexte, sous la forme (passive, agressive).
#: L'ordre est significatif : une `Politique` donne la probabilité de
#: l'action AGRESSIVE, et la convention d'indifférence de la meilleure
#: réponse retient l'action PASSIVE (PRD 1 §6.2).
ACTIONS_LEGALES: Mapping[Contexte, tuple[Action, Action]] = {
    Contexte.OUVERTURE: (Action.CHECK, Action.BET),
    Contexte.FACE_MISE_APRES_CHECK: (Action.FOLD, Action.CALL),
    Contexte.APRES_CHECK: (Action.CHECK, Action.BET),
    Contexte.FACE_MISE: (Action.FOLD, Action.CALL),
}

#: Contextes de chaque position, dans l'ordre du tableau du PRD 1 §3.
CONTEXTES_PAR_POSITION: Mapping[Position, tuple[Contexte, ...]] = {
    Position.J1: (Contexte.OUVERTURE, Contexte.FACE_MISE_APRES_CHECK),
    Position.J2: (Contexte.APRES_CHECK, Contexte.FACE_MISE),
}


class InfoSet(NamedTuple):
    """Clé canonique d'un ensemble d'information : (position, carte, contexte)."""

    position: Position
    carte: Carte
    contexte: Contexte

    @property
    def actions_legales(self) -> tuple[Action, Action]:
        return ACTIONS_LEGALES[self.contexte]

    @property
    def action_passive(self) -> Action:
        return ACTIONS_LEGALES[self.contexte][0]

    @property
    def action_agressive(self) -> Action:
        return ACTIONS_LEGALES[self.contexte][1]

    def __str__(self) -> str:  # pragma: no cover - confort de log/debug
        return f"{self.position.value}/{self.carte.name}/{self.contexte.value}"


def _construire_enumeration() -> tuple[InfoSet, ...]:
    """Ordre du tableau PRD 1 §3 : 1–3 J1 ouverture, 4–6 J1 face à une mise,
    7–9 J2 après check, 10–12 J2 face à une mise ; cartes croissantes."""
    infosets: list[InfoSet] = []
    for position in POSITIONS:
        for contexte in CONTEXTES_PAR_POSITION[position]:
            for carte in CARTES:
                infosets.append(InfoSet(position, carte, contexte))
    return tuple(infosets)


#: Les 12 info-sets, dans l'ordre canonique. Le numéro de log d'un info-set
#: est son index + 1 (cf. `numero`).
INFOSETS: tuple[InfoSet, ...] = _construire_enumeration()

_NUMEROS: Mapping[InfoSet, int] = {ifs: i + 1 for i, ifs in enumerate(INFOSETS)}


def numero(infoset: InfoSet) -> int:
    """Numéro 1–12 de l'info-set, tel qu'il apparaît dans les logs (PRD 4)."""
    return _NUMEROS[infoset]


def infosets_de_position(position: Position) -> tuple[InfoSet, ...]:
    """Les 6 info-sets d'un joueur à une position donnée."""
    return tuple(ifs for ifs in INFOSETS if ifs.position is position)


def infoset(position: Position, carte: Carte, contexte: Contexte) -> InfoSet:
    """Constructeur validant : lève si le contexte n'existe pas à cette position."""
    if contexte not in CONTEXTES_PAR_POSITION[position]:
        raise ValueError(f"contexte {contexte.value} impossible en position {position.value}")
    return InfoSet(position, carte, contexte)


# --------------------------------------------------------------------------
# Politiques
# --------------------------------------------------------------------------

#: Une politique complète : 12 probabilités de jouer l'action agressive.
#: Les valeurs sont des `Fraction` — aucun flottant dans le moteur d'EV
#: (PRD 1 §7), les 1/18 et 7/9 attendus sont exacts.
Politique = Mapping[InfoSet, Fraction]


def construire_politique(valeurs: Mapping[InfoSet, Fraction | int | float | str]) -> Politique:
    """Normalise en `Fraction`, valide la complétude et le domaine [0, 1]."""
    politique: MutableMapping[InfoSet, Fraction] = {}
    for ifs, valeur in valeurs.items():
        if ifs not in _NUMEROS:
            raise ValueError(f"info-set inconnu : {ifs}")
        politique[ifs] = Fraction(valeur)
    valider_politique(politique)
    return politique


def valider_politique(politique: Politique) -> None:
    """Lève `ValueError` si la politique n'est pas totale ou hors [0, 1]."""
    manquants = [ifs for ifs in INFOSETS if ifs not in politique]
    if manquants:
        raise ValueError(f"politique incomplète, info-sets manquants : {[str(i) for i in manquants]}")
    for ifs in INFOSETS:
        p = politique[ifs]
        if not (0 <= p <= 1):
            raise ValueError(f"probabilité hors [0,1] en {ifs} : {p}")
