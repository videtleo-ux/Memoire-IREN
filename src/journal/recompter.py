"""Recalcul du détecteur de dé-obfuscation depuis les journaux (PRD 4 §4).

L'arbitre applique le détecteur à la clôture de chaque série et fige le
résultat dans `sessions.jsonl`. C'est pratique, mais ça enferme la campagne
dans la version du détecteur qui tournait le jour où elle a été lancée — et
un détecteur, ça se découvre incomplet en cours de route. Le mini-run du
2026-08-21 en a fait la démonstration : le modèle traduisait le lexique servi
vers les termes anglais du jeu source, et aucun motif ne les attrapait.

Ce module lève cette contrainte. Comme les journaux conservent **le texte
intégral** de chaque sortie et de chaque état mémoire, le détecteur peut être
rejoué à n'importe quel moment sur des données déjà acquises, avec des motifs
améliorés, sans relancer une seule manche.

Conséquence méthodologique : la mesure de reconnaissance du jeu devient une
**covariable recalculable**, et non un choix à figer avant la campagne. Les
comptes de `sessions.jsonl` restent ceux du détecteur du jour ; ceux d'ici
font foi pour l'analyse, et l'écart entre les deux est lui-même documenté.

Usage : `python -m journal.recompter C:\\arene-runs --sortie deobfuscation.json`
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

from .deobfuscation import NIVEAU_DEOBFUSCATION, NIVEAU_RECITATION, Drapeau, analyser
from .ecrivains import FICHIER_SESSIONS, lire_sessions, lire_tours

#: Champs du bloc `memoire` d'une série soumis au détecteur, avec la source à
#: reporter. `M_s` est ce que l'agent **a lu**, `M_s1` ce qu'il **a écrit** :
#: les deux comptent, et pas de la même façon — un hit dans M_s1 se propagera
#: à toutes les séries suivantes.
CHAMPS_MEMOIRE = (("M_s", "slot"), ("M_s1", "memoire"), ("sortie_reflexion", "sortie"))


def sources(dossier_logs: Path | str) -> Iterator[tuple[int, str, str, int | None]]:
    """Tout ce que le détecteur doit voir : `(série, texte, source, manche)`.

    Le récapitulatif n'est pas balayé pour lui-même : il est produit par
    l'arbitre à partir des gabarits obfusqués, et la suite de tests garantit
    déjà qu'aucun motif interdit n'y figure. Il entre en revanche dans le
    balayage en condition ICL, où il *est* le contenu du slot.
    """
    for tour in lire_tours(dossier_logs):
        yield tour["session"], tour.get("sortie_brute", ""), "sortie", tour.get("manche")
    for serie in lire_sessions(dossier_logs):
        memoire = serie.get("memoire", {})
        for champ, source in CHAMPS_MEMOIRE:
            yield serie["session"], memoire.get(champ, "") or "", source, None


def recompter_run(dossier_logs: Path | str) -> dict[str, Any]:
    """Rejoue le détecteur sur un run et rend le décompte par série."""
    par_serie: dict[int, list[Drapeau]] = {}
    for serie, texte, source, manche in sources(dossier_logs):
        if not texte:
            continue
        par_serie.setdefault(serie, []).extend(analyser(texte, source, manche))

    series: dict[str, Any] = {}
    for numero, drapeaux in sorted(par_serie.items()):
        series[str(numero)] = {
            "deobfuscation": sum(1 for d in drapeaux if d.niveau == NIVEAU_DEOBFUSCATION),
            "recitation": sum(1 for d in drapeaux if d.niveau == NIVEAU_RECITATION),
            "manches_touchees": len(
                {d.manche for d in drapeaux if d.manche is not None}
            ),
            "par_regle": dict(Counter(d.regle for d in drapeaux).most_common()),
        }

    logue = _comptes_logues(dossier_logs)
    return {
        "series": series,
        "total": {
            "deobfuscation": sum(s["deobfuscation"] for s in series.values()),
            "recitation": sum(s["recitation"] for s in series.values()),
        },
        # L'écart avec ce que la campagne a figé n'est pas une anomalie : c'est
        # la trace de l'amélioration du détecteur, et elle se rapporte.
        "logue_a_lepoque": logue,
    }


def _comptes_logues(dossier_logs: Path | str) -> dict[str, int]:
    """Ce que l'arbitre avait compté au moment du run, pour comparaison."""
    totaux = Counter()
    for serie in lire_sessions(dossier_logs):
        for drapeau in serie.get("drapeaux_deobfuscation", []):
            totaux[drapeau.get("niveau", "?")] += 1
    return dict(totaux)


def trouver_runs(racine: Path | str) -> list[Path]:
    """Les dossiers `logs/` de tous les runs sous une racine."""
    return sorted(chemin.parent for chemin in Path(racine).rglob(FICHIER_SESSIONS))


def recompter(racine: Path | str) -> dict[str, Any]:
    """Rejoue le détecteur sur tous les runs trouvés sous `racine`."""
    return {dossier.parent.name: recompter_run(dossier) for dossier in trouver_runs(racine)}


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover - CLI
    analyseur = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    analyseur.add_argument("racine", help="racine des runs, ou un dossier logs/")
    analyseur.add_argument("--sortie", default=None, help="fichier JSON de sortie")
    arguments = analyseur.parse_args(argv)

    racine = Path(arguments.racine)
    rapport = (
        {racine.parent.name: recompter_run(racine)}
        if (racine / FICHIER_SESSIONS).is_file()
        else recompter(racine)
    )

    for run, donnees in rapport.items():
        total, ancien = donnees["total"], donnees["logue_a_lepoque"]
        print(
            f"{run} — dé-obfuscation {total['deobfuscation']} "
            f"(logué {ancien.get('deobfuscation', 0)}) · "
            f"récitation {total['recitation']} (logué {ancien.get('recitation', 0)})"
        )
    if arguments.sortie:
        Path(arguments.sortie).write_text(
            json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"écrit dans {arguments.sortie}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = [
    "CHAMPS_MEMOIRE",
    "recompter",
    "recompter_run",
    "sources",
    "trouver_runs",
]
