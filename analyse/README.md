# analyse/ — scripts d'exploitation des données

Ces scripts ne produisent aucune donnée : ils **dérivent** ce qui existe déjà dans
les journaux. Tout ce qu'ils écrivent est régénérable et jetable ; la source de
vérité reste les JSONL sous `C:\arene-runs`, et les fichiers versionnés de
`donnees/`.

| Script | Ce qu'il fait |
|---|---|
| `exporter-decisions.py` | journaux de tours → `donnees/decisions.csv` (une ligne par décision, sans le prompt servi, qui pèse 55 fois le reste et se reconstruit depuis les gabarits) |
| `exporter-runs.py` | états et rapports d'intégrité → `donnees/runs.csv` (une ligne par exécution : paramètres, graine, canari, verdicts, budget) |
| `exporter-notes.py` | `sessions.jsonl` → `donnees/notes-ae.md` (les 90 notes intégrales de l'agent, avec l'écart de leur série) |
| `dimensionnement-icl.py` | recalcule la dispersion des différences appariées et la différence minimale détectable — le raisonnement du §2.2.7 du chapitre de méthode, rejouable plutôt que cru sur parole |
| `extraire-donnees-pages.py` | `donnees/sessions.csv` → le JSON qu'utilisent les deux pages |
| `rendre-methodologie.py`, `rendre-resultats.py` | mettent en page les documents du mémoire ; le Markdown du dépôt reste la source |

Les CSV de mesure eux-mêmes (`sessions.csv`, `infosets.csv`, `memoire.csv`) ne
sont pas produits ici mais par le dispositif :

```bash
PYTHONPATH=src python -m journal.derives C:/arene-runs --sortie C:/arene-runs/csv
```

## Ce qui reste à écrire — H4

Deux mesures automatiques, sur données déjà déposées :

1. **Incohérence raisonnement↔action.** Comparer l'action de la ligne `ACTION:` à
   la dernière action nommée dans le texte libre qui la précède ; la logique existe
   dans `harnais.parsing`. Porte sur les **13 466 décisions (49,3 %)** qui
   comportent un texte au-delà de la ligne d'action. ⚠️ Le sous-ensemble n'est pas
   aléatoire — 28 % en SM, 36 % en ICL, 64 % en AE — et le taux obtenu est une
   borne inférieure sur un échantillon sélectionné.
2. **Dégénérescence des mixtes.** Concentration de `p` aux bornes, depuis
   `donnees/infosets.csv`. ⚠️ **Ventiler par adversaire** : contre Station et
   Over-folder la meilleure réponse *est* pure, y être n'est pas un biais. Le signal
   est contre GTO, où l'équilibre exige du mixte.
