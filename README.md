# La mémoire d'un agent LLM produit-elle une stratégie ?

Dispositif expérimental, données et analyses du mémoire de M2 IREN de **Léo Videt**
(Université Paris-Saclay, sous la direction du Pr Fabrice Le Guel, 2026).

**Question.** Dans un environnement stratégique à information imparfaite, un agent
LLM autonome équipé d'une mémoire persistante développe-t-il une adaptation
comportementale s'apparentant à une stratégie ? Et si oui, cette adaptation le
rapproche-t-elle de l'optimalité de l'*homo œconomicus*, ou reproduit-elle des
biais de décision ?

**Dispositif.** Un agent joue un poker de Kuhn au vocabulaire réécrit, en séries
répétées, contre des adversaires à politique fixe et connue, sous trois conditions
de mémoire. Le modèle est tenu constant ; la mémoire est la seule variable
manipulée. Chaque série donne un **écart d'exploitation exact** — la distance entre
ce que l'agent obtient et ce qu'obtiendrait un joueur ayant compris cet adversaire
précis — calculé par énumération complète en arithmétique rationnelle, sans
simulation ni intervalle de confiance sur l'instrument.

---

## Par où commencer

| Vous voulez… | Allez à |
|---|---|
| lire le mémoire | [`memoire/`](memoire/) |
| voir les résultats et l'inventaire complet des données | [`memoire/resultats.md`](memoire/resultats.md) |
| **reproduire les analyses** à partir des données | **[`REPLICATION.md`](REPLICATION.md)** |
| comprendre l'architecture du dispositif | [§ Architecture](#architecture) ci-dessous |
| les données brutes d'analyse | [`donnees/`](donnees/) |
| les figures et tableaux du mémoire | [`memoire/figures/`](memoire/figures/), [`memoire/tableaux/`](memoire/tableaux/) |

---

## Résultats

Campagne close le 24 août 2026 : **24 exécutions, 177 séries, 26 550 manches,
27 290 décisions, 47,27 $** sur `openai/gpt-5.6-luna`. Rejeu de complétude 24/24,
intégrité de clôture 24/24, zéro action imposée par défaut, zéro rupture du gel
mémoire.

| Hypothèse | Verdict |
|---|---|
| **H1** — l'adaptation vient de la mémoire | **établie** : jusqu'à **+0,704 jeton/manche** récupéré, neuf paires appariées sur neuf dans le même sens |
| **H2** — elle exploite, elle ne récite pas | **établie** : la référence récitée atteint **exactement 7/9 et 1/9**, les maxima théoriques de l'exploitation ; contrôle négatif tenu sur 39 séries |
| **H3** — le mécanisme de rétention compte | **établie sous condition** : la mémoire auto-écrite bat la réinjection d'historique (**+0,038 ± 0,015**) là où la tâche exige une politique différenciée par carte, pas là où une règle unique suffit |
| **H4** — des biais de décision persistent | **établie sur un volet** : aucune incohérence explicite détectable (0 divergence sur 604 décisions où l'agent énonce son choix), mais la mémoire **produit** la dégénérescence des stratégies mixtes — **0 %** de séries aux bornes sans mémoire, **56 %** dès qu'une note est écrite |

Le résultat central est la conjonction des deux derniers : ce qui rend l'agent
performant — la formulation d'une règle en langue naturelle — est ce qui le rend
incapable de jouer une fréquence. L'adaptation et le biais ne coexistent pas, le
second est produit par le premier.

---

## Le plan expérimental

**Le jeu.** Poker de Kuhn : trois cartes, mise unique, douze ensembles
d'information. Assez petit pour que son équilibre soit calculable exactement,
assez riche pour que le bluff y soit optimal. Le vocabulaire est réécrit (`Tor`,
`Vael`, `Rhun` au lieu de valet/dame/roi) afin que la reconnaissance du jeu source
devienne une covariable mesurée plutôt qu'une hypothèse.

**Trois adversaires**, à politique fixe et publique :

| Adversaire | Comportement | Exploitation optimale |
|---|---|---|
| `GTO` | joue l'équilibre (α = 1/3) | aucune — c'est le plafond |
| `Station` | n'engage jamais, couvre toujours | ne jamais bluffer, engager la carte forte |
| `Over-folder` | n'engage jamais, se couche toujours | engager quelle que soit la carte |

`Station` et `Over-folder` ont des défauts **opposés** : aucune stratégie fixe,
l'équilibre compris, ne peut faire baisser les deux mesures ensemble. C'est ce
plan d'adversaires qui sépare l'exploitation de la récitation, et c'est le cœur de
l'identification.

**Trois conditions de mémoire**, même modèle, mêmes paramètres d'inférence, même
harnais :

| Condition | Ce que l'agent lit entre les séries |
|---|---|
| `SM` | rien — contexte neuf à chaque manche |
| `ICL` | le récapitulatif brut des séries passées, fenêtré |
| `AE` | sa propre note, qu'il rédige et révise lui-même (`MEMORY.md` d'Hermès) |

**L'appariement.** La carte de chaque manche est une **fonction déterministe** de
`(graine, réplication, série, manche)` — pas un tirage. Deux conditions reçoivent
donc les mêmes cartes dans le même ordre *par construction*, et la chance s'annule
dans les comparaisons appariées.

---

## Architecture

Quatre couches aux responsabilités disjointes. Le découpage n'est pas cosmétique :
il garantit que l'instrument de mesure n'a jamais vu un modèle de langage.

```
src/
├── moteur/     règles du jeu, meilleure réponse, écart d'exploitation
│               → arithmétique en Fraction, aucun appel réseau, aucune simulation
├── harnais/    tout ce que l'agent lit et tout ce qu'il produit
│               → gabarits de prompt, parsing des actions, les trois conditions
│                 mémoire, magasin isolé par exécution, gel intra-série
├── arbitre/    orchestration : distribution des cartes, alternance des positions,
│               frontières de série, règle d'arrêt, reprise sur incident
└── journal/    enregistrement validé à l'écriture, CSV dérivés, rejeu
```

L'agent est **Hermès (Nous Research)**, utilisé nativement avec son propre
mécanisme de mémoire. Le dépôt construit l'arène, pas l'agent.

**225 tests, aucune dépendance externe, aucun appel API dans la suite.**

```bash
python -m pytest -q                                      # la suite complète (~10 s)
PYTHONPATH=src python -m journal.rejouer <dossier logs>   # re-régler une exécution
```

### Ce qui fait la validité du dispositif

- **La mesure est exacte.** Douze ensembles d'information, arbre de profondeur
  trois, énumération complète en fractions. Aucune estimation, aucun intervalle de
  confiance sur l'instrument lui-même.
- **Tout est rejouable.** Chaque manche se re-règle depuis ses seuls journaux et
  retrouve les mesures publiées. Vérifié 24 fois sur 24.
- **La mesure a été recalculée par un second chemin**, écrit dans un autre langage
  (`analyse/R/`) sans réutiliser le code du dispositif. Les deux calculs coïncident
  sur les 177 séries à la seizième décimale.
- **L'isolation est vérifiée, jamais supposée.** Un marqueur unique est écrit *par
  l'agent* dans le magasin de son exécution, puis recherché dans tous les autres.
- **Le dispositif a été audité avant la campagne**, en aveugle et sur consigne
  adversariale ([`docs/AUDIT.md`](docs/AUDIT.md)). Ses quatre constats sont
  corrigés. Aucun n'était dans ce code, aucun n'était détecté par les tests, tous
  se logeaient à la frontière avec l'outillage tiers piloté — dont un fichier de
  consignes du dépôt qui nommait le jeu et décrivait l'exploitation de chaque
  adversaire, injecté à l'agent à chaque décision.

---

## Les données

Versionnées dans [`donnees/`](donnees/). Les journaux bruts (401 Mo de JSONL)
restent hors dépôt ; ces fichiers en sont l'export exhaustif, sans les prompts
servis, qui pèsent cinquante-cinq fois le reste et se reconstruisent depuis les
gabarits.

| Fichier | Contenu | Unité |
|---|---|---|
| `sessions.csv` | écart d'exploitation, référence récitée, coûts, drapeaux | une ligne par série (177) |
| `decisions.csv` | chaque décision avec le **texte intégral** du raisonnement de l'agent | une ligne par décision (27 290) |
| `infosets.csv` | fréquences observées par ensemble d'information | série × ensemble |
| `memoire.csv` | événements d'écriture et de révision de la note | frontière de série |
| `runs.csv` | paramètres, graine, verdicts d'intégrité, budget | une ligne par exécution (24) |
| `notes-ae.md` | les **90 notes intégrales** écrites par l'agent, avec l'écart de leur série | note |

`notes-ae.md` est la pièce qualitative du travail : c'est là que se lit ce que
l'agent retient, ce qu'il supprime, et ce qu'il n'écrit jamais — une fréquence.

---

## Le dépôt

| | |
|---|---|
| [`src/`](src/) | l'arène — moteur, harnais, arbitre, journal |
| [`tests/`](tests/) | 225 tests, dont l'oracle analytique du moteur |
| [`donnees/`](donnees/) | les données d'analyse, versionnées |
| [`analyse/`](analyse/) | les scripts qui dérivent tout le reste ([README](analyse/README.md)) |
| [`analyse/R/`](analyse/R/) | le second chemin de calcul, indépendant du Python |
| [`memoire/`](memoire/) | le mémoire, ses figures, ses tableaux |
| [`docs/`](docs/) | spécification d'origine, PRD, contexte, brief d'audit, avancement |
| [`scripts/`](scripts/) | lancement de campagne |

Aucun script d'analyse ne produit de donnée : tous **dérivent** ce qui existe déjà
dans les journaux. Tout ce qu'ils écrivent est régénérable et jetable.

---

## Reproduire

Voir **[`REPLICATION.md`](REPLICATION.md)**. En résumé : les analyses se refont
depuis `donnees/` sans aucun appel API ni aucun coût, en une commande. Relancer la
collecte elle-même suppose un accès au fournisseur et environ 47 $.
