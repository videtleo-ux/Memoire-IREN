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
| `verifier-mesure-independamment.py` | **recalcule l'écart d'exploitation sans importer `src/moteur`** et le confronte aux chiffres publiés — 138 séries, écart maximal 1,4·10⁻¹⁶. Referme l'angle mort n°3 du brief d'audit : l'oracle et le moteur avaient la même main, ce script leur en donne deux |
| `suivre-campagne.py` | suivi d'une campagne en cours : runs terminés, erreurs, seuils de budget |
| `extraire-donnees-pages.py` | `donnees/sessions.csv` → le JSON qu'utilisent les deux pages |
| `rendre-methodologie.py`, `rendre-resultats.py` | mettent en page les documents du mémoire ; le Markdown du dépôt reste la source |

Les CSV de mesure eux-mêmes (`sessions.csv`, `infosets.csv`, `memoire.csv`) ne
sont pas produits ici mais par le dispositif :

```bash
PYTHONPATH=src python -m journal.derives C:/arene-runs --sortie C:/arene-runs/csv
```

## H4 — mesuré, `h4.py`

Les deux mesures automatiques ont été produites et versées au mémoire
(`memoire/h4-mesures.md`) :

1. **Incohérence raisonnement↔action.** L'action de la ligne `ACTION:` comparée à
   la dernière action nommée dans le texte libre qui la précède. La règle
   pré-enregistrée s'est révélée **invalide** (47,8 % d'appariements artefactuels,
   huit faux positifs sur huit relus) ; elle a été resserrée aux décisions où
   l'agent énonce son choix en toutes lettres — 604 décisions, aucune divergence.
   La portée est étroite et énoncée comme telle : 2,2 % de la campagne, sur un
   sous-ensemble sélectionné.
2. **Dégénérescence des mixtes**, depuis `donnees/infosets.csv`, ventilée par
   adversaire — contre Station et Over-folder la meilleure réponse *est* pure, le
   signal est contre GTO. Résultat : 0 % de séries aux bornes sans mémoire, 56 %
   dès qu'une note est écrite, avec un contrôle interne (la série 0 d'une
   exécution AE, note encore vide, n'y est pas).

Le codage manuel sur échantillon stratifié a été écarté du périmètre.
