# CONTEXT.md — Contexte vivant du projet

Dernière mise à jour : 2026-09-03. Ce fichier capture tout ce qui n'est **pas** dans la spec ni dans les PRD : les décisions prises en discussion avec le pilote, les découvertes d'environnement, et les contraintes réelles. À relire en début de toute session de travail, avec `docs/spec-build-arene-kuhn.md` et `docs/prd/00-vue-densemble.md`.

## 1. Le projet en une phrase

Arène expérimentale pour un mémoire de M2 (IREN) : faire jouer un agent LLM à un Kuhn poker obfusqué contre des bots à politique fixe, sous 3 conditions mémoire, et mesurer l'adaptation par un écart d'exploitation exact par session — toute adaptation observée doit être attribuable à la **mémoire**, pas au harnais.

## 2. Cadre et contraintes du pilote (Léo, seul sur le projet)

- **Livrables** : système qui tourne + résultats analysés + mémoire écrit + accès au code + soutenance. **Échéance : quelques semaines** (rentrée 2026). Directeur non impliqué dans les décisions techniques.
- **Budget API : quelques dizaines d'euros.** N = 3 réplications/cellule, K = 200 manches/session au départ (pilote de calibrage prévu pour ajuster).
- **Machines** : Victus Windows 11 (i5-12e gén, RTX 3050 4 Go, 16 Go RAM) — machine principale, Hermes Agent installé et authentifié ; Mac M2 8 Go — Hermes **pas encore installé** (point ouvert).
- **Stack** : Python 3.11 (installé sur le Victus). Analyse finale Python et/ou R. Logs JSONL (source de vérité) + CSV dérivé, centralisés via Git.
- **Hors périmètre confirmé** : bras transfert, bras humain, adversaire LLM figé (§11 spec). Pas de contraintes éthiques/confidentialité sur le build primaire.
- Le papier **Loriente & Diez** (2023) est cité dans la bibliographie finale ; la constante GTO contestée avait de toute façon été tranchée par l'oracle analytique (couverture J1-Vael = 2/3 à α = 1/3). Point clos.

## 3. Découvertes d'environnement (vérifiées sur machine, 2026-08-19)

**« Hermès » = Hermes Agent, le CLI d'agent de Nous Research** — pas des poids de modèle. Install fonctionnelle sous `C:\Users\videt\AppData\Local\hermes` (`HERMES_HOME` défini), OAuth Nous Portal actif, dépôt source du CLI cloné dans `hermes-agent/` (docs complètes sous `website/docs/`). Conséquences :

- **Pas de vLLM, pas d'inférence locale.** Le modèle est servi par l'API Nous Portal (catalogue : Claude, GPT, Gemini, DeepSeek, Qwen, GLM, `tencent/hy3:free`, etc. — aucun modèle nommé « Hermes » au catalogue). Les deux PC ne portent que l'arbitre Python.
- **Mécanisme mémoire natif conforme à la spec** : `MEMORY.md` (~2 200 caractères ≈ 8–15 entrées, erreur en cas de dépassement, pas de compaction auto, auto-élagage par l'agent), snapshot injecté au prompt système en début d'invocation. La spec §5–§7 décrit ce mécanisme quasi mot pour mot.
- **⚠️ Piège n°1 — persistance immédiate** : Hermes écrit la mémoire **sur disque immédiatement** (seul le prompt système est figé par invocation), et une revue d'auto-amélioration en arrière-plan peut écrire après chaque tour. Le « gel intra-session » doit donc être imposé par l'arbitre au niveau fichiers (snapshot/restauration — décision D2).
- **⚠️ Piège n°2 — canaux mémoire annexes** : session_search (FTS5 sur `state.db`), skills auto-créées, providers externes (Honcho, Mem0…), USER.md. Tous doivent être neutralisés/isolés pour que `MEMORY.md` soit l'unique canal d'apprentissage (config + isolation par `HERMES_HOME` dédié par run).
- **Interface scriptable** : `hermes -z "<prompt>"` — prompt en entrée, réponse finale seule sur stdout. C'est l'interface arbitre → agent pour les 3 conditions (décision D1 : harnais unique pour éviter le confond harnais × mémoire).
- **⚠️ Piège n°3 — OneDrive** : le dépôt vit sous OneDrive ; les données de runs (écritures haute fréquence + clones de HERMES_HOME) iront hors OneDrive (`C:\arene-runs`), synchronisées vers Git aux frontières de session (décision D7).

## 4. Décisions de design prises en discussion (au-delà de la spec)

Voir le tableau complet D1–D8 dans `docs/prd/00-vue-densemble.md` §2. Les plus structurantes :

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

## 4 sexies. Audit indépendant du 2026-08-22 — quatre constats, trois corrigés

L'audit prévu par `docs/AUDIT.md` a rendu quatre constats majeurs. Les quatre sont corrigés (220 tests verts, dont 19 nouveaux).

**⚠️ Piège n°9 — C1, corrigé : le chemin du store fuit dans le prompt système.** Hermes insère `HERMES_HOME` en clair dans son prompt système, deux fois (« Current working directory » et « Active Hermes profile »), sans option pour l'éteindre. Un dossier `SM-station-r1` servait donc le nom du bot — « station » et « over-folder » énoncent l'exploitation — et la condition, à chaque manche, invisiblement (le prompt système n'est pas dans `vue_servie`, le raisonnement n'est jamais restitué, le détecteur ignore ces termes). Corrigé : le dossier d'un run est un code opaque dérivé, `run-<sha256(graine|run_id)[:12]>` (`arbitre.run.code_dossier`) ; le run_id reste dans chaque ligne de log, `etat_run.json` et le témoin d'isolation ; le marqueur du canari utilise le code opaque ; l'ancien nommage est refusé au démarrage. Conséquence rétroactive : les runs du pilote avaient tous « station » dans leur chemin — le « AE à 0,000 en une réflexion » est à revérifier après correctif.

**⚠️ Piège n°10 — C2, corrigé (2026-08-22) : la fenêtre ICL de campagne dépassait la limite argv de Windows.** Le prompt partait en argument de `subprocess` ; CreateProcess plafonne à 32 767 caractères ; deux récaps K = 150 + règles ≈ 34 900. Les 9 runs ICL se seraient arrêtés en série 3 (`WinError 206` → `ErreurArbitre`) après deux séries payées — invisible au pilote (ICL à K = 20), invisible aux tests (invocateur simulé). **« Réduire K » a été chiffré et écarté** : tenir 3 séries dans argv exige K ≤ 84, niveau où le critère du PRD 3 §7.3 échoue sur pièces (|écart(80) − écart(200)| = 0,054 > 0,05 sur le run `medium`) et où le bruit par série (σ bootstrap ≈ 0,043) est de l'ordre des effets mesurés au pilote ; le compromis K=120 + fenêtre 2 séries aurait amputé H3. Corrigé sans compromis : `hermes -z` n'étant qu'un habillage de `_run_and_exit_oneshot` (`hermes_cli/main.py`), l'invocateur écrit le prompt dans un fichier temporaire (à côté de `usage.json`, jamais dans `cwd-neutre`) et exécute `src/harnais/pilote_oneshot.py` avec le python du venv d'Hermes — même chemin d'exécution, zéro patch d'Hermes, plafond argv supprimé, pas de repli argv possible (échec bruyant si le venv est introuvable). Vérifié en réel : le prompt ICL série 2 de campagne (34 694 caractères) traverse le chemin de production, réponse `ACTION: engager` en `Parsing.OK`, usage `completed: true`. Au passage : sur ce prompt répété, `cache_lus = 14 336` — le cache de préfixe du fournisseur mord bel et bien à taille de campagne ; le « cache ne mord jamais » du pilote était un artefact des petits prompts. Mesure réelle : ~2,4 caractères/token sur `hy3` (l'estimation à 4 sous-estime les tokens réels — impact coût d'entrée seulement, à re-mesurer sur Luna via `cache_ecrits` dès la première série).

**C3, corrigé : la panne prise pour une réponse, version complète.** Le filet du piège n°8 (4 motifs) ne couvrait qu'une fraction des `final_response` d'échec rendus code retour 0 (« Billing or credits exhausted », « Context length exceeded », refus de politique de contenu, sortie tronquée…). Cas limite vicieux : une série entière en échec → π̂ vide → comblé aux valeurs GTO → écart = 1/9 vs Station et 7/9 vs Over-folder, **exactement le niveau « récitant »** — une panne se lit comme un résultat. Corrigé : le harnais lit désormais le verdict d'Hermes lui-même dans le rapport `--usage-file` (`failed`/`completed`, `harnais.hermes._echec_usage`) — vérifié sur le binaire réel (`completed: true, failed: false` sur un appel nominal) — et les motifs textuels, complétés des formes relevées, deviennent une défense en profondeur.

**C4, corrigé : `tokens.in` était une colonne remplie qui ne mesurait rien.** Le `input_tokens` du fournisseur est net du cache (`prompt_total − cache_lus − cache_écrits`) ; Nous écrivant tout le préfixe en cache à chaque appel sur Luna, le champ valait 3 sur les 540 tours réels des cinq runs pilotes. Corrigé : `cache_ecrits` est propagé jusqu'aux logs de tour et de série et aux CSV — l'entrée réellement servie se reconstruit (`in + cache_lus + cache_ecrits`), et la constante `CARACTERES_PAR_TOKEN` redevient vérifiable sur pièces. Les logs pilotes antérieurs restent lisibles (cellule vide).

Vérifié sans trouvaille à l'audit, sur pièces : mesure re-dérivée indépendamment (écart identique à 10 décimales), appariement des donnes (240 coordonnées, 0 divergence), gel depuis `vue_servie`, toolset de manche réellement vide, pas de canal de session caché, pas de bascule de modèle possible. Constat mineur : `memory.flush_min_turns` n'existe pas dans Hermes (clé inerte).

## 4 septies. Run de validation C2 sur Luna (2026-08-22) — pilote fichier prouvé, enveloppe recalculée

**Run réel `ICL-station-r1`, 4 séries de K = 150 sur `openai/gpt-5.6-luna`** (racine `C:\arene-runs-verif-c2`, dossier opaque `run-f1060d1c067d`). Verdict : **600/600 réponses en parsing `ok` strict, zéro défaut, zéro relance, zéro erreur de harnais**, intégrité de clôture OK, rejeu de complétude OK. Le pilote fichier a servi sans incident les fenêtres de 34 739 puis **51 059 caractères** (`vue_servie` mesurée) — au-delà du plafond argv de 32 767 qui condamnait la campagne. La **reprise sur incident a été exercée deux fois en vrai** (kills externes du lanceur, pas de l'arbitre) : 84 tours archivés en `turns.abandonnes.jsonl`, séries rejouées à donnes identiques, fenêtre reconstruite depuis les récaps logués. Écart : 0,201 → 0,076 → 0,060 → 0,045 — escalier descendant, **sous le niveau récité (0,066) dès la série 3**.

**Mesures de coût/latence par série (Station, `medium`), du provider lui-même :**

| série (fenêtre) | coût | s/manche | entrée réelle/appel |
|---|---|---|---|
| 0 (vide ≈ SM) | 0,131 $ | 11,3 | 1 645 tokens |
| 1 (1 récap) | 0,388 $ | 13,4 | 7 176 |
| 2 (2 récaps) | 0,588 $ | 13,3 | 12 762 |
| ≥3 (saturée) | **0,821 $** | 14,1 | 18 332 |

Trois causes d'écart avec l'estimation initiale : **(a)** le français tokenise à ~2,8 caractères/token sur Luna (mesuré ; l'estimation `CARACTERES_PAR_TOKEN = 4` sous-compte de ~40 % — la fenêtre « 13 000 tokens estimés » pèse ~18 000 tokens réels, sans impact de validité) ; **(b)** **le cache de Luna n'a jamais lu un token en 600 appels** (contrairement à `hy3`, qui mord) ; **(c)** l'écriture cache est tarifée au catalogue Nous ~0,30 $/M, soit ~3,5× l'entrée — payée à fonds perdus vu (b). Pas de bouton client : la clé `prompt_caching` d'Hermes ne couvre que le protocole Anthropic, l'écriture est côté fournisseur. **À vérifier sur le portail Nous** : la balance doit avoir baissé de ~2,33 $ pour ce run si la prime est réellement facturée (~1,0 $ sinon — auquel cas l'enveloppe ci-dessous est pessimiste).

**Enveloppe de campagne recalculée** (27 runs, K = 150, réflexion AE ≈ +0,01 $/frontière, majoration GTO ≈ +15 % de décisions — hypothèse non mesurée) :

| poste | plateau à 10 séries | plafond 16 séries |
|---|---|---|
| SM (9 × 3 séries) | ~3,7 $ | ~3,7 $ |
| ICL (9 runs) | ~64 $ | ~110 $ |
| AE (9 runs) | ~15 $ | ~24 $ |
| **total** | **~83 $** | **~137 $** |

Contre 41–63 $ annoncés : ×1,5 à ×2,2, porté à ~90 % par les séries ICL saturées. **Facturation confirmée sur le portail le 2026-08-22 : balance −2,33 $ pour le run de validation** — la prime cache-write est réelle, l'enveloppe ci-dessus fait foi. Aucun opt-out côté client (vérifié dans Hermes : la clé `prompt_caching` ne couvre que le protocole Anthropic, et il n'existe pas de profil fournisseur « nous » exposant un champ de requête pour désactiver le cache). Leviers restants, par ordre : le plateau (10 vs 16 séries = −46 $ sur ICL — et la courbe de validation, déjà à 0,045 en série 3, plaide pour un plateau précoce) ; demander à Nous si un opt-out cache-write existe (~−60 % sur ICL) ; en dernier recours `SERIES_MAX`, qui est une décision scientifique, pas budgétaire (PRD 3 §3).

**Durée** : 28 min (série SM) à 35 min (saturée). Séquentiel : ~109 h (plateau à 10) à ~167 h (plafond) — « deux jours » ne tient qu'avec du parallélisme, désormais sans risque (isolation prouvée : canari réel, témoin, dossiers opaques) : 3 runs de front ≈ 36–56 h, 5 de front ≈ 22–33 h, lancements décalés de 30 s (§4 quinquies).

## 4 octies. Campagne complète (22-24 août 2026) — collecte close

**24 exécutions, 177 séries, 26 550 manches, 27 290 décisions, 47,27 $.** Rejeu de complétude 24/24, intégrité 24/24, zéro action par défaut, zéro relance, zéro erreur de harnais, zéro rupture du gel. Résultats et inventaire complet des données : `memoire/resultats.md`.

**H1, H2 et H3 sont établies.** L'écart AE tombe à 0,000 contre Station et Over-folder et s'y tient ; la référence récitée atteint exactement 7/9 et 1/9, les maxima théoriques de l'exploitation ; le contrôle négatif tient (référence récitée jamais positive contre GTO). H3 est vraie **sous condition** : AE bat ICL contre Station (+0,038 ± 0,015) mais pas contre Over-folder (+0,004 ± 0,006) — le mécanisme de rétention ne compte que là où la tâche exige une politique différenciée par carte. Et le mécanisme n'est pas celui qu'on attendait : la fenêtre ne produit aucun décrochage en dents de scie, et **les deux conditions chutent à la première frontière** — la vitesse ne les sépare pas. AE se verrouille ensuite sur zéro ; ICL s'arrête à un résidu non nul (~0,058 puis ~0,040) qu'il n'annule jamais. La différence porte sur la **complétude** de l'induction, ni sur la vitesse ni sur l'oubli : contre Station, ICL bluffe encore le sceau faible 7-9 % du temps après dix séries. Détail et décomposition dans `memoire/partie3-v2.md` §3.4.

**⚠️ Piège n°11 — les jetons de rafraîchissement Nous sont à usage unique.** Chaque store clonait `auth.json`, et Hermes place son magasin de jetons partagé **sous `HERMES_HOME`** : chaque run avait donc le sien, et passé l'heure de validité du jeton d'accès, tous rafraîchissaient avec la même copie. Le portail y a vu une réutilisation et a **révoqué la session entière** (« detected refresh-token reuse »). C'est ce qui a coupé l'authentification après la tranche SM+AE, et cela aurait cassé ICL en cours de route. Corrigé : `HERMES_SHARED_AUTH_DIR` désigne un magasin commun aux runs d'une racine (`<racine>/auth-partagee`), avec le verrou qu'Hermes prévoit pour ce cas. L'isolation mémoire n'est pas touchée — c'était l'identité qui était clonée à tort, pas `MEMORY.md`.

**Deux mesures qui changent les projections.** Les journaux bruts pèsent **401 Mo** (le prompt ICL à fenêtre pleine fait 51 000 caractères, répété 1 500 fois par exécution) ; `donnees/decisions.csv` en est l'export sans les prompts, 55 fois plus léger. Et le coût réel d'une exécution ICL est de 4,71 $ (Over-folder) à 6,66 $ (Station) — les séries Station coûtent plus cher parce que l'agent y produit trois fois plus de raisonnement.

**Analyse close le 2026-08-26.** H4 est instrumentée (`analyse/h4.py` → `memoire/h4-mesures.md`) : la règle d'incohérence pré-enregistrée s'est révélée invalide (47,8 % artefactuels, huit faux positifs sur huit relus), et la dégénérescence des mixtes livre le résultat central — 0 % de séries aux bornes sans mémoire, 56 % dès qu'une note est écrite, avec un contrôle interne (la série 0 d'une exécution AE, note encore vide, n'y est pas). La partie III est rédigée (`memoire/partie3-v2.md`). Le codage manuel sur échantillon stratifié est écarté du périmètre.

**Ce qui resterait, hors périmètre** : la vitesse d'adaptation (mal résolue par K = 150, le plateau tombant dès la série 1) et le profil d'oubli d'ICL (jamais observé à cet horizon). Les deux demanderaient un autre protocole, pas plus du même.

## 5. Où en est-on / où va-t-on

**Projet terminé (2026-08-30).** Collecte close le 24 août, analyse close le 26 août, mémoire rédigé et mis en forme : le document remis est `Mémoire Videt Léo.docx`, à la racine du dépôt. Il ne reste ni collecte, ni analyse, ni rédaction. Le dépôt est en état de dépôt d'archive : le code, les données et les sources des chapitres y sont, et `REPLICATION.md` refait les analyses depuis `donnees/` sans appel API.

L'état d'avancement détaillé (tâches, jalons, prochaine action) vit dans **`docs/PROGRESS.md`** — ce fichier-ci ne le duplique pas. Structure cible du dépôt : `docs/prd/` (00 à 04), puis `src/` (moteur, harnais, arbitre, analyse), `tests/`, `runs/` (hors OneDrive, symlink ou chemin configuré).
