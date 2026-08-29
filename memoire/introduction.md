# Introduction

Les modèles de langage ne se contentent plus de produire du texte à la demande.
Ils sont désormais déployés comme agents autonomes : ils négocient des contrats,
enchérissent, fixent des prix, arbitrent des allocations, et le font de plus en
plus souvent face à d'autres agents dont les intérêts divergent des leurs. Le
comportement de ces systèmes en situation stratégique cesse donc d'être une
curiosité technique pour devenir une question économique. Si des agents
artificiels prennent une part croissante des décisions de marché, la nature de
leur rationalité détermine les équilibres qui s'y forment.

L'économie expérimentale a construit, sur les sujets humains, l'instrument qui
permet de poser cette question correctement : plutôt que de décrire un
comportement, elle le confronte à une norme théorique et mesure l'écart. Un
courant récent transpose ce protocole aux modèles de langage, soit pour les
utiliser comme substituts d'agents humains, soit pour les observer comme des
entités dont le comportement mérite une science propre. Les évaluations
stratégiques disponibles établissent que ces modèles tiennent la comparaison dans
les jeux à information imparfaite, mais elles ne permettent pas de dire pourquoi.
Elles sont statiques, elles observent des parties indépendantes, et surtout elles
confondent trois situations que rien ne distingue dans une mesure de performance :
un agent qui gagne peut le faire parce qu'il commet moins d'erreurs, parce qu'il
applique une solution d'équilibre apprise pendant son entraînement, ou parce qu'il
identifie la faiblesse de son adversaire et l'exploite. Ces trois cas n'ont pas
les mêmes implications économiques. Seul le troisième correspond à ce que la
théorie appelle une stratégie.

Un développement parallèle rend cette distinction mesurable. Les architectures
d'agents récentes accordent au modèle une mémoire persistante qu'il rédige
lui-même : à intervalles réguliers, il synthétise son expérience en langue
naturelle et relit cette synthèse par la suite. Ce mécanisme a été validé dans des
environnements coopératifs ou solitaires, où il n'existe aucun adversaire dont la
déviation doive être découverte puis punie. Or c'est précisément là qu'il devient
économiquement intéressant : une mémoire persistante est le canal par lequel un
agent pourrait construire, d'une interaction à l'autre, le modèle de son
adversaire qui lui permet de s'écarter de l'équilibre pour gagner davantage.

Ce travail se place à cette intersection. Il pose la question suivante : dans un
environnement stratégique à information imparfaite, un agent LLM autonome équipé
d'une mémoire persistante développe-t-il une adaptation comportementale
s'apparentant à une stratégie ? Et si oui, cette adaptation le rapproche-t-elle de
l'optimalité de l'*homo œconomicus*, ou reproduit-elle les biais de décision que
l'économie comportementale documente chez l'humain ?

La réponse est construite en trois chapitres.

Le premier situe le travail dans les quatre littératures dont il relève :
l'économie comportementale et expérimentale, qui fournit le protocole de mesure ;
le Machine Behaviour et l'*homo silicus*, qui l'ont transposé aux modèles de
langage ; les évaluations stratégiques existantes, qui établissent la compétence
sans en expliquer l'origine ; et les architectures de mémoire auto-rédigée, dont
le mécanisme n'a jamais été éprouvé face à un adversaire. Le chapitre se clôt sur
le manque que leur intersection laisse ouvert, et sur la position que cette
recherche y occupe.

Le deuxième traduit la question en quatre hypothèses réfutables et décrit le
dispositif construit pour les instrumenter. Un agent y joue un poker de Kuhn — un
jeu à information imparfaite assez petit pour que son équilibre soit calculable
exactement, assez riche pour que le bluff y soit optimal — contre des adversaires
dont la politique est fixe et connue. Deux d'entre eux présentent des défauts
opposés : l'un suit toujours, l'autre se couche toujours. Les exploiter demande
des ajustements de sens contraire, si bien qu'aucune stratégie fixe, l'équilibre
compris, ne peut faire baisser les deux mesures ensemble ; c'est ce plan
d'adversaires qui sépare l'exploitation de la récitation. Le modèle est tenu
constant et la mémoire seule est manipulée, selon trois traitements : aucune
mémoire, réinjection de l'historique brut, et mémoire auto-rédigée par l'agent.
Les trois reçoivent les mêmes distributions de cartes dans le même ordre, ce qui
annule la chance dans les comparaisons. La variable dépendante n'est ni le gain ni
le taux de victoire, mais l'écart d'exploitation : la différence, calculée
exactement sur les douze ensembles d'information du jeu, entre l'espérance de la
meilleure réponse à l'adversaire et celle de la politique effectivement jouée. Un
second instrument, mesuré depuis l'équilibre plutôt que depuis la meilleure
réponse, indique si l'agent récite une solution ou s'en écarte délibérément.

Le troisième expose les résultats de la campagne — vingt-quatre exécutions, cent
soixante-dix-sept séries, plus de vingt-sept mille décisions journalisées avec le
texte intégral du raisonnement de l'agent. Il commence par démonter la mesure sur
une série réelle, afin que chaque chiffre du chapitre puisse être refait par le
lecteur, puis établit les quatre hypothèses dans l'ordre du plan d'analyse arrêté
avant la collecte. Les conclusions vont dans deux directions à la fois. Doté d'une
mémoire auto-rédigée, l'agent atteint exactement la meilleure réponse contre les
deux adversaires exploitables, alors que privé de mémoire il joue en dessous du
niveau de l'équilibre : l'adaptation existe, elle vient de la mémoire, et elle
exploite au lieu de réciter. Mais le mécanisme qui la produit dégrade
simultanément sa capacité à jouer une stratégie mixte, là où l'optimalité exige
d'être imprévisible. L'adaptation et le biais de décision ne coexistent pas : le
second est produit par le premier.
