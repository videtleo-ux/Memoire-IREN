"""Logging, CSV dérivés et détecteur de dé-obfuscation (PRD 4).

JSONL = source de vérité (append-only, une ligne par événement) ; CSV =
vue d'analyse régénérable ; détecteur = observation, jamais censure.

    from journal import ContexteRun, JournalRun, EvenementTour, analyser

    journal = JournalRun(dossier_logs, ContexteRun(run_id="AE-station-r2", ...))
    journal.ecrire_tour(EvenementTour(...))      # validé avant écriture
    journal.ecrire_session(EvenementSession(...))

Deux exécutables :

- `python -m journal.derives <racine> --sortie <dossier>` — régénère
  `sessions.csv`, `infosets.csv`, `memoire.csv`.
- `python -m journal.rejouer <dossier logs>` — re-règle chaque manche depuis
  les seuls logs et vérifie que les mesures loguées se retrouvent
  (« tout est reconstructible », PRD 4 §7.1).
"""

from .deobfuscation import (
    NIVEAU_DEOBFUSCATION,
    NIVEAU_RECITATION,
    Drapeau,
    analyser,
    analyser_lot,
    compter,
)
from .derives import generer
from .ecrivains import (
    FICHIER_SESSIONS,
    FICHIER_TOURS,
    JournalRun,
    lire_jsonl,
    lire_sessions,
    lire_tours,
)
from .rejouer import Rapport, estimer_pi_hat, rejouer_run
from .schemas import (
    VERSION_ARENE,
    ContexteRun,
    EtatReel,
    EvenementSession,
    EvenementTour,
    LigneInvalide,
    Mesures,
    valider_session,
    valider_tour,
)

__all__ = [
    "FICHIER_SESSIONS",
    "FICHIER_TOURS",
    "NIVEAU_DEOBFUSCATION",
    "NIVEAU_RECITATION",
    "VERSION_ARENE",
    "ContexteRun",
    "Drapeau",
    "EtatReel",
    "EvenementSession",
    "EvenementTour",
    "JournalRun",
    "LigneInvalide",
    "Mesures",
    "Rapport",
    "analyser",
    "analyser_lot",
    "compter",
    "estimer_pi_hat",
    "generer",
    "lire_jsonl",
    "lire_sessions",
    "lire_tours",
    "rejouer_run",
    "valider_session",
    "valider_tour",
]
