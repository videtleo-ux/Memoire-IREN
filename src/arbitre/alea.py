"""Aléa contrôlé : trois flux seedés, appariés entre conditions (PRD 3 §4).

C'est le point du projet où un bug ne se voit dans aucun log : si les trois
conditions ne reçoivent pas les mêmes donnes à (r, s, k) égal, les
comparaisons inter-conditions perdent la réduction de variance des nombres
aléatoires communs — et rien, dans les résultats, ne le signalera. D'où deux
partis pris :

1. **Dérivation, pas génération.** La donne d'une manche est une fonction pure
   de `(graine, étiquette, réplication, série, manche)` : aucun état de
   générateur ne circule d'une manche à l'autre, donc aucune dérive possible.
   Deux conditions au même (r, s, k) tirent le même index, octet pour octet,
   même si l'une des deux a joué mille manches de plus.
2. **Un flux par usage, seedé par manche.** Les tirages du bot GTO passent par
   un `Random` seedé sur les mêmes coordonnées : si l'agent joue différemment
   d'une condition à l'autre, la divergence reste confinée à la manche
   concernée au lieu de décaler tout le reste de la série.

Dans cet arbre, les points de décision du bot forment une chaîne déterministe
(en J1 : ouverture puis, éventuellement, face à une mise ; en J2 : une seule
décision) : le n-ième tirage de la manche correspond donc toujours au même
nœud, quelle que soit la façon dont l'agent a joué.

| Flux | Sert à | Partagé entre |
|---|---|---|
| `donne` | permutation des 3 sceaux (agent, bot, écarté) | les 3 conditions **et** les 3 bots |
| `flux_bot` | tirages du bot GTO | les 3 conditions |
| `flux_divers` | affectation machines, échantillonnages | rien |
"""

from __future__ import annotations

import hashlib
import random
from itertools import permutations
from typing import Iterable, Mapping, NamedTuple, Sequence

from moteur import CARTES, Carte, Position

#: Graine maîtresse de campagne : figée une fois pour toutes, loguée dans
#: `etat_run.json` de chaque run. La changer invalide l'appariement de tous
#: les runs déjà joués — elle ne se touche pas en cours de campagne.
GRAINE_CAMPAGNE = "arene-kuhn-2026"

ETIQUETTE_DONNES = "donnes"
ETIQUETTE_BOT = "bot"
ETIQUETTE_DIVERS = "divers"

#: Les 6 attributions ordonnées possibles (sceau de l'agent, sceau du bot,
#: sceau écarté). Ordre figé par `itertools.permutations` sur l'énumération du
#: moteur : c'est lui qui rend l'index reproductible.
ATTRIBUTIONS: tuple[tuple[Carte, Carte, Carte], ...] = tuple(permutations(CARTES, 3))


class Donne(NamedTuple):
    """Une attribution de sceaux, du point de vue de l'agent."""

    agent: Carte
    bot: Carte
    ecartee: Carte


def graine_derivee(graine: str, etiquette: str, *coordonnees: object) -> int:
    """Entier de graine dérivé de `(graine, étiquette, coordonnées…)`.

    SHA-256 plutôt que `hash()` : ce dernier est randomisé par processus sous
    Python 3, deux exécutions ne donneraient pas la même chose.
    """
    materiel = "|".join([graine, etiquette, *(str(c) for c in coordonnees)])
    return int.from_bytes(hashlib.sha256(materiel.encode("utf-8")).digest(), "big")


def donne(graine: str, replication: int, session: int, manche: int) -> Donne:
    """Donne servie à (r, s, k) — identique pour les 3 conditions et les 3 bots.

    Le biais de modulo est de l'ordre de 6/2²⁵⁶ : indétectable, et le prix
    d'une dérivation sans état.
    """
    index = graine_derivee(graine, ETIQUETTE_DONNES, replication, session, manche)
    return Donne(*ATTRIBUTIONS[index % len(ATTRIBUTIONS)])


def position_agent(manche: int) -> Position:
    """Alternance stricte : manche impaire → l'agent ouvre (PRD 3 §2).

    Déterministe, donc identique partout par construction — et K pair implique
    exactement K/2 manches par position (critère d'acceptation §10.4).
    """
    return Position.J1 if manche % 2 else Position.J2


def flux_bot(graine: str, replication: int, session: int, manche: int) -> random.Random:
    """Générateur dédié aux tirages du bot pour **cette** manche (PRD 1 §4).

    Jamais celui des donnes : un bot stochastique qui puiserait dans le flux
    des donnes décalerait les cartes des conditions les unes par rapport aux
    autres dès son premier bluff.
    """
    return random.Random(graine_derivee(graine, ETIQUETTE_BOT, replication, session, manche))


def flux_divers(graine: str, *coordonnees: object) -> random.Random:
    """Tout le reste : affectation run→machine, échantillonnages d'analyse.

    Partagé avec rien — c'est justement ce qui le distingue des deux autres.
    """
    return random.Random(graine_derivee(graine, ETIQUETTE_DIVERS, *coordonnees))


# --------------------------------------------------------------------------
# Séquence de série et empreinte
# --------------------------------------------------------------------------


def sequence_donnes(graine: str, replication: int, session: int, K: int) -> tuple[Donne, ...]:
    """Les K donnes d'une série, dans l'ordre."""
    return tuple(donne(graine, replication, session, k) for k in range(1, K + 1))


def _serialiser(donnes: Sequence[Donne]) -> str:
    """Forme canonique hachée. `int()` explicite : le rendu par défaut d'un
    `IntEnum` a changé entre versions de Python, pas sa valeur entière."""
    return "|".join(
        f"{k}:{int(d.agent)}{int(d.bot)}{int(d.ecartee)}:{position_agent(k).value}"
        for k, d in enumerate(donnes, start=1)
    )


def hash_donnes(graine: str, replication: int, session: int, K: int) -> str:
    """Empreinte de la séquence de donnes d'une série (PRD 3 §8, PRD 4 §3).

    Deux runs appariés doivent afficher la même à (r, s) égal : c'est la
    vérification d'intégrité qui prouve *a posteriori* que l'appariement a
    tenu, sans avoir à rejouer quoi que ce soit.
    """
    materiel = _serialiser(sequence_donnes(graine, replication, session, K))
    return "sha256:" + hashlib.sha256(materiel.encode("utf-8")).hexdigest()[:32]


# --------------------------------------------------------------------------
# Affectation run → machine (PRD 3 §8, spec §8)
# --------------------------------------------------------------------------


def affecter_machines(
    runs: Iterable[str],
    machines: Sequence[str],
    graine: str = GRAINE_CAMPAGNE,
) -> Mapping[str, str]:
    """Affectation randomisée et reproductible des runs aux machines.

    Randomisée pour que l'effet-machine soit testable *a posteriori* (spec
    §8) ; reproductible pour que le plan de campagne se relise à l'identique
    après coup. Une seule machine → affectation triviale, l'effet-machine
    disparaît avec elle.
    """
    runs = list(runs)
    if not machines:
        raise ValueError("au moins une machine est nécessaire")
    tirage = flux_divers(graine, "affectation", len(runs), *machines)
    ordre = list(runs)
    tirage.shuffle(ordre)
    return {run: machines[i % len(machines)] for i, run in enumerate(ordre)}


__all__ = [
    "ATTRIBUTIONS",
    "ETIQUETTE_BOT",
    "ETIQUETTE_DIVERS",
    "ETIQUETTE_DONNES",
    "GRAINE_CAMPAGNE",
    "Donne",
    "affecter_machines",
    "donne",
    "flux_bot",
    "flux_divers",
    "graine_derivee",
    "hash_donnes",
    "position_agent",
    "sequence_donnes",
]
