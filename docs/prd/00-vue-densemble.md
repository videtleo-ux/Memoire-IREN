# PRD 0 — Vue d'ensemble de l'arène

Version 1.0 — 2026-08-19. Document chapeau : architecture, décisions transverses figées, paramètres, et carte des quatre PRD. La spec source (`spec-build-arene-kuhn(1).md`) reste l'autorité sur le *quoi* ; les PRD définissent le *comment*.

## 1. Architecture d'ensemble

```
                        ┌───────────────────────────────────────────┐
                        │  ARBITRE (Python, local, par run)  [PRD 3] │
                        │  boucle sessions → manches → décisions     │
                        └──────┬──────────────┬──────────────┬───────┘
                               │              │              │
              ┌────────────────▼───┐   ┌──────▼──────┐   ┌───▼──────────────┐
              │ MOTEUR DE JEU      │   │ HARNAIS      │   │ LOGGING          │
              │ [PRD 1]            │   │ MÉMOIRE      │   │ [PRD 4]          │
              │ règles obfusquées, │   │ [PRD 2]      │   │ turns.jsonl      │
              │ bots, GTO,         │   │ hermes -z ×3 │   │ sessions.jsonl   │
              │ meilleure réponse, │   │ conditions,  │   │ CSV dérivé,      │
              │ écart exact        │   │ gel mémoire, │   │ détecteur de     │
              │ (aucun LLM)        │   │ isolation    │   │ dé-obfuscation   │
              └────────────────────┘   └──────┬───────┘   └──────────────────┘
                                              │ hermes -z (HERMES_HOME dédié/run)
                                       ┌──────▼───────┐
                                       │ Nous Portal   │  ← un seul modèle,
                                       │ (API hébergée)│    identique partout
                                       └──────────────┘
```

Aucune inférence locale : les deux machines (Mac M2 8 Go, Victus RTX 3050) ne font tourner que l'arbitre Python et des appels réseau. vLLM est abandonné — l'API hébergée joue le rôle d'« endpoint unique » de la spec (§5) avec une garantie d'homogénéité inter-machines supérieure à deux stacks d'inférence locales hétérogènes.

## 2. Décisions transverses figées

| # | Décision | Justification |
|---|---|---|
| D1 | **Harnais unique : `hermes -z` pour les 3 conditions**, outils désactivés pendant les manches. | Sinon confond harnais × mémoire : le prompt système et l'échafaudage d'Hermes différeraient entre conditions. Seul le slot mémoire varie — principe directeur de la spec (§0). |
| D2 | **Gel intra-session imposé par l'arbitre au niveau fichiers** : snapshot du store mémoire à l'ouverture de session, restauration avant *chaque* manche, écriture autorisée uniquement à la réflexion frontière. | Hermes persiste les écritures mémoire sur disque immédiatement et une revue d'arrière-plan peut écrire après chaque tour — sans ce verrou, le gel intra-session (§6 spec) serait silencieusement violé à chaque main. |
| D3 | **Isolation par run via `HERMES_HOME` dédié** (un clone de home par run), vérifiée par canari au démarrage. | §7 spec (piège silencieux). `HERMES_HOME` est la variable officielle, déjà en usage sur l'install Windows. Isole aussi `state.db` (session_search) par construction. |
| D4 | **Modèle unique figé au pilote** parmi une shortlist de modèles « flash » du catalogue Nous Portal, paramètres d'inférence fixes et logués. | Budget « quelques dizaines d'euros » ; le modèle est la constante, la mémoire la variable (§5 spec). |
| D5 | **Lexique obfusqué** : jeu « L'Épreuve des Trois Sceaux », jetons Tor ≺ Vael ≺ Rhun, actions *retenir / engager / couvrir / se retirer*. Un seul texte de règles, versionné et haché dans les logs. | §1.bis spec ; choix validé par le pilote humain (Léo). |
| D6 | **Constantes GTO auto-vérifiées** : le test `exploitabilité(GTO) = 0` tranche la valeur contestée (couverture de J1 avec Vael = α + 1/3 = **2/3** à α = 1/3, et non 1/3 comme écrit en §2 de la spec — le 1/3 correspond au cas α = 0). | Dérivation analytique refaite intégralement (PRD 1 §4) ; recoupement avec Loriente & Diez dès transmission du papier, mais le test est l'arbitre. |
| D7 | **Données de runs hors OneDrive** (`C:\arene-runs` / `~/arene-runs`), synchronisation vers le dépôt Git par commits aux frontières de session. | Des centaines d'écritures fichiers + clones de HERMES_HOME sous synchronisation OneDrive = verrous et conflits garantis. |
| D8 | **Même format de récap de session** servi à la réflexion (condition auto-écrite) et injecté dans la fenêtre ICL. | Comparabilité : les deux conditions à mémoire voient la même matière première, seul le mécanisme de rétention diffère. |

## 3. Paramètres figés (réponses pilote du 2026-08-19)

| Paramètre | Valeur | Source |
|---|---|---|
| K (manches/session), point de départ pilote | **200** | choix pilote |
| Réplications N par cellule | **3** | choix pilote |
| Budget API | quelques dizaines d'euros | choix pilote |
| Conditions mémoire | SM (sans mémoire), ICL (historique brut), AE (auto-écrit Hermes) | spec §5 |
| Bots adversaires | GTO, Station, Over-folder | spec §3 |
| Sessions par run | SM : 3 (plancher plat) ; ICL/AE : plateau automatisé, min 8, max 20 | spec §5 + PRD 3 |
| Fenêtre ICL | 6 000 tokens de récaps, sessions entières les plus récentes | PRD 2 §4 |
| Critère de plateau | automatisé (PRD 3 §6) | choix pilote |
| Hors périmètre | bras transfert, bras humain, adversaire LLM figé | choix pilote (spec §11) |

Matrice expérimentale : 3 conditions × 3 bots × N=3 = **27 runs** (dont 9 runs SM courts).

## 4. Carte des PRD et dépendances

| PRD | Contenu | Dépend de | Bloque |
|---|---|---|---|
| [01 — Moteur de jeu](01-moteur-de-jeu.md) | règles, bots, GTO, meilleure réponse, écart exact, oracle de tests | rien | PRD 3 |
| [02 — Harnais mémoire](02-harnais-memoire.md) | 3 conditions via hermes -z, gel, isolation, prompts, parsing | rien (validable au pilote) | PRD 3 |
| [03 — Arbitre & orchestration](03-arbitre-orchestration.md) | boucle de session, donnes communes, plateau, pilote de calibrage, coûts | PRD 1, 2 | PRD 4 (schémas consommés) |
| [04 — Logging & analyse](04-logging-analyse.md) | schémas JSONL, CSV dérivé, Git, détecteur dé-obfuscation, courbes | PRD 3 | mémoire écrit |

Ordre de build : **PRD 1 d'abord** (aucun coût API, tout le reste s'appuie sur sa mesure), PRD 2 et 4 en parallèle, PRD 3 en intégration, puis pilote de calibrage, puis campagne.

## 5. Points ouverts

| Point | Porteur | Échéance |
|---|---|---|
| Transmission du papier Loriente & Diez (recoupement D6) | Léo | avant rédaction du mémoire (non bloquant pour le build, cf. D6) |
| Installation d'Hermes Agent sur le Mac M2 (seul le Victus est vérifié fonctionnel) | Léo | avant la campagne multi-machines |
| Choix du modèle définitif (shortlist PRD 2 §2) | pilote de calibrage | fin du pilote |
