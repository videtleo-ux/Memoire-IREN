# PRD 1 — Moteur de jeu obfusqué, meilleure réponse & écart d'exploitation

Version 1.1 — 2026-08-19. Dépend de : rien (aucun LLM, aucun coût API). Bloque : PRD 3. Implémenté et testé (`src/moteur/`, `tests/test_moteur.py`).

> **v1.1** — correction des formules paramétrées en α de T5 et T6 (§7.1), fausses hors α = 1/3 dans la v1.0. Les valeurs épinglées 1/9 et 7/9 sont inchangées et vérifiées.

## 1. Objectif

Module Python autonome et testé qui (a) fait jouer une manche entre deux politiques quelconques, (b) calcule la **meilleure réponse exacte** à toute politique fixe et connue, (c) calcule l'**écart d'exploitation** d'une politique (empirique ou fixe). C'est l'instrument de mesure du projet : toute erreur ici invalide silencieusement tous les runs — d'où un oracle analytique complet (§7) à faire passer **avant** le moindre appel API.

## 2. Règles du jeu (payoffs Kuhn, identité obfusquée)

- Jeu : **« L'Épreuve des Trois Sceaux »**. Jetons : **Tor ≺ Vael ≺ Rhun** (règles servies à l'agent : « Rhun bat Vael, Vael bat Tor »). Interdits absolus dans tout texte visible de l'agent : `kuhn`, `poker`, J/Q/K, 1/2/3 comme rangs, tout label ordinal évocateur.
- Actions : *retenir* (check), *engager* (bet 1), *couvrir* (call 1), *se retirer* (fold).
- 2 joueurs, 1 jeton caché chacun parmi 3, le 3ᵉ écarté. Droit d'entrée 1 chacun (pot = 2). Un seul tour de décision.
- Arbre : J1 *retenir* ou *engager*. Après *retenir* : J2 *retenir* (abattage ±1) ou *engager* → J1 *se retirer* (−1/+1) ou *couvrir* (abattage ±2). Après *engager* : J2 *se retirer* (+1/−1) ou *couvrir* (abattage ±2).
- **Représentation interne du moteur : non obfusquée** (cartes 0<1<2, actions check/bet/call/fold). L'obfuscation est une **couche de rendu** appliquée uniquement aux textes servis à l'agent (PRD 2) et une couche de parsing au retour. Le moteur, les logs internes et les tests parlent le langage canonique ; le mapping canonique↔obfusqué est défini en un seul endroit, versionné et haché dans les logs (décision D5).

## 3. Ensembles d'information — source de vérité unique

12 info-sets, clé canonique `(position, carte, contexte)` :

| # | Position | Contexte | Actions légales |
|---|---|---|---|
| 1–3 | J1 | ouverture | check / bet |
| 4–6 | J1 | après son check, face à une mise | fold / call |
| 7–9 | J2 | après un check de J1 | check / bet |
| 10–12 | J2 | face à une mise | fold / call |

Chaque décision est binaire → une politique complète = **12 probabilités** (proba de l'action « agressive » : bet ou call selon le contexte). Ce module exporte l'énumération ; PRD 3 (estimation de π̂) et PRD 4 (logs) la réutilisent telle quelle, sans redéfinition.

**Fait exploitable** : contre Station et Over-folder, qui ne misent jamais, les info-sets 4–6 et 10–12 sont **inatteignables** — l'agent ne fait jamais face à une mise et prend **exactement 1 décision par manche**. Conséquences : π̂ n'est estimée que sur 6 info-sets contre ces bots (les 6 autres sont non contraints par les données et n'affectent pas l'EV — le moteur doit les traiter proprement, cf. §6.3), et le coût LLM par manche est réduit d'un facteur ~1,5 vs GTO.

## 4. Stratégie GTO de référence (α = 1/3) — constante contestée tranchée

Famille d'équilibres standard de Kuhn, paramètre α ∈ [0, 1/3] ; la spec fige **α = 1/3**.

**J1** : bet Rhun prob 3α = **1** ; check Vael toujours ; bet (bluff) Tor prob α = **1/3**. Après check, face à une mise : call Vael prob **α + 1/3 = 2/3** ; fold Tor toujours ; call Rhun toujours (si check accidentel).
**J2** : face à une mise : call Rhun ; fold Tor ; call Vael prob **1/3**. Face à un check : bet Rhun ; check Vael ; bet (bluff) Tor prob **1/3**.

**Résolution du point que la spec marquait « à vérifier »** : la spec §2 écrit « call Moyen prob 1/3 » pour J1 après check-mise. La dérivation analytique donne **α + 1/3**, soit **2/3** à α = 1/3 ; la valeur 1/3 correspond au cas α = 0 (confusion probable entre paramétrages ; le « call Vael 1/3 » de **J2**, lui, est correct — c'est une constante d'indifférence indépendante de α). Arbitre automatique : le test `exploitabilité(GTO) = 0` (§7, T2) **échoue à 1/3 et passe à 2/3**. On implémente 2/3 ; le recoupement avec Loriente & Diez sera cité dans le mémoire quand le papier sera transmis (décision D6, non bloquant).

Le bot GTO est **stochastique** : ses tirages consomment le flux aléatoire dédié au bot (seedé par manche, PRD 3 §4) — jamais le flux des donnes, sinon les conditions ne verraient plus les mêmes cartes.

## 5. Bots déterministes

| Info-set | Station | Over-folder |
|---|---|---|
| J1 ouverture (toute carte) | check | check |
| J2 après check (toute carte) | check | check |
| face à une mise (toute carte, J1 ou J2) | **call** | **fold** |

Tables fixes, zéro aléa, testables en dur. Ce sont les politiques `1..12 → {0,1}` les plus simples possibles ; elles passent par la même interface de politique que GTO et π̂.

## 6. Meilleure réponse exacte & écart d'exploitation

### 6.1 Interface de politique

```python
Politique = Mapping[InfoSet, float]   # proba de l'action agressive (bet/call), 12 entrées
```

GTO, Station, Over-folder et π̂ sont toutes des `Politique`. Le moteur ne distingue pas « bot » et « agent » : il calcule des EV entre deux politiques.

### 6.2 Calculs exacts (énumération exhaustive)

Le jeu est minuscule : 6 deals ordonnés équiprobables × un arbre de profondeur ≤ 3. Tout se calcule par énumération complète, sans échantillonnage :

- `ev(pi_a, pi_b, position_a) → float` : EV exacte par manche de la politique a contre la politique b à position donnée. `ev_moyenne = (ev(a,b,J1) + ev(a,b,J2)) / 2` — l'arène alternant les positions, **toutes les quantités rapportées sont moyennées sur les deux positions**.
- `meilleure_reponse(pi_adverse) → (Politique, float)` : pour chaque info-set de l'agent, backward induction — croyance uniforme sur les 2 cartes restantes, conditionnée par la proba que l'adversaire ait joué l'historique observé avec chaque carte (règle de Bayes, trivial ici), réponses aval de l'adversaire connues ; l'action optimale est le argmax d'EV (proba 0 ou 1 ; en cas d'indifférence exacte, convention figée : l'action passive, et le cas est logué).
- `ecart(pi_agent, pi_adverse) → float` : `ev(meilleure_reponse(pi_adverse), pi_adverse) − ev(pi_agent, pi_adverse)`, moyenné sur les positions. C'est l'**Écart(s)** de la spec §4 quand `pi_agent = π̂(M_s)`.
- Référence « récité » : `ev(pi_agent, pi_adverse) − ev(GTO, pi_adverse)` — distance du comportement observé au comportement d'un réciteur, contre le même adversaire.

### 6.3 Info-sets non observés dans π̂

Contre les bots déterministes, 6 info-sets n'ont jamais de données ; contre GTO, certains peuvent rester vides sur K manches. Convention figée : les entrées non observées de π̂ sont posées à la **valeur GTO** de l'info-set, et un drapeau `infosets_non_observes` est logué par session (PRD 4). Justification : ces info-sets étant inatteignables face au bot concerné, leur valeur **n'affecte pas** `ev(π̂, bot)` ni l'écart — la convention ne sert qu'à rendre π̂ totale et le calcul robuste ; le choix GTO évite d'inventer une agressivité fantôme dans les analyses descriptives de π̂.

## 7. Oracle de tests (analytique, re-dérivé intégralement le 2026-08-19)

Valeurs par manche, moyennées J1/J2. La suite doit les reproduire **exactement** (arithmétique en `Fraction`, pas de flottants dans le moteur d'EV — les 1/18 et 7/9 sont exacts).

| # | Test | Valeur attendue |
|---|---|---|
| T1 | `ev(GTO, GTO, J1)` | **−1/18** (valeur du jeu, invariante sur α ∈ [0, 1/3] — tester α ∈ {0, 1/6, 1/3}) |
| T2 | `ecart(GTO, GTO)` | **0** exactement, pour α ∈ {0, 1/6, 1/3}. **Ce test tranche la constante §4** : il échoue si J1 call Vael = 1/3 à α = 1/3. |
| T3 | `ev(meilleure_reponse(Station), Station)` | **+1/3** (Rhun : bet → call → +2 ; Vael : indifférent, 0 ; Tor : check, −1 ; identique dans les deux positions) |
| T4 | `ev(meilleure_reponse(Over-folder), Over-folder)` | **+1** (bet toute carte → fold → +1, dans les deux positions) |
| T5 | `ecart(GTO, Station)` | **1/9** à α = 1/3 ; en général **2/9 − α/3** (cf. décomposition ci-dessous) |
| T6 | `ecart(GTO, Over-folder)` | **7/9** à α = 1/3 ; en général **8/9 − α/3** (cf. décomposition ci-dessous) |
| T7 | Structure | politiques valides (probas ∈ [0,1]), 12 info-sets atteignables contre GTO, 6 exactement contre Station/Over-folder, actions légales seulement |
| T8 | Obfuscation | aucun texte des templates de rendu ne contient les chaînes interdites (§2) — grep de non-régression |
| T9 | Meilleure réponse sur politique arbitraire | pour 1 000 politiques aléatoires π : `ecart(π, bot) ≥ 0` et `ecart(meilleure_reponse(bot), bot) = 0`, pour les 3 bots |

### 7.1 Décomposition de T5 et T6 (corrigée le 2026-08-19 à l'implémentation)

Les valeurs épinglées **1/9 et 7/9 sont correctes** ; les gloses en α de la version 1.0 de ce PRD ne l'étaient pas hors α = 1/3, parce qu'elles décrivaient la fuite **en position J1 seulement**, alors que toute quantité rapportée est moyennée sur les deux positions (§6.2). Décomposition exacte, reproduite par la suite de tests :

| | Fuite en J1 | Fuite en J2 | Écart rapporté (moyenne) | à α = 1/3 |
|---|---|---|---|---|
| vs **Station** | 1/3 − 2α/3 | **1/9**, constant | **2/9 − α/3** | 1/9 |
| vs **Over-folder** | 1/3 + 2(1−α)/3 = 1 − 2α/3 | **7/9**, constant | **8/9 − α/3** | 7/9 |

Deux points expliquent l'écart avec la v1.0 :

1. **Les fuites de J2 ne dépendent pas de α.** Les fréquences de J2 à l'équilibre (couverture de Vael 1/3, bluff Tor 1/3) sont des constantes d'indifférence indépendantes de α (§4) : seule la stratégie de J1 est paramétrée. Moyenner une fuite variable (J1) et une fuite fixe (J2) divise par deux la pente en α — d'où le −α/3 commun aux deux lignes.
2. **Vs Station, la fuite de J1 a deux termes, pas un.** Le terme « bluffs Tor payés à chaque fois » vaut bien α/3, mais s'y ajoute la **sous-mise de valeur de Rhun** : GTO ne mise Rhun qu'avec probabilité 3α, laissant 1/3 − α sur la table face à un adversaire qui paie toujours. Ce second terme s'annule exactement à α = 1/3 (où 3α = 1, Rhun misé systématiquement) — d'où la coïncidence numérique qui masquait l'erreur. Total J1 : α/3 + (1/3 − α) = 1/3 − 2α/3.

Vs Over-folder, la formule v1.0 était en revanche exacte **en tant que fuite J1** (Rhun rapporte +1 qu'on mise ou non, la fuite ne vient que de Vael jamais volé et de Tor volé à fréquence α) ; il ne lui manquait que le moyennage avec J2.

T5/T6 vérifient au passage le discriminateur central de la spec (§3) : un réciteur saigne **dans les deux sens**, 7 fois plus fort contre Over-folder **à α = 1/3** — asymétrie qu'on doit retrouver dans les courbes réelles. Le rapport 7× est propre à α = 1/3 : l'écart absolu entre les deux, lui, est constant (8/9 − 2/9 = 2/3 quel que soit α).

## 8. Hors périmètre

Séquence de donnes commune et alternance des positions (PRD 3) ; comptage des fréquences π̂ depuis les logs (PRD 3) ; rendu des prompts obfusqués et parsing des réponses LLM (PRD 2) ; détection de dé-obfuscation (PRD 4).

## 9. Critères d'acceptation

1. Suite T1–T9 verte, en `Fraction` exactes.
2. `meilleure_reponse` fonctionne sur toute `Politique` arbitraire (T9), pas seulement les 3 bots — condition nécessaire pour traiter les π̂ bruitées réelles.
3. L'énumération des 12 info-sets est importée par les autres modules, jamais redéfinie.
4. Aucune dépendance réseau ni LLM ; la suite complète tourne en < 10 s sur le Victus.
