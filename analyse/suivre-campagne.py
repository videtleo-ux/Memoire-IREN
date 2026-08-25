# Moniteur de la tranche SM+AE : n'imprime que ce sur quoi on agirait.
# Un run termine, une erreur, un seuil de budget franchi. Le silence veut dire
# « ca avance », jamais « je ne regarde plus » : le bash qui l'appelle detecte
# aussi la fin de la tranche.
import json
import sys
from pathlib import Path

RACINE = Path("C:/arene-runs")
ETAT = Path(sys.argv[1])
# Seuils sur le cout de la TRANCHE en cours, pas sur le cumul : les 13,01 $
# de SM+AE sont deja payes et le solde a ete recharge depuis (50 $).
SEUILS = (20.0, 35.0, 45.0, 48.0)
TRANCHE = "ICL"

etat = json.loads(ETAT.read_text(encoding="utf-8")) if ETAT.exists() else {}
finis_vus = set(etat.get("finis", []))
erreurs_vues = set(etat.get("erreurs", []))
seuils_vus = set(etat.get("seuils", []))

# --- coût réel, depuis les seules lignes de série closes -------------------
cout = 0.0
cout_tranche = 0.0
series_par_run = {}
cout_par_run = {}
for chemin in RACINE.glob("run-*/logs/sessions.jsonl"):
    try:
        for ligne in chemin.read_text(encoding="utf-8").splitlines():
            if not ligne.strip():
                continue
            d = json.loads(ligne)
            c = (d.get("cout_session_tokens") or {}).get("cout_usd") or 0.0
            cout += c
            if d["condition"] == TRANCHE:
                cout_tranche += c
            cout_par_run[d["run_id"]] = cout_par_run.get(d["run_id"], 0.0) + c
            series_par_run.setdefault(d["run_id"], []).append(
                d["mesures"]["ecart_exploitation"]
            )
    except (OSError, ValueError):
        pass  # série en cours d'écriture : on relira dans 90 s


def integrite(run_id):
    for chemin in RACINE.glob("run-*/logs/integrite.json"):
        try:
            r = json.loads(chemin.read_text(encoding="utf-8"))
            if r.get("run_id") == run_id:
                return "OK" if r.get("ok") else f"ANOMALIES {r.get('anomalies')}"
        except (OSError, ValueError):
            pass
    return "?"

lancements = RACINE / "lancements"

# --- runs terminés ---------------------------------------------------------
finis = set()
for sortie in lancements.glob("*.out"):
    try:
        if "CSV dans" in sortie.read_text(encoding="utf-8", errors="replace"):
            finis.add(sortie.stem)
    except OSError:
        pass

for run_id in sorted(finis - finis_vus):
    ecarts = series_par_run.get(run_id, [])
    courbe = " -> ".join(f"{e:.3f}" for e in ecarts[:3])
    if len(ecarts) > 3:
        courbe += f" ... {ecarts[-1]:.3f}"
    print(
        f"termine {run_id} : {len(ecarts)} series, ecart {courbe} "
        f"| integrite {integrite(run_id)} | cout campagne {cout:.2f} $"
    )

# --- jalon : les 9 runs AE sont boucles ------------------------------------
# Emis une seule fois. C'est la moitie de la tranche qui porte la contribution
# du memoire (AE contre ICL) : elle merite son bilan, sans attendre les SM.
AE = {f"AE-{bot}-r{r}" for bot in ("station", "over-folder", "gto") for r in (1, 2, 3)}
ICL = {f"ICL-{bot}-r{r}" for bot in ("station", "over-folder") for r in (1, 2, 3)}
if AE <= finis and "ae" not in etat.get("jalons", []):
    cout_ae = sum(v for k, v in cout_par_run.items() if k.startswith("AE-"))
    print("=" * 62)
    print(f"LES 9 RUNS AE SONT TERMINES - cout AE {cout_ae:.2f} $ (campagne {cout:.2f} $)")
    for run_id in sorted(AE):
        ecarts = series_par_run.get(run_id, [])
        if ecarts:
            depart, arrivee = ecarts[0], ecarts[-1]
            plancher = min(ecarts)
            print(
                f"  {run_id:<22} {len(ecarts):>2} series | "
                f"{depart:.3f} -> {arrivee:.3f} (mini {plancher:.3f}) | {integrite(run_id)}"
            )
        else:
            print(f"  {run_id:<22} AUCUNE SERIE CLOSE | {integrite(run_id)}")
    print("les 9 runs SM prennent le relais (3 series chacun, ~3 h)")
    print("=" * 62)
    etat.setdefault("jalons", []).append("ae")

if ICL <= finis and "icl" not in etat.get("jalons", []):
    print("=" * 62)
    print(f"LES 6 RUNS ICL SONT TERMINES - cout ICL {cout_tranche:.2f} $")
    for run_id in sorted(ICL):
        e = series_par_run.get(run_id, [])
        if e:
            print(f"  {run_id:<22} {len(e):>2} series | {e[0]:.3f} -> {e[-1]:.3f} "
                  f"(mini {min(e):.3f}) | {integrite(run_id)}")
    print("=" * 62)
    etat.setdefault("jalons", []).append("icl")

# --- erreurs ---------------------------------------------------------------
for err in lancements.glob("*.err"):
    try:
        texte = err.read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    for motif in ("ErreurArbitre", "EchecCanari", "Traceback"):
        cle = f"{err.stem}:{motif}"
        if motif in texte and cle not in erreurs_vues:
            erreurs_vues.add(cle)
            extrait = [l for l in texte.splitlines() if motif in l]
            print(f"ERREUR {err.stem} [{motif}] {extrait[0][:200] if extrait else ''}")

# --- budget ----------------------------------------------------------------
for seuil in SEUILS:
    if cout_tranche >= seuil and str(seuil) not in seuils_vus:
        seuils_vus.add(str(seuil))
        print(f"BUDGET {TRANCHE} : {cout_tranche:.2f} $ sur 50 disponibles "
              f"(seuil {seuil} $ franchi) - cumul campagne {cout:.2f} $")

ETAT.write_text(
    json.dumps(
        {
            "finis": sorted(finis),
            "erreurs": sorted(erreurs_vues),
            "seuils": sorted(seuils_vus),
            "jalons": etat.get("jalons", []),
        }
    ),
    encoding="utf-8",
)
