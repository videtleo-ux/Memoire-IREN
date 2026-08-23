# Dimensionnement de la tranche ICL a partir des donnees SM/AE deja acquises.
# Design apparie (memes donnes) : la variance pertinente est celle des
# DIFFERENCES par replication, pas celle des niveaux.
import csv
import collections
import json
import statistics as st

l = list(csv.DictReader(open("C:/arene-runs/csv/sessions.csv", encoding="utf-8")))
par = collections.defaultdict(lambda: collections.defaultdict(list))
for x in l:
    par[(x["bot"], x["replication"])][x["condition"]].append((int(x["session"]), float(x["ecart"])))

BOTS = ("Over-folder", "Station", "GTO")

print("=" * 74)
print("1. DISPERSION INTER-REPLICATIONS (le bruit que le design doit battre)")
print("=" * 74)
sigmas = {}
for bot in BOTS:
    diffs, ae_fin, sm_moy = [], [], []
    for r in ("1", "2", "3"):
        sm = [v for _, v in par[(bot, r)]["SM"]]
        ae = sorted(par[(bot, r)]["AE"])
        diffs.append(st.mean(sm) - ae[-1][1])
        ae_fin.append(ae[-1][1])
        sm_moy.append(st.mean(sm))
    sd_d = st.stdev(diffs)
    sigmas[bot] = sd_d
    print(f"{bot:<13} effet {st.mean(diffs):+.3f}  ecart-type des differences {sd_d:.4f}")
    print(f"{'':<13} niveaux : SM sd {st.stdev(sm_moy):.4f} | AE sd {st.stdev(ae_fin):.4f}")

sd_ref = st.mean(list(sigmas.values()))
print(f"\nsigma_d retenu (moyenne des trois cellules) : {sd_ref:.4f} jeton/manche")

print()
print("=" * 74)
print("2. DIFFERENCE MINIMALE DETECTABLE selon le nombre de replications")
print("=" * 74)
# t de Student bilateral a 95 %, ddl = n-1
T95 = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571}
print("n    t(95%)   demi-largeur IC     effet minimal distinguable de zero")
for n in (2, 3, 4, 5, 6):
    demi = T95[n] * sd_ref / (n ** 0.5)
    print(f"{n}    {T95[n]:>6.3f}   +/- {demi:.3f}            {demi:.3f}")
print("n=1  aucun intervalle : l'effet est mesure, jamais encadre")

print()
print("=" * 74)
print("3. QUEL EFFET FAUT-IL DETECTER POUR H3 ? (ICL vs AE)")
print("=" * 74)
# Run ICL reel a K=150 (validation du correctif C2), contre Station
icl = []
for ligne in open(
    "C:/arene-runs-verif-c2/run-f1060d1c067d/logs/sessions.jsonl", encoding="utf-8"
):
    if ligne.strip():
        j = json.loads(ligne)
        icl.append((j["session"], j["mesures"]["ecart_exploitation"]))
icl.sort()
print("ICL reel (K=150, Station, 4 series) :", " ".join(f"{v:.3f}" for _, v in icl))

ae_station = sorted(par[("Station", "1")]["AE"])
print("AE  (K=150, Station, r1)            :", " ".join(f"{v:.3f}" for _, v in ae_station[:4]))
ecarts_h3 = [i[1] - a[1] for i, a in zip(icl, ae_station)]
print("difference ICL - AE, series 0 a 3   :", " ".join(f"{d:+.3f}" for d in ecarts_h3))
print(f"difference a la serie 3 : {ecarts_h3[-1]:+.3f}")

print()
print("=" * 74)
print("4. COUT DES DESIGNS (prix par serie mesures sur le run de validation)")
print("=" * 74)
PRIX = {0: 0.131, 1: 0.388, 2: 0.588}   # au-dela : fenetre pleine
PLEINE = 0.821
def cout_run(series):
    return sum(PRIX.get(s, PLEINE) for s in range(series))

for series in (10, 16):
    c = cout_run(series)
    etiquette = "plateau a 10 series" if series == 10 else "plafond 16 series"
    print(f"\n-- {etiquette} : {c:.2f} $ par execution --")
    for nom, runs in (
        ("3 adversaires x 3 replications", 9),
        ("2 adversaires (sans GTO) x 3 repl.", 6),
        ("2 adversaires x 2 replications", 4),
        ("Over-folder seul x 3 replications", 3),
    ):
        print(f"   {nom:<38} {runs:>2} exec.  {runs*c:>6.1f} $")
