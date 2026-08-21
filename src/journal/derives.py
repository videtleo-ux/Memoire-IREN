"""CSV dérivés — la vue d'analyse (PRD 4 §5).

Régénérables à tout moment depuis les JSONL, **jamais** édités à la main,
jamais source de vérité. Trois fichiers :

- `sessions.csv` — une ligne par série. C'est *le* fichier du mémoire :
  quelques centaines de lignes, toutes les courbes et tous les tests en
  sortent.
- `infosets.csv` — une ligne par (série × info-set), avec `p` et l'effectif
  `n` : sur quel info-set l'agent apprend-il d'abord ? le bluff au sceau le
  plus faible disparaît-il face à Station ?
- `memoire.csv` — une ligne par frontière : taille des notes, entrées ±,
  overflow, hits de dé-obfuscation. La trajectoire du canal mémoire.

Usage : `python -m journal.derives C:\\arene-runs --sortie C:\\arene-runs\\csv`
balaie tous les runs présents et écrit les trois fichiers.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .ecrivains import FICHIER_SESSIONS, lire_jsonl

COLONNES_SESSIONS = (
    "run_id",
    "condition",
    "bot",
    "replication",
    "machine",
    "session",
    "K",
    "ecart",
    "reference_recite",
    "ev_pi_hat",
    "ev_br",
    "ev_realisee",
    "actions_par_defaut",
    "relances",
    "erreurs_harnais",
    "n_flags_deobf",
    "n_flags_recitation",
    "ecritures_intra_serie",
    "plateau_declare",
    "cout_tokens_in",
    "cout_tokens_out",
)

COLONNES_INFOSETS = ("run_id", "condition", "bot", "replication", "session", "infoset", "p", "n")

COLONNES_MEMOIRE = (
    "run_id",
    "condition",
    "bot",
    "replication",
    "session",
    "taille_m_s",
    "taille_m_s1",
    "entrees_m_s",
    "entrees_m_s1",
    "ajouts",
    "suppressions",
    "elagages",
    "overflows",
    "n_flags_deobf",
)


def _compter_niveau(drapeaux: Sequence[Mapping[str, Any]], niveau: str) -> int:
    return sum(1 for d in drapeaux if d.get("niveau") == niveau)


def _compter_type(evenements: Sequence[Mapping[str, Any]], type_: str) -> int:
    return sum(1 for e in evenements if e.get("type") == type_)


def ligne_session(session: Mapping[str, Any]) -> dict[str, Any]:
    mesures = session["mesures"]
    defauts = session.get("defauts", {})
    memoire = session.get("memoire", {})
    drapeaux = session.get("drapeaux_deobfuscation", [])
    cout = session.get("cout_session_tokens", {})
    return {
        "run_id": session["run_id"],
        "condition": session["condition"],
        "bot": session["bot"],
        "replication": session["replication"],
        "machine": session["machine"],
        "session": session["session"],
        "K": session["K"],
        "ecart": mesures["ecart_exploitation"],
        "reference_recite": mesures["reference_recite"],
        "ev_pi_hat": mesures["ev_pi_hat"],
        "ev_br": mesures["ev_br"],
        "ev_realisee": mesures["ev_realisee"],
        "actions_par_defaut": defauts.get("actions_par_defaut"),
        "relances": defauts.get("relances"),
        "erreurs_harnais": defauts.get("erreurs_harnais"),
        "n_flags_deobf": _compter_niveau(drapeaux, "deobfuscation"),
        "n_flags_recitation": _compter_niveau(drapeaux, "recitation"),
        "ecritures_intra_serie": memoire.get("ecritures_intra_serie"),
        "plateau_declare": session.get("plateau", {}).get("declare"),
        "cout_tokens_in": cout.get("in"),
        "cout_tokens_out": cout.get("out"),
    }


def lignes_infosets(session: Mapping[str, Any]) -> list[dict[str, Any]]:
    pi_hat = session.get("pi_hat", {})
    lignes = []
    for infoset, valeurs in pi_hat.items():
        if not isinstance(valeurs, Mapping):  # `infosets_non_observes` : une liste
            continue
        lignes.append(
            {
                "run_id": session["run_id"],
                "condition": session["condition"],
                "bot": session["bot"],
                "replication": session["replication"],
                "session": session["session"],
                "infoset": infoset,
                "p": valeurs.get("p"),
                "n": valeurs.get("n"),
            }
        )
    return lignes


def ligne_memoire(session: Mapping[str, Any]) -> dict[str, Any] | None:
    """Une ligne par frontière **AE** : les autres conditions n'écrivent rien."""
    if session["condition"] != "AE":
        return None
    memoire = session.get("memoire", {})
    evenements = memoire.get("evenements", [])
    m_s = memoire.get("M_s", "") or ""
    m_s1 = memoire.get("M_s1", "") or ""
    drapeaux = [
        d for d in session.get("drapeaux_deobfuscation", []) if d.get("source") == "memoire"
    ]
    return {
        "run_id": session["run_id"],
        "condition": session["condition"],
        "bot": session["bot"],
        "replication": session["replication"],
        "session": session["session"],
        "taille_m_s": len(m_s),
        "taille_m_s1": len(m_s1),
        "entrees_m_s": memoire.get("entrees_m_s"),
        "entrees_m_s1": memoire.get("entrees_m_s1"),
        "ajouts": _compter_type(evenements, "ajout"),
        "suppressions": _compter_type(evenements, "suppression"),
        "elagages": _compter_type(evenements, "elagage"),
        "overflows": _compter_type(evenements, "overflow"),
        "n_flags_deobf": len(drapeaux),
    }


def _ecrire_csv(chemin: Path, colonnes: Sequence[str], lignes: Iterable[Mapping[str, Any]]) -> int:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    compte = 0
    # `newline=""` : sans lui, le module csv doublerait les fins de ligne sous
    # Windows et R lirait une ligne vide sur deux.
    with chemin.open("w", encoding="utf-8", newline="") as fichier:
        redacteur = csv.DictWriter(fichier, fieldnames=list(colonnes))
        redacteur.writeheader()
        for ligne in lignes:
            redacteur.writerow(ligne)
            compte += 1
    return compte


def trouver_sessions(racine: Path | str) -> list[Path]:
    """Tous les `sessions.jsonl` sous une racine de runs, triés."""
    return sorted(Path(racine).rglob(FICHIER_SESSIONS))


def generer(racine: Path | str, sortie: Path | str) -> Mapping[str, int]:
    """Régénère les trois CSV depuis les JSONL trouvés sous `racine`."""
    sessions = [ligne for chemin in trouver_sessions(racine) for ligne in lire_jsonl(chemin)]
    sortie = Path(sortie)
    return {
        "sessions": _ecrire_csv(
            sortie / "sessions.csv", COLONNES_SESSIONS, (ligne_session(s) for s in sessions)
        ),
        "infosets": _ecrire_csv(
            sortie / "infosets.csv",
            COLONNES_INFOSETS,
            (ligne for s in sessions for ligne in lignes_infosets(s)),
        ),
        "memoire": _ecrire_csv(
            sortie / "memoire.csv",
            COLONNES_MEMOIRE,
            (ligne for s in sessions if (ligne := ligne_memoire(s)) is not None),
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("racine", help="racine des runs (contient les dossiers logs/)")
    analyseur.add_argument("--sortie", default="csv", help="dossier de sortie des CSV")
    arguments = analyseur.parse_args(argv)
    compte = generer(arguments.racine, arguments.sortie)
    for nom, lignes in compte.items():
        print(f"{nom}.csv : {lignes} lignes")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "COLONNES_INFOSETS",
    "COLONNES_MEMOIRE",
    "COLONNES_SESSIONS",
    "generer",
    "ligne_memoire",
    "ligne_session",
    "lignes_infosets",
    "main",
    "trouver_sessions",
]
