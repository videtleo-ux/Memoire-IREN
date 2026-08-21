"""Vérifications d'intégrité à la clôture d'un run (PRD 3 §8).

Cinq contrôles, choisis parce qu'aucun d'eux ne se rattrape après coup :

1. **Donnes appariées** — l'empreinte de la séquence de donnes de chaque série
   est recalculée depuis la graine, et confrontée aux runs de la même
   réplication déjà présents. C'est le contrôle central : si l'appariement a
   sauté, aucune analyse ne le dira, et la réduction de variance sur laquelle
   repose la comparaison inter-conditions n'aura jamais existé.
2. **Équilibre des positions** — K pair ⇒ exactement K/2 par position.
3. **Témoin d'isolation** — le marqueur déposé au démarrage du run est
   toujours dans son store, et nulle part ailleurs.
4. **Complétude des logs** — K manches × S séries, une ligne de série par
   série, aucun trou dans la numérotation.
5. **Texte de règles constant** — le hash servi est le même sur toutes les
   lignes du run, et c'est bien celui des gabarits.

Le rapport est écrit dans les logs et rendu à l'appelant ; il ne détruit rien
et ne corrige rien. Un run en anomalie reste sur le disque : c'est à l'analyse
de décider ce qu'elle en fait, et au mémoire de le documenter.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from harnais.gabarits import HASH_REGLES
from harnais.gel import DOSSIER_MEMOIRE
from harnais.stores import EchecCanari, Store, marqueur_canari
from journal import lire_sessions, lire_tours

from . import alea

FICHIER_RAPPORT = "integrite.json"

#: Témoin d'isolation posé pour toute la durée du run. Il vit à la racine du
#: store, hors du dossier mémoire : le gel intra-série (qui restaure
#: `memories/` avant chaque manche) ne peut donc ni l'effacer ni le
#: ressusciter, et `MEMORY.md` reste vierge en `M_0`.
FICHIER_TEMOIN = "temoin-isolation.txt"


@dataclass
class RapportIntegrite:
    """Le verdict de clôture. `ok` vaut True si rien n'a été signalé."""

    run_id: str
    anomalies: list[str] = field(default_factory=list)
    controles: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.anomalies

    def signaler(self, message: str) -> None:
        self.anomalies.append(message)

    def en_json(self) -> dict[str, Any]:
        return {"run_id": self.run_id, "ok": self.ok, **self.controles, "anomalies": self.anomalies}

    def ecrire(self, dossier_logs: Path | str) -> Path:
        chemin = Path(dossier_logs) / FICHIER_RAPPORT
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(
            json.dumps(self.en_json(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return chemin

    def __str__(self) -> str:  # pragma: no cover - confort CLI
        etat = "OK" if self.ok else f"{len(self.anomalies)} anomalie(s)"
        return f"intégrité {self.run_id} : {etat}"


# --------------------------------------------------------------------------
# Témoin d'isolation
# --------------------------------------------------------------------------


def poser_temoin(store: Store, run_id: str) -> str:
    """Dépose un marqueur unique dans le store, et rend sa valeur.

    Complément du canari du PRD 2 §6, qui prouve *au démarrage* que le chemin
    d'écriture d'Hermes aboutit bien dans le store du run — mais efface son
    marqueur pour laisser `M_0` vide. Le témoin, lui, reste en place toute la
    durée du run : il répond à la question « ce store est-il resté le sien,
    du début à la fin ? », que le canari seul ne couvre pas.
    """
    marqueur = marqueur_canari(run_id)
    store.chemin.mkdir(parents=True, exist_ok=True)
    (store.chemin / FICHIER_TEMOIN).write_text(marqueur, encoding="utf-8")
    return marqueur


def lire_temoin(store: Store) -> str:
    fichier = store.chemin / FICHIER_TEMOIN
    return fichier.read_text(encoding="utf-8") if fichier.is_file() else ""


def verifier_temoin(
    store: Store,
    marqueur: str,
    autres_stores: Iterable[Path | str] = (),
    home_global: Path | str | None = None,
) -> None:
    """Le témoin est-il intact chez lui, et absent partout ailleurs ?"""
    if lire_temoin(store) != marqueur:
        raise EchecCanari(
            f"témoin d'isolation absent ou altéré dans {store.chemin} : "
            "le store du run a été remplacé ou vidé en cours de route"
        )

    suspects = [Path(p) for p in autres_stores if Path(p) != store.chemin]
    if home_global is not None and Path(home_global) != store.chemin:
        suspects.append(Path(home_global))

    for suspect in suspects:
        for fichier in _fichiers_a_inspecter(suspect):
            if marqueur in fichier.read_text(encoding="utf-8", errors="replace"):
                raise EchecCanari(
                    f"témoin du run {store.chemin} retrouvé dans {fichier} : "
                    "les stores ne sont pas isolés"
                )


def _fichiers_a_inspecter(home: Path) -> Sequence[Path]:
    candidats = [home / FICHIER_TEMOIN]
    dossier = home / DOSSIER_MEMOIRE
    if dossier.is_dir():
        candidats += [c for c in sorted(dossier.rglob("*")) if c.is_file()]
    return [c for c in candidats if c.is_file()]


# --------------------------------------------------------------------------
# Contrôles de clôture
# --------------------------------------------------------------------------


def _empreintes_voisines(racine: Path, run_id: str, replication: int) -> dict[int, dict[str, str]]:
    """`{série: {run_id: hash_donnes}}` pour les autres runs de la réplication."""
    voisines: dict[int, dict[str, str]] = {}
    for chemin in sorted(Path(racine).glob("*/logs/sessions.jsonl")):
        for ligne in lire_sessions(chemin.parent):
            if ligne["run_id"] == run_id or ligne.get("replication") != replication:
                continue
            voisines.setdefault(ligne["session"], {})[ligne["run_id"]] = ligne.get("hash_donnes", "")
    return voisines


def verifier_run(
    dossier_logs: Path | str,
    graine: str,
    K: int,
    replication: int,
    run_id: str,
    racine: Path | str | None = None,
    store: Store | None = None,
    marqueur_temoin: str | None = None,
    autres_stores: Iterable[Path | str] = (),
    home_global: Path | str | None = None,
) -> RapportIntegrite:
    """Passe les cinq contrôles et rend le rapport (jamais d'exception)."""
    rapport = RapportIntegrite(run_id=run_id)
    series = {ligne["session"]: ligne for ligne in lire_sessions(dossier_logs)}
    tours = list(lire_tours(dossier_logs))

    rapport.controles["series"] = len(series)
    rapport.controles["tours"] = len(tours)

    _controler_completude(series, tours, K, rapport)
    _controler_positions(series, K, rapport)
    _controler_donnes(series, graine, K, replication, run_id, racine, rapport)
    _controler_regles(series, tours, rapport)
    _controler_temoin(store, marqueur_temoin, autres_stores, home_global, rapport)
    return rapport


def _controler_completude(
    series: Mapping[int, Mapping[str, Any]],
    tours: Sequence[Mapping[str, Any]],
    K: int,
    rapport: RapportIntegrite,
) -> None:
    if not series:
        rapport.signaler("aucune série close : le run n'a rien produit d'exploitable")
        return

    from .etat import series_manquantes

    manquantes = series_manquantes(series, max(series))
    if manquantes:
        rapport.signaler(f"séries manquantes dans les logs : {manquantes}")

    manches_par_serie: dict[int, set[int]] = {}
    for tour in tours:
        manches_par_serie.setdefault(tour["session"], set()).add(tour["manche"])
    for numero in sorted(series):
        jouees = manches_par_serie.get(numero, set())
        if len(jouees) != K:
            rapport.signaler(f"série {numero} : {len(jouees)} manches loguées pour K = {K}")
        elif jouees != set(range(1, K + 1)):
            rapport.signaler(f"série {numero} : numérotation des manches trouée ou dupliquée")
    orphelines = sorted(set(manches_par_serie) - set(series))
    if orphelines:
        rapport.signaler(f"tours logués sans ligne de série : séries {orphelines}")


def _controler_positions(
    series: Mapping[int, Mapping[str, Any]], K: int, rapport: RapportIntegrite
) -> None:
    attendu = K // 2
    for numero, ligne in sorted(series.items()):
        positions = ligne.get("positions", {})
        if K % 2 == 0 and (positions.get("J1") != attendu or positions.get("J2") != attendu):
            rapport.signaler(
                f"série {numero} : positions {dict(positions)} au lieu de {attendu}/{attendu}"
            )
        elif abs(positions.get("J1", 0) - positions.get("J2", 0)) > 1:
            rapport.signaler(f"série {numero} : positions déséquilibrées {dict(positions)}")


def _controler_donnes(
    series: Mapping[int, Mapping[str, Any]],
    graine: str,
    K: int,
    replication: int,
    run_id: str,
    racine: Path | str | None,
    rapport: RapportIntegrite,
) -> None:
    for numero, ligne in sorted(series.items()):
        attendu = alea.hash_donnes(graine, replication, numero, K)
        if ligne.get("hash_donnes") != attendu:
            rapport.signaler(
                f"série {numero} : empreinte de donnes {ligne.get('hash_donnes')} "
                f"≠ empreinte dérivée de la graine {attendu}"
            )

    if racine is None:
        rapport.controles["runs_apparies"] = []
        return

    voisines = _empreintes_voisines(Path(racine), run_id, replication)
    apparies: set[str] = set()
    for numero, ligne in sorted(series.items()):
        for autre_run, empreinte in voisines.get(numero, {}).items():
            apparies.add(autre_run)
            if empreinte != ligne.get("hash_donnes"):
                rapport.signaler(
                    f"série {numero} : donnes différentes de {autre_run} "
                    f"({empreinte} ≠ {ligne.get('hash_donnes')}) — appariement rompu"
                )
    rapport.controles["runs_apparies"] = sorted(apparies)


def _controler_regles(
    series: Mapping[int, Mapping[str, Any]],
    tours: Sequence[Mapping[str, Any]],
    rapport: RapportIntegrite,
) -> None:
    hashes = {ligne.get("hash_regles") for ligne in list(series.values()) + list(tours)}
    hashes.discard(None)
    if hashes and hashes != {HASH_REGLES}:
        rapport.signaler(
            f"texte de règles non constant sur le run : {sorted(hashes)} "
            f"(attendu {HASH_REGLES})"
        )
    rapport.controles["hash_regles"] = sorted(hashes)


def _controler_temoin(
    store: Store | None,
    marqueur: str | None,
    autres_stores: Iterable[Path | str],
    home_global: Path | str | None,
    rapport: RapportIntegrite,
) -> None:
    if store is None or marqueur is None:
        rapport.controles["temoin_isolation"] = "non vérifié"
        return
    try:
        verifier_temoin(store, marqueur, autres_stores, home_global)
    except EchecCanari as echec:
        rapport.signaler(str(echec))
        rapport.controles["temoin_isolation"] = "rompu"
        return
    rapport.controles["temoin_isolation"] = "intact"


__all__ = [
    "FICHIER_RAPPORT",
    "FICHIER_TEMOIN",
    "RapportIntegrite",
    "lire_temoin",
    "poser_temoin",
    "verifier_run",
    "verifier_temoin",
]
