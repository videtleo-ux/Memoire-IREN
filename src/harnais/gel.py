"""Gel intra-série de la mémoire, imposé au niveau fichiers (décision D2).

Hermes persiste ses écritures mémoire **immédiatement** sur disque ; seul le
prompt système est figé le temps d'une invocation. Or une série d'arène, c'est
K invocations successives : sans verrou, l'agent pourrait modifier `M_s` en
cours de série et le « gel intra-session » de la spec §6 serait violé sans que
rien ne le signale.

D'où le protocole, orchestré par l'arbitre :

1. `capturer` le dossier mémoire à l'ouverture de la série → `M_s` ;
2. `restaurer` ce snapshot **avant chaque manche** ; toute écriture faite
   pendant la série est ainsi jetée ;
3. `fichiers_modifies` juste après la manche : une écriture jetée reste un
   **observable** (l'agent tente-t-il d'écrire pendant qu'il joue ?) et part
   dans les logs sous le drapeau `ecriture_intra_serie`.

L'écriture réelle n'a lieu qu'à l'étape de réflexion, hors gel.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

#: Nom du dossier mémoire d'Hermes, relatif à `HERMES_HOME` (vérifié dans
#: `tools/memory_tool.py` : `get_hermes_home() / "memories"`).
DOSSIER_MEMOIRE = "memories"

#: Fichier de notes auto-écrites — l'unique canal d'apprentissage autorisé
#: (spec §6). `USER.md` vit dans le même dossier et est neutralisé par la
#: config du store, mais il est tout de même gelé et surveillé.
FICHIER_NOTES = "MEMORY.md"

#: Séparateur d'entrées du store Hermes (`tools/memory_tool.py`,
#: `ENTRY_DELIMITER`). C'est lui qui rend le diff d'entrées exact plutôt
#: qu'heuristique.
SEPARATEUR_ENTREES = "\n§\n"


@dataclass(frozen=True)
class Snapshot:
    """Contenu binaire figé d'un dossier mémoire, à un instant donné."""

    fichiers: Mapping[str, bytes]

    @property
    def notes(self) -> str:
        """Contenu de `MEMORY.md` (chaîne vide s'il n'existe pas)."""
        return self.fichiers.get(FICHIER_NOTES, b"").decode("utf-8")

    @property
    def entrees(self) -> tuple[str, ...]:
        """Entrées de `MEMORY.md`, découpées au séparateur d'Hermes."""
        return decouper_entrees(self.notes)


def decouper_entrees(notes: str) -> tuple[str, ...]:
    """Découpe un `MEMORY.md` en entrées, vides écartées."""
    if not notes.strip():
        return ()
    return tuple(e.strip() for e in notes.split(SEPARATEUR_ENTREES) if e.strip())


def dossier_memoire(store: Path) -> Path:
    return Path(store) / DOSSIER_MEMOIRE


def capturer(store: Path) -> Snapshot:
    """Snapshot du dossier mémoire du store. Dossier absent → snapshot vide."""
    dossier = dossier_memoire(store)
    if not dossier.is_dir():
        return Snapshot(fichiers={})
    fichiers = {
        chemin.relative_to(dossier).as_posix(): chemin.read_bytes()
        for chemin in sorted(dossier.rglob("*"))
        if chemin.is_file()
    }
    return Snapshot(fichiers=fichiers)


def fichiers_modifies(store: Path, snapshot: Snapshot) -> tuple[str, ...]:
    """Fichiers qui diffèrent du snapshot (créés, modifiés ou supprimés)."""
    actuel = capturer(store)
    noms = set(actuel.fichiers) | set(snapshot.fichiers)
    return tuple(
        sorted(nom for nom in noms if actuel.fichiers.get(nom) != snapshot.fichiers.get(nom))
    )


def restaurer(store: Path, snapshot: Snapshot) -> tuple[str, ...]:
    """Remet le dossier mémoire dans l'état du snapshot.

    Rend la liste des fichiers qui avaient bougé — c'est-à-dire l'observable
    « écriture intra-série » — avant de les écraser. Les fichiers apparus
    depuis le snapshot sont supprimés : un canal mémoire créé en cours de
    série n'a pas plus le droit de survivre qu'une modification.
    """
    modifies = fichiers_modifies(store, snapshot)
    dossier = dossier_memoire(store)
    dossier.mkdir(parents=True, exist_ok=True)

    for chemin in sorted(dossier.rglob("*"), reverse=True):
        if chemin.is_file() and chemin.relative_to(dossier).as_posix() not in snapshot.fichiers:
            chemin.unlink()

    for nom, contenu in snapshot.fichiers.items():
        cible = dossier / nom
        cible.parent.mkdir(parents=True, exist_ok=True)
        if not cible.exists() or cible.read_bytes() != contenu:
            cible.write_bytes(contenu)

    return modifies


def ecrire_notes(store: Path, notes: str) -> None:
    """Écrit `MEMORY.md` (amorçage d'un run, marqueur de canari, tests)."""
    dossier = dossier_memoire(store)
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / FICHIER_NOTES).write_text(notes, encoding="utf-8")


def lire_notes(store: Path) -> str:
    """Contenu courant de `MEMORY.md` (chaîne vide si absent)."""
    fichier = dossier_memoire(store) / FICHIER_NOTES
    return fichier.read_text(encoding="utf-8") if fichier.is_file() else ""


@dataclass(frozen=True)
class EvenementMemoire:
    """Une modification d'entrée à la frontière de série (PRD 4 §3)."""

    type: str  # ajout | suppression | modification | overflow | elagage
    detail: str


def evenements_memoire(
    avant: Snapshot | str,
    apres: Snapshot | str,
    limite_caracteres: int = 2200,
) -> tuple[EvenementMemoire, ...]:
    """Diff d'entrées entre deux états de `MEMORY.md` (PRD 4 §3).

    Le diff est ensembliste : les entrées sont des unités indépendantes chez
    Hermes, leur ordre n'est pas porteur de sens. Une entrée reformulée
    apparaît donc en `suppression` + `ajout` — ce qui est fidèle : on ne peut
    pas savoir si l'agent a réécrit ou remplacé.

    `elagage` signale une série close avec moins d'entrées qu'à l'ouverture
    (l'auto-élagage attendu, spec §6) ; `overflow` signale un dépassement de
    la limite de caractères, que le PRD demande de traiter en erreur visible
    plutôt qu'en compaction silencieuse.
    """
    entrees_avant = avant.entrees if isinstance(avant, Snapshot) else decouper_entrees(avant)
    entrees_apres = apres.entrees if isinstance(apres, Snapshot) else decouper_entrees(apres)

    ensemble_avant, ensemble_apres = set(entrees_avant), set(entrees_apres)
    evenements = [
        EvenementMemoire("suppression", entree)
        for entree in entrees_avant
        if entree not in ensemble_apres
    ]
    evenements += [
        EvenementMemoire("ajout", entree)
        for entree in entrees_apres
        if entree not in ensemble_avant
    ]

    if entrees_apres and len(entrees_apres) < len(entrees_avant):
        evenements.append(
            EvenementMemoire(
                "elagage",
                f"{len(entrees_avant)} entrées → {len(entrees_apres)}",
            )
        )

    taille = len(SEPARATEUR_ENTREES.join(entrees_apres))
    if taille > limite_caracteres:
        evenements.append(
            EvenementMemoire("overflow", f"{taille} caractères > limite {limite_caracteres}")
        )

    return tuple(evenements)


__all__ = [
    "DOSSIER_MEMOIRE",
    "FICHIER_NOTES",
    "SEPARATEUR_ENTREES",
    "EvenementMemoire",
    "Snapshot",
    "capturer",
    "decouper_entrees",
    "dossier_memoire",
    "ecrire_notes",
    "evenements_memoire",
    "fichiers_modifies",
    "lire_notes",
    "restaurer",
]
