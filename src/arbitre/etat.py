"""État de run et reprise sur incident (PRD 3 §8).

Un run, c'est des heures d'appels payants : il doit survivre à un plantage, à
une coupure réseau, à un `kill -9`. La règle du PRD est nette — **on reprend à
la frontière de série, jamais en milieu de série** : une série entamée puis
interrompue est rejouée entièrement, et ses tours partiels sont écartés.

Pourquoi les écarter plutôt que les laisser en place :

`turns.jsonl` doit contenir **une tentative et une seule** par série, sinon le
rejeu de complétude (PRD 4 §7.1) regroupe deux tentatives sur la même clé
(série, manche) et conclut à des donnes dupliquées. Les tours de la tentative
abandonnée sont donc déplacés vers `turns.abandonnes.jsonl`, marqués
`abandonnee` et numérotés par tentative : rien n'est perdu, rien n'est
falsifié, et le fichier canonique reste rejouable.

Deux sources de vérité, dans cet ordre :

1. `sessions.jsonl` — une ligne y est écrite **à la clôture** d'une série ;
   c'est donc lui qui dit ce qui est réellement acquis.
2. `etat_run.json` — la déclaration du run (identité, graine, paramètres) et
   un miroir de l'avancement, réécrit après chaque clôture.

Si les deux divergent (plantage entre les deux écritures), les logs
l'emportent : `etat_run.json` est reconstruit à partir d'eux.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, Mapping, Sequence

from journal import VERSION_ARENE, lire_sessions
from journal.ecrivains import FICHIER_TOURS

FICHIER_ETAT = "etat_run.json"

#: Tours d'une tentative abandonnée. Ignoré de `lire_tours` comme de
#: `journal.derives` : ils sont conservés pour l'audit, pas pour l'analyse.
FICHIER_TOURS_ABANDONNES = "turns.abandonnes.jsonl"


@dataclass
class EtatRun:
    """Ce qu'il faut connaître pour reprendre un run là où il s'est arrêté."""

    run_id: str
    condition: str
    bot: str
    replication: int
    machine: str
    graine: str
    K: int
    sessions_max: int
    version_arene: str = VERSION_ARENE
    derniere_session_close: int = -1
    ecarts: list[float] = field(default_factory=list)
    plateau_declare_a: int | None = None
    abandons: list[dict[str, Any]] = field(default_factory=list)
    canari: dict[str, Any] = field(default_factory=dict)
    demarre_le: str = ""
    maj_le: str = ""

    @property
    def prochaine_session(self) -> int:
        return self.derniere_session_close + 1

    def en_json(self) -> dict[str, Any]:
        return asdict(self)

    def enregistrer(self, dossier: Path | str) -> Path:
        """Écriture atomique : un plantage pendant la sauvegarde ne doit pas
        laisser derrière lui un fichier d'état tronqué — ce serait perdre
        précisément ce qui sert à se relever."""
        from journal.schemas import horodatage

        self.maj_le = horodatage()
        if not self.demarre_le:
            self.demarre_le = self.maj_le

        dossier = Path(dossier)
        dossier.mkdir(parents=True, exist_ok=True)
        cible = dossier / FICHIER_ETAT
        temporaire = cible.with_suffix(".json.tmp")
        temporaire.write_text(
            json.dumps(self.en_json(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        os.replace(temporaire, cible)
        return cible

    @classmethod
    def charger(cls, dossier: Path | str) -> "EtatRun | None":
        """Relit `etat_run.json`. Absent ou illisible → `None` (run neuf).

        Les clés inconnues sont ignorées : un état écrit par une version
        antérieure de l'arène doit rester relisible, quitte à perdre un champ.
        """
        chemin = Path(dossier) / FICHIER_ETAT
        if not chemin.is_file():
            return None
        try:
            donnees = json.loads(chemin.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        connus = {f.name for f in fields(cls)}
        return cls(**{cle: val for cle, val in donnees.items() if cle in connus})


# --------------------------------------------------------------------------
# Reconstitution depuis les logs
# --------------------------------------------------------------------------


def series_closes(dossier_logs: Path | str) -> dict[int, dict[str, Any]]:
    """Les séries effectivement closes, indexées par numéro."""
    return {ligne["session"]: ligne for ligne in lire_sessions(dossier_logs)}


def synchroniser(etat: EtatRun, dossier_logs: Path | str) -> EtatRun:
    """Recale l'état sur `sessions.jsonl` — les logs font foi (§8).

    Rejoue aussi le critère de plateau depuis les lignes de série : la série
    à laquelle il a été déclaré se relit, elle n'a pas à être crue sur parole.
    """
    closes = series_closes(dossier_logs)
    if not closes:
        etat.derniere_session_close = -1
        etat.ecarts = []
        etat.plateau_declare_a = None
        return etat

    ordre = sorted(closes)
    etat.derniere_session_close = max(ordre)
    etat.ecarts = [float(closes[s]["mesures"]["ecart_exploitation"]) for s in ordre]
    declarees = [s for s in ordre if closes[s].get("plateau", {}).get("declare")]
    etat.plateau_declare_a = declarees[0] if declarees else None
    return etat


def series_manquantes(closes: Mapping[int, Any], derniere: int) -> list[int]:
    """Trous dans la numérotation des séries closes — anomalie d'intégrité."""
    return [s for s in range(derniere + 1) if s not in closes]


# --------------------------------------------------------------------------
# Tentative abandonnée
# --------------------------------------------------------------------------


def ecarter_tours_abandonnes(
    dossier_logs: Path | str,
    a_partir_de: int,
    tentative: int = 1,
) -> int:
    """Déplace les tours des séries ≥ `a_partir_de` vers le fichier d'abandons.

    Rend le nombre de tours écartés. La réécriture de `turns.jsonl` est le
    seul moment de la vie d'un run où ce fichier n'est pas strictement en
    ajout : c'est une opération de relèvement, faite avant que la moindre
    manche de la reprise ne soit jouée, et jamais pendant une série.
    """
    dossier = Path(dossier_logs)
    chemin = dossier / FICHIER_TOURS
    if not chemin.is_file():
        return 0

    gardes: list[str] = []
    abandonnes: list[dict[str, Any]] = []
    with chemin.open(encoding="utf-8") as fichier:
        for ligne in fichier:
            if not ligne.strip():
                continue
            donnees = json.loads(ligne)
            if donnees.get("session", -1) >= a_partir_de:
                donnees["abandonnee"] = True
                donnees["tentative"] = tentative
                abandonnes.append(donnees)
            else:
                gardes.append(ligne.rstrip("\n"))

    if not abandonnes:
        return 0

    with (dossier / FICHIER_TOURS_ABANDONNES).open(
        "a", encoding="utf-8", newline="\n"
    ) as sortie:
        for donnees in abandonnes:
            sortie.write(json.dumps(donnees, ensure_ascii=False) + "\n")

    temporaire = chemin.with_suffix(".jsonl.tmp")
    temporaire.write_text(
        "".join(f"{ligne}\n" for ligne in gardes), encoding="utf-8", newline="\n"
    )
    os.replace(temporaire, chemin)
    return len(abandonnes)


def recaps_logues(dossier_logs: Path | str) -> Sequence[tuple[int, str]]:
    """Les récaps des séries closes, dans l'ordre — matière de la reprise ICL.

    La condition ICL garde sa fenêtre en mémoire vive : après un plantage, il
    faut la reconstruire. Les récaps sont logués avec les séries précisément
    pour ça (et parce qu'ils sont, pour ICL, le contenu même de la mémoire).
    """
    closes = series_closes(dossier_logs)
    return [(s, closes[s].get("memoire", {}).get("recap", "")) for s in sorted(closes)]


__all__ = [
    "FICHIER_ETAT",
    "FICHIER_TOURS_ABANDONNES",
    "EtatRun",
    "ecarter_tours_abandonnes",
    "recaps_logues",
    "series_closes",
    "series_manquantes",
    "synchroniser",
]
