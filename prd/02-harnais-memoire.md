# PRD 2 — Harnais mémoire : trois conditions, un seul canal variable

Version 1.0 — 2026-08-19. Dépend de : rien (validable seul au pilote). Bloque : PRD 3.

## 1. Objectif et principe

Fournir la couche qui transforme « une décision de jeu à prendre » en « un appel LLM correctement conditionné par la mémoire de la condition en cours », en garantissant que **la seule différence entre les trois conditions est le contenu du slot mémoire** — même modèle, même harnais, même prompt de règles, même format de réponse, même parsing (décision D1 : sinon confond harnais × mémoire, en violation du principe directeur de la spec §0).

Interface unique exposée à l'arbitre (PRD 3) :

```python
decider(infoset_obfusque, etat_main) → (action, sortie_brute, metadonnees)
ouvrir_session(s) / fermer_session(s, recap)   # gestion du slot mémoire à la frontière
```

## 2. Modèle unique

- Un seul modèle du catalogue Nous Portal, **identique pour les 3 conditions, tous les runs, toutes les machines**, paramètres d'inférence figés et logués à chaque appel (modèle, version, température, max_tokens).
- Shortlist pour le pilote de calibrage (critères : coût/manche, taux de parsing valide, latence) : `tencent/hy3:free` (plancher gratuit — utile pour déboguer le harnais sans brûler le budget), un « flash » économique (ex. `google/gemini-3.6-flash` ou `deepseek/deepseek-v4-flash`), et un candidat à raisonnement léger si le budget le permet. **Le débogage se fait sur le modèle gratuit ; la campagne sur le modèle élu — jamais de mélange dans un même run.**
- Température : celle par défaut du modèle, figée et loguée. On ne force pas T=0 : les stratégies mixtes (bluff à fréquence) exigent de la stochasticité ; c'est un choix expérimental, pas un détail technique.

## 3. Harnais commun : `hermes -z`, outils coupés

Chaque décision de jeu = **une invocation `hermes -z "<prompt>"`** (un prompt en entrée, la réponse finale seule sur stdout), exécutée avec :

- `HERMES_HOME` pointant sur le **store isolé du run** (§6) ;
- **tous les outils désactivés** (terminal, web, browser, session_search, skills) via la config du store : la manche est un pur échange texte, l'agent ne doit rien pouvoir consulter ni exécuter ;
- revue d'auto-amélioration d'arrière-plan **désactivée** ; `USER.md` désactivé ; providers de mémoire externes désactivés — `MEMORY.md` est l'**unique** canal persistant (spec §6) ;
- timeout + 2 relances sur échec réseau ; échec persistant = manche marquée `erreur_harnais` et rejouée avec la même donne (jamais silencieusement sautée).

La liste exacte des clés de config à poser (tools, memory, auxiliary.background_review, user_profile) sera arrêtée à l'implémentation contre la doc du dépôt `hermes-agent` local et **vérifiée par le canari du §6** — pas supposée.

## 4. Structure du prompt de manche (identique pour les 3 conditions)

```
[RÈGLES]        texte canonique obfusqué de « L'Épreuve des Trois Sceaux »
                (versionné, haché — même texte partout, toujours)
[SLOT MÉMOIRE]  ← la seule partie qui varie selon la condition (§5)
[MAIN COURANTE] position (premier/second à parler), jeton reçu,
                historique de la main en vocabulaire obfusqué
[TÂCHE]         « Réponds par exactement une action parmi : … »
                + format de sortie imposé : dernière ligne = ACTION: <terme>
```

- **Parsing** : extraction stricte de la dernière ligne `ACTION:` ; à défaut, recherche du dernier terme d'action valide dans la sortie. Sortie inexploitable → 1 relance avec rappel de format ; nouvel échec → action par défaut **passive** (*retenir* / *se retirer*), drapeau `action_par_defaut` logué. Le taux de défauts par session est un critère de qualité du pilote (< 2 %, sinon changer de modèle ou de format).
- Le texte libre avant `ACTION:` est conservé intégralement dans les logs (raisonnement libre, spec §9) — c'est la matière du détecteur de dé-obfuscation (PRD 4).
- Pas d'inter-manche : chaque invocation est un contexte neuf (spec §6) ; l'historique de la main courante seule est inclus (une main = 1 à 2 décisions max).

## 5. Les trois conditions = trois contenus du slot

| Condition | Slot mémoire dans le prompt | Frontière de session |
|---|---|---|
| **SM** (sans mémoire) | vide (section absente) | rien |
| **ICL** (historique brut) | `[HISTORIQUE DES SESSIONS PRÉCÉDENTES]` : récaps bruts des sessions passées, fenêtrés | l'arbitre ajoute le récap de la session close à la fenêtre ; **aucune étape LLM** |
| **AE** (auto-écrit) | `[VOS NOTES]` : contenu du snapshot MEMORY.md gelé `M_s` | étape de réflexion : Hermès reçoit le récap et écrit/élègue son MEMORY.md → `M_{s+1}` |

### 5.1 ICL — fenêtrage

Récap par session = mains résumées ligne par ligne en vocabulaire obfusqué (`main 37 : second à parler, jeton Vael, adversaire engage, vous couvrez, adversaire montre Rhun, −2`) + solde de session. Fenêtre : **6 000 tokens**, sessions entières les plus récentes (jamais de session tronquée en milieu — le « dents de scie » attendu vient précisément de l'éviction des sessions anciennes). Contenu figé intra-session. **Le même récap** sert de matière à la réflexion AE (décision D8 : les deux conditions à mémoire voient la même information, seul le mécanisme de rétention diffère).

### 5.2 AE — réflexion à la frontière et gel intra-session

Fermeture de session AE : une invocation `hermes -z` **avec outils mémoire actifs cette fois**, prompt = récap de session + consigne de réflexion (style Reflexion : qu'est-ce qui a marché, qu'écrire/élaguer dans tes notes pour mieux jouer la prochaine fois) ; Hermès écrit son MEMORY.md via son outil natif (cap ~2 200 caractères, erreur en cas de dépassement, auto-élagage — comportement natif conforme spec §6). L'arbitre capture ensuite le fichier = snapshot `M_{s+1}`.

**Gel intra-session — imposé par l'arbitre, pas supposé** (décision D2) : Hermes persiste les écritures mémoire sur disque immédiatement ; or une session d'arène = K invocations successives. Donc : snapshot fichiers du store à l'ouverture de session ; **restauration du snapshot avant chaque manche** ; toute écriture intra-session est ainsi jetée — mais détectée (diff après la manche) et loguée `ecriture_intra_session` (observable : l'agent tente-t-il d'écrire pendant qu'il joue ?). Écriture réelle uniquement à l'étape de réflexion.

Événements MEMORY.md à loguer par frontière (spec §6/§9) : contenu avant/après, entrées ajoutées/supprimées/modifiées, tentatives d'overflow, élagage.

### 5.3 Équité inter-conditions

SM et ICL utilisent le même `hermes -z` avec mémoire native **désactivée** (slot rempli par l'arbitre dans le prompt pour ICL, vide pour SM). Ainsi les trois conditions traversent strictement le même code, le même prompt système Hermes, le même modèle — l'ablation est propre.

## 6. Isolation par run (spec §7 — piège silencieux)

- Un répertoire `HERMES_HOME` **par run**, créé par clonage d'un template de config vierge (config figée §3, auth copiée), sous `C:\arene-runs\<run_id>\hermes-home\` (hors OneDrive, décision D7).
- **Canari d'isolation, exécuté au démarrage de chaque run** : écrire un marqueur unique dans le MEMORY.md du store du run via une invocation de test, vérifier (a) qu'il est présent dans le store du run, (b) qu'il est **absent** du `HERMES_HOME` global de la machine et de tout autre store de run actif. Échec canari = run refusé. On ne *suppose* jamais l'isolation (spec §7), on la teste.
- Runs parallèles sur une même machine autorisés uniquement si leurs `HERMES_HOME` sont distincts et les canaris passés ; `state.db` (session_search) est isolé par construction puisqu'il vit sous `HERMES_HOME`.

## 7. Ce que ce PRD ne couvre pas

Boucle de session, alternance des positions, séquence de donnes, récaps (génération) : PRD 3. Schémas de logs : PRD 4. Choix final du modèle : pilote de calibrage (PRD 3 §7).

## 8. Critères d'acceptation

1. **Test d'équité** : à slot identique, les prompts des 3 conditions sont octet-pour-octet identiques hors slot ; le hash du texte de règles est identique dans tous les logs de tous les runs.
2. **Canari d'isolation** passe sur 2 runs simultanés sur le Victus ; les MEMORY.md ne se contaminent pas.
3. **Test de gel** : sur une session de test, modification manuelle du MEMORY.md en cours de session → la manche suivante voit toujours `M_s` ; le diff est logué.
4. **Parsing** : ≥ 98 % d'actions valides sans défaut sur le pilote, sinon itération sur le format avant campagne.
5. SM ne montre aucune trace des mains passées (vérifiable dans les prompts logués) ; ICL n'évolue jamais intra-session ; AE ne voit jamais le récap brut pendant les manches (seulement ses notes).
