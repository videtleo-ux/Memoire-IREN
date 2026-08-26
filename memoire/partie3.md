# 3. Résultats et analyses

> **État de rédaction** : chapitre complet — 3.1 à 3.7.

Le protocole décrit au chapitre précédent a été exécuté du 22 au 24 août 2026 :
vingt-quatre exécutions, cent soixante-dix-sept séries, vingt-six mille cinq cent
cinquante manches et vingt-sept mille deux cent quatre-vingt-dix décisions de
l'agent, sur un modèle unique tenu constant (`gpt-5.6-luna`, effort de
raisonnement `medium`, cent cinquante manches par série). Les trois traitements
d'une même réplication ont reçu des distributions strictement identiques, manche
pour manche : toutes les comparaisons qui suivent sont appariées à la carte près.
La condition de réinjection d'historique n'a pas été jouée contre l'adversaire à
l'équilibre, pour la raison exposée au §2.2.7. Les contrôles de conformité — rejeu
intégral depuis les journaux, intégrité de clôture, absence d'action imposée — et
les trois incidents d'exécution sont rapportés au §2.2.8.

Les résultats sont présentés dans l'ordre du plan d'analyse arrêté avant la
campagne (§2.2.9). Cet ordre n'a pas été révisé après coup : les hypothèses,
leurs critères de réfutation et la séquence de leur examen ont été fixés avant
que la moindre donnée ne soit collectée.

---

## 3.1 Comment lire les deux instruments

Deux quantités mesurent la politique de l'agent à chaque série, et le chapitre de
méthode les a définies séparément parce qu'elles répondent à deux questions
distinctes.

> **Écart d'exploitation** = EV(meilleure réponse à l'adversaire) − EV(politique
> observée). Ce que l'agent laisse sur la table à chaque manche, faute d'exploiter
> parfaitement. Zéro signifie exploitation optimale.
>
> **Référence récitée** = EV(politique observée) − EV(équilibre), contre le même
> adversaire. La distance au comportement d'un agent qui appliquerait
> l'équilibre. Un pur récitant y reste à zéro quel que soit l'adversaire.

Les deux sont calculées exactement, en arithmétique rationnelle, par énumération
complète des douze ensembles d'information — aucune simulation, aucun intervalle
de confiance sur la mesure elle-même.

**Ces deux instruments ne sont pas indépendants.** Leur somme vaut
EV(meilleure réponse) − EV(équilibre), c'est-à-dire une constante de l'adversaire
— et cette constante est précisément l'écart qu'afficherait un récitant.
Vérification sur les cent soixante-dix-sept séries : la somme prend **une seule
valeur par adversaire**, identique à la douzième décimale.

| Adversaire | Écart + référence récitée | Soit |
|---|---|---|
| Over-folder | 0,7778 | 7/9 |
| Station | 0,1111 | 1/9 |
| GTO | 0,0000 | 0 |

À adversaire fixé, les deux mesures n'ont donc **qu'un seul degré de liberté** :
la référence récitée est un recalage affine de l'écart, de pente −1. Ce n'est pas
une seconde mesure. Trois conséquences, qu'il vaut mieux énoncer que laisser
découvrir.

D'abord, le point 2 du plan d'analyse prévoyait de tracer la trajectoire de
l'agent dans le plan formé par les deux instruments. Cette figure ne peut être
qu'une droite ; elle n'est pas produite. La référence récitée est néanmoins
tracée séparément (§3.3), parce qu'elle déplace l'origine sur le comportement du
récitant et rend visible un franchissement de signe que l'écart seul masque.

Ensuite, le contrôle négatif énoncé au §2.4 comme deux falsifications
indépendantes — une référence récitée positive contre l'adversaire à l'équilibre
*ou* un écart négatif — n'en constitue qu'une seule : contre cet adversaire la
constante vaut zéro, donc la référence récitée est l'opposé exact de l'écart. Le
dispositif n'offre pas deux verrous mais un, ce qui ne l'affaiblit pas mais doit
être dit.

Enfin, et c'est l'essentiel, **H2 n'est pas testée par le couple d'instruments
mais par la comparaison entre adversaires**. C'était déjà la position du §2.2.2 :
les fuites de Station et d'Over-folder sont opposées, et aucune stratégie fixe —
fût-elle celle de l'équilibre — ne peut faire descendre les deux courbes
simultanément. L'identification reposait au bon endroit ; seule la figure prévue
la cherchait au mauvais.

---

## 3.2 L'adaptation existe, et elle vient de la mémoire

H1 énonce que l'écart d'exploitation d'un agent doté d'une mémoire persistante
auto-rédigée décroît au fil des séries, tandis que celui du même modèle privé de
mémoire reste stationnaire. Sa réfutation était simple : que les deux conditions
ne se distinguent pas.

**Figure 1 — trajectoires d'adaptation.** *(`memoire/figures/fig1-trajectoires.png`)*

La figure porte l'écart par série, un panneau par adversaire, les trois
traitements sur les mêmes axes, les réplications individuelles en filigrane et
leur moyenne en trait épais. Deux lignes de référence l'encadrent : zéro, qui est
l'exploitation optimale, et l'écart qu'afficherait un récitant. La courbe sans
mémoire s'arrête à la série 2 : le protocole n'en prévoit que trois pour cette
condition (§2.2.6), puisque rien ne s'y accumule d'une série à l'autre et que
trois points suffisent à établir un niveau et sa dispersion.

La lecture est immédiate. **La condition sans mémoire ne décroît jamais**, contre
aucun des trois adversaires. La condition à mémoire auto-écrite chute à la
première frontière et atteint zéro contre les deux adversaires exploitables.

L'effet apparié — écart final de la mémoire auto-écrite contre le niveau moyen
sans mémoire, sur des distributions identiques — se lit ainsi :

| Adversaire | Sans mémoire | Mémoire auto-écrite (série 9) | Réduction | Par réplication |
|---|---|---|---|---|
| Over-folder | 0,704 | 0,000 | **+0,704** | +0,688 · +0,707 · +0,717 |
| Station | 0,222 | 0,002 | **+0,220** | +0,229 · +0,207 · +0,224 |
| GTO | 0,187 | 0,008 | **+0,178** | +0,156 · +0,195 · +0,184 |

Trois observations en soutiennent la lecture.

**Les neuf paires vont dans le même sens**, avec une dispersion
inter-réplications de l'ordre du centième. Trois réplications par cellule
n'autorisent aucun test d'hypothèse dont la puissance ne serait décorative ; ce
qui porte la conclusion est la cohérence du signe sur neuf comparaisons appariées
indépendantes, et l'ordre de grandeur de l'effet rapporté à sa dispersion.

**Le témoin sans mémoire fait le travail d'identification.** Il tourne sur les
mêmes distributions, avec le même modèle, le même harnais et le même calcul de
mesure ; la seule différence est la rubrique mémoire du prompt. Si la décroissance
observée venait de l'instrument, de la séquence de cartes ou d'un artefact du
harnais, elle apparaîtrait aussi dans cette condition. Elle n'y apparaît pas.

**L'écart atteint zéro exactement**, et non « une valeur proche de zéro ». La
mesure étant exacte, un écart nul signifie que la politique observée *est* une
meilleure réponse à l'adversaire, au sens strict. Contre Over-folder, les trois
réplications y sont ; contre Station, deux sur trois, la troisième à 0,005.

H1 est établie. La question de savoir ce qui, dans la mémoire, produit cet effet
est celle de la section 3.4 ; celle de savoir si l'agent exploite ou récite est
celle de la section suivante.

---

## 3.3 Elle exploite, elle ne récite pas

L'objection la plus sérieuse à H1 n'est pas que l'effet soit absent, mais qu'il
soit trivial. Le modèle a rencontré ce jeu et sa solution durant son
pré-entraînement ; une mémoire pourrait n'avoir d'autre effet que de l'aider à se
souvenir de l'équilibre. Une amélioration de l'écart serait alors une récitation
mieux exécutée, non une adaptation à un adversaire particulier.

H2 tranche cette question, et le plan d'adversaires a été construit pour cela.

**Figure 2 — récitation ou exploitation.** *(`memoire/figures/fig2-recitation.png`)*

Même découpage que la figure 1, mais l'ordonnée porte la référence récitée : le
zéro y est le comportement d'un récitant, et le plafond, l'exploitation parfaite.
C'est un recalage de la figure 1 (§3.1) et non une mesure supplémentaire ; il est
tracé parce qu'il rend visible le **franchissement de signe**, que l'échelle de la
figure 1 masque.

| Adversaire | Sans mémoire | Mémoire auto-écrite (séries 7-9) | Maximum théorique |
|---|---|---|---|
| Over-folder | +0,074 | **+0,778** | +0,778 (7/9) |
| Station | −0,111 | **+0,110** | +0,111 (1/9) |
| GTO | −0,187 | −0,024 | 0 (plafond) |

**Contre les deux adversaires exploitables, l'agent à mémoire atteint exactement
la valeur maximale de l'exploitation.** Ce maximum n'est pas une borne empirique
constatée après coup : il se calcule d'avance, et vaut 7/9 contre Over-folder,
1/9 contre Station. L'agent ne récite donc pas l'équilibre — il s'en écarte, dans
la direction que chaque adversaire commande, et jusqu'à l'optimum.

**L'asymétrie des deux adversaires est le test décisif.** Leurs fuites sont
exactement opposées : l'un paie systématiquement, l'autre se couche
systématiquement. Les exploiter demande des ajustements de sens contraire —
cesser de bluffer contre le premier, bluffer sans retenue contre le second.
Aucune stratégie fixe ne peut satisfaire les deux, et l'équilibre lui-même n'y
parvient pas : c'est précisément lui, la ligne zéro, que l'agent dépasse dans les
deux cas. Le résultat ne repose donc pas sur l'ignorance supposée du modèle, mais
sur une contrainte structurelle du plan de test.

Un point mérite d'être relevé, que le chapitre de méthode n'anticipait pas.
**Sans mémoire, l'agent est *en dessous* de l'équilibre** — de 0,111 contre
Station et de 0,187 contre GTO. La condition sans mémoire ne mesure donc pas
« le niveau récité », comme le §2.2.3 le formulait, mais quelque chose de
sensiblement moins bon qu'un récitant. Le modèle ne joue pas l'équilibre de
mémoire ; il joue moins bien, et la mémoire persistante ne lui sert pas à s'en
souvenir mais à le dépasser.

### 3.3.1 Le contrôle négatif

L'adversaire jouant l'équilibre fournit une falsification interne du dispositif
de mesure. Contre lui, aucune politique ne peut rapporter davantage que
l'équilibre : la référence récitée ne peut pas y devenir positive, ni l'écart
négatif — deux formulations d'une seule condition (§3.1). Une violation
invaliderait l'ensemble des mesures de la campagne.

Sur les trente-neuf séries jouées contre cet adversaire, **la référence récitée
n'est jamais positive** et **l'écart jamais négatif**. Six séries atteignent
exactement zéro : l'agent y joue une meilleure réponse à l'équilibre, encaissant
exactement la valeur du jeu. Aucune ne dépasse. Le contrôle tient.

Reste un fait qu'il faut interpréter et non écarter : **l'écart décroît aussi
contre GTO**, de 0,161 à la première série à 0,008 à la dixième. Ce n'est pas un
artefact, et le chapitre de méthode a été corrigé sur ce point — sa formulation
initiale tenait toute décroissance contre cet adversaire pour un défaut
invalidant, critère qui, pris au mot, aurait invalidé des résultats sains.

L'explication tient à ce que l'écart mesure. Il mesure la distance à la meilleure
réponse, et contre un adversaire à l'équilibre, toute meilleure réponse rapporte
exactement la valeur du jeu. Un agent qui cesse de commettre des fautes
grossières s'en rapproche donc sans exploiter quoi que ce soit. La distinction
entre les deux lectures est tranchée par la condition sans mémoire : si cette
décroissance venait de l'instrument, elle s'y observerait aussi, sur les mêmes
distributions et le même calcul. Elle ne s'y observe pas.

Contre GTO, la mémoire ne sert donc qu'à corriger des erreurs propres — et l'on
notera que l'écart n'y atteint jamais zéro de façon stable, contrairement aux deux
adversaires exploitables. La section 3.6 montrera pourquoi.

---

## 3.4 Le mécanisme de rétention

Les deux sections précédentes ont établi qu'une mémoire persistante produit une
adaptation, et que cette adaptation exploite au lieu de réciter. Elles ne disent
rien de la *forme* que prend cette mémoire. H3 pose cette question-là : à
information égale, deux mécanismes de rétention différents produisent-ils la même
adaptation ?

La réponse est non, mais la différence n'est ni celle que le protocole
anticipait, ni là où il la cherchait.

### 3.4.1 Deux mémoires, une seule matière

La comparaison n'a de sens que si les deux conditions reçoivent la même
information. C'est le cas, et par construction : à la clôture de chaque série,
l'arbitre produit un récapitulatif canonique — une ligne par manche, sans
agrégat, sans conseil, sans interprétation — et le sert **à l'identique** aux
deux traitements. En condition ICL, l'expérimentateur empile ce récapitulatif
dans le prompt et évince les séries anciennes lorsque la fenêtre sature ; aucun
appel au modèle n'a lieu à la frontière. En condition AE, l'agent lit le même
récapitulatif et réécrit lui-même ses notes.

Seul le mécanisme de rétention diffère. Sans cette précaution, H3 comparerait
deux informations et non deux mémoires, et tout écart observé serait
ininterprétable.

Il faut ajouter que la condition ICL n'est pas désavantagée par la capacité : sa
fenêtre contient trois séries entières, soit 450 manches de journal brut, là où
les notes de l'agent tiennent en 377 à 1 561 caractères (§3.5). Si l'une des deux
conditions dispose de plus d'information à l'instant de décider, c'est ICL.

### 3.4.2 L'effet mesuré

Les comparaisons portent sur la moyenne des quatre dernières séries plutôt que
sur un point terminal isolé, plus sensible au bruit d'échantillonnage. Elles sont
appariées par réplication : chaque paire ICL − AE compare deux exécutions ayant
reçu les mêmes cartes, manche pour manche.

| Adversaire | Effet ICL − AE | Écart-type | IC 95 % | Conclusion |
|---|---|---|---|---|
| **Station** | **+0,0381** | 0,0059 | ± 0,0148 | l'intervalle exclut zéro |
| Over-folder | +0,0039 | 0,0023 | ± 0,0056 | l'intervalle contient zéro |

Contre Station, la mémoire auto-écrite l'emporte, et l'effet est net : l'écart
résiduel d'ICL est seize fois celui d'AE (0,0405 contre 0,0024 jeton par manche).
Contre Over-folder, les deux mécanismes sont indistinguables — tous deux
atteignent l'exploitation parfaite et s'y tiennent.

**H3 est donc vérifiée, mais sous condition.** Le mécanisme de rétention ne
départage les deux mémoires que contre l'un des deux adversaires exploitables. La
suite de cette section établit ce qui distingue les deux tâches, et ce que cette
distinction dit du mécanisme.

### 3.4.3 Ce que les trajectoires montrent, et ce qu'elles ne montrent pas

Le chapitre de méthode prévoyait pour la condition ICL un profil d'oubli en dents
de scie : la fenêtre sature à la quatrième série, évince la plus ancienne, et
l'agent perd périodiquement ce qu'il avait appris. **Rien de tel n'apparaît.** La
saturation de la fenêtre ne produit aucun décrochage, ni à la quatrième série ni
ailleurs.

Ce n'est pas la seule prédiction que les données démentent. On attendait aussi
que les deux mémoires se distinguent par leur *vitesse* d'adaptation. Les
trajectoires moyennes, contre Station, ne le confirment pas :

| Série | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| ICL | 0,202 | 0,059 | 0,057 | 0,060 | 0,057 | 0,029 | 0,036 | 0,061 | 0,041 | 0,024 |
| AE | 0,226 | 0,000 | 0,000 | 0,000 | 0,000 | 0,000 | 0,006 | 0,000 | 0,002 | 0,002 |

**Les deux conditions chutent à la première frontière**, et dans les mêmes
proportions : dès qu'un souvenir de la série passée existe, sous quelque forme
que ce soit, l'essentiel de l'adaptation est acquis. La vitesse initiale ne les
sépare pas.

Ce qui les sépare est ce qui se passe ensuite. **AE se verrouille sur zéro** — la
meilleure réponse exacte, atteinte dès la série 1, tenue sur les neuf séries
suivantes à trois oscillations près, toutes inférieures à 0,015. **ICL s'arrête à
un résidu non nul** : il stagne autour de 0,058 pendant quatre séries, puis
dérive lentement et bruyamment vers 0,040, sans jamais atteindre zéro sur une
seule des trente séries jouées.

La différence ne porte donc ni sur la vitesse, ni sur la rétention — les deux
conditions adaptent aussi vite, et aucune n'oublie. Elle porte sur la
**complétude** de ce qui est extrait : là où la synthèse produit une politique
exacte, la réinjection d'historique produit une politique presque exacte, et s'y
arrête définitivement.

### 3.4.4 Où ICL s'arrête

L'écart d'exploitation est une quantité agrégée ; il ne dit pas *quelle* décision
est mal jouée. La politique observée, ensemble d'information par ensemble
d'information, le dit.

Une précision de lecture d'abord. Contre Station, la meilleure réponse n'est pas
unique : **huit des douze ensembles d'information sont des points
d'indifférence exacts**, où les deux actions rapportent rigoureusement la même
espérance. Engager le sceau médian face à un adversaire qui couvre toujours, par
exemple, rapporte exactement zéro — comme retenir. La qualité de la politique ne
se joue donc que sur quatre décisions, et l'écart n'est sensible qu'à
celles-là. C'est une propriété de l'instrument qu'il faut connaître pour ne pas
sur-interpréter une fréquence : sur les huit autres, l'agent peut jouer n'importe
quoi sans que cela lui coûte un jeton.

Ces quatre décisions se résument à deux règles. **Ne jamais bluffer le sceau
faible** — Station paie systématiquement, un bluff y est perdu d'avance. **Toujours
engager le sceau fort** — Station paie systématiquement, chaque mise de valeur y
est encaissée. Voici ce que les deux conditions jouent, en moyenne sur les quatre
dernières séries :

| Décision | Meilleure réponse | ICL | AE |
|---|---|---|---|
| Bluffer le sceau faible, en Ouvrant | 0,00 | 0,066 | **0,006** |
| Bluffer le sceau faible, en Répondant | 0,00 | 0,090 | **0,008** |
| Engager le sceau fort, en Ouvrant | 1,00 | 0,973 | **1,000** |
| Engager le sceau fort, en Répondant | 1,00 | 0,940 | **1,000** |

Après dix séries — mille cinq cents manches, dont les quatre cent cinquante
dernières intégralement présentes dans son prompt — la condition ICL bluffe encore
le sceau faible dans sept à neuf pour cent des cas, et laisse passer trois à six
pour cent de ses mises de valeur. La condition AE a supprimé le second défaut
entièrement et ramené le premier sous le pour cent.

En décomposant le résidu d'ICL sur ces quatre décisions, on obtient : **64 % de
bluffs résiduels, 36 % de mises de valeur manquées**. Celui d'AE, seize fois plus
faible, provient en totalité des premiers.

Contre Over-folder, la même analyse ne trouve rien à décomposer : les deux
conditions jouent la meilleure réponse exactement, et l'écart des deux est nul ou
à la troisième décimale.

### 3.4.5 Une règle, ou deux

La comparaison des deux adversaires livre alors une explication, et elle est
simple.

Contre Over-folder, la politique optimale tient en **une règle unique et
positive** : engager, quel que soit le sceau. Elle ne demande aucune distinction
entre les cartes, et le journal brut la porte de façon transparente — trois cents
engagements suivis de trois cents retraits adverses n'admettent qu'une lecture.
Les deux mécanismes l'extraient immédiatement et intégralement.

Contre Station, la politique optimale demande **deux règles, dont une négative**,
et une distinction entre les sceaux. Cesser de faire quelque chose est
précisément ce qu'un historique brut soutient mal : le journal enregistre ce qui
a été joué et ce que cela a rapporté, mais un bluff perdant y figure comme une
manche parmi cent cinquante, noyée dans les manches où le même geste, avec un
autre sceau, a gagné. Rien dans le document ne rassemble ces occurrences ni n'en
tire une interdiction. L'étape de synthèse fait exactement cela : elle contraint
l'agent à écrire une règle, et une règle énonce ce qu'il ne faut pas faire aussi
bien que ce qu'il faut faire.

C'est là que réside l'apport de la mémoire auto-écrite, et il est plus étroit que
l'hypothèse ne le supposait. Elle ne retient pas mieux — les deux conditions
retiennent aussi bien. Elle ne retient pas plus longtemps — aucune n'oublie sur
l'horizon observé. **Elle achève l'induction là où la réinjection d'historique
l'abandonne à quelques pour cent de l'optimum.** La contrepartie de cette
propriété est mesurée à la section 3.6 : une règle écrite est déterministe, et
cette même vertu devient un défaut là où l'optimum exige de randomiser.

### 3.4.6 Une remarque sur la précision du plan

Le dimensionnement de la tranche ICL (§2.2.7) reposait sur une extrapolation : la
dispersion des différences appariées, estimée à 0,0153 sur les paires SM − AE
déjà acquises, était supposée valoir également pour les paires ICL − AE. La
réserve était explicite — le fenêtrage introduit une dépendance au contenu
susceptible d'accroître la variabilité, et si la différence détectable réelle
avait excédé 0,038, H3 se serait trouvée à la limite du mesurable.

Elle s'est levée dans l'autre sens. La dispersion des paires ICL − AE vaut
**0,0059** contre Station, soit deux fois et demie moins. Les deux conditions
partageant tout sauf le mécanisme — même matière première, mêmes distributions,
même modèle, mêmes paramètres d'inférence —, leurs différences sont nettement
moins bruitées que celles qui séparent deux traitements éloignés. La différence
minimale détectable à trois réplications tombe ainsi de 0,038 à **0,015**, et
l'effet mesuré (+0,038) la dépasse largement. Le plan retenu était donc plus que
suffisant, là où le dimensionnement le donnait pour tout juste adéquat.

### 3.4.7 Ce que cette section ne permet pas de conclure

Trois réserves, dont deux tiennent au plan d'observation.

**Le dispositif résout mal ce qu'il montre.** Les deux conditions atteignent
l'essentiel de leur adaptation à la première frontière, c'est-à-dire au premier
point de mesure disponible. Les neuf séries suivantes documentent la persistance
d'un état stable, non la dynamique qui y conduit. Or c'est dans cette dynamique
que se logerait une différence de vitesse, si elle existait. Des séries plus
courtes — cinquante manches plutôt que cent cinquante, pour un coût comparable —
la résoudraient ; le plan actuel ne le permet pas.

**L'absence de décrochage n'est pas une absence d'oubli.** La fenêtre à trois
séries n'a produit aucune perte visible à la saturation. On ne peut pas en
conclure qu'une réinjection d'historique n'oublie jamais : seulement qu'à cet
horizon, sur ces adversaires, avec cette taille de fenêtre, elle n'a pas oublié.
Une fenêtre plus étroite ou un horizon plus long reste à explorer.

**La condition ICL n'a pas été jouée contre l'adversaire à l'équilibre.** Cet
arbitrage est exposé et assumé au §2.2.7 : il n'y a rien d'exploitable à retenir
contre un adversaire sans faille, et le contrôle négatif est acquis par ailleurs
sur trente séries en SM et en AE. Mais la question a d'abord été posée par le
budget, et la vérification qu'une réinjection d'historique ne bat pas l'équilibre
contre l'équilibre n'a donc pas été faite.

---

## 3.5 Ce que l'agent écrit

Les sections précédentes traitent la mémoire comme une variable : présente ou
absente, auto-écrite ou réinjectée. Elle est aussi un **objet observable**. Le
fichier de notes que l'agent rédige à chaque frontière est conservé intégralement
— quatre-vingt-dix notes, quatre-vingt-douze mille caractères, jamais édités par
l'expérimentateur. On peut donc lire ce que l'agent a retenu, et confronter ce
qu'il écrit à ce qu'il joue.

Cette section est la seule de la partie à procéder par lecture plutôt que par
mesure. Elle n'établit pas d'hypothèse ; elle fournit le mécanisme des deux
sections qui l'encadrent.

### 3.5.1 Ce que la mémoire contient

Le dispositif autorisait huit à quinze entrées, avec erreur en cas de
dépassement et sans compaction automatique : l'agent devait hiérarchiser et
élaguer lui-même. Cette contrainte n'a jamais mordu. Sur les quatre-vingt-dix
frontières, la note tient en **une seule entrée dans quatre-vingt-quatre cas** et
en deux dans les six autres ; on relève deux élagages et **aucun dépassement**.
La question « que sacrifie-t-il à saturation ? », posée au protocole, reste donc
sans objet : il n'a jamais saturé.

Ce que l'agent règle de lui-même, en revanche, c'est la longueur, et elle suit la
difficulté du problème :

| Adversaire | Longueur de la note (caractères) | Moyenne |
|---|---|---|
| Over-folder | 333 – 685 | 470 |
| Station | 589 – 1 557 | 808 |
| GTO | 680 – 1 906 | 1 337 |

Contre l'adversaire qui se couche toujours, il n'y a qu'une régularité à énoncer,
et la note fait quatre cent soixante-dix caractères. Contre l'adversaire à
l'équilibre, il faut détailler sceau par sceau et position par position, et elle
en fait près de trois fois plus. La note est proportionnée à ce qu'il y a à dire.

Contre Over-folder, l'induction est exacte et complète :

> « Dans "Trois Sceaux", contre cet adversaire (bilan de 150 épreuves), il n'a
> jamais engagé ni couvert. Ouvrant, il a toujours retenu ; Répondant, il s'est
> toujours retiré face à notre engagement. Nos 150 engagements ont donc tous
> rapporté +1, sans coût ni révélation des sceaux. Stratégie : engager
> systématiquement, Ouvrant comme Répondant ; ne pas retenir ni couvrir sauf
> changement manifeste. »
> — *AE-over-folder-r2, frontière de la série 9, écart 0,000*

Tout y est : le constat, sa portée, la stratégie qui en découle, et une clause de
révision. L'expérimentateur n'a fourni que le journal brut des cent cinquante
manches — une ligne par manche, sans agrégat ni conseil. La distillation est le
fait de l'agent, et c'est exactement ce que le dispositif cherchait à observer.

### 3.5.2 Une mémoire réécrite, non cumulée

Le protocole parlait d'accumulation. Ce n'est pas ce qui se produit. Sur les
quatre-vingt-dix frontières, **soixante-dix comportent une suppression** et
soixante-dix-neuf un ajout : l'agent efface sa note précédente et en écrit une
nouvelle, plutôt que d'ajouter à ce qui existe.

Le traitement qu'il réserve à son propre solde cumulé le montre bien. Trois notes
successives d'une même exécution donnent :

> « bilan corrigé après 150 épreuves : solde cumulé +5 (**remplace l'ancien
> −13**) »
> puis « solde cumulé −20 (**remplace l'ancien +5**) »

La grandeur est présentée comme cumulée, mais elle ne cumule rien : chaque note
rapporte le solde de la *dernière* série et traite la valeur précédente comme une
erreur à corriger, non comme le résultat d'une série antérieure à additionner.
L'agent ne tient pas un registre, il tient un état.

Ce constat éclaire rétrospectivement la section 3.4. Si la mémoire auto-écrite
n'accumule pas, comment produit-elle une adaptation supérieure ? Parce qu'elle
n'a pas besoin d'accumuler : contre un adversaire stationnaire, une seule série
d'observation suffit à établir la régularité, et c'est bien à la première
frontière que l'écart s'annule. Ce qu'apporte la note n'est pas un cumul de
preuves, c'est une **règle formulée**. La question de savoir ce que ce mécanisme
donnerait face à un adversaire non stationnaire — où le registre vaudrait mieux
que l'état — n'est pas tranchée ici, et relève des extensions.

### 3.5.3 Ce que la mémoire ne contient jamais : une fréquence

Le résultat le plus important de cette section est une **absence**, et elle est
totale. Sur les quatre-vingt-dix notes et leurs quatre-vingt-douze mille
caractères :

| Recherché dans les notes | Occurrences |
|---|---|
| Un pourcentage (« 33 % ») | **0** |
| Une fraction écrite (« 1/3 ») | **0** |
| Une proportion en toutes lettres (« un tiers », « une fois sur trois », « la moitié du temps ») | **0** |
| Un quantificateur non chiffré (toujours, jamais, souvent, parfois, rarement…) | **358** |

L'agent n'écrit jamais une fréquence. Il écrit des adverbes. Le mot « aléatoire »
apparaît quatre fois, et jamais à propos de sa propre stratégie : il y qualifie la
distribution des sceaux ou l'imprévisibilité d'une issue, jamais une prescription
de randomiser.

Il serait faux d'en conclure que l'agent ne perçoit pas la différence entre un
adversaire déterministe et un adversaire mixte. **Il la perçoit, et son
vocabulaire l'enregistre** :

| Adversaire | Quantificateurs | Dont catégoriques (*toujours*, *jamais*, *systématiquement*) |
|---|---|---|
| Over-folder | 98 | **100 %** |
| Station | 94 | **100 %** |
| GTO | 166 | **17 %** |

Face aux deux adversaires déterministes, la totalité des quantificateurs sont
catégoriques. Face à l'adversaire à l'équilibre, ils ne le sont plus que dans un
cas sur six ; l'agent bascule vers un registre gradué — « très souvent »,
« parfois », « fréquemment », « régulièrement », « prévisiblement ».

**La détection du caractère stochastique est donc acquise ; c'est son encodage
qui manque.** Le canal mémoire dispose d'adverbes gradués et d'aucun nombre. Or
un adverbe gradué ne s'exécute pas comme une fréquence : au moment de décider,
« il couvre souvent avec Vael » ne dit pas s'il faut engager cette fois-ci. La
note tranche donc, et elle tranche catégoriquement. Le même document, contre
l'adversaire à l'équilibre, prescrit :

> « Éviter d'engager avec Tor ou Vael après sa retenue. »
> — *AE-gto-r2, frontière de la série 9*

Tor est le sceau faible. L'équilibre y demande d'engager **une fois sur trois**.
La note prescrit zéro.

C'est le mécanisme complet de la dégénérescence mesurée en 3.6.2, établi ici sur
le canal lui-même et non par inférence : l'agent observe correctement, écrit
fidèlement ce qu'il observe dans le vocabulaire dont il dispose, et ce vocabulaire
ne sait pas porter un tiers.

### 3.5.4 Une note fausse, une stratégie juste

Une note sur les trente écrites contre Over-folder inverse les rôles :

> « Contre cet adversaire, lors des 150 dernières épreuves, **il a toujours
> engagé** en tant qu'Ouvrant puis s'est retiré après chacun de mes engagements
> en tant que Répondant. »
> — *AE-over-folder-r3, frontière de la série 9, écart 0,000*

Le bot n'a jamais engagé : sur les quatre mille cinq cents manches jouées contre
lui en condition AE, il a retenu deux mille deux cent cinquante fois en position
d'Ouvrant et n'a pas misé une seule fois. La proposition est fausse, et
vérifiablement fausse dans les journaux.

L'écart de la série concernée est pourtant de **0,000** : la stratégie jouée est
la meilleure réponse exacte. Le cas est isolé — une note sur trente, et non un
tiers des exécutions comme des notes de travail antérieures l'indiquaient — mais
il est instructif pour deux raisons.

D'abord parce qu'il montre que **l'explication n'est pas porteuse** : l'agent peut
énoncer une justification fausse tout en jouant juste. Le comportement optimal ne
garantit pas que le modèle du monde qui le sous-tend soit correct, ce qui est
précisément la thèse de la branche *homo silicus* de la question de recherche.

Ensuite parce que cette incohérence-là est **invisible à l'instrument de la
section 3.6.1**. La mesure automatique compare le texte d'une décision à l'action
de cette même décision ; elle ne compare pas le contenu de la mémoire aux faits
enregistrés dans les journaux. Une contradiction logée dans le canal mémoire y
échappe entièrement. Le taux d'incohérence rapporté en 3.6.1 doit donc se lire en
sachant qu'un canal entier n'est pas couvert.

---

## 3.6 Ce que l'adaptation coûte

Les sections précédentes ont montré un agent qui s'améliore : il exploite ses
adversaires jusqu'à l'optimum, et le mécanisme qui le lui permet est identifié.
H4 pose la question inverse. La littérature documente chez les modèles de langage
des défaillances de décision robustes — incohérence entre le raisonnement
verbalisé et l'action jouée, incapacité à stabiliser une stratégie mixte. Ces
défaillances survivent-elles à l'adaptation, ou celle-ci les corrige-t-elle ?

La réponse est double, et la seconde moitié est le résultat le plus inattendu de
ce travail. Elle exige d'abord d'établir qu'un des deux instruments prévus ne
mesure pas ce qu'il annonçait.

### 3.6.1 L'incohérence raisonnement↔action : une mesure qui ne mesure pas

Le protocole prévoyait (§2.2.5.3) une mesure automatique simple : l'agent
délibère librement avant d'énoncer son action sur une ligne dédiée ; on compare
l'action jouée à **la dernière action nommée dans le texte libre qui la
précède**, et toute divergence compte comme une incohérence.

Appliquée à la lettre sur les 27 270 décisions au parsing strict, cette règle
rend un taux d'incohérence de **47,8 %**, calculé sur les 13 442 décisions dont
le raisonnement nomme au moins une action. Le chiffre est à un point des 45,1 %
d'erreurs factuelles relevés par GTBENCH.

**Cette coïncidence est précisément ce qui doit alerter.** Un résultat qui
confirme la littérature sans effort, sur une mesure jamais validée, mérite d'être
examiné avant d'être publié. Il ne survit pas à l'examen.

La cause est grammaticale. Le raisonnement produit par le modèle conclut
régulièrement par une clause contrastive, qui nomme non pas l'option retenue mais
l'option **écartée** :

> « Engager garantit donc un gain de +1, *tandis que retenir* expose à une perte
> selon le sceau adverse. »
> — action effectivement jouée : engager.

La règle lit « retenir » — la dernière action nommée — et enregistre une
incohérence là où le raisonnement est parfaitement cohérent. Huit divergences
tirées au hasard dans le corpus et relues intégralement se sont révélées être
**huit faux positifs**, toutes de cette forme. Une règle positionnelle hérite de
la structure du discours français, où l'alternative rejetée occupe la position
finale.

Une variante conservatrice a été testée, qui écarte les occurrences dont le sujet
apparent est l'adversaire — « *l'adversaire se retire systématiquement* »
n'énonce pas une intention de l'agent. Elle abaisse le taux à 36,6 % sans le
rendre valide : le défaut ne tient pas à l'attribution du sujet mais à la
structure contrastive elle-même.

| Variante de la règle | Décisions mesurables | Divergences | Taux |
|---|---|---|---|
| A — positionnelle, telle que pré-enregistrée | 13 442 | 6 422 | 47,8 % |
| B — occurrences attribuées à l'adversaire écartées | 12 095 | 4 425 | 36,6 % |
| C — l'agent **énonce** son choix | 604 | **0** | **0,00 %** |

La troisième variante renonce au rappel pour gagner la précision. Elle ne retient
que les décisions où l'agent déclare son choix par une formule explicite — « il
vaut mieux X », « je choisis X », « X est préférable » — et ne mesure donc rien
d'autre que ce que H4 demande. Sur les **604 décisions** de ce sous-ensemble,
l'agent joue l'action qu'il vient de désigner dans **tous les cas**.

**L'énoncé que les données permettent est donc celui-ci, et pas un mot de plus :
l'agent ne se contredit jamais explicitement.** C'est plus étroit que « l'agent
est cohérent », et il importe de ne pas confondre les deux. Deux bornes le
limitent.

D'abord, **le raisonnement n'est observable qu'en partie**. Le modèle retenu
facture une chaîne de pensée interne que le fournisseur ne restitue jamais, et sa
sortie visible se réduit souvent à la seule ligne d'action : 13 447 décisions sur
27 270, soit 49,3 %, comportent un texte au-delà de cette ligne. Une incohérence
entre la chaîne non restituée et l'action jouée est invisible par construction.

Ensuite, **ce sous-ensemble n'est pas aléatoire**. La propension à verbaliser
dépend fortement du traitement :

| Traitement | Décisions | Avec texte au-delà de la ligne d'action | Avec choix explicitement énoncé |
|---|---|---|---|
| SM | 4 229 | 28,1 % | 4,6 % |
| ICL | 8 996 | 36,1 % | 0,9 % |
| AE | 14 045 | 64,1 % | 2,3 % |

L'agent verbalise plus de deux fois plus souvent lorsqu'il dispose de notes. La
mesure porte donc préférentiellement sur les décisions du traitement AE, et le
taux obtenu est une propriété d'un échantillon sélectionné, non une fréquence de
campagne.

Le troisième volet prévu au §2.2.5.3 — un codage manuel sur échantillon
stratifié, selon les cinq catégories de GTBENCH — aurait permis d'estimer le taux
de faux négatifs de la mesure automatique. Il n'a pas été conduit ; cette limite
est reprise au chapitre suivant.

### 3.6.2 La dégénérescence des stratégies mixtes

Le second volet de H4 ne dépend d'aucune verbalisation : il se lit directement
dans la politique observée. L'équilibre du jeu exige des fréquences
intermédiaires sur plusieurs ensembles d'information ; on mesure si l'agent s'y
tient, ou s'il s'échoue sur les bornes 0 et 1.

**Une précaution d'interprétation détermine tout le résultat.** Contre un
adversaire exploitable, la meilleure réponse *est* pure : jouer une fréquence de
0 ou de 1 y est optimal, non dégénéré. Agréger les trois adversaires reviendrait
à compter comme un biais une politique correcte. Sur l'ensemble d'information du
bluff au sceau faible, le comptage agrégé donne 56 % de séries aux bornes ; le
comptage restreint à l'adversaire jouant l'équilibre — le seul où le mélange soit
requis — en donne **38 %**. C'est ce second chiffre qui a un sens.

Toutes les fréquences rapportées ici sont estimées sur au moins vingt
observations ; les couples série × ensemble d'information en deçà sont écartés,
une fréquence établie sur trois observations ne disant rien d'un mélange.

Le résultat repose sur cet unique ensemble d'information, et il faut dire
pourquoi. Les trois autres ensembles à fréquence d'équilibre intermédiaire ne
sont atteints que si l'adversaire mise, ce que l'équilibre ne fait
qu'occasionnellement : leur effectif médian est de neuf à seize observations par
série, et une, deux et six séries respectivement atteignent le seuil. Il n'y a
rien à conclure de si peu.

Sur l'ensemble d'information retenu — l'ouverture avec le sceau faible, que
l'équilibre veut jouée agressivement un tiers du temps —, la ventilation donne
ceci :

| | Séries | Aux bornes 0 ou 1 | Distance moyenne à 1/3 |
|---|---|---|---|
| SM — sans mémoire | 9 | **0 %** | 0,078 |
| AE — première série, note encore vide | 3 | **0 %** | 0,113 |
| AE — séries suivantes, note écrite | 25 | **56 %** | 0,323 |

**La mémoire ne corrige pas la dégénérescence : elle la produit.** Privé de
mémoire, l'agent joue des fréquences intermédiaires, et remarquablement proches
de la valeur d'équilibre — entre 0,20 et 0,40 sur les neuf séries, pour une
moyenne de 0,279 contre 0,333 attendus. Doté d'une note, il s'échoue sur les
bornes plus d'une série sur deux, et sa distance moyenne à la fréquence
d'équilibre est multipliée par quatre.

La troisième ligne du tableau fournit un **contrôle interne** qui exclut toute
explication par le traitement ou par le harnais. La première série d'une
exécution AE se joue avec un emplacement mémoire présent mais vide : même
modèle, même gabarit de prompt, même exécution, même adversaire — seule la note
manque. Sur ces trois séries, aucune fréquence n'est aux bornes. L'effondrement
apparaît exactement à la première série jouée avec une note écrite.

Il faut enfin décrire correctement la forme de cette dégénérescence, car elle
n'est pas un simple effondrement vers une borne unique. Sur les vingt-cinq séries
concernées, treize sont à zéro exactement et une à un exactement : l'agent
**alterne entre les deux extrêmes d'une série à l'autre**. Une réplication passe
de 0,00 à 0,85, puis 0,54, 0,96 et 1,00 avant de revenir à 0,00 ; on relève sept
sauts de plus de 0,40 entre deux séries consécutives sur les trois réplications.

Autrement dit, l'agent ne remplace pas le mélange par une politique pure stable.
**Il remplace une randomisation intra-série par une alternance inter-séries** —
il choisit une règle, l'applique intégralement pendant cent cinquante manches,
puis en change à la frontière suivante. La variabilité que l'équilibre demande
existe encore, mais elle a migré vers la mauvaise échelle de temps, où elle ne
produit aucune imprévisibilité exploitable par un adversaire au sein d'une même
série.

### 3.6.3 Ce que H4 établit

L'hypothèse admettait un résultat mixte, et c'est ce qu'elle obtient. Sur le
premier volet, aucune incohérence explicite n'est détectable — et l'instrument
prévu pour la mesurer s'est révélé mesurer autre chose. Sur le second, le biais
est non seulement présent mais **amplifié par le dispositif même qui produit
l'adaptation**.

Ce second constat s'articule directement à la section 3.4. Ce qui rend la mémoire
auto-écrite supérieure à la réinjection d'historique — le fait qu'elle contraigne
l'agent à formuler une règle, et donc à achever l'induction — est exactement ce
qui la rend incapable de randomiser. Une règle écrite en langue naturelle est
déterministe : elle dit « engager avec le sceau fort », jamais « engager avec le
sceau faible une fois sur trois ». Le canal qui porte l'adaptation ne sait pas
porter une fréquence.

**L'adaptation et le biais ne sont pas deux phénomènes qui coexistent par
hasard : c'est le même mécanisme, observé sur deux tâches qui ne demandent pas la
même chose.** Contre un adversaire à faille, où l'optimum est pur, formuler une
règle est exactement ce qu'il faut faire. Contre un adversaire à l'équilibre, où
l'optimum est mixte, c'est ce qu'il ne faut pas faire — et l'agent le fait quand
même, parce que c'est la seule chose que sa mémoire sache faire.

Deux réserves closent cette section. Le résultat quantitatif porte sur **un seul
ensemble d'information**, faute d'effectifs suffisants sur les trois autres. Et
le taux d'incohérence n'est établi que sur les décisions où l'agent énonce son
choix, soit 2,2 % de la campagne ; le codage manuel qui aurait permis d'en
estimer la portée réelle n'a pas été conduit.

---

## 3.7 Synthèse

La question de recherche comportait deux branches, et le dispositif a été conçu
pour les instrumenter séparément — c'est sa contribution méthodologique, et c'est
ce qui permet à cette synthèse de dire autre chose qu'un verdict.

| | Énoncé | Réfutation prévue | Verdict |
|---|---|---|---|
| **H1** | l'adaptation vient de la mémoire | AE ne se distingue pas de SM | **établie** — neuf paires appariées sur neuf, effet de +0,178 à +0,704 |
| **H2** | elle exploite, elle ne récite pas | l'écart ne descend que contre l'un des deux adversaires biaisés | **établie** — maxima théoriques atteints exactement, contrôle négatif tenu sur 39 séries |
| **H3** | le mécanisme de rétention compte | ICL égale ou surpasse AE | **établie sous condition** — +0,038 ± 0,015 contre Station, indistinguable contre Over-folder |
| **H4** | des biais de décision persistent | les fréquences se stabilisent aux valeurs mixtes | **établie sur un volet** — dégénérescence produite par la mémoire ; aucune incohérence explicite détectable |

### La branche *homo œconomicus*

La réponse est positive, et elle est nette. Doté d'une mémoire persistante
auto-rédigée, l'agent développe une adaptation comportementale qui s'apparente
bien à une stratégie : il identifie la régularité de son adversaire à partir d'un
journal brut que personne n'a interprété pour lui, en tire une règle, et applique
cette règle jusqu'à l'exploitation maximale. Contre les deux adversaires
exploitables, il atteint **exactement** l'optimum théorique — non une valeur
proche, mais la meilleure réponse au sens strict, sur une mesure exacte.

Ce n'est pas une récitation mieux exécutée. La démonstration ne repose pas sur
l'hypothèse que le modèle ignorerait le jeu, mais sur l'asymétrie du plan
d'adversaires : les deux fuites exploitées demandent des ajustements de sens
contraire, et aucune stratégie fixe — pas même l'équilibre — ne les satisfait
ensemble. Le fait que l'agent privé de mémoire joue *en dessous* de l'équilibre
achève de l'établir : la mémoire ne lui sert pas à se souvenir de la solution,
elle lui sert à la dépasser.

### La branche *homo silicus*

C'est ici que le résultat cesse d'être confortable, et qu'il devient
intéressant.

L'adaptation observée ne cohabite pas avec un biais de décision : **elle le
produit**. Sur l'ensemble d'information où l'équilibre exige de bluffer une fois
sur trois, l'agent privé de mémoire joue des fréquences intermédiaires, proches de
la valeur théorique. Dès qu'une note existe, il s'échoue sur les bornes 0 et 1
plus d'une série sur deux, et sa distance à la fréquence d'équilibre quadruple.
Le contrôle interne exclut toute autre explication : la première série d'une
exécution à mémoire, jouée avec un emplacement présent mais vide, ne présente pas
le phénomène.

Le mécanisme est identifié, et il est le même que celui qui produit le succès.
Ce qui rend la mémoire auto-écrite supérieure à la réinjection d'historique
(§3.4), c'est qu'elle contraint l'agent à **formuler une règle** — et c'est en
formulant une règle qu'il achève l'induction là où l'historique brut l'abandonne
à quelques pour cent de l'optimum. Mais une règle écrite en langue naturelle est
déterministe. Les quatre-vingt-dix notes de la campagne le montrent sans
exception : zéro pourcentage, zéro fraction, zéro proportion en toutes lettres,
contre trois cent cinquante-huit quantificateurs non chiffrés. L'agent *détecte*
que l'adversaire à l'équilibre est stochastique — son vocabulaire passe de
100 % de quantificateurs catégoriques face aux adversaires déterministes à 17 %
face à lui — mais il n'a aucun moyen d'écrire une fréquence. Il écrit « éviter
d'engager avec Tor » là où l'optimum demande de le faire une fois sur trois.

**Le canal qui porte l'adaptation ne sait pas porter une fréquence.** L'adaptation
et le biais ne sont donc pas deux phénomènes qui coexistent : c'est le même
mécanisme, observé sur deux tâches qui ne demandent pas la même chose. Contre un
adversaire à faille, où l'optimum est pur, formuler une règle est exactement ce
qu'il faut faire. Contre un adversaire à l'équilibre, où l'optimum est mixte,
c'est exactement ce qu'il ne faut pas faire — et l'agent le fait quand même,
parce que c'est la seule chose que sa mémoire sache faire.

On ne peut donc pas assimiler cette adaptation à une rationalité économique au
sens strict. L'agent optimise, et il optimise remarquablement bien dans un espace
de stratégies pures. Mais l'espace où il optimise n'est pas celui que la théorie
des jeux à information imparfaite lui assigne, et il s'en éloigne au moment même
où il exploite le mieux.

### Ce que le dispositif apporte

Un travail qui n'aurait mesuré que la performance aurait observé un agent qui
joue de mieux en mieux, et conclu à une rationalité accrue. La séparation des
trois dimensions — stratégie exploitative, stratégie d'équilibre, biais de
décision — que la littérature recensée en §1.5.4 confond régulièrement, est ce
qui permet d'observer les deux mouvements à la fois : la politique se rapproche
de la meilleure réponse *et* s'éloigne de l'équilibre, et le second mouvement est
la contrepartie du premier.

Trois résultats méthodologiques accompagnent ces conclusions, et méritent d'être
retenus indépendamment d'elles. La redondance des deux instruments à adversaire
fixé (§3.1), qui invalide une figure prévue au plan d'analyse. L'invalidité de la
mesure automatique d'incohérence telle qu'elle était pré-enregistrée (§3.6.1),
dont le taux artefactuel de 47,8 % tombait à un point du chiffre attendu par la
littérature. Et le fait, établi par un audit conduit avant la campagne (§2.4), que
les défauts les plus dangereux d'un tel dispositif ne se logent ni dans son code
ni dans ses journaux, mais à sa frontière avec l'outillage tiers qu'il pilote.

Les limites de ce travail — trois réplications, un seul modèle, une seule tâche,
un horizon de dix séries, un codage manuel non conduit, un contrôle négatif absent
en condition de réinjection d'historique — sont reprises au chapitre suivant.
