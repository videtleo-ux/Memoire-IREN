# PROGRESS.md — Suivi d'avancement

Dernière mise à jour : 2026-08-21. Convention : ✅ fait · 🔄 en cours · ⬜ à faire · ⚠️ bloqué/attention.

## Phase 0 — Cadrage (✅ terminée le 2026-08-19)

- ✅ Lecture et analyse de la spec (`spec-build-arene-kuhn(1).md`)
- ✅ Questionnaire de cadrage pilote + réponses (budget, N=3, K=200, lexique, périmètre)
- ✅ Audit de l'environnement : Hermes Agent identifié et inspecté (mémoire native, `hermes -z`, pièges de persistance/isolation/OneDrive)
- ✅ Re-dérivation analytique complète de l'équilibre de Kuhn et de l'oracle de tests ; constante contestée tranchée (couverture J1-Vael = 2/3 à α=1/3)
- ✅ Décisions transverses D1–D8 figées
- ✅ `CONTEXT.md` créé

## Phase 1 — PRD (✅ terminée le 2026-08-19)

- ✅ `prd/00-vue-densemble.md` — architecture, décisions D1–D8, paramètres, carte des PRD
- ✅ `prd/01-moteur-de-jeu.md` — règles obfusquées, bots, GTO (constante tranchée : 2/3), meilleure réponse, écart exact, oracle de tests T1–T9 · **v1.1** : formules en α de T5/T6 corrigées (§7.1) au moment de l'implémentation
- ✅ `prd/02-harnais-memoire.md` — 3 conditions via hermes -z, gel fichiers, isolation HERMES_HOME + canari, prompts, parsing des actions
- ✅ `prd/03-arbitre-orchestration.md` — boucle de session, 3 flux aléatoires seedés, critère de plateau automatisé, pilote de calibrage, enveloppe de coût 20–50 €
- ✅ `prd/04-logging-analyse.md` — schémas turns.jsonl/sessions.jsonl, CSV dérivés, Git, détecteur dé-obfuscation/récitation, plan d'analyse

## Phase 2 — Build (🔄 en cours, ordre imposé par les dépendances)

- ✅ Moteur de jeu + suite de tests oracle (PRD 1) — `src/moteur/`, `tests/test_moteur.py`, **41 tests**, arithmétique exacte en `Fraction`, zéro dépendance
- ✅ Harnais mémoire (PRD 2) — `src/harnais/`, `tests/test_harnais.py`, **56 tests**. Gabarits obfusqués + hash des règles, parsing strict/repli/relance/défaut, gel fichiers, stores isolés, canari d'isolation, 3 conditions SM/ICL/AE. **Canari exécuté pour de vrai** le 2026-08-21 (store jetable, modèle gratuit) : écriture confirmée dans le store du run, absente du home global, écriture impossible en configuration de manche.
- ✅ Logging (PRD 4) — `src/journal/`, `tests/test_journal.py`, **44 tests**. Schémas JSONL validés à l'écriture, détecteur dé-obfuscation/récitation à deux niveaux, CSV dérivés, `rejouer.py` (re-règle chaque manche depuis les seuls logs et retrouve π̂ et l'écart).
- ✅ Arbitre & orchestration (PRD 3) — `src/arbitre/`, `tests/test_arbitre.py`, **43 tests**. Donnes *dérivées* de la graine de campagne (fonction pure de `(graine, r, s, k)`, donc appariées entre conditions par construction), flux du bot seedé par manche, boucle session/manche avec gel avant chaque manche, manche atomique (rejeu à donne identique sur `ErreurHarnais`), récap canonique, π̂ + mesures exactes, critère de plateau automatisé, état de run et reprise sur incident, vérifications d'intégrité de clôture, CLI `python -m arbitre`.
- ✅ Test de bout en bout : mini-run `SM-station-r1` (1 série, K = 20, Station, SM, `tencent/hy3:free`) exécuté le 2026-08-21. Intégrité verte, rejeu complet, **100 % de parsing**, positions 10/10, canari et gel prouvés sur le binaire réel, écart = 1/18 exact. Quatre constats consignés en `CONTEXT.md` §4 quater.

Total : **201 tests verts en ~13 s**, toujours sans dépendance ni appel API dans la suite.

## Phase 3 — Pilote de calibrage (🔄 quasi terminé, 2026-08-21)

- ✅ **Modèle arrêté** : `openai/gpt-5.6-luna`, effort `medium`. Parsing **260/260** sur 4 runs réels. `tencent/hy3:free` écarté (ignore le contrôle d'effort, 4 000 tokens de raisonnement non réductibles, 5× plus lent).
- ✅ **K = 150 validé sur pièces** : |écart(150) − écart(200)| = 0,0032, quinze fois sous le seuil du PRD 3 §7.3.
- ✅ **Coût projeté** : 41 $ attendu (plateau à 10 séries), 63 $ au pire (plafond 16). Mesuré : 0,172 $ la série de 200 manches.
- ✅ **Les trois conditions tournent pour de vrai.** AE atteint la meilleure réponse exacte après une seule réflexion ; ICL descend plus lentement ; SM plafonne à ~0,23 — pas d'effet plafond, la marge de mesure existe.
- ✅ **Deux failles majeures trouvées et corrigées** (pièges n°7 et n°8, `CONTEXT.md` §4 quinquies) : `CLAUDE.md` injecté dans le prompt de l'agent, et les échecs de fournisseur pris pour des réponses.
- ✅ **Fenêtre ICL portée à 13 000 tokens** (3 séries entières à K=150). À 6 000, elle n'en contenait plus qu'une et H3 devenait tautologique.
- ⬜ Installation + vérification d'Hermes Agent sur le Mac M2 (si campagne multi-machines confirmée)

## Phase 4 — Campagne (⬜)

- ⬜ 27 runs (3 conditions × 3 bots × N=3), affectation run→machine randomisée et loguée
- ⬜ Collecte centralisée des logs via Git
- ⬜ Vérifications d'intégrité (donnes communes identiques, isolation, drapeaux de dé-obfuscation)

## Phase 5 — Analyse & mémoire (⬜)

- ⬜ Courbes d'écart d'exploitation par condition × bot (plate / dents de scie / escalier ?)
- ⬜ Analyse du contenu MEMORY.md (que distille l'agent ? élagage destructeur ?)
- ⬜ Test d'effet-machine a posteriori
- ⬜ Rédaction du mémoire + préparation soutenance

## ⚠️ Points ouverts / bloquants

| Point | Porteur | Impact si non résolu |
|---|---|---|
| Papier Loriente & Diez à transmettre | Léo | Aucun sur le build (D6) ; manque un recoupement citable dans le mémoire |
| Hermes non installé sur le Mac M2 | Léo | Campagne mono-machine (plus lente), pas d'invalidation |
| Audit indépendant avant campagne | Léo | Deux failles de contamination trouvées par hasard au pilote ; une troisième passerait inaperçue |

## Journal des sessions de travail

| Date | Fait |
|---|---|
| 2026-08-19 | Cadrage complet, audit environnement, oracle analytique, D1–D8, CONTEXT.md, PROGRESS.md, PRD 00–04 rédigés. |
| 2026-08-19 | **Phase 2, étape 1 : moteur de jeu implémenté et testé** (`src/moteur/`, 41 tests T1–T9 verts). Constante GTO 2/3 confirmée par T2 (la variante 1/3 est bien exploitable). Formules en α de T5/T6 corrigées → PRD 1 v1.1 §7.1. |
| 2026-08-21 | **Phase 2, étapes 2 et 3 : harnais mémoire (PRD 2) et logging (PRD 4)** (`src/harnais/`, `src/journal/`, 100 tests de plus, 141 au total). Clés de config Hermes relevées dans son code source et **vérifiées sur machine** ; canari d'isolation réel passé. Trois constats à retenir : `context_engine` est le toolset « zéro outil » utilisable (`memory` en expose exactement un) ; le modèle gratuit hallucine des appels d'outils quand on ne lui en donne aucun (drapeau `sortie_pseudo_outil`) ; l'auto-déclaration d'outils par l'agent n'est pas fiable, le canari vérifie donc un fichier, pas une réponse. |
| 2026-08-21 | **Phase 2, étape 4 : arbitre & orchestration (PRD 3)** (`src/arbitre/`, 43 tests de plus, 184 au total). Le build est terminé : aucune couche ne manque entre la graine de campagne et le CSV d'analyse. Quatre choix d'implémentation à retenir (détail en `CONTEXT.md` §4 ter) : donnes **dérivées** au lieu de tirées ; manche **atomique** (les tours ne sont écrits qu'à la fin de la manche) ; tours d'une série interrompue **déplacés** vers `turns.abandonnes.jsonl` ; π̂ estimée depuis les lignes de log déjà écrites, via `journal.estimer_pi_hat`. **Prochaine action : le mini-run de bout en bout** — `PYTHONPATH=src python -m arbitre --condition SM --bot Station --K 20 --series 1`, sur le modèle gratuit, premier appel API réel du projet. |
| 2026-08-21 | **Phase 3 : pilote de calibrage complet** sur `openai/gpt-5.6-luna`. Sept runs réels, les trois conditions éprouvées. **Deux failles majeures trouvées et corrigées** : Hermes injectait `CLAUDE.md` du dépôt — donc le corrigé de l'expérience — dans son prompt système à chaque manche (piège n°7) ; et `hermes -z` rendait les échecs de fournisseur sur stdout avec le code retour 0, où le harnais les prenait pour des réponses du modèle (piège n°8). Modèle et paramètres arrêtés, K=150 validé sur pièces, budget borné à 41-63 $. **AE atteint la meilleure réponse exacte après une seule réflexion.** Détail en `CONTEXT.md` §4 quinquies. **Prochaine action : trancher la fenêtre ICL, puis lancer la campagne.** |
