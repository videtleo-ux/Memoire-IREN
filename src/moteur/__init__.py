"""Moteur de jeu obfusqué, meilleure réponse et écart d'exploitation (PRD 1).

Instrument de mesure du projet, sans aucune dépendance réseau ni LLM. Les
autres modules importent l'énumération des info-sets et les fonctions de
mesure d'ici, et ne les redéfinissent jamais (PRD 1 §9).

    from moteur import GTO, STATION, ecart, meilleure_reponse

    ecart(pi_chapeau, STATION)  # → Écart(s) de la spec §4, exact
"""

from .infosets import (
    ACTIONS_LEGALES,
    CARTES,
    INFOSETS,
    POSITIONS,
    Action,
    Carte,
    Contexte,
    InfoSet,
    Politique,
    Position,
    construire_politique,
    infoset,
    infosets_de_position,
    numero,
    valider_politique,
)
from .lexique import (
    HASH_LEXIQUE,
    VERSION_LEXIQUE,
    lire_action,
    lire_carte,
    rendre_action,
    rendre_carte,
    violations_obfuscation,
)
from .meilleure_reponse import (
    ResultatMeilleureReponse,
    completer_politique,
    ecart,
    ecart_recitation,
    infosets_atteignables,
    meilleure_reponse,
    poids_contrefactuels,
    politique_pure,
)
from .politiques import ALPHA_DEFAUT, BOTS, GTO, OVER_FOLDER, STATION, gto
from .regles import (
    DONNES,
    PROBA_DONNE,
    Decideur,
    ResultatManche,
    decideur_depuis_politique,
    ev,
    ev_moyenne,
    jouer_manche,
    valeur_du_jeu,
)

__all__ = [
    "ACTIONS_LEGALES",
    "ALPHA_DEFAUT",
    "BOTS",
    "CARTES",
    "DONNES",
    "GTO",
    "HASH_LEXIQUE",
    "INFOSETS",
    "OVER_FOLDER",
    "POSITIONS",
    "PROBA_DONNE",
    "STATION",
    "VERSION_LEXIQUE",
    "Action",
    "Carte",
    "Contexte",
    "Decideur",
    "InfoSet",
    "Politique",
    "Position",
    "ResultatManche",
    "ResultatMeilleureReponse",
    "completer_politique",
    "construire_politique",
    "decideur_depuis_politique",
    "ecart",
    "ecart_recitation",
    "ev",
    "ev_moyenne",
    "gto",
    "infoset",
    "infosets_atteignables",
    "infosets_de_position",
    "jouer_manche",
    "lire_action",
    "lire_carte",
    "meilleure_reponse",
    "numero",
    "poids_contrefactuels",
    "politique_pure",
    "rendre_action",
    "rendre_carte",
    "valeur_du_jeu",
    "valider_politique",
    "violations_obfuscation",
]
