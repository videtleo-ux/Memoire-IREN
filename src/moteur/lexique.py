"""Lexique obfusqué — point unique du mapping canonique ↔ obfusqué (D5, PRD 1 §2).

Le moteur, les logs internes et les tests parlent le langage canonique
(`Carte.C0 < C1 < C2`, check/bet/call/fold). Tout ce qui est **servi à
l'agent** passe par ce module, et par lui seul. Le mapping est versionné et
haché : le hash part dans les logs de session (PRD 4) pour prouver que les 27
runs ont vu le même vocabulaire.

Les gabarits de prompt complets (texte des règles, vue d'une manche, consigne
de format) relèvent du PRD 2 ; ce module fournit le vocabulaire et le filet
de sécurité (`MOTIFS_INTERDITS`, `textes_destines_a_lagent`) sur lequel le
test de non-régression T8 s'appuie dès maintenant, et qui couvrira les
gabarits dès qu'ils existeront.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Mapping, MutableMapping

from .infosets import Action, Carte

VERSION_LEXIQUE = "1.0"

#: Nom du jeu servi à l'agent.
NOM_DU_JEU = "L'Épreuve des Trois Sceaux"

#: Jetons : Tor ≺ Vael ≺ Rhun. La dominance est énoncée explicitement à
#: l'agent, jamais laissée à déduire d'un ordre alphabétique ou numérique.
JETONS: Mapping[Carte, str] = {
    Carte.C0: "Tor",
    Carte.C1: "Vael",
    Carte.C2: "Rhun",
}

#: Énoncé de dominance servi à l'agent (spec §1.bis : l'ordre doit être dit).
DOMINANCE = "Rhun bat Vael, Vael bat Tor."

#: Actions obfusquées.
ACTIONS: Mapping[Action, str] = {
    Action.CHECK: "retenir",
    Action.BET: "engager",
    Action.CALL: "couvrir",
    Action.FOLD: "se retirer",
}

_JETONS_INVERSE: Mapping[str, Carte] = {nom.lower(): carte for carte, nom in JETONS.items()}
_ACTIONS_INVERSE: Mapping[str, Action] = {nom.lower(): action for action, nom in ACTIONS.items()}


def rendre_carte(carte: Carte) -> str:
    return JETONS[carte]


def rendre_action(action: Action) -> str:
    return ACTIONS[action]


def lire_carte(texte: str) -> Carte:
    """Parse un jeton obfusqué. Lève `ValueError` si inconnu."""
    try:
        return _JETONS_INVERSE[texte.strip().lower()]
    except KeyError:
        raise ValueError(f"jeton inconnu : {texte!r}") from None


def lire_action(texte: str) -> Action:
    """Parse une action obfusquée. Lève `ValueError` si inconnue.

    Le parsing tolérant des sorties LLM (verbe noyé dans une phrase, casse,
    accents) relève du PRD 2 ; ici, la correspondance stricte fait foi.
    """
    try:
        return _ACTIONS_INVERSE[texte.strip().lower()]
    except KeyError:
        raise ValueError(f"action inconnue : {texte!r}") from None


def _empreinte() -> str:
    """Hash stable du mapping, à loguer par session (PRD 4)."""
    charge = json.dumps(
        {
            "version": VERSION_LEXIQUE,
            "jeu": NOM_DU_JEU,
            "dominance": DOMINANCE,
            "jetons": {carte.name: nom for carte, nom in JETONS.items()},
            "actions": {action.name: nom for action, nom in ACTIONS.items()},
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(charge.encode("utf-8")).hexdigest()[:12]


HASH_LEXIQUE = _empreinte()


# --------------------------------------------------------------------------
# Filet de sécurité obfuscation (T8)
# --------------------------------------------------------------------------

#: Motifs interdits dans tout texte visible de l'agent (PRD 1 §2). Testés en
#: insensible à la casse. Sur les rangs numériques, seule la forme
#: « <mot de carte> 1/2/3 » est interdite : « droit d'entrée 1 » et « pot = 2 »
#: sont des montants légitimes des règles.
MOTIFS_INTERDITS: tuple[tuple[str, str], ...] = (
    (r"kuhn", "nom du jeu source"),
    (r"poker", "famille de jeu source"),
    (r"\b(valet|dame|roi|as)\b", "rangs de cartes (français)"),
    (r"\b(jack|queen|king|ace)\b", "rangs de cartes (anglais)"),
    (r"\b[JQK]\b", "abréviations de rangs"),
    (
        r"\b(carte|cartes|jeton|jetons|sceau|sceaux|rang|rangs)\b[^.\n]{0,12}\b[123]\b",
        "rang numérique",
    ),
    (
        r"\b(haute?s?|moyenn?e?s?|basse?s?|fort|faible|premi(er|ère)|deuxième|troisième)\b",
        "label ordinal évocateur",
    ),
    (r"\b(bluff\w*|mise[rs]?|relance\w*|tapis|abattage|showdown|pot)\b", "jargon du jeu source"),
)

_MOTIFS_COMPILES = tuple(
    (re.compile(motif, re.IGNORECASE), raison) for motif, raison in MOTIFS_INTERDITS
)


#: Textes déclarés par les couches supérieures (gabarits du PRD 2). Le
#: registre est alimenté à l'import du module qui les définit.
_TEXTES_ENREGISTRES: MutableMapping[str, str] = {}


def enregistrer_textes(textes: Mapping[str, str]) -> None:
    """Déclare des textes servis à l'agent pour qu'ils entrent dans T8.

    Appelé par `harnais.gabarits` (règles, rubriques, consignes) : le balayage
    d'obfuscation couvre ainsi les gabarits sans que ce module ait à connaître
    le harnais — l'inversion de dépendance évite un cycle d'import.
    """
    _TEXTES_ENREGISTRES.update(textes)


def textes_destines_a_lagent() -> Mapping[str, str]:
    """Tous les textes actuellement servis à l'agent, étiquetés.

    Contient le vocabulaire de ce module, plus tout ce qu'une couche
    supérieure a déclaré via `enregistrer_textes` — la couverture de T8
    grandit donc automatiquement avec le harnais, **à condition** que le
    module de gabarits ait été importé (`tests/test_harnais.py` s'en charge
    pour les gabarits du PRD 2).
    """
    textes: dict[str, str] = {
        "nom_du_jeu": NOM_DU_JEU,
        "dominance": DOMINANCE,
    }
    textes.update({f"jeton.{carte.name}": nom for carte, nom in JETONS.items()})
    textes.update({f"action.{action.name}": nom for action, nom in ACTIONS.items()})
    textes.update(_TEXTES_ENREGISTRES)
    return textes


def violations_obfuscation(texte: str) -> tuple[tuple[str, str], ...]:
    """Motifs interdits trouvés dans un texte : tuples (extrait, raison).

    Vide = conforme. Réutilisé par le détecteur de dé-obfuscation du PRD 4,
    qui applique les mêmes motifs aux **sorties** de l'agent.
    """
    trouvees: list[tuple[str, str]] = []
    for motif, raison in _MOTIFS_COMPILES:
        for correspondance in motif.finditer(texte):
            trouvees.append((correspondance.group(0), raison))
    return tuple(trouvees)


__all__ = [
    "ACTIONS",
    "DOMINANCE",
    "HASH_LEXIQUE",
    "JETONS",
    "MOTIFS_INTERDITS",
    "NOM_DU_JEU",
    "VERSION_LEXIQUE",
    "enregistrer_textes",
    "lire_action",
    "lire_carte",
    "rendre_action",
    "rendre_carte",
    "textes_destines_a_lagent",
    "violations_obfuscation",
]
