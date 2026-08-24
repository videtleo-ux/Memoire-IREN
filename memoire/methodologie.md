# 2. Méthodologie

*Mémoire de M2 — IREN, année 2025-2026. Version de travail, août 2026 — paramètres figés au pilote de calibrage, section 2.4 révisée après audit adversarial pré-campagne.*
*Dispositif : [github.com/videtleo-ux/Memoire-IREN](https://github.com/videtleo-ux/Memoire-IREN)*

> **Note de structure.** Ce document couvre 2.0 (hypothèses), 2.2 (les expériences), 2.3 (l'architecture) et 2.4 (validité interne). La section 2.1 « Présentation d'Hermès Agent » est déjà rédigée ; deux corrections à y apporter sont signalées en annexe A de ce document. Le bloc « Limites » en fin de document est destiné à la section *Limites et extensions* du plan, pas au chapitre de méthode.

---

## 2.0 Des questions aux hypothèses

### 2.0.1 Ce qu'il faut mesurer

La question de recherche comporte deux branches, et la seconde est celle qu'on oublie le plus souvent d'instrumenter :

> Dans un environnement stratégique à information imparfaite doté d'un équilibre théorique calculable, un agent LLM autonome équipé d'une mémoire persistante auto-rédigée développe-t-il une adaptation comportementale s'apparentant à une stratégie — **et si oui**, cette adaptation le rapproche-t-elle de l'optimalité de l'*homo œconomicus*, ou reproduit-elle les biais comportementaux humains ?

La taxonomie établie en revue de littérature (§1.5.4) distingue trois dimensions que les travaux existants confondent régulièrement : le **biais de décision**, la **stratégie GTO** et la **stratégie exploitative**. Le protocole les instrumente séparément, par trois mesures indépendantes.

| Dimension | Ce qu'elle capture | Instrument |
|---|---|---|
| Stratégie exploitative | l'agent punit-il la faille adverse ? | **écart d'exploitation** — §2.2.5.1 |
| Stratégie GTO | l'agent récite-t-il l'équilibre ? | **référence récitée** — §2.2.5.2 |
| Biais de décision | l'agent est-il cohérent et sait-il randomiser ? | **incohérence et dégénérescence** — §2.2.5.3 |

Cette séparation est la contribution méthodologique du dispositif. Un travail qui ne mesure que la performance ne peut pas distinguer un agent qui gagne parce qu'il a compris son adversaire d'un agent qui gagne parce qu'il récite une stratégie robuste face à un adversaire faible — ni, dans les deux cas, dire s'il raisonne de façon cohérente en le faisant.

### 2.0.2 Les quatre hypothèses

**H1 — Il y a adaptation, et elle vient de la mémoire.**
Face à un adversaire exploitable, l'écart d'exploitation d'un agent doté d'une mémoire persistante auto-rédigée décroît au fil des séries, tandis que celui du même modèle privé de mémoire reste stationnaire.
*Mesure* : pente de `Écart(s)` et écart final, condition AE contre condition SM, à donnes appariées.
*Réfutation* : AE ne se distingue pas de SM.

C'est l'hypothèse principale, et le reste du protocole n'existe que pour rendre sa réfutation possible.

**H2 — L'adaptation est exploitative, non récitée.**
L'adaptation observée consiste à s'écarter de l'équilibre dans la direction que commande l'adversaire rencontré : cesser de bluffer contre un adversaire qui paie systématiquement, engager toutes les mains contre un adversaire qui se couche.
*Mesure* : signe et amplitude de la **référence récitée**, par adversaire. Un récitant y reste à zéro par construction.
*Réfutation* : l'écart ne descend que contre l'un des deux adversaires biaisés ; ou la référence récitée devient positive contre l'adversaire jouant l'équilibre, ce qui signalerait un artefact de mesure et non une adaptation.

L'asymétrie des deux adversaires biaisés est le cœur du test : leurs fuites sont opposées, et **aucune stratégie fixe, fût-elle celle de l'équilibre, ne peut faire descendre les deux courbes simultanément**.

**H3 — Le mécanisme de rétention détermine la forme de l'adaptation.**
La mémoire auto-rédigée produit une adaptation plus durable que la simple réinjection de l'historique brut, laquelle présente un profil d'oubli lié à la saturation de la fenêtre de contexte.
*Mesure* : forme de la trajectoire (monotonie, périodicité), écart final, aire sous la courbe, série d'atteinte du plateau ; comparaison appariée AE contre ICL par réplication.
*Réfutation* : ICL égale ou surpasse AE ; ou AE ne présente aucune accumulation.

C'est l'hypothèse qui opérationnalise le **gradient de persistance** de la §1.5.2 : la condition ICL en occupe le premier niveau (adaptation volatile), la condition AE incarne le paradigme de mémoire auto-générée de la §1.5.3, et la condition sans mémoire en constitue le degré zéro.

**H4 — L'adaptation coexiste avec des biais de décision persistants.**
Même lorsque sa politique s'améliore, l'agent conserve les défaillances documentées par la littérature : incohérence entre le raisonnement verbalisé et l'action jouée (GTBENCH : 45,1 % d'erreurs factuelles), et incapacité à stabiliser une stratégie mixte là où l'optimum en exige une.
*Mesure* : taux d'incohérence raisonnement↔action ; concentration des fréquences `π̂` aux bornes 0 et 1.
*Réfutation* : les fréquences se stabilisent aux valeurs mixtes et l'incohérence devient négligeable.

H4 est la branche *homo silicus* de la question. Elle admet un résultat mixte — et c'est précisément ce qui la rend intéressante : un agent peut très bien exploiter efficacement son adversaire **tout en** raisonnant de façon incohérente, ce qui invaliderait l'assimilation de son adaptation à une rationalité économique au sens strict.

---

## 2.2 Présentation des expériences

### 2.2.1 La tâche : une cellule d'observation minimale

L'agent joue au **Poker de Kuhn** en parties répétées, en tête-à-tête, contre un adversaire à politique fixe. Les paiements sont ceux du jeu canonique : trois cartes hiérarchisées, une par joueur et la troisième écartée, un droit d'entrée d'un jeton chacun, un seul tour de décision et une seule taille de mise.

Le choix de ce jeu suit directement du zoom analytique opéré en §1.5.1 : il isole l'agent individuel en situation compétitive 1v1, éliminant les phénomènes émergents de groupe pour garantir une validité interne de premier ordre. Trois propriétés le rendent irremplaçable ici.

**Il est entièrement résoluble.** Douze ensembles d'information, six par position ; une politique se résume à douze probabilités. La meilleure réponse à toute politique adverse se calcule par énumération exhaustive, en arithmétique rationnelle exacte. C'est ce qui autorise une mesure d'exploitation *exacte*, là où la complexité arborescente du Texas Hold'em contraint la littérature à des approximations heuristiques (§1.5.4).

**Il exige une stratégie mixte.** L'équilibre parfait bayésien impose de bluffer et de payer à des fréquences précises. C'est ce qui donne prise à H4 : la difficulté des LLM à randomiser de manière stable est documentée, et devient ici directement observable.

**Il sépare la performance de l'adaptation.** Gagner contre un adversaire faible ne prouve rien. L'écart d'exploitation, lui, mesure la distance à ce qu'un joueur ayant *compris* cet adversaire précis obtiendrait.

Le jeu est servi à l'agent sous une identité et un vocabulaire réécrits — jetons `Tor ≺ Vael ≺ Rhun`, actions *retenir / engager / couvrir / se retirer* — vocabulaire tenu constant dans toutes les conditions et tous les traitements. La portée réelle de ce recodage et ses limites sont discutées en §L.1.

**Valeur induite.** Le paiement est exprimé en jetons, et l'énoncé des règles se clôt sur l'objectif : en accumuler le plus possible. Le dispositif satisfait ainsi les conditions de la théorie de la valeur induite (Smith, 1976) — le signal de récompense est **saillant** (chaque manche produit un solde chiffré immédiat), **monotone** (plus de jetons vaut toujours mieux) et **dominant** (aucun autre objectif n'est proposé à l'agent, aucun outil ne lui est laissé, aucune consigne de style ne concurrence le gain).

### 2.2.2 Les adversaires : trois profils décisionnels contrastés

L'agent affronte trois politiques fixes, connues de l'expérimentateur et jamais de l'agent. Aucune n'est un modèle de langage : ce sont des tables de décision déterministes ou paramétrées, sans coût d'inférence.

| Adversaire | Comportement | Exploitation optimale | Écart d'un récitant |
|---|---|---|---|
| **GTO** | équilibre exact (α = 1/3) | aucune — plafond théorique | `0` |
| **Station** | ne mise jamais, paie toujours | ne jamais bluffer, engager pour la valeur | `1/9 ≈ 0,111` |
| **Over-folder** | ne mise jamais, se couche toujours | engager toutes les mains | `7/9 ≈ 0,778` |

Ce triplet n'est pas un échantillon d'adversaires : c'est un **plan de test**.

**GTO est le contrôle négatif**, et c'est la **référence récitée** qui le teste. Contre un adversaire jouant l'équilibre, aucune politique ne rapporte davantage que l'équilibre lui-même : cette mesure ne peut donc pas y devenir positive. Une valeur positive contre GTO — ou un écart négatif, qui est un maximum diminué d'une valeur — signalerait un défaut de l'instrument et invaliderait les résultats obtenus contre les deux autres adversaires.

L'écart, en revanche, **peut légitimement décroître contre GTO**, et il importe de ne pas y voir un artefact. Il mesure la distance à la meilleure réponse : un agent qui cesse de commettre des fautes grossières s'en rapproche sans exploiter quoi que ce soit, puisque l'ensemble des meilleures réponses à l'équilibre rapporte exactement la valeur du jeu. C'est précisément la distinction que le triplet d'adversaires permet d'établir — contre GTO, une mémoire ne peut que corriger des erreurs propres ; contre Station et Over-folder, elle peut en outre punir une faille. Le contrôle qui tranche entre les deux lectures est la condition sans mémoire : si une telle décroissance venait de l'instrument, elle s'y observerait également, sur les mêmes distributions et le même calcul.

**Station et Over-folder sont le discriminateur.** Leurs fuites sont exactement opposées — sur-paiement contre sur-abandon — et leurs exploitations demandent des ajustements de sens contraire. C'est le test décisif de H2 : un agent qui appliquerait une fréquence de bluff constante, y compris celle de l'équilibre, perd dans les deux directions. La littérature note que les LLM tendent à retomber sur des heuristiques déterministes ou sur des constantes apprises ; ce plan rend ce comportement immédiatement visible.

Le rapport de 7 entre les deux écarts de récitation fournit en outre une échelle : contre Over-folder, la marge d'amélioration disponible est sept fois plus grande, et une adaptation même partielle y sera lisible sans ambiguïté statistique.

### 2.2.3 Les trois traitements : la mémoire comme unique variable manipulée

Le modèle de langage est tenu constant, ainsi que ses paramètres d'inférence, le harnais logiciel, le texte des règles, le format de réponse et la procédure d'extraction de l'action. **Une seule rubrique du prompt change d'un traitement à l'autre.**

| Traitement | Rubrique dans le prompt | Mise à jour en fin de série | Niveau du gradient (§1.5.2) |
|---|---|---|---|
| **SM** — sans mémoire | *aucune* | aucune | degré zéro |
| **ICL** — historique brut | les récapitulatifs des séries passées, fenêtrés | l'expérimentateur empile le récapitulatif ; **aucun appel au modèle** | apprentissage en contexte |
| **AE** — auto-écrite | le fichier de notes de l'agent | l'agent lit le récapitulatif et **réécrit ses notes lui-même** | mémoire auto-générée |

**SM** n'est pas un simple témoin technique. Puisque le modèle a rencontré ce jeu et sa solution durant son pré-entraînement, la condition sans mémoire mesure empiriquement **le niveau de jeu récité** — ce que le modèle produit à partir de sa seule mémorisation, sans aucune expérience de cet adversaire-ci. C'est la ligne de base contre laquelle H1 se juge, et elle est observée, non postulée.

**ICL** représente la solution naïve. La fenêtre est bornée à 52 000 caractères — trois séries entières — et l'éviction se fait par **séries complètes**, jamais en tronquant une série : le profil d'oubli attendu doit provenir de la disparition des séries anciennes, non d'un artefact de découpe. Le dimensionnement de cette fenêtre est justifié en §2.2.6 ; il conditionne la portée de H3.

**AE** est le traitement d'intérêt. Deux propriétés en font l'objet même de l'observation :

- **le contenu est intégralement laissé à l'agent.** L'expérimentateur n'édite jamais ses notes, ne lui suggère rien, ne résume rien pour lui. Le récapitulatif qu'il reçoit est le journal brut de ses manches — une ligne par manche, sans conseil, sans fréquence agrégée, sans interprétation. Distiller la régularité du comportement adverse est précisément le travail dont on mesure la présence ou l'absence ;
- **la capacité est bornée et ne se compacte pas** (environ 2 200 caractères, soit huit à quinze entrées). Un dépassement produit une erreur, pas une troncature : l'agent doit hiérarchiser et élaguer lui-même. Ce qu'il choisit de sacrifier à saturation constitue une observation qualitative en soi.

Les deux traitements à mémoire reçoivent **exactement la même matière première**. Seul le mécanisme de rétention diffère — sans quoi H3 comparerait deux informations et non deux mémoires.

### 2.2.4 La série : l'unité d'adaptation

Une exécution se décompose en **séries** ; une série est une suite de K manches jouées sous un état mémoire fixe. Un point sur la courbe d'adaptation correspond à un état mémoire, et à un seul.

Ce découpage est une condition de la mesure, non un confort de mise en œuvre. La politique observée s'énonce comme *« la politique de l'agent étant donné l'état mémoire M<sub>s</sub> »*. Si la mémoire évoluait au cours des K manches, l'échantillon ne serait plus celui d'une politique mais le mélange de plusieurs, et l'écart calculé perdrait son sujet.

La mémoire est donc **capturée à l'ouverture de la série, figée pendant toute sa durée, et mise à jour uniquement à la frontière**. Le gel porte sur le *moment* où une modification prend effet, jamais sur son *contenu*. Trois raisons le justifient :

1. la définition même de la mesure, ci-dessus ;
2. la comparabilité : le traitement ICL est figé intra-série par construction ; si AE pouvait se mettre à jour en cours de route, les deux traitements différeraient par le mécanisme *et* par la fréquence de mise à jour, et H3 ne serait plus identifiable ;
3. la pureté du canal : le contexte étant neuf à chaque manche, l'agent n'accumule rien d'une manche à l'autre ; autoriser une écriture intra-série créerait un canal d'apprentissage parasite, fondé sur une information partielle.

**Ce gel est imposé par l'expérimentateur au niveau du système de fichiers**, et non hérité du comportement natif de l'agent (voir annexe A.1 : sous invocation *one-shot*, le mécanisme natif ne le fournit pas). Les tentatives d'écriture en cours de série ne sont pas ignorées pour autant : chacune est **détectée, enregistrée, puis annulée**. « L'agent cherche-t-il à prendre des notes pendant qu'il joue ? » est une observation.

Réinitialisations aux trois échelles : entre exécutions, tout est neuf (mémoire vierge) ; entre séries d'une même exécution, **aucune** — l'accumulation est l'objet de l'étude ; à l'intérieur d'une série, contexte neuf à chaque manche et mémoire gelée.

### 2.2.5 Les trois instruments de mesure

#### 2.2.5.1 L'écart d'exploitation — la stratégie exploitative

La variable dépendante principale n'est ni le gain ni le taux de victoire, deux quantités qui confondent la qualité du jeu et la chance de la distribution.

> **Écart(s) = EV(meilleure réponse à l'adversaire) − EV(politique observée)**

Exprimé en jetons par manche et moyenné sur les deux positions, il se lit directement : **ce que l'agent laisse sur la table à chaque coup**, faute d'exploiter parfaitement la faille de son adversaire. Zéro signifie exploitation optimale.

Trois propriétés en font l'instrument central :

- **il est exact**. Six distributions équiprobables et un arbre de profondeur au plus trois : l'espérance de toute politique contre toute autre se calcule par énumération complète, en fractions rationnelles. Aucune simulation, aucun intervalle de confiance sur la mesure elle-même ;
- **il est insensible à la chance**. Il porte sur la politique observée, non sur les gains réalisés. Un agent qui joue parfaitement et perd sur une série de mauvaises distributions affiche un écart nul ;
- **il est borné par un étalon interprétable** : `0` pour la meilleure réponse, et l'écart du récitant (`1/9`, `7/9`) comme repère.

La politique observée `π̂(M_s)` est estimée par les fréquences brutes de l'agent sur chacun des ensembles d'information, sur les manches de la série. Les décisions où le harnais a dû imposer une action faute de réponse exploitable sont **exclues** du comptage et rapportées à part : elles renseignent sur le harnais, non sur la politique de l'agent. Les ensembles d'information non atteints — six d'entre eux le sont systématiquement face aux adversaires qui ne misent jamais — sont comblés par convention à la valeur d'équilibre et signalés ; leur valeur n'affecte ni l'espérance ni l'écart, puisqu'ils sont inatteignables.

#### 2.2.5.2 La référence récitée — la stratégie GTO

> **Référence récitée = EV(politique observée) − EV(équilibre)**, contre le même adversaire.

Elle mesure la distance au comportement d'un pur récitant. Un agent qui applique l'équilibre y reste à zéro **quel que soit l'adversaire** ; un agent qui exploite s'en écarte positivement, et d'autant plus que l'adversaire est biaisé. C'est l'instrument de H2, et le passage de l'obfuscation en limite (§L.1) en fait la mesure co-principale du dispositif : puisqu'on ne peut pas garantir que l'agent ignore l'équilibre, on mesure explicitement à quelle distance de lui il se place.

#### 2.2.5.3 Incohérence et dégénérescence — le biais de décision

Cet axe instrumente la branche *homo silicus* de la question (H4), et il n'existe dans aucun des cadres d'évaluation recensés en §1.4.3.

**Incohérence raisonnement↔action.** L'agent est contraint de délibérer librement avant d'énoncer son action sur une ligne dédiée, et l'intégralité du texte est conservée. On mesure, sur la totalité des décisions, la divergence entre l'action que le raisonnement désigne et celle qui est effectivement jouée. Deux niveaux :

- *automatique*, sur 100 % des décisions : comparaison entre l'action extraite de la ligne d'action et la dernière action nommée dans le texte libre qui la précède. C'est une **borne inférieure** du taux d'incohérence — elle n'attrape que les contradictions explicites ;
- *codage manuel*, sur un échantillon stratifié (~20 décisions par exécution), selon les cinq catégories d'erreur de GTBENCH — erreur factuelle, non-détection de fin de partie, excès de confiance, mésinterprétation d'état, erreur de calcul. Le taux de faux négatifs de la mesure automatique en est déduit et rapporté.

**Dégénérescence des stratégies mixtes.** L'équilibre exige des fréquences intermédiaires sur plusieurs ensembles d'information. On mesure la concentration de `π̂` aux bornes 0 et 1, et sa distance aux fréquences d'indifférence. Un agent qui alterne entre des phases purement passives et purement agressives, plutôt que de mélanger, produit une signature immédiatement lisible sur cette mesure.

Cet axe autorise un résultat que le dispositif seul de la performance ne pourrait pas produire : **une adaptation efficace accompagnée d'un raisonnement incohérent**, qui interdirait d'assimiler l'agent à un optimisateur rationnel même s'il exploite correctement son adversaire.

### 2.2.6 Plan de campagne et contrôle de l'aléa

**La matrice.** 3 traitements × 3 adversaires × 3 réplications = **27 exécutions** dans le plan nominal ; **24 dans le plan effectif**, la condition ICL étant restreinte à deux adversaires pour la raison exposée en §2.2.7. Chaque réplication reçoit sa propre séquence de distributions ; elles capturent la variabilité conjointe de la distribution des cartes et de la stochasticité du modèle.

**L'appariement.** Les trois traitements d'une même réplication reçoivent des distributions **strictement identiques**, manche par manche — technique des nombres aléatoires communs. Les tirages de l'adversaire stochastique sont eux aussi appariés. Le design est donc **intra-sujet à environnement commun** : les comparaisons entre traitements se font à cartes égales, ce qui élimine la variance due à la distribution et rend possible une comparaison appariée sur trois réplications malgré la faiblesse de l'effectif. C'est un contrôle plus fort que l'assignation aléatoire aux traitements, puisqu'il annule la source de variance principale au lieu de l'équilibrer en espérance.

L'alternance des positions est déterministe — l'agent ouvre les manches impaires, répond les manches paires — de sorte que l'équilibre est exact et identique dans toutes les cellules. Toutes les quantités rapportées sont moyennées sur les deux positions.

**Vérification.** À la clôture de chaque exécution, l'empreinte de la séquence de distributions est recalculée depuis la graine et confrontée à celle des exécutions appariées. L'appariement est ainsi *prouvé a posteriori*, et non seulement organisé a priori.

**Paramètres.**

| Paramètre | Valeur | Justification |
|---|---|---|
| Modèle | `openai/gpt-5.6-luna` | arrêté au pilote ; 100 % de réponses exploitables sur 260 décisions |
| Effort de raisonnement | `medium` | mesuré équivalent à `low` en coût et en latence ; retenu pour écarter toute objection de bridage |
| Manches par série (K) | **150** | validé au pilote : l'écart y diffère de 0,0032 de celui mesuré à K = 200 |
| Réplications | 3 | contrainte de budget ; compensée par l'appariement |
| Séries — SM | 3 | rien à accumuler ; trois points établissent le niveau récité et sa dispersion |
| Séries — ICL et AE | 8 à **16** | arrêt automatisé au plateau, borné des deux côtés |
| Fenêtre ICL | **52 000 caractères** (~18 000 tokens) | contient trois séries entières — cf. encadré ci-dessous |

La **règle d'arrêt** est automatisée et enregistrée à chaque évaluation : le plateau est déclaré lorsque, avec au moins huit séries, la pente de la régression de l'écart sur les quatre dernières est supérieure ou égale à `−0,02` jeton/manche/série **et** que la dispersion de ces quatre valeurs est inférieure à `0,05`. Les deux conditions sont nécessaires : la pente seule déclarerait un plateau sur une trajectoire périodique, la dispersion seule le déclarerait au milieu d'une descente lente. L'exécution se poursuit ensuite deux séries au-delà, afin que le plateau soit constaté et non anticipé. Le plafond de seize séries borne le coût **sans toucher à la règle** : en faire un compte fixe reviendrait à remplacer un critère scientifique par une contrainte budgétaire, ce qu'il faudrait alors énoncer comme tel.

> **Le dimensionnement de la fenêtre ICL est une décision de validité, pas de budget.** Le récapitulatif pèse 109 caractères par manche (mesuré), soit 16 300 caractères pour une série de 150 manches. Avec une fenêtre étroite et une éviction par séries entières, la condition ICL n'aurait retenu qu'**une seule** série passée : elle aurait été incapable d'accumuler *par construction*, et H3 se serait réduite à « une mémoire qui ne peut pas accumuler n'accumule pas » — un artefact de paramétrage présenté comme un résultat. La fenêtre est donc fixée à 52 000 caractères, soit trois séries : ICL accumule, puis sature et évince, ce qui rend la comparaison avec AE informative dans les deux sens. L'alternative envisagée — comprimer le récapitulatif pour en faire tenir davantage — a été écartée : elle aurait modifié le **stimulus** que les deux conditions consomment, et non un paramètre de la condition étudiée.
>
> La fenêtre est bornée **en caractères**, et non en tokens, faute d'un compteur de tokens accessible au dispositif. Le rapport de conversion retenu à l'origine — quatre caractères par token — s'est révélé faux à la mesure : le français de ces récapitulatifs se découpe à raison de **2,8 caractères par token**. La fenêtre pèse donc environ 18 000 tokens et non 13 000. Cela ne change ni le comportement recherché ni la comparabilité — l'éviction porte sur des séries entières, et le seuil est identique pour les neuf exécutions ICL —, mais l'écart est rapporté ici parce qu'il conditionne l'enveloppe budgétaire (§2.2.6) et qu'un paramètre exprimé dans une unité que le dispositif ne mesure pas doit être énoncé comme tel.

**Pilote de calibrage.** Une exécution courte précède la campagne et tranche, dans cet ordre de véto : taux de réponses exploitables (seuil de 98 %), coût par manche et projection budgétaire, stabilité de `π̂` à K = 200, latence, puis constantes de la règle d'arrêt. Les paramètres élus sont figés avant la campagne : un changement en cours de route rendrait les exécutions non comparables.

Le pilote a été conduit en sept exécutions réelles, couvrant les trois traitements. Ses sorties :

1. **Taux de réponses exploitables : 260 sur 260**, sans une seule relance ni action imposée — très au-dessus du seuil de véto.
2. **Coût mesuré : 0,86 millième de dollar par décision**, soit 0,172 $ pour une série de 200 manches. La projection qui en découlait — 47 $ au plateau, 70 $ au plafond — s'est révélée trop basse d'un facteur deux, pour deux raisons découvertes après coup (§2.4) : le texte français se découpe en tokens à raison de 2,8 caractères et non 4, et le fournisseur facture une prime d'écriture de cache sur un cache qu'il ne relit jamais. **Projection révisée sur mesures réelles : 83 $ si le plateau survient à dix séries, 137 $ au plafond**, dont neuf dixièmes imputables aux séries ICL à fenêtre pleine. L'écart entre les deux projections est lui-même instructif : une enveloppe budgétaire estimée sur un prompt court ne se transpose pas à un prompt long, et le poste qui explose est précisément celui de la condition dont dépend l'hypothèse H3.
3. **Stabilité de `π̂` : K = 150 validé sur pièces.** Les distributions étant dérivées de `(graine, r, s, k)`, les 150 premières manches d'une série de 200 *sont* la série de 150, à l'octet près : l'écart se recalcule donc par sous-échantillonnage, sans exécution supplémentaire. Résultat : |écart(K=150) − écart(K=200)| = **0,0032**, quinze fois sous le seuil retenu.
4. **Latence : 11,7 secondes par décision** en condition sans mémoire, 14,1 en condition ICL à fenêtre pleine — soit vingt-huit à trente-cinq minutes par série. L'unité parallélisable étant l'exécution, trois en parallèle placent la campagne autour de trente-cinq heures. Le degré de parallélisme n'est pas librement choisi : au-delà de trois exécutions simultanées, le compte heurte la limite de débit du fournisseur (§2.4).
5. **Sensibilité du dispositif vérifiée.** L'écart mesuré en condition sans mémoire s'établit à 0,23, loin de zéro : il reste toute la marge nécessaire pour qu'une adaptation soit observable. L'hypothèse d'un effet plafond — un modèle si compétent que la mémoire ne changerait rien — est écartée.

L'effort de raisonnement a fait l'objet d'un test dédié, deux séries de 200 manches jouées **sur les mêmes distributions** : `low` et `medium` produisent le même volume de sortie (445 contre 427 tokens), la même latence et le même coût. `medium` est retenu, puisqu'il ne coûte rien de plus et qu'il retire par avance l'objection d'un modèle bridé pour des raisons budgétaires.

### 2.2.7 Dimensionnement de la tranche ICL

La première tranche — dix-huit exécutions, conditions SM et AE — a coûté 13,01 $. La tranche ICL en coûterait, aux prix mesurés, 62 $ si le plateau survient à dix séries et 106 $ si toutes les exécutions vont au plafond : un facteur cinq à huit, entièrement imputable aux séries à fenêtre pleine, où le prompt servi atteint 51 000 caractères. La question d'une réduction se pose donc, et elle est tranchée ici, *avant* la tranche et sur des critères énoncés — faute de quoi le budget déciderait en silence.

**Le seuil de détectabilité, estimé sur les données déjà acquises.** Le plan étant apparié, la quantité qui gouverne la précision n'est pas la dispersion des niveaux mais celle des **différences par réplication**. Mesurée sur les dix-huit exécutions de la première tranche, elle vaut `σ = 0,0153` jeton/manche, et elle est homogène d'une cellule à l'autre (0,011 à 0,020). La différence minimale détectable au seuil de 95 % en découle :

| Réplications | *t* (95 %) | Effet minimal distinguable de zéro |
|---|---|---|
| 2 | 12,706 | **0,138** |
| **3** | 4,303 | **0,038** |
| 4 | 3,182 | 0,024 |
| 6 | 2,571 | 0,016 |

Le passage de trois à deux réplications ne coûte pas un tiers de précision : il en coûte **3,6 fois**, parce qu'un unique degré de liberté fait bondir le *t* de Student de 4,3 à 12,7. La falaise du plan expérimental tombe exactement là.

**L'effet que H3 doit détecter.** Il s'estime sur l'exécution ICL déjà conduite à K = 150, confrontée à son homologue AE sur les mêmes distributions : la différence ICL − AE vaut +0,076, +0,060 puis +0,045 aux séries 1 à 3. **L'effet attendu, de l'ordre de 0,045, dépasse à peine la différence détectable à trois réplications, et se situe six fois en dessous de celle à deux.** À deux réplications, l'expérience ne serait pas moins précise : elle serait *non concluante*, c'est-à-dire une dépense sans résultat — l'issue la plus coûteuse de toutes. Trois réplications constituent donc un plancher, non un confort.

**Trois leviers écartés.** Le nombre de **réplications**, pour la raison ci-dessus. Le nombre de **séries** : la fenêtre contient trois séries, l'éviction ne commence donc qu'à la quatrième, et l'exécution disponible s'arrête précisément avant — le décrochage que H3 prédit lorsque la fenêtre sature n'a jamais été observé, et raccourcir les séries reviendrait à interrompre l'expérience avant l'événement qu'elle cherche. Le nombre de **manches par série**, enfin : SM et AE sont joués à K = 150, et un ICL plus court romprait l'appariement avec les dix-huit exécutions acquises. Cette économie-là détruirait l'actif qu'elle prétend ménager.

**Le levier retenu : l'adversaire jouant l'équilibre.** H3 compare deux mécanismes de **rétention d'information exploitable**. Contre GTO, il n'y a rien à retenir qui serve : l'adversaire n'a pas de faille, et la question de savoir quel dispositif mémoriel conserve le mieux une régularité exploitable n'a pas d'objet là où il n'en existe aucune. Le contrôle négatif, lui, est déjà acquis — trente séries en SM et en AE contre GTO, référence récitée jamais positive (§2.2.2). La tranche ICL se limite donc à **Station et Over-folder, trois réplications, K = 150 : six exécutions**.

| Plan | Exécutions | Plateau à 10 séries | Plafond 16 séries |
|---|---|---|---|
| 3 adversaires × 3 réplications | 9 | 62 $ | 106 $ |
| **2 adversaires × 3 réplications** | **6** | **41 $** | **71 $** |
| 2 adversaires × 2 réplications | 4 | 27 $ | 47 $ — *non concluant* |

**La contrainte de coût, énoncée comme telle.** Il serait malhonnête de présenter ce retrait comme une décision purement scientifique : *la question a été posée par le budget*. Ce qui relève de la méthode, c'est la réponse — le refus de toucher aux réplications, aux séries et à K, où l'économie aurait détruit la mesure, et le choix de la seule coupe qui laisse H3 intacte. Ce que l'on perd est identifiable : la vérification que la condition ICL ne bat pas l'équilibre contre un adversaire à l'équilibre. Elle est redondante avec ce qu'établissent SM et AE, mais elle n'est pas nulle, et **elle n'aurait pas été retirée sans la contrainte financière**. C'est une économie justifiée, non une économie neutre. Portée à l'ensemble, la campagne revient à 54 $ dans le scénario de plateau et 84 $ au pire, contre 83 à 137 $ pour la matrice complète des vingt-sept exécutions.

**Deux réserves.** D'abord, `σ` est estimé sur SM et AE puis extrapolé à ICL, alors que le fenêtrage introduit une dépendance au contenu susceptible d'accroître la variabilité ; si la différence détectable réelle excédait 0,038, H3 se trouverait à la limite du mesurable, et il faudrait l'écrire plutôt que de conclure. Ensuite, la différence ICL − AE **décroît** sur les trois séries observées : la condition ICL rattrape tant que sa fenêtre n'a pas saturé. Si la saturation ne produisait pas le décrochage attendu, l'effet final pourrait passer sous le seuil — ce serait un résultat en soi, à condition de pouvoir l'affirmer, ce qui suppose précisément les trois réplications retenues.

> **Ce que la tranche a effectivement donné.** La première réserve s'est levée dans le bon sens : la dispersion des différences appariées ICL − AE vaut `0,0059` contre Station, soit **deux fois et demie moins** que celle des paires SM − AE sur laquelle le dimensionnement était calibré. Les deux conditions partageant tout sauf le mécanisme — même matière première, mêmes distributions, même modèle —, leurs différences sont nettement moins bruitées que celles qui séparent deux traitements éloignés. La différence détectable à trois réplications tombe ainsi à `0,015`, et l'effet mesuré (`+0,038`) la dépasse largement. Le plan retenu était donc plus que suffisant, là où ce dimensionnement le donnait pour tout juste adéquat. La seconde réserve, elle, s'est confirmée : la saturation de la fenêtre n'a produit aucun décrochage, et c'est la vitesse d'adaptation, non la rétention, qui sépare les deux mémoires (résultats, §2.4).

### 2.2.8 Plan d'analyse

1. **Trajectoires d'adaptation** — figure centrale : `Écart(s)` par série, en grille 3 traitements × 3 adversaires, tracés individuels des réplications et moyenne, avec deux lignes de référence : `y = 0` (exploitation optimale) et l'écart du récitant. Test visuel et quantitatif de **H1** et **H3**.
2. **Trajectoire (écart, référence récitée)** — par série et par adversaire. Test de **H2** : un récitant reste au voisinage de zéro sur la seconde coordonnée ; un exploiteur s'en écarte, dans des directions dictées par l'adversaire.
3. **Comparaison appariée AE contre ICL** par réplication : écart final, aire sous la courbe, série d'atteinte du plateau. Compte tenu de trois réplications, on rapporte des **effets appariés et des intervalles bootstrap**, non des tests d'hypothèse dont la puissance serait décorative.
4. **Biais de décision** — taux d'incohérence et dégénérescence des mixtes, par traitement et par série. Test de **H4** ; on examine en particulier si l'incohérence décroît avec l'adaptation ou lui survit.
5. **Contenu du canal mémoire** — analyse qualitative des notes aux frontières : l'agent identifie-t-il la régularité adverse ? son élagage est-il destructeur ? une écriture donnée précède-t-elle un palier ?
6. **Contrôles** — équilibre des positions, taux de réponses imposées par traitement, taux de reconnaissance du jeu (covariable, §L.1), coût.

---

## 2.3 Architecture du dispositif

Le dispositif a été entièrement développé pour cette recherche : il n'existait aucun cadre permettant de faire jouer un agent à mémoire persistante en séries répétées avec mesure exacte de l'exploitation. Il est présenté ici dans ses grandes lignes ; le code, ses spécifications et sa suite de tests sont publics.

Quatre couches, aux responsabilités disjointes :

- **le moteur de jeu** — les règles et l'instrument de mesure ; il ne communique avec aucun modèle de langage et calcule meilleures réponses et écarts en arithmétique exacte ;
- **le harnais mémoire** — tout ce que l'agent lit et tout ce qu'il produit ; il compose le prompt, invoque le modèle, extrait l'action du texte libre, et incarne les trois traitements ;
- **le journal** — l'enregistrement, validé à l'écriture ; les fichiers d'analyse en sont dérivés ;
- **l'arbitre** — l'orchestration : distribution des cartes, alternance des positions, gel de la mémoire, frontières de série, mesure, règle d'arrêt.

Deux choix ont des conséquences méthodologiques directes.

**Les distributions sont dérivées, non tirées.** La carte servie à la manche *k* de la série *s* de la réplication *r* est une fonction déterministe de la graine de campagne et de ce triplet. Aucun état de générateur pseudo-aléatoire ne circule d'une manche à la suivante : deux traitements au même triplet reçoivent des cartes identiques **par construction, et non par discipline** — propriété qui serait autrement fragile, et dont aucun journal ne révélerait la violation après coup.

**L'isolation des exécutions est vérifiée, jamais supposée.** Le fichier de notes de l'agent vit dans son répertoire personnel : deux exécutions parallèles sur une même machine s'écraseraient mutuellement la mémoire en silence — et une exécution contaminée ne se lit pas comme une anomalie dans les résultats, elle se lit comme de l'adaptation. Chaque exécution dispose d'un répertoire dédié, et un marqueur unique y est écrit *par l'agent lui-même* puis recherché dans tous les autres répertoires avant tout démarrage. L'échec de cette vérification interdit le démarrage.

Une troisième contrainte n'a pas de portée théorique mais une conséquence méthodologique : **le prompt est transmis au sous-processus par fichier, et non en argument de ligne de commande**. La fenêtre ICL pleine dépasse la longueur maximale admise pour une ligne de commande par le système d'exploitation ; y adapter le protocole aurait signifié réduire le nombre de manches par série ou la taille de la fenêtre, c'est-à-dire laisser une limite d'outillage fixer un paramètre expérimental (§2.4).

Le dispositif est couvert par 223 tests automatisés, dont un oracle analytique du moteur de mesure — les valeurs d'équilibre et d'exploitation ont été re-dérivées à la main et sont vérifiées exactement — et une procédure de **rejeu** qui re-règle chaque manche depuis les seuls journaux et retrouve les mesures publiées. L'expérience est donc reconstructible dans son intégralité à partir des données déposées.

> **Code, spécifications, journaux :** [github.com/videtleo-ux/Memoire-IREN](https://github.com/videtleo-ux/Memoire-IREN)

---

## 2.4 Validité interne

La validité interne repose sur le contrôle de l'environnement de choix et sur l'identification du traitement (Jacquemet & L'Haridon, 2016 ; Jacquemet & Le Lec, 2017). Le tableau ci-dessous recense les menaces identifiées et le dispositif qui y répond.

| Menace | Dispositif |
|---|---|
| Confusion traitement × harnais | chemin logiciel unique pour les trois traitements ; prompts identiques hors la rubrique mémoire ; empreinte du texte de règles enregistrée sur chaque ligne de journal |
| Reconnaissance du jeu, récitation | recodage vérifié automatiquement ; double détecteur sur les sorties **et** sur le canal mémoire, recalculable *a posteriori* ; identification portée par l'asymétrie des adversaires (cf. §L.1 bis) |
| **Fuite du dispositif vers l'agent** | sous-processus confiné dans un répertoire vide ; **répertoires d'exécution nommés par un code opaque**, le chemin étant lui-même servi à l'agent ; contenu intégral du prompt système lu et comparé au journal (cf. encadré ci-dessous) |
| **Panne de fournisseur prise pour une réponse** | verdict d'échec lu dans le rapport d'usage de l'outil lui-même, les signatures textuelles ne servant plus que de second filet ; manche rejouée à distribution identique ; interruption de l'exécution après trois tentatives |
| **Limite de débit confondue avec une panne** | délai de reset lu et attendu, tentative rejouée sans être décomptée ; attentes bornées et remontées |
| **Champ de journal ne mesurant pas ce qu'il nomme** | tokens d'entrée enregistrés en trois postes distincts — entrée nette, cache lu, cache écrit — le fournisseur ne comptant l'entrée que nette du cache |
| Variance de la distribution | distributions dérivées et appariées entre traitements ; mesure portant sur la politique et non sur les gains |
| Contamination entre exécutions | répertoire de mémoire dédié par exécution ; marqueur d'isolation écrit par l'agent et vérifié avant démarrage et à la clôture |
| Violation silencieuse du gel | instantané restauré avant chaque manche ; toute tentative d'écriture enregistrée |
| Fuite d'information dans les récapitulatifs | la carte de l'adversaire n'y figure que si elle a été dévoilée au jeu ; vérifié par test exhaustif |
| Réponses inexploitables biaisant `π̂` | exclues du comptage et rapportées séparément ; seuil de véto au pilote |
| Dérive du matériel entre traitements | modèle, paramètres d'inférence et énoncé des règles figés et enregistrés à chaque appel |
| Perte de données en cours de campagne | journaux en ajout seul ; reprise à la frontière de série ; série interrompue rejouée intégralement, tentative avortée conservée à part |

Le contrôle négatif que constitue l'adversaire jouant l'équilibre mérite d'être souligné : il fournit une **falsification interne** du dispositif de mesure lui-même. Deux observations l'activeraient et invalideraient l'ensemble des mesures de la campagne : une **référence récitée positive** contre lui — un agent qui gagnerait plus que l'équilibre face à l'équilibre — ou un **écart négatif**. La décroissance de l'écart contre GTO, elle, est admissible et attendue : elle traduit la disparition d'erreurs propres et non une exploitation, et s'en distingue par le fait qu'elle ne s'accompagne d'aucun gain au-delà de la valeur du jeu (§2.2.2).

#### Trois canaux de contamination, et la procédure qui les a trouvés

Le calibrage puis un audit adversarial ont mis au jour trois défauts qui n'apparaissaient dans aucun test automatisé et qu'aucun journal n'aurait signalés. Ils sont rapportés ici parce qu'ils appartiennent au même genre : **des défaillances qui ne ressemblent pas à des erreurs dans les résultats, mais à des résultats.**

**Le premier tenait à l'échafaudage de l'agent.** L'outil utilisé explore le répertoire de travail à la recherche de fichiers de consignes et les verse dans son prompt système. L'arène étant exécutée depuis le dépôt du projet, l'agent recevait à chaque manche un document décrivant le jeu réel, la constante d'équilibre et l'exploitation propre à chaque adversaire. Mesuré : 11 633 octets de consignes du dépôt dans le prompt système, contre zéro depuis un répertoire vide. Autrement dit, l'agent disposait de la solution de l'expérience — et sa « reconnaissance du jeu » n'en était pas une (cf. §L.1 bis). *Remède* : le sous-processus est confiné dans un répertoire vide dédié, sous le magasin isolé de l'exécution ; un test de non-régression y place un fichier de consignes piégé et vérifie qu'il n'est pas lu.

**Le second tenait au canal d'erreur.** Une panne de fournisseur — quota épuisé, limite de débit — était restituée sur la sortie standard avec un code de retour nul. Le harnais la prenait pour une réponse du modèle : l'extraction d'action échouait, l'action passive était imposée, et l'exécution se terminait normalement en ayant enregistré des dizaines de décisions par défaut **comme des données**. *Remède* : les signatures d'échec de fournisseur sont reconnues et converties en erreur ; la manche est alors rejouée à distribution identique, et l'exécution s'interrompt après trois tentatives infructueuses plutôt que de produire des données douteuses.

**Le troisième tenait au nom des répertoires.** Il n'a pas été trouvé par les tests, mais par un audit conduit après le calibrage, sur un dispositif alors réputé terminé (voir ci-dessous). L'outil insère dans son prompt système le chemin du répertoire de travail et celui du magasin mémoire de la session — deux lignes qu'aucune option ne désactive. Or les répertoires d'exécution portaient le nom de la cellule expérimentale : `SM-station-r1`, `AE-over-folder-r2`. L'agent recevait donc à chaque manche le nom de son adversaire — et « station » comme « over-folder » ne sont pas des étiquettes neutres : ils **énoncent la faille à exploiter**, la première désignant en jargon le joueur qui paie tout, la seconde celui qui se couche trop. Le traitement mémoire lui était livré par la même voie. *Remède* : le répertoire d'une exécution est désormais un code opaque dérivé par hachage de la graine et de l'identifiant ; la correspondance lisible ne vit que dans les journaux, que l'agent ne voit jamais. Ce défaut est le plus instructif des trois : il **survivait au correctif du premier**. Confiner le sous-processus dans un répertoire vide empêchait la lecture de fichiers de consignes, mais le chemin de ce répertoire restait, lui, servi à l'agent.

Ces trois corrections invalident les exécutions de calibrage qui les précèdent ; celles-ci ont été rejouées. On en tire un principe de conduite pour la campagne : **la frontière entre le dispositif expérimental et l'outillage tiers qu'il pilote est l'endroit où les défauts silencieux se logent**, et elle mérite une vérification empirique propre — lire ce que l'agent reçoit réellement — et non seulement une couverture par les tests.

#### L'audit adversarial comme procédure de validité

Le dispositif étant destiné à consommer vingt-sept exécutions et deux jours de calcul, il a été soumis, **avant la campagne et non après**, à un audit adversarial documenté. Le cahier des charges remis à l'auditeur n'était pas « vérifie que c'est correct » — deux cent une vérifications automatisées s'en chargeaient déjà — mais deux questions : *que peut voir l'agent qu'il ne devrait pas voir ; qu'est-ce qui pourrait être enregistré comme une donnée sans en être une.* L'auteur y déclarait ses propres angles morts, dont celui-ci : avoir mesuré la taille du prompt système sans jamais en lire le contenu.

L'audit a produit quatre constats. Le premier est le canal de contamination décrit ci-dessus. Le deuxième portait sur la mesure du coût : le champ « tokens d'entrée » des journaux valait invariablement trois, le fournisseur ne comptant l'entrée que nette du cache — une colonne pleine qui ne mesurait rien, et qui rendait invérifiable le dimensionnement de la fenêtre ICL. Le troisième établissait que les signatures textuelles de panne ne couvraient qu'une fraction des messages d'échec possibles, avec une conséquence précise : une série entièrement en échec produit une politique vide, comblée par convention aux valeurs d'équilibre, donc **un écart exactement égal à celui d'un récitant** — une panne se serait lue comme un résultat théoriquement interprétable. Le quatrième était une contrainte de transport : le prompt de la condition ICL à fenêtre pleine dépasse la longueur maximale d'une ligne de commande sous Windows, ce qui aurait interrompu les neuf exécutions ICL à leur troisième série. Ce dernier point mérite d'être signalé pour une raison de méthode : le contournement évident — réduire le nombre de manches par série — aurait fait déterminer un paramètre scientifique par une limite d'outillage, et la vérification a montré qu'il aurait fait échouer le critère de stabilité de `π̂`. Le prompt est donc transmis par fichier, et le paramètre est resté intact.

**Aucun des quatre défauts n'était situé dans le code du dispositif ; aucun n'était détecté par les tests ; aucun n'aurait laissé de trace dans les journaux.** Tous se logeaient à la frontière avec l'outillage tiers. Le principe énoncé plus haut n'est donc pas une leçon tirée de deux incidents isolés : il a été confirmé par une procédure indépendante, appliquée en aveugle sur un dispositif que son auteur croyait achevé.

Un cinquième défaut, de même famille, s'est révélé pendant la campagne elle-même : au-delà de trois exécutions simultanées, le compte heurte la limite de débit du fournisseur, qui restitue un message d'indisponibilité — assorti d'un délai de reset — avec un code de retour normal. Le contrôle issu du troisième constat l'a intercepté : cinq exécutions se sont arrêtées **sans enregistrer une seule décision douteuse**, et les séries déjà closes ont été retrouvées intactes à la reprise. Le harnais attend désormais le délai annoncé plutôt que d'épuiser ses tentatives, une limite de débit n'étant pas une panne mais une file d'attente.

---

## Annexe A — Corrections à apporter à la section 2.1

**A.1 — Le « snapshot figé » ne produit pas la granularité annoncée.** La section 2.1 indique que le bloc mémoire est capturé au démarrage de session et n'apparaît qu'à la session suivante, et en conclut que *« la granularité session est le pas d'adaptation observable »*. Cela vaut pour une session conversationnelle longue. Le protocole utilise en revanche l'invocation **en un coup**, où **chaque manche constitue une session** : le mécanisme natif produirait donc une granularité *manche*, et non *série*. C'est précisément pour cette raison que l'arbitre impose le gel au niveau du système de fichiers (§2.2.4). La formulation est à corriger, faute de quoi la description du dispositif contredirait son fonctionnement réel.

**A.2 — La « double structure mémorielle » n'a pas été retenue.** La section 2.1 annonce un journal d'expérience quantitatif *et* un registre de réflexions qualitatives. Le dispositif construit ne comporte **qu'un seul canal** de mémoire persistante, le fichier de notes auto-écrit. Ce choix est délibéré : deux canaux distincts introduiraient deux variables au lieu d'une et rendraient l'ablation non identifiable. Le rôle du journal quantitatif est tenu par le récapitulatif canonique, produit par l'expérimentateur et servi identiquement aux traitements ICL et AE — ce qui garantit que les deux voient la même information brute. La formulation est à aligner sur ce design.

---

## Bloc destiné à la section « Limites et extensions »

### L.1 Le raisonnement de l'agent n'est qu'en partie observable

L'axe « biais de décision » (H4) repose sur la comparaison entre ce que la délibération de l'agent désigne et ce qu'il joue. Or le modèle retenu **ne restitue pas l'essentiel de son raisonnement** : sur 200 décisions, la sortie visible tient en quatre tokens — la seule ligne d'action — dans 141 cas, tandis que le fournisseur facture en moyenne 420 tokens de chaîne de pensée interne, jamais rendus.

Trois conséquences :

1. **La mesure automatique d'incohérence porte sur une minorité des décisions.** Elle reste valide sur celles où l'agent verbalise, mais son dénominateur n'est plus l'ensemble des décisions. Le taux doit être rapporté comme tel, et non comme une fréquence sur la campagne entière.
2. **La comparabilité avec la littérature en souffre.** GTBENCH et la *Game Reasoning Arena* classent les justifications textuelles ; sans texte, l'appariement avec leurs taxonomies devient partiel.
3. **Le second volet de H4 n'est pas affecté.** La dégénérescence des stratégies mixtes se lit directement dans `π̂`, indépendamment de toute verbalisation — et le pilote y a déjà relevé un signal net : contre un adversaire qui paie systématiquement, l'agent n'engage le sceau dominant que dans 43 à 67 % des cas, alors que l'engagement y est dominant sans calcul.

Deux remèdes ont été envisagés puis écartés avant la campagne : forcer une justification écrite par la consigne — cela modifierait le stimulus servi aux trois traitements — et relever l'effort de raisonnement, dont le pilote a montré qu'il ne change pas le volume rendu.

### L.1 bis Le recodage du jeu : portée réelle

Le jeu est servi sous un vocabulaire réécrit, en réponse à l'objection de mémorisation superficielle relevée en §1.4.3.

Un premier test d'intégration avait paru le mettre en échec : le modèle nommait le jeu source et récitait la stratégie d'équilibre dès la troisième manche, sans aucune mémoire, dans quatorze manches sur vingt. **Ce constat était un artefact du harnais, non un comportement du modèle.** L'agent recevait alors, injecté à son insu dans son prompt système, un document de travail du dépôt décrivant le jeu réel et l'exploitation de chaque adversaire (cf. §2.4). Le canal fermé, la mesure a été refaite : **zéro mention du jeu source sur 200 sorties**, et cinq occurrences du mot « équilibre » sans que le jeu soit jamais nommé.

Le recodage n'est pas revendiqué comme une garantie pour autant, et ce pour deux raisons. D'abord parce que la verbalisation est rare (L.1) : le détecteur n'a que peu de texte à examiner, et l'absence de signal y est un argument faible. Ensuite parce qu'une reconnaissance silencieuse — un modèle qui identifie le jeu sans le nommer — resterait invisible par construction.

L'identification de l'effet ne repose donc pas sur l'ignorance supposée du modèle, mais sur l'**asymétrie des adversaires** : aucune stratégie récitée ne peut faire décroître conjointement l'écart contre un adversaire qui paie systématiquement et contre un adversaire qui se couche systématiquement. La condition sans mémoire fournit par ailleurs la mesure empirique du niveau récité. La reconnaissance du jeu est traitée comme une **covariable mesurée**, rapportée par série et recalculable *a posteriori* sur les journaux, sans qu'aucune censure ne soit appliquée.

### L.2 Autres limites

- **Effectif.** Trois réplications par cellule interdisent toute inférence statistique puissante. L'appariement améliore la précision des comparaisons mais ne remplace pas la taille d'échantillon. Les résultats sont présentés comme des effets mesurés sur un dispositif contrôlé, non comme une estimation populationnelle.
- **Un seul modèle.** La constance du modèle rend l'ablation propre ; elle interdit en retour toute généralisation à d'autres modèles. Le dispositif est conçu pour être rejoué à l'identique avec un autre modèle.
- **Une seule tâche, et sa validité externe.** Le jeu doit sa valeur méthodologique à sa petitesse. Ce qui est mesuré est l'adaptation à un adversaire stationnaire et parfaitement caractérisé — non une capacité d'apprentissage générale. Le parallélisme avec les situations économiques réelles où des agents autonomes interagissent de façon répétée (tarification algorithmique, enchères, négociation) reste à établir : la structure de paiement y est incomparablement plus riche et l'adversaire y est lui-même adaptatif.
- **Une seule implémentation de mémoire auto-écrite.** Le traitement AE teste un mécanisme particulier, avec sa capacité et son style d'invite propres. Un résultat négatif porterait sur ce mécanisme, non sur l'idée de mémoire auto-écrite.
- **Adversaires non adaptatifs.** Les trois adversaires sont fixes. La co-évolution — adversaire qui s'adapte à l'adaptation de l'agent — relève des extensions.
- **Extensions identifiées et écartées** : un bras de transfert (adversaire biaisé puis adversaire optimal, mémoire conservée), un bras humain, et un adversaire constitué d'un modèle de langage figé.

---

## Références mobilisées dans ce chapitre

- Kuhn, H. W. (1950). *A Simplified Two-Person Poker*. Contributions to the Theory of Games.
- Smith, V. L. (1976). *Experimental Economics: Induced Value Theory*. American Economic Review, 66(2), 274-279.
- Jacquemet, N., & L'Haridon, O. (2016). *Économie expérimentale : comportements individuels, stratégiques et sociaux*. L'Actualité économique, 92(1-2).
- Jacquemet, N., & Le Lec, F. (2017). *Développements récents de l'économie comportementale et expérimentale*. Revue économique, 68(5).
- Duan, J. *et al.* (2024). *GTBENCH*. arXiv:2402.12348.
- Shinn, N. *et al.* (2023). *Reflexion*. — origine de la procédure de réflexion en fin de série.
- Loriente & Diez (2023). — *[recoupement des constantes d'équilibre ; référence complète dans la bibliographie générale].*
