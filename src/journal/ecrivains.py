"""Écriture des logs d'un run : `turns.jsonl` et `sessions.jsonl` (PRD 4 §1).

Append-only, une ligne par événement, UTF-8, `ensure_ascii=False` : les logs
se relisent tels quels sur les deux machines (critère PRD 4 §7.4) et un crash
en cours de série ne coûte que la ligne en cours d'écriture.

Chaque ligne est **validée avant d'être écrite** (PRD 4 §7.5). Une ligne
invalide fait échouer le run à l'instant où elle se produit, plutôt que
l'analyse trois semaines plus tard.

Le flush est immédiat : un run qui tourne des heures ne doit rien perdre
d'utile si la machine s'éteint. Le coût est négligeable devant la latence
d'un appel LLM.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping

from .schemas import (
    ContexteRun,
    EvenementSession,
    EvenementTour,
    horodatage,
    valider_session,
    valider_tour,
)

FICHIER_TOURS = "turns.jsonl"
FICHIER_SESSIONS = "sessions.jsonl"


def _serialiser(ligne: Mapping[str, Any]) -> str:
    return json.dumps(ligne, ensure_ascii=False, sort_keys=False)


@dataclass
class JournalRun:
    """Les deux fichiers de log d'un run, ouverts en append.

        journal = JournalRun(Path(r"C:\\arene-runs\\AE-station-r2\\logs"), contexte)
        journal.ecrire_tour(evenement)
        journal.ecrire_session(evenement)

    Réentrant : rouvrir un journal existant reprend l'append là où il en
    était — c'est ce qui permet la reprise sur incident du PRD 3 §8.
    """

    dossier: Path
    contexte: ContexteRun

    def __post_init__(self) -> None:
        self.dossier = Path(self.dossier)
        self.dossier.mkdir(parents=True, exist_ok=True)

    @property
    def chemin_tours(self) -> Path:
        return self.dossier / FICHIER_TOURS

    @property
    def chemin_sessions(self) -> Path:
        return self.dossier / FICHIER_SESSIONS

    def _ligne(self, charge: Mapping[str, Any]) -> dict[str, Any]:
        return {**self.contexte.en_json(), "horodatage": horodatage(), **charge}

    def ecrire_tour(self, evenement: EvenementTour) -> Mapping[str, Any]:
        ligne = self._ligne(evenement.en_json())
        valider_tour(ligne)
        self._ajouter(self.chemin_tours, ligne)
        return ligne

    def ecrire_session(self, evenement: EvenementSession) -> Mapping[str, Any]:
        ligne = self._ligne(evenement.en_json())
        valider_session(ligne)
        self._ajouter(self.chemin_sessions, ligne)
        return ligne

    @staticmethod
    def _ajouter(chemin: Path, ligne: Mapping[str, Any]) -> None:
        with chemin.open("a", encoding="utf-8", newline="\n") as fichier:
            fichier.write(_serialiser(ligne) + "\n")
            fichier.flush()


def lire_jsonl(chemin: Path | str) -> Iterator[dict[str, Any]]:
    """Relit un fichier JSONL ligne à ligne.

    Les lignes vides sont tolérées (fin de fichier après un crash) ; une ligne
    tronquée, elle, lève — c'est un log corrompu, et le taire fausserait
    silencieusement l'analyse.
    """
    chemin = Path(chemin)
    if not chemin.is_file():
        return
    with chemin.open(encoding="utf-8") as fichier:
        for numero, ligne in enumerate(fichier, start=1):
            if not ligne.strip():
                continue
            try:
                yield json.loads(ligne)
            except ValueError as exc:
                raise ValueError(f"{chemin}, ligne {numero} : JSON invalide ({exc})") from None


def lire_tours(dossier: Path | str) -> Iterator[dict[str, Any]]:
    return lire_jsonl(Path(dossier) / FICHIER_TOURS)


def lire_sessions(dossier: Path | str) -> Iterator[dict[str, Any]]:
    return lire_jsonl(Path(dossier) / FICHIER_SESSIONS)


__all__ = [
    "FICHIER_SESSIONS",
    "FICHIER_TOURS",
    "JournalRun",
    "lire_jsonl",
    "lire_sessions",
    "lire_tours",
]
