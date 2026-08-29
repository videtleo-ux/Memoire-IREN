# Reproduire les résultats

Trois niveaux, du plus léger au plus lourd. **Le niveau 1 suffit à refaire tous les
chiffres du mémoire** : il ne coûte rien, ne demande aucune clé d'API, et part des
données versionnées dans `donnees/`.

| Niveau | Ce qu'on refait | Coût | Durée |
|---|---|---|---|
| 1 — analyses | toutes les mesures, figures et tableaux du mémoire | 0 € | ~1 min |
| 2 — dispositif | les 225 tests et le rejeu des journaux | 0 € | ~10 s |
| 3 — collecte | la campagne elle-même, de zéro | ~47 $ | ~40 h |

---

## Prérequis

- **Python 3.11 ou 3.12.** Le dispositif (`src/`) est en bibliothèque standard
  pure, sans aucune dépendance. Seuls les scripts d'analyse et de rendu ont besoin
  de paquets.
- **R 4.x** pour le second chemin de calcul (niveau 1, variante R).

```bash
git clone https://github.com/videtleo-ux/Memoire-IREN.git
cd Memoire-IREN
```

Le paquet n'est pas installé : les exécutables ont besoin de `PYTHONPATH=src`. Les
tests, eux, le trouvent seuls (`pyproject.toml` fixe `pythonpath = ["src"]`).

---

## Niveau 1 — Refaire les analyses

### Variante R — recommandée, c'est le chemin de vérification

`analyse/R/analyse.R` recalcule **toute la partie III** depuis
`donnees/decisions.csv`, avec un moteur de jeu (`analyse/R/moteur.R`) réécrit
indépendamment du Python. C'est ce second chemin qui ferme l'angle mort déclaré au
§3 du brief d'audit : l'oracle et le moteur avaient la même main, ce script leur
en donne deux.

```r
install.packages(c("dplyr", "tidyr", "readr", "ggplot2"))
```

```bash
Rscript analyse/R/analyse.R      # à lancer depuis la racine du dépôt
```

Le script procède dans cet ordre, et l'affiche :

1. charge les 27 290 décisions ;
2. en tire π̂, la seule statistique du dispositif ;
3. calcule l'écart d'exploitation et la référence récitée des 177 séries ;
4. **vérifie** ces valeurs contre les chiffres publiés dans `donnees/sessions.csv` —
   c'est l'étape qui compte : elle doit rendre un écart maximal nul à la
   précision machine ;
5. établit H1, H2, H3 et H4 ;
6. écrit les figures dans `memoire/figures/` et les tableaux dans
   `memoire/tableaux/`.

Sorties attendues : les 5 figures et les 10 tableaux du mémoire, identiques à ceux
versionnés.

### Variante Python

```bash
pip install matplotlib pandas openpyxl python-docx
PYTHONPATH=src python analyse/verifier-mesure-independamment.py   # recalcule l'écart sans importer src/moteur
PYTHONPATH=src python analyse/h4.py                               # H4 → memoire/h4-mesures.md
PYTHONPATH=src python analyse/figures.py                          # figures
python analyse/rendre-tableaux-xlsx.py                            # tableaux → memoire/tableaux-partie3.xlsx
```

`verifier-mesure-independamment.py` est le contrôle le plus court : il recalcule
l'écart d'exploitation **sans importer `src/moteur`** et le confronte aux chiffres
publiés. Résultat attendu : 138 séries vérifiées, écart maximal de l'ordre de
10⁻¹⁶.

---

## Niveau 2 — Vérifier le dispositif

```bash
python -m pytest -q
```

225 tests, aucune dépendance, **aucun appel API**. Ils couvrent notamment un
oracle analytique du moteur (T1–T9), le gel de la mémoire intra-série, le canari
d'isolation des magasins, l'appariement des distributions et l'intégrité de
clôture.

Un test tient lieu de preuve pour la constante d'équilibre contestée :
`exploitability(GTO) = 0` est vérifié en arithmétique exacte pour toute la famille
α ∈ [0, 1/3], ce qui établit que le jeu admet une famille d'équilibres et que le
protocole en retient le membre α = 1/3.

### Rejouer une exécution depuis ses seuls journaux

Si vous disposez des journaux bruts (hors dépôt, 401 Mo) :

```bash
PYTHONPATH=src python -m journal.rejouer <dossier>/logs      # complétude
PYTHONPATH=src python -m journal.derives <racine> --sortie <dossier csv>
```

`rejouer` reconstitue chaque manche à partir des seules lignes écrites et retrouve
les mesures publiées. C'est ce contrôle qui a rendu 24/24 sur la campagne.

---

## Niveau 3 — Relancer la collecte

Ce niveau consomme des appels API payants. Il n'est **pas nécessaire** pour
vérifier les résultats : les niveaux 1 et 2 le font depuis les données déposées.

### Ce qu'il faut en plus

- **Hermès Agent** (Nous Research) installé et authentifié, avec un solde
  suffisant sur le portail Nous. La campagne complète a coûté 47,27 $ sur
  `openai/gpt-5.6-luna`.
- Un répertoire de travail **hors OneDrive** (par exemple `C:\arene-runs`) : la
  synchronisation corrompt les magasins mémoire en cours d'écriture.

### Une exécution

```bash
PYTHONPATH=src python -m arbitre --condition AE --bot Station --K 150 --series 10
```

Paramètres de campagne : `K = 150` manches par série, `--reasoning medium`,
3 réplications par cellule, plateau déclaré à 10 séries.

### La campagne complète

```powershell
scripts/lancer-campagne.ps1
```

**Décaler les lancements de 30 secondes** entre exécutions parallèles : le canari
d'isolation de chaque exécution doit voir les magasins déjà créés pour que le
contrôle soit *a priori* plutôt qu'*a posteriori*.

Trois exécutions de front tiennent en 36 à 56 heures ; cinq de front, en 22 à 33.

### Pièges vérifiés sur machine

Le détail est dans [`docs/CONTEXT.md`](docs/CONTEXT.md). Les trois qui menacent la
validité :

1. **Hermès lit les fichiers de consignes du répertoire courant** (`CLAUDE.md`,
   `AGENTS.md`, `.cursorrules`) et les verse dans son prompt système. Lancé depuis
   ce dépôt, l'agent recevait à chaque manche un document qui nomme le jeu et
   décrit l'exploitation de chaque adversaire. Le sous-processus tourne désormais
   dans un répertoire neutre.
2. **Le chemin du magasin apparaît en clair dans le prompt système.** Un dossier
   nommé `AE-station-r1` sert donc le nom de l'adversaire à l'agent. Les
   répertoires d'exécution sont des codes opaques dérivés.
3. **Les jetons de rafraîchissement Nous sont à usage unique.** Cloner `auth.json`
   par magasin fait révoquer la session entière. Un magasin de jetons commun
   (`HERMES_SHARED_AUTH_DIR`) est partagé par les exécutions d'une même racine ;
   l'isolation mémoire n'en est pas affectée.

---

## Ce que vous devez retrouver

| Contrôle | Attendu |
|---|---|
| suite de tests | 225 verts |
| vérification indépendante de la mesure | écart ≤ 10⁻¹⁵ sur toutes les séries |
| rejeu de complétude | 24 / 24 |
| intégrité de clôture | 24 / 24 |
| actions imposées par défaut | 0 |
| H1, effet apparié SM → AE | +0,178 à +0,704 selon l'adversaire, 9 paires sur 9 |
| H2, référence récitée | exactement 7/9 et 1/9 |
| H3, effet apparié ICL − AE | +0,038 ± 0,015 (Station), +0,004 ± 0,006 (Over-folder) |
| H4, dégénérescence | 0 % sans mémoire, 56 % avec note écrite |

Si un de ces chiffres diffère, l'écart est un résultat en soi : signalez-le en
ouvrant une issue, avec la commande exécutée et sa sortie.
