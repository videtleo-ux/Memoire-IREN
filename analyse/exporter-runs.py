# Metadonnees d'execution : une ligne par run.
# Ce que les CSV de mesure ne portent pas — parametres, preuves d'isolation,
# verdicts d'integrite, budget — et sans quoi une campagne n'est pas reproductible.
import csv
import glob
import json
import os
import sys

SORTIE = sys.argv[1]
COLONNES = [
    "run_id", "condition", "bot", "replication", "machine", "graine", "K",
    "series_jouees", "plateau_declare_a", "version_arene",
    "canari_reel", "canari_ecriture_confirmee", "canari_ecriture_bloquee_en_manche",
    "integrite_ok", "integrite_anomalies", "series_controlees", "tours_controles",
    "decisions", "actions_par_defaut", "relances", "erreurs_harnais",
    "ecritures_intra_serie", "gel_rompu",
    "tokens_in", "tokens_out", "tokens_raisonnement", "tokens_cache_ecrits",
    "cout_usd", "demarre_le", "maj_le", "dossier",
]

lignes = []
for dossier in sorted(glob.glob("C:/arene-runs/run-*/")):
    etat_p = os.path.join(dossier, "etat_run.json")
    if not os.path.exists(etat_p):
        continue
    etat = json.load(open(etat_p, encoding="utf-8"))
    canari = etat.get("canari", {})

    integ_p = os.path.join(dossier, "logs", "integrite.json")
    integ = json.load(open(integ_p, encoding="utf-8")) if os.path.exists(integ_p) else {}

    agg = dict.fromkeys(
        ["decisions", "actions_par_defaut", "relances", "erreurs_harnais",
         "ecritures_intra_serie", "tokens_in", "tokens_out", "tokens_raisonnement",
         "tokens_cache_ecrits"], 0)
    agg["cout_usd"] = 0.0
    gel_rompu = 0
    series = 0
    for l in open(os.path.join(dossier, "logs", "sessions.jsonl"), encoding="utf-8"):
        if not l.strip():
            continue
        j = json.loads(l)
        series += 1
        d, c = j["defauts"], j.get("cout_session_tokens") or {}
        agg["actions_par_defaut"] += d["actions_par_defaut"]
        agg["relances"] += d["relances"]
        agg["erreurs_harnais"] += d["erreurs_harnais"]
        agg["ecritures_intra_serie"] += j["memoire"]["ecritures_intra_serie"]
        gel_rompu += 1 if j["memoire"]["gel_rompu"] else 0
        for k, src in (("tokens_in", "in"), ("tokens_out", "out"),
                       ("tokens_raisonnement", "raisonnement"),
                       ("tokens_cache_ecrits", "cache_ecrits")):
            agg[k] += c.get(src) or 0
        agg["cout_usd"] += c.get("cout_usd") or 0
    agg["decisions"] = sum(1 for _ in open(os.path.join(dossier, "logs", "turns.jsonl"), encoding="utf-8"))

    lignes.append({
        "run_id": etat["run_id"], "condition": etat["condition"], "bot": etat["bot"],
        "replication": etat["replication"], "machine": etat["machine"],
        "graine": etat["graine"], "K": etat["K"], "series_jouees": series,
        "plateau_declare_a": etat.get("plateau_declare_a"),
        "version_arene": etat.get("version_arene"),
        "canari_reel": canari.get("reel"),
        "canari_ecriture_confirmee": canari.get("ecriture_confirmee"),
        "canari_ecriture_bloquee_en_manche": canari.get("ecriture_bloquee_en_manche"),
        "integrite_ok": integ.get("ok"),
        "integrite_anomalies": " | ".join(integ.get("anomalies") or []) or "aucune",
        "series_controlees": integ.get("series"), "tours_controles": integ.get("tours"),
        "gel_rompu": gel_rompu,
        "cout_usd": round(agg.pop("cout_usd"), 6),
        **agg,
        "demarre_le": etat.get("demarre_le"), "maj_le": etat.get("maj_le"),
        "dossier": os.path.basename(dossier.rstrip("/\\")),
    })

lignes.sort(key=lambda x: (x["condition"], x["bot"], x["replication"]))
with open(SORTIE, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLONNES)
    w.writeheader()
    w.writerows(lignes)

print("runs :", len(lignes))
print("cout total :", round(sum(l["cout_usd"] for l in lignes), 2), "$")
print("decisions :", sum(l["decisions"] for l in lignes))
print("integrite verte :", sum(1 for l in lignes if l["integrite_ok"]), "/", len(lignes))
