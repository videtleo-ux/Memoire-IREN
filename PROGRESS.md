# PROGRESS.md — Suivi d'avancement

Dernière mise à jour : 2026-08-26. Convention : ✅ fait · 🔄 en cours · ⬜ à faire · ⚠️ attention.

> **Pages en ligne** : [chapitre de méthode](https://claude.ai/code/artifact/9c6cc820-7c44-4eac-a360-a69450d35ef5) · [résultats](https://claude.ai/code/artifact/40a26434-ed5f-4640-a651-d0cde8964a0b) · [plan de la partie III](https://claude.ai/code/artifact/79b11edd-7000-4027-a905-c296ee7bdadf) — les deux premières régénérables par `analyse/rendre-*.py`.
>
> **La collecte est close et l'analyse est terminée.** Les quatre hypothèses sont
> instrumentées, la partie III est rédigée **et reportée dans le `.docx`**. Ce qui
> reste est de la rédaction sur les autres chapitres et de la mise en forme —
> détail dans l'audit du document plus bas. Résultats et inventaire des données :
> `memoire/resultats.md`.

## Phase 0 — Cadrage (✅ 2026-08-19)

- ✅ Spec analysée, questionnaire de cadrage, périmètre arrêté
- ✅ Audit d'environnement : Hermes Agent identifié et inspecté (mémoire native, `hermes -z`, pièges de persistance, d'isolation, OneDrive)
- ✅ Équilibre de Kuhn re-dérivé à la main ; constante contestée tranchée (couverture J1-Vael = 2/3 à α = 1/3)
- ✅ Décisions transverses D1–D8 figées · `CONTEXT.md` créé

## Phase 1 — PRD (✅ 2026-08-19)

- ✅ `prd/00` à `prd/04` — architecture, moteur, harnais, arbitre, journalisation

## Phase 2 — Build (✅ 2026-08-21)

- ✅ Moteur de jeu (PRD 1) — arithmétique exacte en `Fraction`, oracle T1–T9
- ✅ Harnais mémoire (PRD 2) — trois conditions, gel fichiers, stores isolés, canari
- ✅ Journal (PRD 4) — schémas validés à l'écriture, détecteur de dé-obfuscation, rejeu
- ✅ Arbitre (PRD 3) — donnes dérivées, boucle session/manche, plateau, reprise sur incident
- ✅ Mini-run de bout en bout sur modèle gratuit

**225 tests verts**, sans dépendance ni appel API dans la suite.

## Phase 3 — Pilote de calibrage (✅ 2026-08-21)

- ✅ Modèle arrêté : `openai/gpt-5.6-luna`, effort `medium` · K = 150 validé sur pièces
- ✅ Fenêtre ICL portée à trois séries (sans quoi H3 devenait tautologique)
- ✅ **Deux failles de contamination trouvées et corrigées** (pièges n°7 et n°8)
- ✅ Pas d'effet plafond : la marge de mesure existe

## Phase 3 bis — Audit adversarial (✅ 2026-08-22)

Conduit **avant** la campagne, sur un dispositif réputé terminé. Quatre constats,
tous à la frontière avec l'outillage tiers, aucun dans le code du dépôt, aucun
détecté par les tests, aucun visible dans les journaux (`AUDIT.md`, `CONTEXT.md` §4 sexies) :

- ✅ **C1** — le chemin du magasin, servi à l'agent par le prompt système, nommait son adversaire → répertoires d'exécution en code opaque
- ✅ **C2** — le prompt ICL à fenêtre pleine dépasse la ligne de commande Windows → transmission par fichier, sans toucher aux paramètres expérimentaux
- ✅ **C3** — les signatures textuelles de panne étaient incomplètes → verdict lu dans le rapport d'usage d'Hermes
- ✅ **C4** — les tokens d'entrée logués valaient 3 (comptés nets du cache) → les trois postes sont enregistrés

## Phase 4 — Campagne (✅ 2026-08-22 au 24)

- ✅ **Tranche SM + AE** — 18 exécutions, 117 séries, 13,01 $
- ✅ **Tranche ICL** — 6 exécutions (Station et Over-folder, dimensionnement au §2.2.7 du chapitre de méthode), 34,26 $
- ✅ **Total : 24 exécutions, 177 séries, 26 550 manches, 27 290 décisions, 47,27 $**
- ✅ Rejeu de complétude **24/24**, intégrité **24/24**, zéro action par défaut, zéro relance, zéro erreur de harnais, zéro rupture du gel
- ✅ Données versionnées dans `donnees/` ; journaux bruts (401 Mo) hors dépôt

**Trois incidents, tous rattrapés sans perte de données** : limite de débit du
fournisseur prise pour une panne (le harnais patiente désormais) ; révocation de
session par réutilisation d'un jeton à usage unique (magasin de jetons partagé —
piège n°11) ; erreur de passage de paramètres au lanceur, interceptée par le CLI
avant tout appel API.

## Phase 5 — Analyse (✅ 2026-08-26)

- ✅ **H1** — l'adaptation vient de la mémoire (effet apparié +0,704 / +0,220 / +0,178 selon l'adversaire, neuf paires sur neuf dans le même sens)
- ✅ **H2** — elle exploite, elle ne récite pas (référence récitée à +0,778 et +0,110, les maxima théoriques ; contrôle négatif tenu sur 39 séries)
- ✅ **H3** — le mécanisme de rétention compte, mais seulement là où la tâche exige une politique différenciée (+0,038 ± 0,015 contre Station ; indistinguable contre Over-folder). **Ce n'est ni la vitesse ni l'oubli qui les sépare, mais la complétude** : les deux conditions chutent à la première frontière, AE se verrouille sur zéro, ICL s'arrête à un résidu qu'il n'annule jamais.
- ✅ **H4** — les deux mesures automatiques sont écrites (`analyse/h4.py` → `memoire/h4-mesures.md`). Le codage manuel est **écarté du périmètre** (décision du 2026-08-25) : il précise le taux d'incohérence, il ne change aucun résultat acquis.
- ✅ Analyse qualitative du canal mémoire (90 notes intégrales dans `donnees/notes-ae.md`) — le canal n'encode **jamais** une fréquence : 0 pourcentage, 0 fraction, 0 proportion en toutes lettres sur 90 notes, contre 358 quantificateurs non chiffrés. C'est le mécanisme de la dégénérescence mesurée en H4.
- ✅ **Conditionnalité en α énoncée** — l'équilibre de Kuhn est une famille à un paramètre ; le protocole en retient un membre (α = 1/3) sans l'avoir jamais dit. Vérifié : l'écart d'exploitation est α-libre, donc H1, H3 et l'énoncé central de H2 le sont aussi ; seule l'échelle de la référence récitée en dépend. Une phrase a dû être nuancée (« sans mémoire, l'agent est en dessous de l'équilibre » vaut à α = 1/3 ; à α = 0 il y serait exactement). Encadré ajouté au §2.2.2, sous-section 3.3.2 ajoutée à la partie III.

## Phase 6 — Rédaction du mémoire (🔄 en cours)

- ✅ **Partie III rédigée** — `memoire/partie3.md`, sections 3.1 à 3.7, ~7 900 mots. Plan dans `memoire/partie3-plan.md`, figures dans `memoire/figures/`, export Word par `analyse/rendre-partie3-docx.py` → `memoire/partie3.docx`.
- ✅ **Chapitre de méthode** — quatre corrections appliquées (§2.4 contrôle négatif énoncé comme un seul test ; §2.2.5.3 règle d'incohérence signalée invalide ; §2.2.3 SM n'est plus « le niveau récité » ; §2.2.9 point 2 du plan d'analyse). Plus l'encadré sur α.
- ✅ **Partie III reportée dans le `.docx`** (2026-08-26, à la main) — sections 3.1 à 3.7 collées, les treize tableaux convertis en vraies tables Word, les deux figures insérées. Le document passe de 269 à 538 paragraphes et de 251 Ko à 766 Ko. Le chapitre 2 y est désormais complet jusqu'à la validité interne.
- 🔄 **Ce qu'il reste à porter dans le `.docx`** — la sous-section 3.3.2 (conditionnalité en α) et les deux corrections du chapitre 2 listées au bas de `memoire/partie3-plan.md` ; plus l'audit ci-dessous.
- ⬜ Rédaction des parties 1 et 4, préparation de la soutenance

### Où en est H4 — `analyse/h4.py`, rapport dans `memoire/h4-mesures.md`

1. **Incohérence raisonnement↔action** — ✅ mesurée, et **la règle pré-enregistrée
   est invalide**. « La dernière action nommée dans le texte libre » rend 47,8 %,
   voisin des 45,1 % de GTBENCH et entièrement artefactuel : le français conclut par
   une clause contrastive qui nomme l'option *rejetée* (« engager garantit +1,
   **tandis que retenir** expose à… »). Huit divergences relues, huit faux positifs.
   La variante à haute précision — ne compter que les décisions où l'agent **énonce**
   son choix (« il vaut mieux X », « je choisis X ») — donne **0 divergence sur 604**.
   L'agent ne se contredit jamais explicitement. ⚠️ La chaîne de pensée n'étant pas
   restituée (§L.1), la mesure ne voit qu'une partie du raisonnement.
2. **Dégénérescence des mixtes** — ✅ mesurée. Contre GTO, sur `J1/C0/ouverture`
   (équilibre 1/3) : **0 % des séries aux bornes sans mémoire, 56 % dès qu'une note
   est écrite**. La mémoire ne l'atténue pas, elle la **produit**. Contrôle interne :
   la première série d'une exécution AE, jouée avec une note encore vide, n'est pas
   aux bornes non plus — l'effondrement apparaît exactement quand la note apparaît.
   Et ce n'est pas un effondrement mais une **alternance** : 13 séries à 0, 1 à 1,
   7 sauts de plus de 0,40 entre séries consécutives — la randomisation intra-série
   est remplacée par une alternance inter-séries.
   ⚠️ Le chiffre de 58 % des notes antérieures agrégeait les trois adversaires : il
   comptait comme dégénérées des politiques pures optimales contre Station et
   Over-folder. Contre GTO seul, c'est **38 %**. Corrigé aussi dans
   `memoire/methodologie.md` §L.1.
3. **Codage manuel** — ❌ **écarté du périmètre** (2026-08-25). Il aurait précisé le
   taux d'incohérence sur les 97,8 % de décisions que la variante à haute précision
   ne couvre pas ; il ne change aucun résultat acquis. Limite assumée et rapportée
   comme telle en §3.6.1 et §3.6.3.

## Audit du document du 2026-08-26 — ce qui reste à faire à la main

Le `.docx` complet a été relu et chaque chiffre recoupé contre `donnees/`.
**Aucune erreur n'invalide un résultat** : les mesures tiennent, les tableaux de
dimensionnement sont exacts, les effets appariés sont justes. Ce qui suit est de la
rédaction et de la mise en forme, à la charge de Léo.

**État après le report de la partie III** (vérifié sur le `.docx` de travail, non
commité) : les placeholders `SOURCE`, `(mettre l'auteur)` et « I don't know » ont
disparu ; la bibliographie a reçu quinze entrées numérotées `[1]`–`[15]`. Le reste
du tableau tient toujours, et le collage a ajouté du Markdown brut.

| Priorité | Constat |
|---|---|
| 🔴 | **Bibliographie — partiellement traitée.** Quinze entrées numérotées `[1]`–`[15]` ont été ajoutées, mais les deux systèmes de citation coexistent toujours (numéroté et auteur-date), Loriente & Diez reste un placeholder, et 23 marqueurs `[188]`, `[305, 373]` d'un autre système traînent. Reste à vérifier les références citées et absentes (Borel 1938, Von Neumann 1928, Ferguson 2004, Reiley 2005/2008, Gao 2025, Wang 2023a, Packer 2024, Guan 2024) et les 6 jamais citées. |
| 🔴 | **Tous les renvois croisés du chapitre 2 pointent dans le vide** — le document numérote 2.1 / 2.3.x / 2.5, le texte renvoie à §2.2.x. Idem §1.5.4 et §L.1. |
| 🔴 | **Blocs toujours absents du `.docx`** — le plan d'analyse (§2.2.9, auquel la partie III renvoie deux fois), les trois paragraphes SM/ICL/AE de §2.3.3 (le tableau y est, pas le texte), les deux sous-sections d'audit, l'encadré sur α, et tout le bloc Limites (L.1, L.1 bis, L.2) — alors que la partie III y renvoie et que le document est titré « Résultats, limites et extensions ». La sous-section 3.3.2 de la partie III n'a pas été reportée non plus. |
| 🟠 | **Markdown non converti — aggravé par le collage.** 538 lignes portent des accents graves (le code inline de la partie III est passé tel quel), 14 `**`, 19 lignes de tableau en tubes, un `M<sub>s</sub>`, un `## 2.5`. Le tableau de validité interne est toujours entièrement en Markdown brut. |
| 🟠 | **Numérotation** — 2.2 et 2.4 n'existent toujours pas ; deux « Tableau 3 » ; les 5 légendes disent encore « Titre, Lecture » ; les 13 tableaux de la partie III, désormais collés, n'ont ni numéro ni légende. |
| 🟡 | **Placeholders — partiellement traités.** `SOURCE`, `(mettre l'auteur)` et « I don't know » ont disparu. Restent `tttt`, « Phrase de transition » ×2, « nanianninain… ». |
| 🟡 | Coquilles récurrentes (« comportemental » pour « comportementale », « sillicus », « Poket de Khun », « Von Neumannen »), page de garde qui tronque la question de recherche, partie III titrée « Résultats, limites et extensions » alors qu'elle ne contient que les résultats. |

**Trois erreurs de chiffres relevées dans la partie III et corrigées** : notes de
333 à 1 906 caractères (et non 377 à 1 561, qui contredisait §3.5.1) ; cent
cinquante engagements par série (et non trois cents, vérifié sur
`decisions.csv`) ; contrôle négatif sur trente-neuf séries (et non trente, qui
contredisait §3.3.1).

## ⚠️ Points ouverts

| Point | Porteur | Impact |
|---|---|---|
| Papier Loriente & Diez à transmettre | Léo | Aucun sur les résultats ; manque un recoupement citable |
| GTO non joué en condition ICL | — | Arbitrage assumé (§2.2.7) ; la vérification qu'ICL ne bat pas l'équilibre contre l'équilibre n'a pas été faite |
| Profil d'oubli d'ICL jamais observé | — | La fenêtre n'a pas produit de décrochage à cet horizon ; demanderait un autre protocole, pas plus du même |

Le Mac M2 n'est plus un point ouvert : la campagne a tourné sur une seule machine,
ce qui supprime aussi le test d'effet-machine (sans objet).

## Journal des sessions

| Date | Fait |
|---|---|
| 2026-08-19 | Cadrage, audit d'environnement, oracle analytique, D1–D8, PRD 00–04. |
| 2026-08-19 | Moteur de jeu implémenté et testé ; constante GTO 2/3 confirmée par l'oracle. |
| 2026-08-21 | Harnais mémoire et journal ; clés de config relevées dans le code d'Hermes et vérifiées par canari réel. |
| 2026-08-21 | Arbitre et orchestration ; le build est complet de la graine au CSV. |
| 2026-08-21 | Pilote de calibrage sur `gpt-5.6-luna`. Deux failles de contamination trouvées et corrigées (pièges n°7 et n°8). |
| 2026-08-22 | **Audit adversarial** : quatre constats, tous à la frontière avec l'outillage tiers. Correctifs et tests de non-régression. |
| 2026-08-22 | **Tranche SM + AE** : 18 exécutions. H1 et H2 établies. |
| 2026-08-23 | Piège n°11 (jetons à usage unique) trouvé et corrigé avant qu'il ne casse la tranche ICL. |
| 2026-08-24 | **Tranche ICL** : 6 exécutions. H3 établie, sous condition. Collecte close. |
| 2026-08-25 | Documents mis à jour ; chapitre de méthode en version définitive. |
| 2026-08-25 | **H4 instrumentée** : la règle d'incohérence pré-enregistrée s'avère invalide (47,8 % artefactuels) ; la dégénérescence des mixtes livre le résultat central, avec son contrôle interne. Figures produites. Codage manuel écarté. |
| 2026-08-25 | **Partie III rédigée** — 3.4 puis 3.6, 3.5, 3.7, 3.1, 3.2, 3.3. Export Word natif (`python-docx`). |
| 2026-08-26 | Deux incohérences de rédaction corrigées : `partie3-plan.md` disait 41 % là où le chiffre arrêté est 38 % ; dans `partie3.md`, 3.3.2 précédait 3.3.1 — ordre rétabli, renvois internes ajustés. |
| 2026-08-26 | **Report de la partie III dans le `.docx`** par Léo : 3.1 à 3.7, treize tableaux en tables Word, deux figures ; le document double de volume. Bibliographie amorcée (15 entrées), trois placeholders levés. Modifications non commitées. |
| 2026-08-26 | **Audit complet du `.docx`** : aucune erreur invalidante, trois chiffres corrigés, la conditionnalité en α énoncée dans les deux chapitres. Le reste de l'audit (bibliographie, renvois, blocs manquants) est traité à la main par Léo. |
