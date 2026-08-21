"""Invocation d'Hermes en un coup : `hermes -z` (PRD 2 §3, décision D1).

Une décision de jeu = une invocation, un prompt en entrée, la réponse finale
seule sur stdout. C'est le **seul** point de contact entre l'arène et le
modèle, et il est identique pour les trois conditions mémoire : si le harnais
différait d'une condition à l'autre, l'expérience mesurerait « harnais ×
mémoire » au lieu de « mémoire » (spec §0).

Options posées à chaque appel :

- `HERMES_HOME` = le store isolé du run (§6), et **aucune** autre variable
  `HERMES_*` héritée du shell : une variable oubliée (`HERMES_MODEL`,
  `HERMES_KANBAN_*`…) rerouterait silencieusement le run ;
- `-t <toolset>` — `context_engine` (vide) pendant les manches, `memory` à la
  seule réflexion AE ;
- `-m` / `--provider` — modèle figé, identique aux 27 runs (`--provider` sans
  `--model` est refusé par Hermes : les deux vont ensemble) ;
- `--usage-file` — rapport JSON par appel (tokens entrée/sortie, modèle
  réellement servi, coût estimé), écrit même en cas d'échec. C'est la source
  des champs `tokens` des logs (PRD 4 §2) et du suivi de budget.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Protocol

from .stores import ParametresModele, Store, TOOLSET_SANS_OUTIL

#: Timeout d'une invocation. Généreux : une manche est un aller-retour court,
#: mais le premier appel d'un store paie l'initialisation d'Hermes.
TIMEOUT_DEFAUT = 180

#: Relances sur échec (réseau, timeout, sortie vide). Au-delà, la manche est
#: marquée `erreur_harnais` et rejouée par l'arbitre avec la même donne —
#: jamais silencieusement sautée (PRD 2 §3).
RELANCES_DEFAUT = 2


@dataclass(frozen=True)
class Reponse:
    """Résultat d'une invocation, tel qu'il part dans les logs."""

    texte: str
    code_retour: int
    latence_ms: int
    tentatives: int
    tokens_entree: int | None = None
    tokens_sortie: int | None = None
    modele: str | None = None
    cout_usd: float | None = None
    erreur: str | None = None

    @property
    def ok(self) -> bool:
        return self.erreur is None and bool(self.texte.strip())

    def tokens(self) -> Mapping[str, int | None]:
        return {"in": self.tokens_entree, "out": self.tokens_sortie}


class Invocateur(Protocol):
    """Contrat minimal attendu par le harnais.

    Les tests substituent un invocateur en mémoire : rien dans
    `conditions.py` ne suppose un sous-processus, et la suite tourne sans le
    moindre appel API.
    """

    def __call__(self, prompt: str, toolset: str = TOOLSET_SANS_OUTIL) -> Reponse: ...


def _executable(chemin: str | None) -> str:
    if chemin:
        return chemin
    trouve = shutil.which("hermes")
    if not trouve:
        raise FileNotFoundError(
            "exécutable `hermes` introuvable sur le PATH — "
            "passer `executable=` explicitement"
        )
    return trouve


def _environnement(store: Store) -> Mapping[str, str]:
    """Env du sous-processus : celui du shell, purgé de tout `HERMES_*`."""
    env = {cle: val for cle, val in os.environ.items() if not cle.startswith("HERMES_")}
    env.update(store.variables_env())
    return env


@dataclass
class InvocateurHermes:
    """Invocateur réel, lié au store d'un run."""

    store: Store
    parametres: ParametresModele = field(default_factory=ParametresModele)
    executable: str | None = None
    timeout: int = TIMEOUT_DEFAUT
    relances: int = RELANCES_DEFAUT

    def __call__(self, prompt: str, toolset: str = TOOLSET_SANS_OUTIL) -> Reponse:
        commande_base = [
            _executable(self.executable),
            "-z",
            prompt,
            "-t",
            toolset,
            "-m",
            self.parametres.modele,
            "--provider",
            self.parametres.fournisseur,
        ]
        env = _environnement(self.store)
        derniere: Reponse | None = None

        for tentative in range(1, self.relances + 2):
            with tempfile.TemporaryDirectory(prefix="arene-usage-") as tmp:
                rapport = Path(tmp) / "usage.json"
                commande = commande_base + ["--usage-file", str(rapport)]
                reponse = self._executer(commande, env, rapport, tentative)
            if reponse.ok:
                return reponse
            derniere = reponse

        assert derniere is not None  # la boucle tourne au moins une fois
        return derniere

    def _executer(
        self,
        commande: list[str],
        env: Mapping[str, str],
        rapport: Path,
        tentative: int,
    ) -> Reponse:
        debut = time.monotonic()
        try:
            acheve = subprocess.run(
                commande,
                env=dict(env),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired:
            return Reponse(
                texte="",
                code_retour=-1,
                latence_ms=int((time.monotonic() - debut) * 1000),
                tentatives=tentative,
                erreur=f"timeout après {self.timeout} s",
                **_usage(rapport),
            )
        except OSError as exc:  # exécutable absent, droits, etc.
            return Reponse(
                texte="",
                code_retour=-1,
                latence_ms=int((time.monotonic() - debut) * 1000),
                tentatives=tentative,
                erreur=f"lancement impossible : {exc}",
            )

        latence = int((time.monotonic() - debut) * 1000)
        texte = acheve.stdout or ""
        erreur = None
        if acheve.returncode != 0:
            erreur = f"code retour {acheve.returncode} : {(acheve.stderr or '').strip()[:400]}"
        elif not texte.strip():
            erreur = "sortie vide"

        return Reponse(
            texte=texte,
            code_retour=acheve.returncode,
            latence_ms=latence,
            tentatives=tentative,
            erreur=erreur,
            **_usage(rapport),
        )


def _usage(rapport: Path) -> Mapping[str, object]:
    """Lit le rapport `--usage-file`. Absent ou illisible → champs à `None`.

    Best-effort assumé : un rapport de coût manquant ne doit jamais faire
    échouer une manche par ailleurs valide, il laisse juste un trou visible
    dans les logs.
    """
    vide: dict[str, object] = {
        "tokens_entree": None,
        "tokens_sortie": None,
        "modele": None,
        "cout_usd": None,
    }
    try:
        donnees = json.loads(rapport.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return vide
    return {
        "tokens_entree": donnees.get("input_tokens"),
        "tokens_sortie": donnees.get("output_tokens"),
        "modele": donnees.get("model"),
        "cout_usd": donnees.get("estimated_cost_usd"),
    }


__all__ = [
    "RELANCES_DEFAUT",
    "TIMEOUT_DEFAUT",
    "Invocateur",
    "InvocateurHermes",
    "Reponse",
]
