# Recalcule l'ecart d'exploitation SANS importer `src/moteur`, et le confronte
# aux mesures publiees.
#
# Pourquoi ce script existe : le brief d'audit (AUDIT.md §3) declarait un angle
# mort — « l'oracle de mesure et le moteur ont la meme main ». Les tests T1-T9
# verifient le moteur contre une derivation analytique ecrite par le meme auteur ;
# une erreur commune aux deux ne s'y verrait pas. Ce script referme cet angle mort
# en refaisant le calcul par un chemin entierement separe : arbre ecrit a la main
# ici, aucune importation du dispositif, lecture des seuls journaux.
#
#     PYTHONPATH=src python analyse/verifier-mesure-independamment.py
#
# Le calcul, contre Station et Over-folder. Ces deux adversaires ne misent jamais,
# donc l'agent n'a qu'une decision par manche et six ensembles d'information sont
# atteignables. En notant `b` sa frequence d'engagement et `w = c/2` la probabilite
# que son sceau `c` (0, 1, 2) domine celui de l'adversaire :
#
#   Station    couvre toujours   -> EV = (2w-1)(1+b)   [engager double l'enjeu]
#   Over-folder se retire toujours -> EV = b + (1-b)(2w-1)
#
# La meilleure reponse maximise chaque terme separement : +1/3 contre Station
# (engager le seul sceau superieur), +1 contre Over-folder (engager toujours).
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

RACINE = Path(sys.argv[1] if len(sys.argv) > 1 else "C:/arene-runs")

EV_BR = {"Station": 1 / 3, "Over-folder": 1.0}


def ecart_independant(tours, bot):
    """Ecart d'exploitation d'une serie, calcule sans le moteur."""
    n = defaultdict(int)
    agressives = defaultdict(int)
    for t in tours:
        if t["parsing"] == "defaut":      # exclusion : dit du harnais, pas de l'agent
            continue
        e = t["etat_reel"]
        cle = (e["position_agent"], e["carte_agent"])
        n[cle] += 1
        if t["action_parsee"] == "bet":
            agressives[cle] += 1

    ev = 0.0
    for position in ("J1", "J2"):
        for carte in (0, 1, 2):
            w = carte / 2                       # P(mon sceau domine)
            cle = (position, carte)
            if n[cle]:
                b = agressives[cle] / n[cle]
            else:
                # non observe : convention du protocole, valeur d'equilibre
                b = {0: 1 / 3, 1: 0.0, 2: 1.0}[carte]
            if bot == "Station":
                ev += (2 * w - 1) * (1 + b) / 6
            else:                                # Over-folder
                ev += (b + (1 - b) * (2 * w - 1)) / 6
    return EV_BR[bot] - ev


ecarts = 0
pires = []
for chemin in sorted(RACINE.glob("run-*/logs/sessions.jsonl")):
    series = [json.loads(l) for l in open(chemin, encoding="utf-8") if l.strip()]
    if not series or series[0]["bot"] not in EV_BR:
        continue                                  # GTO : arbre plus profond, hors scope
    tours = defaultdict(list)
    for l in open(str(chemin).replace("sessions.jsonl", "turns.jsonl"), encoding="utf-8"):
        t = json.loads(l)
        tours[t["session"]].append(t)
    for j in series:
        publie = j["mesures"]["ecart_exploitation"]
        recalcule = ecart_independant(tours[j["session"]], j["bot"])
        pires.append((abs(publie - recalcule), j["run_id"], j["session"], publie, recalcule))
        ecarts += 1

pires.sort(reverse=True)
print(f"series recalculees sans le moteur : {ecarts}")
print(f"ecart maximal au chiffre publie   : {pires[0][0]:.2e}")
print()
print("les cinq plus grands ecarts :")
for d, run, s, p, r in pires[:5]:
    print(f"  {run:<22} serie {s:>2} | publie {p:.10f} | recalcule {r:.10f} | delta {d:.2e}")

TOLERANCE = 1e-9
if pires[0][0] < TOLERANCE:
    print(f"\nOK — les deux chemins de calcul coincident a {TOLERANCE:.0e} pres.")
else:
    print(f"\nECHEC — divergence au-dela de {TOLERANCE:.0e}.")
    raise SystemExit(1)
