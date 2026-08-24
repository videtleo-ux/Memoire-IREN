# Exporte les notes memoire des runs AE dans un fichier lisible.
# memoire.csv ne porte que les tailles ; le contenu vit dans sessions.jsonl.
import collections
import glob
import json

runs = collections.defaultdict(list)
for chemin in sorted(glob.glob("C:/arene-runs/run-*/logs/sessions.jsonl")):
    for ligne in open(chemin, encoding="utf-8"):
        if not ligne.strip():
            continue
        j = json.loads(ligne)
        if j["condition"] == "AE":
            runs[j["run_id"]].append(j)

out = [
    "# Notes mémoire des runs AE",
    "",
    "Contenu intégral de `MEMORY.md` à chaque frontière de série, tel que l'agent",
    "l'a écrit lui-même. Source : champ `memoire.M_s1` de `sessions.jsonl`.",
    "",
    "L'état servi *pendant* la série s (`M_s`) est celui écrit à la frontière",
    "précédente : la note de la série 0 est donc ce que l'agent a lu pendant la",
    "série 1. La série 0 se joue avec une mémoire vide.",
    "",
]

total = 0
for run in sorted(runs):
    series = sorted(runs[run], key=lambda j: j["session"])
    out += [f"## {run}", ""]
    for j in series:
        m = j["memoire"]
        total += 1
        evenements = ", ".join(e["type"] for e in m["evenements"]) or "aucun"
        out += [
            f"### Série {j['session']} — écart {j['mesures']['ecart_exploitation']:.4f}"
            f" — {m['entrees_m_s1']} entrée(s), {len(m['M_s1'])} caractères",
            "",
            f"*Événements : {evenements}. Écritures bloquées pendant la série :"
            f" {m['ecritures_intra_serie']}.*",
            "",
            "```",
            m["M_s1"].strip() or "(mémoire vide)",
            "```",
            "",
        ]
    out.append("")

CIBLE = "C:/arene-runs/csv/notes-ae.md"
with open(CIBLE, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

import os

print("frontieres exportees :", total, "| runs :", len(runs))
print("fichier :", CIBLE, "|", os.path.getsize(CIBLE), "octets")
