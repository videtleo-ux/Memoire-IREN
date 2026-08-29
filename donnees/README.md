# donnees/ — les données de la campagne

Export exhaustif des journaux de la campagne close le 24 août 2026 : 24 exécutions,
177 séries, 26 550 manches, 27 290 décisions.

Les journaux bruts (JSONL, 401 Mo) restent hors dépôt. Ces fichiers en sont
l'export complet **sans les prompts servis**, qui pèsent cinquante-cinq fois le
reste et se reconstruisent depuis les gabarits de `src/harnais/`.

## Les fichiers

### `sessions.csv` — 177 lignes, une par série

L'unité d'analyse du mémoire. Une série est une suite de 150 manches jouées sous
un état mémoire figé.

| Colonne | |
|---|---|
| `run_id`, `condition`, `bot`, `replication` | la cellule expérimentale |
| `session` | l'indice de série dans l'exécution, à partir de 0 |
| `K` | manches par série (150 en campagne) |
| `ecart` | **l'écart d'exploitation**, en jetons par manche — la variable dépendante |
| `reference_recite` | le second instrument, mesuré depuis l'équilibre |
| `ev_pi_hat`, `ev_br`, `ev_realisee` | espérance observée, de la meilleure réponse, et gain réalisé |
| `actions_par_defaut`, `relances`, `erreurs_harnais` | contrôles de conformité — tous à 0 sur la campagne |
| `n_flags_deobf`, `n_flags_recitation` | covariables de reconnaissance du jeu source |
| `ecritures_intra_serie` | contrôle du gel de la mémoire |
| `plateau_declare` | la règle d'arrêt |
| `cout_tokens_*` | entrée, sortie, cache lu, cache écrit |

`ecart` et `reference_recite` sont **exacts**, pas estimés : douze ensembles
d'information, énumération complète en arithmétique rationnelle.

### `decisions.csv` — 27 290 lignes, une par décision

Chaque décision de l'agent avec le **texte intégral** de sa délibération. C'est le
fichier qui permet de recalculer π̂, et donc tout le reste, sans faire confiance
aux mesures publiées.

### `infosets.csv` — série × ensemble d'information

Les fréquences observées de l'agent sur chacun des douze ensembles. C'est la
source de la mesure de dégénérescence des stratégies mixtes (H4).

### `memoire.csv` — frontières de série

Les événements d'écriture et de révision de la note : ce que l'agent ajoute, ce
qu'il conserve, ce qu'il supprime.

### `runs.csv` — 24 lignes, une par exécution

Paramètres, graine de campagne, verdicts du canari d'isolation et de l'intégrité
de clôture, budget consommé.

### `notes-ae.md` — les 90 notes intégrales

La pièce qualitative du travail : chaque note écrite par l'agent, avec l'écart de
la série qui l'a produite. C'est là que se lit ce qu'il retient, ce qu'il élague,
et ce qu'il n'écrit **jamais** — une fréquence pour sa propre action, dans aucune
des 90 notes.

## Refaire les mesures

Voir [`../REPLICATION.md`](../REPLICATION.md). En une commande :

```bash
Rscript analyse/R/analyse.R
```

Le script recalcule tout depuis `decisions.csv` avec un moteur de jeu écrit
indépendamment du dispositif, puis **confronte** ses résultats à `sessions.csv`.
L'écart attendu est nul à la précision machine.
