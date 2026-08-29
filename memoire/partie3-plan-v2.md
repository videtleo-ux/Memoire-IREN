# Partie III — plan v2

*Arrêté le 2026-08-27, en révision du plan initial (`partie3-plan.md`) et du texte
rédigé (`partie3.md`, 7 707 mots). Aucun résultat n'est modifié : c'est une
restructuration de l'exposition.*

## Les trois problèmes que ce plan corrige

**1. L'instrument n'est jamais démonté.** Le §3.1 donne les formules, jamais le
calcul. Le lecteur arrive au §3.2 sans savoir d'où sort un seul chiffre, et doit
faire crédit pendant tout le chapitre. L'unité elle-même — le jeton par manche —
n'est pas expliquée.

**2. Treize tableaux, deux figures.** Le rapport est inversé. Un tableau de neuf
lignes de décimales ne se lit pas. La figure des trajectoires porte H1 et H3 en
un coup d'œil.

**3. Le §3.4 a sept sous-sections, et le §3.6.1 est le plus long bloc du
chapitre** (696 mots, 9,0 %) pour un résultat nul sur un instrument invalide,
tandis que le résultat central de H4 en occupe 612.

## Pièces retenues — 5 figures, 10 tableaux

Les tableaux bruts par réplication passent en annexe : ils servent la
vérifiabilité, pas la lecture.

| | Pièce | Section | Existe ? |
|---|---|---|---|
| T1 | Une série, décomposée du comptage à l'écart | 3.1 | **à produire** |
| T2 | L'échelle de lecture par adversaire | 3.1 | **à produire** |
| F1 | Trajectoires de l'écart — 3 panneaux, 3 conditions | 3.2 | ✅ `fig1` |
| T3 | Effet apparié SM → AE | 3.2 | ✅ |
| F2 | Fréquence de bluff avec la carte faible, par adversaire | 3.3 | **à produire** |
| T4 | Référence récitée : SM, AE, maximum théorique, % atteint | 3.3 | ✅ |
| F3 | Référence récitée par série, avec plafond | 3.3 | ✅ `fig2` |
| T5 | Effet apparié ICL − AE, écart-type, intervalle | 3.4 | ✅ |
| T6 | Les quatre décisions qui comptent contre Station, ICL vs AE | 3.4 | **à produire** |
| F4 | Zoom sur les trajectoires, séries 1-9, échelle resserrée | 3.4 | **à produire** |
| T7 | Vocabulaire des notes par adversaire | 3.5 | ✅ |
| F5 | Nuage de la dégénérescence — 3 groupes, ligne à 1/3 | 3.6 | ✅ `fig3` |
| T8 | Dégénérescence chiffrée | 3.6 | ✅ |
| T9 | Incohérence, deux variantes | annexe | ✅ |
| T10 | Les quatre hypothèses, récapitulatif | 3.7 | **à produire** |

Production : `analyse/R/analyse.R` calcule tout et exporte les figures en PNG et
les tableaux en CSV, à mettre en forme dans Excel puis à coller dans Word comme
vraies tables. Le passage par le CSV supprime le problème des tableaux Markdown
collés bruts dans le `.docx` (audit du 2026-08-26).

---

## §3.1 — L'instrument, démonté sur une série

**Objectif.** Rendre chaque chiffre du chapitre vérifiable par le lecteur. À la
fin de cette section, il doit pouvoir ouvrir `decisions.csv`, prendre n'importe
quelle série et refaire le calcul.

**Déroulé.**

1. *L'unité.* Le jeu se compte en jetons ; chaque manche en engage un d'office,
   plus un éventuel engagement. Toutes les mesures sont en **jetons par manche**,
   et se traduisent en jetons par série en multipliant par 150.
2. *De 150 manches à six nombres.* Contre un adversaire qui n'engage jamais,
   l'agent n'a qu'une décision par manche, et sa situation se résume à sa
   position et à son jeton. Six situations, six fréquences. **[T1]**
3. *De six nombres à une espérance.* Le raisonnement jeton par jeton contre
   Station : le jeton fort gagne à coup sûr, donc engager rapporte 1 de plus ; le
   jeton faible perd à coup sûr, donc engager coûte 1 de plus ; le jeton moyen
   gagne une fois sur deux, donc engager ne change rien. D'où la forme close :
   `EV = (fréquence jeton fort − fréquence jeton faible) / 6`, sommée sur les
   deux positions.
4. *L'écart.* Le plafond est 1/3 contre Station. L'écart est la soustraction. Sur
   la série servant d'exemple : 0,3333 − 0,0819 = **0,2515**, soit 38 jetons
   laissés sur 150 manches.
5. *Le second instrument.* Le récité est la même espérance, mesurée depuis
   l'équilibre au lieu du plafond.
6. *L'échelle de lecture.* **[T2]** Un écart de 0,70 contre Over-folder et de
   0,22 contre Station ne signalent pas trois fois plus d'erreurs : les plafonds
   sont différents. Sans ce tableau, aucune comparaison entre adversaires n'est
   possible.

**Précaution.** Ne pas réexposer ici la définition formelle, déjà au §2.2.5. On
calcule, on ne redéfinit pas.

**Point notable à conserver.** Contre Station, le jeton moyen est un point
d'indifférence exact : toute la qualité du jeu se décide sur quatre décisions.
C'est ce qui rend T6 lisible plus loin.

---

## §3.2 — H1 : l'adaptation existe, et elle vient de la mémoire

**Objectif.** Établir l'effet principal, et surtout établir que le contrôle qui
le prouve est la condition sans mémoire.

**Déroulé.** F1 d'abord, commentée : la ligne sans mémoire ne décroît jamais, la
ligne à mémoire écrite plonge et se verrouille. Puis T3, l'effet apparié, avec
l'insistance sur l'appariement — mêmes cartes, même ordre, la chance s'annule
dans la soustraction. Neuf paires sur neuf dans le même sens, dispersion au
centième.

**Précaution.** Ne pas conclure ici sur le mécanisme : H1 dit que la mémoire
produit l'adaptation, pas comment. Le tableau brut à neuf lignes part en annexe.

---

## §3.3 — H2 : elle exploite, elle ne récite pas

**Objectif.** Montrer que l'adaptation consiste à s'écarter de l'équilibre dans
la direction que chaque adversaire commande, et non à appliquer une solution
apprise.

**Déroulé.**

1. *L'argument.* Station et Over-folder ont des défauts opposés. Aucune stratégie
   fixe, l'équilibre compris, ne peut faire descendre les deux courbes.
2. **[F2]** — la pièce neuve, et la plus importante du chapitre. Face au même
   jeton faible, l'agent fait trois choses différentes selon l'adversaire :
   il cesse d'engager contre Station, il engage systématiquement contre
   Over-folder, il reste vers un tiers contre GTO. L'asymétrie est un fait de
   comportement, et une courbe de gains ne la montre pas.
3. **[T4]** — l'agent atteint 100 % et 99 % du maximum théorique d'exploitation.
4. **[F3]** — la récitée par série, avec le plafond en pointillés.

### 3.3.1 Le contrôle négatif
Contre GTO, la récitée ne peut pas devenir positive. Sur 39 séries, elle ne l'est
jamais. Signaler explicitement que récitée = −écart contre cet adversaire : ce
sont deux lectures du même fait, pas deux vérifications.

### 3.3.2 Ce que ces valeurs doivent au choix de l'équilibre
Inchangé. L'écart est libre en α, l'échelle de la récitée ne l'est pas.

---

## §3.4 — H3 : le mécanisme de rétention

**Sept sous-sections deviennent trois.**

### 3.4.1 Deux mémoires, une seule matière
ICL et AE reçoivent le même récapitulatif brut. Seul le mécanisme diffère : l'un
empile sans appel au modèle, l'autre fait synthétiser l'agent. Sans cette
identité de matière, H3 comparerait deux informations et non deux mémoires.

### 3.4.2 L'effet mesuré
**[T5]**, avec la moyenne des quatre dernières séries plutôt qu'un point terminal
isolé. L'intervalle exclut zéro contre Station, le contient contre Over-folder.

### 3.4.3 Le mécanisme
Ce qui les sépare n'est ni la vitesse ni l'oubli. **[F4]** montre les deux points :
les deux conditions chutent identiquement à la première frontière, et le profil
d'oubli attendu pour ICL n'apparaît pas. Ce qui suit diffère : AE se verrouille
sur zéro, ICL s'arrête à un résidu qu'il n'annule sur aucune des trente séries —
son écart minimal est 0,0083.

**[T6]** localise le résidu : les quatre décisions qui comptent contre Station, en
série 9. ICL engage le jeton fort 92,6 % du temps en seconde position — deux
engagements gratuits laissés passer sur vingt-sept manches.

L'explication tient à la forme de la politique optimale. Contre Over-folder, une
règle unique et positive : engager quel que soit le jeton. Un journal brut la
porte. Contre Station, deux règles dont une négative — cesser d'engager le jeton
faible — et une distinction entre jetons. Un engagement perdant figure dans
l'historique comme une manche parmi cent cinquante ; rien ne rassemble ces
occurrences en interdiction. La synthèse fait cela.

*Absorbés en paragraphes :* l'ancien 3.4.5 (une règle ou deux) entre ici ;
l'ancien 3.4.6 (dispersion des paires deux fois et demie plus faible qu'attendu)
devient une note de méthode ; l'ancien 3.4.7 (ce qu'on ne peut pas conclure) va
au bloc Limites.

---

## §3.5 — Ce que l'agent écrit

Inchangé sur le fond, resserré. Quatre sous-sections deviennent trois blocs :
ce que la mémoire contient (**[T7]** et une note citée), une mémoire réécrite et
non cumulée (70 frontières sur 90 comportent une suppression), et ce qu'elle ne
contient jamais — une fréquence. Ce dernier point prépare directement le §3.6 et
doit être écrit comme tel.

La note fausse accompagnée d'une stratégie juste (ancien 3.5.4) reste : c'est une
observation, et elle est invisible à la mesure de H4.

---

## §3.6 — L'agent adapté ne sait plus jouer au hasard

**Le titre change.** « Ce que l'adaptation coûte » n'annonce pas le résultat.

**Le poids s'inverse.** L'incohérence passe de 696 mots à un paragraphe ; la
dégénérescence de 612 à environ 700, réécrits pour un lecteur non technicien.

### 3.6.1 Une mesure pré-enregistrée déclarée invalide
Un paragraphe. La règle rend 47,8 %, à un point de GTBENCH, et c'est un artefact
grammatical. Restreinte aux décisions où l'agent énonce son choix : 0 divergence
sur 604. Le détail des trois variantes et la relecture des huit divergences
partent en **annexe C** avec **[T9]**.

L'honnêteté méthodologique est préservée — un instrument pré-enregistré déclaré
invalide plutôt que corrigé en silence — sans occuper le premier rang.

### 3.6.2 La dégénérescence des stratégies mixtes
Le bloc rédigé est ci-dessous. **[F5]** et **[T8]**.

### 3.6.3 Ce que H4 établit
Le lien avec §3.4 : ce qui rend l'agent fort est ce qui le rend incapable de
mélanger. Puis la limite, énoncée franchement : le résultat repose sur un seul
ensemble d'information et le contrôle interne sur trois séries.

---

## §3.7 — Synthèse

**[T10]** — les quatre hypothèses : énoncé, ce qui l'aurait réfutée, ce qu'on
observe, la limite. Puis les deux branches, *homo œconomicus* et *homo silicus*,
et ce que le dispositif apporte.

---

# Blocs rédigés

## §3.6.1 — version courte

> La règle d'incohérence prévue au §2.2.5.3 s'est révélée invalide sur ce corpus.
> Appliquée à la lettre — comparer l'action jouée à la dernière action nommée
> dans le texte libre — elle rend un taux de 47,8 % sur 13 442 décisions, à un
> point des 45,1 % relevés par GTBENCH. Cette proximité est ce qui doit alerter :
> le chiffre est un artefact grammatical. La délibération en français conclut
> régulièrement par une clause contrastive qui nomme l'option écartée et non
> celle retenue — « engager garantit +1, tandis que retenir expose à une perte » —
> et la règle enregistre une incohérence là où le raisonnement est cohérent. Huit
> divergences relues intégralement se sont révélées être huit faux positifs.
>
> Restreinte aux décisions où l'agent énonce son choix par une formule explicite,
> la mesure donne **0 divergence sur 604**. Sur ce sous-ensemble, l'agent joue
> toujours l'action qu'il déclare retenir. Le prix de cette précision est le
> rappel : la mesure ne couvre plus que 2,2 % des décisions, et la chaîne de
> pensée n'étant pas restituée par le fournisseur (§L.1), elle ne voit qu'une
> partie du raisonnement. Le détail des variantes est en annexe C.

## §3.6.2 — ouverture réécrite

> Contre l'adversaire qui joue l'équilibre, bien jouer exige d'engager le jeton
> faible une fois sur trois, et de façon imprévisible. Toujours l'engager, ou ne
> jamais l'engager, se punit également : un adversaire qui anticipe la règle
> ajuste sa réponse et récupère la différence. L'imprévisibilité est ici la
> condition de l'optimalité, et c'est ce que la théorie des jeux appelle une
> stratégie mixte.
>
> Sans mémoire, l'agent s'en approche : ses fréquences d'engagement se tiennent
> autour de 30 %, pour un optimum à 33 %. Dès qu'il a écrit une note, il joue
> 0 % ou 100 %.
>
> Il n'a pas oublié comment jouer — son écart continue de baisser. Il a cessé de
> tirer au sort.
>
> [F5, puis T8]
>
> La deuxième ligne du tableau est un contrôle interne, et c'est elle qui porte
> la conclusion. La première série d'une exécution à mémoire écrite se joue avec
> un emplacement mémoire présent mais vide : même modèle, même gabarit, même
> adversaire, mêmes cartes — seule la note manque. L'agent y mélange encore
> normalement. L'effondrement apparaît exactement à la première série jouée avec
> une note écrite. Ce n'est donc pas le modèle qui dégénère : c'est la note qui
> le fait dégénérer.
>
> Et ce n'est pas un effondrement vers une valeur unique. Sur les 25 séries
> concernées, 13 sont à zéro et 1 à un, avec sept sauts de plus de 0,40 entre
> deux séries consécutives. L'agent choisit une règle, l'applique cent cinquante
> manches, puis en change à la frontière suivante. La variabilité que l'équilibre
> demande existe encore, mais elle s'est déplacée à une échelle de temps où elle
> ne produit aucune imprévisibilité à l'intérieur d'une série — la seule échelle
> où l'adversaire pourrait en subir l'effet.
>
> L'explication est dans les notes elles-mêmes (§3.5). Sur 92 000 caractères,
> l'agent n'écrit jamais une fréquence : aucun pourcentage, aucune fraction,
> aucune proportion en toutes lettres. Il écrit « éviter d'engager avec Tor ».
> Une note écrite s'exécute ; elle ne se tire pas au sort.

## Note de style

Écriture simple et directe, sans métaphore. Dire la chose, pas une image de la
chose. Vaut pour les titres de section.
