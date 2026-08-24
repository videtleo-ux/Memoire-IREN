# Extrait de sessions.csv le strict necessaire a la page de resultats.
import csv
import collections
import json
import statistics

lignes = list(csv.DictReader(open("C:/arene-runs/csv/sessions.csv", encoding="utf-8")))

RECITANT = {"Over-folder": 7 / 9, "Station": 1 / 9, "GTO": 0.0}

series = collections.defaultdict(list)   # (condition, bot, repl) -> [(session, ecart, ref)]
for x in lignes:
    cle = (x["condition"], x["bot"], x["replication"])
    series[cle].append(
        (int(x["session"]), float(x["ecart"]), float(x["reference_recite"]))
    )
for v in series.values():
    v.sort()

donnees = {"recitant": RECITANT, "bots": ["Over-folder", "Station", "GTO"], "cellules": {}}

for bot in donnees["bots"]:
    cell = {}
    for cond in ("SM", "ICL", "AE"):
        traces = []
        for r in ("1", "2", "3"):
            v = series.get((cond, bot, r), [])
            traces.append({"repl": r, "points": [[s, round(e, 5)] for s, e, _ in v]})
        # moyenne par serie, sur les series ou les 3 replications existent
        par_serie = collections.defaultdict(list)
        for t in traces:
            for s, e in t["points"]:
                par_serie[s].append(e)
        moyenne = [
            [s, round(statistics.mean(v), 5)]
            for s, v in sorted(par_serie.items())
            if len(v) == 3
        ]
        cell[cond] = {"traces": traces, "moyenne": moyenne}
    cell["recitant"] = round(RECITANT[bot], 5)
    donnees["cellules"][bot] = cell

# --- synthese : effet apparie et test H2 --------------------------------
synthese = []
for bot in donnees["bots"]:
    diffs, ae_fin, sm_moy, ref_ae, ref_sm, h3 = [], [], [], [], [], []
    for r in ("1", "2", "3"):
        sm = [e for _, e, _ in series[("SM", bot, r)]]
        ae = [e for _, e, _ in series[("AE", bot, r)]]
        diffs.append(statistics.mean(sm) - ae[-1])
        ae_fin.append(ae[-1])
        sm_moy.append(statistics.mean(sm))
        ref_ae += [v for s, _, v in series[("AE", bot, r)] if s >= 7]
        ref_sm += [v for _, _, v in series[("SM", bot, r)]]
        icl = [e for _, e, _ in series.get(("ICL", bot, r), [])]
        if icl:
            h3.append(statistics.mean(icl[-4:]) - statistics.mean(ae[-4:]))
    synthese.append(
        {
            "bot": bot,
            "sm": round(statistics.mean(sm_moy), 4),
            "ae": round(statistics.mean(ae_fin), 4),
            "reduction": round(statistics.mean(diffs), 4),
            "reductions": [round(d, 4) for d in diffs],
            "ref_sm": round(statistics.mean(ref_sm), 4),
            "ref_ae": round(statistics.mean(ref_ae), 4),
            "ref_max": round(RECITANT[bot], 4),
            "h3": round(statistics.mean(h3), 4) if h3 else None,
            "h3_ic": round(4.303 * statistics.stdev(h3) / (3 ** 0.5), 4) if len(h3) == 3 else None,
            "h3_icl": round(statistics.mean(
                [statistics.mean([e for _, e, _ in series[("ICL", bot, r)]][-4:])
                 for r in ("1", "2", "3")]), 4) if h3 else None,
            "h3_ae": round(statistics.mean(
                [statistics.mean([e for _, e, _ in series[("AE", bot, r)]][-4:])
                 for r in ("1", "2", "3")]), 4) if h3 else None,
        }
    )
donnees["synthese"] = synthese

CIBLE = "C:/Users/videt/AppData/Local/Temp/claude/" \
    "C--Users-videt-OneDrive-Bureau-Fac-Master-2---IREN-Exercices-de-recherches-Exercice-3-M-moire-Code/" \
    "69a6fb30-f3ce-4b32-b63c-1dab0615c239/scratchpad/donnees.json"
with open(CIBLE, "w", encoding="utf-8") as f:
    json.dump(donnees, f, ensure_ascii=False)

for s in synthese:
    print(
        f"{s['bot']:<13} SM {s['sm']:.3f} | AE {s['ae']:.3f} | reduction {s['reduction']:+.3f} "
        f"| ref recitee AE {s['ref_ae']:+.3f} (max {s['ref_max']:+.3f})"
    )
print("json ecrit")
