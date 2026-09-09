# Brief d'audit — avant lancement de la campagne

*Rédigé le 2026-08-21 par l'auteur du dispositif, à l'intention d'un auditeur indépendant.*

---

## 1. Ce qu'on te demande

Le dispositif est terminé, calibré, et sur le point de consommer 27 exécutions,
~50 000 appels API et deux jours de calcul. Avant de le lancer, on veut savoir
s'il reste une faille capable d'invalider la campagne **sans que rien ne le
signale**.

Ta consigne n'est pas « vérifie que c'est correct ». C'est :

> **Trouve ce que l'agent peut voir et qu'il ne devrait pas voir.
> Trouve ce qui pourrait être enregistré comme une donnée sans en être une.**

La première consigne produit un rapport rassurant. La seconde trouve des choses.

## 2. Pourquoi cet audit existe : deux exemples vécus

En une soirée de calibrage, deux défauts ont été trouvés. **Aucun des deux
n'était dans le code de ce dépôt. Aucun n'a été attrapé par les 201 tests.
Aucun n'aurait laissé de trace dans les journaux.** Ils ont été trouvés par
accident.

**Défaut n°1 — le corrigé dans le prompt.** Hermes explore le répertoire de
travail à la recherche de fichiers de consignes (`AGENTS.md`, `CLAUDE.md`,
`.cursorrules`) et **les injecte dans son prompt système**. L'arène tournait
depuis le dépôt. L'agent recevait donc, à chaque manche, un `CLAUDE.md` qui
nomme le jeu réel, donne la constante d'équilibre, et décrit l'exploitation de
chaque adversaire nommément. Mesuré : 11 633 octets de consignes du dépôt dans
le prompt système, contre 0 depuis un répertoire vide.

Conséquence : les 45 « reconnaissances du jeu » relevées au premier mini-run
ne prouvaient rien — l'agent lisait. Après correctif : **0 sur 200 sorties**.

**Défaut n°2 — la panne prise pour une réponse.** `hermes -z` restitue les
échecs de fournisseur **sur stdout avec un code de retour 0**. Le harnais
prenait « API call failed after 3 retries: HTTP 404… » pour une réponse du
modèle : parsing en échec, action passive imposée, exécution terminée
proprement, série entière d'`action_par_defaut` **enregistrées comme des
données**.

**Le motif commun, et c'est lui qu'il faut chasser :** une défaillance qui ne
ressemble pas à une erreur dans les résultats, mais **à un résultat**. Un run
contaminé ne plante pas — il se lit comme de l'adaptation.

Les deux se logeaient à la **frontière entre notre code et l'outillage tiers
qu'il pilote**. C'est là qu'il faut chercher.

## 3. Mes angles morts, déclarés

J'ai conçu ce dispositif, donc je regarde là où j'ai déjà regardé. Trois
faiblesses que je m'attribue :

- **J'ai mesuré le prompt système sans jamais le lire.** Je connais sa taille
  (8 977 octets hors fuite) et j'ignore son contenu. C'est exactement l'angle
  mort qui a laissé passer le défaut n°1 : j'avais mesuré la fuite avant de la
  comprendre.
- **J'ai neutralisé les canaux mémoire que je connaissais** (`USER.md`, revue
  d'arrière-plan, création de skills, `session_search`). Pas ceux que
  j'ignore. Le journal d'Hermes annonce « 48 plugins activés ».
- **L'oracle de mesure et le moteur ont la même main.** Les tests T1–T9
  vérifient le moteur contre une dérivation analytique que j'ai faite
  moi-même. Une erreur commune aux deux ne se verrait pas.

## 4. Les quatre cibles, par ordre de rendement attendu

### Cible 1 — Lire ce que l'agent reçoit réellement (priorité maximale)

Le prompt système d'Hermes fait ~9 Ko et personne ne l'a lu. Que contient-il ?

```bash
# taille et décomposition, sans appel API
HERMES_HOME=<store> hermes prompt-size
HERMES_HOME=<store> hermes prompt-size --json
```

Questions ouvertes : y a-t-il un horodatage, un identifiant de session, des
définitions d'outils, le contenu de `SOUL.md` ? Quelque chose qui pourrait
orienter le jeu, nommer le domaine, ou varier d'un appel à l'autre ?

Compare aussi le prompt **effectivement envoyé** au champ `vue_servie` des
journaux. Ils doivent différer exactement du prompt système d'Hermes, et de
rien d'autre.

### Cible 2 — Chercher les autres canaux d'injection

Le store d'une exécution contient, après un run : `SOUL.md`, `state.db`,
`skills/`, `shared/`, `sessions/`, `cache/`, `logs/`. Lesquels peuvent
remonter dans le contexte de l'agent ?

Le code d'Hermes est local et lisible :
`C:\Users\videt\AppData\Local\hermes\hermes-agent`. Point d'entrée utile :
`run_agent.py`, `agent/system_prompt*.py`, `hermes_cli/plugins.py`.

Vérifie en particulier que le toolset servi pendant les manches
(`context_engine`) n'expose réellement **aucun** outil, et que la mémoire
native est bien inerte hors frontière.

### Cible 3 — Re-dériver la mesure, indépendamment

L'écart d'exploitation est l'instrument : s'il est faux, tout est faux.

Prends un journal réel, et recalcule `π̂` puis l'écart **sans utiliser
`src/moteur/`**. Une implémentation naïve suffit : 6 donnes, un arbre de
profondeur 3, énumération complète. Confronte à `mesures.exact` dans
`sessions.jsonl`.

Valeurs de référence à retrouver (dérivées à la main, PRD 1 §7) : valeur du
jeu `−1/18` ; meilleure réponse `+1/3` contre Station et `+1` contre
Over-folder ; écart d'un récitant d'équilibre `1/9` contre Station et `7/9`
contre Over-folder.

### Cible 4 — Attaquer les invariants d'orchestration

Trois propriétés dont la violation serait invisible :

- **Appariement des donnes.** Deux traitements au même `(réplication, série,
  manche)` doivent recevoir des cartes identiques. Vérifie sur des journaux
  réels de deux exécutions différentes, pas seulement par les tests.
- **Gel de la mémoire.** Le contenu servi doit être identique aux K manches
  d'une série. Le champ `memoire.gel_rompu` doit être `false`, mais vérifie-le
  toi-même depuis `vue_servie`.
- **Isolation entre exécutions.** Deux runs parallèles ne doivent pas se
  toucher. Le contrôle croisé au démarrage est **partiel** si les runs
  démarrent simultanément (le canari ne voit que les stores déjà créés) ;
  celui de clôture est complet. C'est un point que je considère comme fragile.

## 5. Ce qui est déjà vérifié — ne le refais pas

- **201 tests** couvrent la logique interne (`python -m pytest -q`, ~13 s, zéro
  appel API). La couverture fonctionnelle n'est pas le sujet.
- **Le rejeu de complétude** re-règle chaque manche depuis les seuls journaux
  et retrouve `π̂` et l'écart : `python -m journal.rejouer <dossier logs>`.
- **L'appariement, le gel, l'isolation et l'équilibre des positions** passent
  sur les journaux réels — mais par mes propres contrôles, écrits par moi.
- **Le calibrage** : modèle `openai/gpt-5.6-luna`, effort `medium`, K = 150,
  260/260 réponses exploitables, coût 0,86 millième de dollar par décision.

## 6. Où sont les choses

| | |
|---|---|
| Spécification (autorité sur le *quoi*) | `docs/spec-build-arene-kuhn.md` |
| Conception (autorité sur le *comment*) | `prd/00` à `prd/04` |
| **Contexte vivant, pièges connus** | **`docs/CONTEXT.md` — à lire en premier** |
| Chapitre de méthode du mémoire | `memoire/methodologie.md` |
| Journaux d'exécutions réelles | `C:\arene-runs-k200`, `-luna`, `-icl`, `-ae`, `-medium` |

Le code s'exécute sans installation : `PYTHONPATH=src`. L'interpréteur avec
pytest est `C:/Users/videt/anaconda3/python.exe`.

⚠️ **Le modèle par défaut est payant.** Pour tout essai, passe
`--modele tencent/hy3:free`, gratuit — en sachant qu'il ignore le contrôle
d'effort de raisonnement et n'est donc pas représentatif du modèle de campagne.

## 7. Ce qu'on ne te demande pas

- Une revue de style, d'architecture ou de lisibilité. Le code est en
  français, documenté sur le *pourquoi*, et ce n'est pas le risque.
- Des tests supplémentaires sur la logique interne. Il y en a 201.
- Un avis sur les choix de conception déjà tranchés et documentés
  (`docs/CONTEXT.md` §4, §4 bis, §4 ter). Ils ont leurs raisons ; conteste-les
  seulement si tu trouves qu'ils créent une faille, pas parce que tu ferais
  autrement.

## 8. Ce qu'on attend en sortie

Par constat : **où**, **comment le reproduire**, et surtout **pourquoi ça ne
se verrait pas dans les résultats**. Ce dernier point est le critère de tri —
un défaut visible n'est pas dangereux ; un défaut silencieux l'est.

S'il n'y a rien : dis-le. Un audit qui ne trouve rien après avoir cherché aux
bons endroits est une information, à condition d'énoncer ce qui a été
réellement exploré et ce qui ne l'a pas été.
