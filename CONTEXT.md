# CONTEXT.md — Contexte vivant du projet

Dernière mise à jour : 2026-08-21. Ce fichier capture tout ce qui n'est **pas** dans la spec ni dans les PRD : les décisions prises en discussion avec le pilote, les découvertes d'environnement, et les contraintes réelles. À relire en début de toute session de travail, avec `spec-build-arene-kuhn(1).md` et `prd/00-vue-densemble.md`.

## 1. Le projet en une phrase

Arène expérimentale pour un mémoire de M2 (IREN) : faire jouer un agent LLM à un Kuhn poker obfusqué contre des bots à politique fixe, sous 3 conditions mémoire, et mesurer l'adaptation par un écart d'exploitation exact par session — toute adaptation observée doit être attribuable à la **mémoire**, pas au harnais.

## 2. Cadre et contraintes du pilote (Léo, seul sur le projet)

- **Livrables** : système qui tourne + résultats analysés + mémoire écrit + accès au code + soutenance. **Échéance : quelques semaines** (rentrée 2026). Directeur non impliqué dans les décisions techniques.
- **Budget API : quelques dizaines d'euros.** N = 3 réplications/cellule, K = 200 manches/session au départ (pilote de calibrage prévu pour ajuster).
- **Machines** : Victus Windows 11 (i5-12e gén, RTX 3050 4 Go, 16 Go RAM) — machine principale, Hermes Agent installé et authentifié ; Mac M2 8 Go — Hermes **pas encore installé** (point ouvert).
- **Stack** : Python 3.11 (installé sur le Victus). Analyse finale Python et/ou R. Logs JSONL (source de vérité) + CSV dérivé, centralisés via Git.
- **Hors périmètre confirmé** : bras transfert, bras humain, adversaire LLM figé (§11 spec). Pas de contraintes éthiques/confidentialité sur le build primaire.
- Le papier **Loriente & Diez** est en possession de Léo, pas encore transmis — non bloquant (cf. décision D6).

## 3. Découvertes d'environnement (vérifiées sur machine, 2026-08-19)

**« Hermès » = Hermes Agent, le CLI d'agent de Nous Research** — pas des poids de modèle. Install fonctionnelle sous `C:\Users\videt\AppData\Local\hermes` (`HERMES_HOME` défini), OAuth Nous Portal actif, dépôt source du CLI cloné dans `hermes-agent/` (docs complètes sous `website/docs/`). Conséquences :

- **Pas de vLLM, pas d'inférence locale.** Le modèle est servi par l'API Nous Portal (catalogue : Claude, GPT, Gemini, DeepSeek, Qwen, GLM, `tencent/hy3:free`, etc. — aucun modèle nommé « Hermes » au catalogue). Les deux PC ne portent que l'arbitre Python.
- **Mécanisme mémoire natif conforme à la spec** : `MEMORY.md` (~2 200 caractères ≈ 8–15 entrées, erreur en cas de dépassement, pas de compaction auto, auto-élagage par l'agent), snapshot injecté au prompt système en début d'invocation. La spec §5–§7 décrit ce mécanisme quasi mot pour mot.
- **⚠️ Piège n°1 — persistance immédiate** : Hermes écrit la mémoire **sur disque immédiatement** (seul le prompt système est figé par invocation), et une revue d'auto-amélioration en arrière-plan peut écrire après chaque tour. Le « gel intra-session » doit donc être imposé par l'arbitre au niveau fichiers (snapshot/restauration — décision D2).
- **⚠️ Piège n°2 — canaux mémoire annexes** : session_search (FTS5 sur `state.db`), skills auto-créées, providers externes (Honcho, Mem0…), USER.md. Tous doivent être neutralisés/isolés pour que `MEMORY.md` soit l'unique canal d'apprentissage (config + isolation par `HERMES_HOME` dédié par run).
- **Interface scriptable** : `hermes -z "<prompt>"` — prompt en entrée, réponse finale seule sur stdout. C'est l'interface arbitre → agent pour les 3 conditions (décision D1 : harnais unique pour éviter le confond harnais × mémoire).
- **⚠️ Piège n°3 — OneDrive** : le dépôt vit sous OneDrive ; les données de runs (écritures haute fréquence + clones de HERMES_HOME) iront hors OneDrive (`C:\arene-runs`), synchronisées vers Git aux frontières de session (décision D7).

## 4. Décisions de design prises en discussion (au-delà de la spec)

Voir le tableau complet D1–D8 dans `prd/00-vue-densemble.md` §2. Les plus structurantes :

1. **Harnais unique `hermes -z` pour les 3 conditions**, outils désactivés — seul le slot mémoire varie.
2. **Gel intra-session par snapshot/restauration fichiers** orchestré par l'arbitre.
3. **Constante GTO contestée tranchée par le maths + test** : couverture J1-Vael face à une mise = **2/3** à α = 1/3 (la spec §2 dit 1/3, qui correspond au cas α = 0 ; le test `exploitabilité(GTO) = 0` échoue avec 1/3 et passe avec 2/3 — le moteur s'auto-vérifie).
4. **Lexique obfusqué figé** : « L'Épreuve des Trois Sceaux », Tor ≺ Vael ≺ Rhun, actions *retenir / engager / couvrir / se retirer* (validé par Léo).
5. **Oracle analytique du moteur** (dérivé à la main, à reproduire exactement par le code) : valeur du jeu −1/18 ; meilleure réponse +1/3/manche vs Station, +1/manche vs Over-folder ; écart d'un réciteur GTO = 1/9 vs Station, 7/9 vs Over-folder. Contre Station/Over-folder, seuls 6 info-sets sont atteignables et il y a exactement 1 décision LLM par manche.
6. **Règles rappelées dans le prompt de réflexion AE** (validé par Léo le 2026-08-21). Le PRD 2 §5.2 écrit « prompt = récap + consigne » ; on y ajoute le texte des règles. Coût : ~300 tokens une fois par série, négligeable devant K = 200 manches. Gain : l'agent ne rédige pas ses notes hors du référentiel du jeu. Réversible d'une constante — `harnais.gabarits.INCLURE_REGLES_DANS_REFLEXION`. **À figer avant la campagne** : basculer cette constante en cours de route rendrait les runs non comparables.
7. **Clé d'info-set dans les logs = celle du moteur**, `"J1/C1/face_mise"` (validé par Léo le 2026-08-21), et non le `"J1-haut-face-mise"` de l'exemple du PRD 4 §2 : « haut » est exactement le label ordinal que l'obfuscation proscrit (PRD 1 §2), et une seconde énumération des info-sets contredirait la source unique du PRD 1 §9. Le numéro 1–12 part en plus dans le champ `infoset_numero`.

## 4 bis. Constats machine du 2026-08-21 (implémentation du harnais, PRD 2)

Le PRD 2 §3 exigeait d'arrêter les clés de config **contre le code d'Hermes**, pas de les supposer. Fait, puis vérifié par un canari réel sur store jetable (modèle gratuit, deux appels) :

- **Clés relevées dans le code** (`agent/agent_init.py`, `agent/turn_context.py`) : `memory.memory_enabled`, `memory.user_profile_enabled`, `memory.nudge_interval` (0 = plus aucune revue d'auto-amélioration d'arrière-plan), `skills.creation_nudge_interval`. Toutes posées par `harnais.stores.config_arene`.
- **Toolset « zéro outil » = `context_engine`** : vérifié, `get_tool_definitions(enabled_toolsets=["context_engine"])` rend une liste vide, et `["memory"]` rend exactement `memory`. Ce n'est pas un bricolage : `hermes -z` **refuse** une liste de toolsets vide ou inconnue, il fallait un nom légitime et creux.
- **`MEMORY.md` = `$HERMES_HOME/memories/MEMORY.md`**, entrées séparées par `"\n§\n"` — le diff d'entrées de la frontière est donc exact, pas heuristique.
- **`hermes -z --usage-file`** écrit un rapport JSON par appel (tokens entrée/sortie, modèle réellement servi, coût estimé), y compris en cas d'échec : c'est la source des champs `tokens` des logs et du suivi de budget.
- **⚠️ Piège n°4 — l'agent ne sait pas s'introspecter** : interrogé sur le nombre d'outils dont il dispose alors qu'il n'en a aucun, le modèle gratuit répond « 5 ». Le canari ne vérifie donc plus une *réponse* mais un *fichier* : même consigne d'écriture jouée en configuration de manche, `MEMORY.md` ne doit pas bouger d'un octet.
- **⚠️ Piège n°5 — pseudo-appels d'outils** : privé d'outils, `tencent/hy3:free` a émis un `<tool_call:…>terminal…` **en clair dans sa réponse** au lieu de répondre. Inerte (aucun outil n'existe), mais la sortie est inexploitable et coûte une relance. Drapeau `sortie_pseudo_outil` posé dans les logs ; à surveiller au pilote de calibrage, où le taux de parsing ≥ 98 % est un critère de véto.

## 4 ter. Choix d'implémentation de l'arbitre (PRD 3, 2026-08-21)

Quatre décisions prises à l'implémentation, qui ne sont pas dans le PRD et qu'il ne faut pas défaire sans lire ce qui suit. Aucune découverte machine nouvelle : l'arbitre ne fait aucune hypothèse sur Hermes que le PRD 2 n'ait déjà vérifiée.

1. **Les donnes sont dérivées, pas tirées.** `donne(graine, r, s, k)` est une fonction pure : SHA-256 des coordonnées, modulo les 6 attributions possibles. Aucun état de générateur ne circule d'une manche à l'autre, donc **aucune dérive possible** entre conditions — deux runs au même (r, s, k) voient les mêmes sceaux même si l'un a joué mille manches de plus. C'est le critère d'acceptation §10.2, celui qu'aucun log ne rattrape après coup. Le flux du bot, lui, reste un `random.Random` (le moteur attend cette interface) mais **seedé par manche** : une divergence de jeu reste confinée à la manche où elle se produit.
2. **La manche est atomique.** Les tours d'une manche ne sont écrits dans `turns.jsonl` qu'une fois la manche terminée. Sans ça, un échec de harnais sur la 2ᵉ décision laisserait une demi-manche orpheline, et le rejeu de complétude (PRD 4 §7.1) échouerait sur un run par ailleurs sain. Corollaire : une manche rejouée après `ErreurHarnais` l'est **avec la même donne et le même flux de bot**, donc à l'identique.
3. **Les tours d'une série interrompue sont déplacés, pas annotés.** `turns.jsonl` doit contenir une tentative et une seule par série, sinon `rejouer.py` regroupe deux tentatives sur la même clé (série, manche) et conclut à des donnes dupliquées. À la reprise, les tours de la tentative avortée partent donc dans `turns.abandonnes.jsonl`, marqués `abandonnee` + `tentative` — rien n'est perdu, le fichier canonique reste rejouable. C'est le seul moment de la vie d'un run où `turns.jsonl` n'est pas en pur ajout, et il est hors série.
4. **π̂ est estimée depuis les lignes de log déjà écrites**, via `journal.estimer_pi_hat`, et non d'un compteur tenu en parallèle. La règle d'exclusion des décisions `action_par_defaut` n'existe ainsi qu'à un seul endroit, et l'arbitre mesure exactement ce que le rejeu retrouvera.

S'y ajoute un **témoin d'isolation** (`<store>/temoin-isolation.txt`) posé au démarrage et vérifié à la clôture : le canari du PRD 2 §6 prouve l'isolation *au démarrage* mais efface son marqueur pour laisser `M_0` vide ; le témoin, lui, répond à « ce store est-il resté le sien du début à la fin ? ». Il vit hors du dossier `memories/`, donc le gel intra-série ne peut ni l'effacer ni le ressusciter.

## 4 quater. Mini-run de bout en bout (2026-08-21) — ce qu'il a tranché

Premier appel API réel du projet : 1 série, K = 20, Station, SM, `tencent/hy3:free`, 22 appels, coût nul. Intégrité verte, rejeu complet, 100 % de parsing, positions 10/10, canari et gel prouvés sur le binaire réel. Quatre constats qui changent le plan.

1. **⚠️ Piège n°6 — la console Windows est en cp1252.** Le run est tombé sur un `≤` non encodable **avant le premier appel API**. `arbitre.cli._console_tolerante()` dégrade désormais l'affichage au lieu du run ; les journaux restent en UTF-8, écrits par le journal.
2. **L'obfuscation ne tient pas.** Le modèle a nommé « Kuhn » et récité le profil GTO à la **3ᵉ manche, sans mémoire**. 14 manches sur 20 portent une mention du jeu source. Décision du pilote : **on n'en fait plus un pilier**, elle passe en limite du mémoire (bloc L.1 de `memoire/methodologie.md`), le lexique est conservé (le changer romprait la comparabilité), et la reconnaissance du jeu devient une **covariable mesurée**. L'identification repose sur l'asymétrie Station/Over-folder, et SM devient la mesure empirique du niveau récité.
3. **Le détecteur avait un trou et ne l'aura plus jamais.** Il laissait passer `check`, `bet`, `fold`, `main`, `ante` — les traductions spontanées du modèle vers le jeu source. Motifs ajoutés (45 → 70 hits sur le même run). Surtout : `journal.recompter` **rejoue le détecteur depuis les journaux**, qui conservent le texte intégral. Le détecteur n'est donc plus une décision à figer avant campagne ; il s'améliore après coup sans invalider une seule manche, et l'écart avec le compte figé se rapporte.
4. **L'enveloppe de coût du PRD 3 §9 est fausse d'un ordre de grandeur.** Mesuré : **1 296 tokens d'entrée / 3 580 de sortie par manche** (estimé : 800 / 150). L'entrée est 5× l'estimation (le prompt système d'Hermès s'ajoute au nôtre), la sortie 24× (chaînes de raisonnement). La latence de 62 s/manche n'est pas exploitable pour projeter la durée : c'est celle du palier gratuit.

### Catalogue Nous Portal et coûts (cache local du 2026-08-03)

| Modèle | Prix / 1M tokens | Campagne 12 séries |
|---|---|---|
| `tencent/hy3:free`, `poolside/laguna-s-2.1:free`, `inclusionai/ling-3.0-flash:free`, `stepfun/step-3.7-flash:free`, `poolside/laguna-xs-2.1:free` | **gratuit** | **0 $** |
| `openai/gpt-5.6-luna` | in 0,08 $ / out 0,48 $ | ~113 $ |
| `openai/gpt-5.6-terra` | in 0,80 $ / out 4,80 $ | ~1 130 $ |
| `openai/gpt-5.6-sol` | in 4,00 $ / out 24,00 $ | ~5 640 $ |

**Cinq modèles gratuits au catalogue, pas un seul.** La campagne complète est donc réalisable à coût nul ; la contrainte réelle devient le **temps**, pas l'argent. Le levier principal sur le coût comme sur la durée est l'effort de raisonnement (`--reasoning`, exposé au CLI depuis le 2026-08-21, `medium` par défaut) : il commande les tokens de sortie, qui représentent 60 % du volume et 90 % du prix chez les modèles payants.

## 4 quinquies. Pilote complet du 2026-08-21 (soirée) — sur `gpt-5.6-luna`

**⚠️ Piège n°7 — Hermes injectait `CLAUDE.md` du dépôt dans son prompt système.** La faille de validité la plus grave du projet. Hermes explore le répertoire courant à la recherche de consignes d'agent (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`) et les y verse. L'arène tournait depuis le dépôt : l'agent recevait à chaque manche un document qui nomme le jeu réel, donne la constante d'équilibre et **décrit l'exploitation de chaque bot**. Mesuré par `hermes prompt-size` : 11 633 octets, contre 0 depuis un répertoire vide. Corrigé — le sous-processus tourne dans `<store>/cwd-neutre`. **Conséquence rétroactive : les 45 drapeaux de dé-obfuscation du premier mini-run ne prouvaient rien, l'agent lisait le corrigé.** Après correctif : 0 drapeau de dé-obfuscation sur 200 sorties.

**⚠️ Piège n°8 — `hermes -z` rend les échecs de fournisseur sur stdout avec le code retour 0.** Un manque de crédits imprimait « API call failed… » que le harnais prenait pour une réponse du modèle. Sans détection, une campagne entière se remplit d'`action_par_defaut` loguées comme des données. Corrigé (`harnais.hermes.echec_fournisseur`).

**Le cache de préfixe ne mord jamais.** Trois appels au préfixe identique : 4 038 tokens écrits en cache, 0 lu, à chaque fois. Le levier « cache » est mort ; la fermeture de la fuite l'a remplacé avantageusement (entrée par appel : 4 041 → 1 626 tokens).

**L'effort de raisonnement ne change presque rien sur Luna** (200 manches, mêmes donnes) : `low` → sortie 445 tokens, écart 0,248 ; `medium` → 427 tokens, écart 0,227. Même coût, même latence, même durée. **Donc `medium` par défaut** : il retire l'objection « le modèle a été bridé » sans rien coûter. (Sur `tencent/hy3:free`, le paramètre était purement ignoré.)

**Résultats de mesure, `Station`, réplication 1 :**

| Condition | K | séries | écart par série |
|---|---|---|---|
| SM | 200 | 1 | 0,248 (`low`) · 0,227 (`medium`) |
| ICL | 20 | 3 | 0,333 → 0,278 → 0,190 |
| AE | 20 | 3 | 0,111 → **0,000** → **0,000** |

- **Pas d'effet plafond** : la ligne de base SM est à ~0,23, loin de 0. Il reste toute la place pour observer une adaptation.
- **AE atteint la meilleure réponse exacte après une seule réflexion**, et ses notes identifient Station explicitement (« stratégie parfaitement passive et déterministe… engager avec Rhun »). Une seule entrée mémoire, tenue à jour sur trois frontières, jamais saturée.
- **Luna ne value-bet pas de façon fiable** : il n'engage Rhun que 43–67 % du temps contre un adversaire qui couvre toujours, à tous les niveaux d'effort. C'est le motif d'*endgame misdetection* documenté par GTBENCH — matière pour H4.
- Prudence : ICL/AE à K = 20, soit n ≈ 3 par info-set. Direction, pas mesure.

**K = 150 validé sur pièces** : |écart(K=150) − écart(K=200)| = **0,0032**, quinze fois sous le seuil de 0,05 du PRD 3 §7.3.

**Coût réel** : 0,172 $ la série de 200 manches, soit 0,86 millième de dollar par décision. Latence 11 s/manche, 40 min la série. Parsing **260/260** sur les quatre runs.

**Fenêtre ICL portée de 6 000 à 13 000 tokens (tranché le 2026-08-21).** Le récap pèse 109 caractères par manche (mesuré), soit ~4 088 tokens pour une série de K = 150. À 6 000 tokens et avec une éviction par séries entières, la fenêtre n'en retenait plus **qu'une** : ICL devenait incapable d'accumuler *par construction*, et H3 se réduisait à « une mémoire qui ne peut pas accumuler n'accumule pas » — un artefact de paramétrage, pas un résultat. À 13 000, elle en contient **trois** : ICL accumule, puis sature et évince. Marge calculée pour rester à 3 même si les récaps s'allongent (3 × 4 088 = 12 264 ≤ 13 000 < 16 352). Coût : +7 $ sur la campagne, exactement le poste où il doit aller — ICL contre AE *est* la question de contribution du mémoire. Écartée : la compression du récap (elle aurait touché au **stimulus**, la matière que les deux conditions consomment).

**Contrôle croisé d'isolation recalculé à la clôture.** La liste des stores voisins était figée à la préparation : six runs démarrés ensemble ne se voyaient pas les uns les autres, et le contrôle restait vide jusqu'à la fin. Elle est désormais recalculée à la clôture, où tous les voisins existent. Conseil opérationnel : **décaler les lancements de 30 secondes** pour que le canari de chaque run voie les précédents dès le démarrage — un contrôle *a priori* vaut mieux qu'*a posteriori* quand un run contaminé ressemble à de l'adaptation.

## 5. Où en est-on / où va-t-on

L'état d'avancement détaillé (tâches, jalons, prochaine action) vit dans **`PROGRESS.md`** — ce fichier-ci ne le duplique pas. Structure cible du dépôt : `prd/` (00 à 04), puis `src/` (moteur, harnais, arbitre, analyse), `tests/`, `runs/` (hors OneDrive, symlink ou chemin configuré).
