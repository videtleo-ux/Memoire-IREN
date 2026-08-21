"""Point d'entrée d'un run — dont le mini-run de bout en bout (PRD 3 §10.1).

    python -m arbitre --condition SM --bot Station --K 20 --series 1

Le mini-run est le premier jalon d'intégration et la **première dépense réelle
du projet** : il se joue sur le modèle gratuit du catalogue, donc à coût nul,
et il doit produire des logs complets, un écart calculable et un rapport
d'intégrité vert avant que la moindre campagne payante ne soit lancée.

Trois sorties, dans l'ordre où on les regarde :

1. l'écart d'exploitation série par série (la mesure) ;
2. le rapport d'intégrité de clôture (les donnes, les positions, l'isolation,
   la complétude — PRD 3 §8) ;
3. les CSV dérivés régénérés (PRD 4 §5), pour vérifier d'un coup d'œil que la
   chaîne va bien jusqu'au fichier d'analyse.

Le code de sortie vaut 1 si l'intégrité a signalé quoi que ce soit : un run
douteux ne doit pas passer inaperçu dans un enchaînement de scripts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from harnais import Condition, ParametresModele
from journal import generer
from moteur import BOTS

from .run import ConfigRun, preparer_run, racine_defaut


def _analyseur() -> argparse.ArgumentParser:
    analyseur = argparse.ArgumentParser(
        prog="python -m arbitre",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    analyseur.add_argument("--condition", choices=[c.value for c in Condition], required=True)
    analyseur.add_argument("--bot", choices=sorted(BOTS), required=True)
    analyseur.add_argument("--replication", type=int, default=1)
    analyseur.add_argument("--K", type=int, default=20, help="manches par série (pair)")
    analyseur.add_argument(
        "--series", type=int, default=None, help="nombre de séries (défaut : règle du PRD 3 §3)"
    )
    analyseur.add_argument("--racine", default=None, help="racine des runs (hors OneDrive)")
    analyseur.add_argument("--machine", default="victus")
    analyseur.add_argument("--modele", default=None, help="modèle du catalogue Nous Portal")
    analyseur.add_argument(
        "--home-source", default=None, help="HERMES_HOME global, d'où l'auth est recopiée"
    )
    analyseur.add_argument(
        "--sans-canari",
        action="store_true",
        help="canari fichier au lieu du canari réel (aucun appel API, ne prouve "
        "pas le chemin d'écriture d'Hermes)",
    )
    analyseur.add_argument("--csv", default=None, help="dossier de sortie des CSV dérivés")
    return analyseur


def _console_tolerante() -> None:
    """Rend l'affichage insensible à l'encodage de la console.

    La console Windows tourne en cp1252 : un « ≤ » dans l'en-tête suffisait à
    faire tomber le run **avant le premier appel API**. On garde l'encodage de
    la console — les accents français y passent — et on remplace ce qui n'y
    entre pas. Ce sont les messages qu'on dégrade, jamais les données : les
    journaux sont écrits en UTF-8 par le journal, indépendamment d'ici.

    Le filet est nécessaire au-delà de nos propres chaînes : les anomalies
    d'intégrité citent des « ≠ » et des « π̂ » qu'on ne peut pas prévoir une
    par une.
    """
    for flux in (sys.stdout, sys.stderr):
        try:
            flux.reconfigure(errors="replace")
        except (AttributeError, ValueError):  # flux redirigé, non reconfigurable
            pass


def _tracer(ligne: Mapping[str, Any]) -> None:
    mesures = ligne["mesures"]
    defauts = ligne["defauts"]
    print(
        f"  série {ligne['session']} : écart {mesures['ecart_exploitation']:+.4f} "
        f"· récité {mesures['reference_recite']:+.4f} "
        f"· réalisé {mesures['ev_realisee']:+.3f} "
        f"· défauts {defauts['actions_par_defaut']} "
        f"· plateau {ligne['plateau'].get('declare')}"
    )


def main(argv: Sequence[str] | None = None) -> int:
    _console_tolerante()
    arguments = _analyseur().parse_args(argv)

    parametres = (
        ParametresModele(modele=arguments.modele) if arguments.modele else ParametresModele()
    )
    config = ConfigRun(
        condition=Condition(arguments.condition),
        bot=arguments.bot,
        replication=arguments.replication,
        machine=arguments.machine,
        K=arguments.K,
        series_max=arguments.series,
        racine=Path(arguments.racine) if arguments.racine else racine_defaut(),
        parametres=parametres,
    )

    print(f"run {config.run_id} — K={config.K}, séries au plus {config.series_prevues}")
    print(f"  dossier : {config.dossier}")

    arbitre = preparer_run(
        config,
        home_source=arguments.home_source,
        canari_reel=not arguments.sans_canari,
        home_global=arguments.home_source,
    )
    arbitre.apres_serie = _tracer
    arbitre.jouer()

    rapport = arbitre.clore()
    print(rapport)
    for anomalie in rapport.anomalies:
        print(f"  · {anomalie}")

    sortie_csv = Path(arguments.csv) if arguments.csv else Path(config.racine) / "csv"
    compte = generer(config.racine, sortie_csv)
    print(f"CSV dans {sortie_csv} : " + ", ".join(f"{n} ({v})" for n, v in compte.items()))
    return 0 if rapport.ok else 1


__all__ = ["main"]
