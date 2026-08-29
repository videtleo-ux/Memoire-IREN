# Conclusion

La question posée en introduction comportait deux branches, et le dispositif a été
conçu pour les instrumenter séparément. Elles reçoivent des réponses de signe
opposé, et c'est leur conjonction qui constitue le résultat de ce travail.

À la première branche, la réponse est positive et sans ambiguïté. Doté d'une
mémoire persistante qu'il rédige lui-même, l'agent développe une adaptation qui
mérite le nom de stratégie. Il identifie la régularité de son adversaire à partir
d'un journal brut que personne n'a interprété pour lui, en tire une règle, et
applique cette règle jusqu'à l'exploitation maximale. Contre les deux adversaires
exploitables, il atteint exactement l'optimum théorique — non une valeur proche,
mais la meilleure réponse au sens strict. Les neuf paires appariées vont toutes
dans le même sens. Et il ne s'agit pas d'une récitation mieux exécutée : les deux
adversaires demandent des ajustements de sens contraire, aucune stratégie fixe ne
peut les satisfaire ensemble, et l'agent privé de mémoire joue en dessous du
niveau de l'équilibre. La mémoire ne lui sert pas à retrouver la solution du jeu,
elle lui sert à s'en écarter dans la direction que chaque adversaire commande.

Le mécanisme de rétention n'est pas neutre non plus. À information strictement
identique, la mémoire auto-rédigée l'emporte sur la réinjection de l'historique
brut, mais seulement là où la politique optimale exige une conduite différenciée
selon la carte détenue. Ce qui sépare les deux dispositifs n'est ni la vitesse
d'apprentissage ni l'oubli, contrairement à ce que le protocole anticipait : les
deux chutent à la première frontière, et aucun décrochage n'apparaît quand la
fenêtre sature. Ce qui les sépare est la complétude de l'induction. Un
comportement perdant figure dans un historique brut comme une partie parmi cent
cinquante ; rien ne rassemble ces occurrences en interdiction. La synthèse écrite
le fait.

À la seconde branche, la réponse est négative, et elle est le résultat le plus
inattendu de ce travail. L'adaptation observée ne cohabite pas avec un biais de
décision : elle le produit. Face à l'adversaire qui joue l'équilibre, où
l'optimalité exige d'engager une fois sur trois et de façon imprévisible, l'agent
privé de mémoire joue des fréquences intermédiaires proches de la valeur
théorique. Dès qu'une note existe, il s'échoue sur les valeurs extrêmes plus d'une
série sur deux. Un contrôle interne exclut les autres explications : la première
série d'une exécution à mémoire, jouée avec un emplacement présent mais encore
vide, ne présente pas le phénomène.

Le mécanisme responsable est identifié, et c'est le même que celui du succès. Ce
qui rend la mémoire auto-écrite supérieure, c'est qu'elle contraint l'agent à
formuler une règle. Mais une règle écrite en langue naturelle est déterministe.
Les quatre-vingt-dix notes produites pendant la campagne le confirment sans
exception : l'agent n'y prescrit jamais une fréquence pour sa propre action, ni en
pourcentage, ni en fraction, ni en proportion énoncée. Il détecte pourtant le
caractère stochastique de son adversaire, et il sait écrire un rapport de
probabilité lorsqu'il décrit une situation. Il ne le fait jamais pour lui-même. Le
canal qui porte l'adaptation ne sait pas porter une fréquence.

On ne peut donc pas assimiler cette adaptation à une rationalité économique au
sens strict. L'agent optimise, et il optimise remarquablement bien, mais dans un
espace de stratégies pures. L'espace où il optimise n'est pas celui que la théorie
des jeux à information imparfaite lui assigne, et il s'en éloigne au moment même
où il exploite le mieux.

La portée de ce constat dépasse le jeu qui a servi à l'établir. Un agent
artificiel doté de mémoire est un meilleur exploiteur et un adversaire plus
prévisible. Dans une interaction répétée avec un partenaire capable d'apprendre à
son tour, ces deux propriétés se compensent, et la seconde peut annuler la
première. Une évaluation qui ne mesurerait que la performance conclurait pourtant
à une rationalité accrue : elle observerait un agent qui joue de mieux en mieux et
manquerait le mouvement opposé qui l'accompagne. C'est la séparation des trois
dimensions — exploitation, équilibre, biais de décision — qui permet de voir les
deux à la fois, et c'est la contribution principale du dispositif.

Trois résultats méthodologiques s'ajoutent à ces conclusions et valent
indépendamment d'elles. Une mesure d'incohérence entre raisonnement et action,
pré-enregistrée avant la campagne, s'est révélée invalide : appliquée à la lettre,
elle produit un taux artefactuel qui tombe à un point du chiffre attendu par la
littérature, et huit divergences relues se sont révélées être huit faux positifs.
Les deux instruments du dispositif se sont avérés redondants à adversaire fixé, ce
qui invalide une figure prévue au plan d'analyse. Enfin, un audit conduit avant la
campagne a montré que les défauts les plus dangereux d'un tel dispositif ne se
logent ni dans son code ni dans ses journaux, mais à sa frontière avec l'outillage
tiers qu'il pilote : dans le cas présent, un fichier de consignes du dépôt qui
nommait le jeu et décrivait l'exploitation de chaque adversaire était injecté à
l'agent à chaque décision.

Les limites de ce travail doivent être énoncées franchement. Il repose sur trois
réplications, un seul modèle, une seule tâche et un horizon de dix séries. Le
plateau étant atteint dès les premières frontières, le dispositif mesure la
persistance de l'adaptation mais résout mal sa vitesse. Le profil d'oubli attendu
pour la réinjection d'historique n'a jamais été observé à cet horizon. Le contrôle
négatif n'a pas été conduit en condition de réinjection, arbitrage assumé et
motivé par le dimensionnement. Le résultat sur la dégénérescence des stratégies
mixtes repose sur un seul ensemble d'information, et son contrôle interne sur
trois séries. Le codage manuel du raisonnement, qui aurait précisé le taux
d'incohérence sur les décisions que la mesure automatique ne couvre pas, a été
écarté du périmètre. Enfin, le fournisseur ne restitue pas la chaîne de pensée du
modèle : les mesures portant sur le texte ne voient qu'une partie du raisonnement.
Une limite plus fondamentale tient à l'obfuscation du jeu, qui n'a pas tenu :
l'agent reconnaît la structure du poker de Kuhn. C'est précisément pour cette
raison que l'identification repose sur l'asymétrie des adversaires plutôt que sur
l'ignorance supposée du modèle.

Ces limites dessinent les prolongements. La vitesse d'adaptation et le profil
d'oubli demanderaient un protocole différent, à séries plus courtes et plus
nombreuses, et non davantage du même. La généralité du résultat sur la
dégénérescence appelle un jeu comportant plusieurs ensembles d'information à
équilibre mixte, et plusieurs modèles. Trois extensions écartées du périmètre de
ce travail restent ouvertes : un bras de transfert, où l'agent affronte un
adversaire biaisé puis un adversaire à l'équilibre en conservant sa mémoire, qui
dirait si l'exploitation apprise devient une charge ; un bras humain, jouant le
même protocole, qui donnerait la référence comportementale qui manque ici ; et un
adversaire lui-même doté d'un modèle de langage, qui ferait de la prévisibilité
mesurée une variable et non plus une observation.

Reste un fait dont il faut mesurer la portée. L'agent construit une stratégie
exploitative à partir d'un journal brut, seul, sans supervision et sans
réapprentissage de ses paramètres. Que le canal par lequel il y parvient soit un
texte écrit en langue naturelle explique à la fois ce qu'il réussit et ce qu'il
perd. Concevoir des agents économiques capables de jouer des stratégies mixtes
suppose donc de leur donner un canal de mémoire qui sache représenter une
fréquence — ce qu'une note écrite ne fait pas.
