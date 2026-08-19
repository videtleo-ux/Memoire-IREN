"""Règles de la manche et EV exactes par énumération (PRD 1 §2, §6.2).

Le jeu est minuscule : 6 donnes ordonnées équiprobables × un arbre de
profondeur ≤ 3. Tout se calcule par énumération complète, en `Fraction`,
sans échantillonnage.

Arbre (représentation canonique) :

    J1 check ─┬─ J2 check                 → abattage ±1
              └─ J2 bet ─┬─ J1 fold        → −1
                         └─ J1 call        → abattage ±2
    J1 bet ───┬─ J2 fold                   → +1
              └─ J2 call                   → abattage ±2

Tous les gains sont exprimés du point de vue de J1 (jeu à somme nulle).
"""

from __future__ import annotations

import random
from fractions import Fraction
from itertools import permutations
from typing import Callable, NamedTuple

from .infosets import (
    Action,
    Carte,
    Contexte,
    InfoSet,
    Politique,
    Position,
    valider_politique,
)

#: Les 6 donnes ordonnées (carte de J1, carte de J2), équiprobables.
#: La 3ᵉ carte est écartée et n'est connue de personne.
DONNES: tuple[tuple[Carte, Carte], ...] = tuple(permutations(Carte, 2))  # type: ignore[arg-type]

#: Probabilité d'une donne.
PROBA_DONNE = Fraction(1, len(DONNES))


def _gain_abattage(carte_j1: Carte, carte_j2: Carte, mise: int) -> int:
    """Gain de J1 à l'abattage. `mise` = 1 (check-check) ou 2 (une mise payée)."""
    return mise if carte_j1 > carte_j2 else -mise


# --------------------------------------------------------------------------
# EV exactes
# --------------------------------------------------------------------------


def _ev_j1_sur_donne(
    carte_j1: Carte,
    carte_j2: Carte,
    pi_j1: Politique,
    pi_j2: Politique,
) -> Fraction:
    """EV de J1 sur une donne fixée, en propageant les probabilités de l'arbre."""
    p_bet_j1 = pi_j1[InfoSet(Position.J1, carte_j1, Contexte.OUVERTURE)]
    p_call_j1 = pi_j1[InfoSet(Position.J1, carte_j1, Contexte.FACE_MISE_APRES_CHECK)]
    p_bet_j2 = pi_j2[InfoSet(Position.J2, carte_j2, Contexte.APRES_CHECK)]
    p_call_j2 = pi_j2[InfoSet(Position.J2, carte_j2, Contexte.FACE_MISE)]

    # Branche « J1 mise »
    v_mise = (1 - p_call_j2) * 1 + p_call_j2 * _gain_abattage(carte_j1, carte_j2, 2)

    # Branche « J1 check », sous-branche « J2 mise »
    v_check_puis_mise = (1 - p_call_j1) * (-1) + p_call_j1 * _gain_abattage(carte_j1, carte_j2, 2)
    # Branche « J1 check »
    v_check = (1 - p_bet_j2) * _gain_abattage(carte_j1, carte_j2, 1) + p_bet_j2 * v_check_puis_mise

    return p_bet_j1 * v_mise + (1 - p_bet_j1) * v_check


def ev(pi_a: Politique, pi_b: Politique, position_a: Position = Position.J1) -> Fraction:
    """EV exacte par manche de la politique `pi_a` contre `pi_b`, `pi_a` étant
    assise en `position_a`. Résultat exact (`Fraction`), du point de vue de a.

    Chaque politique est complète (12 info-sets) ; seules les entrées de la
    position occupée sont consultées.
    """
    if position_a is Position.J1:
        pi_j1, pi_j2 = pi_a, pi_b
    else:
        pi_j1, pi_j2 = pi_b, pi_a

    total = sum(
        (_ev_j1_sur_donne(c1, c2, pi_j1, pi_j2) for c1, c2 in DONNES),
        start=Fraction(0),
    )
    esperance_j1 = total * PROBA_DONNE
    return esperance_j1 if position_a is Position.J1 else -esperance_j1


def ev_moyenne(pi_a: Politique, pi_b: Politique) -> Fraction:
    """EV moyennée sur les deux positions — l'arène alterne J1/J2, donc
    **toutes les quantités rapportées** passent par ici (PRD 1 §6.2)."""
    return (ev(pi_a, pi_b, Position.J1) + ev(pi_a, pi_b, Position.J2)) / 2


def valeur_du_jeu(pi_j1: Politique, pi_j2: Politique) -> Fraction:
    """EV de J1 quand J1 joue `pi_j1` et J2 joue `pi_j2` (alias explicite de T1)."""
    return ev(pi_j1, pi_j2, Position.J1)


# --------------------------------------------------------------------------
# Déroulement d'une manche effective
# --------------------------------------------------------------------------

#: Un décideur reçoit l'info-set atteint et rend l'action choisie. C'est le
#: point de couture entre le moteur et le harnais LLM (PRD 2) : un bot est un
#: décideur tiré d'une politique, l'agent est un décideur qui appelle Hermes.
Decideur = Callable[[InfoSet], Action]


class ResultatManche(NamedTuple):
    cartes: tuple[Carte, Carte]  # (carte de J1, carte de J2)
    historique: tuple[tuple[InfoSet, Action], ...]  # décisions dans l'ordre
    gain_j1: int
    abattage: bool


def decideur_depuis_politique(politique: Politique, alea: random.Random) -> Decideur:
    """Transforme une politique en décideur stochastique.

    `alea` doit être le flux aléatoire dédié au bot (seedé par manche, PRD 3
    §4) — jamais celui des donnes, sinon les conditions mémoire ne verraient
    plus les mêmes cartes (PRD 1 §4).
    """
    valider_politique(politique)

    def decideur(infoset: InfoSet) -> Action:
        p_agressive = politique[infoset]
        if p_agressive == 1:
            return infoset.action_agressive
        if p_agressive == 0:
            return infoset.action_passive
        tirage = Fraction(alea.random()).limit_denominator(10**9)
        return infoset.action_agressive if tirage < p_agressive else infoset.action_passive

    return decideur


def _decider(decideur: Decideur, infoset: InfoSet) -> Action:
    action = decideur(infoset)
    if action not in infoset.actions_legales:
        raise ValueError(f"action illégale {action.value} en {infoset}")
    return action


def jouer_manche(
    decideur_j1: Decideur,
    decideur_j2: Decideur,
    carte_j1: Carte,
    carte_j2: Carte,
) -> ResultatManche:
    """Joue une manche entre deux décideurs sur une donne imposée.

    La donne est fournie par l'appelant (l'arbitre sert la séquence de donnes
    commune aux trois conditions, PRD 3 §4) : le moteur ne tire jamais les
    cartes lui-même.
    """
    if carte_j1 == carte_j2:
        raise ValueError("les deux joueurs ne peuvent pas détenir le même jeton")

    historique: list[tuple[InfoSet, Action]] = []

    ifs_ouverture = InfoSet(Position.J1, carte_j1, Contexte.OUVERTURE)
    ouverture = _decider(decideur_j1, ifs_ouverture)
    historique.append((ifs_ouverture, ouverture))

    if ouverture is Action.BET:
        ifs = InfoSet(Position.J2, carte_j2, Contexte.FACE_MISE)
        reponse = _decider(decideur_j2, ifs)
        historique.append((ifs, reponse))
        if reponse is Action.FOLD:
            gain, abattage = 1, False
        else:
            gain, abattage = _gain_abattage(carte_j1, carte_j2, 2), True
    else:
        ifs = InfoSet(Position.J2, carte_j2, Contexte.APRES_CHECK)
        reponse = _decider(decideur_j2, ifs)
        historique.append((ifs, reponse))
        if reponse is Action.CHECK:
            gain, abattage = _gain_abattage(carte_j1, carte_j2, 1), True
        else:
            ifs_face = InfoSet(Position.J1, carte_j1, Contexte.FACE_MISE_APRES_CHECK)
            finale = _decider(decideur_j1, ifs_face)
            historique.append((ifs_face, finale))
            if finale is Action.FOLD:
                gain, abattage = -1, False
            else:
                gain, abattage = _gain_abattage(carte_j1, carte_j2, 2), True

    return ResultatManche(
        cartes=(carte_j1, carte_j2),
        historique=tuple(historique),
        gain_j1=gain,
        abattage=abattage,
    )
