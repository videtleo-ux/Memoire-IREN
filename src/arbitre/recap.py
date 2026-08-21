"""Récap canonique de série — unique, brut, sans interprétation (PRD 3 §5).

Ce texte est servi tel quel à la réflexion de la condition AE **et** empilé
dans la fenêtre de la condition ICL (décision D8) : les deux conditions à
mémoire voient exactement la même matière première, seul le mécanisme de
rétention diffère. S'il différait d'une condition à l'autre, la comparaison
« escalier vs dents de scie » comparerait deux informations, pas deux
mémoires.

Deux règles dont on ne dévie pas :

- **Aucune agrégation.** Une ligne par épreuve, un solde en pied, rien
  d'autre : ni fréquence par info-set, ni conseil, ni « il couvre toujours ».
  Distiller la fuite de l'adversaire est le travail de l'agent — c'est
  exactement ce que l'expérience mesure (spec §6).
- **Aucune fuite.** Le sceau adverse n'apparaît que si les sceaux ont été
  dévoilés. Une manche close par un retrait dit « sceau adverse non
  dévoilé » : donner davantage offrirait à l'agent une information que la
  table ne lui a pas donnée (critère d'acceptation PRD 3 §10.5).

Le rendu textuel lui-même appartient aux gabarits (PRD 2) : ce module ne fait
que choisir *quoi* montrer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from harnais import gabarits
from moteur import Carte, Position, ResultatManche


def carte_agent(resultat: ResultatManche, position: Position) -> Carte:
    return resultat.cartes[0] if position is Position.J1 else resultat.cartes[1]


def carte_adverse_visible(resultat: ResultatManche, position: Position) -> Carte | None:
    """Sceau adverse **si et seulement si** il a été dévoilé à l'abattage."""
    if not resultat.abattage:
        return None
    return resultat.cartes[1] if position is Position.J1 else resultat.cartes[0]


def gain_agent(resultat: ResultatManche, position: Position) -> int:
    """Le moteur compte du point de vue de J1 ; le récap, de celui de l'agent."""
    return resultat.gain_j1 if position is Position.J1 else -resultat.gain_j1


def ligne_manche(numero_manche: int, position: Position, resultat: ResultatManche) -> str:
    """Une épreuve jouée, résumée en une ligne de vocabulaire obfusqué."""
    return gabarits.ligne_recap(
        numero_epreuve=numero_manche,
        position_agent=position,
        carte_agent=carte_agent(resultat, position),
        historique=[(ifs.position, action) for ifs, action in resultat.historique],
        carte_adverse=carte_adverse_visible(resultat, position),
        solde=gain_agent(resultat, position),
    )


@dataclass
class Recapitulateur:
    """Accumule les lignes d'une série et rend le récap final.

    Le solde est recalculé par addition des gains de manche plutôt que relu
    ailleurs : c'est le seul chiffre agrégé du récap, autant qu'il vienne
    directement de ce qui a été joué.
    """

    lignes: list[str] = field(default_factory=list)
    gains: list[int] = field(default_factory=list)

    def ajouter(self, numero_manche: int, position: Position, resultat: ResultatManche) -> int:
        gain = gain_agent(resultat, position)
        self.lignes.append(ligne_manche(numero_manche, position, resultat))
        self.gains.append(gain)
        return gain

    @property
    def solde(self) -> int:
        return sum(self.gains)

    @property
    def manches(self) -> int:
        return len(self.lignes)

    def texte(self) -> str:
        return gabarits.recap_serie(self.lignes, self.solde)


def recap_depuis_lignes(lignes: Sequence[str], solde: int) -> str:
    """Reconstruction d'un récap à partir de lignes déjà rendues (reprise)."""
    return gabarits.recap_serie(list(lignes), solde)


__all__ = [
    "Recapitulateur",
    "carte_adverse_visible",
    "carte_agent",
    "gain_agent",
    "ligne_manche",
    "recap_depuis_lignes",
]
