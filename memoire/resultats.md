# Résultats de la campagne

*Campagne des 22-24 août 2026, complète. Document central : les résultats, et
l'inventaire de toutes les données et de tous les documents du dispositif.*

**Ce document est le point d'entrée unique.** Les mesures sont ci-dessous ; les
fichiers de données sont dans `donnees/` (§5) ; les documents de conception et de
méthode sont recensés en §6. Rien d'essentiel ne vit ailleurs — hormis les
journaux bruts complets, dont la taille interdit le versionnement (§5.3).

> **Versions consultables en ligne** (privées, partageables depuis leur menu) :
> [chapitre de méthode](https://claude.ai/code/artifact/9c6cc820-7c44-4eac-a360-a69450d35ef5) ·
> [résultats et courbes d'adaptation](https://claude.ai/code/artifact/40a26434-ed5f-4640-a651-d0cde8964a0b).
> Elles sont générées depuis les Markdown de ce dépôt par `analyse/rendre-*.py` :
> le Markdown reste la source, la page n'en est que la mise en forme.

---

## 1. Ce qui a été joué

| | |
|---|---|
| Conditions | **SM** (sans mémoire), **ICL** (historique brut), **AE** (auto-écrite) |
| Adversaires | GTO, Station, Over-folder — ICL sur Station et Over-folder seulement |
| Réplications | 3 par cellule |
| Exécutions | **24** — 9 SM × 3 séries, 9 AE × 10 séries, 6 ICL × 10 séries |
| Séries | **177** |
| Manches | **26 550** · décisions de l'agent : **27 290** |
| Modèle | `openai/gpt-5.6-luna`, effort `medium`, K = 150 |
| Graine de campagne | `arene-kuhn-2026` |
| Coût | **47,27 $** (13,01 pour SM+AE, 34,26 pour ICL) |

La condition ICL est restreinte à deux adversaires : contre GTO il n'y a aucune
information exploitable à retenir, donc rien que deux mécanismes de rétention
puissent conserver différemment. Le dimensionnement complet — et l'énoncé de la
part qui revient à la contrainte de coût — est au §2.2.7 du chapitre de méthode.

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

Contre GTO, sur les **39 séries** jouées (9 SM + 30 AE), la référence récitée n'est
**jamais positive** et l'écart **jamais négatif** : l'agent ne gagne jamais plus
que l'équilibre face à un adversaire à l'équilibre. Six séries atteignent
exactement zéro — l'agent y joue une meilleure réponse à l'équilibre, encaissant
exactement la valeur du jeu. Aucune ne dépasse. C'est la propriété qui devait être
vérifiée, et elle l'est.

⚠️ Les deux formulations ne sont pas deux verrous indépendants : contre GTO la
constante vaut 0, donc `récitée = −écart` (§3.1 de la partie III). Le §2.4 du
chapitre de méthode les présente comme distinctes — à corriger.

L'écart, lui, **décroît** contre GTO (0,161 → 0,008). Ce n'est pas un artefact de
mesure : la décroissance est absente en condition SM, sur les mêmes donnes et le
même calcul. Contre GTO il n'y a rien à exploiter — la mémoire n'y sert qu'à cesser
de commettre des erreurs, et l'écart baisse sans jamais se stabiliser à zéro,
contrairement aux deux adversaires exploitables.

> **Le chapitre de méthode a été corrigé sur ce point.** Sa formulation initiale
> tenait toute décroissance de l'écart contre GTO pour un défaut de mesure
> invalidant la campagne — critère qui, pris au mot, invalidait des résultats
> pourtant sains. Le contrôle négatif est désormais énoncé sur l'instrument qui le
> teste réellement : *la référence récitée ne devient jamais positive contre GTO*
> (§2.2.2 et §2.4 du chapitre). Cela tient sur les 39 séries jouées.

### 2.4 Le mécanisme de rétention — H3

La condition ICL reçoit **exactement la même matière** que AE — le récapitulatif
brut des séries passées — mais sans étape de synthèse : l'expérimentateur empile,
la fenêtre évince par séries entières, et aucun appel au modèle n'a lieu à la
frontière. Seul le mécanisme de rétention diffère.

| Adversaire | Répl. | ICL série 0 | ICL série 9 | ICL 4 dernières | AE 4 dernières | Différence |
|---|---|---|---|---|---|---|
| Over-folder | r1 | 0,715 | 0,000 | 0,0064 | 0,0000 | +0,0064 |
| Over-folder | r2 | 0,666 | 0,000 | 0,0021 | 0,0000 | +0,0021 |
| Over-folder | r3 | 0,722 | 0,012 | 0,0031 | 0,0000 | +0,0031 |
| Station | r1 | 0,147 | 0,024 | 0,0366 | 0,0025 | **+0,0341** |
| Station | r2 | 0,261 | 0,015 | 0,0388 | 0,0035 | **+0,0354** |
| Station | r3 | 0,197 | 0,033 | 0,0461 | 0,0012 | **+0,0449** |

Effets appariés, sur la moyenne des quatre dernières séries — plus robuste qu'un
point terminal isolé :

| Adversaire | Effet ICL − AE | Écart-type | IC 95 % | Conclusion |
|---|---|---|---|---|
| **Station** | **+0,0381** | 0,0059 | ± 0,0148 | l'intervalle exclut zéro : **AE l'emporte** |
| Over-folder | +0,0039 | 0,0023 | ± 0,0056 | l'intervalle contient zéro : **indistinguable** |

**H3 est vérifiée, mais sous condition — et la condition est interprétable.** Le
mécanisme de rétention ne départage les deux mémoires que là où la tâche exige une
politique *différenciée selon la carte*. Contre Over-folder, la stratégie optimale
tient en une règle unique — engager quel que soit le sceau — et un historique brut
la maintient aussi bien qu'une note synthétisée : les deux conditions atteignent
l'exploitation parfaite et s'y tiennent. Contre Station, où il faut cesser de
bluffer *et* miser pour la valeur au seul sceau supérieur, la synthèse fait la
différence.

**Le mécanisme observé n'est pas celui qui était anticipé.** Le chapitre prévoyait
pour ICL un profil d'oubli en dents de scie, produit par l'éviction des séries
anciennes à la saturation de la fenêtre. Rien de tel n'apparaît : la fenêtre ne
produit aucun décrochage.

La vitesse ne les sépare pas non plus. **Les deux conditions chutent à la première
frontière**, dans les mêmes proportions (contre Station : 0,202 → 0,059 pour ICL,
0,226 → 0,000 pour AE). Ce qui les sépare est ce qui suit : AE **se verrouille sur
zéro** et l'y tient sur neuf séries, tandis qu'ICL **s'arrête à un résidu non nul**
— stagnation autour de 0,058, puis dérive lente et bruitée vers 0,040, sans jamais
atteindre zéro sur une seule des trente séries jouées.

La différence porte donc sur la **complétude** de ce qui est extrait, ni sur la
vitesse ni sur la rétention. Le détail par ensemble d'information le confirme :
contre Station, huit des douze info-sets sont des points d'indifférence exacts, et
la qualité de la politique ne se joue que sur quatre décisions — ne jamais bluffer
le sceau faible, toujours engager le sceau fort. Après dix séries, ICL bluffe
encore le sceau faible dans 7 à 9 % des cas et laisse passer 3 à 6 % de ses mises
de valeur ; AE a supprimé le second défaut entièrement et ramené le premier sous
le pour cent. Le résidu d'ICL se décompose en 64 % de bluffs résiduels et 36 % de
mises de valeur manquées.

L'explication tient à la forme de la politique optimale. Contre Over-folder, elle
tient en **une règle unique et positive** — engager quel que soit le sceau — que le
journal brut porte de façon transparente. Contre Station, elle demande **deux
règles, dont une négative**, et une distinction entre les sceaux. Cesser de faire
quelque chose est ce qu'un historique brut soutient mal : un bluff perdant y figure
comme une manche parmi cent cinquante, et rien ne rassemble ces occurrences en
interdiction. L'étape de synthèse fait précisément cela.

Une remarque de méthode : la dispersion inter-réplications des paires ICL−AE
(0,0059 sur Station) est **deux fois et demie plus faible** que celle des paires
SM−AE (0,0153) sur laquelle le dimensionnement avait été calibré. Les deux
conditions partageant tout sauf le mécanisme — même matière première, mêmes
distributions, même modèle —, leurs différences sont nettement moins bruitées. Le
plan à trois réplications était donc plus que suffisant, alors que le
dimensionnement le donnait pour tout juste adéquat (§2.2.7 du chapitre).

### 2.5 Le canal mémoire

Les notes tiennent en **une seule entrée** dans 84 cas sur 90 (deux dans les six
autres), de 333 à 1 906 caractères : **aucun dépassement**, deux élagages sur les
90 frontières. La contrainte de capacité n'a jamais mordu. Leur longueur suit la
difficulté du problème — 470 caractères en moyenne contre Over-folder, où il n'y a
qu'une régularité à énoncer ; 808 contre Station ; 1 337 contre GTO, où il faut
détailler sceau par sceau.

> « Il n'a jamais engagé ni couvert. Ouvrant, il a toujours retenu ; Répondant, il
> s'est toujours retiré face à notre engagement. Nos 150 engagements ont donc tous
> rapporté +1, sans coût ni révélation des sceaux. »
> — *AE-over-folder-r2, frontière de la série 9, écart 0,000*

**Le canal n'encode jamais une fréquence — et c'est le mécanisme de H4.** Sur les
90 notes et leurs 92 000 caractères : **0** pourcentage, **0** fraction écrite,
**0** proportion en toutes lettres (« un tiers », « une fois sur trois »), contre
**358** quantificateurs non chiffrés. Le mot « aléatoire » apparaît 4 fois, jamais
à propos de la stratégie de l'agent.

L'agent perçoit pourtant bien la différence entre un adversaire déterministe et un
adversaire mixte — son vocabulaire l'enregistre :

| Adversaire | Quantificateurs | Dont catégoriques (*toujours*, *jamais*, *systématiquement*) |
|---|---|---|
| Over-folder | 98 | **100 %** |
| Station | 94 | **100 %** |
| GTO | 166 | **17 %** |

Face à GTO il bascule vers un registre gradué (« très souvent », « parfois »). La
détection est acquise ; c'est l'encodage qui manque. Et un adverbe gradué ne
s'exécute pas comme une fréquence : la note tranche catégoriquement — « *éviter
d'engager avec Tor* », là où l'équilibre demande de le faire une fois sur trois.

**Deux imperfections, matière directe pour H4 :**

- **Inversion des rôles.** Une note sur les 30 écrites contre Over-folder décrit
  l'adversaire comme ayant « toujours engagé », alors que le bot n'a pas misé une
  seule fois (2 250 retenues en position d'Ouvrant, zéro engagement sur les
  4 500 manches AE) — tout en jouant la meilleure réponse exacte, écart 0,000. Le
  comportement est juste, son explication est fausse. Cette incohérence-là est
  **invisible à la mesure de H4**, qui compare le texte d'une décision à l'action
  de cette même décision, jamais la mémoire aux journaux.
- **Écrasement plutôt qu'accumulation.** 70 frontières sur 90 comportent une
  suppression. L'agent traite sa note antérieure comme une erreur à corriger
  (« remplace l'ancien −13 », puis « remplace l'ancien +5 ») et non comme le
  résultat d'une série passée. Il tient un état, pas un registre — ce qui suffit
  contre un adversaire stationnaire, et expliquerait mal une tâche non
  stationnaire.

Les 90 notes intégrales : `donnees/notes-ae.md`.

### 2.6 Les biais de décision — H4

Les deux mesures automatiques sont calculées ; le détail complet et sa
justification sont dans `memoire/h4-mesures.md`, régénérable par `analyse/h4.py`.

**Incohérence raisonnement↔action — la règle pré-enregistrée est invalide.**
Appliquée à la lettre (§2.2.5.3, « la dernière action nommée dans le texte
libre »), elle rend 47,8 % sur 13 442 décisions verbalisées — à un point des
45,1 % de GTBENCH, et entièrement artefactuel : le raisonnement français conclut
par une clause contrastive qui nomme l'option *rejetée* (« engager garantit +1,
**tandis que retenir** expose à une perte »). Huit divergences relues, huit faux
positifs. La variante à haute précision — ne compter que les décisions où l'agent
*énonce* son choix — donne **0 divergence sur 604**. L'agent ne se contredit
jamais explicitement. La chaîne de pensée n'étant pas restituée (§L.1), la mesure
ne voit qu'une partie du raisonnement.

**Dégénérescence des mixtes — la mémoire la produit.** Sur `J1/C0/ouverture`, où
l'équilibre exige un bluff au tiers, contre l'adversaire à l'équilibre (fréquences
estimées sur au moins 20 observations) :

| | Séries | Aux bornes 0 ou 1 | Distance moyenne à 1/3 |
|---|---|---|---|
| SM — sans mémoire | 9 | **0 %** | 0,078 |
| AE — première série, note encore vide | 3 | **0 %** | 0,113 |
| AE — séries suivantes, note écrite | 25 | **56 %** | 0,323 |

La deuxième ligne est un **contrôle interne** : la première série d'une exécution
AE se joue avec un emplacement mémoire présent mais vide — même modèle, même
gabarit, même exécution, même adversaire, seule la note manque. L'effondrement
apparaît exactement à la première série jouée avec une note écrite.

Et ce n'est pas un effondrement vers une borne unique : 13 séries à zéro, 1 à un,
**7 sauts de plus de 0,40** entre séries consécutives. L'agent remplace une
randomisation *intra-série* par une alternance *inter-séries* — il choisit une
règle, l'applique 150 manches, puis en change à la frontière. La variabilité a
migré vers une échelle de temps où elle ne produit aucune imprévisibilité.

**L'adaptation et le biais sont le même mécanisme.** Ce qui rend AE supérieure à
ICL (§2.4) — contraindre l'agent à formuler une règle — est ce qui la rend
incapable de randomiser. Une règle écrite est déterministe : elle dit « engager
avec le sceau fort », jamais « engager avec le sceau faible une fois sur trois ».

Deux réserves : le résultat repose sur un seul info-set (les trois autres info-sets
mixtes ne sont atteints que si l'adversaire mise — 1, 2 et 6 séries à effectif
suffisant), et le codage manuel sur échantillon stratifié n'a pas été conduit.

⚠️ Le chiffre de 58 % qui circulait dans les notes de travail agrégeait les trois
adversaires — il comptait comme dégénérées des politiques pures qui sont optimales
contre Station et Over-folder. Contre GTO seul, c'est **38 %**.

## 3. Contrôles de validité

| Contrôle | Résultat |
|---|---|
| Rejeu de complétude — chaque manche re-réglée depuis les seuls journaux | **24 / 24** |
| Intégrité de clôture — donnes, positions, appariement, isolation, complétude | **24 / 24** |
| Actions imposées par défaut | **0** sur 27 290 décisions |
| Relances de format · erreurs de harnais | **0** · **0** |
| Ruptures du gel intra-série | **0** sur 177 séries |
| Écritures mémoire pendant une série | **0** |
| Équilibre des positions Ouvrant / Répondant | 13 275 / 13 275 |
| Canari d'isolation réel (écriture confirmée, écriture bloquée en manche) | 24 / 24 |
| Reconnaissance du jeu source (covariable) | 113 signalements |
| Récitation d'équilibre (covariable) | 198 signalements |

## 4. Limites

- **GTO n'est pas joué en ICL**, par un arbitrage exposé au §2.2.7 du chapitre :
  l'argument est qu'il n'y a rien d'exploitable à retenir contre un adversaire sans
  faille, mais la question a été posée par le budget, et la vérification qu'ICL ne
  bat pas l'équilibre contre l'équilibre n'a donc pas été faite.
- **Trois réplications** par cellule : on rapporte des effets appariés et leurs
  intervalles, pas des tests d'hypothèse dont la puissance serait décorative.
- **Le plateau AE est atteint dès la série 2** dans la plupart des cellules ; les
  huit séries suivantes mesurent la *persistance*, pas la vitesse d'adaptation.
  La vitesse serait mieux résolue par des séries plus courtes — et c'est
  précisément sur elle que se joue la différence avec ICL (§2.4), qui reste donc
  moins bien résolue qu'elle ne pourrait l'être.
- **Le profil d'oubli d'ICL n'a pas été observé** : la fenêtre à trois séries n'a
  pas produit de décrochage à la saturation. On ne peut pas conclure qu'elle n'en
  produit jamais — seulement qu'à cet horizon, sur ces adversaires, elle n'en a pas
  produit. Un horizon plus long ou une fenêtre plus étroite reste à explorer.
- **Le raisonnement n'est observable qu'en partie** : l'essentiel des tokens de
  sortie est de la chaîne de pensée facturée mais jamais restituée (cf. §L.1 du
  chapitre de méthode).

## 5. Les données — `donnees/`

### 5.1 Fichiers versionnés

| Fichier | Lignes | Taille | Contenu |
|---|---|---|---|
| `sessions.csv` | 177 | 26 Ko | **Une ligne par série.** Le fichier d'analyse principal : écart, référence récitée, EV, défauts, drapeaux, plateau, coûts. |
| `decisions.csv` | 27 290 | 7,3 Mo | **Une ligne par décision.** État réel, info-set, action, parsing, résultat, tokens, latence, coût, et le texte intégral produit par le modèle. |
| `infosets.csv` | 1 261 | 75 Ko | **Une ligne par série × info-set.** Fréquence `p` et effectif `n` — comment la politique se déplace, info-set par info-set. |
| `memoire.csv` | 90 | 5 Ko | **Une ligne par frontière AE.** Tailles, entrées ±, élagages, saturations. La condition ICL n'écrit pas : sa mémoire est le récapitulatif, conservé dans `sessions.csv`. |
| `runs.csv` | 24 | 6 Ko | **Une ligne par exécution.** Paramètres, graine, canari, verdicts d'intégrité, agrégats, budget, horodatages. |
| `notes-ae.md` | 90 notes | 94 Ko | **Contenu intégral de `MEMORY.md`** à chaque frontière, avec l'écart de la série correspondante. |

### 5.2 Correspondance avec les répertoires d'exécution

Les répertoires portent un **code opaque** (`run-<empreinte>`) et non le nom de la
cellule : leur chemin est servi à l'agent par le prompt système de l'outil, et un
répertoire nommé `AE-over-folder-r2` lui livrerait le nom — donc la faille — de son
adversaire (constat C1 de l'audit). La colonne `dossier` de `runs.csv` donne la
correspondance.

### 5.3 Journaux bruts — non versionnés

`C:\arene-runs\run-<code>\logs\` : `turns.jsonl` (**401 Mo**), `sessions.jsonl`
(8,1 Mo), `integrite.json`, plus `etat_run.json` à la racine du run.

`decisions.csv` en est l'export intégral **moins le prompt servi** (`vue_servie`),
et le rapport est de 55 pour 1 : 7,3 Mo contre 401. La condition ICL explique
l'essentiel du volume — à fenêtre pleine, son prompt atteint 51 000 caractères,
répétés à chacune des 1 500 manches d'une exécution. Ce prompt est identique d'une
manche à l'autre à l'état de l'épreuve près, et reconstructible depuis les
gabarits ; tout le reste est conservé, y compris le texte intégral produit par le
modèle.

Les JSONL restent la **source de vérité** : c'est sur eux que tourne le rejeu de
complétude, et c'est d'eux que tous les CSV sont dérivés — régénérables à tout
moment par `python -m journal.derives C:/arene-runs --sortie C:/arene-runs/csv`.

## 6. Les documents

| Document | Rôle |
|---|---|
| `memoire/methodologie.md` | **Chapitre 2 du mémoire** : hypothèses, protocole, instruments, validité interne. Autorité sur ce qui est mesuré et pourquoi. |
| `memoire/resultats.md` | Ce document. |
| `Mémoire Videt Léo.docx` | **Le mémoire remis** (racine du dépôt), terminé le 2026-08-30 : trois chapitres, conclusion, bibliographie, 14 tableaux, 4 figures. |
| `memoire/introduction.md`, `memoire/conclusion.md`, `memoire/partie1-conclusion.md` | Introduction, conclusion et § 1.3.5, en source. |
| `memoire/partie3-v2.md` | **Chapitre III du mémoire**, rédigé, dans la version restructurée du 27 août. |
| `memoire/partie3-plan-v2.md` | Plan du chapitre III et décisions d'exposition. La première rédaction et son plan sont dans `memoire/archive/`. |
| `memoire/h4-mesures.md` | **Les deux mesures automatiques de H4**, générées par `analyse/h4.py` : incohérence raisonnement↔action (et l'invalidité de la règle pré-enregistrée), dégénérescence des mixtes. |
| `memoire/figures/` | Les 5 figures, générées par `analyse/R/analyse.R`. |
| `memoire/tableaux/`, `memoire/tableaux-partie3.xlsx` | Les 10 tableaux en CSV et leur mise en forme Excel. |
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
powershell -File scripts/lancer-campagne.ps1                          # SM + AE
powershell -File scripts/lancer-campagne.ps1 -Conditions ICL -Bots Station,Over-folder

# Vérifier un run depuis ses seuls journaux
PYTHONPATH=src python -m journal.rejouer C:/arene-runs/run-<code>/logs

# Régénérer les CSV
PYTHONPATH=src python -m journal.derives C:/arene-runs --sortie C:/arene-runs/csv
```

Les donnes sont **dérivées** de `(graine, réplication, série, manche)` : à graine
identique, la campagne rejoue les mêmes cartes, manche pour manche.

## 8. Suite

**Le travail est terminé.** La collecte est close, l'analyse est close, le mémoire
est rédigé et mis en forme (`Mémoire Videt Léo.docx`, 2026-08-30). Aucune
exécution supplémentaire n'est requise, et rien n'attend d'être écrit.

Ce qui suit relève d'un autre protocole, et a été écarté du périmètre :

1. **Le codage manuel du raisonnement** sur échantillon stratifié — il préciserait
   le taux d'incohérence de H4 sur les décisions que la mesure automatique ne
   couvre pas ; il ne change aucun résultat acquis.
2. **La vitesse d'adaptation**, qui est ce qui sépare AE d'ICL (§2.4) et que le
   plan actuel résout mal : le plateau AE est atteint dès la deuxième série. Des
   séries plus courtes la mesureraient mieux, à coût comparable.
3. **Le profil d'oubli d'ICL**, jamais observé à cet horizon. Une fenêtre plus
   étroite ou un horizon plus long dirait s'il existe ou si la réinjection d'un
   historique brut se contente d'être plus lente, sans jamais oublier.
