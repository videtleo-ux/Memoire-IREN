"""Détecteur de dé-obfuscation et de récitation (PRD 4 §4, spec §1.bis).

Deux drapeaux **distincts**, parce que leurs implications le sont :

- **dé-obfuscation** — l'agent nomme le jeu réel (« c'est du poker », « Kuhn »,
  « le valet »). C'est une contamination : l'agent ne joue plus le jeu qu'on
  lui a servi, il joue celui qu'il a reconnu.
- **récitation** — l'agent énonce des constantes d'équilibre sans nommer le
  jeu (« bluffer un tiers du temps », « Nash », « GTO », « alpha »). C'est
  précisément le comportement que les bots Station et Over-folder sont censés
  discriminer (spec §3/§4) : une stratégie récitée échoue dans les deux
  directions opposées.

Trois principes de fonctionnement :

1. **Aucune censure.** On observe, on n'intervient pas. Que faire d'un run
   contaminé est une décision d'analyse, documentée dans le mémoire.
2. **Le canal mémoire compte autant que les sorties.** Un hit dans
   `MEMORY.md` ou dans la fenêtre ICL se propage à toutes les séries
   suivantes : le drapeau de série porte donc aussi sur le contenu du slot.
3. **Insensible à la casse et aux accents**, mais **à mots entiers** : « Tor »
   ne doit rien déclencher, et « trois » ne doit pas déclencher « roi ».
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

NIVEAU_DEOBFUSCATION = "deobfuscation"
NIVEAU_RECITATION = "recitation"

#: Motifs appliqués sur le texte **plié** (minuscules, sans accents). Écrire
#: les motifs sans accent est donc volontaire : « equilibre » attrape aussi
#: « équilibre ».
MOTIFS: Mapping[str, tuple[tuple[str, str], ...]] = {
    NIVEAU_DEOBFUSCATION: (
        (r"\bkuhn\b", "nomme le jeu source"),
        (r"\bpoker\b", "nomme la famille de jeu"),
        (r"\b(valet|dame|roi)\b", "rang de carte (français)"),
        (r"\b(jack|queen|king)\b", "rang de carte (anglais)"),
        # Lettre isolée : l'apostrophe est explicitement exclue des deux
        # côtés, sinon « j'ai » et « qu'il » déclencheraient à chaque phrase.
        (r"(?<![\w'’])[jqk](?![\w'’])", "abréviation de rang"),
        (r"\b(cartes?|deck|paquet)\b", "vocabulaire de cartes"),
        (r"\b(mise[rs]?|relance[rs]?|pot|tapis|showdown|abattage)\b", "jargon du jeu source"),
    ),
    NIVEAU_RECITATION: (
        (r"\bnash\b", "équilibre nommé"),
        (r"\bgto\b", "stratégie d'équilibre nommée"),
        (r"\bequilibr\w*\b", "équilibre invoqué"),
        (r"\balpha\b", "paramètre d'équilibre"),
        (r"\bbluff\w*\b", "concept de bluff"),
        # Pas de `\b` en queue d'alternative : « 33 % » finit sur un caractère
        # non-mot, une frontière y échouerait toujours.
        (
            r"(?:\b1\s*/\s*3\b|\bun\s+tiers\b|\b0[.,]33+\b|\b33\s*%)",
            "constante d'équilibre",
        ),
        (r"\btheorie\s+des\s+jeux\b", "cadre théorique nommé"),
    ),
}

_COMPILES: Mapping[str, tuple[tuple[re.Pattern[str], str], ...]] = {
    niveau: tuple((re.compile(motif), raison) for motif, raison in motifs)
    for niveau, motifs in MOTIFS.items()
}

#: Fenêtre d'extrait conservée autour d'un hit, en caractères de part et
#: d'autre — assez pour juger à la relecture, assez peu pour ne pas recopier
#: la sortie entière dans le log de série.
MARGE_EXTRAIT = 60


def plier(texte: str) -> str:
    """Minuscules sans accents — l'espace de comparaison des motifs."""
    decompose = unicodedata.normalize("NFD", (texte or "").lower())
    return "".join(c for c in decompose if not unicodedata.combining(c))


@dataclass(frozen=True)
class Drapeau:
    """Un hit, avec de quoi le rejuger à la main (PRD 4 §4)."""

    niveau: str  # deobfuscation | recitation
    regle: str  # le motif déclenché
    raison: str
    extrait: str
    source: str = "sortie"  # sortie | memoire | slot | recap
    manche: int | None = None

    def en_json(self) -> dict[str, object]:
        return {
            "niveau": self.niveau,
            "regle": self.regle,
            "raison": self.raison,
            "extrait": self.extrait,
            "source": self.source,
            "manche": self.manche,
        }


def analyser(
    texte: str,
    source: str = "sortie",
    manche: int | None = None,
) -> tuple[Drapeau, ...]:
    """Tous les hits d'un texte, tous niveaux confondus.

    L'extrait est découpé dans le texte **plié** : on relit ce que le
    détecteur a vu, pas une reconstruction — un extrait qui ne contiendrait
    pas le motif serait pire qu'inutile lors de la revue manuelle.
    """
    plie = plier(texte)
    drapeaux: list[Drapeau] = []
    for niveau, motifs in _COMPILES.items():
        for motif, raison in motifs:
            for correspondance in motif.finditer(plie):
                debut = max(0, correspondance.start() - MARGE_EXTRAIT)
                fin = min(len(plie), correspondance.end() + MARGE_EXTRAIT)
                drapeaux.append(
                    Drapeau(
                        niveau=niveau,
                        regle=motif.pattern,
                        raison=raison,
                        extrait=plie[debut:fin].strip(),
                        source=source,
                        manche=manche,
                    )
                )
    return tuple(drapeaux)


def analyser_lot(textes: Iterable[tuple[str, str, int | None]]) -> tuple[Drapeau, ...]:
    """Analyse une série de `(texte, source, manche)` — usage arbitre."""
    drapeaux: list[Drapeau] = []
    for texte, source, manche in textes:
        drapeaux.extend(analyser(texte, source, manche))
    return tuple(drapeaux)


def compter(drapeaux: Sequence[Drapeau]) -> Mapping[str, int]:
    """Décompte par niveau — les deux colonnes du CSV de séries."""
    return {
        NIVEAU_DEOBFUSCATION: sum(1 for d in drapeaux if d.niveau == NIVEAU_DEOBFUSCATION),
        NIVEAU_RECITATION: sum(1 for d in drapeaux if d.niveau == NIVEAU_RECITATION),
    }


__all__ = [
    "MARGE_EXTRAIT",
    "MOTIFS",
    "NIVEAU_DEOBFUSCATION",
    "NIVEAU_RECITATION",
    "Drapeau",
    "analyser",
    "analyser_lot",
    "compter",
    "plier",
]
