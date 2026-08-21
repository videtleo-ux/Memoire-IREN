# Méthodologie

*Mémoire de M2 — IREN. Version de travail, août 2026.*
*Dispositif logiciel : [github.com/videtleo-ux/Memoire-IREN](https://github.com/videtleo-ux/Memoire-IREN)*

---

## 1. Question de recherche et stratégie d'identification

### 1.1 La question

Un agent conversationnel doté d'une mémoire persistante s'améliore-t-il réellement à une tâche répétée, et si oui, quel type de mémoire produit quel type d'amélioration ? La question est empirique et non spéculative : les architectures d'agents dotées d'un fichier de notes auto-écrit se sont généralisées sans qu'on dispose de mesure propre de ce qu'elles apportent, ni de comparaison contrôlée avec l'alternative la plus simple — réinjecter l'historique brut dans le contexte.

Cette recherche construit un dispositif expérimental — une **arène** — qui isole la mémoire comme variable indépendante et mesure l'adaptation par une quantité exacte plutôt qu'estimée.

### 1.2 Le problème d'attribution

La difficulté centrale n'est pas de faire progresser un agent, elle est d'établir que la progression observée vient bien de la mémoire. Trois confusions guettent :

- **le harnais** — si les trois conditions passaient par des chemins logiciels différents (prompts différents, échafaudages différents, modèles différents), on mesurerait « harnais × mémoire » et non « mémoire » ;
- **la connaissance préalable** — si la tâche est un jeu que le modèle connaît par son entraînement, l'agent peut réciter une stratégie apprise sans rien apprendre de son adversaire, et la courbe monterait sans qu'aucune adaptation ait eu lieu ;
- **la chance** — sur quelques centaines de coups, la variance des cartes distribuées peut dominer l'effet cherché.

Le dispositif répond aux trois par construction, non par correction *a posteriori*. C'est le principe directeur qui organise tous les choix qui suivent : **toute adaptation observée doit être attribuable à la mémoire, et à elle seule.**

### 1.3 Stratégie : tout tenir constant sauf un canal

Le modèle est identique dans les trois conditions ; le harnais logiciel est identique ; le texte des règles est identique, versionné et haché, et son empreinte est enregistrée sur chaque ligne de journal ; le format de réponse et le parsing sont identiques ; les cartes distribuées sont identiques. **Une seule rubrique du prompt change d'une condition à l'autre.** L'ablation porte donc sur cette rubrique et sur rien d'autre.

---

## 2. Le dispositif expérimental

### 2.1 La tâche

L'agent joue un jeu à information imparfaite à deux joueurs, en parties répétées, contre un adversaire dont la politique est fixe et connue de l'expérimentateur. Les paiements sont ceux du **poker de Kuhn** (Kuhn, 1950) : trois cartes, une par joueur, la troisième écartée ; droit d'entrée d'un jeton chacun ; un seul tour de décision ; une seule taille de mise.

Ce jeu est retenu pour trois propriétés qu'aucune tâche plus riche ne possède simultanément :

1. **Il est minuscule et entièrement résoluble.** Douze ensembles d'information, six par position. Toute politique se résume à douze probabilités. La meilleure réponse à toute politique adverse se calcule par énumération exhaustive, en arithmétique exacte.
2. **Il est non trivial.** Il admet un équilibre en stratégies mixtes qui exige de bluffer et de payer à des fréquences précises. Un joueur naïf y perd, un joueur qui récite l'équilibre y gagne moins qu'un joueur qui exploite.
3. **Il produit une mesure d'adaptation, pas seulement une mesure de performance.** On peut distinguer un agent qui gagne parce que son adversaire est mauvais d'un agent qui gagne parce qu'il a compris *en quoi* son adversaire est mauvais.

### 2.2 L'obfuscation

Le jeu est servi à l'agent sous une identité entièrement réécrite : **« L'Épreuve des Trois Sceaux »**. Les cartes deviennent trois jetons nommés `Tor`, `Vael`, `Rhun`, dont la relation de dominance est énoncée explicitement dans les règles et non laissée à déduire d'un ordre alphabétique. Les actions deviennent *retenir*, *engager*, *couvrir*, *se retirer*.

Aucun texte servi à l'agent ne contient les termes « Kuhn », « poker », un rang de carte, une abréviation de rang, ni un label ordinal évocateur (« haute », « faible », « première »). Cette contrainte est vérifiée automatiquement : un filet de motifs interdits balaie l'intégralité des gabarits, des vues de manche et des récapitulatifs générés, et fait échouer la suite de tests à la moindre fuite.

L'obfuscation est dirigée **vers l'agent, pas vers le lecteur** : elle vise à empêcher la reconnaissance du jeu et le rappel d'une stratégie mémorisée, non à dissimuler quoi que ce soit de la méthode. La représentation interne du moteur, les journaux et les analyses restent en vocabulaire canonique.

L'obfuscation étant imparfaite par nature, elle est doublée d'une **surveillance**. Chaque sortie du modèle, chaque contenu de mémoire et chaque récapitulatif réinjecté sont passés au crible de deux détecteurs distincts :

- la **dé-obfuscation** — l'agent nomme le jeu réel (« c'est du poker », « le valet ») ;
- la **récitation** — l'agent énonce des constantes d'équilibre sans nommer le jeu (« bluffer un tiers du temps », « Nash », « GTO »).

Les deux drapeaux sont distincts parce que leurs implications le sont : le premier signale une contamination, le second le comportement même que le dispositif cherche à discriminer. Aucune censure automatique n'est appliquée : on observe, on n'intervient pas, et le traitement des runs contaminés est une décision d'analyse documentée. Une vigilance particulière porte sur le **canal mémoire** : un hit dans le fichier de notes se propage à toutes les séries suivantes.

### 2.3 Les adversaires

Trois adversaires à politique fixe, connus de l'expérimentateur et jamais de l'agent :

| Adversaire | Comportement | Exploitation optimale | Écart d'un récitant d'équilibre |
|---|---|---|---|
| **GTO** | équilibre exact (α = 1/3) | aucune — c'est le plafond | `0` |
| **Station** | ne mise jamais, paie toujours | ne jamais bluffer, miser pour la valeur | `1/9 ≈ 0,111` |
| **Over-folder** | ne mise jamais, se couche toujours | miser toutes les mains | `7/9 ≈ 0,778` |

Le choix de Station et Over-folder n'est pas décoratif : leurs fuites sont **exactement opposées** (sur-paiement contre sur-abandon), et leurs exploitations demandent des ajustements de sens contraire. Un agent qui appliquerait une fréquence de bluff fixe — fût-elle celle de l'équilibre — perd dans les deux directions. C'est le **discriminateur central** entre adaptation réelle et récitation : il fournit deux courbes que seule une lecture effective du comportement adverse peut faire descendre simultanément.

Le bot GTO joue le rôle de plafond expérimental : il n'est par construction pas exploitable, et l'écart mesuré contre lui ne peut donc pas descendre en dessous de zéro quelle que soit la mémoire de l'agent. Il contrôle l'hypothèse alternative d'un « progrès » qui ne serait qu'un artefact de mesure.

### 2.4 La mesure : l'écart d'exploitation

La variable dépendante n'est ni le gain, ni le taux de victoire — deux quantités bruitées qui confondent la qualité du jeu et la chance des cartes. C'est l'**écart d'exploitation** :

> `Écart(s) = EV(meilleure réponse à l'adversaire) − EV(politique observée de l'agent)`

exprimé en jetons par manche, moyenné sur les deux positions. Il se lit directement : **c'est ce que l'agent laisse sur la table à chaque coup**, faute d'exploiter parfaitement le défaut de son adversaire. Zéro signifie exploitation optimale.

Trois propriétés en font l'instrument du dispositif :

- **Il est exact, pas estimé.** Le jeu comptant six donnes équiprobables et un arbre de profondeur au plus trois, l'espérance de toute politique contre toute autre se calcule par énumération complète, en fractions rationnelles. Aucune simulation, aucun intervalle de confiance sur la mesure elle-même.
- **Il est insensible à la chance.** Il porte sur la politique observée, pas sur les gains réalisés. Un agent qui joue parfaitement et perd sur une série de mauvaises donnes affiche un écart nul.
- **Il est décomposable.** L'écart s'accompagne d'une **référence récitée** — `EV(politique observée) − EV(équilibre)` contre le même adversaire — qui mesure la distance au comportement d'un pur récitant.

La politique observée `π̂(M_s)` est estimée par les fréquences brutes de l'agent sur chacun des douze ensembles d'information, sur les manches d'une série. Les décisions où le harnais a dû imposer une action faute de réponse exploitable sont **exclues** du comptage et rapportées séparément : elles renseignent sur le harnais, pas sur la politique de l'agent. Les ensembles d'information non atteints — six d'entre eux le sont systématiquement face aux adversaires qui ne misent jamais — sont comblés par convention à la valeur d'équilibre et signalés ; leur valeur n'affecte ni l'espérance ni l'écart, puisqu'ils sont inatteignables.

> **Note sur une constante.** La littérature de référence disponible indiquait pour l'un des douze paramètres d'équilibre une valeur (`1/3`) que la re-dérivation analytique contredit (`α + 1/3 = 2/3` à α = 1/3). L'arbitrage n'a pas été laissé à l'autorité : le dispositif s'auto-vérifie par un test qui exige `écart(équilibre, équilibre) = 0`, condition qui échoue avec la première valeur et passe avec la seconde. La valeur retenue est donc celle que la définition même de l'équilibre impose. *[Recoupement avec Loriente & Diez à insérer ici.]*

---

## 3. La variable indépendante : trois régimes de mémoire

### 3.1 Les trois conditions

Le modèle est constant ; le harnais est constant ; seule la rubrique mémoire du prompt varie.

| Condition | Rubrique dans le prompt | Mise à jour en fin de série |
|---|---|---|
| **SM** — sans mémoire | *aucune rubrique* | rien |
| **ICL** — historique brut | les récapitulatifs des séries passées, fenêtrés | l'expérimentateur empile le récapitulatif ; **aucun appel au modèle** |
| **AE** — auto-écrite | le fichier de notes personnelles de l'agent | l'agent lit le récapitulatif et **réécrit ses notes lui-même** |

**SM** est le témoin : contexte neuf à chaque manche, aucune trace du passé. Il établit le niveau de performance « sans mémoire » du modèle et sa variance, c'est-à-dire la ligne de base contre laquelle toute progression doit être jugée.

**ICL** représente la solution naïve : réinjecter l'historique. La fenêtre est bornée (6 000 tokens) et l'éviction se fait par **séries entières**, jamais en tronquant une série en son milieu — le phénomène attendu vient précisément de la disparition des séries anciennes, et une troncature arbitraire mesurerait un artefact de découpe.

**AE** représente la mémoire agentique native : l'agent tient un fichier de notes qu'il rédige, révise et élague lui-même. Deux points méritent d'être soulignés parce qu'ils constituent l'objet même de l'observation :

- **le contenu est entièrement laissé à l'agent.** L'expérimentateur n'édite jamais ses notes, ne lui suggère rien, ne résume rien pour lui. Le récapitulatif qu'il reçoit est le journal brut de ses manches — sans conseil, sans statistique agrégée par ensemble d'information, sans interprétation. Distiller la fuite de l'adversaire est précisément le travail que l'on mesure ;
- **la capacité est bornée et sans compaction automatique** (environ 2 200 caractères). Le dépassement est une erreur, pas une troncature silencieuse : c'est à l'agent d'élaguer. Ce qu'il choisit de sacrifier lorsqu'il arrive à saturation est un résultat en soi.

Les deux conditions à mémoire reçoivent **la même matière première** — le même récapitulatif canonique. Seul le mécanisme de rétention diffère. Sans cette contrainte, on comparerait deux informations et non deux mémoires.

### 3.2 L'unité d'adaptation : la série

Un **run** se décompose en séries ; une série est une suite de **K = 200 manches** jouées sous un état mémoire fixe. La série est l'unité atomique d'adaptation : un point sur la courbe correspond à un état mémoire.

Ce découpage n'est pas un confort de mise en œuvre, c'est une condition de la mesure. `π̂(M_s)` s'énonce comme « la politique de l'agent **étant donné l'état mémoire M_s** ». Si la mémoire évoluait au cours des 200 manches, l'échantillon ne serait plus celui d'une politique mais le mélange de plusieurs, et l'écart calculé n'aurait plus de sujet bien défini.

### 3.3 Le gel intra-série

D'où le protocole : la mémoire est **capturée à l'ouverture de la série, figée pendant toute sa durée, et mise à jour uniquement à la frontière**. Le gel porte sur le *moment* où une modification prend effet, jamais sur son *contenu*.

Trois raisons le motivent :

1. **la mesure**, exposée ci-dessus ;
2. **la comparabilité** — la condition ICL est figée intra-série par construction. Si AE pouvait se mettre à jour en cours de route, les deux conditions différeraient par le mécanisme de rétention *et* par la fréquence de mise à jour, et l'écart ne serait plus attribuable à l'un des deux ;
3. **la pureté du canal** — le contexte étant neuf à chaque manche, l'agent n'accumule rien d'une manche à l'autre. Autoriser une écriture en cours de série créerait un canal d'apprentissage parasite, distinct de celui que l'on étudie et fondé sur une information partielle.

Le gel est **imposé au niveau du système de fichiers** par l'expérimentateur, et non supposé : l'agent utilisé persiste ses écritures mémoire immédiatement, et une routine d'auto-révision peut écrire après n'importe quel tour. Un instantané est donc restauré avant chaque manche. Les tentatives d'écriture ne sont pas pour autant ignorées : chacune est **détectée, enregistrée, puis annulée**. « L'agent cherche-t-il à prendre des notes pendant qu'il joue ? » constitue une observation, non un incident.

### 3.4 Signatures attendues

Les trois conditions prédisent trois formes de courbe distinctes, ce qui rend l'hypothèse falsifiable au-delà d'une simple comparaison de moyennes :

- **SM — plate.** Sans mémoire, aucune accumulation possible ; les fluctuations sont celles de l'échantillonnage.
- **ICL — en dents de scie.** L'agent réapprend puis oublie au rythme de l'éviction de la fenêtre. La périodicité attendue est celle du fenêtrage, ce qui constitue une prédiction testable et non une simple attente qualitative.
- **AE — en escalier.** Chaque frontière peut produire un palier ; l'accumulation est monotone tant que l'élagage ne détruit pas d'information utile.

La question de contribution du mémoire est alors précise : **l'escalier AE descend-il plus bas, et plus vite, que la scie ICL, à donnes identiques ?**

---

## 4. Architecture du dispositif logiciel

Le dispositif a été entièrement développé pour cette recherche. Il est décrit ici dans ses grandes lignes ; le code, ses spécifications et sa suite de tests sont publics.

Quatre couches, aux responsabilités strictement disjointes :

- **Le moteur de jeu** — les règles et l'instrument de mesure. Il ne communique avec aucun modèle de langage. Il règle les manches, calcule les meilleures réponses et les écarts d'exploitation en arithmétique exacte.
- **Le harnais mémoire** — tout ce que l'agent lit et tout ce qu'il produit. Il compose le prompt, invoque le modèle, extrait l'action de la réponse en texte libre, et incarne les trois conditions.
- **Le journal** — l'enregistrement. Chaque événement est écrit en JSON par lignes, validé à l'écriture, et les fichiers d'analyse en sont dérivés.
- **L'arbitre** — l'orchestration. Il distribue les cartes, alterne les positions, applique le gel, déclenche les frontières de série, mesure et décide de l'arrêt.

Deux choix d'implémentation ont des conséquences méthodologiques directes et méritent d'être signalés :

**Les donnes sont dérivées, non tirées.** La distribution des jetons à la manche *k* de la série *s* de la réplication *r* est une fonction déterministe de `(graine, r, s, k)`. Aucun état de générateur pseudo-aléatoire ne circule d'une manche à la suivante. Il en résulte que deux conditions au même triplet `(r, s, k)` reçoivent des cartes rigoureusement identiques, **par construction et non par discipline** — propriété qui serait autrement fragile et dont aucun journal ne révélerait la violation après coup.

**L'isolation des exécutions est vérifiée, jamais supposée.** Le fichier de notes de l'agent vit dans son répertoire personnel ; deux exécutions parallèles sur une même machine s'écraseraient mutuellement la mémoire en silence, et une exécution contaminée ne se lit pas comme une anomalie dans les résultats — elle se lit comme de l'adaptation. Chaque run dispose donc d'un répertoire dédié, et un marqueur unique est écrit puis recherché dans tous les autres répertoires avant que le run ne démarre. L'échec de cette vérification interdit le démarrage.

Le dispositif est couvert par 184 tests automatisés, dont un oracle analytique du moteur de mesure — les valeurs d'équilibre et d'exploitation ont été re-dérivées à la main et sont vérifiées exactement par la suite — et une procédure de **rejeu** qui re-règle chaque manche depuis les seuls journaux et retrouve les mesures publiées.

> **Code, spécifications et journaux :** [github.com/videtleo-ux/Memoire-IREN](https://github.com/videtleo-ux/Memoire-IREN)

---

## 5. Plan expérimental

### 5.1 La matrice

**3 conditions × 3 adversaires × 3 réplications = 27 runs.**

Les réplications ne sont pas des répétitions à l'identique : chacune reçoit sa propre séquence de donnes. Elles capturent la variabilité conjointe de l'échantillonnage des cartes et de la stochasticité du modèle.

### 5.2 L'appariement

Les trois conditions d'une même réplication reçoivent des donnes **strictement identiques**, manche par manche — technique des nombres aléatoires communs. Les tirages de l'adversaire stochastique sont eux aussi appariés. Les comparaisons entre conditions se font donc à cartes égales, ce qui élimine la variance due à la distribution et permet une comparaison appariée sur N = 3 malgré la faiblesse de l'effectif.

L'alternance des positions est déterministe — l'agent ouvre les manches impaires, répond les manches paires — de sorte que l'équilibre est exact et identique partout. Toutes les quantités rapportées sont moyennées sur les deux positions.

Une vérification d'intégrité à la clôture de chaque run recalcule l'empreinte de la séquence de donnes et la confronte à celle des runs appariés. L'appariement est ainsi **prouvé a posteriori** et non seulement organisé a priori.

### 5.3 Paramètres et règle d'arrêt

| Paramètre | Valeur | Justification |
|---|---|---|
| Manches par série (K) | 200 | compromis entre stabilité de `π̂` et coût ; revalidé au pilote |
| Réplications (N) | 3 | contrainte de budget ; compensée par l'appariement |
| Séries — condition SM | 3 | rien à accumuler ; trois points suffisent à établir le plancher et sa dispersion |
| Séries — ICL et AE | 8 à 20 | arrêt au plateau, borné des deux côtés |
| Fenêtre ICL | 6 000 tokens | éviction par séries entières |

La **règle d'arrêt** est automatisée et enregistrée à chaque évaluation. Le plateau est déclaré lorsque, avec au moins huit séries, la pente de la régression linéaire de l'écart sur les quatre dernières séries est supérieure ou égale à `−0,02` jeton/manche/série **et** que la dispersion de ces quatre valeurs est inférieure à `0,05`. Les deux conditions sont nécessaires : la pente seule déclarerait un plateau sur une courbe en dents de scie régulières, la dispersion seule le déclarerait au milieu d'une descente lente. Le run se poursuit ensuite **deux séries au-delà** de la déclaration, afin que le plateau soit constaté et non anticipé.

Le minimum de huit séries garantit assez de points pour distinguer les trois formes attendues même si la courbe se stabilise rapidement ; le maximum de vingt borne le coût.

### 5.4 Pilote de calibrage

Un pilote précède la campagne, sur un run court par condition contre un adversaire déterministe. Il tranche, dans cet ordre de véto :

1. **le taux de réponses exploitables** — seuil de 98 %, en dessous duquel le format de réponse ou le modèle est rejeté avant toute dépense ;
2. **le coût mesuré par manche**, et par extrapolation le coût de la campagne ;
3. **la stabilité de `π̂` à K = 200**, par comparaison des écarts obtenus à K = 100, 150 et 200 ;
4. **la latence**, et donc la durée projetée ;
5. **les constantes de la règle d'arrêt**, confrontées aux premières courbes réelles.

Les paramètres élus sont figés avant la campagne et ne sont plus modifiés : un changement en cours de route rendrait les runs non comparables.

---

## 6. Données produites et plan d'analyse

### 6.1 Ce qui est enregistré

Le grain d'enregistrement est celui qui rend la mesure exacte possible et l'expérience entièrement reconstructible.

**Par décision :** le prompt exact servi à l'agent, le texte intégral de sa réponse — raisonnement libre compris —, l'action extraite et la manière dont elle l'a été, l'état réel de la table en représentation canonique, et le résultat. Le couple *état réel / vue servie* permet de vérifier après coup que la vue était légale et fidèle, c'est-à-dire qu'aucun défaut de rendu n'a donné à l'agent une information qu'il n'aurait pas dû recevoir.

**Par série :** l'état mémoire d'entrée et de sortie, le détail des entrées ajoutées, modifiées ou supprimées, la politique observée avec les effectifs par ensemble d'information, l'écart d'exploitation et la référence récitée, les défauts de parsing, les drapeaux de dé-obfuscation avec leurs extraits, et la décision d'arrêt.

Les effectifs par ensemble d'information sont enregistrés parce qu'ils fournissent les barres d'erreur : une fréquence de 1,0 sur deux observations ne dit pas la même chose que sur soixante.

Une procédure de rejeu re-règle chaque manche à partir des seuls journaux et doit retrouver exactement les résultats, la politique observée et l'écart. C'est le test de complétude de l'enregistrement : si quelque chose manque pour reconstruire l'expérience, il échoue.

### 6.2 Analyses prévues

1. **Courbes d'adaptation** — la figure centrale : l'écart par série, en grille de trois conditions par trois adversaires, avec les tracés individuels des réplications et leur moyenne. Deux lignes de référence y sont portées : `y = 0` (exploitation optimale) et l'écart d'un récitant d'équilibre (`0,111` contre Station, `0,778` contre Over-folder). La lecture attendue est une courbe plate, une courbe en dents de scie et un escalier.
2. **Question de contribution** — comparaison appariée AE contre ICL par réplication : écart final, aire sous la courbe, série d'atteinte du plateau. Compte tenu de N = 3, on rapporte des **effets appariés et des intervalles bootstrap**, non des tests d'hypothèse dont la puissance serait décorative.
3. **Discriminateur récité contre émergent** — trajectoire du couple (écart, référence récitée) par série. Un récitant reste au voisinage de la référence ; un agent qui exploite s'en écarte, et dans des directions opposées selon l'adversaire.
4. **Analyse du canal mémoire** — contenu des notes aux frontières : l'agent distille-t-il la fuite de l'adversaire ? Son élagage est-il destructeur ? Une écriture donnée précède-t-elle un palier à la série suivante ?
5. **Contrôles** — équilibre des positions, taux de réponses par défaut par condition, effet-machine le cas échéant, coût.

### 6.3 Ce qui compterait comme réfutation

L'hypothèse est réfutée si l'un des faits suivants est observé :

- la condition AE ne se distingue pas de SM contre les adversaires exploitables ;
- l'écart descend contre GTO, adversaire non exploitable, ce qui signalerait un artefact de mesure ;
- les courbes contre Station et Over-folder descendent l'une **sans** l'autre, ce qui signalerait une stratégie récitée plutôt qu'une lecture du comportement adverse ;
- les gains descendent sans que la politique observée s'écarte de l'équilibre, ce qui signalerait de la chance et non de l'apprentissage.

---

## 7. Validité

### 7.1 Menaces internes et parades

| Menace | Parade |
|---|---|
| Confusion harnais × mémoire | chemin logiciel unique pour les trois conditions ; prompts identiques hors la rubrique mémoire ; empreinte du texte de règles enregistrée sur chaque ligne |
| Reconnaissance du jeu et récitation | obfuscation vérifiée automatiquement ; double détecteur sur les sorties **et** sur le canal mémoire ; adversaires à fuites opposées |
| Variance des cartes | donnes dérivées et appariées entre conditions ; mesure portant sur la politique et non sur les gains |
| Fuite de mémoire entre exécutions | répertoire dédié par run ; marqueur d'isolation vérifié avant démarrage et à la clôture |
| Violation silencieuse du gel | instantané restauré avant chaque manche ; toute tentative d'écriture enregistrée |
| Fuite d'information dans les récapitulatifs | la carte de l'adversaire n'apparaît que si elle a été dévoilée ; vérifié par test exhaustif |
| Réponses inexploitables biaisant la politique observée | exclues du comptage et rapportées séparément ; seuil de véto au pilote |
| Perte de données en cours de campagne | journaux en ajout seul, reprise à la frontière de série, série interrompue rejouée intégralement et tentative avortée conservée à part |

### 7.2 Limites reconnues

- **Effectif.** N = 3 réplications par cellule interdit toute inférence statistique puissante. L'appariement par donnes communes améliore la précision des comparaisons mais ne remplace pas la taille d'échantillon. Les résultats sont présentés comme des effets mesurés sur un dispositif contrôlé, non comme une estimation populationnelle.
- **Un seul modèle.** La constance du modèle est ce qui rend l'ablation propre ; elle interdit en retour toute généralisation à d'autres modèles. Le dispositif est conçu pour être rejoué avec un autre modèle sans modification.
- **Une seule tâche.** Le jeu retenu doit sa valeur méthodologique à sa petitesse. Ce qu'on mesure est l'adaptation à un adversaire dans un environnement stationnaire et parfaitement caractérisé, non une capacité d'apprentissage générale.
- **Une seule implémentation de mémoire auto-écrite.** La condition AE teste un mécanisme particulier, avec sa capacité et son style d'invite propres. Un résultat négatif porterait sur ce mécanisme, non sur l'idée de mémoire auto-écrite.
- **Périmètre.** Trois extensions ont été identifiées puis écartées faute de temps : un bras de transfert (adversaire biaisé puis adversaire optimal, mémoire conservée), un bras humain, et un adversaire constitué d'un modèle figé. Elles sont documentées comme prolongements.

---

## Références

- Kuhn, H. W. (1950). *A Simplified Two-Person Poker*. Contributions to the Theory of Games.
- Shinn, N. *et al.* (2023). *Reflexion: Language Agents with Verbal Reinforcement Learning*. — origine de la procédure de réflexion en fin de série.
- Loriente & Diez — *[référence complète à insérer ; recoupement des constantes d'équilibre, cf. §2.4].*

*Bibliographie à compléter et à harmoniser au style du mémoire.*
