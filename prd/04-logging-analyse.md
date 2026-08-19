# PRD 4 — Logging, centralisation & analyse

Version 1.0 — 2026-08-19. Dépend de : PRD 3 (émetteur des événements). Alimente directement le mémoire écrit.

## 1. Principes

- **JSONL = source de vérité**, append-only, une ligne = un événement, un couple de fichiers par run (`turns.jsonl`, `sessions.jsonl`). Robuste au crash, streamable, lisible en Python (`pandas.read_json(lines=True)`) et R (`jsonlite::stream_in`).
- **CSV dérivé = vue d'analyse**, régénérable à tout moment depuis les JSONL par un script unique — jamais édité à la main, jamais source.
- Tout événement porte : `run_id, condition, bot, replication, machine, session, hash_regles, modele, version_arene, horodatage`. On doit pouvoir reconstruire **toute** l'expérience à partir des seuls logs (spec §9 : c'est le grain qui permet l'écart exact).
- Les logs vivent sous `C:\arene-runs\<run_id>\logs\` (hors OneDrive, D7) et sont **committés dans Git aux frontières de session** (centralisation choisie par le pilote) : dossier `runs/` du dépôt, un commit par session close, message normé `run <run_id> session <s>`. JSONL texte + diffs append-only = Git-friendly ; à ~10⁵ manches × ~1 Ko, l'ordre de grandeur reste en dizaines–centaines de Mo, acceptable ; `git gc` et compression Git font le reste.

## 2. Schéma `turns.jsonl` (un événement par décision, spec §9 « par tour »)

```jsonc
{
  "run_id": "AE-station-r2", "session": 4, "manche": 137, "decision": 1,
  "etat_reel":   { "carte_agent": 2, "carte_bot": 0, "carte_ecartee": 1,
                   "position_agent": "J1", "historique": ["check", "bet"] },   // canonique
  "infoset":     "J1-haut-face-mise",                                          // clé PRD 1 §3
  "vue_servie":  "<prompt complet servi, obfusqué>",                           // vérifiabilité totale
  "sortie_brute": "<texte intégral du modèle, raisonnement libre inclus>",
  "action_parsee": "call", "parsing": "ok|relance|defaut",
  "resultat_manche": 2,                    // renseigné sur la dernière décision de la manche
  "flags": ["ecriture_intra_session"],     // + "erreur_harnais", "action_par_defaut", …
  "tokens": {"in": 812, "out": 143}, "latence_ms": 2140
}
```

`etat_reel` est en représentation canonique (le moteur ne connaît pas l'obfuscation, PRD 1 §2) ; `vue_servie` est le texte obfusqué exact — le couple permet de vérifier après coup que la vue était légale et fidèle.

## 3. Schéma `sessions.jsonl` (un événement par session close, spec §9 « par session »)

```jsonc
{
  "run_id": "AE-station-r2", "session": 4, "K": 200, "positions": {"J1": 100, "J2": 100},
  "memoire": { "M_s": "<snapshot entrée>", "M_s1": "<snapshot sortie>",
               "evenements": [{"type": "ajout|suppression|modification|overflow|elagage", "detail": "…"}],
               "ecritures_intra_session": 3 },
  "pi_hat":   { "J1-bas-ouverture": {"p": 0.31, "n": 34}, "...": "12 entrées, p + effectif",
                "infosets_non_observes": ["J1-bas-face-mise", "…"] },
  "mesures":  { "ecart_exploitation": 0.42,       // EV(BR) − EV(π̂)  [PRD 1 §6.2]
                "reference_recite": 0.35,          // EV(π̂) − EV(GTO) vs même bot
                "ev_pi_hat": 0.58, "ev_br": 1.0,
                "ev_realisee": 0.51 },             // gains effectifs/manche (contrôle : ≈ ev_pi_hat)
  "defauts": {"actions_par_defaut": 1, "relances": 4, "erreurs_harnais": 0},
  "drapeaux_deobfuscation": [ {"manche": 88, "regle": "poker", "extrait": "…"} ],
  "plateau": {"evalue": true, "pente": -0.01, "declare": false},
  "hash_donnes": "sha256:…", "cout_session_tokens": {"in": 1.6e6, "out": 2.9e5}
}
```

`ev_realisee` vs `ev_pi_hat` est un auto-contrôle : un écart important entre les deux signale un bug d'estimation ou de règlement des mains.

## 4. Détecteur de dé-obfuscation (simple — choix pilote, spec §1.bis)

- Passe par mots-clés (insensible casse/accents) sur `sortie_brute`, le contenu MEMORY.md et les récaps réinjectés : `kuhn`, `poker`, `jack|queen|king|valet|dame|roi`, `J/Q/K` isolés, `bluff.*(1/3|un tiers|0[.,]33)`, `nash`, `équilibre|equilibrium`, `GTO`, `alpha`.
- Deux niveaux : **dé-obfuscation** (nomme le jeu réel) et **récitation** (énonce des constantes d'équilibre sans nommer le jeu) — drapeaux distincts, car leurs implications diffèrent (contamination vs stratégie récitée, spec §4).
- Chaque hit = drapeau logué avec extrait ; **aucune censure automatique** — on observe, on n'intervient pas ; le traitement (exclusion de run, discussion) est une décision d'analyse documentée dans le mémoire. Vigilance particulière sur le **canal mémoire** : un hit dans MEMORY.md ou dans la fenêtre ICL se propage à toutes les sessions suivantes (spec §1.bis) — le drapeau de session porte donc aussi sur le contenu du slot, pas seulement sur les sorties.
- Revue manuelle par échantillon (~20 sorties/run) pour estimer le taux de faux négatifs du filtre — honnêteté méthodologique à rapporter.

## 5. CSV dérivés (analyse rapide Python/R)

- `sessions.csv` — 1 ligne/session : `run_id, condition, bot, replication, machine, session, ecart, reference_recite, ev_realisee, n_defauts, n_flags_deobf, K, cout_tokens`. **C'est le fichier du mémoire** : ~300–500 lignes, toutes les courbes et tous les tests en sortent.
- `infosets.csv` — 1 ligne/(session × info-set) : `p, n` — pour les analyses fines (sur quel info-set l'agent apprend-il d'abord ? le bluff Tor disparaît-il contre Station ?).
- `memoire.csv` — 1 ligne/frontière AE : taille MEMORY.md, entrées ±, overflow, hits dé-obfuscation — la trajectoire du contenu mémoire (observable spec §6).

## 6. Analyses prévues (script Python ; R en complément au choix)

1. **Courbes d'adaptation** — la figure centrale : Écart(s) par session, grille 3 conditions × 3 bots, N=3 tracés fins + moyenne épaisse, bande min–max ; lignes de référence y = écart d'un réciteur GTO (1/9 Station, 7/9 Over-folder — oracle PRD 1) et y = 0 (meilleure réponse). Lecture attendue : plate (SM) / dents de scie (ICL) / escalier (AE), spec §5.
2. **Question de contribution** (spec §5) : l'escalier AE monte-t-il plus haut/plus vite que l'ICL ? Comparaison appariée par réplication (donnes communes) : écart final moyen, aire sous la courbe, session d'atteinte du plateau — effets + IC bootstrap (N=3 : pas de test puissant, on rapporte des effets appariés, pas des p-values décoratives).
3. **Discriminateur récité vs émergent** (spec §3/§4) : trajectoire de (écart, référence_récité) par session — un réciteur reste près de « référence_récité ≈ 0 » ; un exploiteur s'en éloigne dans les deux directions opposées selon le bot.
4. **Analyse du canal mémoire** : contenu MEMORY.md aux frontières — distille-t-il la fuite (« il couvre toujours » / « il se retire toujours ») ? élagage destructeur ? corrélation écriture→saut de la courbe à s+1.
5. **Contrôles** : effet-machine (si 2 machines : comparaison des runs appariés par machine), équilibre des positions, taux de défauts par condition, coût.
6. Figures pour le mémoire : réutiliser la charte du skill dataviz au moment de produire les figures finales.

## 7. Critères d'acceptation

1. `rejouer.py` : re-règle chaque manche depuis `turns.jsonl` (état réel + actions parsées) et retrouve exactement `resultat_manche`, π̂ et l'écart de `sessions.jsonl` — test de complétude du logging (« tout est reconstructible »).
2. Le mini-run de bout en bout (PRD 3 §10.1) produit des CSV lisibles d'un trait en pandas et en R.
3. Détecteur : suite de tests avec vrais positifs (« c'est du poker », « bluff 1/3 »), vrais négatifs (vocabulaire obfusqué pur), et pièges (« Tor » ne déclenche rien).
4. Un run committé dans Git est relisible sur l'autre machine sans étape manuelle (chemins relatifs, UTF-8, pas de dépendance à `C:\`).
5. Aucune ligne JSONL invalide sur l'ensemble d'un run (validation de schéma en écriture).
