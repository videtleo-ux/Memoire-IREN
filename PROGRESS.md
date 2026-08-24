# PROGRESS.md — Suivi d'avancement

Dernière mise à jour : 2026-08-25. Convention : ✅ fait · 🔄 en cours · ⬜ à faire · ⚠️ attention.

> **La collecte est close.** Les phases 0 à 4 sont terminées : le dispositif est
> construit, calibré, audité, et la campagne a produit ses données. Ce qui reste
> est de l'analyse sur données acquises et de la rédaction. Résultats et
> inventaire des données : `memoire/resultats.md`.

## Phase 0 — Cadrage (✅ 2026-08-19)

- ✅ Spec analysée, questionnaire de cadrage, périmètre arrêté
- ✅ Audit d'environnement : Hermes Agent identifié et inspecté (mémoire native, `hermes -z`, pièges de persistance, d'isolation, OneDrive)
- ✅ Équilibre de Kuhn re-dérivé à la main ; constante contestée tranchée (couverture J1-Vael = 2/3 à α = 1/3)
- ✅ Décisions transverses D1–D8 figées · `CONTEXT.md` créé

## Phase 1 — PRD (✅ 2026-08-19)

- ✅ `prd/00` à `prd/04` — architecture, moteur, harnais, arbitre, journalisation

## Phase 2 — Build (✅ 2026-08-21)

- ✅ Moteur de jeu (PRD 1) — arithmétique exacte en `Fraction`, oracle T1–T9
- ✅ Harnais mémoire (PRD 2) — trois conditions, gel fichiers, stores isolés, canari
- ✅ Journal (PRD 4) — schémas validés à l'écriture, détecteur de dé-obfuscation, rejeu
- ✅ Arbitre (PRD 3) — donnes dérivées, boucle session/manche, plateau, reprise sur incident
- ✅ Mini-run de bout en bout sur modèle gratuit

**225 tests verts**, sans dépendance ni appel API dans la suite.

## Phase 3 — Pilote de calibrage (✅ 2026-08-21)

- ✅ Modèle arrêté : `openai/gpt-5.6-luna`, effort `medium` · K = 150 validé sur pièces
- ✅ Fenêtre ICL portée à trois séries (sans quoi H3 devenait tautologique)
- ✅ **Deux failles de contamination trouvées et corrigées** (pièges n°7 et n°8)
- ✅ Pas d'effet plafond : la marge de mesure existe

## Phase 3 bis — Audit adversarial (✅ 2026-08-22)

Conduit **avant** la campagne, sur un dispositif réputé terminé. Quatre constats,
tous à la frontière avec l'outillage tiers, aucun dans le code du dépôt, aucun
détecté par les tests, aucun visible dans les journaux (`AUDIT.md`, `CONTEXT.md` §4 sexies) :

- ✅ **C1** — le chemin du magasin, servi à l'agent par le prompt système, nommait son adversaire → répertoires d'exécution en code opaque
- ✅ **C2** — le prompt ICL à fenêtre pleine dépasse la ligne de commande Windows → transmission par fichier, sans toucher aux paramètres expérimentaux
- ✅ **C3** — les signatures textuelles de panne étaient incomplètes → verdict lu dans le rapport d'usage d'Hermes
- ✅ **C4** — les tokens d'entrée logués valaient 3 (comptés nets du cache) → les trois postes sont enregistrés

## Phase 4 — Campagne (✅ 2026-08-22 au 24)

- ✅ **Tranche SM + AE** — 18 exécutions, 117 séries, 13,01 $
- ✅ **Tranche ICL** — 6 exécutions (Station et Over-folder, dimensionnement au §2.2.7 du chapitre de méthode), 34,26 $
- ✅ **Total : 24 exécutions, 177 séries, 26 550 manches, 27 290 décisions, 47,27 $**
- ✅ Rejeu de complétude **24/24**, intégrité **24/24**, zéro action par défaut, zéro relance, zéro erreur de harnais, zéro rupture du gel
- ✅ Données versionnées dans `donnees/` ; journaux bruts (401 Mo) hors dépôt

**Trois incidents, tous rattrapés sans perte de données** : limite de débit du
fournisseur prise pour une panne (le harnais patiente désormais) ; révocation de
session par réutilisation d'un jeton à usage unique (magasin de jetons partagé —
piège n°11) ; erreur de passage de paramètres au lanceur, interceptée par le CLI
avant tout appel API.

## Phase 5 — Analyse & mémoire (🔄 en cours)

- ✅ **H1** — l'adaptation vient de la mémoire (effet apparié +0,704 / +0,220 / +0,178 selon l'adversaire, neuf paires sur neuf dans le même sens)
- ✅ **H2** — elle exploite, elle ne récite pas (référence récitée à +0,778 et +0,110, les maxima théoriques ; contrôle négatif tenu)
- ✅ **H3** — le mécanisme de rétention compte, mais seulement là où la tâche exige une politique différenciée (+0,038 ± 0,015 contre Station ; indistinguable contre Over-folder)
- 🔄 **H4** — non instrumentée. Deux mesures automatiques à écrire sur `donnees/` (incohérence raisonnement↔action, dégénérescence des mixtes), plus un codage manuel sur échantillon stratifié
- ✅ Analyse qualitative du canal mémoire (90 notes intégrales dans `donnees/notes-ae.md`)
- 🔄 Chapitre de méthode (`memoire/methodologie.md`) et résultats (`memoire/resultats.md`)
- ⬜ Rédaction des autres chapitres, préparation de la soutenance

### Ce que H4 demande exactement

1. **Incohérence raisonnement↔action**, automatique : comparer l'action de la ligne
   `ACTION:` à la dernière action nommée dans le texte libre. Mesurable sur
   **13 466 décisions (49,3 %)** — celles où l'agent écrit au-delà de sa ligne
   d'action. ⚠️ Biais de sélection à déclarer : 28 % en SM, 36 % en ICL, 64 % en AE.
2. **Dégénérescence des mixtes**, automatique : concentration de `p` aux bornes.
   ⚠️ **Ventiler par adversaire** — contre Station et Over-folder la meilleure
   réponse *est* pure, y être n'est pas un biais. Le signal est contre GTO, où
   l'équilibre exige du mixte : `J1/C0/ouverture` (attendu 1/3) est aux bornes dans
   **58 %** des séries.
3. **Codage manuel** sur échantillon stratifié (150 à 200 décisions suffisent),
   selon les cinq catégories GTBENCH, pour estimer le taux de faux négatifs de la
   mesure automatique. Un cas est déjà documenté : l'inversion des rôles dans une
   note AE, avec stratégie jouée pourtant correcte.

## ⚠️ Points ouverts

| Point | Porteur | Impact |
|---|---|---|
| Papier Loriente & Diez à transmettre | Léo | Aucun sur les résultats ; manque un recoupement citable |
| GTO non joué en condition ICL | — | Arbitrage assumé (§2.2.7) ; la vérification qu'ICL ne bat pas l'équilibre contre l'équilibre n'a pas été faite |
| Profil d'oubli d'ICL jamais observé | — | La fenêtre n'a pas produit de décrochage à cet horizon ; demanderait un autre protocole, pas plus du même |

Le Mac M2 n'est plus un point ouvert : la campagne a tourné sur une seule machine,
ce qui supprime aussi le test d'effet-machine (sans objet).

## Journal des sessions

| Date | Fait |
|---|---|
| 2026-08-19 | Cadrage, audit d'environnement, oracle analytique, D1–D8, PRD 00–04. |
| 2026-08-19 | Moteur de jeu implémenté et testé ; constante GTO 2/3 confirmée par l'oracle. |
| 2026-08-21 | Harnais mémoire et journal ; clés de config relevées dans le code d'Hermes et vérifiées par canari réel. |
| 2026-08-21 | Arbitre et orchestration ; le build est complet de la graine au CSV. |
| 2026-08-21 | Pilote de calibrage sur `gpt-5.6-luna`. Deux failles de contamination trouvées et corrigées (pièges n°7 et n°8). |
| 2026-08-22 | **Audit adversarial** : quatre constats, tous à la frontière avec l'outillage tiers. Correctifs et tests de non-régression. |
| 2026-08-22 | **Tranche SM + AE** : 18 exécutions. H1 et H2 établies. |
| 2026-08-23 | Piège n°11 (jetons à usage unique) trouvé et corrigé avant qu'il ne casse la tranche ICL. |
| 2026-08-24 | **Tranche ICL** : 6 exécutions. H3 établie, sous condition. Collecte close. |
| 2026-08-25 | Documents mis à jour ; chapitre de méthode en version définitive. |
