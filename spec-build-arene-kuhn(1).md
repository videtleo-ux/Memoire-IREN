# Spec de build — Arène Kuhn obfusquée & mesure d'adaptation

Document autoportant destiné au build (Claude Code). Toutes les décisions de cadrage sont figées ; ce qui reste au pilote est signalé en §10.

---

## 0. Objet

Construire une **arène** qui fait jouer un agent LLM à un Kuhn poker **obfusqué**, en parties répétées découpées en **sessions**, contre des adversaires à politique **fixe et connue**, sous **trois conditions mémoire**, et qui logue tout au grain permettant de calculer un **écart d'exploitation exact par session**.

Principe directeur unique : toute adaptation observée doit être attribuable à la **mémoire** (la variable), pas au harnais. L'arène construit l'*arène*, pas l'agent — l'agent auto-écrit est Hermès (Nous Research), utilisé nativement.

---

## 1. Le jeu (règles exactes)

Kuhn poker, deux joueurs. Paquet de 3 cartes ordonnées `bas < moyen < haut`. Une carte cachée par joueur, la 3ᵉ écartée. **Ante = 1** chacun (pot = 2). Un seul tour de mise, mise = 1.

Arbre :
- **P1** (premier à parler) : `check` ou `bet(1)`.
  - P1 check :
    - P2 `check` → abattage, meilleure carte gagne (gagnant +1, perdant −1).
    - P2 `bet(1)` → P1 : `fold` (P1 −1, P2 +1) ou `call(1)` → abattage (gagnant +2, perdant −2).
  - P1 bet(1) :
    - P2 `fold` (P1 +1, P2 −1) ou `call(1)` → abattage (gagnant +2, perdant −2).

**Ensembles d'information : 12** (6 par joueur) — pour chaque carte : P1-ouverture, P1-face-à-une-mise-après-son-check, P2-après-un-check-de-P1, P2-face-à-une-mise.

## 1.bis Obfuscation (identité masquée, genre préservé)

Objectif : empêcher l'agent de reconnaître **Kuhn poker** (jeu résolu, dans les données d'entraînement) et d'en réciter l'équilibre. On masque l'**identité**, on garde le **genre** (jeu de mise adversarial à information cachée — c'est l'objet d'étude).

Règles :
- **Aucune** occurrence de « Kuhn », « poker », ni des noms de cartes J/Q/K ou 1/2/3.
- Cartes = **3 jetons arbitraires** avec ordre de dominance **énoncé explicitement** dans les règles (ex. `Tor ≺ Vael ≺ Rhun`, préciser « Rhun bat Vael, Vael bat Tor »). Éviter tout label ordinal ou évocateur.
- Nom de jeu neutre, actions à vocabulaire de mise conservé (le genre est préservé) mais non calqué sur le lexique poker si évitable.
- **Le même vocabulaire obfusqué partout** : trois conditions mémoire, tous les bots, bras humain éventuel. Sinon vocabulaire = confond.
- Paiements identiques à Kuhn (ante 1, mise 1).

Surveillance : loguer et détecter dans le contenu **écrit** de l'agent toute **dé-obfuscation** (« c'est du Kuhn poker, l'équilibre est… ») — la contamination peut rentrer par le canal mémoire et se réinjecter à chaque session.

---

## 2. Stratégie d'équilibre de référence (GTO)

Sert à la fois d'**adversaire-plafond** et d'**étalon d'optimalité**. Famille d'équilibres paramétrée par α ∈ [0, 1/3] ; on fixe **α = 1/3** (point cité dans l'état de l'art, Loriente & Diez).

- **P1** : `bet` Haut (prob 1) ; `check` Moyen (prob 1, ne mise jamais) ; `bet`(bluff) Bas prob 1/3, sinon check. Après check, face à une mise : `call` Moyen prob 1/3, `fold` Bas.
- **P2** : face à une mise → `call` Haut, `fold` Bas, `call` Moyen prob 1/3. Face à un check → `bet` Haut (prob 1), `bet` Bas prob 1/3, `check` Moyen.

> **À vérifier avant de hard-coder** : recaler les constantes exactes (notamment les fréquences d'appel au point d'indifférence) sur Loriente & Diez — le calcul d'écart d'exploitation en dépend.

---

## 3. Bots adversaires (déterministes)

Kuhn a 3 cartes : le retrait de cartes **étouffe les fuites fréquentielles** (tout « appel élargi » retombe vers du 50/50). Les fuites **nettes et fortes** de Kuhn sont donc **déterministes** — meilleure réponse triviale à calculer, écart large et lisible. On retient la **paire opposée** + GTO.

| Bot | Règle | Fuite | Meilleure réponse de l'agent | Pourquoi le GTO **récité** saigne |
|---|---|---|---|---|
| **GTO** | équilibre §2 | aucune | rien à exploiter | — (borne-plafond) |
| **Station** | ne mise/bluffe **jamais** ; face à une mise, **suit toujours** | sur-appel | **ne jamais bluffer** ; value-bet le Haut ; checker le reste | il bluffe le Bas à fréquence fixe → chaque bluff est payé et perdu (−2 répété) |
| **Over-folder** | ne mise **jamais** ; face à une mise, **se couche toujours** | sur-fold | **miser toute main** (vol +1 garanti) | il checke Moyen et 2/3 des Bas → rate tous les vols gratuits (+1 laissés) |

**Station et Over-folder = axe opposé** (face à une mise : trop suivre vs trop se coucher) → exploits **inverses** (ne jamais bluffer vs toujours miser). C'est le discriminateur : un agent qui *récite* une fréquence de bluff fixe est faux **dans les deux sens**. S'adapter dans les deux directions ⇒ adaptation **émergente**, pas récitée.

Spec par ensemble d'information (P1 = premier ; positions alternées en jeu) :

| | Station | Over-folder |
|---|---|---|
| P1 ouvre (Bas/Moyen/Haut) | check / check / check | check / check / check |
| P2 après un check | check / check / check | check / check / check |
| face à une mise (Bas/Moyen/Haut) | **call / call / call** | **fold / fold / fold** |

---

## 4. Meilleure réponse & écart d'exploitation

Stratégie du bot **fixe et connue** ⇒ meilleure réponse **exacte** par maximisation d'EV à chaque ensemble d'information de l'agent (croyance sur la carte adverse par retrait de cartes ; réponses du bot en aval connues). 12 ensembles, calcul direct.

Par **session** s (mémoire gelée ⇒ politique stationnaire) :
- estimer la politique empirique de l'agent `π̂(M_s)` sur les K manches ;
- **Écart d'exploitation(s) = EV(meilleure réponse) − EV(π̂(M_s))** — exact, pas estimé.
- Référence « récité » : **EV(π̂) − EV(GTO)**. π̂ ≈ GTO ⇒ jeu défensif/récité ; π̂ → meilleure réponse ⇒ exploitation (adaptation émergente).

La suite `Écart(0), Écart(1), …` indexée par session **est** la courbe d'adaptation (§6).

---

## 5. Les trois conditions mémoire — **même modèle de base partout**

Le modèle est **la constante**, la mémoire **la seule chose qui bouge** (sinon confond mémoire × modèle). Un endpoint unique sert le **modèle de base d'Hermès** (vLLM) ; trois harnais l'appellent :

| Condition | Slot mémoire | Signature attendue de la courbe | Runs |
|---|---|---|---|
| **Sans mémoire** | rien ; contexte neuf à chaque manche | **plate** (aveugle à chaque donne) = plancher | quelques sessions |
| **Historique brut (ICL)** | transcript des sessions passées, injecté à la frontière, gelé intra-session, fenêtré à la limite de contexte | **dents de scie** (recraque puis oublie) | runs longs |
| **Auto-écrit (Hermès)** | MEMORY.md natif, frozen snapshot par session, réflexion/écriture à la frontière | **escalier monotone** (capitalise) | runs longs |

Question de contribution rendue lisible : *l'escalier réflexif monte-t-il plus haut/plus vite que les dents de scie brutes ?* S'ils montent pareil, l'auto-écriture n'apporte rien — résultat en soi. La différenciation d'avec MEMO tient à la présence de la baseline ICL : ne pas la couper.

---

## 6. Découpage en sessions — l'horloge d'adaptation

La **session** est l'unité atomique d'adaptation (imposée par le *frozen snapshot* d'Hermès : mémoire capturée au démarrage, figée en cours de session ; écriture visible seulement à la session suivante). Même découpage en sessions **pour les trois conditions** (horloge commune).

Boucle de l'arbitre pour un run **Hermès**, condition « contexte neuf par manche » (décision figée) :

1. Ouvrir session s → Hermès charge le snapshot `M_s` depuis le **store isolé du run**.
2. Pour k = 1..K : distribuer (séquence de donnes commune, §8) ; alterner position P1/P2 ; jouer la manche avec un **contexte neuf** = `M_s` gelé + état de la main courante uniquement (**pas** d'accumulation inter-manches) ; l'arbitre sert la vue légale obfusquée et logue le tour.
3. Fermer session → l'arbitre fournit à Hermès le **récap des K manches** ; Hermès **réfléchit (style Reflexion) et écrit/actualise MEMORY.md** → persisté disque = `M_{s+1}`. L'arbitre **capture le snapshot** `M_{s+1}`.
4. Estimer `π̂(M_s)` ; calculer l'écart d'exploitation du palier (§4).
5. Session suivante charge `M_{s+1}`. Répéter jusqu'au **plateau de l'écart + marge**.

⇒ MEMORY.md est le **canal d'apprentissage unique** ; l'escalier est stationnaire par palier ; « apprenable » = l'agent doit **distiller la fuite du bot dans MEMORY.md**.

**Resets, trois échelles :**
- entre **runs** (conditions, réplications) : reset complet, `M_0` vide → agent frais (attribution primaire propre) ;
- entre **sessions** d'un run : **aucun** reset (l'accumulation = l'escalier) ;
- intra-**session** : contexte neuf par manche + MEMORY.md gelé.

**Contrainte MEMORY.md** : ~8–15 entrées, plafond strict, **pas de compaction auto** → overflow = erreur, l'agent doit s'**auto-élaguer**. À loguer comme *observable* (que garde-t-il ?) et *risque* (overflow, élagage destructeur).

ICL : même boucle, slot = transcript fenêtré injecté à la frontière (pas d'étape d'écriture). Sans mémoire : même boucle de jeu, aucun slot, aucune accumulation.

---

## 7. Isolation mémoire par run — **piège silencieux**

MEMORY.md vit dans `~/.hermes/memories/`. Deux runs Hermès parallèles sur un même PC **s'écrasent mutuellement** la mémoire → contamination totale et **invisible**. Chaque run doit avoir un **store isolé** : `HOME` dédié, ou `~/.hermes` dédié, ou **conteneur** par run. À **vérifier explicitement**, jamais supposer.

---

## 8. Orchestration (multi-PC, **sans réseau**)

- Unité parallélisable = le **run** (S sessions séquentielles, un adversaire, une condition).
- Les **sessions d'un run restent séquentielles sur une même machine** (`M_s` dépend de `M_{s-1}`) — **ne pas** découper un run entre PC.
- Les runs entre eux sont indépendants (réplications, conditions) → chaque PC avale des runs entiers.
- **Pas de serveur de jeu live** : arbitre local jouant un run en autarcie + distribution des runs + **collecte centralisée des logs**.
- **Réduction de variance** : servir la **même séquence de donnes** aux trois conditions (nombres aléatoires communs, appariés sur seed) → seule la mémoire diffère.
- Homogénéité machine : poids/quantization/paramètres d'inférence **identiques** sur tous les PC (vérifiés) ; affectation run→machine **randomisée** ; machine **loguée** (test d'effet-machine a posteriori).

---

## 9. Logging (deux grains)

- **Par tour** : état réel, vue obfusquée servie, sortie brute du modèle (**raisonnement libre inclus**), action parsée, résultat.
- **Par session** : snapshot `M_s` d'entrée **et** `M_{s+1}` de sortie, événements d'écriture/élagage, `π̂(M_s)`, écart d'exploitation du palier, équilibre des positions P1/P2, drapeaux de dé-obfuscation/récitation d'équilibre.

---

## 10. Laissé au pilote

- **K manches / session** : plancher de mesure — assez pour (a) nourrir la réflexion de l'agent, (b) estimer `π̂` aux ensembles d'information de Kuhn. Ordre de grandeur à confirmer : **~150–300**. Puis résolution de la courbe achetée par le **nombre de sessions**, pas en rognant la session.
- **Sessions jusqu'au plateau** (+ marge) : horizon de convergence donné par le pilote.
- **Réplications N** : dimensionnées par la variance mesurée au pilote.
- Rappel : MEMORY.md étant capé, au-delà d'une longueur de session les manches en plus n'achètent plus de *contenu* mémoire, seulement de la précision d'estimation (rendements décroissants).

---

## 11. Hors périmètre du build primaire (extensions)

- **Bras transfert** (sonde secondaire) : même agent enchaînant les conditions, mémoire portée. Ordre informatif = **bot biaisé d'abord** (installer l'habitude), **puis GTO** (révéler la persévération / transfert négatif). Jamais dans le noyau primaire (l'ordre y serait un confond).
- **Bras humain** : humain comme **sujet** (reproduit-il les biais ?), via UI minimale séparée — jamais comme adversaire fixe. Consentement/éthique IREN à traiter.
- **Adversaire LLM figé** (politique gelée) comme adversaire « complexe » mais stationnaire, si besoin d'un adversaire non trivial sans casser l'instrument.
