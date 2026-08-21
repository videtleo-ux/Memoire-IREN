"""Extraction de l'action depuis la sortie libre du modèle (PRD 2 §4).

Deux passes, dans cet ordre :

1. **Stricte** — la dernière ligne de la forme `ACTION: <terme>` (le format
   imposé par la consigne). Tolère la casse, les accents, le gras Markdown et
   la ponctuation finale, rien de plus.
2. **De repli** — le dernier terme d'action valide trouvé dans la sortie
   entière. Sur « je ne vais pas couvrir, je préfère me retirer », c'est bien
   « se retirer » qui est retenu : la dernière décision énoncée est la bonne.

Les deux passes n'acceptent qu'une action **légale à l'info-set courant** : un
« engager » servi face à un engagement adverse est traité comme une sortie
inexploitable, pas comme une action illégale à jouer.

Ce module ne décide pas de la relance ni du défaut passif : c'est le rôle du
harnais (`conditions.py`), qui compte aussi les drapeaux pour les logs.
"""

from __future__ import annotations

import re
import unicodedata
from enum import Enum
from typing import Mapping, Sequence

from moteur import Action
from moteur.lexique import ACTIONS, enregistrer_textes


class Parsing(Enum):
    """Comment l'action a été obtenue — logué tel quel (PRD 4 §2)."""

    OK = "ok"  # format respecté du premier coup
    REPLI = "repli"  # terme récupéré hors du format `ACTION:`
    RELANCE = "relance"  # obtenu après une relance de format
    DEFAUT = "defaut"  # échec : action passive imposée par le harnais


def _plier(texte: str) -> str:
    """Minuscules sans accents — la comparaison des termes s'y fait."""
    decompose = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in decompose if not unicodedata.combining(c))


#: Termes obfusqués pliés → action canonique. Seuls ceux-là sont acceptés
#: sur la ligne `ACTION:` : le format imposé n'admet pas de paraphrase.
_TERMES: Mapping[str, Action] = {_plier(nom): action for action, nom in ACTIONS.items()}

#: Formes fléchies acceptées **uniquement** par la passe de repli. Sans elles,
#: « je vais couvrir, non, je me retire » se lirait « couvrir » : le seul terme
#: canonique de la phrase n'est pas celui de la décision. Les accents ayant
#: déjà été pliés, « engagé » et « retiré » se ramènent à « engage » et
#: « retire ».
_VARIANTES: Mapping[str, Action] = {
    **_TERMES,
    "retiens": Action.CHECK,
    "retient": Action.CHECK,
    "retenez": Action.CHECK,
    "retenu": Action.CHECK,
    "engage": Action.BET,
    "engages": Action.BET,
    "engagez": Action.BET,
    "couvre": Action.CALL,
    "couvres": Action.CALL,
    "couvrez": Action.CALL,
    "couvert": Action.CALL,
    "retirer": Action.FOLD,
    "retire": Action.FOLD,
    "retires": Action.FOLD,
    "retirez": Action.FOLD,
}

#: Motif de recherche du repli, formes longues d'abord pour que « se retirer »
#: l'emporte sur « retirer » et « couvrez » sur « couvre ».
_MOTIF_TERMES = re.compile(
    r"\b(" + "|".join(sorted((re.escape(t) for t in _VARIANTES), key=len, reverse=True)) + r")\b"
)

#: Ligne de sortie imposée. Le gras Markdown (`**ACTION:** couvrir`) est
#: fréquent chez les modèles bavards et ne doit pas coûter une relance.
_MOTIF_LIGNE = re.compile(r"^[\s*_#>-]*action\s*[:：]\s*(.+?)\s*$")


def _nettoyer(fragment: str) -> str:
    return fragment.strip().strip("*_`\"'«».;,!?()[] \t")


def extraire_action(sortie: str, actions_legales: Sequence[Action]) -> tuple[Action | None, Parsing]:
    """Rend l'action lue et la façon dont elle a été obtenue.

    `(None, Parsing.DEFAUT)` signale une sortie inexploitable ; l'appelant
    décide alors de relancer ou d'imposer l'action passive.
    """
    legales = frozenset(actions_legales)
    plie = _plier(sortie or "")

    for ligne in reversed(plie.splitlines()):
        correspondance = _MOTIF_LIGNE.match(ligne)
        if not correspondance:
            continue
        action = _TERMES.get(_nettoyer(correspondance.group(1)))
        if action is not None and action in legales:
            return action, Parsing.OK
        # Une ligne `ACTION:` illisible ou illégale ne clôt pas la recherche :
        # le repli peut encore trouver le terme ailleurs dans la sortie.
        break

    dernier: Action | None = None
    for correspondance in _MOTIF_TERMES.finditer(plie):
        action = _VARIANTES[correspondance.group(1)]
        if action in legales:
            dernier = action
    if dernier is not None:
        return dernier, Parsing.REPLI

    return None, Parsing.DEFAUT


#: Rappel ajouté au prompt lors de l'unique relance de format (PRD 2 §4). Le
#: contexte étant neuf à chaque invocation, la relance rejoue le prompt entier
#: augmenté de ce paragraphe — pas un échange de suivi.
RAPPEL_FORMAT = (
    "[FORMAT]\n"
    "Votre réponse précédente n'était pas exploitable. Reprenez la même "
    "décision et répondez cette fois avec, en dernière ligne et seule sur sa "
    "ligne :\n"
    "ACTION: <l'action choisie>"
)

enregistrer_textes({"gabarit.rappel_format": RAPPEL_FORMAT})


__all__ = ["RAPPEL_FORMAT", "Parsing", "extraire_action"]
