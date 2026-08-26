# H4 — mesures automatiques du biais de décision

*Généré par `analyse/h4.py` depuis `donnees/decisions.csv` et `donnees/infosets.csv`. Aucune collecte nouvelle.*


## 1. Incohérence raisonnement↔action

Base : **27 270** décisions au parsing strict (20 écartées, extraites par repli).


### 1.1 La règle pré-enregistrée ne mesure pas ce qu'elle annonce

Le §2.2.5.3 prévoit de comparer l'action jouée à **la dernière action nommée dans le texte libre**. Appliquée littéralement :


> Décisions où le raisonnement nomme au moins une action : **13 442** (49.3 %). Taux de divergence : **47.8 %**.


Ce chiffre est **un artefact**, et il faut le dire d'autant plus nettement qu'il tombe à un point des 45,1 % de GTBENCH — coïncidence qui rendrait la confirmation d'H4 très facile à publier et parfaitement fausse.


La cause est grammaticale. Le raisonnement de l'agent conclut par une clause contrastive qui nomme l'option **rejetée**, non celle retenue :


> « *Engager garantit donc un gain de +1, **tandis que retenir** expose à une perte selon le sceau adverse.* » — action jouée : engager. La règle lit « retenir » et compte une incohérence.


Huit divergences tirées au hasard ont été relues : **huit faux positifs**, tous de cette forme. Une règle positionnelle hérite de la structure du discours français, où l'alternative écartée vient en dernier.


### 1.2 Trois variantes, et laquelle porte le résultat

| Variante | Décisions mesurables | Divergences | Taux |
|---|---|---|---|
| **A** — positionnelle, pré-enregistrée | 13 442 | 6 422 | 47.8 % |
| **B** — A, occurrences attribuées à l'adversaire écartées | 12 095 | 4 425 | 36.6 % |
| **C** — l'agent **énonce** son choix (« il vaut mieux X », « je choisis X ») | 604 | 0 | **0.00 %** |

A et B restent positionnelles et souffrent du même défaut ; B ne corrige que l'attribution du sujet, pas la structure contrastive. **C est la seule à haute précision** : elle ne retient que les décisions où l'agent déclare son choix par une formule explicite, et ne mesure donc rien d'autre que ce que H4 demande. Son prix est le rappel — elle ne couvre que 2.2 % des décisions.


**Résultat : sur les 604 décisions où l'agent énonce explicitement l'action qu'il retient, il joue cette action dans tous les cas.**


| Traitement | Décisions | C — mesurables | C — divergences |
|---|---|---|---|
| SM | 4 229 | 194 (4.6 %) | 0 |
| ICL | 8 996 | 83 (0.9 %) | 0 |
| AE | 14 045 | 327 (2.3 %) | 0 |

| Adversaire | Décisions | C — mesurables | C — divergences |
|---|---|---|---|
| Over-folder | 10 344 | 158 (1.5 %) | 0 |
| Station | 10 343 | 243 (2.3 %) | 0 |
| GTO | 6 583 | 203 (3.1 %) | 0 |

### 1.3 Par série — la variante A, pour mémoire

Le §2.2.9 demande si l'incohérence décroît avec l'adaptation. La question ne peut pas être tranchée par A, dont on vient de voir qu'elle mesure autre chose ; le tableau est donné parce que la **stabilité** du taux est elle-même informative — un artefact grammatical n'a aucune raison de varier avec la série, et c'est bien ce qu'on observe.

| Série | SM | ICL | AE |
|---|---|---|---|
| 0 | 67.1 % | 67.8 % | 63.4 % |
| 1 | 62.6 % | 44.4 % | 46.6 % |
| 2 | 64.8 % | 30.0 % | 40.2 % |
| 3 | — | 37.9 % | 51.5 % |
| 4 | — | 45.4 % | 46.7 % |
| 5 | — | 44.9 % | 51.5 % |
| 6 | — | 45.6 % | 46.4 % |
| 7 | — | 40.4 % | 48.9 % |
| 8 | — | 38.7 % | 45.9 % |
| 9 | — | 42.9 % | 47.1 % |

### 1.4 Sens des divergences de la variante A

| Action lue par la règle | Action jouée | Occurrences |
|---|---|---|
| call | bet | 2 156 |
| check | bet | 1 341 |
| fold | bet | 1 020 |
| call | check | 648 |
| bet | check | 593 |
| fold | call | 258 |
| fold | check | 171 |
| call | fold | 163 |

### 1.5 Ce que cette mesure ne peut pas voir

Deux bornes, à énoncer avec le résultat :


1. **La chaîne de pensée n'est pas restituée** (§L.1). Le fournisseur facture un raisonnement interne qu'il ne rend jamais. Une incohérence entre cette chaîne et l'action jouée est invisible par construction.
2. **La variante C porte sur un sous-ensemble sélectionné**, et non aléatoire : les décisions où l'agent formule son choix en toutes lettres. Le taux obtenu n'est pas une fréquence de campagne.


Le codage manuel sur échantillon stratifié (§2.2.5.3, troisième volet) n'est donc pas un raffinement facultatif : c'est **la seule voie** vers un taux d'incohérence défendable. Ce que les mesures automatiques établissent est plus étroit, et solide : *l'agent ne se contredit pas explicitement*.



## 2. Dégénérescence des stratégies mixtes

Fréquences de `infosets.csv`, restreintes aux couples série × info-set observés au moins **20** fois (340 couples écartés à ce titre) — une fréquence sur trois observations ne dit rien d'un mélange.


**La ventilation par adversaire est obligatoire.** Contre Station et Over-folder, la meilleure réponse *est* pure : une fréquence à 0 ou 1 y est optimale, pas dégénérée.


### 2.1 Où l'optimum exige-t-il un mélange ?

| Adversaire | Info-sets à meilleure réponse mixte |
|---|---|
| Over-folder | **aucun** — la meilleure réponse est entièrement pure |
| Station | **aucun** — la meilleure réponse est entièrement pure |
| GTO | **aucun** — la meilleure réponse est entièrement pure |

Contre GTO, toute meilleure réponse rapporte la valeur du jeu, y compris les pures : c'est l'**équilibre** qui exige un mélange, et c'est à lui qu'on compare. Les quatre info-sets concernés :

| Info-set | Fréquence d'équilibre |
|---|---|
| `J1/C0/ouverture` | 1/3 |
| `J1/C1/face_mise_apres_check` | 2/3 |
| `J2/C0/apres_check` | 1/3 |
| `J2/C1/face_mise` | 1/3 |

### 2.2 Concentration aux bornes, par adversaire

| Adversaire | Traitement | Séries × info-sets | Aux bornes (0 ou 1) |
|---|---|---|---|
| Over-folder | SM | 51 | 0.0 % |
| Over-folder | ICL | 168 | 64.3 % |
| Over-folder | AE | 168 | 89.3 % |
| Station | SM | 51 | 0.0 % |
| Station | ICL | 168 | 15.5 % |
| Station | AE | 168 | 79.2 % |
| GTO | SM | 34 | 0.0 % |
| GTO | AE | 113 | 62.8 % |

*À lire en regard du 2.1 : contre Over-folder et Station, une valeur élevée est le signe d'une politique correcte, non d'une dégénérescence.*

### 2.3 Le signal — les info-sets mixtes, contre GTO

| Info-set | Équilibre | Traitement | Séries | Aux bornes | `p` moyen | Écart moyen à l'équilibre |
|---|---|---|---|---|---|---|
| `J1/C0/ouverture` | 1/3 | SM | 9 | **0.0 %** | 0.279 | 0.078 |
| `J1/C0/ouverture` | 1/3 | AE | 28 | **50.0 %** | 0.248 | 0.301 |
| `J1/C1/face_mise_apres_check` | 2/3 | AE | 1 | **0.0 %** | 0.667 | 0.000 |
| `J2/C0/apres_check` | 1/3 | AE | 2 | **50.0 %** | 0.071 | 0.262 |
| `J2/C1/face_mise` | 1/3 | SM | 1 | **0.0 %** | 0.682 | 0.348 |
| `J2/C1/face_mise` | 1/3 | AE | 5 | **40.0 %** | 0.201 | 0.254 |

### 2.4 Pourquoi la ventilation change la conclusion

Sur `J1/C0/ouverture` — le bluff au sceau faible, que l'équilibre veut à 1/3 — le même comptage donne deux chiffres très différents selon qu'on ventile ou non :

| Périmètre | Séries | Aux bornes | Lecture |
|---|---|---|---|
| Tous adversaires confondus | 167 | **56.3 %** | **trompeur** — contre Station et Over-folder, être à une borne *est* l'optimum |
| Contre GTO seulement | 37 | **37.8 %** | le signal réel : l'équilibre y exige un mélange |

*Le premier chiffre est celui qui figurait dans les notes de travail. Il surestime la dégénérescence en comptant comme telle une politique pure là où la politique pure est correcte.*


### 2.5 Le résultat, et son contrôle interne

Sur `J1/C0/ouverture`, contre l'adversaire à l'équilibre :

| | Séries | Aux bornes | Distance moyenne à l'équilibre |
|---|---|---|---|
| SM — sans mémoire | 9 | **0.0 %** | 0.078 |
| AE — première série, note encore vide | 3 | **0.0 %** | 0.113 |
| AE — séries suivantes, note écrite | 25 | **56.0 %** | 0.323 |

**La mémoire ne corrige pas la dégénérescence : elle la produit.** Privé de mémoire, l'agent joue des fréquences intermédiaires, et proches de la valeur d'équilibre. Doté d'une note, il s'échoue sur les bornes dans près de six séries sur dix.


La deuxième ligne est un **contrôle interne** qui exclut toute explication par le traitement ou par le harnais : la première série d'une exécution AE se joue avec un emplacement mémoire présent mais vide — même modèle, même gabarit, même exécution, même adversaire, seule la note manque. Aucune fréquence n'y est aux bornes. L'effondrement apparaît exactement à la première série jouée avec une note écrite.


**Ce n'est pas un effondrement vers une borne unique, mais une alternance entre les deux.** Sur les 25 séries concernées, 13 sont à zéro exactement et 1 à un exactement, et l'on relève **7 sauts de plus de 0,40** entre deux séries consécutives. L'agent ne remplace pas le mélange par une politique pure stable : il remplace une randomisation **intra-série** par une alternance **inter-séries** — il choisit une règle, l'applique intégralement pendant K manches, puis en change à la frontière. La variabilité que l'équilibre demande existe encore, mais elle a migré vers une échelle de temps où elle ne produit aucune imprévisibilité au sein d'une série.


C'est le résultat que H4 cherchait, et il est **conjoint** à H1 et H3 : ce qui rend la mémoire auto-écrite supérieure — contraindre l'agent à formuler une règle, donc achever l'induction — est exactement ce qui la rend incapable de randomiser. Une règle écrite en langue naturelle est déterministe : elle dit « engager avec le sceau fort », jamais « engager avec le sceau faible une fois sur trois ». Le canal qui porte l'adaptation ne sait pas porter une fréquence.

