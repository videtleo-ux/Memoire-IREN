# PROGRESS.md — Suivi d'avancement

Dernière mise à jour : 2026-08-19. Convention : ✅ fait · 🔄 en cours · ⬜ à faire · ⚠️ bloqué/attention.

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

## Phase 2 — Build (⬜ à faire, ordre imposé par les dépendances)

- ✅ Moteur de jeu + suite de tests oracle (PRD 1) — `src/moteur/`, `tests/test_moteur.py`, **41 tests verts en 3,5 s**, arithmétique exacte en `Fraction`, zéro dépendance
- ⬜ Harnais mémoire : wrapper hermes -z, gel/restauration, isolation par run, canari d'isolation (PRD 2)
- ⬜ Logging : writers JSONL, schémas, détecteur mots-clés (PRD 4, en parallèle du harnais)
- ⬜ Arbitre : boucle session/manche, intégration moteur+harnais+logs (PRD 3)
- ⬜ Test de bout en bout : 1 mini-run (1 session, K réduit ~20, bot Station, condition SM) sur le Victus

## Phase 3 — Pilote de calibrage (⬜)

- ⬜ Choix du modèle définitif (shortlist PRD 2) : taux de parsing, coût/manche, latence
- ⬜ Validation de K=200 (stabilité de π̂) ou ajustement
- ⬜ Estimation du coût total de la campagne → go/no-go sur le budget
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
| Modèle définitif non choisi | Pilote (Phase 3) | Bloque le lancement de la campagne, pas le build |

## Journal des sessions de travail

| Date | Fait |
|---|---|
| 2026-08-19 | Cadrage complet, audit environnement, oracle analytique, D1–D8, CONTEXT.md, PROGRESS.md, PRD 00–04 rédigés. |
| 2026-08-19 | **Phase 2, étape 1 : moteur de jeu implémenté et testé** (`src/moteur/`, 41 tests T1–T9 verts). Constante GTO 2/3 confirmée par T2 (la variante 1/3 est bien exploitable). Formules en α de T5/T6 corrigées → PRD 1 v1.1 §7.1. **Prochaine action : PRD 2 (harnais mémoire) et PRD 4 (logging) en parallèle.** |
