"""Meilleure réponse exacte et écart d'exploitation (PRD 1 §6).

C'est l'instrument de mesure du projet : `ecart(π̂(M_s), bot)` est l'Écart(s)
de la spec §4. Tout est exact — induction arrière sur poids contrefactuels,
arithmétique en `Fraction`, aucun échantillonnage.

Poids contrefactuels : le poids d'un info-set de l'agent est la probabilité
que la nature et l'**adversaire seul** amènent le jeu jusque-là (la politique
de l'agent est délibérément ignorée). C'est ce qui rend l'induction arrière
valide info-set par info-set, et c'est aussi la bonne notion
d'« atteignabilité » : contre Station et Over-folder, qui ne misent jamais,
les info-sets 4–6 et 10–12 ont un poids nul (PRD 1 §3).
"""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Mapping, MutableMapping, NamedTuple

from .infosets import (
    CARTES,
    INFOSETS,
    Carte,
    Contexte,
    InfoSet,
    Politique,
    Position,
    construire_politique,
    valider_politique,
)
from .politiques import ALPHA_DEFAUT, gto
from .regles import PROBA_DONNE, ev_moyenne


class ResultatMeilleureReponse(NamedTuple):
    """Résultat de `meilleure_reponse`.

    Écart assumé avec la signature `(Politique, float)` du PRD 1 §6.2 : un
    troisième champ expose les indifférences exactes, que la même section
    demande de loguer.
    """

    politique: Politique
    ev: Fraction  # EV moyennée sur les deux positions
    indifferences: tuple[InfoSet, ...]  # cas d'égalité exacte, tranchés en passif


class _Decision(NamedTuple):
    action_agressive: bool
    valeur: Fraction
    indifferent: bool


def _trancher(valeur_passive: Fraction, valeur_agressive: Fraction) -> _Decision:
    """Argmax avec convention figée : en cas d'indifférence exacte, l'action
    passive (PRD 1 §6.2), et le cas est signalé pour être logué."""
    if valeur_agressive > valeur_passive:
        return _Decision(True, valeur_agressive, False)
    return _Decision(False, valeur_passive, valeur_agressive == valeur_passive)


def _autres_cartes(carte: Carte) -> tuple[Carte, ...]:
    """Les 2 jetons que l'adversaire peut détenir (croyance uniforme a priori)."""
    return tuple(d for d in CARTES if d != carte)


def _gain(carte_agent: Carte, carte_adverse: Carte, mise: int) -> int:
    """Gain de l'agent à l'abattage, de son point de vue."""
    return mise if carte_agent > carte_adverse else -mise


def _meilleure_reponse_j1(
    pi_adverse: Politique,
) -> tuple[dict[InfoSet, Fraction], Fraction, list[InfoSet]]:
    """Agent en J1 ; l'adversaire occupe J2."""
    politique: dict[InfoSet, Fraction] = {}
    indifferences: list[InfoSet] = []
    total = Fraction(0)

    for c in CARTES:
        autres = _autres_cartes(c)

        # --- Info-set profond : J1 a checké, J2 a misé -------------------
        ifs_face = InfoSet(Position.J1, c, Contexte.FACE_MISE_APRES_CHECK)
        poids = {
            d: PROBA_DONNE * pi_adverse[InfoSet(Position.J2, d, Contexte.APRES_CHECK)]
            for d in autres
        }
        v_fold = sum((p * -1 for p in poids.values()), start=Fraction(0))
        v_call = sum((poids[d] * _gain(c, d, 2) for d in autres), start=Fraction(0))
        face = _trancher(v_fold, v_call)
        politique[ifs_face] = Fraction(1) if face.action_agressive else Fraction(0)
        if face.indifferent:
            indifferences.append(ifs_face)
        # Valeur, par carte adverse, de l'action retenue en aval.
        gain_aval = {d: (_gain(c, d, 2) if face.action_agressive else -1) for d in autres}

        # --- Ouverture ---------------------------------------------------
        ifs_ouv = InfoSet(Position.J1, c, Contexte.OUVERTURE)
        v_check = Fraction(0)
        v_bet = Fraction(0)
        for d in autres:
            p_bet_adv = pi_adverse[InfoSet(Position.J2, d, Contexte.APRES_CHECK)]
            p_call_adv = pi_adverse[InfoSet(Position.J2, d, Contexte.FACE_MISE)]
            v_check += PROBA_DONNE * (
                (1 - p_bet_adv) * _gain(c, d, 1) + p_bet_adv * gain_aval[d]
            )
            v_bet += PROBA_DONNE * ((1 - p_call_adv) * 1 + p_call_adv * _gain(c, d, 2))
        ouverture = _trancher(v_check, v_bet)
        politique[ifs_ouv] = Fraction(1) if ouverture.action_agressive else Fraction(0)
        if ouverture.indifferent:
            indifferences.append(ifs_ouv)
        total += ouverture.valeur

    return politique, total, indifferences


def _meilleure_reponse_j2(
    pi_adverse: Politique,
) -> tuple[dict[InfoSet, Fraction], Fraction, list[InfoSet]]:
    """Agent en J2 ; l'adversaire occupe J1. Les deux décisions de J2 sont
    terminales de son point de vue, et leurs poids partitionnent les donnes
    (J1 a misé, ou J1 a checké)."""
    politique: dict[InfoSet, Fraction] = {}
    indifferences: list[InfoSet] = []
    total = Fraction(0)

    for c in CARTES:
        autres = _autres_cartes(c)

        # --- Face à la mise d'ouverture de J1 ----------------------------
        ifs_face = InfoSet(Position.J2, c, Contexte.FACE_MISE)
        poids = {
            d: PROBA_DONNE * pi_adverse[InfoSet(Position.J1, d, Contexte.OUVERTURE)]
            for d in autres
        }
        v_fold = sum((p * -1 for p in poids.values()), start=Fraction(0))
        v_call = sum((poids[d] * _gain(c, d, 2) for d in autres), start=Fraction(0))
        face = _trancher(v_fold, v_call)
        politique[ifs_face] = Fraction(1) if face.action_agressive else Fraction(0)
        if face.indifferent:
            indifferences.append(ifs_face)
        total += face.valeur

        # --- Après un check de J1 ----------------------------------------
        ifs_apres = InfoSet(Position.J2, c, Contexte.APRES_CHECK)
        v_check = Fraction(0)
        v_bet = Fraction(0)
        for d in autres:
            p_check_adv = 1 - pi_adverse[InfoSet(Position.J1, d, Contexte.OUVERTURE)]
            p_call_adv = pi_adverse[InfoSet(Position.J1, d, Contexte.FACE_MISE_APRES_CHECK)]
            poids_d = PROBA_DONNE * p_check_adv
            v_check += poids_d * _gain(c, d, 1)
            v_bet += poids_d * ((1 - p_call_adv) * 1 + p_call_adv * _gain(c, d, 2))
        apres = _trancher(v_check, v_bet)
        politique[ifs_apres] = Fraction(1) if apres.action_agressive else Fraction(0)
        if apres.indifferent:
            indifferences.append(ifs_apres)
        total += apres.valeur

    return politique, total, indifferences


def meilleure_reponse(pi_adverse: Politique) -> ResultatMeilleureReponse:
    """Meilleure réponse exacte à une politique fixe et connue.

    Rend une politique **pure** complète (12 entrées à 0 ou 1 : la meilleure
    réponse aux deux positions, l'arène alternant J1/J2) et son EV moyennée
    sur les positions.
    """
    valider_politique(pi_adverse)
    pol_j1, ev_j1, ind_j1 = _meilleure_reponse_j1(pi_adverse)
    pol_j2, ev_j2, ind_j2 = _meilleure_reponse_j2(pi_adverse)
    politique = construire_politique({**pol_j1, **pol_j2})
    return ResultatMeilleureReponse(
        politique=politique,
        ev=(ev_j1 + ev_j2) / 2,
        indifferences=tuple(ind_j1 + ind_j2),
    )


def ecart(pi_agent: Politique, pi_adverse: Politique) -> Fraction:
    """Écart d'exploitation : `EV(meilleure réponse) − EV(pi_agent)` contre le
    même adversaire, moyenné sur les positions. C'est l'**Écart(s)** de la
    spec §4 quand `pi_agent = π̂(M_s)`. Toujours ≥ 0, nul ssi `pi_agent` est
    une meilleure réponse."""
    return meilleure_reponse(pi_adverse).ev - ev_moyenne(pi_agent, pi_adverse)


def ecart_recitation(
    pi_agent: Politique,
    pi_adverse: Politique,
    alpha: Fraction = ALPHA_DEFAUT,
) -> Fraction:
    """Référence « récité » (PRD 1 §6.2) : `EV(pi_agent) − EV(GTO)` contre le
    même adversaire. Positif ⇒ l'agent fait mieux qu'un réciteur d'équilibre."""
    return ev_moyenne(pi_agent, pi_adverse) - ev_moyenne(gto(alpha), pi_adverse)


# --------------------------------------------------------------------------
# Atteignabilité et complétion de π̂
# --------------------------------------------------------------------------


def poids_contrefactuels(pi_adverse: Politique) -> Mapping[InfoSet, Fraction]:
    """Probabilité que nature + adversaire seuls mènent à chaque info-set de
    l'agent (la politique de l'agent est ignorée : elle n'affecte pas
    l'atteignabilité au sens contrefactuel)."""
    valider_politique(pi_adverse)
    poids: dict[InfoSet, Fraction] = {}
    for c in CARTES:
        autres = _autres_cartes(c)
        # L'ouverture est toujours atteinte : l'adversaire n'a encore rien joué.
        poids[InfoSet(Position.J1, c, Contexte.OUVERTURE)] = len(autres) * PROBA_DONNE
        poids[InfoSet(Position.J1, c, Contexte.FACE_MISE_APRES_CHECK)] = sum(
            (
                PROBA_DONNE * pi_adverse[InfoSet(Position.J2, d, Contexte.APRES_CHECK)]
                for d in autres
            ),
            start=Fraction(0),
        )
        poids[InfoSet(Position.J2, c, Contexte.APRES_CHECK)] = sum(
            (
                PROBA_DONNE * (1 - pi_adverse[InfoSet(Position.J1, d, Contexte.OUVERTURE)])
                for d in autres
            ),
            start=Fraction(0),
        )
        poids[InfoSet(Position.J2, c, Contexte.FACE_MISE)] = sum(
            (
                PROBA_DONNE * pi_adverse[InfoSet(Position.J1, d, Contexte.OUVERTURE)]
                for d in autres
            ),
            start=Fraction(0),
        )
    return poids


def infosets_atteignables(pi_adverse: Politique) -> frozenset[InfoSet]:
    """Info-sets de l'agent que l'adversaire rend atteignables (poids > 0).

    12 contre GTO ; exactement 6 contre Station et Over-folder, qui ne misent
    jamais (PRD 1 §3)."""
    poids = poids_contrefactuels(pi_adverse)
    return frozenset(ifs for ifs in INFOSETS if poids[ifs] > 0)


def completer_politique(
    pi_partielle: Mapping[InfoSet, Fraction],
    alpha: Fraction = ALPHA_DEFAUT,
) -> tuple[Politique, tuple[InfoSet, ...]]:
    """Rend π̂ totale en comblant les info-sets non observés par la valeur GTO
    (convention figée, PRD 1 §6.3).

    Ces info-sets étant inatteignables face au bot concerné, leur valeur
    n'affecte ni `ev(π̂, bot)` ni l'écart ; la convention ne sert qu'à rendre
    le calcul robuste, et le choix GTO évite d'inventer une agressivité
    fantôme dans les analyses descriptives de π̂. Le tuple rendu alimente le
    drapeau `infosets_non_observes` des logs de session (PRD 4).
    """
    reference = gto(alpha)
    valeurs: MutableMapping[InfoSet, Fraction] = {}
    non_observes: list[InfoSet] = []
    for ifs in INFOSETS:
        if ifs in pi_partielle:
            valeurs[ifs] = Fraction(pi_partielle[ifs])
        else:
            valeurs[ifs] = reference[ifs]
            non_observes.append(ifs)
    return construire_politique(valeurs), tuple(non_observes)


def politique_pure(agressifs: Iterable[InfoSet]) -> Politique:
    """Politique déterministe : action agressive sur les info-sets listés,
    passive partout ailleurs. Utilisée par les tests d'énumération."""
    ensemble = frozenset(agressifs)
    return construire_politique({ifs: Fraction(int(ifs in ensemble)) for ifs in INFOSETS})


__all__ = [
    "ResultatMeilleureReponse",
    "completer_politique",
    "ecart",
    "ecart_recitation",
    "infosets_atteignables",
    "meilleure_reponse",
    "poids_contrefactuels",
    "politique_pure",
]
