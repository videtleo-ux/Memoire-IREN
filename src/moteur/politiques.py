"""Politiques de référence : GTO paramétrée et bots déterministes (PRD 1 §4, §5).

Toutes passent par la même interface `Politique` : le moteur ne distingue pas
« bot » et « agent », il calcule des EV entre deux politiques (PRD 1 §6.1).
"""

from __future__ import annotations

from fractions import Fraction
from typing import Mapping

from .infosets import (
    INFOSETS,
    Carte,
    Contexte,
    InfoSet,
    Politique,
    Position,
    construire_politique,
)

#: Paramètre de la famille d'équilibres de Kuhn, α ∈ [0, 1/3]. La spec fige 1/3.
ALPHA_DEFAUT = Fraction(1, 3)


def gto(alpha: Fraction = ALPHA_DEFAUT) -> Politique:
    """Stratégie d'équilibre pour un α donné.

    J1 : mise C2 avec proba 3α ; check C1 toujours ; bluff C0 avec proba α.
    Après son check, face à une mise : couvre C1 avec proba **α + 1/3**,
    se retire avec C0, couvre toujours avec C2 (cas d'un check accidentel).

    J2 : face à une mise, couvre C2, se retire C0, couvre C1 avec proba 1/3.
    Face à un check, mise C2, check C1, bluffe C0 avec proba 1/3.

    ⚠️ Constante tranchée (PRD 1 §4, décision D6) : la couverture de J1 avec
    C1 vaut **α + 1/3**, soit 2/3 à α = 1/3 — et non 1/3 comme écrit en §2 de
    la spec (le 1/3 correspond au cas α = 0). Le test `ecart(gto, gto) == 0`
    échoue à 1/3 et passe à 2/3 : le moteur s'auto-vérifie. Le « couvre C1 à
    1/3 » de **J2**, lui, est correct — constante d'indifférence indépendante
    de α.
    """
    alpha = Fraction(alpha)
    if not (0 <= alpha <= Fraction(1, 3)):
        raise ValueError(f"alpha doit être dans [0, 1/3], reçu {alpha}")

    valeurs: dict[InfoSet, Fraction] = {
        # J1 — ouverture
        InfoSet(Position.J1, Carte.C0, Contexte.OUVERTURE): alpha,
        InfoSet(Position.J1, Carte.C1, Contexte.OUVERTURE): Fraction(0),
        InfoSet(Position.J1, Carte.C2, Contexte.OUVERTURE): 3 * alpha,
        # J1 — après son check, face à une mise
        InfoSet(Position.J1, Carte.C0, Contexte.FACE_MISE_APRES_CHECK): Fraction(0),
        InfoSet(Position.J1, Carte.C1, Contexte.FACE_MISE_APRES_CHECK): alpha + Fraction(1, 3),
        InfoSet(Position.J1, Carte.C2, Contexte.FACE_MISE_APRES_CHECK): Fraction(1),
        # J2 — après un check de J1
        InfoSet(Position.J2, Carte.C0, Contexte.APRES_CHECK): Fraction(1, 3),
        InfoSet(Position.J2, Carte.C1, Contexte.APRES_CHECK): Fraction(0),
        InfoSet(Position.J2, Carte.C2, Contexte.APRES_CHECK): Fraction(1),
        # J2 — face à une mise
        InfoSet(Position.J2, Carte.C0, Contexte.FACE_MISE): Fraction(0),
        InfoSet(Position.J2, Carte.C1, Contexte.FACE_MISE): Fraction(1, 3),
        InfoSet(Position.J2, Carte.C2, Contexte.FACE_MISE): Fraction(1),
    }
    return construire_politique(valeurs)


GTO: Politique = gto()


_CONTEXTES_FACE_MISE = (Contexte.FACE_MISE, Contexte.FACE_MISE_APRES_CHECK)


def _politique_uniforme(p_ouverture: int, p_face_mise: int) -> Politique:
    """Bot déterministe : même action quelle que soit la carte (PRD 1 §5)."""
    valeurs: dict[InfoSet, Fraction] = {}
    for ifs in INFOSETS:
        agressif = p_face_mise if ifs.contexte in _CONTEXTES_FACE_MISE else p_ouverture
        valeurs[ifs] = Fraction(agressif)
    return construire_politique(valeurs)


#: Ne mise/bluffe jamais, couvre toujours une mise.
#: Exploit : ne jamais bluffer, miser pour la valeur avec le jeton fort.
STATION: Politique = _politique_uniforme(p_ouverture=0, p_face_mise=1)

#: Ne mise jamais, se retire toujours face à une mise.
#: Exploit : miser toutes les mains.
OVER_FOLDER: Politique = _politique_uniforme(p_ouverture=0, p_face_mise=0)

#: Les trois adversaires de la campagne (spec §3).
BOTS: Mapping[str, Politique] = {
    "GTO": GTO,
    "Station": STATION,
    "Over-folder": OVER_FOLDER,
}


__all__ = [
    "ALPHA_DEFAUT",
    "BOTS",
    "GTO",
    "OVER_FOLDER",
    "STATION",
    "gto",
]
