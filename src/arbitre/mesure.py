"""Estimation de π̂ et critère de plateau (PRD 3 §6).

Deux mesures, deux natures :

- **π̂(M_s) et l'écart d'exploitation** sont exacts. π̂ est une simple
  fréquence par info-set, mais l'écart qui s'en déduit passe par la meilleure
  réponse exacte du moteur (PRD 1) : aucune simulation, aucun échantillonnage.
- **Le plateau** est une heuristique d'arrêt, assumée comme telle. Ses
  constantes sont revalidées au pilote de calibrage sur les premières courbes
  réelles ; la décision est loguée à chaque évaluation, avec la pente et
  l'écart-type qui l'ont produite, pour qu'on puisse la rejuger après coup
  sans relancer un seul run.

π̂ est estimée à partir des **lignes de log déjà écrites**, via
`journal.estimer_pi_hat`, et non d'un compteur tenu en parallèle : la règle
d'exclusion des décisions `action_par_defaut` (PRD 3 §6.1) n'existe ainsi
qu'à un seul endroit, et l'arbitre mesure exactement ce que le rejeu
retrouvera (PRD 4 §7.1).
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Iterable, Mapping, Sequence

from journal import Mesures, estimer_pi_hat
from moteur import (
    InfoSet,
    Politique,
    completer_politique,
    ecart,
    ecart_recitation,
    ev_moyenne,
    meilleure_reponse,
)

# --------------------------------------------------------------------------
# π̂ et mesures de série
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class MesureSerie:
    """Tout ce que la clôture d'une série produit côté mesure."""

    mesures: Mesures
    pi_hat: Politique  # totale : les non-observés comblés à la valeur GTO
    pi_observee: Mapping[InfoSet, Fraction]  # les seuls info-sets vus
    effectifs: Mapping[InfoSet, int]
    non_observes: Sequence[InfoSet]

    def pi_hat_json(self) -> dict[str, Any]:
        """Bloc `pi_hat` du log de série (PRD 4 §3) : `p` et effectif `n`.

        Les effectifs partent dans les logs parce qu'ils donnent les barres
        d'erreur : un π̂ de 1,0 sur 2 observations ne dit pas la même chose
        qu'un π̂ de 1,0 sur 60.
        """
        bloc: dict[str, Any] = {
            str(ifs): {"p": float(self.pi_observee[ifs]), "n": self.effectifs[ifs]}
            for ifs in self.pi_observee
        }
        bloc["infosets_non_observes"] = [str(ifs) for ifs in self.non_observes]
        return bloc


def mesurer_serie(
    tours: Iterable[Mapping[str, Any]],
    gains: Sequence[int],
    bot: Politique,
) -> MesureSerie:
    """Mesure une série close à partir de ses tours logués et de ses gains.

    `ev_realisee` (gains effectifs par manche) est le contre-témoin de
    `ev_pi_hat` : les deux doivent se ressembler. Un écart marqué entre elles
    signale un bug d'estimation ou de règlement des manches, pas une
    trouvaille expérimentale (PRD 4 §3).
    """
    pi_observee, effectifs = estimer_pi_hat(tours)
    pi_hat, non_observes = completer_politique(pi_observee)
    return MesureSerie(
        mesures=Mesures(
            ecart_exploitation=ecart(pi_hat, bot),
            reference_recite=ecart_recitation(pi_hat, bot),
            ev_pi_hat=ev_moyenne(pi_hat, bot),
            ev_br=meilleure_reponse(bot).ev,
            ev_realisee=(sum(gains) / len(gains)) if gains else 0.0,
        ),
        pi_hat=pi_hat,
        pi_observee=pi_observee,
        effectifs=effectifs,
        non_observes=non_observes,
    )


# --------------------------------------------------------------------------
# Critère de plateau (PRD 3 §6.2)
# --------------------------------------------------------------------------

#: Nombre minimal de séries avant toute évaluation : moins de points, et
#: « plat » ne se distingue pas de « pas encore parti ».
SERIES_MIN_PLATEAU = 8

#: Fenêtre glissante sur laquelle on régresse.
FENETRE_PLATEAU = 4

#: Pente au-delà de laquelle l'écart ne décroît plus significativement
#: (jeton/manche/série). Le signe compte : on cherche l'arrêt de la
#: *décroissance*, une remontée franche est un plateau au sens de l'arrêt.
EPSILON_PENTE = 0.02

#: Dispersion maximale des dernières valeurs : une courbe en dents de scie
#: peut avoir une pente nulle sans avoir plateauté du tout.
SEUIL_DISPERSION = 0.05

#: Marge après déclaration (spec §6 : « plateau + marge »).
MARGE_PLATEAU = 2


@dataclass(frozen=True)
class Plateau:
    """Une évaluation du critère, telle qu'elle part dans les logs."""

    evalue: bool
    pente: float | None = None
    dispersion: float | None = None
    declare: bool = False

    def en_json(self) -> dict[str, Any]:
        return {
            "evalue": self.evalue,
            "pente": self.pente,
            "dispersion": self.dispersion,
            "declare": self.declare,
        }


def pente_regression(valeurs: Sequence[float]) -> float:
    """Pente des moindres carrés de `valeurs` contre 0, 1, 2… (série par série).

    Formule explicite plutôt que `statistics.linear_regression` : celle-ci
    n'existe qu'à partir de Python 3.10 et lève sur une variance nulle en
    abscisse, cas que l'on préfère traiter ici, à découvert.
    """
    n = len(valeurs)
    if n < 2:
        return 0.0
    abscisses = range(n)
    moyenne_x = (n - 1) / 2
    moyenne_y = sum(valeurs) / n
    numerateur = sum((x - moyenne_x) * (y - moyenne_y) for x, y in zip(abscisses, valeurs))
    denominateur = sum((x - moyenne_x) ** 2 for x in abscisses)
    return numerateur / denominateur if denominateur else 0.0


def evaluer_plateau(
    ecarts: Sequence[float],
    series_min: int = SERIES_MIN_PLATEAU,
    fenetre: int = FENETRE_PLATEAU,
) -> Plateau:
    """Le critère du PRD 3 §6.2, appliqué à la suite `Écart(0..s)`.

    Plateau déclaré si, avec au moins `series_min` séries, la pente de la
    régression sur les `fenetre` dernières est ≥ −ε **et** leur dispersion est
    sous le seuil. Les deux conditions sont nécessaires : la pente seule
    déclarerait plateau sur des dents de scie régulières, la dispersion seule
    le déclarerait au milieu d'une descente lente et lisse.
    """
    if len(ecarts) < max(series_min, fenetre):
        return Plateau(evalue=False)
    dernieres = [float(e) for e in ecarts[-fenetre:]]
    pente = pente_regression(dernieres)
    dispersion = statistics.pstdev(dernieres)
    return Plateau(
        evalue=True,
        pente=pente,
        dispersion=dispersion,
        declare=pente >= -EPSILON_PENTE and dispersion < SEUIL_DISPERSION,
    )


__all__ = [
    "EPSILON_PENTE",
    "FENETRE_PLATEAU",
    "MARGE_PLATEAU",
    "SERIES_MIN_PLATEAU",
    "SEUIL_DISPERSION",
    "MesureSerie",
    "Plateau",
    "evaluer_plateau",
    "mesurer_serie",
    "pente_regression",
]
