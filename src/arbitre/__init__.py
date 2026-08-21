"""Arbitre & orchestration (PRD 3) — le bloc qui assemble les trois autres.

Il ne réimplémente ni les règles (PRD 1), ni les prompts (PRD 2), ni les
schémas de logs (PRD 4) : il tient la boucle et garantit les invariants
d'orchestration que personne d'autre ne peut garantir — donnes communes aux
trois conditions, gel de la mémoire avant chaque manche, atomicité de la
manche, frontière de série, reprise sur incident, intégrité de clôture.

    from arbitre import Condition, ConfigRun, preparer_run

    config = ConfigRun(condition=Condition.SM, bot="Station", replication=1, K=20)
    arbitre = preparer_run(config, home_source=r"C:\\Users\\videt\\AppData\\Local\\hermes")
    arbitre.jouer()
    rapport = arbitre.clore()

En ligne de commande : `python -m arbitre --condition SM --bot Station --K 20 --series 1`.
"""

from harnais import Condition

from .alea import (
    ATTRIBUTIONS,
    GRAINE_CAMPAGNE,
    Donne,
    affecter_machines,
    donne,
    flux_bot,
    flux_divers,
    graine_derivee,
    hash_donnes,
    position_agent,
    sequence_donnes,
)
from .etat import (
    EtatRun,
    ecarter_tours_abandonnes,
    recaps_logues,
    series_closes,
    synchroniser,
)
from .integrite import RapportIntegrite, poser_temoin, verifier_run, verifier_temoin
from .mesure import (
    MARGE_PLATEAU,
    MesureSerie,
    Plateau,
    evaluer_plateau,
    mesurer_serie,
    pente_regression,
)
from .recap import Recapitulateur, ligne_manche
from .run import (
    K_DEFAUT,
    SERIES_MAX,
    SERIES_SM,
    TENTATIVES_MANCHE,
    Arbitre,
    ConfigRun,
    ErreurArbitre,
    MancheJouee,
    PriseDeDecision,
    identifiant,
    matrice_campagne,
    preparer_run,
    racine_defaut,
)

__all__ = [
    "ATTRIBUTIONS",
    "GRAINE_CAMPAGNE",
    "K_DEFAUT",
    "MARGE_PLATEAU",
    "SERIES_MAX",
    "SERIES_SM",
    "TENTATIVES_MANCHE",
    "Arbitre",
    "Condition",
    "ConfigRun",
    "Donne",
    "ErreurArbitre",
    "EtatRun",
    "MancheJouee",
    "MesureSerie",
    "Plateau",
    "PriseDeDecision",
    "RapportIntegrite",
    "Recapitulateur",
    "affecter_machines",
    "donne",
    "ecarter_tours_abandonnes",
    "evaluer_plateau",
    "flux_bot",
    "flux_divers",
    "graine_derivee",
    "hash_donnes",
    "identifiant",
    "ligne_manche",
    "matrice_campagne",
    "mesurer_serie",
    "pente_regression",
    "poser_temoin",
    "position_agent",
    "preparer_run",
    "racine_defaut",
    "recaps_logues",
    "sequence_donnes",
    "series_closes",
    "synchroniser",
    "verifier_run",
    "verifier_temoin",
]
