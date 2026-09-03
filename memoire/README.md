# memoire/ — le mémoire et ses pièces

Le document remis est le `.docx`. Le Markdown de ce dossier est la **source** des
chapitres rédigés avec assistance : il sert à régénérer les figures, les tableaux
et les exports, et à retrouver l'origine de chaque chiffre.

## Le document

Le mémoire est **terminé** (2026-08-30). Les `.docx` vivent à la racine du dépôt :

| Fichier | |
|---|---|
| [`../Mémoire Videt Léo.docx`](../Mémoire%20Videt%20L%C3%A9o.docx) | **le mémoire remis** — trois chapitres, conclusion, bibliographie, 14 tableaux, 4 figures |
| `../Master Industries de Réseau et Economie Numérique - restructure.docx` | état du 29 août, avant la mise en forme finale |
| `../Master Industries de Réseau et Economie Numérique.docx` | version antérieure à la restructuration, conservée comme référence |

## Les chapitres, en source

| Fichier | Correspond à |
|---|---|
| `introduction.md` | l'introduction |
| `partie1-conclusion.md` | § 1.3.5, le positionnement de la recherche |
| `methodologie.md` | le chapitre II |
| `partie3-v2.md` | le chapitre III, dans la version restructurée |
| `partie3-plan-v2.md` | le plan du chapitre III et les décisions d'exposition |
| `conclusion.md` | la conclusion |
| `resultats.md` | **les résultats et l'inventaire complet des données et documents** |
| `h4-mesures.md` | le rapport détaillé de H4, produit par `analyse/h4.py` |

## Les pièces

| | |
|---|---|
| `figures/` | les 5 figures, produites par `analyse/R/analyse.R` |
| `tableaux/` | les 10 tableaux en CSV, produits par le même script |
| `tableaux-partie3.xlsx` | les mêmes tableaux mis en forme, un onglet chacun |

Figures et tableaux sont **régénérables** : voir [`../REPLICATION.md`](../REPLICATION.md).

## `archive/`

Versions dépassées, conservées pour la traçabilité : la première rédaction de la
partie III et son plan, remplacés le 27 août 2026 par une restructuration de
l'exposition qui ne change aucun résultat.
