# Résultats — tranche SM et AE

*Campagne du 22 août 2026. Document central : les résultats, et l'inventaire de
toutes les données et de tous les documents du dispositif.*

**Ce document est le point d'entrée unique.** Les mesures sont ci-dessous ; les
fichiers de données sont dans `donnees/` (§5) ; les documents de conception et de
méthode sont recensés en §6. Rien d'essentiel ne vit ailleurs — hormis les
journaux bruts complets, dont la taille interdit le versionnement (§5.3).

---

## 1. Ce qui a été joué

| | |
|---|---|
| Conditions | **SM** (sans mémoire) et **AE** (mémoire auto-écrite) |
| Adversaires | GTO, Station, Over-folder |
| Réplications | 3 par cellule |
| Exécutions | **18** (9 SM × 3 séries, 9 AE × 10 séries) |
| Séries | **117** |
| Manches | **17 550** · décisions de l'agent : **18 290** |
| Modèle | `openai/gpt-5.6-luna`, effort `medium`, K = 150 |
| Graine de campagne | `arene-kuhn-2026` |
| Coût | **13,01 $** |

La condition **ICL** n'est pas jouée : elle constitue la tranche suivante et porte
l'hypothèse H3.

## 2. Résultats

### 2.1 Écart d'exploitation — H1

L'écart est ce que l'agent laisse sur la table à chaque manche, faute d'exploiter
parfaitement son adversaire. Zéro signifie exploitation optimale.

| Adversaire | Répl. | SM (séries 0-2) | AE série 0 | AE série 9 |
|---|---|---|---|---|
| Over-folder | r1 | 0,702 · 0,675 · 0,687 | 0,776 | **0,000** |
| Over-folder | r2 | 0,731 · 0,725 · 0,665 | 0,582 | **0,000** |
| Over-folder | r3 | 0,679 · 0,744 · 0,727 | 0,803 | **0,000** |
| Station | r1 | 0,189 · 0,248 · 0,264 | 0,251 | 0,005 |
| Station | r2 | 0,175 · 0,248 · 0,199 | 0,222 | **0,000** |
| Station | r3 | 0,224 · 0,243 · 0,204 | 0,204 | **0,000** |
| GTO | r1 | 0,169 · 0,158 · 0,186 | 0,181 | 0,015 |
| GTO | r2 | 0,149 · 0,220 · 0,215 | 0,180 | **0,000** |
| GTO | r3 | 0,197 · 0,197 · 0,189 | 0,122 | 0,010 |

Effet apparié — écart final AE contre moyenne SM, à donnes identiques :

| Adversaire | SM | AE | Réduction | Par réplication |
|---|---|---|---|---|
| Over-folder | 0,704 | 0,000 | **+0,704** | +0,688 · +0,707 · +0,717 |
| Station | 0,222 | 0,002 | **+0,220** | +0,229 · +0,207 · +0,224 |
| GTO | 0,187 | 0,008 | +0,178 | +0,156 · +0,195 · +0,184 |

Les neuf paires vont dans le même sens, avec une dispersion inter-réplications de
l'ordre du centième. La ligne sans mémoire ne décroît jamais.

### 2.2 Référence récitée — H2

Distance au comportement d'un agent qui appliquerait l'équilibre. Un récitant y
reste à zéro quel que soit l'adversaire ; un exploiteur s'en écarte positivement,
et son maximum est connu d'avance.

| Adversaire | SM | AE (séries 7-9) | Maximum théorique |
|---|---|---|---|
| Over-folder | +0,074 | **+0,778** | +0,778 (7/9) |
| Station | −0,111 | **+0,110** | +0,111 (1/9) |
| GTO | −0,187 | −0,024 | 0 (plafond) |

Contre les deux adversaires exploitables, l'agent à mémoire atteint **exactement la
valeur maximale de l'exploitation**. Il ne récite pas l'équilibre : il s'en écarte
dans la direction que chaque adversaire commande, et jusqu'à l'optimum. Sans
mémoire, il est *en dessous* de l'équilibre contre Station et contre GTO.

### 2.3 Le contrôle négatif

Contre GTO, la référence récitée reste négative sur les trente séries : l'agent ne
gagne jamais plus que l'équilibre face à un adversaire à l'équilibre. C'est la
propriété qui devait être vérifiée, et elle l'est.

L'écart, lui, **décroît** contre GTO (0,161 → 0,008). Ce n'est pas un artefact de
mesure : la décroissance est absente en condition SM, sur les mêmes donnes et le
même calcul. Contre GTO il n'y a rien à exploiter — la mémoire n'y sert qu'à cesser
de commettre des erreurs, et l'écart baisse sans jamais se stabiliser à zéro,
contrairement aux deux adversaires exploitables.

> **Le chapitre de méthode a été corrigé sur ce point.** Sa formulation initiale
> tenait toute décroissance de l'écart contre GTO pour un défaut de mesure
> invalidant la campagne — critère qui, pris au mot, invalidait des résultats
> pourtant sains. Le contrôle négatif est désormais énoncé sur l'instrument qui le
> teste réellement : *la référence récitée ne devient jamais positive contre GTO, et
> l'écart n'y devient jamais négatif* (§2.2.2 et §2.4 du chapitre). Les deux
> tiennent sur les trente séries jouées.

### 2.4 Le canal mémoire

Les notes tiennent en **une seule entrée**, de 377 à 1 561 caractères : jamais de
saturation, jamais d'élagage destructeur sur les 90 frontières. Leur longueur suit
la difficulté du problème — 380 caractères contre Over-folder, où il n'y a qu'une
régularité à énoncer ; 1 500 contre GTO, où il faut détailler carte par carte.

> « Il n'a jamais engagé ni couvert. Ouvrant, il a toujours retenu ; Répondant, il
> s'est toujours retiré face à notre engagement. Nos 150 engagements ont donc tous
> rapporté +1, sans coût ni révélation des sceaux. »
> — *AE-over-folder-r2, frontière de la série 9, écart 0,000*

Deux imperfections, matière directe pour H4 :

- **Inversion des rôles.** Un run sur trois contre Over-folder décrit l'adversaire
  comme ayant « toujours engagé », alors que le bot n'a jamais misé (795 `check`,
  1 400 `fold`, zéro `bet` dans les journaux) — tout en jouant la stratégie
  optimale. Le comportement est juste, son explication est fausse.
- **Écrasement plutôt qu'accumulation.** L'agent traite systématiquement sa note
  antérieure comme une erreur à corriger (« remplace l'ancien −13 ») et non comme
  le résultat d'une série passée.

Les 90 notes intégrales : `donnees/notes-ae.md`.

## 3. Contrôles de validité

| Contrôle | Résultat |
|---|---|
| Rejeu de complétude — chaque manche re-réglée depuis les seuls journaux | **18 / 18** |
| Intégrité de clôture — donnes, positions, appariement, isolation, complétude | **18 / 18** |
| Actions imposées par défaut | **0** sur 18 290 décisions |
| Relances de format · erreurs de harnais | **0** · **0** |
| Ruptures du gel intra-série | **0** sur 117 séries |
| Écritures mémoire pendant une série | **0** |
| Équilibre des positions Ouvrant / Répondant | 8 775 / 8 775 |
| Canari d'isolation réel (écriture confirmée, écriture bloquée en manche) | 18 / 18 |
| Reconnaissance du jeu source (covariable) | 96 signalements |
| Récitation d'équilibre (covariable) | 158 signalements |

## 4. Limites de cette tranche

- **ICL manque**, donc H3 n'est pas testée. Les résultats ci-dessus établissent
  qu'il y a adaptation (H1) et qu'elle est exploitative (H2), pas que la mémoire
  auto-écrite fasse mieux que la réinjection d'historique brut.
- **Trois réplications** par cellule : on rapporte des effets appariés, pas des
  tests d'hypothèse dont la puissance serait décorative.
- **Le plateau AE est atteint dès la série 2** dans la plupart des cellules ; les
  huit séries suivantes mesurent la *persistance*, pas la vitesse d'adaptation.
  La vitesse serait mieux résolue par des séries plus courtes.
- **Le raisonnement n'est observable qu'en partie** : l'essentiel des tokens de
  sortie est de la chaîne de pensée facturée mais jamais restituée (cf. §L.1 du
  chapitre de méthode).

## 5. Les données — `donnees/`

### 5.1 Fichiers versionnés

| Fichier | Lignes | Taille | Contenu |
|---|---|---|---|
| `sessions.csv` | 117 | 17 Ko | **Une ligne par série.** Le fichier d'analyse principal : écart, référence récitée, EV, défauts, drapeaux, plateau, coûts. |
| `decisions.csv` | 18 290 | 5,0 Mo | **Une ligne par décision.** État réel, info-set, action, parsing, résultat, tokens, latence, coût, et le texte intégral produit par le modèle. |
| `infosets.csv` | 901 | 51 Ko | **Une ligne par série × info-set.** Fréquence `p` et effectif `n` — comment la politique se déplace, info-set par info-set. |
| `memoire.csv` | 90 | 5 Ko | **Une ligne par frontière AE.** Tailles, entrées ±, élagages, saturations. |
| `runs.csv` | 18 | 4 Ko | **Une ligne par exécution.** Paramètres, graine, canari, verdicts d'intégrité, agrégats, budget, horodatages. |
| `notes-ae.md` | 90 notes | 94 Ko | **Contenu intégral de `MEMORY.md`** à chaque frontière, avec l'écart de la série correspondante. |

### 5.2 Correspondance avec les répertoires d'exécution

Les répertoires portent un **code opaque** (`run-<empreinte>`) et non le nom de la
cellule : leur chemin est servi à l'agent par le prompt système de l'outil, et un
répertoire nommé `AE-over-folder-r2` lui livrerait le nom — donc la faille — de son
adversaire (constat C1 de l'audit). La colonne `dossier` de `runs.csv` donne la
correspondance.

### 5.3 Journaux bruts — non versionnés

`C:\arene-runs\run-<code>\logs\` : `turns.jsonl` (**65 Mo**), `sessions.jsonl`
(2,6 Mo), `integrite.json`, plus `etat_run.json` à la racine du run.

`decisions.csv` en est l'export intégral **moins le prompt servi** (`vue_servie`),
qui représente environ 60 % du volume : il est identique d'une manche à l'autre à
l'état près, et reconstructible depuis les gabarits. Tout le reste est conservé, y
compris le texte intégral produit par le modèle.

Les JSONL restent la **source de vérité** : c'est sur eux que tourne le rejeu de
complétude, et c'est d'eux que tous les CSV sont dérivés — régénérables à tout
moment par `python -m journal.derives C:/arene-runs --sortie C:/arene-runs/csv`.

## 6. Les documents

| Document | Rôle |
|---|---|
| `memoire/methodologie.md` | **Chapitre 2 du mémoire** : hypothèses, protocole, instruments, validité interne. Autorité sur ce qui est mesuré et pourquoi. |
| `memoire/resultats.md` | Ce document. |
| `donnees/notes-ae.md` | Les 90 notes de l'agent, données qualitatives brutes. |
| `spec-build-arene-kuhn(1).md` | Spécification d'origine — autorité sur *quoi* construire. |
| `prd/00-vue-densemble.md` … `prd/04-logging-analyse.md` | Conception — autorité sur *comment*. Décisions transverses D1–D8, oracle analytique, schémas. |
| `CONTEXT.md` | Contexte vivant : découvertes d'environnement, pièges n°1 à n°10, décisions de discussion, calibrage, enveloppes recalculées. |
| `AUDIT.md` | Cahier des charges de l'audit adversarial pré-campagne. |
| `PROGRESS.md` | État d'avancement phase par phase. |
| `CLAUDE.md` | Consignes de travail sur le dépôt. |
| `README.md` | Présentation du dépôt. |

## 7. Reproduire

```bash
# Un run
PYTHONPATH=src python -m arbitre --condition AE --bot Station --K 150 \
    --modele openai/gpt-5.6-luna --racine C:/arene-runs \
    --home-source C:/Users/<vous>/AppData/Local/hermes

# Une tranche complète (pool de 3, décalage 30 s)
powershell -File scripts/lancer-campagne.ps1

# Vérifier un run depuis ses seuls journaux
PYTHONPATH=src python -m journal.rejouer C:/arene-runs/run-<code>/logs

# Régénérer les CSV
PYTHONPATH=src python -m journal.derives C:/arene-runs --sortie C:/arene-runs/csv
```

Les donnes sont **dérivées** de `(graine, réplication, série, manche)` : à graine
identique, la campagne rejoue les mêmes cartes, manche pour manche.

## 8. Suite

1. **Jouer la tranche ICL** — 9 exécutions, ~62 $ aux prix mesurés, seule voie vers
   H3.
2. **H4** — le taux d'incohérence raisonnement↔action reste à coder sur
   `decisions.csv` (la colonne `sortie_brute` porte le texte nécessaire), et
   l'inversion des rôles relevée en §2.4 en est un premier cas documenté.
