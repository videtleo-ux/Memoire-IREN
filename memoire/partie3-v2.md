# 3. Résultats et analyses

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

## 3.1 Comment se lit un chiffre de ce chapitre

Le chapitre de méthode a défini les deux instruments de mesure ; il ne les a pas
appliqués. Cette section le fait, sur une série réelle et jusqu'au bout, pour que
chaque chiffre des sections suivantes soit vérifiable et non simplement admis.

### 3.1.1 L'unité

Le jeu se compte en jetons. Chaque manche en engage un d'office de la part de
chaque joueur, plus un éventuel engagement supplémentaire. Toutes les quantités
rapportées dans ce chapitre sont en **jetons par manche**, moyennés sur les deux
positions. Elles se traduisent en jetons par série en multipliant par cent
cinquante, ce qui donne l'ordre de grandeur concret de ce qui se joue.

### 3.1.2 De cent cinquante manches à six nombres

L'adversaire *Station* n'engage jamais. L'agent n'a donc qu'une seule décision
par manche — engager ou retenir — et sa situation se résume à deux choses : la
position qu'il occupe et le sceau qu'il détient. Deux positions, trois sceaux :
six situations. La politique observée est la fréquence d'engagement dans
chacune.

Voici la première série d'une exécution à mémoire auto-écrite contre cet
adversaire :

**Tableau 1 — Une série décomposée.** *(`memoire/tableaux/T1-serie-decomposee.csv`)*

| Position | Sceau | Engagements | Manches | Fréquence |
|---|---|---|---|---|
| Ouvrant | faible | 9 | 30 | 0,300 |
| Ouvrant | moyen | 6 | 23 | 0,261 |
| Ouvrant | fort | 14 | 22 | 0,636 |
| Répondant | faible | 5 | 21 | 0,238 |
| Répondant | moyen | 7 | 26 | 0,269 |
| Répondant | fort | 11 | 28 | 0,393 |

*Exécution AE-station-r1, série 0. Ces six fréquences constituent l'intégralité
de ce que la mesure retient d'une série de cent cinquante manches.*

### 3.1.3 De six nombres à une espérance

Ce que ces six fréquences rapportent contre *Station* se déduit sceau par sceau,
sans calcul intermédiaire, parce que cet adversaire couvre systématiquement — il
y a donc toujours abattage, et l'abattage est déterminé par le seul rang des
sceaux.

**Le sceau fort gagne à coup sûr.** Retenir rapporte un jeton ; engager en
rapporte deux, puisque l'adversaire couvre. Engager rapporte donc **un jeton de
plus**, et l'optimum est d'engager systématiquement.

**Le sceau faible perd à coup sûr.** Retenir coûte un jeton, engager en coûte
deux. Engager coûte donc **un jeton de plus**, et l'optimum est de ne jamais
engager.

**Le sceau moyen gagne une fois sur deux.** Retenir rapporte +1 ou −1, espérance
nulle ; engager rapporte +2 ou −2, espérance nulle également. Engager ou retenir
y est **exactement indifférent**. Ce point n'est pas anecdotique : il signifie que
la qualité de la politique contre cet adversaire ne se joue que sur quatre
décisions, et cette propriété sera mobilisée en 3.4.3.

Les six situations étant équiprobables, l'espérance s'écrit alors :

> EV = [ (fréquence au sceau fort − fréquence au sceau faible) en Ouvrant
> + (fréquence au sceau fort − fréquence au sceau faible) en Répondant ] / 6

Appliquée au tableau 1 :

> EV = [ (0,636 − 0,300) + (0,393 − 0,238) ] / 6 = **0,0819 jeton par manche**

Sur les cent cinquante manches de la série, cela représente un gain net d'environ
douze jetons.

### 3.1.4 De l'espérance à l'écart

Le meilleur jeu possible contre cet adversaire consiste à engager le sceau fort
systématiquement et à ne jamais engager le sceau faible, dans les deux
positions :

> EV(meilleure réponse) = [ (1 − 0) + (1 − 0) ] / 6 = **0,3333 jeton par manche**

Ce nombre est un plafond : aucune politique ne peut faire mieux contre *Station*.
L'écart d'exploitation est la différence.

> **Écart = 0,3333 − 0,0819 = 0,2515 jeton par manche**

Soit, sur la série, **trente-huit jetons** qu'un joueur parfait aurait ramassés et
que l'agent laisse — non par malchance, puisque la mesure porte sur la politique
et non sur les gains réalisés, mais par imperfection du jeu.

La seconde mesure procède de la même espérance, en changeant de référence. Un
agent qui appliquerait l'équilibre gagnerait 0,2222 jeton par manche contre cet
adversaire ; la référence récitée est l'écart à ce niveau :

> **Référence récitée = 0,0819 − 0,2222 = −0,1403 jeton par manche**

Négative : à cette série, l'agent joue moins bien qu'un pur récitant de
l'équilibre.

Ces deux calculs sont exacts. Les six distributions et un arbre de profondeur au
plus trois autorisent une énumération complète en arithmétique rationnelle : il
n'y a ni simulation, ni intervalle de confiance sur la mesure elle-même. Les
seuls intervalles rapportés dans ce chapitre portent sur la dispersion entre
réplications, jamais sur le calcul.

### 3.1.5 L'échelle de lecture

Un écart ne s'interprète pas dans l'absolu, parce que le plafond dépend de
l'adversaire. Le tableau suivant donne la règle graduée du chapitre.

**Tableau 2 — L'échelle de lecture.** *(`memoire/tableaux/T2-echelle-de-lecture.csv`)*

| Adversaire | Gain du joueur parfait | Gain d'un récitant | Écart d'un récitant | Référence récitée maximale |
|---|---|---|---|---|
| Over-folder | 1,0000 | 0,2222 | 0,7778 (7/9) | +0,7778 |
| Station | 0,3333 | 0,2222 | 0,1111 (1/9) | +0,1111 |
| GTO | 0,0000 | 0,0000 | 0,0000 | 0 |

Un écart de 0,70 contre *Over-folder* et de 0,22 contre *Station* ne signalent
donc pas trois fois plus d'erreurs : rapportés à leurs plafonds respectifs, ils
représentent une qualité de jeu comparable. Le rapport de sept entre les deux
écarts de récitation fournit en outre une échelle de sensibilité — contre
*Over-folder*, une adaptation même partielle sera lisible sans ambiguïté.

### 3.1.6 Les deux instruments n'en font qu'un, à adversaire fixé

Une propriété du dispositif doit être énoncée avant d'être découverte. La somme
des deux mesures vaut EV(meilleure réponse) − EV(équilibre), c'est-à-dire une
constante de l'adversaire — et cette constante est précisément la dernière colonne
du tableau 2. Vérification sur les cent soixante-dix-sept séries : la somme prend
une seule valeur par adversaire, identique à la douzième décimale.

À adversaire fixé, les deux mesures n'ont donc **qu'un seul degré de liberté** :
la référence récitée est un recalage affine de l'écart, de pente −1. Ce n'est pas
une seconde mesure. Trois conséquences en découlent.

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
les fuites de *Station* et d'*Over-folder* sont opposées, et aucune stratégie
fixe — fût-elle celle de l'équilibre — ne peut faire descendre les deux courbes
simultanément. L'identification reposait au bon endroit ; seule la figure prévue
la cherchait au mauvais.

---

## 3.2 L'adaptation existe, et elle vient de la mémoire

H1 énonce que l'écart d'exploitation d'un agent doté d'une mémoire persistante
auto-rédigée décroît au fil des séries, tandis que celui du même modèle privé de
mémoire reste stationnaire. Sa réfutation était simple : que les deux conditions
ne se distinguent pas.

**Figure 1 — Trajectoires d'adaptation : écart d'exploitation par série.** *(`memoire/figures/fig1-trajectoires.png`)*

La figure porte l'écart par série, un panneau par adversaire, les trois
traitements sur les mêmes axes. La courbe sans mémoire s'arrête à la série 2 : le
protocole n'en prévoit que trois pour cette condition (§2.2.6), puisque rien ne
s'y accumule d'une série à l'autre et que trois points suffisent à établir un
niveau et sa dispersion.

La lecture est immédiate. **La condition sans mémoire ne décroît jamais**, contre
aucun des trois adversaires — sa pente est même légèrement positive contre deux
d'entre eux. La condition à mémoire auto-écrite chute à la première frontière et
atteint zéro contre les deux adversaires exploitables.

**Tableau 3 — Effet apparié de la mémoire sur l'écart d'exploitation.** *(`memoire/tableaux/T3-effet-apparie-H1.csv`)*

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
meilleure réponse à l'adversaire, au sens strict. Contre *Over-folder*, les trois
réplications y sont ; contre *Station*, deux sur trois, la troisième à 0,005.

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

### 3.3.1 L'asymétrie, qui est le test décisif

Les fuites de *Station* et d'*Over-folder* sont exactement opposées : l'un couvre
systématiquement, l'autre se retire systématiquement. Les exploiter demande des
ajustements de sens contraire — cesser d'engager le sceau faible contre le
premier, l'engager sans retenue contre le second. **Aucune stratégie fixe ne peut
satisfaire les deux**, et l'équilibre lui-même n'y parvient pas.

Cette contrainte se vérifie directement sur le comportement, sans passer par
aucune mesure de gain.

**Figure 2 — Fréquence d'engagement avec le sceau faible, selon l'adversaire.** *(`memoire/figures/fig2-asymetrie.png`)*

Une seule situation est représentée — l'agent détient le sceau le plus faible —
et la figure donne la fréquence à laquelle il l'engage, sans mémoire puis en fin
d'exécution avec mémoire.

**Sans mémoire, cette fréquence ne peut pas dépendre de l'adversaire, et c'est
une propriété du dispositif avant d'être une observation.** En position
d'Ouvrant, l'agent parle le premier : aucune action adverse n'a encore eu lieu
dans la manche. Le contexte étant neuf à chaque manche (§2.2.4), l'information
dont il dispose à cet instant — les règles, le vocabulaire, son propre sceau —
est rigoureusement identique face aux trois adversaires. Toute différence de
fréquence y relève du bruit d'échantillonnage. C'est bien ce qu'on observe :
0,285 · 0,307 · 0,355 selon l'adversaire, pour un écart-type d'échantillonnage de
0,031 sur les 228 observations de chaque cellule.

Avec mémoire, la même fréquence monte à **1,000** contre *Over-folder* et tombe à
**0,004** contre *Station*, tout en restant proche du tiers contre l'adversaire à
l'équilibre. Trois réponses à la même situation, dont deux diamétralement
opposées.

**Ce contraste ne peut pas s'obtenir en appliquant l'équilibre, et il faut être
précis sur ce que cela signifie.** La stratégie d'équilibre est un objet fixe —
douze probabilités, calculées contre un adversaire supposé jouer lui-même
l'équilibre. Un agent qui la met en œuvre en révisant ses croyances exactement
comme l'équilibre bayésien parfait le prescrit n'en sort pas : dans un tel
équilibre, les croyances portent sur le **nœud atteint à l'intérieur d'un
ensemble d'information** — donc sur le sceau de l'adversaire — et se dérivent par
Bayes **à partir de la stratégie d'équilibre supposée**, non à partir des
fréquences observées. Face à *Station*, ce modèle est faux, et la règle de Bayes
ainsi spécifiée ne le corrige jamais : elle n'a pas d'entrée pour cela. Le jeu ne
comportant qu'un seul tour de décision, la révision intra-manche est de surcroît
déjà entièrement encodée dans les douze probabilités.

Réviser ses croyances sur la **stratégie** de l'adversaire, et non sur son sceau,
produirait bien une adaptation. Mais cette révision-là suppose de comparer des
manches entre elles, donc une mémoire — et c'est précisément ce que le mémoire
appelle exploiter. C'est l'hypothèse que H2 établit, non celle qu'elle écarte.

Le résultat ne repose donc pas sur l'ignorance supposée du modèle, mais sur une
contrainte structurelle du plan de test : deux fuites opposées, et une politique
qui ne peut les exploiter toutes deux qu'en variant avec l'adversaire.

### 3.3.2 L'amplitude, rapportée à son maximum théorique

**Tableau 4 — Référence récitée : distance au comportement d'équilibre.** *(`memoire/tableaux/T4-reference-recitee.csv`)*

| Adversaire | Sans mémoire | Mémoire auto-écrite (séries 7-9) | Maximum théorique | Atteint |
|---|---|---|---|---|
| Over-folder | +0,074 | **+0,778** | +0,778 (7/9) | 100 % |
| Station | −0,111 | **+0,110** | +0,111 (1/9) | 99 % |
| GTO | −0,187 | −0,024 | 0 (plafond) | — |

**Contre les deux adversaires exploitables, l'agent à mémoire atteint exactement
la valeur maximale de l'exploitation.** Ce maximum n'est pas une borne empirique
constatée après coup : il se calcule d'avance (tableau 2), et vaut 7/9 contre
*Over-folder*, 1/9 contre *Station*. L'agent ne récite donc pas l'équilibre — il
s'en écarte, dans la direction que chaque adversaire commande, et jusqu'à la
meilleure réponse exacte.

Il faut insister sur ce point, car l'intuition courante veut que bien jouer et
jouer l'équilibre soient une seule et même chose. **Face à un adversaire qui ne
joue pas l'équilibre, ce sont deux exigences incompatibles**, et le tableau
suivant le montre sur la seule décision de l'ouverture au sceau faible :

| | Ce que prescrit l'équilibre | Ce que prescrit la meilleure réponse | Ce que joue l'agent à mémoire |
|---|---|---|---|
| contre *Over-folder* | 1/3 | **1** | **1,000** |
| contre *Station* | 1/3 | **0** | **0,004** |
| contre *GTO* | 1/3 | *toute fréquence convient* | 0,202 |

Deux prescriptions opposées pour une seule et même situation, et l'agent suit
chaque fois la meilleure réponse plutôt que l'équilibre. La troisième ligne
mérite d'être lue à part : contre un adversaire qui joue l'équilibre, cette
décision est un **point d'indifférence exact** — toutes les fréquences y
rapportent la valeur du jeu, et aucune n'est donc meilleure qu'une autre au sens
de l'écart. C'est pourquoi l'agent peut y jouer 0,202 sans que cela lui coûte
quoi que ce soit, et c'est aussi ce qui rend la section 3.6 nécessaire : ce que
l'agent perd en cessant de mélanger n'est pas visible sur cet instrument-là. Le manque à gagner d'un
agent qui s'en tiendrait à l'équilibre est d'ailleurs considérable : 0,111 jeton
par manche contre *Station*, et **0,778 contre *Over-folder***, soit cent
dix-sept jetons abandonnés sur une série de cent cinquante. L'équilibre ne
garantit pas de bien jouer ; il garantit de ne pas être exploité, et cette
garantie se paie cher face à un adversaire qui a une faille.

Un point de vocabulaire suit de là. Le couple formé par l'agent optimal et
*Station* n'est **pas** un équilibre du jeu : un équilibre exige que les deux
joueurs se répondent optimalement, or les bots sont des tables de décision figées
qui ne répondent à rien. L'agent y est optimal, son adversaire non. C'est une
meilleure réponse à une politique fixe — l'objet même que ce mémoire appelle
exploitation.

Les deux notions ne se confondent que dans un seul cas : **contre l'adversaire à
l'équilibre**, où toute meilleure réponse rapporte exactement la valeur du jeu et
où l'équilibre est une meilleure réponse à lui-même. C'est ce qui en fait le
contrôle négatif de la section suivante.

**Figure 3 — Référence récitée par série, avec le plafond théorique.** *(`memoire/figures/fig3-recitee.png`)*

Même découpage que la figure 1, mais l'ordonnée porte la référence récitée : le
zéro y est le comportement d'un récitant, et les tirets, l'exploitation parfaite.
C'est un recalage de la figure 1 (§3.1.6) et non une mesure supplémentaire ; il
est tracé parce qu'il rend visible le **franchissement de signe**, que l'échelle
de la figure 1 masque.

Un point mérite d'être relevé, que le chapitre de méthode n'anticipait pas.
**Sans mémoire, l'agent est *en dessous* de l'équilibre** — de 0,111 contre
*Station* et de 0,187 contre *GTO*. La condition sans mémoire ne mesure donc pas
« le niveau récité », comme le §2.2.3 le formulait, mais quelque chose de
sensiblement moins bon qu'un récitant. Le modèle ne joue pas l'équilibre de
mémoire ; il joue moins bien, et la mémoire persistante ne lui sert pas à s'en
souvenir mais à le dépasser.

### 3.3.3 Le contrôle négatif

L'adversaire jouant l'équilibre fournit une falsification interne du dispositif
de mesure. Contre lui, aucune politique ne peut rapporter davantage que
l'équilibre : la référence récitée ne peut pas y devenir positive, ni l'écart
négatif — deux formulations d'une seule condition (§3.1.6). Une violation
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

Contre *GTO*, la mémoire ne sert donc qu'à corriger des erreurs propres — et l'on
notera que l'écart n'y atteint jamais zéro de façon stable, contrairement aux deux
adversaires exploitables. La section 3.6 montrera pourquoi.

### 3.3.4 Ce que ces valeurs doivent au choix de l'équilibre

L'équilibre de Kuhn est une famille à un paramètre et le protocole en a retenu un
membre, α = 1/3 (§2.2.2). Il faut dire ce que les chiffres de cette section lui
doivent, d'autant que la réponse départage nettement les énoncés.

**Le résultat principal n'y doit rien.** L'écart d'exploitation se mesure contre
la meilleure réponse, dont l'espérance est indépendante de l'équilibre choisi ;
il est donc α-libre, et H1 comme H3 avec lui. Il en va de même de l'énoncé central
de cette section : *atteindre exactement le maximum d'exploitation* équivaut à
*afficher un écart nul*, puisque le maximum et l'écart somment à une constante
(§3.1.6). La conclusion « l'agent exploite jusqu'à l'optimum » vaudrait donc à
l'identique pour n'importe quel membre de la famille.

**L'échelle, elle, en dépend entièrement.** L'espérance de la politique
d'équilibre contre les deux adversaires biaisés passe de 1/9 à 2/9 lorsque α va
de 0 à 1/3 ; le plafond de la référence récitée descend en conséquence de 8/9 à
7/9 contre *Over-folder*, et de 2/9 à 1/9 contre *Station*. Les colonnes du
tableau 4 sont donc lisibles à α = 1/3, et à lui seul.

**Une observation change de sens selon α, et c'est celle qu'il faut nuancer.** Le
constat « sans mémoire, l'agent est en dessous de l'équilibre » vaut à α = 1/3 :
il y est à −0,111 contre *Station*. Recalculé contre le membre α = 0 de la
famille, le même agent afficherait +0,001 — soit exactement le niveau de
l'équilibre. Ce que la campagne établit n'est donc pas que le modèle joue mal dans
l'absolu, mais qu'**il n'atteint pas le meilleur équilibre disponible**, ce qui
est une proposition plus faible et plus exacte.

Reste que ce choix est le plus exigeant des trois : α = 1/3 est le membre de la
famille qui exploite le mieux *Station* et *Over-folder*. Le récitant auquel
l'agent est comparé est le plus fort que la théorie autorise, et le dépasser est
donc un résultat plus fort — non plus faible — que s'il avait été comparé à un
récitant plus timide.

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
fenêtre contient trois séries entières, soit quatre cent cinquante manches de
journal brut, là où les notes de l'agent tiennent en 333 à 1 906 caractères
(§3.5). Si l'une des deux conditions dispose de plus d'information à l'instant de
décider, c'est ICL.

### 3.4.2 L'effet mesuré

Les comparaisons portent sur la moyenne des quatre dernières séries plutôt que
sur un point terminal isolé, plus sensible au bruit d'échantillonnage. Elles sont
appariées par réplication : chaque paire ICL − AE compare deux exécutions ayant
reçu les mêmes cartes, manche pour manche.

**Tableau 5 — Effet apparié du mécanisme de rétention.** *(`memoire/tableaux/T5-effet-apparie-H3.csv`)*

| Adversaire | Effet ICL − AE | Écart-type | IC 95 % | Conclusion |
|---|---|---|---|---|
| **Station** | **+0,0381** | 0,0059 | ± 0,0148 | l'intervalle exclut zéro |
| Over-folder | +0,0039 | 0,0023 | ± 0,0056 | l'intervalle contient zéro |

Contre *Station*, la mémoire auto-écrite l'emporte, et l'effet est net : l'écart
résiduel d'ICL est seize fois celui d'AE. Contre *Over-folder*, les deux
mécanismes sont indistinguables — tous deux atteignent l'exploitation parfaite et
s'y tiennent.

**H3 est donc vérifiée, mais sous condition.** Le mécanisme de rétention ne
départage les deux mémoires que contre l'un des deux adversaires exploitables. La
suite de cette section établit ce qui distingue les deux tâches, et ce que cette
distinction dit du mécanisme.

### 3.4.3 Ni la vitesse, ni l'oubli : la complétude

Le chapitre de méthode prévoyait pour la condition ICL un profil d'oubli en dents
de scie : la fenêtre sature à la quatrième série, évince la plus ancienne, et
l'agent perd périodiquement ce qu'il avait appris. **Rien de tel n'apparaît.** La
saturation de la fenêtre ne produit aucun décrochage, ni à la quatrième série ni
ailleurs.

Ce n'est pas la seule prédiction que les données démentent. On attendait aussi
que les deux mémoires se distinguent par leur *vitesse* d'adaptation. Elles ne le
font pas : **les deux conditions chutent à la première frontière**, et dans les
mêmes proportions — contre *Station*, de 0,202 à 0,059 pour ICL, de 0,226 à 0,000
pour AE. Dès qu'un souvenir de la série passée existe, sous quelque forme que ce
soit, l'essentiel de l'adaptation est acquis.

**Figure 4 — Après la première frontière : échelle resserrée.** *(`memoire/figures/fig4-zoom.png`)*

Ce qui les sépare est ce qui se passe ensuite, et la figure 1 l'écrase par son
échelle. **AE se verrouille sur zéro** — la meilleure réponse exacte, atteinte dès
la série 1 et tenue ensuite : sur les vingt-sept séries postérieures à la première
frontière, vingt-trois affichent un écart exactement nul. **ICL s'arrête à un
résidu** : il stagne autour de 0,058 pendant quatre séries, puis dérive lentement
vers 0,040, et **son écart minimal sur les trente séries jouées vaut 0,0083** — il
n'atteint zéro sur aucune d'entre elles.

La différence ne porte donc ni sur la vitesse, ni sur la rétention. Elle porte sur
la **complétude** de ce qui est extrait : là où la synthèse produit une politique
exacte, la réinjection d'historique produit une politique presque exacte, et s'y
arrête définitivement.

L'écart d'exploitation étant une quantité agrégée, il ne dit pas *quelle* décision
est mal jouée. La politique observée le dit. On a vu en 3.1.3 que contre *Station*
le sceau moyen est un point d'indifférence exact ; huit des douze ensembles
d'information le sont, et la qualité de la politique ne se joue que sur quatre
décisions, qui se résument à deux règles — ne jamais engager le sceau faible,
toujours engager le sceau fort.

**Tableau 6 — Les quatre décisions qui décident, contre Station.** *(`memoire/tableaux/T6-quatre-decisions-Station.csv`)*

| Décision | Meilleure réponse | ICL | AE |
|---|---|---|---|
| Engager le sceau faible, en Ouvrant | 0,000 | 0,065 | **0,006** |
| Engager le sceau faible, en Répondant | 0,000 | 0,091 | **0,009** |
| Engager le sceau fort, en Ouvrant | 1,000 | 0,973 | **1,000** |
| Engager le sceau fort, en Répondant | 1,000 | 0,941 | **1,000** |

*Moyennes pondérées sur les quatre dernières séries des trois réplications.*

Après dix séries — mille cinq cents manches, dont les quatre cent cinquante
dernières intégralement présentes dans son prompt — la condition ICL engage encore
le sceau faible dans sept à neuf pour cent des cas, et laisse passer trois à six
pour cent de ses engagements de valeur. La condition AE a supprimé le second
défaut entièrement et ramené le premier sous le pour cent. En décomposant le
résidu d'ICL sur ces quatre décisions : **64 % d'engagements perdants au sceau
faible, 36 % d'engagements de valeur manqués**.

Contre *Over-folder*, la même analyse ne trouve rien à décomposer : les deux
conditions jouent la meilleure réponse exactement.

### 3.4.4 Une règle, ou deux

La comparaison des deux adversaires livre alors une explication, et elle est
simple.

Contre *Over-folder*, la politique optimale tient en **une règle unique et
positive** : engager, quel que soit le sceau. Elle ne demande aucune distinction
entre les cartes, et le journal brut la porte de façon transparente — cent
cinquante engagements suivis de cent cinquante retraits adverses, à chaque série,
n'admettent qu'une lecture. Les deux mécanismes l'extraient immédiatement et
intégralement.

Contre *Station*, la politique optimale demande **deux règles, dont une
négative**, et une distinction entre les sceaux. Cesser de faire quelque chose est
précisément ce qu'un historique brut soutient mal : le journal enregistre ce qui a
été joué et ce que cela a rapporté, mais un engagement perdant y figure comme une
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

*Note de méthode.* Le dimensionnement de la tranche ICL (§2.2.7) supposait que la
dispersion des différences appariées valait 0,0153, comme sur les paires SM − AE
déjà acquises. Elle vaut **0,0059**, soit deux fois et demie moins : les deux
conditions partageant tout sauf le mécanisme, leurs différences sont nettement
moins bruitées. La différence minimale détectable à trois réplications tombe ainsi
de 0,038 à 0,015, et l'effet mesuré la dépasse largement. Le plan retenu était plus
que suffisant, là où le dimensionnement le donnait pour tout juste adéquat.

### 3.4.5 Ce que cette section ne permet pas de conclure

**Le dispositif résout mal ce qu'il montre.** Les deux conditions atteignent
l'essentiel de leur adaptation à la première frontière, c'est-à-dire au premier
point de mesure disponible. Les neuf séries suivantes documentent la persistance
d'un état stable, non la dynamique qui y conduit. Or c'est dans cette dynamique
que se logerait une différence de vitesse, si elle existait. Des séries plus
courtes — cinquante manches plutôt que cent cinquante, pour un coût comparable —
la résoudraient.

**L'absence de décrochage n'est pas une absence d'oubli.** On ne peut pas conclure
qu'une réinjection d'historique n'oublie jamais : seulement qu'à cet horizon, sur
ces adversaires, avec cette taille de fenêtre, elle n'a pas oublié.

**La condition ICL n'a pas été jouée contre l'adversaire à l'équilibre.** Cet
arbitrage est exposé et assumé au §2.2.7. Mais la question a d'abord été posée par
le budget, et la vérification qu'une réinjection d'historique ne bat pas
l'équilibre contre l'équilibre n'a donc pas été faite.

---

## 3.5 Ce que l'agent écrit

Les sections précédentes traitent la mémoire comme une variable : présente ou
absente, auto-écrite ou réinjectée. Elle est aussi un **objet observable**. Le
fichier de notes que l'agent rédige à chaque frontière est conservé intégralement
— quatre-vingt-dix notes, quatre-vingt-douze mille caractères, jamais édités par
l'expérimentateur.

Cette section est la seule de la partie à procéder par lecture plutôt que par
mesure. Elle n'établit pas d'hypothèse ; elle fournit le mécanisme des deux
sections qui l'encadrent.

### 3.5.1 Ce que la mémoire contient

Le dispositif autorisait huit à quinze entrées, avec erreur en cas de dépassement
et sans compaction automatique : l'agent devait hiérarchiser et élaguer lui-même.
Cette contrainte n'a jamais mordu. Sur les quatre-vingt-dix frontières, la note
tient en **une seule entrée dans quatre-vingt-quatre cas** et en deux dans les six
autres ; on relève deux élagages et **aucun dépassement**. La question « que
sacrifie-t-il à saturation ? », posée au protocole, reste donc sans objet.

Ce que l'agent règle de lui-même, en revanche, c'est la longueur, et elle suit la
difficulté du problème : 470 caractères en moyenne contre *Over-folder*, où il n'y
a qu'une régularité à énoncer ; 808 contre *Station* ; 1 337 contre *GTO*, où il
faut détailler sceau par sceau et position par position.

Contre *Over-folder*, l'induction est exacte et complète :

> « Dans "Trois Sceaux", contre cet adversaire (bilan de 150 épreuves), il n'a
> jamais engagé ni couvert. Ouvrant, il a toujours retenu ; Répondant, il s'est
> toujours retiré face à notre engagement. Nos 150 engagements ont donc tous
> rapporté +1, sans coût ni révélation des sceaux. Stratégie : engager
> systématiquement, Ouvrant comme Répondant ; ne pas retenir ni couvrir sauf
> changement manifeste. »
> — *AE-over-folder-r2, frontière de la série 9, écart 0,000*

Tout y est : le constat, sa portée, la stratégie qui en découle, et une clause de
révision. L'expérimentateur n'a fourni que le journal brut des cent cinquante
manches. La distillation est le fait de l'agent, et c'est exactement ce que le
dispositif cherchait à observer.

### 3.5.2 Une mémoire réécrite, non cumulée

Le protocole parlait d'accumulation. Ce n'est pas ce qui se produit. Sur les
quatre-vingt-dix frontières, **soixante-dix comportent une suppression** :
l'agent efface sa note précédente et en écrit une nouvelle, plutôt que d'ajouter à
ce qui existe.

Le traitement qu'il réserve à son propre solde cumulé le montre bien. Trois notes
successives d'une même exécution donnent : « solde cumulé +5 (**remplace l'ancien
−13**) », puis « solde cumulé −20 (**remplace l'ancien +5**) ». La grandeur est
présentée comme cumulée, mais elle ne cumule rien : chaque note rapporte le solde
de la *dernière* série et traite la valeur précédente comme une erreur à corriger.
L'agent ne tient pas un registre, il tient un état.

Ce constat éclaire rétrospectivement la section 3.4. Si la mémoire auto-écrite
n'accumule pas, comment produit-elle une adaptation supérieure ? Parce qu'elle n'a
pas besoin d'accumuler : contre un adversaire stationnaire, une seule série
d'observation suffit à établir la régularité, et c'est bien à la première frontière
que l'écart s'annule. Ce qu'apporte la note n'est pas un cumul de preuves, c'est
une **règle formulée**. Ce que ce mécanisme donnerait face à un adversaire non
stationnaire — où le registre vaudrait mieux que l'état — n'est pas tranché ici.

### 3.5.3 Ce que la mémoire ne contient jamais : une fréquence

Le résultat le plus important de cette section est une **absence**, et elle est
totale.

**Tableau 7 — Ce que les quatre-vingt-dix notes contiennent.** *(`memoire/tableaux/T7-vocabulaire-notes.csv`)*

| Recherché dans les notes | Occurrences |
|---|---|
| Un pourcentage (« 33 % ») | **0** |
| Une proportion en toutes lettres (« un tiers », « une fois sur trois ») | **0** |
| Une fraction numérique (« 1/3 », « 50/50 ») | 2 |
| **Une fréquence prescrite pour sa propre action** | **0** |
| Un quantificateur catégorique (*toujours*, *jamais*, *systématiquement*) | 221 |
| Un quantificateur gradué (*souvent*, *parfois*, *généralement*…) | 228 |

Les deux occurrences numériques méritent d'être citées, parce qu'elles précisent
l'énoncé au lieu de l'affaiblir. La première est un score — « les gains de la
série (+44/150) » — et non une proportion. La seconde en est bien une : « Vael est
**50/50** face au sceau restant ». **L'agent sait donc écrire un rapport**, et il
le fait pour décrire une probabilité d'abattage. Il ne le fait jamais pour
prescrire la fréquence à laquelle il doit lui-même agir. Ce n'est pas le
vocabulaire qui lui manque, c'est l'usage qu'il en ferait pour sa propre
politique.

Le mot « aléatoire » apparaît quatre fois, et jamais à propos de sa propre
stratégie.

Il serait faux de conclure qu'il ne perçoit pas la différence entre un adversaire
déterministe et un adversaire mixte. **Il la perçoit, et son vocabulaire
l'enregistre** :

**Tableau 7 bis — Registre des quantificateurs, par adversaire.** *(`memoire/tableaux/T7bis-registre-par-adversaire.csv`)*

| Adversaire | Catégoriques | Gradués | Part catégorique |
|---|---|---|---|
| Over-folder | 98 | 0 | **100 %** |
| Station | 94 | 20 | 82 % |
| GTO | 29 | 208 | **12 %** |

Face à l'adversaire qui se retire toujours, la totalité des quantificateurs sont
catégoriques. Face à l'adversaire à l'équilibre, ils ne le sont plus que dans un
cas sur huit, et l'agent bascule vers un registre gradué. Le cas de *Station* est
intermédiaire pour une raison qui se lit dans les notes : les formes graduées y
portent toutes sur la **comptabilité des gains** — « les retenues avec Tor coûtent
généralement −1 » — et jamais sur le comportement de l'adversaire, décrit lui de
façon strictement catégorique. Le basculement de registre suit donc bien le
caractère stochastique de ce qui est décrit.

**La détection du caractère stochastique est acquise ; c'est son encodage qui
manque.** Un adverbe gradué ne s'exécute pas comme une fréquence : au moment de
décider, « il couvre souvent avec Vael » ne dit pas s'il faut engager cette
fois-ci. La note tranche donc, et elle tranche catégoriquement :

> « Éviter d'engager avec Tor ou Vael après sa retenue. »
> — *AE-gto-r2, frontière de la série 9*

Tor est le sceau faible. L'équilibre y demande d'engager **une fois sur trois**.
La note prescrit zéro.

C'est le mécanisme complet de la dégénérescence mesurée en 3.6.2, établi ici sur
le canal lui-même et non par inférence : l'agent observe correctement, écrit
fidèlement ce qu'il observe dans le vocabulaire dont il dispose, et ce vocabulaire
ne sait pas porter un tiers.

### 3.5.4 Une note fausse, une stratégie juste

Une note sur les trente écrites contre *Over-folder* inverse les rôles : elle
affirme que l'adversaire « a toujours engagé » alors qu'il n'a pas misé une seule
fois sur les quatre mille cinq cents manches jouées contre lui. La proposition est
fausse, et vérifiablement fausse dans les journaux. L'écart de la série concernée
est pourtant de **0,000** : la stratégie jouée est la meilleure réponse exacte.

Le cas est isolé, mais instructif pour deux raisons. D'abord parce qu'il montre
que **l'explication n'est pas porteuse** : l'agent peut énoncer une justification
fausse tout en jouant juste. Le comportement optimal ne garantit pas que le modèle
du monde qui le sous-tend soit correct — ce qui est précisément la thèse de la
branche *homo silicus*.

Ensuite parce que cette incohérence est **invisible à l'instrument de la section
3.6.1**, qui compare le texte d'une décision à l'action de cette même décision et
jamais le contenu de la mémoire aux faits enregistrés. Un canal entier n'est pas
couvert.

---

## 3.6 L'agent adapté ne sait plus jouer au hasard

Les sections précédentes ont montré un agent qui s'améliore : il exploite ses
adversaires jusqu'à l'optimum, et le mécanisme qui le lui permet est identifié.
H4 pose la question inverse. La littérature documente chez les modèles de langage
des défaillances de décision robustes — incohérence entre le raisonnement
verbalisé et l'action jouée, incapacité à stabiliser une stratégie mixte. Ces
défaillances survivent-elles à l'adaptation, ou celle-ci les corrige-t-elle ?

La réponse est double, et la seconde moitié est le résultat le plus inattendu de
ce travail.

### 3.6.1 Une mesure pré-enregistrée déclarée invalide

La règle d'incohérence prévue au §2.2.5.3 s'est révélée invalide sur ce corpus.
Appliquée à la lettre — comparer l'action jouée à la dernière action nommée dans
le texte libre — elle rend un taux de **47,8 %** sur 13 442 décisions, à un point
des 45,1 % relevés par GTBENCH. Cette proximité est ce qui doit alerter : le
chiffre est un artefact grammatical. La délibération en français conclut
régulièrement par une clause contrastive qui nomme l'option écartée et non celle
retenue — « engager garantit +1, *tandis que retenir* expose à une perte » — et la
règle enregistre une incohérence là où le raisonnement est cohérent. Huit
divergences relues intégralement se sont révélées être huit faux positifs.

Restreinte aux décisions où l'agent **énonce** son choix par une formule explicite,
la mesure donne **0 divergence sur 604**. Sur ce sous-ensemble, l'agent joue
toujours l'action qu'il déclare retenir. Le prix de cette précision est le rappel :
la mesure ne couvre plus que 2,2 % des décisions, et la chaîne de pensée n'étant
pas restituée par le fournisseur (§L.1), elle ne voit qu'une partie du
raisonnement. Le détail des variantes est en annexe C.

Ce constat est conservé plutôt que corrigé en silence : la règle avait été
pré-enregistrée, et son échec fait partie du résultat.

### 3.6.2 La dégénérescence des stratégies mixtes

Contre l'adversaire qui joue l'équilibre, bien jouer exige d'engager le sceau
faible une fois sur trois, et de façon imprévisible. Toujours l'engager, ou ne
jamais l'engager, se punit également : un adversaire qui anticipe la règle ajuste
sa réponse et récupère la différence. L'imprévisibilité est ici la condition de
l'optimalité, et c'est ce que la théorie des jeux appelle une stratégie mixte.

Sans mémoire, l'agent s'en approche : ses fréquences d'engagement se tiennent
autour de 28 %, pour un optimum à 33 %. Dès qu'il a écrit une note, il joue 0 % ou
100 %.

Il n'a pas oublié comment jouer — son écart continue de baisser (§3.3.3). Il a
cessé de tirer au sort.

**Ce que cette dégénérescence coûte, et ce qu'elle ne coûte pas, doit être dit
avec précision.** L'adversaire de cette campagne est une table de décision figée :
il ne modélise personne et ne s'ajuste jamais. Contre lui, cette décision est un
point d'indifférence exact (§3.3.2) — toutes les fréquences rapportent la valeur
du jeu, et l'agent ne perd donc **rien** en abandonnant le mélange. C'est
d'ailleurs pourquoi son écart continue de descendre alors même que sa politique
dégénère : l'instrument principal du mémoire est aveugle à ce phénomène, et il
faut un second instrument pour le voir.

Ce que la dégénérescence coûte est ailleurs, et relève de la nature de la
politique plutôt que de son gain ici. Une politique pure sur cet ensemble
d'information n'est plus une politique d'équilibre : elle est exploitable par tout
adversaire capable de l'observer et de s'y ajuster. L'agent conserve donc son gain
face à un adversaire figé, et perdrait la propriété qui le protégeait face à un
adversaire qui apprend. Le dispositif n'ayant pas d'adversaire adaptatif (§2.2.2),
ce coût est **établi par la théorie et non mesuré ici** : c'est une limite du
protocole, énoncée comme telle en 3.6.3.

**Figure 5 — Fréquence d'engagement au sceau faible contre l'adversaire à l'équilibre.** *(`memoire/figures/fig5-degenerescence.png`)*

**Tableau 8 — Dégénérescence des stratégies mixtes.** *(`memoire/tableaux/T8-degenerescence.csv`)*

| | Séries | Aux bornes 0 ou 1 | Distance moyenne à 1/3 |
|---|---|---|---|
| Sans mémoire | 9 | **0 %** | 0,078 |
| Mémoire auto-écrite, première série, note encore vide | 3 | **0 %** | 0,113 |
| Mémoire auto-écrite, séries suivantes, note écrite | 25 | **56 %** | 0,323 |

Deux précautions déterminent la portée de ce tableau. D'abord, contre un
adversaire exploitable, la meilleure réponse *est* pure : jouer une fréquence de 0
ou de 1 y est optimal, non dégénéré. Agréger les trois adversaires reviendrait à
compter comme un biais une politique correcte, et donnerait 56 % là où le comptage
restreint à l'adversaire à l'équilibre — le seul où le mélange soit requis — donne
**38 %**. Ensuite, toutes les fréquences rapportées sont estimées sur au moins
vingt observations ; une fréquence établie sur trois observations ne dit rien d'un
mélange.

**La deuxième ligne du tableau est un contrôle interne, et c'est elle qui porte la
conclusion.** La première série d'une exécution à mémoire auto-écrite se joue avec
un emplacement mémoire présent mais vide : même modèle, même gabarit de prompt,
même exécution, même adversaire, mêmes cartes — seule la note manque. L'agent y
mélange encore normalement. L'effondrement apparaît exactement à la première série
jouée avec une note écrite. Ce n'est donc pas le modèle qui dégénère, c'est la
note qui le fait dégénérer.

Il faut enfin décrire correctement la forme de cette dégénérescence, car elle
n'est pas un effondrement vers une valeur unique. Sur les vingt-cinq séries
concernées, treize sont à zéro exactement et une à un exactement, avec **sept
sauts de plus de 0,40** entre deux séries consécutives. L'agent choisit une règle,
l'applique intégralement pendant cent cinquante manches, puis en change à la
frontière suivante. **Il remplace une randomisation intra-série par une alternance
inter-séries** : la variabilité que l'équilibre demande existe encore, mais elle
s'est déplacée à une échelle de temps où elle ne produit aucune imprévisibilité à
l'intérieur d'une série — la seule échelle où l'adversaire pourrait en subir
l'effet.

L'explication est dans les notes elles-mêmes (§3.5.3). Sur quatre-vingt-douze
mille caractères, l'agent n'écrit jamais une fréquence. Il écrit « éviter
d'engager avec Tor ». Une note écrite s'exécute ; elle ne se tire pas au sort.

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

**L'adaptation et le biais ne sont pas deux phénomènes qui coexistent par hasard :
c'est le même mécanisme, observé sur deux tâches qui ne demandent pas la même
chose.** Contre un adversaire à faille, où l'optimum est pur, formuler une règle
est exactement ce qu'il faut faire. Contre un adversaire à l'équilibre, où
l'optimum est mixte, c'est ce qu'il ne faut pas faire — et l'agent le fait quand
même, parce que c'est la seule chose que sa mémoire sache faire.

Trois réserves closent cette section. **Le coût de la dégénérescence n'est pas
mesuré, il est déduit.** Face aux bots figés de la campagne, abandonner le mélange
ne coûte rien ; ce qu'il coûte face à un adversaire capable de s'ajuster relève de
la théorie, et le vérifier demanderait un adversaire adaptatif, explicitement hors
périmètre (§2.2.2). Le résultat quantitatif porte par ailleurs sur **un seul
ensemble d'information** : les trois autres ensembles à fréquence d'équilibre
intermédiaire ne sont atteints que si l'adversaire engage, et une, deux et six
séries respectivement y atteignent le seuil d'effectif. Et le taux d'incohérence
n'est établi que sur les décisions où l'agent énonce son choix, soit 2,2 % de la
campagne ; le codage manuel qui aurait permis d'en estimer la portée réelle n'a pas
été conduit.

---

## 3.7 Synthèse

La question de recherche comportait deux branches, et le dispositif a été conçu
pour les instrumenter séparément — c'est sa contribution méthodologique, et c'est
ce qui permet à cette synthèse de dire autre chose qu'un verdict.

**Tableau 9 — Les quatre hypothèses.** *(`memoire/tableaux/T10-synthese-hypotheses.csv`)*

| | Énoncé | Réfutation prévue | Verdict | Limite |
|---|---|---|---|---|
| **H1** | l'adaptation vient de la mémoire | AE ne se distingue pas de SM | **établie** — neuf paires appariées sur neuf, effet de +0,178 à +0,704 | plateau atteint dès la série 2 : on mesure la persistance, pas la vitesse |
| **H2** | elle exploite, elle ne récite pas | l'écart ne descend que contre l'un des deux adversaires biaisés | **établie** — maxima théoriques atteints exactement, contrôle négatif tenu sur 39 séries | l'échelle de la référence récitée dépend du choix α = 1/3 ; l'écart, non |
| **H3** | le mécanisme de rétention compte | ICL égale ou surpasse AE | **établie sous condition** — +0,038 ± 0,015 contre Station, indistinguable contre Over-folder | GTO non joué en ICL ; profil d'oubli jamais observé |
| **H4** | des biais de décision persistent | les fréquences se stabilisent aux valeurs mixtes | **établie sur un volet** — dégénérescence produite par la mémoire ; aucune incohérence explicite détectable | un seul ensemble d'information ; contrôle interne sur trois séries |

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

C'est ici que le résultat cesse d'être confortable, et qu'il devient intéressant.

L'adaptation observée ne cohabite pas avec un biais de décision : **elle le
produit**. Sur l'ensemble d'information où l'équilibre exige d'engager une fois
sur trois, l'agent privé de mémoire joue des fréquences intermédiaires, proches de
la valeur théorique. Dès qu'une note existe, il s'échoue sur les bornes 0 et 1
plus d'une série sur deux, et sa distance à la fréquence d'équilibre quadruple. Le
contrôle interne exclut toute autre explication : la première série d'une
exécution à mémoire, jouée avec un emplacement présent mais vide, ne présente pas
le phénomène.

Le mécanisme est identifié, et il est le même que celui qui produit le succès. Ce
qui rend la mémoire auto-écrite supérieure à la réinjection d'historique (§3.4),
c'est qu'elle contraint l'agent à **formuler une règle** — et c'est en formulant
une règle qu'il achève l'induction là où l'historique brut l'abandonne à quelques
pour cent de l'optimum. Mais une règle écrite en langue naturelle est
déterministe. Les quatre-vingt-dix notes de la campagne le montrent sans
exception : sur quatre cent quarante-neuf quantificateurs, aucune fréquence n'est
jamais prescrite pour sa propre action — ni en pourcentage, ni en proportion, ni
en fraction. L'agent *détecte* pourtant que l'adversaire à l'équilibre est
stochastique : son registre passe de 100 % de quantificateurs catégoriques face à
l'adversaire déterministe à 12 % face à lui. Il sait même écrire un rapport
lorsqu'il décrit une probabilité d'abattage — « Vael est 50/50 face au sceau
restant ». Il ne le fait jamais pour lui-même.

**Le canal qui porte l'adaptation ne sait pas porter une fréquence.** L'adaptation
et le biais ne sont donc pas deux phénomènes qui coexistent : c'est le même
mécanisme, observé sur deux tâches qui ne demandent pas la même chose.

On ne peut donc pas assimiler cette adaptation à une rationalité économique au
sens strict. L'agent optimise, et il optimise remarquablement bien dans un espace
de stratégies pures. Mais l'espace où il optimise n'est pas celui que la théorie
des jeux à information imparfaite lui assigne, et il s'en éloigne au moment même
où il exploite le mieux.

### Ce que le dispositif apporte

Un travail qui n'aurait mesuré que la performance aurait observé un agent qui joue
de mieux en mieux, et conclu à une rationalité accrue. La séparation des trois
dimensions — stratégie exploitative, stratégie d'équilibre, biais de décision —
que la littérature recensée en §1.5.4 confond régulièrement, est ce qui permet
d'observer les deux mouvements à la fois : la politique se rapproche de la
meilleure réponse *et* s'éloigne de l'équilibre, et le second mouvement est la
contrepartie du premier.

Trois résultats méthodologiques accompagnent ces conclusions, et méritent d'être
retenus indépendamment d'elles. La redondance des deux instruments à adversaire
fixé (§3.1.6), qui invalide une figure prévue au plan d'analyse. L'invalidité de
la mesure automatique d'incohérence telle qu'elle était pré-enregistrée (§3.6.1),
dont le taux artefactuel de 47,8 % tombait à un point du chiffre attendu par la
littérature. Et le fait, établi par un audit conduit avant la campagne (§2.4), que
les défauts les plus dangereux d'un tel dispositif ne se logent ni dans son code
ni dans ses journaux, mais à sa frontière avec l'outillage tiers qu'il pilote.

L'ensemble des mesures de ce chapitre a par ailleurs été recalculé par un second
chemin indépendant, écrit dans un autre langage et sans réutiliser le code du
dispositif : les deux calculs coïncident sur les cent soixante-dix-sept séries à
la seizième décimale.

Les limites de ce travail — trois réplications, un seul modèle, une seule tâche,
un horizon de dix séries, un codage manuel non conduit, un contrôle négatif absent
en condition de réinjection d'historique — sont reprises au chapitre suivant.
