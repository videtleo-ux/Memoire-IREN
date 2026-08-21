"""Canari d'isolation exécuté au démarrage de chaque run (PRD 2 §6, spec §7).

La spec est explicite : on ne *suppose* jamais l'isolation, on la teste. Le
canari fait donc écrire un marqueur unique **par l'agent lui-même**, via son
outil de mémoire natif — pas par un `open()` du côté Python. C'est la seule
façon de vérifier que le chemin réellement emprunté par Hermes pour persister
`MEMORY.md` aboutit dans le store du run, et nulle part ailleurs.

Deux phases, deux appels :

1. **Écriture** — configuration de réflexion (mémoire native active, toolset
   `memory`). Le marqueur doit atterrir dans le store du run, et nulle part
   ailleurs.
2. **Blocage** — *même consigne*, configuration de manche (mémoire native
   éteinte, toolset vide). `MEMORY.md` ne doit pas bouger d'un octet.

La phase 2 remplace une sonde antérieure qui demandait à l'agent combien
d'outils il voyait : sur le modèle gratuit du pilote, il répond « 5 » alors
que le toolset des manches en expose zéro (vérifié dans Hermes :
`get_tool_definitions(enabled_toolsets=["context_engine"])` rend une liste
vide). Un agent n'a pas d'introspection fiable sur son propre outillage ; un
fichier qui ne bouge pas, si.

    rapport = canari(store, "AE-station-r2", InvocateurHermes(store),
                     autres_stores=[...], home_global=HOME_MACHINE)

Échec = `EchecCanari`, et le run ne démarre pas.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .gel import lire_notes
from .hermes import Invocateur
from .stores import (
    TOOLSET_MEMOIRE,
    TOOLSET_SANS_OUTIL,
    EchecCanari,
    Store,
    marqueur_canari,
    verifier_isolation,
)

#: Le prompt du canari est le seul texte servi à l'agent qui ne respecte pas
#: le lexique obfusqué — et c'est sans conséquence : il est joué **avant** la
#: série 0, ses notes sont effacées juste après, et le contexte est neuf à
#: chaque manche. Il ne peut donc rien contaminer.
PROMPT_MARQUEUR = (
    "Enregistre exactement cette ligne dans ta mémoire persistante, telle "
    "quelle, sans la reformuler :\n\n{marqueur}\n\n"
    "Réponds ensuite par le seul mot : enregistré."
)


@dataclass(frozen=True)
class RapportCanari:
    """Ce que le canari a constaté — logué au démarrage du run."""

    marqueur: str
    ecriture_confirmee: bool
    ecriture_bloquee_en_manche: bool | None
    reponse_ecriture: str = ""
    reponse_manche: str = ""


def canari(
    store: Store,
    run_id: str,
    invocateur: Invocateur,
    autres_stores: Iterable[Path | str] = (),
    home_global: Path | str | None = None,
    verifier_blocage: bool = True,
) -> RapportCanari:
    """Écrit un marqueur via l'agent, vérifie qu'il n'a fui nulle part.

    Le store est laissé **vierge** en sortie : le marqueur est effacé, sinon
    `M_0` ne serait pas vide et la série 0 démarrerait avec une note parasite.
    """
    marqueur = marqueur_canari(run_id)
    consigne = PROMPT_MARQUEUR.format(marqueur=marqueur)

    store.ecrire_config(memoire_native=True, max_turns=6)
    try:
        ecriture = invocateur(consigne, TOOLSET_MEMOIRE)
    finally:
        store.ecrire_config(memoire_native=False)

    if not ecriture.ok:
        raise EchecCanari(f"invocation du canari en échec : {ecriture.erreur}")

    verifier_isolation(store, marqueur, autres_stores, home_global)

    bloquee: bool | None = None
    reponse_manche = ""
    if verifier_blocage:
        avant = lire_notes(store.chemin)
        sonde = invocateur(consigne, TOOLSET_SANS_OUTIL)
        reponse_manche = sonde.texte.strip()
        bloquee = lire_notes(store.chemin) == avant
        if not bloquee:
            raise EchecCanari(
                "la mémoire a été écrite avec la configuration de manche : "
                "le gel intra-série reposerait sur du vide"
            )

    store.notes.write_text("", encoding="utf-8")
    return RapportCanari(
        marqueur=marqueur,
        ecriture_confirmee=True,
        ecriture_bloquee_en_manche=bloquee,
        reponse_ecriture=ecriture.texte.strip(),
        reponse_manche=reponse_manche,
    )


def canari_fichier(
    store: Store,
    run_id: str,
    autres_stores: Iterable[Path | str] = (),
    home_global: Path | str | None = None,
) -> RapportCanari:
    """Variante sans appel API : le marqueur est écrit par l'arbitre.

    Utile pour vérifier l'arborescence d'un run à coût nul (mise au point,
    tests). Elle ne prouve **pas** que le chemin d'écriture d'Hermes aboutit
    dans le store — seul `canari` le fait, et c'est lui qui garde la campagne.
    """
    marqueur = marqueur_canari(run_id)
    store.notes.write_text(marqueur, encoding="utf-8")
    verifier_isolation(store, marqueur, autres_stores, home_global)
    store.notes.write_text("", encoding="utf-8")
    return RapportCanari(
        marqueur=marqueur,
        ecriture_confirmee=False,
        ecriture_bloquee_en_manche=None,
    )


def stores_actifs(racine: Path | str) -> Sequence[Path]:
    """Les stores des autres runs présents sous une racine — l'ensemble que le
    canari doit trouver indemne."""
    racine = Path(racine)
    if not racine.is_dir():
        return ()
    return [chemin.parent for chemin in sorted(racine.glob("*/hermes-home/config.yaml"))]


__all__ = [
    "PROMPT_MARQUEUR",
    "RapportCanari",
    "canari",
    "canari_fichier",
    "stores_actifs",
]
