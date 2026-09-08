# `Soutenance.pptx`

**La source, c'est `Soutenance.pptx` à la racine du dépôt.** Il s'édite dans PowerPoint,
et c'est lui qui fait foi. Les scripts de ce dossier ont servi à produire la première
version du deck ; depuis le 8 septembre 2026 ils ne la produisent plus.

Cette règle est l'inverse de la précédente. Avant, le `.pptx` était généré à chaque build
depuis `contenu.py` et toute retouche manuelle était perdue. Les slides ont ensuite été
reprises à la main dans PowerPoint, `contenu.py` n'a pas suivi, et les deux ont divergé.
Plutôt que de remonter les modifications dans le code, on a inversé la règle : le fichier
PowerPoint est devenu la référence.

## Ce qu'on peut encore lancer

```bash
"C:/Users/videt/anaconda3/python.exe" scripts/soutenance/notes.py    # notes de présentateur
"C:/Users/videt/anaconda3/python.exe" scripts/soutenance/rendre.py   # aperçu PNG
```

`notes.py` ouvre le `.pptx` existant, remplace les notes de présentateur et le réenregistre.
Il ne touche ni aux slides, ni aux images, ni aux géométries — vérifié par comparaison du
texte et des positions avant/après. C'est le seul script encore dans la chaîne.

`rendre.py` exporte les 12 slides en PNG dans `apercu/` via PowerPoint. Lecture seule, sans
effet sur le fichier. Demande PowerPoint installé et `pywin32`. Les PNG sont ignorés par git.

Dépendance des deux : `python-pptx` (`pip install python-pptx`).

## Ce qu'il ne faut plus lancer

> **`assembler.py` détruirait le deck.** Il repart de `Soutenance-squelette.pptx` et réécrit
> l'archive entière depuis `contenu.py` — donc il écrase toutes les modifications faites
> dans PowerPoint. Même chose pour la chaîne complète décrite dans les anciennes versions de
> ce fichier.

Il porte désormais une garde : lancé sans argument, il refuse et explique pourquoi, sans
rien écrire. Repartir de zéro depuis `contenu.py` demande `--force`, et une sauvegarde du
`.pptx` au préalable.

`assembler.py`, `contenu.py` et `deck.py` sont conservés parce qu'ils documentent comment le
deck a été construit, et parce que `deck.py` reste la référence du style. Ils ne décrivent
plus l'état des slides.

## Les fichiers

| Fichier | Rôle |
|---|---|
| `notes.py` | **Actif.** Les notes de présentateur, une par slide, minutées. Le fichier à éditer pour changer ce qui se dit. |
| `rendre.py` | **Actif.** Export PNG des slides dans `apercu/`, pour vérifier les débordements. |
| `deck.py` | Historique, mais utile : le design system en briques XML, toutes les constantes de style en tête. À consulter avant de retoucher une slide à la main. |
| `contenu.py` | Historique. Le texte des slides 2-6 et 8-11 tel qu'il était à la génération. **Désynchronisé du `.pptx` depuis le 8 septembre 2026.** |
| `assembler.py` | Historique. **Destructif** : voir l'avertissement ci-dessus. |
| `Soutenance-squelette.pptx` | La maquette d'origine : thème, polices embarquées (Playfair Display, Inter), logos, et les slides 7 et 12 écrites à la main. |

## Éditer les notes

Les notes sont de la prose suivie, à dire telle quelle, et non des puces. Deux pièges dans
`notes.py`, tous deux réglés — ne pas les défaire :

- **`deplier()`** recolle les lignes. Le texte des notes est coupé à ~90 colonnes dans le
  source pour rester lisible, or `notes_text_frame.text` fait un paragraphe PowerPoint par
  ligne. Sans ce recollage, une note de six paragraphes en produit trente, chacun avec son
  retour forcé au milieu d'une phrase. Un paragraphe = un bloc séparé par une ligne vide.
- **`sans_puce()`** pose un `<a:buNone/>` sur chaque paragraphe. Le `notesMaster` du
  squelette impose une puce `●` par héritage ; elle n'apparaît nulle part dans le texte mais
  s'affiche dans le volet de commentaires.

Chaque note s'ouvre sur un minutage indicatif. Le total actuel est d'environ 3 480 mots,
soit près de 25 minutes à 140 mots/minute, pour une cible à 20 : les minutages par slide
sont donc optimistes et le texte demande une coupe.

## Retoucher une slide

Dans PowerPoint, directement. Pour rester dans le style du deck, les valeurs de `deck.py` :

| Élément | Valeur |
|---|---|
| Format | 10″ × 5,625″, fond blanc |
| Titre | Playfair Display SemiBold 26 pt `#993333`, à x 0,5″ / y 0,35″ |
| Carte | roundRect rayon 2285, fond `#FDFBF7`, filet `#E5E5E5`, barre d'accent `#993333` de 0,04″ à gauche |
| Titre de carte | Playfair Display gras 13 pt `#993333` |
| Corps | Inter 9 pt `#333333` ; chapô `#5B6570` ; puces ● |
| Zone de contenu | x 0,5″ → 9,5″, y 1,05″ → 4,85″ |
| Logos | deux images en bas à droite, sur chaque slide |

Deux limites de rendu rencontrées à la génération, qui valent toujours à la main : Playfair
Display n'a pas le glyphe `→`, et PowerPoint coupe la ligne avant `:`, `»` ou `%`, ce qui
demande des espaces insécables.

Les figures sont les PNG de `memoire/figures/`, non retouchés : ils portent leur propre
titre et sous-titre, ce qui évite de dupliquer le titre de slide.

| Slide | Figure |
|---|---|
| 8 — H1 | `fig1-trajectoires.png` |
| 9 — H2 | `fig2-asymetrie.png` |
| 10 — H3 | `fig4-zoom.png` |
| 11 — H4 | `fig5-degenerescence.png` |

## Versionner

`Soutenance.pptx` étant devenu la source, il doit être commité à chaque modification qui
compte — c'est le seul endroit où vit le contenu des slides. Un `.pptx` est une archive
binaire : git ne sait pas en fusionner deux versions, donc ne pas l'éditer depuis deux
machines sans avoir poussé entre les deux.
