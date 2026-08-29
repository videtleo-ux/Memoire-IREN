# PRD 3 — Arbitre & orchestration

Version 1.0 — 2026-08-19. Dépend de : PRD 1 (mesure), PRD 2 (harnais). Produit les événements consommés par PRD 4.

## 1. Objets et vocabulaire

- **Run** = S sessions séquentielles × (1 condition, 1 bot, 1 réplication). Unité parallélisable, insécable entre machines (`M_s` dépend de `M_{s-1}`, spec §8). Identifiant : `run_id = {condition}-{bot}-r{réplication}` (ex. `AE-station-r2`).
- **Session** = K manches sous mémoire gelée `M_s`, close par une frontière (récap → mise à jour du slot).
- **Manche** = 1 donne, 1 à 2 décisions agent, résultat en jetons.
- **Campagne** = matrice 3 conditions × 3 bots × N=3 = **27 runs** (9 SM courts + 18 longs).

## 2. Boucle de l'arbitre (un run)

```
préparer_run:      créer C:\arene-runs\<run_id>\ ; cloner HERMES_HOME template ;
                   canari d'isolation (PRD 2 §6) ; M_0 = vide ; état_run.json
pour s = 0..S-1:
  ouvrir_session:  charger snapshot M_s (AE : fichiers ; ICL : fenêtre de récaps ; SM : rien)
  pour k = 1..K:
    donne         ← flux_donnes(réplication, s, k)      # commun aux 3 conditions
    position      ← J1 si k impair sinon J2             # alternance stricte 50/50
    restaurer M_s (AE — gel fichiers, PRD 2 §5.2)
    jouer la manche : à chaque décision agent → harnais.decider(...) ;
                      à chaque décision bot → politique du bot (GTO : flux_bot(r,s,k)) ;
                      moteur (PRD 1) valide la légalité et règle le résultat
    loguer le tour (PRD 4)
  fermer_session:  générer le récap canonique (§5) ; frontière selon condition (PRD 2 §5) ;
                   capturer M_{s+1} ; estimer π̂(M_s) (§6.1) ; calculer Écart(s),
                   référence récité, EV réalisée ; loguer la session (PRD 4)
  si condition ≠ SM et plateau(Écarts) (§6.2): arrêter le run
clore_run:         vérifications d'intégrité (§8) ; commit Git des logs (PRD 4)
```

Resets aux trois échelles (spec §6) : entre runs = tout est neuf (store, M_0, état) ; entre sessions d'un run = **aucun** reset ; intra-session = contexte neuf par manche + M_s gelé.

## 3. Nombre de sessions

- **SM** : S = 3 fixes (il n'y a rien à accumuler ; 3 points suffisent à établir le plancher plat et sa variance).
- **ICL / AE** : arrêt au plateau (§6.2), bornes **min 8, max 20** sessions. Le max borne le coût ; le min garantit assez de points pour distinguer escalier / dents de scie / plat même si le plateau est atteint vite.

## 4. Aléa contrôlé (nombres aléatoires communs, spec §8)

Trois flux dérivés indépendamment d'une **graine maîtresse de campagne** (figée, loguée) via `(graine, étiquette, réplication, session, manche)` :

| Flux | Sert à | Partagé entre |
|---|---|---|
| `flux_donnes` | permutation des 3 jetons (carte agent, carte bot, carte écartée) | **les 3 conditions** à (r, s, k) égal — cœur de la réduction de variance ; également commun aux 3 bots (les mêmes mains, seule la politique adverse change) |
| `flux_bot` | tirages du bot GTO (bluffs, calls mixtes) | les 3 conditions à (r, s, k) égal — sinon le « même deal » divergerait dès le premier tirage adverse |
| `flux_divers` | tout le reste (ordres d'exécution, échantillonnages d'analyse) | rien |

L'alternance de position est déterministe (k impair/pair), donc identique partout par construction. Chaque réplication r a des donnes différentes (r entre dans la dérivation), mais le **triplet de conditions d'une même réplication est apparié** — les comparaisons inter-conditions se font à donnes strictement identiques.

## 5. Récap de session (canonique, unique)

Généré par l'arbitre en vocabulaire obfusqué, une ligne par manche : position, jeton reçu, séquence d'actions, jeton adverse **si abattage** (sinon « non révélé » — ne jamais fuiter une carte non montrée), gain/perte ; en pied : solde de session, nombre de manches. Ce texte **unique** sert à la fois de matière à la réflexion AE et d'unité d'accumulation ICL (décision D8). Il ne contient ni conseil, ni statistique agrégée par info-set, ni interprétation — distiller la fuite du bot est **le travail de l'agent**, pas celui de l'arbitre (spec §6 : « apprenable » = l'agent doit distiller lui-même).

## 6. Mesure

### 6.1 Estimation de π̂(M_s)

Fréquences brutes par info-set sur les K manches de la session (actions parsées, y compris relances réussies ; les manches `action_par_defaut` sont **exclues** du comptage et comptées à part). Info-sets non observés → convention GTO + drapeau (PRD 1 §6.3). Sortie : politique 12 entrées + effectifs par info-set (les effectifs partent dans les logs — ils donnent les barres d'erreur).

### 6.2 Critère de plateau (automatisé — choix pilote)

Sur la suite `Écart(0..s)` : plateau déclaré si, avec au moins 8 sessions, la **pente de la régression linéaire sur les 4 dernières sessions** est ≥ −ε avec ε = **0,02 jeton/manche/session** (l'écart ne décroît plus significativement), **et** l'écart-type de ces 4 valeurs est < 0,05. Arrêt au plateau + **2 sessions de marge** (spec §6 : « plateau + marge »), ou à S = 20. Constantes revalidées au pilote de calibrage sur les courbes réelles ; valeurs et décision loguées à chaque évaluation.

## 7. Pilote de calibrage (avant campagne — spec §10)

Périmètre : **1 run court par condition** (4 sessions, K = 200) contre Station, sur le Victus, pour chaque modèle candidat de la shortlist (PRD 2 §2) — en commençant par le gratuit pour valider la mécanique à coût nul.

Sorties attendues, dans l'ordre de véto :
1. **Taux de parsing** ≥ 98 % (sinon modèle/format rejeté) ;
2. **Coût mesuré par manche** (tokens in/out réels) par condition → projection du coût de campagne (§9) ; go/no-go budget ;
3. **Stabilité de π̂ à K = 200** : bootstrap sur les manches de session (π̂ à K=100 vs 150 vs 200) — si l'écart d'exploitation bouge de < 0,05 entre K=150 et 200, K=150 suffit et on économise 25 % ;
4. Latence/manche → durée projetée de la campagne par machine ;
5. Constantes du plateau (§6.2) confrontées aux premières courbes.

Le choix de modèle et les paramètres élus sont figés dans `CONTEXT.md` et `PROGRESS.md` à la clôture du pilote.

## 8. Machines, affectation, intégrité

- **Affectation run→machine randomisée et loguée** (spec §8) entre Victus et Mac M2 — *si* Hermes est opérationnel sur le Mac (point ouvert) ; sinon campagne mono-machine sur le Victus, l'effet-machine disparaissant du même coup. Le modèle étant servi par API, l'homogénéité d'inférence inter-machines est garantie par construction ; on logue quand même `machine` par run pour le test a posteriori.
- **Reprise sur incident** : logs append-only + `état_run.json` (dernière session close, position dans les flux) → un run interrompu reprend à la frontière de session suivante, jamais en milieu de session (une session entamée puis interrompue est rejouée entièrement, ses logs partiels marqués `abandonnée`).
- **Vérifications d'intégrité à la clôture de run** : mêmes donnes que les runs appariés (hash de la séquence), équilibre exact des positions, canari d'isolation toujours intact, complétude des logs (K manches × S sessions), hash du texte de règles constant.

## 9. Enveloppe de coût (à confirmer au pilote)

Estimation grossière (~800 tokens de prompt hors slot, ~150 de sortie, 1 décision/manche vs bots déterministes, ≤ 2 vs GTO ; fenêtre ICL jusqu'à 6 000 tokens **en plus** par manche) : les 27 runs ≈ 60–80 k appels ; l'ICL domine le coût (son slot multiplie les tokens d'entrée par ~8). Ordre de grandeur total sur un modèle « flash » : **20–50 €** — dans le budget mais sans marge de refonte ; d'où l'ordre impératif : moteur (gratuit) → pilote sur modèle gratuit → pilote payant court → campagne. Levier si dépassement projeté : fenêtre ICL à 4 000 tokens, K à 150 (si §7.3 le permet), max sessions à 16.

## 10. Critères d'acceptation

1. **Mini-run de bout en bout** (1 session, K = 20, Station, SM, modèle gratuit) produit des logs complets et un Écart calculable — premier jalon d'intégration.
2. **Test d'appariement** : deux exécutions du même (r, s) sous deux conditions différentes reçoivent des donnes octet-pour-octet identiques ; le bot GTO y fait les mêmes tirages.
3. **Test de reprise** : kill -9 en milieu de session → la reprise rejoue la session proprement, aucune donne sautée ni dupliquée sur l'ensemble du run.
4. Positions exactement équilibrées (K pair ⇒ K/2 par position) dans tous les logs de session.
5. Le récap ne contient jamais une carte adverse non montrée (test sur mains avec retrait).
