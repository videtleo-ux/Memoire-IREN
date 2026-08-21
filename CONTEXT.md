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

## 5. Où en est-on / où va-t-on

L'état d'avancement détaillé (tâches, jalons, prochaine action) vit dans **`PROGRESS.md`** — ce fichier-ci ne le duplique pas. Structure cible du dépôt : `prd/` (00 à 04), puis `src/` (moteur, harnais, arbitre, analyse), `tests/`, `runs/` (hors OneDrive, symlink ou chemin configuré).
