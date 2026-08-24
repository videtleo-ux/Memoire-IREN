# Exporte les journaux de tours en CSV exploitable : une ligne par decision.
#
# Le prompt servi (`vue_servie`) est ecarte : il est reconstructible a
# l'identique depuis les gabarits + l'etat, il est repete a chaque manche, et il
# represente ~60 % des 65 Mo. Le raisonnement du modele (`sortie_brute`), lui,
# est conserve : c'est une donnee, pas une repetition.
import csv
import glob
import json
import os
import sys

SORTIE = sys.argv[1]
COLONNES = [
    "run_id", "condition", "bot", "replication", "session", "manche", "decision",
    "position_agent", "carte_agent", "carte_bot", "carte_ecartee",
    "historique", "infoset", "infoset_numero", "action_parsee", "parsing",
    "resultat_manche", "historique_final", "flags",
    "tokens_in", "tokens_out", "tokens_raisonnement", "tokens_cache_lus",
    "tokens_cache_ecrits", "cout_usd", "latence_ms", "modele", "horodatage",
    "sortie_brute",
]

n = 0
with open(SORTIE, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLONNES)
    w.writeheader()
    for chemin in sorted(glob.glob("C:/arene-runs/run-*/logs/turns.jsonl")):
        for ligne in open(chemin, encoding="utf-8"):
            if not ligne.strip():
                continue
            t = json.loads(ligne)
            e, tok = t["etat_reel"], t.get("tokens") or {}
            w.writerow({
                "run_id": t["run_id"], "condition": t["condition"], "bot": t["bot"],
                "replication": t["replication"], "session": t["session"],
                "manche": t["manche"], "decision": t["decision"],
                "position_agent": e["position_agent"], "carte_agent": e["carte_agent"],
                "carte_bot": e["carte_bot"], "carte_ecartee": e["carte_ecartee"],
                "historique": " ".join(e["historique"]),
                "infoset": t["infoset"], "infoset_numero": t["infoset_numero"],
                "action_parsee": t["action_parsee"], "parsing": t["parsing"],
                "resultat_manche": t.get("resultat_manche"),
                "historique_final": " ".join(t["historique_final"] or []),
                "flags": " ".join(t.get("flags") or []),
                "tokens_in": tok.get("in"), "tokens_out": tok.get("out"),
                "tokens_raisonnement": tok.get("raisonnement"),
                "tokens_cache_lus": tok.get("cache_lus"),
                "tokens_cache_ecrits": tok.get("cache_ecrits"),
                "cout_usd": t.get("cout_usd"), "latence_ms": t.get("latence_ms"),
                "modele": t.get("modele"), "horodatage": t.get("horodatage"),
                "sortie_brute": t["sortie_brute"],
            })
            n += 1

print(f"decisions exportees : {n}")
print(f"taille : {os.path.getsize(SORTIE)/1048576:.1f} Mo")
