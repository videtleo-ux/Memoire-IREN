# Plan détaillé de la partie III

*Sept sections. Chacune est construite de la même façon : ce qu'elle doit
établir, les paragraphes à écrire dans l'ordre, les pièces à insérer, et ce qu'il
ne faut pas oublier de dire.*

**État** — données closes, 24 exécutions, 177 séries, 26 550 manches, 47,27 $ ·
**Volume visé** — 17 à 24 pages · **Établi le** — 25 août 2026.

> **Version en ligne** : [claude.ai/code/artifact/79b11edd](https://claude.ai/code/artifact/79b11edd-7000-4027-a905-c296ee7bdadf)
> — mise en forme de ce document. Le Markdown reste la source ; les deux doivent
> rester alignés.

## Comment lire ce plan

Chaque section a exactement la même anatomie. On lit toujours les quatre mêmes
blocs, dans le même ordre.

| Bloc | Contenu |
|---|---|
| **Objectif** | Ce que la section doit établir. Une phrase. Si le lecteur ne l'a pas compris en sortant, la section a raté. |
| **Ce que tu écris** | Les paragraphes, dans l'ordre de rédaction. **Un numéro = un paragraphe du mémoire**, avec l'affirmation à tenir et les chiffres qui la portent. |
| **Les pièces** | Les figures et tableaux à insérer, avec le fichier d'où ils viennent. |
| **À ne pas oublier** | Les précautions. Sans elles, l'énoncé serait plus fort que la preuve — et c'est là qu'un jury attaque. |

## Les sept sections

| § | Titre | En une ligne |
|---|---|---|
| 3.1 | Comment lire les deux instruments | Les deux mesures n'en font qu'une à adversaire fixé. À assumer. |
| 3.2 | L'adaptation existe et vient de la mémoire — **H1** | Neuf paires sur neuf. La ligne sans mémoire ne décroît jamais. |
| 3.3 | Elle exploite, elle ne récite pas — **H2** | L'agent atteint exactement le maximum théorique d'exploitation. |
| 3.4 | Le mécanisme de rétention — **H3** | Le cœur. Même vitesse, mais ICL s'arrête avant zéro. Ce n'était pas prévu. |
| 3.5 | Ce que l'agent écrit | Les 90 notes. Une stratégie juste, expliquée à l'envers. |
| 3.6 | Ce que l'adaptation coûte — **H4** | Une mesure invalide, et une mémoire qui rigidifie la politique. |
| 3.7 | Synthèse | Les deux branches de la question, et la tension entre elles. |

---

## Le fil de la partie

*L'adaptation existe et vient de la mémoire* (3.2) → *elle exploite au lieu de
réciter* (3.3) → *le mécanisme de rétention compte, mais pas comme prévu* (3.4)
→ *voici ce que l'agent écrit* (3.5) → *et voici ce que son adaptation lui coûte*
(3.6) → *ce que les quatre résultats disent ensemble* (3.7).

La partie suit l'ordre du plan d'analyse pré-enregistré au §2.2.9 du chapitre de
méthode, sans le réordonner. À dire dès l'ouverture : les hypothèses, leurs
critères de réfutation et l'ordre de leur examen ont été écrits **avant** la
campagne.

Le point d'arrivée est une **tension**, pas une liste : l'agent atteint l'optimum
exploitatif, et il s'éloigne en même temps de la seule compétence que l'équilibre
exige. La partie doit y conduire, pas la découvrir en 3.7.

## Avant 3.1 — le paragraphe d'ouverture

**Quatre à cinq lignes, sans titre de section et sans tableau.** Il n'y a pas de
section « ce qui a été joué » : la campagne exécutée et ses contrôles de
conformité sont au **§2.2.8** du chapitre de méthode, qui revendique
explicitement de décrire un protocole exécuté. Dupliquer ces tableaux ici les
ferait diverger dès la première relecture.

Ce que le paragraphe doit donner au lecteur qui ouvrirait le mémoire à cette
page :

- l'échelle — **24 exécutions, 177 séries, 26 550 manches, 27 290 décisions** ;
- le matériel — `gpt-5.6-luna`, effort `medium`, K = 150 ;
- le fait que les trois traitements sont **appariés à la carte près**, ce qui
  fonde toutes les comparaisons qui suivent ;
- que la condition ICL n'a pas été jouée contre GTO (§2.2.7) — sinon son absence
  dans chaque figure se lira comme un oubli ;
- un renvoi au §2.2.8 pour les contrôles de conformité et les trois incidents
  d'exécution.

---

## 3.1 Comment lire les deux instruments

`1 à 2 pages` · `contribution de méthode`

**Objectif** — Le lecteur sait ce que valent 0, 0,111 et 0,778 — et il apprend
que les deux instruments n'en font qu'un à adversaire fixé.

### Ce que tu écris

1. **Rappel des deux définitions.** Écart = EV(meilleure réponse) − EV(π̂).
   Référence récitée = EV(π̂) − EV(équilibre). Deux phrases, pas plus : le
   chapitre 2 les a posées.
2. **Le constat.** La somme des deux vaut une constante de l'adversaire — qui est
   exactement l'écart d'un récitant. Vérifié à la douzième décimale sur les
   177 séries : 0,778 contre Over-folder, 0,111 contre Station, 0 contre GTO.
3. **Ce qui en découle, et qu'il faut assumer.** À adversaire fixé, les deux
   instruments ont **un seul degré de liberté**. La référence récitée est un
   recalage affine de l'écart, pas une seconde mesure. Le point 2 du plan
   d'analyse — « trajectoire dans le plan des deux instruments » — ne peut donner
   qu'une droite de pente −1 : il n'est pas produit.
4. **Ce que cela ne remet pas en cause.** H2 reste testée, mais par le *niveau
   relatif à zéro* et par la *comparaison entre adversaires*. C'est ce que disait
   déjà le §2.2.2 : aucune stratégie fixe ne fait descendre les deux courbes
   simultanément. L'identification était au bon endroit ; seule la figure la
   cherchait au mauvais.

> Un mémoire qui trouve et énonce la redondance de ses propres instruments est
> plus crédible qu'un mémoire qui présente deux courbes en laissant croire à deux
> mesures.
> — *la raison d'être de cette section*

### Les pièces

- **Tableau** — somme des deux instruments, par adversaire · à composer

### À ne pas oublier

- **Une correction au chapitre 2.** Le §2.4 énonce le contrôle négatif comme deux
  falsifications indépendantes — « référence récitée positive *ou* écart
  négatif ». Contre GTO la constante vaut 0, donc récitée = −écart : c'est **une
  seule condition**. Soit on corrige le §2.4, soit on le signale ici en note.

---

## 3.2 L'adaptation existe et vient de la mémoire — H1

`4 à 5 pages`

**Objectif** — L'écart décroît en condition mémoire, et pas en condition sans
mémoire — sur les mêmes cartes.

### Ce que tu écris

1. **Présenter la figure 1, et lui laisser la place.** C'est la figure centrale
   de la partie. Trois panneaux par adversaire, les trois traitements sur les
   mêmes axes, réplications en filigrane, lignes de référence à 0 et à l'écart du
   récitant.
2. **L'effet apparié, en tableau.** Écart final AE contre moyenne SM, à donnes
   identiques. Les **neuf paires sur neuf** vont dans le même sens, avec une
   dispersion inter-réplications de l'ordre du centième. Avec trois réplications,
   c'est la cohérence du signe qui porte — pas un test d'hypothèse dont la
   puissance serait décorative.
3. **La ligne sans mémoire ne décroît jamais.** C'est elle qui exclut que la
   décroissance vienne de l'instrument : elle tourne sur les mêmes donnes et le
   même calcul. Sans ce témoin, H1 ne serait pas identifiée.
4. **L'écart AE atteint 0,000 exactement.** Contre les deux adversaires
   exploitables, et il s'y tient. Pas « proche de zéro » : la mesure est exacte,
   en fractions rationnelles, par énumération complète des douze ensembles
   d'information.

| Adversaire | SM | AE | Réduction | Par réplication |
|---|---|---|---|---|
| Over-folder | 0,704 | 0,000 | **+0,704** | +0,688 · +0,707 · +0,717 |
| Station | 0,222 | 0,002 | **+0,220** | +0,229 · +0,207 · +0,224 |
| GTO | 0,187 | 0,008 | **+0,178** | +0,156 · +0,195 · +0,184 |

### Les pièces

- **Figure 1** — trajectoires d'adaptation · `memoire/figures/fig1-trajectoires.png`
- **Tableau** — effet apparié AE − SM · `resultats.md §2.1`

### À ne pas oublier

- **Expliquer pourquoi la courbe SM s'arrête à la série 2.** Trois séries par
  protocole (§2.2.6) : sans mémoire rien ne s'accumule, et trois points
  établissent un niveau et sa dispersion. Sans cette phrase, le lecteur y voit
  une exécution tronquée.
- **Ne pas parler de vitesse ici.** Le plateau AE tombe dès la série 2 et le plan
  la résout mal. C'est en 3.4 que la question se pose.

---

## 3.3 Elle exploite, elle ne récite pas — H2

`3 à 4 pages`

**Objectif** — L'adaptation consiste à s'écarter de l'équilibre dans la direction
que chaque adversaire commande — et jusqu'à l'optimum.

### Ce que tu écris

1. **Présenter la figure 2, et dire pourquoi on la trace quand même.** C'est un
   recalage de la figure 1 (cf. 3.1) — mais il déplace le zéro sur le
   comportement du récitant, et **le franchissement de signe y devient visible**.
   Il ne l'est pas sur la figure 1.
2. **L'agent atteint exactement la valeur maximale de l'exploitation.** +0,778
   contre Over-folder, soit 7/9. +0,110 contre Station, pour un maximum de
   1/9 = 0,111. Il ne récite pas l'équilibre : il s'en écarte, dans la direction
   commandée, jusqu'à l'optimum théorique.
3. **L'asymétrie est le test décisif.** Les deux fuites sont opposées —
   sur-paiement contre sur-abandon — et leurs exploitations demandent des
   ajustements de sens contraire. Aucune stratégie fixe, fût-elle celle de
   l'équilibre, ne fait descendre les deux courbes. C'est là que repose
   l'identification, et non sur l'obfuscation (cf. §L.1 bis).
4. **Sans mémoire, l'agent est *sous* l'équilibre.** −0,111 contre Station,
   −0,187 contre GTO. La condition SM ne mesure donc pas « un récitant » mais
   quelque chose de moins bon qu'un récitant. Nuance à énoncer : le chapitre 2
   présentait SM comme la mesure empirique du niveau récité.

| Adversaire | SM | AE (séries 7-9) | Maximum théorique |
|---|---|---|---|
| Over-folder | +0,074 | **+0,778** | +0,778 (7/9) |
| Station | −0,111 | **+0,110** | +0,111 (1/9) |
| GTO | −0,187 | −0,024 | 0 (plafond) |

### 3.3.1 — Le contrôle négatif

1. **La propriété qui devait être vérifiée l'est.** Contre GTO, la référence
   récitée reste **négative sur les trente séries** : l'agent ne gagne jamais plus
   que l'équilibre face à un adversaire à l'équilibre.
2. **L'écart décroît pourtant contre GTO — et ce n'est pas un artefact.**
   0,161 → 0,008. Contre GTO il n'y a rien à exploiter : la mémoire n'y sert qu'à
   cesser de commettre des erreurs propres. Le témoin qui tranche est la condition
   SM, où la décroissance est absente sur les mêmes donnes et le même calcul.
3. **Signaler que le chapitre de méthode a été corrigé sur ce point.** Sa
   formulation initiale tenait toute décroissance contre GTO pour un défaut
   invalidant — critère qui, pris au mot, invalidait des résultats sains.

### Les pièces

- **Figure 2** — récitation ou exploitation · `memoire/figures/fig2-recitation.png`
- **Tableau** — référence récitée et maxima · `resultats.md §2.2`

### À ne pas oublier

- Rappeler que la figure 2 est un recalage, pas une seconde mesure — sinon 3.1 ne
  sert à rien.
- Le maximum théorique n'est pas une borne empirique : il se calcule d'avance. Que
  l'agent l'atteigne **exactement** est ce qui rend le résultat fort.

---

## 3.4 Le mécanisme de rétention — H3

`4 à 5 pages` · **le cœur de la contribution**

**Objectif** — Deux mémoires recevant la même matière ne produisent pas la même
adaptation — et la différence n'est pas celle qu'on attendait.

### Ce que tu écris

1. **Rappeler le dispositif, sans l'escamoter.** ICL et AE reçoivent **exactement
   la même matière première** : le récapitulatif brut des séries passées. Seul le
   mécanisme de rétention diffère — l'expérimentateur empile et évince par séries
   entières d'un côté, l'agent synthétise de l'autre. Sans cela, H3 comparerait
   deux informations et non deux mémoires.
2. **Les effets appariés, sur la moyenne des quatre dernières séries.** Plus
   robuste qu'un point terminal isolé. Contre Station, l'intervalle exclut zéro.
   Contre Over-folder, il le contient.
3. **H3 est vérifiée, mais sous condition — et la condition est interprétable.**
   Le mécanisme ne départage les deux mémoires que là où la tâche exige une
   politique *différenciée selon la carte*. Contre Over-folder, la stratégie
   optimale tient en une règle unique — engager quel que soit le sceau — et un
   historique brut la maintient aussi bien qu'une note synthétisée. Contre
   Station, où il faut cesser de bluffer *et* miser pour la valeur au seul sceau
   supérieur, la synthèse fait la différence.
4. **Le mécanisme observé n'est pas celui qui était anticipé.** Le chapitre 2
   prévoyait pour ICL un profil d'oubli en dents de scie, produit par l'éviction
   des séries anciennes à saturation. **Rien de tel n'apparaît** — et la vitesse
   ne les sépare pas non plus : *les deux conditions chutent à la première
   frontière*, dans les mêmes proportions. Ce qui les sépare est ce qui suit — AE
   se verrouille sur zéro, ICL s'arrête à un résidu non nul (~0,058 puis ~0,040)
   qu'il n'annule sur aucune des trente séries. La différence porte sur la
   **complétude** de l'induction, ni sur la vitesse ni sur la rétention.
5. **Descendre au niveau de l'ensemble d'information — c'est là qu'est le
   résultat.** Contre Station, huit des douze info-sets sont des points
   d'indifférence exacts : la qualité de la politique ne se joue que sur quatre
   décisions, résumées en deux règles — *ne jamais bluffer le sceau faible*,
   *toujours engager le sceau fort*. Après dix séries, ICL bluffe encore le sceau
   faible dans 7 à 9 % des cas et laisse passer 3 à 6 % de ses mises de valeur ;
   AE a supprimé le second défaut entièrement et ramené le premier sous le pour
   cent. Décomposition du résidu d'ICL : **64 % de bluffs résiduels, 36 % de mises
   de valeur manquées**.
6. **L'explication : une règle, ou deux.** Contre Over-folder, la politique
   optimale tient en une règle unique et **positive** — engager quel que soit le
   sceau — que le journal brut porte de façon transparente. Contre Station, elle
   demande deux règles, dont une **négative**, et une distinction entre les
   sceaux. Cesser de faire quelque chose est ce qu'un historique brut soutient
   mal : un bluff perdant y figure comme une manche parmi cent cinquante, et rien
   ne rassemble ces occurrences en interdiction. L'étape de synthèse fait
   précisément cela.
7. **Une remarque de méthode, qui joue en faveur du plan.** La dispersion des
   paires ICL − AE (0,0059 sur Station) est **deux fois et demie plus faible** que
   celle des paires SM − AE (0,0153) sur laquelle le dimensionnement était
   calibré : deux conditions partageant tout sauf le mécanisme ont des différences
   moins bruitées. La différence détectable à trois réplications tombe à 0,015, et
   l'effet mesuré (+0,038) la dépasse largement. Le plan était plus que suffisant,
   là où le §2.2.7 le donnait pour tout juste adéquat.

| Adversaire | Effet ICL − AE | Écart-type | IC 95 % | Conclusion |
|---|---|---|---|---|
| **Station** | **+0,0381** | 0,0059 | ± 0,0148 | l'intervalle exclut zéro : **AE l'emporte** |
| Over-folder | +0,0039 | 0,0023 | ± 0,0056 | l'intervalle contient zéro : indistinguable |

### Les pièces

- **Figure 2** — verrouillage sur zéro contre résidu · `memoire/figures/fig2-recitation.png`
- **Tableau** — effets appariés ICL − AE · `resultats.md §2.4`
- **Tableau** — trajectoires moyennes série par série · `partie3.md §3.4.3`
- **Tableau** — les quatre décisions qui coûtent · `partie3.md §3.4.4`

### À ne pas oublier

- **Le dispositif résout mal ce qui le sépare.** Le plateau AE est atteint dès la
  série 2 : les huit séries suivantes mesurent la *persistance*, pas la vitesse.
  Or c'est sur la vitesse que se joue la différence avec ICL. À dire franchement,
  et à reprendre en Limites.
- **Le profil d'oubli d'ICL n'a pas été observé à cet horizon.** On ne peut pas
  conclure qu'il n'existe pas — seulement qu'il ne s'est pas manifesté là.
- **ICL n'a pas été joué contre GTO** (§2.2.7) : la vérification qu'ICL ne bat pas
  l'équilibre contre l'équilibre n'existe pas.
- C'est la seule section où le résultat **contredit** ce que le chapitre 2
  prédisait. L'assumer plutôt que l'aplatir : c'est ce qui fait la contribution.

---

## 3.5 Ce que l'agent écrit

`2 à 3 pages` · analyse qualitative

**Objectif** — La mémoire auto-écrite n'est pas une boîte noire : on peut lire ce
qu'elle contient, et ce qu'elle contient est instructif — y compris quand c'est
faux.

### Ce que tu écris

1. **Le format observé.** Une seule entrée, de 377 à 1 561 caractères. Jamais de
   saturation, jamais d'élagage destructeur sur les 90 frontières. La contrainte
   de capacité — 8 à 15 entrées, pas de compaction automatique — n'a jamais mordu.
2. **La longueur suit la difficulté du problème.** Environ 380 caractères contre
   Over-folder, où il n'y a qu'une régularité à énoncer ; environ 1 500 contre
   GTO, où il faut détailler carte par carte. La note est proportionnée à la tâche.
3. **Citer une note, en entier.** C'est le dispositif qui fonctionne comme prévu :
   l'agent distille la régularité adverse à partir d'un journal brut, sans qu'on
   la lui souffle.
4. **Première imperfection : l'inversion des rôles.** Un run sur trois contre
   Over-folder décrit l'adversaire comme ayant « toujours engagé », alors que le
   bot n'a jamais misé — 795 `check`, 1 400 `fold`, zéro `bet` dans les journaux —
   **tout en jouant la stratégie optimale**. Le comportement est juste, son
   explication est fausse.
5. **Seconde imperfection : l'écrasement plutôt que l'accumulation.** L'agent
   traite systématiquement sa note antérieure comme une erreur à corriger —
   « remplace l'ancien −13 » — et non comme le résultat d'une série passée. La
   mémoire est réécrite, pas cumulée.
6. **La phrase qui ouvre 3.6.** L'inversion des rôles *est déjà* une incohérence
   entre le raisonnement et l'action — avec cette particularité que c'est l'action
   qui a raison.

> « Il n'a jamais engagé ni couvert. Ouvrant, il a toujours retenu ; Répondant,
> il s'est toujours retiré face à notre engagement. Nos 150 engagements ont donc
> tous rapporté +1, sans coût ni révélation des sceaux. »
> — *AE-over-folder-r2, frontière de la série 9 — écart 0,000*

### Les pièces

- **Corpus** — les 90 notes intégrales · `donnees/notes-ae.md`
- **Données** — tailles, entrées, élagages · `donnees/memoire.csv`

### À ne pas oublier

- C'est la seule section qualitative de la partie. Elle vaut par les
  **citations**, pas par des comptages — ne pas la transformer en tableau.
- Les deux imperfections ne sont pas des anecdotes : elles préparent 3.6. Le dire
  explicitement en fin de section.

---

## 3.6 Ce que l'adaptation coûte — H4

`4 à 5 pages` · `contribution de méthode`

**Objectif** — L'agent exploite parfaitement *et* raisonne mal — deux choses qui
coexistent, ce qui interdit de l'assimiler à un optimisateur rationnel.

### 3.6.1 — Une mesure qui ne mesurait pas

1. **Appliquer la règle pré-enregistrée, et donner son résultat.** Comparer
   l'action jouée à *la dernière action nommée dans le texte libre* (§2.2.5.3)
   donne **47,8 %** sur 13 442 décisions verbalisées. À un point des **45,1 %** de
   GTBENCH.
2. **Démontrer que ce chiffre est un artefact.** La coïncidence avec la
   littérature est précisément ce qui le rendait dangereux : il confirmait H4 sans
   effort. La cause est grammaticale — le raisonnement français conclut par une
   clause contrastive qui nomme l'option **rejetée**.
3. **Donner la preuve, pas seulement l'argument.** Huit divergences tirées au
   hasard et relues : **huit faux positifs**, tous de cette forme. Écarter les
   actions attribuées à l'adversaire ne sauve rien (36,6 %) : le défaut est
   structurel, pas dans l'attribution du sujet.
4. **La variante à haute précision, et son résultat.** Ne compter que les
   décisions où l'agent *énonce* son choix — « il vaut mieux X », « je choisis
   X » — donne **0 divergence sur 604**.
5. **L'énoncé à tenir, et pas un mot de plus.** *L'agent ne se contredit jamais
   explicitement.* C'est plus étroit que « l'agent est cohérent », et c'est tout
   ce que les données permettent.

> « Engager garantit donc un gain de +1, **tandis que retenir** expose à une perte
> selon le sceau adverse. »
> — *action jouée : engager. La règle lit « retenir » et compte une incohérence.*

| Variante de la règle | Décisions mesurables | Divergences | Taux |
|---|---|---|---|
| A — positionnelle, pré-enregistrée | 13 442 | 6 422 | 47,8 % |
| B — sujet adverse écarté | 12 095 | 4 425 | 36,6 % |
| C — l'agent énonce son choix | 604 | 0 | **0,00 %** |

### 3.6.2 — La dégénérescence des stratégies mixtes

1. **Montrer pourquoi la ventilation par adversaire est obligatoire.** Contre
   Station et Over-folder, la meilleure réponse *est* pure : une fréquence à 0 ou
   1 y est optimale, pas dégénérée. Agréger revient à compter comme un biais une
   politique correcte. Le même comptage donne 56 % agrégé contre **41 %** contre
   GTO seul.
2. **Le résultat, sur l'info-set du bluff au sceau faible.** `J1/C0/ouverture`,
   que l'équilibre veut à 1/3, contre l'adversaire à l'équilibre : **0 %** des
   séries aux bornes sans mémoire, **53 %** avec mémoire auto-écrite.
3. **L'interprétation — et c'est le résultat de la section.** *La mémoire ne
   corrige pas la dégénérescence : elle l'aggrave.* L'agent sans mémoire produit
   des fréquences intermédiaires, non par maîtrise du mélange mais parce que ses
   décisions varient d'une manche à l'autre sans règle stable. Dès qu'il se dote
   d'une note, il se donne une règle — et une règle écrite est **déterministe**.
   Il bascule vers le tout ou rien, là même où l'optimum demande un tiers.

| Sur `J1/C0/ouverture`, contre GTO | Séries | Aux bornes 0 ou 1 |
|---|---|---|
| SM — sans mémoire | 9 | **0 %** |
| AE — mémoire auto-écrite | 30 | **53 %** |

### Les pièces

- **Rapport** — les deux mesures, en entier · `memoire/h4-mesures.md`
- **Code** — régénération · `analyse/h4.py`

### À ne pas oublier

- **Les deux bornes de la mesure d'incohérence**, à énoncer avec le résultat.
  Un : la chaîne de pensée est facturée mais jamais restituée (§L.1) — une
  incohérence entre elle et l'action est invisible par construction. Deux : les
  604 décisions sont un sous-ensemble *sélectionné*, non aléatoire.
- **Le codage manuel n'a pas été conduit** (troisième volet du §2.2.5.3). Limite
  assumée, à porter en *Limites*, pas un oubli à taire.
- **Le résultat de 3.6.2 repose sur un seul info-set.** Les trois autres info-sets
  mixtes ont des effectifs de 1 à 5 séries — GTO ne mise pas assez souvent pour
  les alimenter. À écrire.
- **Correction à porter au chapitre 2 :** la règle du §2.2.5.3 est invalide sur ce
  corpus. Recommandation — la traiter entièrement ici, avec un simple renvoi
  depuis le chapitre 2, pour que celui-ci reste un protocole et non un journal de
  bord.

---

## 3.7 Synthèse

`2 à 3 pages`

**Objectif** — Répondre aux deux branches de la question de recherche — et
montrer que la réponse à l'une explique le défaut relevé par l'autre.

### Ce que tu écris

1. **Le tableau des quatre hypothèses.** Énoncé, critère de réfutation
   pré-enregistré, verdict. Court : il récapitule, il ne réargumente pas.
2. **Branche *homo œconomicus* : oui.** Doté d'une mémoire auto-écrite, l'agent
   atteint l'exploitation maximale contre les deux adversaires exploitables, et
   l'atteint **exactement**. La question « développe-t-il une adaptation
   s'apparentant à une stratégie ? » reçoit une réponse positive et mesurée.
3. **Branche *homo silicus* : la même adaptation le rigidifie.** Ce qui rend
   l'agent optimal contre un adversaire à faille — se donner une règle écrite —
   est ce qui le rend incapable de randomiser là où l'équilibre l'exige.
   L'adaptation et le biais ne coexistent pas par hasard : **c'est le même
   mécanisme**. Une note est une règle ; une règle est déterministe.
4. **Ce que le dispositif apporte à la littérature.** La séparation des trois
   dimensions — exploitative, GTO, biais de décision — que les travaux existants
   confondent (§1.5.4). Sans elle, on aurait observé « l'agent joue mieux » et
   conclu à une rationalité accrue, en manquant que sa politique s'éloigne de
   l'équilibre au moment même où elle exploite le mieux.

| | Énoncé | Verdict |
|---|---|---|
| **H1** | l'adaptation vient de la mémoire | **établie** — 9 paires sur 9 |
| **H2** | elle exploite, ne récite pas | **établie** — optimum atteint exactement, contrôle négatif tenu |
| **H3** | le mécanisme de rétention compte | **établie sous condition** — et le mécanisme n'est pas celui prévu |
| **H4** | des biais persistent | **établie sur un volet** — dégénérescence aggravée ; incohérence explicite absente |

### À ne pas oublier

- **Ne pas traiter les limites ici.** Effectif, modèle unique, tâche unique,
  horizon, codage manuel non conduit, contrôle négatif absent en ICL : tout cela
  va dans la partie *Limites et extensions*.
- Le paragraphe 3 est le point d'arrivée du mémoire entier. Il doit se lire comme
  la conclusion d'une démonstration, pas comme une remarque finale.

---

## Les pièces, en un coup d'œil

| Pièce | Fichier | Section |
|---|---|---|
| Figure 1 — trajectoires | `memoire/figures/fig1-trajectoires.png` | 3.2 |
| Figure 2 — récitation | `memoire/figures/fig2-recitation.png` | 3.3 · 3.4 |
| Mesures et effets appariés | `memoire/resultats.md` | 3.2 à 3.4 |
| Notes de l'agent | `donnees/notes-ae.md` | 3.5 |
| Mesures H4 | `memoire/h4-mesures.md` | 3.6 |
| Régénérer les figures | `analyse/figures.py` | — |
| Régénérer H4 | `analyse/h4.py` | — |

## Corrections à porter au chapitre 2

Aucune n'est bloquante pour commencer à rédiger.

1. **§2.4 — le contrôle négatif.** Il y est énoncé comme deux falsifications
   indépendantes (« référence récitée positive *ou* écart négatif ») ; contre GTO
   c'est une seule condition, puisque récitée = −écart. Voir 3.1.
2. **§2.2.5.3 — la règle d'incohérence.** Telle qu'elle est écrite, elle est
   invalide sur ce corpus. À signaler dans le chapitre, ou à traiter entièrement
   en 3.6.1 avec un renvoi. Voir 3.6.
3. **§L.1 — le chiffre de 58 %. ✅ Déjà corrigé.** Il agrégeait les trois
   adversaires ; ramené à 38 % contre GTO.

---

*Plan établi sur données closes : 24 exécutions, 177 séries, 26 550 manches,
47,27 $. Sources — `memoire/resultats.md`, `memoire/h4-mesures.md`,
`memoire/methodologie.md`, `donnees/`. Le codage manuel sur échantillon stratifié
(§2.2.5.3, troisième volet) est écarté du périmètre.*
