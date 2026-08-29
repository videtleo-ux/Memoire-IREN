# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & test

```bash
# Le moteur (PRD 1) est stdlib pure — aucune dépendance. pytest suffit.
# `python` sur le PATH pointe vers le venv d'Hermes (3.11, sans pip) : utiliser
# l'interpréteur Anaconda, qui a pytest. Le code tourne sur les deux.
"C:/Users/videt/anaconda3/python.exe" -m pytest -q          # suite complète (~8 s)
"C:/Users/videt/anaconda3/python.exe" -m pytest -q -k t2    # un test de l'oracle
```

`pyproject.toml` fixe `pythonpath = ["src"]` : les tests importent `moteur` sans installation.
Les exécutables, eux, ont besoin de `PYTHONPATH=src` (le paquet n'est pas installé) :

```bash
PYTHONPATH=src python -m arbitre --condition SM --bot Station --K 20 --series 1   # un run
PYTHONPATH=src python -m journal.rejouer C:/arene-runs/SM-station-r1/logs         # complétude
PYTHONPATH=src python -m journal.derives C:/arene-runs --sortie C:/arene-runs/csv # CSV
```

## Repository state

Build terminé — 225 tests verts, zéro dépendance, aucun appel API dans la suite :

- `src/moteur/` + `tests/test_moteur.py` — PRD 1 : moteur de jeu, meilleure réponse, écart d'exploitation, lexique obfusqué (oracle T1–T9, 41 tests).
- `src/harnais/` + `tests/test_harnais.py` — PRD 2 : gabarits de prompt obfusqués, parsing des actions, stores Hermes isolés par run, canari d'isolation, gel mémoire fichiers, trois conditions SM/ICL/AE (56 tests).
- `src/journal/` + `tests/test_journal.py` — PRD 4 : schémas JSONL validés à l'écriture, détecteur dé-obfuscation/récitation, CSV dérivés, rejeu de complétude (44 tests).
- `src/arbitre/` + `tests/test_arbitre.py` — PRD 3 : donnes dérivées et appariées, boucle session/manche, récap canonique, π̂ et mesures, plateau, reprise sur incident, intégrité de clôture, CLI de run (43 tests).

**Campagne terminée (2026-08-24), collecte close. Analyse terminée (2026-08-26).** 24 exécutions, 177 séries, 26 550 manches, 47,27 $ ; rejeu 24/24, intégrité 24/24, zéro action par défaut. **Les quatre hypothèses sont instrumentées et la partie III est rédigée** (`memoire/partie3-v2.md`). Résultats et inventaire complet des données dans `memoire/resultats.md`, données versionnées dans `donnees/`. Ce qui reste est de la rédaction sur les autres chapitres et de la mise en forme — pas d'analyse, pas de collecte. La documentation de référence :

- `docs/spec-build-arene-kuhn.md` — the original build specification (French). Authority on *what* to build; every clause is a fixed design decision.
- `docs/prd/00-vue-densemble.md` … `docs/prd/04-logging-analyse.md` — the PRDs (French). Authority on *how* to build it: architecture, fixed cross-cutting decisions D1–D8, pinned parameters (K=200, N=3, obfuscated lexicon), analytic test oracle, schemas.
- `docs/CONTEXT.md` — living context: pilot constraints, verified environment findings (Hermes Agent install, its memory-persistence pitfalls, OneDrive pitfall), decisions made in discussion. **Read this first in any new session.**
- `docs/AUDIT.md` — adversarial audit brief written before the campaign. Historical: the audit was carried out and its four findings are fixed (C1 opaque run directories, C2 prompt passed by file, C3 provider-failure verdict read from the usage report, C4 cache tokens logged). Its lesson stands — the harness/Hermes boundary is where silent defects live. Read it before touching that boundary.
- `docs/PROGRESS.md` — phase-by-phase status, closed campaign, what remains.
- `memoire/resultats.md` — **the results, and the single inventory of every data file and document.** Start here for anything about the campaign's output.
- `donnees/` — the analysis data, versioned: `sessions.csv` (per series), `decisions.csv` (27 290 decisions with the model's full text), `infosets.csv`, `memoire.csv`, `runs.csv`, `notes-ae.md`. Raw JSONL logs stay out of the repo (401 MB) under `C:\arene-runs`.

**Before implementing, read (in order): `docs/CONTEXT.md`, `docs/prd/00-vue-densemble.md`, then the PRD of the component you're touching, with the spec as backstop.** Do not re-derive the design from first principles. Key resolved points to not re-litigate: the GTO constant dispute is settled (J1 calls with the middle card at α+1/3 = 2/3, self-verified by the `exploitability(GTO)=0` test — PRD 1 §4); all three memory conditions go through `hermes -z` with a dedicated `HERMES_HOME` per run; intra-session memory freezing is enforced by the referee via file snapshot/restore because Hermes persists memory writes immediately; deals are **derived** from the campaign seed (a pure function of `(graine, r, s, k)`), never drawn from a running generator — that is what makes the three conditions byte-for-byte paired.

## Project summary (from the spec)

The goal is to build an **arena** that makes an LLM agent play an **obfuscated Kuhn poker** variant, in repeated games split into **sessions**, against opponents with a **fixed, known policy**, under **three memory conditions**, logging everything at the granularity needed to compute an **exact per-session exploitability gap**.

Guiding principle: any adaptation observed must be attributable to **memory** (the independent variable), not to the harness. The arena builds the *arena*, not the agent — the agent is Hermès (Nous Research), used natively with its own memory mechanism.

### Core mechanics

- **Game**: standard Kuhn poker payoffs/tree (3-card deck, ante 1, single bet of 1, 12 information sets total — 6 per player), but **obfuscated**: no mention of "Kuhn", "poker", or card ranks J/Q/K/1/2/3. Cards become 3 arbitrary tokens with an explicitly stated dominance order (e.g. `Tor ≺ Vael ≺ Rhun`). The same obfuscated vocabulary must be used everywhere (all memory conditions, all bots). The agent's free-text output must be monitored for de-obfuscation ("this is Kuhn poker, the equilibrium is...") — contamination can re-enter via the memory channel across sessions.
- **Reference GTO strategy** (§2): a fixed equilibrium at α = 1/3, used both as a ceiling opponent and as the "recited" baseline. The exact constants (indifference-point call frequencies) must be checked against Loriente & Diez before hard-coding — the exploitability-gap calculation depends on them.
- **Fixed opponent bots** (§3): `GTO` (no exploit available — ceiling), `Station` (never bets/bluffs, always calls a bet — exploit: never bluff, value-bet the top card), `Over-folder` (never bets, always folds to a bet — exploit: bet every hand). Station and Over-folder are deliberately opposite exploits (over-call vs over-fold) so a recited fixed bluff frequency fails in both directions — this is the discriminator for genuine vs. recited adaptation.
- **Exploitability gap** (§4): per session, compute the agent's empirical policy π̂(M_s) over the session's hands, then `Écart(s) = EV(best response) − EV(π̂(M_s))`, computed exactly (12 info sets, direct best-response maximization), not estimated. Compare against the "recited" reference `EV(π̂) − EV(GTO)`.

### Three memory conditions (§5) — same base model everywhere

Model is held constant; memory is the only manipulated variable. One vLLM endpoint serves Hermès's base model; three harnesses call it differently:

1. **No memory**: fresh context every hand. Expected signature: flat curve (floor).
2. **Raw history (ICL)**: past-session transcript injected at session boundary, frozen intra-session, windowed to context limit. Expected signature: sawtooth (relearns then forgets).
3. **Self-written (Hermès)**: native `MEMORY.md`, frozen snapshot per session, reflection/write at the session boundary. Expected signature: monotonic staircase (accumulates).

### Sessions — the adaptation clock (§6)

A **session** is the atomic unit of adaptation, driven by Hermès's frozen-snapshot mechanism: memory is captured at session start, frozen during the session, and only updated visibly at the next session. All three conditions share the same session segmentation.

Referee loop per run (Hermès, "fresh context per hand" condition):
1. Open session s → load memory snapshot `M_s` from the run's isolated store.
2. For k = 1..K hands: deal (shared deal sequence, §8), alternate P1/P2 position, play with a fresh context = frozen `M_s` + current-hand state only (no inter-hand accumulation); referee serves the obfuscated legal view and logs the turn.
3. Close session → referee gives Hermès the K-hand recap; Hermès reflects (Reflexion-style) and writes/updates `MEMORY.md` → persisted as `M_{s+1}`; referee captures the `M_{s+1}` snapshot.
4. Estimate π̂(M_s); compute the session's exploitability gap.
5. Next session loads `M_{s+1}`. Repeat until the gap plateaus (+ margin).

Reset scales: full reset between **runs** (fresh `M_0` per condition/replication); **no** reset between sessions within a run (accumulation is the point); fresh context per hand + frozen `MEMORY.md` intra-session.

`MEMORY.md` constraint: ~8–15 entries, hard cap, **no auto-compaction** — overflow is an error; the agent must self-prune. This must be logged both as an observable (what does it keep?) and a risk (overflow, destructive pruning).

### Isolation trap (§7)

Hermès's `MEMORY.md` lives in `~/.hermes/memories/`. Two parallel Hermès runs on the same machine will silently overwrite each other's memory. Every run needs an isolated store (dedicated `HOME`, dedicated `~/.hermes`, or a container per run) — verify this explicitly, never assume it.

### Orchestration (§8)

- Parallelizable unit = the **run** (S sequential sessions, one opponent, one condition). Sessions within a run must stay on one machine (`M_s` depends on `M_{s-1}`).
- No live game server: a local referee plays one run in isolation; centralized log collection across machines.
- Same deal sequence (common random numbers, seed-paired) served to all three conditions to reduce variance.
- Identical model weights/quantization/inference params across machines (verified); run→machine assignment randomized and logged (for a post-hoc machine-effect test).

### Logging (§9)

- **Per turn**: real state, obfuscated view served, raw model output (including free-text reasoning), parsed action, result.
- **Per session**: input snapshot `M_s` and output snapshot `M_{s+1}`, write/prune events, `π̂(M_s)`, session exploitability gap, P1/P2 position balance, de-obfuscation/recited-equilibrium flags.

### Out of scope for the primary build (§11)

Transfer arm (biased bot then GTO, memory carried across), human arm (human as subject via a separate minimal UI), frozen-LLM adversary — all explicitly deferred extensions, not part of the core build.
