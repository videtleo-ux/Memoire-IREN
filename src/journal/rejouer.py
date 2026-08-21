"""Test de complétude du logging : tout est-il reconstructible ? (PRD 4 §7.1)

On relit `turns.jsonl` seul, on re-règle chaque manche avec le moteur (PRD 1),
on ré-estime π̂ et on recalcule l'écart d'exploitation — puis on confronte le
tout à `sessions.jsonl`. Une divergence signale soit un bug de mesure, soit un
trou dans les logs : dans les deux cas, l'analyse du mémoire reposerait sur du
sable.

C'est volontairement une **re-dérivation indépendante**, pas une relecture :
le rejeu n'utilise que l'état réel et les actions parsées, jamais les mesures
déjà calculées.

Usage : `python -m journal.rejouer C:\\arene-runs\\AE-station-r2\\logs`
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from moteur import (
    BOTS,
    Action,
    Carte,
    Contexte,
    InfoSet,
    Position,
    completer_politique,
    ecart,
    jouer_manche,
)

from .ecrivains import lire_sessions, lire_tours

#: Tolérance sur les mesures relues : les logs portent des flottants, la
#: re-dérivation des `Fraction`. Le champ `mesures.exact` permet, lui, une
#: comparaison strictement exacte — c'est celle qui fait foi quand il est là.
TOLERANCE = 1e-9

_ACTIONS = {a.value: a for a in Action}
_CONTEXTES = {c.value: c for c in Contexte}


@dataclass
class Rapport:
    """Ce que le rejeu a trouvé. `ok` vaut True si rien n'a divergé."""

    manches: int = 0
    sessions: int = 0
    anomalies: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.anomalies

    def signaler(self, message: str) -> None:
        self.anomalies.append(message)

    def __str__(self) -> str:  # pragma: no cover - confort CLI
        etat = "OK" if self.ok else f"{len(self.anomalies)} anomalie(s)"
        return f"{self.manches} manches, {self.sessions} sessions rejouées : {etat}"


def rejouer_manche(
    carte_j1: Carte,
    carte_j2: Carte,
    sequence: Sequence[Action],
) -> int:
    """Re-règle une manche depuis la séquence complète d'actions (gain de J1).

    Un seul décideur scripté sert les deux joueurs : l'arbre de la manche est
    une ligne, l'ordre des décisions est donc celui de la séquence. Le moteur
    valide au passage la légalité de chaque action à l'info-set atteint — une
    séquence impossible lève, ce qui est le comportement voulu.
    """
    file = list(sequence)

    def decideur(_: InfoSet) -> Action:
        if not file:
            raise ValueError("séquence d'actions trop courte pour la manche loguée")
        return file.pop(0)

    resultat = jouer_manche(decideur, decideur, carte_j1, carte_j2)
    if file:
        raise ValueError(f"{len(file)} action(s) loguée(s) en trop dans la manche")
    return resultat.gain_j1


def _manches(tours: Iterable[Mapping[str, Any]]) -> Mapping[tuple[int, int], list[dict]]:
    groupes: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for tour in tours:
        groupes[(tour["session"], tour["manche"])].append(dict(tour))
    for cle in groupes:
        groupes[cle].sort(key=lambda t: t["decision"])
    return groupes


def _infoset_depuis_cle(cle: str) -> InfoSet:
    """Inverse de `str(InfoSet)` : `"J1/C1/face_mise"` → l'info-set."""
    position, carte, contexte = cle.split("/")
    return InfoSet(Position(position), Carte[carte], _CONTEXTES[contexte])


def estimer_pi_hat(tours: Iterable[Mapping[str, Any]]) -> tuple[dict[InfoSet, Fraction], dict[InfoSet, int]]:
    """Fréquences brutes par info-set (PRD 3 §6.1).

    Les décisions marquées `action_par_defaut` sont **exclues** : elles disent
    quelque chose du harnais, pas de la politique de l'agent.
    """
    agressives: dict[InfoSet, int] = defaultdict(int)
    effectifs: dict[InfoSet, int] = defaultdict(int)
    for tour in tours:
        if "action_par_defaut" in tour.get("flags", ()):
            continue
        infoset = _infoset_depuis_cle(tour["infoset"])
        effectifs[infoset] += 1
        if _ACTIONS[tour["action_parsee"]] is infoset.action_agressive:
            agressives[infoset] += 1
    pi_hat = {ifs: Fraction(agressives[ifs], n) for ifs, n in effectifs.items() if n}
    return pi_hat, dict(effectifs)


def rejouer_run(dossier: Path | str) -> Rapport:
    """Rejoue un run complet et confronte le résultat à `sessions.jsonl`."""
    dossier = Path(dossier)
    rapport = Rapport()
    tours = list(lire_tours(dossier))
    sessions = {s["session"]: s for s in lire_sessions(dossier)}

    par_session: dict[int, list[dict]] = defaultdict(list)
    for (session, manche), decisions in _manches(tours).items():
        par_session[session].extend(decisions)
        rapport.manches += 1
        _verifier_manche(session, manche, decisions, rapport)

    for session, decisions in sorted(par_session.items()):
        if session not in sessions:
            rapport.signaler(f"session {session} : tours logués sans ligne de session")
            continue
        rapport.sessions += 1
        _verifier_session(sessions[session], decisions, rapport)

    for session in sessions:
        if session not in par_session:
            rapport.signaler(f"session {session} : ligne de session sans aucun tour logué")

    return rapport


def _verifier_manche(
    session: int,
    manche: int,
    decisions: Sequence[Mapping[str, Any]],
    rapport: Rapport,
) -> None:
    final = decisions[-1]
    etat = final["etat_reel"]
    sequence = final.get("historique_final")
    if sequence is None:
        rapport.signaler(
            f"s{session}/m{manche} : `historique_final` absent — manche non re-règlable"
        )
        return
    if final.get("resultat_manche") is None:
        rapport.signaler(f"s{session}/m{manche} : résultat absent sur la dernière décision")
        return

    position_agent = Position(etat["position_agent"])
    carte_agent = Carte(etat["carte_agent"])
    carte_bot = Carte(etat["carte_bot"])
    if position_agent is Position.J1:
        carte_j1, carte_j2 = carte_agent, carte_bot
    else:
        carte_j1, carte_j2 = carte_bot, carte_agent

    try:
        gain_j1 = rejouer_manche(carte_j1, carte_j2, [_ACTIONS[a] for a in sequence])
    except (ValueError, KeyError) as exc:
        rapport.signaler(f"s{session}/m{manche} : rejeu impossible ({exc})")
        return

    gain_agent = gain_j1 if position_agent is Position.J1 else -gain_j1
    if gain_agent != final["resultat_manche"]:
        rapport.signaler(
            f"s{session}/m{manche} : résultat rejoué {gain_agent:+d} "
            f"≠ résultat logué {final['resultat_manche']:+d}"
        )


def _verifier_session(
    session: Mapping[str, Any],
    decisions: Sequence[Mapping[str, Any]],
    rapport: Rapport,
) -> None:
    numero = session["session"]
    pi_partielle, effectifs = estimer_pi_hat(decisions)
    pi_hat, _ = completer_politique(pi_partielle)

    for cle, valeurs in session.get("pi_hat", {}).items():
        if not isinstance(valeurs, Mapping):
            continue
        infoset = _infoset_depuis_cle(cle)
        attendu = effectifs.get(infoset, 0)
        if valeurs.get("n") != attendu:
            rapport.signaler(
                f"s{numero} : effectif de {cle} logué {valeurs.get('n')} ≠ rejoué {attendu}"
            )
        elif attendu and abs(float(valeurs.get("p", 0)) - float(pi_partielle[infoset])) > TOLERANCE:
            rapport.signaler(
                f"s{numero} : π̂({cle}) logué {valeurs.get('p')} ≠ rejoué {float(pi_partielle[infoset])}"
            )

    bot = BOTS.get(session["bot"])
    if bot is None:
        rapport.signaler(f"s{numero} : bot inconnu {session['bot']!r}")
        return

    rejoue = ecart(pi_hat, bot)
    exact = session["mesures"].get("exact", {}).get("ecart_exploitation")
    if exact is not None:
        if Fraction(exact) != rejoue:
            rapport.signaler(
                f"s{numero} : écart logué {exact} ≠ écart rejoué {rejoue} (comparaison exacte)"
            )
    elif abs(float(session["mesures"]["ecart_exploitation"]) - float(rejoue)) > TOLERANCE:
        rapport.signaler(
            f"s{numero} : écart logué {session['mesures']['ecart_exploitation']} "
            f"≠ écart rejoué {float(rejoue)}"
        )

    manches = {(d["manche"]) for d in decisions}
    if len(manches) != session["K"]:
        rapport.signaler(f"s{numero} : {len(manches)} manches loguées pour K = {session['K']}")


def main(argv: Sequence[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    analyseur.add_argument("dossier", nargs="+", help="dossier(s) logs/ d'un run")
    arguments = analyseur.parse_args(argv)

    code = 0
    for dossier in arguments.dossier:
        rapport = rejouer_run(dossier)
        print(f"{dossier} — {rapport}")
        for anomalie in rapport.anomalies:
            print(f"  · {anomalie}")
        code |= 0 if rapport.ok else 1
    return code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["TOLERANCE", "Rapport", "estimer_pi_hat", "main", "rejouer_manche", "rejouer_run"]
