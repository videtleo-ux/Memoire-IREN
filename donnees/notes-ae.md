# Notes mémoire des runs AE

Contenu intégral de `MEMORY.md` à chaque frontière de série, tel que l'agent
l'a écrit lui-même. Source : champ `memoire.M_s1` de `sessions.jsonl`.

L'état servi *pendant* la série s (`M_s`) est celui écrit à la frontière
précédente : la note de la série 0 est donc ce que l'agent a lu pendant la
série 1. La série 0 se joue avec une mémoire vide.

## AE-gto-r1

### Série 0 — écart 0.1812 — 1 entrée(s), 1319 caractères

*Événements : ajout. Écritures bloquées pendant la série : 0.*

```
Jeu des Trois Sceaux — leçons contre cet adversaire : gains = engagement suivi d'un retrait adverse (+1), couverture gagnante (+2), ou retenue mutuelle gagnée (+1). Coûts = couverture perdante (-2), retenue avec sceau inférieur (-1), et retrait après engagement adverse (-1). Quand je suis Ouvrant et engage, l'adversaire se retire souvent ; s'il couvre, il montre très souvent Rhun, parfois Vael, et pratiquement jamais Tor observé : engager avec Tor est très risqué. Quand il engage en Ouvrant, il couvre fréquemment si je réponds ; son sceau révélé est souvent Rhun, parfois Tor, et rarement/jamais Vael dans le bilan. Il se retire aussi parfois quand je couvre : ses engagements ne garantissent donc pas une bonne main. Il existe des bluffs ou engagements avec sceau perdant, notamment Vael ou Tor, que l'on peut parfois exploiter en couvrant. Politique : engager surtout avec Rhun pour provoquer un retrait ; avec Vael, engager si l'adversaire semble réticent/bluffable ; éviter Tor. En Répondant, couvrir avec Rhun ; avec Vael, couvrir seulement contre Tor probable, sinon se retirer ; avec Tor, se retirer par défaut. Les retenues mutuelles sont profitables seulement avec un sceau supérieur ; retenir avec Tor contre Vael coûte -1. Score de la série : -13, principalement à cause des couvertures perdantes (-2).
```

### Série 1 — écart 0.0432 — 1 entrée(s), 1538 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Jeu des Trois Sceaux — bilan corrigé après 150 épreuves : solde cumulé +5 (remplace l'ancien -13). Gains : engagements suivis d'un retrait adverse (+1), surtout avec Rhun ; couvertures gagnantes (+2), très fiables avec Rhun contre Tor ou Vael ; retenues mutuelles gagnées (+1), notamment Vael contre Tor et Rhun contre Vael. Coûts : couvertures perdantes (-2), surtout Vael ou Tor contre Rhun ; engagements avec Vael sont souvent couverts par Rhun et perdent ; retenues mutuelles avec Tor contre Vael coûtent -1. Retrait après engagement adverse coûte -1 mais reste préférable à une couverture spéculative (-2). Adversaire : en Répondant face à mon engagement, il se retire souvent avec Rhun, mais couvre aussi régulièrement ; il a couvert mes engagements avec Rhun et les a perdus, tandis qu'il a couvert mes engagements avec Vael et m'a battu plusieurs fois. Quand il est Ouvrant et engage, les sceaux révélés lors de mes couvertures étaient surtout Tor, parfois Rhun, et jamais Vael dans ce bilan : il bluffe donc probablement parfois avec Tor/Rhun ; ne pas couvrir automatiquement sans Rhun. Politique : engager avec Rhun ; avec Vael, engager seulement comme bluff ponctuel ou si sa réticence est exploitable ; éviter d'engager avec Tor. En Répondant, couvrir par défaut avec Rhun ; avec Vael, couvrir seulement si Tor adverse est assez probable ; avec Tor, se retirer par défaut. Sur retenue adverse, engager avec Rhun ou Vael peut rapporter +1 si l'adversaire se retire, mais accepter qu'il couvre : Rhun reste sûr, Vael est risqué.
```

### Série 2 — écart 0.0000 — 1 entrée(s), 1469 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Épreuve des Trois Sceaux — bilan de 150 épreuves : solde cumulé -20 (remplace l'ancien +5). Gains : engager avec Rhun ; l'adversaire se retire souvent (+1), et ses couvertures révélées étaient Vael, donc Rhun gagne aussi ces confrontations (+2). Répondre à un engagement par couverture avec Rhun a été très rentable contre Tor (+2). Quand l'adversaire retient, engager avec Rhun ou Vael a souvent gagné (+1 si retrait, +2 si couverture adverse perdante). Coûts : retenir avec Tor contre Vael (-1), et se retirer après engagement adverse (-1), mais cela reste préférable à une couverture spéculative (-2). Les couvertures avec Vael perdent contre Rhun (-2) et gagnent contre Tor (+2) : ne couvrir Vael que si Tor adverse est assez probable. Avec Tor, se retirer par défaut ; éviter de couvrir et d'engager. Adversaire : répond à mes engagements avec Rhun par un retrait fréquent, mais couvre parfois ; ses couvertures contre Rhun ont révélé Vael. Lorsqu'il engage après ma retenue, mes couvertures avec Rhun ont souvent révélé Tor. Il couvre régulièrement mes engagements avec Vael, parfois avec Rhun, parfois avec Tor. Politique future : engager avec Rhun dès que possible ; répondre à un engagement par couverture avec Rhun ; avec Vael, couvrir seulement contre Tor probable, sinon se retirer ; avec Tor, se retirer ; éviter de retenir avec Tor et éviter les engagements avec Tor. Sur retenue adverse, engager surtout avec Rhun, Vael seulement comme variante calculée.
```

### Série 3 — écart 0.0231 — 1 entrée(s), 1485 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Épreuve des Trois Sceaux — bilan de 150 épreuves : solde cumulé -11 (corrige -20). Gains : engager avec Rhun ; l'adversaire se retire souvent (+1), et ses couvertures révélées étaient Vael, donc Rhun gagne aussi ces confrontations (+2). Répondre à un engagement par couverture avec Rhun a été très rentable contre Tor (+2). Quand l'adversaire retient, engager avec Rhun ou Vael a souvent gagné (+1 si retrait, +2 si couverture adverse perdante). Coûts : retenir avec Tor contre Vael (-1), et se retirer après engagement adverse (-1), mais cela reste préférable à une couverture spéculative (-2). Les couvertures avec Vael perdent contre Rhun (-2) et gagnent contre Tor (+2) : ne couvrir Vael que si Tor adverse est assez probable. Avec Tor, se retirer par défaut ; éviter de couvrir et d'engager. Adversaire : répond à mes engagements avec Rhun par un retrait fréquent, mais couvre parfois ; ses couvertures contre Rhun ont révélé Vael. Lorsqu'il engage après ma retenue, mes couvertures avec Rhun ont souvent révélé Tor. Il couvre régulièrement mes engagements avec Vael, presque toujours avec Rhun, et ces couvertures me coûtent -2. Politique future : engager avec Rhun dès que possible ; répondre à un engagement par couverture avec Rhun ; avec Vael, couvrir seulement contre Tor probable, sinon se retirer ; avec Tor, se retirer ; éviter de retenir avec Tor et éviter les engagements avec Tor. Sur retenue adverse, engager surtout avec Rhun, Vael seulement comme variante calculée.
```

### Série 4 — écart 0.0000 — 1 entrée(s), 1470 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Épreuve des Trois Sceaux — bilan de 150 épreuves, solde annoncé -16. Ce qui rapporte : engager avec Rhun, comme Ouvrant ou Répondant après une retenue adverse ; l'adversaire se retire souvent (+1), et ses couvertures révélées étaient généralement Vael, donc Rhun gagne (+2). Répondre à un engagement par couverture avec Rhun a été très rentable contre Vael. Quand l'adversaire retient, engager avec Rhun ou parfois Vael a souvent gagné (+1 si retrait, +2 si couverture adverse perdante). Avec Vael, retenir puis couvrir contre Tor rapporte +2 ; mais couvrir contre Rhun coûte -2. Avec Tor, les révélations contre Vael coûtent -1 ; se retirer après engagement adverse coûte -1 mais reste préférable à une couverture spéculative (-2). Politique : engager avec Rhun dès que possible ; répondre à un engagement par couverture avec Rhun ; avec Vael, couvrir seulement si Tor adverse est assez probable, sinon se retirer ; avec Tor, se retirer par défaut, éviter de couvrir, d'engager, et de retenir en réponse à une retenue. Adversaire : répond souvent aux engagements avec Rhun par un retrait, mais couvre parfois avec Vael ; il couvre régulièrement les engagements avec Vael, souvent avec Rhun, ce qui coûte -2 ; lorsqu'il engage après notre retenue, ses sceaux révélés contre nos couvertures avec Rhun étaient souvent Tor. Il semble exploiter nos sceaux faibles (engagements contre Tor/Vael) et sa couverture est prévisible par moments. Solde du bilan fourni : -16 jetons.
```

### Série 5 — écart 0.0000 — 1 entrée(s), 1906 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Épreuve des Trois Sceaux — bilan de 150 épreuves, solde réel annoncé -17 (la somme des soldes ligne par ligne est à privilégier). Ce qui rapporte : engager avec Rhun comme Ouvrant ; répondre à une retenue adverse en engageant surtout avec Rhun (l’adversaire se retire souvent, ou couvre parfois avec Vael et Rhun gagne) ; couvrir un engagement adverse avec Rhun quand Tor adverse est probable ; avec Vael, couvrir seulement si Tor adverse est assez probable. Les couvertures gagnantes Vael/Rhun contre Tor et Rhun contre Tor ont rapporté +2, ainsi que Rhun contre Vael ; les retenues mutuelles avec Vael contre Tor rapportent +1. Ce qui coûte : couvrir avec Vael quand Rhun adverse est probable (-2), couvrir avec Tor contre Vael (-2), et les retenues mutuelles avec Tor contre Vael (-1). Avec Tor, se retirer après engagement adverse coûte -1 mais reste préférable à une couverture spéculative ; éviter d’engager avec Tor, sauf contexte très favorable. Politique : engager avec Rhun dès que possible ; répondre à un engagement par couverture avec Rhun si Tor adverse est plausible, sinon se retirer ; avec Vael, couvrir seulement contre Tor plausible, sinon se retirer ; avec Tor, se retirer par défaut et ne pas retenir/engager inutilement. Adversaire : répond très souvent à nos engagements d’Ouvrant par un retrait, mais peut couvrir (ex. contre Rhun) ; il couvre fréquemment nos engagements de Répondant, surtout quand nous avons Vael/Tor, et ces couvertures sont parfois prévisibles. Après nos retenues, il engage souvent ; ses sceaux révélés contre nos couvertures Vael alternent entre Tor (perdant pour lui) et Rhun (gagnant), suggérant qu’il exploite nos sceaux faibles et peut nous piéger avec Rhun. Sa couverture contre nos engagements avec Rhun a souvent été Vael, donc favorable à Rhun. Ne pas surinterpréter les retraits : ils rendent l’engagement Rhun rentable sans révéler le sceau adverse.
```

### Série 6 — écart 0.0089 — 1 entrée(s), 1830 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Épreuve des Trois Sceaux — série de 150 : le bilan cumulé est -12 (l’ancienne note -17 était fausse ; le total annoncé ici est -12). Ce qui rapporte : engager avec Rhun comme Ouvrant (+1 si l’adversaire se retire, +2 si sa couverture est Vael) ; répondre à une retenue adverse en engageant avec Rhun (souvent retrait adverse, parfois couverture Vael) ; couvrir un engagement adverse avec Rhun quand Tor adverse est plausible (+2 observés) ; avec Vael, engager après retenue adverse peut rapporter +1 si l’adversaire se retire, mais la couverture adverse avec Rhun coûte -2. Les retenues mutuelles avec Vael contre Tor rapportent +1. Ce qui coûte : retenir avec Tor (souvent Vael en face, -1) ; répondre à un engagement avec Tor ou Vael en se retirant (-1, mais préférable à une couverture spéculative) ; couvrir avec Vael si Rhun adverse est plausible (-2) ; engager avec Vael quand une couverture est plausible ; les retenues mutuelles avec Tor contre Vael (-1). Politique : engager avec Rhun dès que possible ; répondre à un engagement par couverture avec Rhun si Tor adverse est plausible, sinon se retirer ; avec Vael, couvrir seulement contre Tor assez probable, sinon se retirer ; avec Tor, se retirer par défaut et éviter d’engager ou de retenir inutilement. Adversaire : répond très souvent à nos engagements d’Ouvrant par un retrait, mais peut couvrir — notamment nos engagements avec Rhun, souvent avec Vael, ce qui nous est favorable ; il couvre fréquemment nos engagements de Répondant, surtout avec Rhun/Vael en main, parfois avec le sceau qui nous bat (Rhun contre Vael), suggérant qu’il exploite nos sceaux faibles et peut piéger un engagement Vael. Après nos retenues, il engage souvent. Les retraits ne révèlent pas son sceau et ne doivent pas être surinterprétés : ils rendent surtout l’engagement Rhun rentable.
```

### Série 7 — écart 0.0127 — 1 entrée(s), 1332 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Épreuve des Trois Sceaux — série de 150 : le bilan fourni est -3 jetons. Rhun est le meilleur sceau offensif : Ouvrant, engager rapporte souvent +1 (retrait adverse) et +2 si la couverture adverse est Vael ; Répondant après retenue adverse, engager rapporte +1 ou +2 contre Vael ; après engagement adverse, couvrir avec Rhun rapporte +2 contre Tor. Vael peut retenir contre Tor (+1 en retenue mutuelle) et engager après retenue adverse (+1 si retrait), mais son engagement est risqué (Rhun le bat) et sa couverture contre Rhun coûte -2. Tor est très défavorable : éviter engager/retenir inutilement ; après engagement adverse, se retirer par défaut (-1), plutôt que couvrir spéculativement. Répondre à un engagement par couverture avec Rhun si Tor adverse est plausible, sinon se retirer ; avec Vael, couvrir seulement contre Tor assez probable. Adversaire : répond très souvent à nos engagements d’Ouvrant par un retrait, mais couvre parfois — notamment Rhun avec Vael, ce qui nous est favorable ; il couvre fréquemment nos engagements de Répondant, surtout avec Rhun/Vael en main, et peut exploiter nos sceaux faibles avec le sceau gagnant (Rhun contre Vael). Après nos retenues, il engage souvent. Les retraits ne révèlent pas son sceau et ne doivent pas être surinterprétés : ils rendent surtout l’engagement avec Rhun rentable.
```

### Série 8 — écart 0.0292 — 1 entrée(s), 1461 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Épreuve des Trois Sceaux — série de 150 : bilan réel -28 jetons (l’ancienne note à -3 était fausse). Rentable : engager avec Rhun comme Ouvrant ou Répondant après retenue adverse donne presque toujours +1 (retrait adverse) ; couvrir avec Rhun après engagement adverse rapporte +2 contre Tor. Les retenues mutuelles avec Vael contre Tor rapportent +1. Vael/Tor peuvent obtenir +1 en engageant si l’adversaire se retire, mais c’est risqué.

Pertes : engager avec Vael ou Tor comme Ouvrant est souvent couvert par Rhun (-2) ; répondre par couverture avec Vael perd généralement contre Rhun (-2), et avec Tor perd contre Vael/Rhun (-2). Se retirer après engagement adverse coûte -1 et reste préférable à une couverture spéculative avec Tor ; avec Vael, couvrir seulement si Tor adverse est assez probable. Retenir davantage avec Vael/Tor plutôt que les engager automatiquement.

Adversaire : contre nos engagements d’Ouvrant, il répond très souvent par un retrait, mais couvre régulièrement Vael et certains Tor ; il ne semble pas couvrir Rhun. Comme Ouvrant, il engage fréquemment. Contre nos engagements de Répondant, il couvre souvent, notamment quand nous avons Vael (Rhun adverse), exploitant nos sceaux faibles. Les retraits ne révèlent pas son sceau : les traiter surtout comme occasion de prendre +1 avec Rhun. Priorité : engager avec Rhun ; répondre à un engagement par retrait par défaut, couvrir seulement avec un avantage de sceau suffisamment probable.
```

### Série 9 — écart 0.0148 — 1 entrée(s), 1561 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Épreuve des Trois Sceaux — série de 150 : bilan réel 0 jeton (l’ancienne note à -28 était fausse). Rentable : engager avec Rhun comme Ouvrant ou Répondant après retenue adverse donne +1 si l’adversaire se retire, et peut donner +2 s’il couvre avec Vael ; couvrir avec Rhun après engagement adverse rapporte +2 contre Tor. Les retenues mutuelles avec Vael contre Tor rapportent +1. Vael/Tor peuvent obtenir +1 en engageant si l’adversaire se retire, mais c’est risqué.

Pertes : engager avec Vael ou Tor comme Ouvrant est souvent couvert par Rhun (-2) ; répondre par couverture avec Vael perd généralement contre Rhun (-2), et avec Tor perd contre Vael/Rhun (-2). Se retirer après engagement adverse coûte -1 et reste préférable à une couverture spéculative avec Tor ; avec Vael, couvrir seulement si Tor adverse est assez probable. Retenir davantage avec Vael/Tor plutôt que les engager automatiquement.

Adversaire : contre nos engagements d’Ouvrant, il répond très souvent par un retrait, mais couvre régulièrement Vael et certains Tor ; il ne semble pas couvrir Rhun. Comme Ouvrant, il engage fréquemment, ce qui nous coûte surtout quand nous avons Tor/Vael et nous retirons. Contre nos engagements de Répondant, il couvre souvent, notamment quand nous avons Vael (Rhun adverse), exploitant nos sceaux faibles. Les retraits ne révèlent pas son sceau : les traiter surtout comme occasion de prendre +1 avec Rhun. Priorité : engager avec Rhun ; répondre à un engagement par retrait par défaut, couvrir seulement avec un avantage de sceau suffisamment probable.
```


## AE-gto-r2

### Série 0 — écart 0.1802 — 1 entrée(s), 1110 caractères

*Événements : ajout. Écritures bloquées pendant la série : 0.*

```
Dans la série des 150 épreuves, stratégie à privilégier contre cet adversaire : Ouvrant avec Rhun, engager (très rentable : les couvertures adverses avec Vael perdent et les retraits rapportent) ; avec Tor ou Vael, éviter d'engager, plutôt retenir. Répondant après une retenue adverse, engager systématiquement : l'adversaire se retire presque toujours, et couvre lorsqu'il a Rhun ; avec Rhun, couvrir est gagnant. Répondant après un engagement adverse : avec Tor ou Vael, se retirer plutôt que couvrir (ses couvertures observées étaient presque toujours avec Rhun et faisaient -2) ; avec Rhun, couvrir, car ses couvertures observées avec Tor perdent -2 pour lui. Motif adverse observé : il ne couvre jamais avec Tor ; il couvre avec Rhun contre nos sceaux inférieurs et avec Vael contre Rhun. Ses engagements comme Ouvrant semblaient venir surtout de Rhun (et parfois Tor), jamais Vael dans les dévoilements ; ses retenues sont exploitables par un engagement en réponse. Bilan de cette série : -27, dû surtout aux engagements avec Tor/Vael et aux couvertures (ou décisions d'escalade) avec un sceau inférieur.
```

### Série 1 — écart 0.0000 — 1 entrée(s), 762 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150, bilan +3) : Ouvrant, engager avec Rhun ; avec Tor ou Vael, retenir. Répondant après retenue adverse, engager avec Rhun/Vael (retraits fréquents ; ses couvertures avec Rhun contre Vael perdent pour lui). Répondant après engagement adverse, se retirer avec Tor/Vael ; couvrir avec Rhun (ses couvertures avec Tor perdent pour lui). Il couvre après nos engagements, surtout avec Vael contre Tor (nous coûte -2) ; avec Vael contre Rhun ou Tor contre Rhun, ses couvertures nous rapportent +2. Il n'a jamais couvert avec Tor contre nos sceaux inférieurs dans cette série. Ses engagements comme Ouvrant semblaient surtout avec Rhun/Tor, jamais Vael dans les dévoilements ; ses retenues sont exploitables par un engagement en réponse.
```

### Série 2 — écart 0.0492 — 1 entrée(s), 839 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150, bilan -7) : gains surtout en engageant avec Rhun (comme Ouvrant, l'adversaire se retire souvent ; comme Répondant après sa retenue, il couvre fréquemment avec Vael et perd, donnant +2). Avec Tor, retenir face à un engagement adverse puis se retirer est préférable à couvrir. Pertes majeures : retenir avec Tor contre Vael en dévoilement (+ les retenues avec Tor contre Vael), et surtout couvrir avec Tor contre Rhun ou Vael contre Rhun après ses engagements (-2). L'adversaire engage très souvent après nos retenues ; après nos engagements, il se retire généralement. Ses couvertures après nos engagements de Répondant sont répétées avec Vael contre notre Rhun et nous rapportent +2 ; ses couvertures après nos retenues exploitent nos mauvais couvrements. Ne pas surinterpréter les sceaux non dévoilés.
```

### Série 3 — écart 0.0265 — 2 entrée(s), 1681 caractères

*Événements : ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150, bilan -7) : gains surtout en engageant avec Rhun (comme Ouvrant, l'adversaire se retire souvent ; comme Répondant après sa retenue, il couvre fréquemment avec Vael et perd, donnant +2). Avec Tor, retenir face à un engagement adverse puis se retirer est préférable à couvrir. Pertes majeures : retenir avec Tor contre Vael en dévoilement (+ les retenues avec Tor contre Vael), et surtout couvrir avec Tor contre Rhun ou Vael contre Rhun après ses engagements (-2). L'adversaire engage très souvent après nos retenues ; après nos engagements, il se retire généralement. Ses couvertures après nos engagements de Répondant sont répétées avec Vael contre notre Rhun et nous rapportent +2 ; ses couvertures après nos retenues exploitent nos mauvais couvrements. Ne pas surinterpréter les sceaux non dévoilés.
§
Contre cet adversaire (série de 150, bilan +1) : gains surtout en engageant avec Rhun (comme Ouvrant, l'adversaire se retire souvent ; comme Répondant après sa retenue, il couvre fréquemment avec Vael et perd, donnant +2). Avec Tor, retenir face à un engagement adverse puis se retirer est préférable à couvrir. Pertes majeures : retenir avec Tor contre Vael en dévoilement (+ les retenues avec Tor contre Vael), et surtout couvrir avec Tor contre Rhun ou Vael contre Rhun après ses engagements (-2). L'adversaire engage très souvent après nos retenues ; après nos engagements, il se retire généralement. Ses couvertures après nos engagements de Répondant sont répétées avec Vael contre notre Rhun et nous rapportent +2 ; ses couvertures après nos retenues exploitent nos mauvais couvrements. Ne pas surinterpréter les sceaux non dévoilés.
```

### Série 4 — écart 0.0229 — 2 entrée(s), 1902 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150, bilan +17) : engager avec Rhun est la meilleure ligne, comme Ouvrant (l'adversaire se retire le plus souvent ; lorsqu'il couvre, Rhun gagne systématiquement les dévoilements observés, +2) et comme Répondant après sa retenue (retraits adverses à +1, couvertures avec Vael à +2). Après un engagement adverse, se retirer est la ligne sûre (-1), sauf couvrir avec Rhun : les trois couvertures observées contre Tor ont rapporté +2. Éviter de couvrir avec Tor ou Vael : Tor a perdu chaque couverture observée contre Vael (-2), Vael chaque couverture observée contre Rhun (-2). Comme Ouvrant, retenir est mauvais : l'adversaire engage alors souvent et Tor perd aussi presque toujours les dévoilements quand il retient face à Vael. L'adversaire couvre assez souvent nos engagements (surtout contre Tor/Vael) mais se retire généralement face à Rhun ; après ses retenues, il couvre parfois contre nos sceaux faibles. Priorité : engager avec Rhun ; répondre à sa retenue par engagement ; ne pas surinterpréter les sceaux non dévoilés.
§
Contre cet adversaire (série de 150, bilan +1) : gains surtout en engageant avec Rhun (comme Ouvrant, l'adversaire se retire souvent ; comme Répondant après sa retenue, il couvre fréquemment avec Vael et perd, donnant +2). Avec Tor, retenir face à un engagement adverse puis se retirer est préférable à couvrir. Pertes majeures : retenir avec Tor contre Vael en dévoilement (+ les retenues avec Tor contre Vael), et surtout couvrir avec Tor contre Rhun ou Vael contre Rhun après ses engagements (-2). L'adversaire engage très souvent après nos retenues ; après nos engagements, il se retire généralement. Ses couvertures après nos engagements de Répondant sont répétées avec Vael contre notre Rhun et nous rapportent +2 ; ses couvertures après nos retenues exploitent nos mauvais couvrements. Ne pas surinterpréter les sceaux non dévoilés.
```

### Série 5 — écart 0.0278 — 1 entrée(s), 1224 caractères

*Événements : suppression, suppression, ajout, elagage. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (nouvelle série de 150, bilan +13 ; à combiner avec les observations antérieures) : comme Ouvrant, engager reste la meilleure ligne, surtout avec Rhun. L'adversaire se retire souvent face à nos engagements ; lorsqu'il couvre, Rhun gagne les dévoilements observés contre Vael (+2), tandis que Tor et Vael perdent fréquemment contre ses couvertures (-2, surtout contre Rhun, et Tor aussi contre Vael). Comme Répondant après son engagement, se retirer est la ligne sûre (-1) ; couvrir avec Rhun contre Tor a systématiquement rapporté +2 dans les cas observés. Éviter de couvrir avec Tor ou Vael : les couvertures défensives de ces sceaux sont mauvaises ou non rentables dans les séries observées. Après sa retenue, engager rapporte souvent +1 quand il se retire ; avec Rhun, ses couvertures répétées avec Vael donnent +2. Prudence avec Tor après sa retenue : Vael l'a couvert à plusieurs reprises et lui a fait perdre -2. L'adversaire engage très souvent après nos retenues, se retire souvent après nos engagements, et couvre surtout quand notre sceau est Tor/Vael ; il couvre parfois nos engagements de Répondant avec Vael contre Rhun, ce qui nous favorise. Ne pas surinterpréter les sceaux non dévoilés.
```

### Série 6 — écart 0.0278 — 1 entrée(s), 1149 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150, solde -17) : comme Ouvrant, engager reste obligatoire dans les observations mais est très exploitable par l'adversaire : il couvre très souvent nos engagements avec Vael et Tor, surtout quand notre sceau est Vael/Tor, ce qui nous coûte -2 presque à chaque fois. Avec Rhun, engager reste excellent : l'adversaire se retire presque toujours, et ses rares couvertures avec Vael nous donnent +2. Comme Répondant après son engagement, se retirer est la ligne sûre mais rapporte -1 ; couvrir avec Rhun est très rentable contre Tor (observé à plusieurs reprises, +2). Éviter de couvrir avec Tor/Vael : Tor perd notamment -2 quand l'adversaire couvre avec Vael, et Vael a surtout dû se retirer (-1). Après sa retenue, engager rapporte +1 quand il se retire ; avec Rhun, accepter sa couverture avec Vael rapporte +2. L'adversaire engage très souvent après nos retenues, se retire très souvent après nos engagements avec Rhun, et couvre de façon prévisible nos engagements avec Vael/Tor ; il couvre aussi nos engagements défensifs avec Vael contre Rhun, ce qui nous favorise. Ne pas surinterpréter les sceaux non dévoilés.
```

### Série 7 — écart 0.0000 — 1 entrée(s), 1122 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (bilan fourni : 150 épreuves, solde cumulé -3) : comme Ouvrant, engager avec Rhun est la meilleure ligne observée : l'adversaire se retire presque toujours (+1), et ses couvertures avec Vael donnent +2. Engager avec Tor/Vael n'est pas recommandé ; retenir puis couvrir son engagement avec Vael est très mauvais, car il couvre régulièrement avec Rhun (-2). Comme Répondant après son engagement, se retirer est sûr mais coûte -1 ; couvrir avec Rhun est excellent contre son Tor (+2, observé à plusieurs reprises). Éviter de couvrir avec Tor ou Vael : Tor perd contre ses couvertures Vael (-2), et Vael perd contre ses couvertures Rhun (-2). Après sa retenue, engager rapporte généralement +1 quand il se retire ; avec Rhun, ses couvertures avec Vael rapportent +2. L'adversaire engage souvent après nos retenues, se retire très souvent après nos engagements avec Rhun, et couvre de façon prévisible nos engagements défensifs avec Tor/Vael (Vael contre Tor, Rhun contre Vael) ; il couvre aussi nos engagements avec Rhun de manière perdante. Les sceaux non dévoilés ne permettent pas d'inférer davantage.
```

### Série 8 — écart 0.0245 — 1 entrée(s), 1265 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150 épreuves, solde réel +16) : comme Ouvrant, engager avec Rhun est la meilleure ligne observée : il se retire presque toujours (+1), et ses couvertures avec Vael donnent +2. Engager avec Tor/Vael est déconseillé ; après notre retenue, il engage souvent, et couvrir avec Tor ou Vael est généralement perdant. Comme Répondant après son engagement, se retirer avec Tor ou Vael coûte -1 ; couvrir avec Rhun est excellent contre son Tor (+2), et couvrir avec Vael peut gagner contre son Tor (+2), mais couvrir avec Tor est très mauvais (il a montré Rhun ou Vael, -2). Après sa retenue, engager avec Rhun est profitable : il se retire souvent (+1) et couvre parfois avec Vael (+2). Éviter d'engager avec Tor après sa retenue (il couvre régulièrement avec Vael, -2) et avec Vael (il couvre avec Rhun, -2). En retenue contre retenue, Vael bat souvent son Tor (+1), tandis que Tor perd souvent contre son Vael (-1). L'adversaire engage fréquemment après nos retenues, se retire très souvent après nos engagements avec Rhun, et couvre de manière prévisible nos engagements avec Tor/Vael (respectivement Vael/Rhun) ; il couvre aussi nos engagements avec Rhun de manière perdante. Les sceaux non dévoilés ne permettent pas d'inférer davantage.
```

### Série 9 — écart 0.0000 — 1 entrée(s), 1044 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (150 épreuves, solde réel +17) : Ouvrant, engager avec Rhun est la meilleure ligne : il se retire très souvent (+1), et couvre parfois avec Vael, ce qui rapporte +2. Après sa retenue, engager avec Rhun reste profitable (+1 ou +2). Éviter d'engager avec Tor ou Vael après sa retenue : il couvre prévisiblement avec Vael contre Tor et Rhun contre Vael, généralement -2. Après son engagement, avec Rhun couvrir est excellent contre son Tor (+2) ; avec Vael, couvrir gagne contre Tor (+2) mais perd lourdement contre Rhun (-2), donc rester prudent ; avec Tor, se retirer (-1) est préférable. En retenue contre retenue, Vael bat souvent son Tor (+1), tandis que Tor perd souvent contre son Vael (-1). Il engage fréquemment après nos retenues, se retire très souvent après nos engagements avec Rhun, et couvre régulièrement nos engagements avec Tor/Vael (Vael/Rhun). Il couvre aussi parfois nos engagements avec Rhun, mais avec Vael et donc à notre désavantage. Les sceaux non dévoilés n’apportent pas d’information exploitable.
```


## AE-gto-r3

### Série 0 — écart 0.1221 — 1 entrée(s), 1359 caractères

*Événements : ajout. Écritures bloquées pendant la série : 0.*

```
Dans « L'Épreuve des Trois Sceaux », règle structurelle : Tor perd toujours en dévoilement (Rhun et Vael le battent), Rhun gagne toujours, Vael est 50/50 face au sceau restant. Priorité : avec Rhun, accepter/chercher le dévoilement ; avec Tor, éviter toute couverture et éviter le dévoilement ; avec Vael, dévoilement acceptable mais pas garanti. Adversaire observé : très sélectif, il couvre fréquemment quand il révèle Rhun contre Tor/Vael, tandis qu'il se retire souvent lorsque notre Rhun est engagé ; cela suggère une prudence/agression dépendant du sceau, avec sélection des révélations plutôt qu'un adversaire uniformément téméraire. Il a toutefois parfois couvert avec Vael contre notre Rhun (nous gagnions +2), donc ses couvertures ne sont pas infaillibles. Notre série (-28) a surtout été pénalisée par des couvertures avec Tor ou Vael contre Rhun et quelques couvertures avec Tor contre Vael ; les retraits après nos engagements, les couvertures gagnantes avec Rhun, et les retenues gagnantes avec Rhun/Vael ont rapporté. À l'avenir : ne pas couvrir avec Tor ; couvrir avec Rhun ; avec Tor se retirer face à un engagement adverse ; avec Rhun couvrir une ouverture adverse ou engager ; avec Vael privilégier la prudence, engager si l'adversaire a retenu et se retirer plutôt que couvrir si l'adversaire engage, sauf indice exploitable sur son sceau.
```

### Série 1 — écart 0.0022 — 1 entrée(s), 1389 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Dans « L'Épreuve des Trois Sceaux » (bilan de 150 épreuves, solde -7), Rhun bat toujours Vael, Vael bat Tor ; avec Rhun, engager puis couvrir reste très rentable (+2 si l'adversaire couvre), et couvrir un engagement adverse est sûr contre Tor (+2). Avec Tor, les dévoilements sont systématiquement mauvais contre Vael : ne pas couvrir ; retenir contre un engagement adverse coûte -1, et engager ne rapporte que si l'adversaire se retire (+1) mais coûte -2 s'il couvre. Avec Vael, retenir face à une retenue adverse gagne contre Tor (+1), mais couvrir un engagement adverse est mauvais contre Rhun (-2) ; préférer se retirer, et engager face à une retenue peut obtenir +1 si l'adversaire se retire.

Adversaire : il exploite souvent nos retenues faibles (Tor/Vael) en engageant ; quand il engage, il semble sélectionner la couverture selon son sceau : couvertures gagnantes avec Vael contre notre Tor et avec Rhun contre notre Vael. Il se retire fréquemment face à nos engagements de Rhun, mais couvre parfois avec Vael et nous donne alors +2 ; nos engagements de Rhun ont donc la meilleure valeur. Il est prudent/sélectif plutôt qu'uniformément téméraire. Ligne pratique : avec Rhun, engager/couvrir ; avec Tor, éviter les couvertures et éviter d'engager si l'adversaire semble couvrir ; avec Vael, retenir face à l'ouverture retenue, et se retirer plutôt que couvrir face à un engagement.
```

### Série 2 — écart 0.0108 — 1 entrée(s), 1635 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Dans « L'Épreuve des Trois Sceaux » (bilan de 150 épreuves, solde réel +6), Rhun est notre sceau le plus rentable : engager rapporte presque toujours +1 quand l'adversaire se retire, et +2 contre une couverture adverse avec Vael ; couvrir un engagement est excellent contre Tor (+2). Vael rapporte surtout en retenant contre une retenue adverse avec Tor (+1), ou en engageant si l'adversaire se retire (+1), mais coûte -1 si l'adversaire engage et que l'on se retire, et -2 si l'on engage face à sa couverture avec Rhun. Tor est globalement perdant : retenir face à un engagement coûte -1, retenir face à une retenue perd contre Vael (-1), et engager face à une couverture de Vael coûte -2. Éviter les couvertures non favorables.

Adversaire : il exploite souvent nos retenues, surtout avec un engagement (nos Tor/Vael ont ainsi subi beaucoup de -1). Quand nous engageons, il se retire fréquemment — surtout face à Rhun — mais ses couvertures sont sélectives et cohérentes avec son sceau : il couvre notre Vael avec Rhun et notre Rhun avec Vael, ce qui nous a coûté -2 avec Vael et lui a coûté -2 quand Rhun nous a permis de gagner ; Vael peut aussi couvrir Tor. Il couvre également souvent notre engagement de Rhun quand il est Répondant avec Vael, nous donnant +2, mais alterne avec le retrait. Ligne pratique : avec Rhun, engager en priorité et couvrir contre un engagement (notamment si l'adversaire est Tor) ; avec Vael, retenir face à une retenue, engager seulement en acceptant le risque de couverture et éviter de couvrir un engagement ; avec Tor, limiter les engagements/couvertures et attendre plutôt que révéler face à Vael.
```

### Série 3 — écart 0.0432 — 1 entrée(s), 680 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire : il exploite souvent nos retenues par un engagement, surtout dans la seconde moitié, nous forçant à perdre -1 quand nous nous retirons. Quand nous engageons, il se retire fréquemment — surtout face à Rhun — mais couvre sélectivement : il couvre notre Vael avec Rhun (ce qui nous coûte -2) et couvre aussi notre Rhun avec Vael, couverture alors exploitable car Rhun nous donne +2. Ligne pratique : avec Rhun, engager en priorité et couvrir un engagement si les indices sont favorables ; avec Vael, engager seulement en acceptant le risque de Rhun adverse, retenir face à une retenue ; avec Tor, limiter les engagements/couvertures et éviter les révélations contre Vael.
```

### Série 4 — écart 0.0685 — 1 entrée(s), 1105 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire (série de 150) : il exploite nos retenues par un engagement, surtout en seconde moitié, et nous fait souvent perdre -1 quand nous nous retirons. Quand nous engageons, il se retire très fréquemment, surtout face à Rhun, donc nos engagements avec Rhun puis Vael rapportent beaucoup de +1 sans révélation. Ses couvertures sont sélectives et parfois lisibles : il couvre souvent notre Vael avec Rhun (nous coûte -2) et couvre aussi notre Rhun avec Vael (ce qui nous rapporte +2) ; contre Tor, il couvre surtout avec Rhun et nous perdons -2. Ligne pratique : avec Rhun, engager en priorité, couvrir un engagement si les indices sont favorables ; avec Vael, engager seulement en acceptant le risque de Rhun adverse, retenir face à une retenue ; avec Tor, éviter les engagements/couvertures et les révélations contre Vael/Rhun, retenir face à une retenue ; après une retenue adverse, préférer souvent retenir avec Tor/Vael plutôt que s'exposer à -2. Les révélations favorables (+2) sont très rentables, mais les couvertures perdantes et les retraits après engagement ont dominé : la série finit à -12.
```

### Série 5 — écart 0.0639 — 1 entrée(s), 1122 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire (série de 150, bilan final +15) : il exploite nos retenues par un engagement, surtout en seconde moitié, et nous fait souvent perdre -1 quand nous nous retirons. Quand nous engageons, il se retire très fréquemment, surtout face à Rhun, donc nos engagements avec Rhun puis Vael rapportent beaucoup de +1 sans révélation. Ses couvertures sont sélectives et parfois lisibles : il couvre souvent notre Vael avec Rhun (nous coûte -2) et couvre aussi notre Rhun avec Vael (ce qui nous rapporte +2) ; contre Tor, il couvre surtout avec Rhun et nous perdons -2. Ligne pratique : avec Rhun, engager en priorité, couvrir un engagement si les indices sont favorables ; avec Vael, engager seulement en acceptant le risque de Rhun adverse, retenir face à une retenue ; avec Tor, éviter les engagements/couvertures et les révélations contre Vael/Rhun, retenir face à une retenue ; après une retenue adverse, préférer souvent retenir avec Tor/Vael plutôt que s'exposer à -2. Les révélations favorables (+2) sont très rentables, mais les couvertures perdantes et les retraits après engagement ont dominé ; la série finit à +15.
```

### Série 6 — écart 0.0294 — 1 entrée(s), 1227 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire (série de 150, bilan corrigé : -10) : nos gains viennent surtout des engagements avec Rhun qui font souvent se retirer l'adversaire (+1), puis des engagements de Rhun couverts par son Vael (+2) ; Vael rapporte +2 quand il couvre un engagement adverse et révèle Tor. Nos coûts majeurs sont les engagements de Vael couverts par son Rhun (-2), les couvertures avec Vael face à son Rhun (-2), les retraits après son engagement (-1), et les retenues avec Tor face à Vael (-1). Il répond souvent à nos engagements par un retrait, surtout face à Rhun, mais ses couvertures sont sélectives et exploitables : Rhun couvre fréquemment Vael, tandis que Vael couvre Rhun ; il engage aussi régulièrement après notre retenue, comptant sur notre retrait. Ligne pratique : engager prioritairement avec Rhun ; avec Vael, éviter l'engagement si une couverture adverse par Rhun est plausible et ne couvrir qu'avec de bons indices ; avec Tor, retenir prudemment, mais éviter de retenir automatiquement face à une retenue si Vael est probable ; après son engagement, ne pas se retirer automatiquement, surtout avec Rhun/Vael. Les gains de +2 sont très rentables, mais les pièges de couverture et les retraits ont produit le déficit final.
```

### Série 7 — écart 0.0945 — 1 entrée(s), 1219 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire (série de 150, solde réel -39) : les gains viennent surtout de nos engagements avec Rhun (l'adversaire se retire très souvent, +1), puis des engagements de Rhun couverts par son Vael (+2) et des couvertures gagnantes avec Vael contre Tor (+2). Les coûts majeurs sont nos couvertures trop fréquentes quand l'adversaire engage avec Rhun (notamment nous avec Vael ou Tor, -2), les couvertures avec Tor face à Vael (-2), les retenues face à Vael (-1), et les retraits après son engagement (-1). L'adversaire répond très souvent à nos retenues par un engagement, mais répond très souvent à nos engagements par un retrait ; il couvre de manière sélective, parfois même avec Vael face à notre Rhun, et ses engagements gagnants révèlent souvent Rhun. Ligne pratique : engager prioritairement avec Rhun ; avec Vael, ne couvrir qu'avec de bons indices et éviter de couvrir si Rhun adverse est plausible ; avec Tor, éviter la couverture sauf indice fort, et préférer le retrait face à un engagement menaçant ; après son engagement, ne pas couvrir automatiquement. Exploiter davantage ses retraits en engageant avec les sceaux forts, et retenir davantage avec un sceau faible plutôt que de payer une couverture perdante.
```

### Série 8 — écart 0.0256 — 1 entrée(s), 1357 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire — série de 150 (bilan fourni : +4). Gains : engager avec Rhun, que l'on soit Ouvrant ou Répondant ; ses retraits après nos engagements donnent +1, et ses couvertures avec Vael contre notre Rhun donnent +2. Nos couvertures avec Rhun contre Tor/Vael sont également gagnantes. Coûts : engager avec Vael ou Tor quand il couvre (il révèle alors presque toujours Rhun contre eux) : -2 ; couvrir avec Tor, notamment face à son Vael/Rhun, est très mauvais ; retenir avec Tor face à Vael coûte -1 ; se retirer après son engagement coûte -1. Profil adverse : il répond très souvent à nos engagements par un retrait, mais couvre sélectivement ; dans les couvertures observées après nos engagements, il n'a jamais révélé Tor, utilise souvent Rhun contre notre Vael/Tor, et parfois Vael contre notre Rhun. Quand il retient puis que nous engageons, il se retire souvent, mais ses couvertures observées révèlent systématiquement Vael. Ligne pratique : engager prioritairement avec Rhun ; avec Vael, engager seulement en acceptant le risque de sa couverture et éviter de couvrir si Rhun adverse est plausible ; avec Tor, préférer le retrait face à son engagement et ne couvrir qu'avec un indice très fort. Face à son retrait fréquent, exploiter les sceaux forts en engageant ; avec un sceau faible, retenir ou se retirer plutôt que payer une couverture perdante.
```

### Série 9 — écart 0.0103 — 1 entrée(s), 1551 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire — série de 150, solde cumulé -2. Gains : engager avec Rhun, Ouvrant ou Répondant ; ses retraits après nos engagements donnent +1 ; ses couvertures avec Vael contre notre Rhun donnent +2 ; nos couvertures avec Rhun contre Tor/Vael donnent +2 ; retenir face à son engagement puis le voir se retirer n'est pas possible (on doit se retirer/couvrir). Coûts : engager avec Vael ou Tor quand il couvre (il révèle alors presque toujours Rhun contre eux) : -2 ; couvrir avec Tor face à Vael, ou avec Vael face à Rhun, coûte -2 ; retenir avec Tor face à Vael coûte -1 ; se retirer après son engagement coûte -1. Profil : il répond très souvent à nos engagements par un retrait, mais couvre sélectivement ; dans les couvertures après nos engagements, il n'a jamais révélé Tor, utilise souvent Rhun contre notre Vael/Tor, et parfois Vael contre notre Rhun. Quand il retient puis que nous engageons, il se retire souvent ; ses couvertures observées dans cette situation révèlent systématiquement Vael. Ligne pratique : engager prioritairement avec Rhun ; avec Vael, engager seulement si l'on accepte le risque de Rhun adverse ; avec Tor, préférer retenir si Ouvrant, et après son engagement se retirer sauf indice très fort pour couvrir avec Rhun ; couvrir avec Rhun contre un engagement adverse est favorable quand Tor/Vael adverse est plausible ; éviter les couvertures perdantes avec Vael/Tor. Face à son retrait fréquent, exploiter les sceaux forts en engageant ; avec un sceau faible, retenir ou se retirer plutôt que payer une couverture perdante.
```


## AE-over-folder-r1

### Série 0 — écart 0.7757 — 1 entrée(s), 595 caractères

*Événements : ajout. Écritures bloquées pendant la série : 0.*

```
Contre l'adversaire de la série des 150 épreuves : il retient systématiquement quand il est Ouvrant et se retire systématiquement quand le Répondant engage (aucune couverture ni engagement observé). Donc engager rapporte +1 garanti, que je sois Ouvrant ou Répondant ; retenir mène au dévoilement et dépend des sceaux. Dans cette série, tous mes engagements ont rapporté +1 ; le solde cumulé final était +34. Priorité pour les prochaines épreuves contre lui : engager systématiquement plutôt que retenir ; ne pas supposer que ses sceaux sont prévisibles, les résultats de retenue sont aléatoires.
```

### Série 1 — écart 0.0000 — 1 entrée(s), 492 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150 épreuves) : il retient systématiquement quand il est Ouvrant, puis se retire systématiquement quand le Répondant engage ; aucune couverture ni engagement observé. Engager rapporte donc +1 garanti, que je sois Ouvrant ou Répondant ; retenir permettrait seulement un dévoilement incertain et n’a rien rapporté dans cette série. Tous mes engagements ont rapporté +1, sans coût ; solde final +150. Stratégie à privilégier : engager systématiquement contre lui.
```

### Série 2 — écart 0.0000 — 1 entrée(s), 350 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire : il retient systématiquement quand il est Ouvrant, puis se retire systématiquement quand le Répondant engage ; aucune couverture ni engagement observé. Engager rapporte donc +1 garanti, que je sois Ouvrant ou Répondant ; retenir n’a rien rapporté dans cette série. Stratégie à privilégier : engager systématiquement contre lui.
```

### Série 3 — écart 0.0000 — 1 entrée(s), 359 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire : il retient systématiquement quand il est Ouvrant, puis se retire systématiquement quand le Répondant engage ; aucune couverture ni prise d’initiative observée. Engager rapporte donc +1 garanti, que je sois Ouvrant ou Répondant ; retenir n’a pas été testé comme mon action. Stratégie à privilégier : engager systématiquement contre lui.
```

### Série 4 — écart 0.0000 — 1 entrée(s), 333 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, engager rapporte systématiquement +1 garanti, que je sois Ouvrant ou Répondant : il retient quand il est Ouvrant, puis se retire quand je l'engage comme Répondant. Il n'a jamais couvert ni pris l'initiative ; retenir de mon côté n'a pas été testé. Stratégie à privilégier : engager systématiquement contre lui.
```

### Série 5 — écart 0.0000 — 1 entrée(s), 393 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, engager rapporte systématiquement +1 garanti, que je sois Ouvrant ou Répondant : il retient quand il est Ouvrant, puis se retire quand je l'engage comme Répondant. Sur 150 épreuves, aucun coût, aucune couverture adverse ni initiative adverse observée. Stratégie à privilégier : engager systématiquement ; ne pas retenir ni couvrir (non testés/inutiles contre ce profil).
```

### Série 6 — écart 0.0000 — 1 entrée(s), 393 caractères

*Événements : aucun. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, engager rapporte systématiquement +1 garanti, que je sois Ouvrant ou Répondant : il retient quand il est Ouvrant, puis se retire quand je l'engage comme Répondant. Sur 150 épreuves, aucun coût, aucune couverture adverse ni initiative adverse observée. Stratégie à privilégier : engager systématiquement ; ne pas retenir ni couvrir (non testés/inutiles contre ce profil).
```

### Série 7 — écart 0.0000 — 1 entrée(s), 367 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, engager systématiquement rapporte +1 net, que je sois Ouvrant ou Répondant : il retient quand il est Ouvrant, puis se retire quand je l'engage comme Répondant. Sur 150 épreuves, aucun coût, aucune couverture adverse ni initiative adverse observée. Stratégie à privilégier : engager systématiquement ; ne pas retenir ni couvrir contre ce profil.
```

### Série 8 — écart 0.0000 — 1 entrée(s), 367 caractères

*Événements : aucun. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, engager systématiquement rapporte +1 net, que je sois Ouvrant ou Répondant : il retient quand il est Ouvrant, puis se retire quand je l'engage comme Répondant. Sur 150 épreuves, aucun coût, aucune couverture adverse ni initiative adverse observée. Stratégie à privilégier : engager systématiquement ; ne pas retenir ni couvrir contre ce profil.
```

### Série 9 — écart 0.0000 — 1 entrée(s), 377 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, il ouvre toujours en retenant et, face à mon engagement (que je sois Ouvrant ou Répondant), se retire systématiquement. Sur 150 épreuves : 150 engagements de ma part, aucun coût, aucune couverture ni initiative adverse observée, solde +150 (+1 par épreuve). Stratégie à privilégier : engager systématiquement ; ne pas retenir ni couvrir contre ce profil.
```


## AE-over-folder-r2

### Série 0 — écart 0.5821 — 1 entrée(s), 569 caractères

*Événements : ajout. Écritures bloquées pendant la série : 0.*

```
Dans la série « Trois Sceaux » (150 épreuves, +64), l'adversaire a toujours retenu en premier et, face à un engagement, s'est toujours retiré : jamais d'engagement ni de couverture observé. Engager est donc un gain garanti de +1 contre lui (69 fois observé), sans révéler les sceaux. Les 81 retenues suivies d'une retenue ont produit 38 gains et 43 pertes, soit -5 net ; retenir est donc moins rentable qu'engager contre ce profil. Priorité future : engager systématiquement, qu'Ouvrant ou Répondant, et éviter de retenir sauf changement manifeste de stratégie adverse.
```

### Série 1 — écart 0.0000 — 1 entrée(s), 462 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Dans la série « Trois Sceaux » (150 épreuves, +150), l'adversaire n'a jamais couvert ni engagé : quand il était Ouvrant, il a toujours retenu ; quand il était Répondant, il s'est toujours retiré face à notre engagement (75 cas de chaque). Nos 150 engagements ont donc tous rapporté +1, sans coût ni révélation des sceaux. Stratégie à reconduire contre lui : engager systématiquement, Ouvrant comme Répondant ; ne pas retenir ni couvrir sauf changement manifeste.
```

### Série 2 — écart 0.0000 — 1 entrée(s), 419 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Dans la série « Trois Sceaux » (150 épreuves, +150), l'adversaire n'a jamais couvert ni engagé : Ouvrant, il a toujours retenu ; Répondant, il s'est toujours retiré face à notre engagement (75 cas de chaque). Nos 150 engagements ont donc tous rapporté +1, sans coût ni révélation des sceaux. Stratégie contre lui : engager systématiquement, Ouvrant comme Répondant ; ne pas retenir ni couvrir sauf changement manifeste.
```

### Série 3 — écart 0.0000 — 1 entrée(s), 419 caractères

*Événements : aucun. Écritures bloquées pendant la série : 0.*

```
Dans la série « Trois Sceaux » (150 épreuves, +150), l'adversaire n'a jamais couvert ni engagé : Ouvrant, il a toujours retenu ; Répondant, il s'est toujours retiré face à notre engagement (75 cas de chaque). Nos 150 engagements ont donc tous rapporté +1, sans coût ni révélation des sceaux. Stratégie contre lui : engager systématiquement, Ouvrant comme Répondant ; ne pas retenir ni couvrir sauf changement manifeste.
```

### Série 4 — écart 0.0000 — 1 entrée(s), 419 caractères

*Événements : aucun. Écritures bloquées pendant la série : 0.*

```
Dans la série « Trois Sceaux » (150 épreuves, +150), l'adversaire n'a jamais couvert ni engagé : Ouvrant, il a toujours retenu ; Répondant, il s'est toujours retiré face à notre engagement (75 cas de chaque). Nos 150 engagements ont donc tous rapporté +1, sans coût ni révélation des sceaux. Stratégie contre lui : engager systématiquement, Ouvrant comme Répondant ; ne pas retenir ni couvrir sauf changement manifeste.
```

### Série 5 — écart 0.0000 — 1 entrée(s), 387 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Dans « Trois Sceaux », contre cet adversaire (150 épreuves), il n'a jamais couvert ni engagé : Ouvrant, il a toujours retenu ; Répondant, il s'est toujours retiré face à notre engagement. Nos 150 engagements ont donc tous rapporté +1, sans coût ni révélation des sceaux. Stratégie : engager systématiquement, Ouvrant comme Répondant ; ne pas retenir ni couvrir sauf changement manifeste.
```

### Série 6 — écart 0.0000 — 1 entrée(s), 402 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Dans « Trois Sceaux », après 150 épreuves contre cet adversaire : il n'a jamais engagé ni couvert. Ouvrant, il a toujours retenu ; Répondant, il s'est toujours retiré face à notre engagement. Nos 150 engagements ont donc tous rapporté +1, sans coût ni révélation des sceaux. Stratégie contre lui : engager systématiquement, Ouvrant comme Répondant ; ne pas retenir ni couvrir sauf changement manifeste.
```

### Série 7 — écart 0.0000 — 1 entrée(s), 402 caractères

*Événements : aucun. Écritures bloquées pendant la série : 0.*

```
Dans « Trois Sceaux », après 150 épreuves contre cet adversaire : il n'a jamais engagé ni couvert. Ouvrant, il a toujours retenu ; Répondant, il s'est toujours retiré face à notre engagement. Nos 150 engagements ont donc tous rapporté +1, sans coût ni révélation des sceaux. Stratégie contre lui : engager systématiquement, Ouvrant comme Répondant ; ne pas retenir ni couvrir sauf changement manifeste.
```

### Série 8 — écart 0.0000 — 1 entrée(s), 402 caractères

*Événements : aucun. Écritures bloquées pendant la série : 0.*

```
Dans « Trois Sceaux », après 150 épreuves contre cet adversaire : il n'a jamais engagé ni couvert. Ouvrant, il a toujours retenu ; Répondant, il s'est toujours retiré face à notre engagement. Nos 150 engagements ont donc tous rapporté +1, sans coût ni révélation des sceaux. Stratégie contre lui : engager systématiquement, Ouvrant comme Répondant ; ne pas retenir ni couvrir sauf changement manifeste.
```

### Série 9 — écart 0.0000 — 1 entrée(s), 395 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Dans « Trois Sceaux », contre cet adversaire (bilan de 150 épreuves), il n'a jamais engagé ni couvert. Ouvrant, il a toujours retenu ; Répondant, il s'est toujours retiré face à notre engagement. Nos 150 engagements ont donc tous rapporté +1, sans coût ni révélation des sceaux. Stratégie : engager systématiquement, Ouvrant comme Répondant ; ne pas retenir ni couvrir sauf changement manifeste.
```


## AE-over-folder-r3

### Série 0 — écart 0.8032 — 1 entrée(s), 685 caractères

*Événements : ajout. Écritures bloquées pendant la série : 0.*

```
Dans la série des Trois Sceaux (150 manches), l'adversaire a joué une stratégie entièrement passive : il a toujours retenu quand il ouvrait, a toujours retenu face à ma retenue, et s'est toujours retiré face à mon engagement ; aucune couverture ni aucun engagement adverse observé. Mes engagements ont rapporté +1 garanti à chaque fois (51 fois). Les 99 retenues réciproques ont produit 36 victoires (+1) et 63 défaites (-1), soit -27 ; bilan total +24. Contre cet adversaire, engager systématiquement dès que possible domine retenir, quel que soit mon sceau ; ne pas chercher à couvrir, car il ne répond pas par couverture. Rester attentif à un éventuel changement futur de stratégie.
```

### Série 1 — écart 0.0000 — 1 entrée(s), 589 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Dans la série des Trois Sceaux (150 manches), l'adversaire a toujours retenu quand il ouvrait, puis s'est toujours retiré après chacun de mes engagements comme Répondant ; quand j'ouvrais, mes engagements ont aussi toujours provoqué son retrait. Aucun échange de couverture ni sceau adverse dévoilé. Mes 150 engagements ont tous rapporté +1 garanti, sans aucun coût : bilan +150. Contre lui, engager systématiquement dès que possible domine retenir, quel que soit mon sceau ; ne pas couvrir, car il ne répond pas par couverture. Rester attentif à un éventuel changement futur de stratégie.
```

### Série 2 — écart 0.0000 — 1 entrée(s), 590 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, sur 150 manches : il a toujours retenu quand il était Ouvrant, puis s'est toujours retiré après chacun de mes engagements quand il était Répondant. Quand j'étais Ouvrant, il s'est aussi toujours retiré après mon engagement. Aucun échange de couverture, aucun sceau adverse dévoilé. Mes 150 engagements ont rapporté +1 garanti chacun, sans perte observée : bilan +150. Stratégie à reconduire : engager systématiquement dès que possible, quel que soit mon sceau, et ne pas couvrir ; retenir ne rapporte rien ici. Rester attentif à tout changement futur de comportement.
```

### Série 3 — écart 0.0000 — 1 entrée(s), 674 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, sur 150 manches : il a toujours retenu comme Ouvrant, puis s'est toujours retiré après chacun de mes engagements comme Répondant. Quand j'étais Ouvrant, il s'est aussi toujours retiré après mon engagement. Aucun échange de couverture ; un seul sceau adverse dévoilé (Tor) lors de la manche où nous avons tous deux retenu. Mes 149 engagements ont tous rapporté +1 garanti, et l'unique retenue mutuelle a aussi rapporté +1 : bilan +150, aucune perte. Stratégie à reconduire : engager systématiquement dès que possible, quel que soit mon sceau, et ne pas couvrir ; retenir ne rapporte pas davantage ici. Surveiller un éventuel changement de comportement.
```

### Série 4 — écart 0.0000 — 1 entrée(s), 607 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, sur les 150 épreuves du dernier bilan, il a toujours retenu comme Ouvrant puis s'est retiré après chacun de mes engagements comme Répondant. Quand j'étais Ouvrant, il s'est aussi toujours retiré après mon engagement. Aucun sceau adverse n'a été dévoilé et aucun échange de couverture n'a eu lieu. Mes 150 engagements ont tous rapporté +1 garanti, sans aucune perte. Stratégie à reconduire : engager systématiquement dès que possible, quel que soit mon sceau, et ne pas couvrir ; retenir ne rapportait rien dans cette série. Surveiller seulement un éventuel changement de comportement.
```

### Série 5 — écart 0.0000 — 1 entrée(s), 607 caractères

*Événements : aucun. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, sur les 150 épreuves du dernier bilan, il a toujours retenu comme Ouvrant puis s'est retiré après chacun de mes engagements comme Répondant. Quand j'étais Ouvrant, il s'est aussi toujours retiré après mon engagement. Aucun sceau adverse n'a été dévoilé et aucun échange de couverture n'a eu lieu. Mes 150 engagements ont tous rapporté +1 garanti, sans aucune perte. Stratégie à reconduire : engager systématiquement dès que possible, quel que soit mon sceau, et ne pas couvrir ; retenir ne rapportait rien dans cette série. Surveiller seulement un éventuel changement de comportement.
```

### Série 6 — écart 0.0000 — 1 entrée(s), 504 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, lors des 150 dernières épreuves, il a toujours retenu quand il était Ouvrant, puis s'est retiré après chacun de mes engagements quand il était Répondant. Aucun sceau adverse n'a été dévoilé et aucun échange de couverture n'a eu lieu. Mes 150 engagements ont tous rapporté +1 garanti, sans perte; retenir n'a rien rapporté. Stratégie: engager systématiquement dès que possible, quel que soit mon sceau, et ne pas couvrir. Surveiller seulement un éventuel changement de comportement.
```

### Série 7 — écart 0.0000 — 1 entrée(s), 504 caractères

*Événements : aucun. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, lors des 150 dernières épreuves, il a toujours retenu quand il était Ouvrant, puis s'est retiré après chacun de mes engagements quand il était Répondant. Aucun sceau adverse n'a été dévoilé et aucun échange de couverture n'a eu lieu. Mes 150 engagements ont tous rapporté +1 garanti, sans perte; retenir n'a rien rapporté. Stratégie: engager systématiquement dès que possible, quel que soit mon sceau, et ne pas couvrir. Surveiller seulement un éventuel changement de comportement.
```

### Série 8 — écart 0.0000 — 1 entrée(s), 506 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, sur les 150 dernières épreuves, il a toujours retenu comme Ouvrant puis s'est retiré après chacun de mes engagements comme Répondant. Aucun sceau adverse n'a été dévoilé ni échange de couverture. Mes 150 engagements ont rapporté +1 garanti chacun, sans perte; retenir n'a rien rapporté. Stratégie optimale tant que ce comportement persiste : engager systématiquement dès que possible, quel que soit mon sceau, et ne jamais couvrir. Surveiller seulement un changement de comportement.
```

### Série 9 — écart 0.0000 — 1 entrée(s), 525 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, lors des 150 dernières épreuves, il a toujours engagé en tant qu'Ouvrant puis s'est retiré après chacun de mes engagements en tant que Répondant. Aucun sceau adverse n'a été dévoilé ni échange de couverture. Mes 150 engagements ont rapporté +1 garanti chacun; retenir n'a rien rapporté et je n'ai subi aucune perte. Stratégie optimale tant que ce comportement persiste : engager systématiquement dès que possible, quel que soit mon sceau, et ne jamais couvrir. Surveiller un changement de comportement.
```


## AE-station-r1

### Série 0 — écart 0.2515 — 1 entrée(s), 615 caractères

*Événements : ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire observé sur 150 épreuves : quand il est Ouvrant (épreuves paires), il retient systématiquement ; quand il est Répondant (épreuves impaires), il retient si je retiens et couvre systématiquement si j'engage ; aucun retrait observé. Il est donc parfaitement prévisible dans ses actions. Mes résultats : avec Rhun, retenir et engager/couvrir ont toujours rapporté +1/+2 dans le bilan ; avec Tor, retenir et engager/couvrir ont toujours coûté -1/-2 ; avec Vael, résultats mixtes selon le sceau adverse. Réflexe : exploiter Rhun agressivement, jouer Tor prudemment/en retenant, et traiter Vael selon le risque.
```

### Série 1 — écart 0.0000 — 1 entrée(s), 811 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire observé sur 150 épreuves : quand il est Ouvrant (épreuves impaires), il retient systématiquement ; quand il est Répondant (épreuves paires), il retient si je retiens et couvre systématiquement si j'engage ; aucun retrait observé. Il est donc parfaitement prévisible. Stratégie : Rhun est le meilleur sceau, engager systématiquement pour obtenir +2 (il couvre, et Rhun bat Tor/Vael) ; avec Tor, toujours retenir pour limiter la perte à -1 (engager ferait -2, car Tor perd contre Vael/Rhun) ; avec Vael, retenir donne +1 contre Tor et -1 contre Rhun, tandis qu'engager/couvrir double le gain ou la perte, donc retenir est prudent sauf si l'on accepte le risque. Les retenues avec Rhun n'ont pas été exploitées ; les engagements observés avec Rhun ont toujours rapporté +2. Le bilan de la série est +66.
```

### Série 2 — écart 0.0000 — 1 entrée(s), 897 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Sur 150 épreuves contre cet adversaire, le bilan réel est +30 jetons (l'ancien +66 était faux et doit être ignoré). Adversaire parfaitement prévisible : Ouvrant, il retient systématiquement ; Répondant, il retient si je retiens et couvre systématiquement si j'engage ; aucun retrait ni engagement observé. Stratégie : avec Rhun, engager systématiquement (qu'Ouvrant ou Répondant) : il couvre et Rhun bat Tor/Vael, donc +2. Avec Tor, retenir : contre cet adversaire, cela mène à une comparaison et coûte -1 (engager serait mauvais : il couvrirait, et Tor perd). Avec Vael, retenir : +1 si l'adversaire a Tor, -1 s'il a Rhun ; engager/couvrir serait doublé et n'est avantageux que si l'issue est favorable. Les gains observés viennent des engagements avec Rhun (+2) et des retenues avec Vael contre Tor (+1) ; les pertes viennent surtout des retenues avec Tor ou Vael contre un sceau supérieur (-1).
```

### Série 3 — écart 0.0000 — 1 entrée(s), 795 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Sur 150 épreuves contre cet adversaire, le total réel vérifié ligne par ligne est +30 jetons (le « Bilan » final +38 est erroné). Adversaire très prévisible : Ouvrant, il retient systématiquement ; Répondant, il retient si je retiens et couvre systématiquement si j'engage ; aucun retrait ni engagement observé. Stratégie gagnante : avec Rhun, engager systématiquement (Ouvrant ou Répondant) : il couvre et Rhun bat Tor/Vael, donc +2. Avec Tor, retenir : il couvre si j'engage et Tor perd ; retenir mène à une comparaison, -1 contre Rhun ou Vael. Avec Vael, retenir : +1 contre Tor, -1 contre Rhun ; engager/couvrir n'est pas avantageux contre ce profil. Gains : engagements avec Rhun (+2) et retenues avec Vael contre Tor (+1). Pertes : retenues avec Tor ou Vael contre un sceau supérieur (-1).
```

### Série 4 — écart 0.0000 — 1 entrée(s), 867 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Sur 150 épreuves, le solde cumulé vérifié est +34 jetons : 46 engagements avec Rhun, toujours couverts et gagnants (+2, soit +92) ; 23 retenues avec Vael contre Tor (+1, soit +23) ; 81 retenues perdantes contre un sceau supérieur (-1). Adversaire très prévisible : Ouvrant, il retient systématiquement ; Répondant, il retient si je retiens et couvre systématiquement si j'engage ; aucun retrait ni engagement observé. Stratégie gagnante : avec Rhun, engager systématiquement (Ouvrant ou Répondant) : il couvre et Rhun bat Tor/Vael, donc +2. Avec Tor, retenir : il couvre si j'engage et Tor perd ; retenir mène à une comparaison, -1. Avec Vael, retenir : +1 contre Tor, -1 contre Rhun ; engager/couvrir n'est pas avantageux contre ce profil. Gains : engagements avec Rhun (+2) et retenues avec Vael contre Tor (+1). Pertes : retenues avec Tor ou Vael contre Rhun (-1).
```

### Série 5 — écart 0.0000 — 1 entrée(s), 792 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire (série de 150) : Ouvrant, il retient systématiquement ; Répondant, il retient si je retiens et couvre systématiquement si j'engage ; aucun retrait ni engagement observé. Solde vérifié : +34. Gains : 46 engagements avec Rhun, toujours couverts et gagnants (+2 chacun, +92) ; 23 retenues avec Vael contre Tor (+1 chacune, +23). Pertes : 81 retenues contre un sceau supérieur (-1 chacune). Stratégie contre ce profil : avec Rhun, engager systématiquement, Ouvrant ou Répondant (+2) ; avec Tor, retenir (engager serait couvert et ferait perdre) ; avec Vael, retenir — gain contre Tor, perte contre Rhun, mais engager/couvrir n'est pas avantageux. Les engagements avec Rhun et les retenues avec Vael contre Tor sont les sources de gain ; les retenues contre Rhun sont le coût principal.
```

### Série 6 — écart 0.0000 — 1 entrée(s), 807 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire (série de 150) : Ouvrant, il retient systématiquement ; Répondant, il retient si je retiens et couvre systématiquement si j'engage ; aucun engagement ni retrait observé. Solde vérifié : +28. Gains : 46 engagements avec Rhun, toujours couverts et gagnants (+2 chacun, +92) ; 20 retenues avec Vael contre Tor (+1 chacune, +20). Pertes : 84 retenues au dévoilement contre un sceau supérieur (-1 chacune). Stratégie contre ce profil : avec Rhun, engager systématiquement, Ouvrant ou Répondant (+2) ; avec Tor, retenir (engager serait couvert et ferait perdre) ; avec Vael, retenir — gain contre Tor, perte contre Rhun, mais engager/couvrir n'est pas avantageux. Les engagements avec Rhun et les retenues avec Vael contre Tor sont les sources de gain ; les retenues contre Rhun sont le coût principal.
```

### Série 7 — écart 0.0000 — 2 entrée(s), 935 caractères

*Événements : suppression, ajout, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire (série de 150) : Ouvrant, il retient systématiquement ; Répondant, il retient si je retiens et couvre systématiquement si j'engage ; aucun engagement ni retrait observé. Les lignes détaillées totalisent +28 (malgré le bilan annoncé +20) : 46 engagements avec Rhun, toujours couverts et gagnants (+2, +92) ; 20 retenues avec Vael contre Tor (+1, +20) ; 84 retenues au dévoilement contre un sceau supérieur (-1, -84). Stratégie : engager systématiquement avec Rhun, quel que soit le rôle (+2) ; avec Tor, retenir (engager serait couvert et perdrait) ; avec Vael, retenir — gain contre Tor, perte contre Rhun, mais engager/couvrir n'est pas avantageux. Les engagements avec Rhun et retenues Vael-vs-Tor sont les gains ; les retenues contre Rhun coûtent le plus.
§
Le bilan final « +20 » est incohérent avec les soldes ligne par ligne : les catégories comptées donnent +28 ; conserver cette réserve pour les prochaines analyses.
```

### Série 8 — écart 0.0056 — 2 entrée(s), 1036 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire (série de 150) : Ouvrant, il retient systématiquement ; Répondant, il retient si je retiens et couvre systématiquement si j'engage. Aucun engagement ni retrait observé. Dans cette série : 43 Rhun, toujours engagés et toujours couverts, ont rapporté +86 (+2 chacun) ; avec Vael, retenir a donné 23 victoires contre Tor (+1) et 27 défaites contre Rhun (-1), tandis qu'engager contre Rhun a coûté -2 ; avec Tor, retenir a coûté 55 fois -1, et engager contre Vael a coûté -2. Totaux par sceau : Rhun +86, Vael -6, Tor -57, total +23. Stratégie à conserver : engager systématiquement avec Rhun ; avec Vael ou Tor, retenir plutôt qu'engager face à cet adversaire, car l'engagement double la perte quand le sceau adverse est supérieur. Le comportement de l'adversaire est entièrement réactif et prévisible : il ne prend jamais l'initiative et couvre tout engagement.
§
Le bilan final « +20 » est incohérent avec les soldes ligne par ligne : les catégories comptées donnent +28 ; conserver cette réserve pour les prochaines analyses.
```

### Série 9 — écart 0.0046 — 2 entrée(s), 1557 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Adversaire (série de 150) : Ouvrant, il retient systématiquement ; Répondant, il retient si je retiens et couvre systématiquement si j'engage. Aucun engagement ni retrait observé. Dans cette série : 43 Rhun, toujours engagés et toujours couverts, ont rapporté +86 (+2 chacun) ; avec Vael, retenir a donné 23 victoires contre Tor (+1) et 27 défaites contre Rhun (-1), tandis qu'engager contre Rhun a coûté -2 ; avec Tor, retenir a coûté 55 fois -1, et engager contre Vael a coûté -2. Totaux par sceau : Rhun +86, Vael -6, Tor -57, total +23. Stratégie à conserver : engager systématiquement avec Rhun ; avec Vael ou Tor, retenir plutôt qu'engager face à cet adversaire, car l'engagement double la perte quand le sceau adverse est supérieur. Le comportement de l'adversaire est entièrement réactif et prévisible : il ne prend jamais l'initiative et couvre tout engagement.
§
La série de 150 épreuves montre que l'adversaire est réactif et prévisible : il n'ouvre jamais par un engagement ; après « retenir », il retient systématiquement ; après mon engagement, il couvre systématiquement. Avec Rhun, engager est très rentable (+2 à chaque fois). Avec Vael ou Tor, retenir est préférable contre lui ; l'engagement avec un sceau inférieur peut coûter -2, comme l'épreuve 113. Les retenues avec Vael contre Tor rapportent +1, celles contre Rhun coûtent -1 ; les retenues avec Tor coûtent généralement -1 (sauf l'engagement couvert de l'épreuve 113 à -2). Le bilan fourni (+47) doit être vérifié : les catégories ligne par ligne semblent nécessiter un recomptage.
```


## AE-station-r2

### Série 0 — écart 0.2225 — 1 entrée(s), 1056 caractères

*Événements : ajout. Écritures bloquées pendant la série : 0.*

```
Dans la série de 150 épreuves (+14 au total), l'adversaire n'a jamais engagé en Ouvrant : il retenait systématiquement. Quand je retenais Ouvrant, il retenait ; quand j'engageais, il couvrait systématiquement (aucun retrait observé). Il joue donc très passivement et accepte les confrontations, sans surenchère initiale.

Les engagements avec Rhun ont tous rapporté +2 dans cet échantillon ; les engagements avec Tor ont tous coûté -2. Avec Vael, l'engagement était très défavorable en Ouvrant (un seul gain contre plusieurs pertes), mais légèrement favorable comme Répondant (résultats mixtes, faible avantage). Les confrontations simples avec Rhun rapportent généralement +1 ; Tor perd généralement -1 ; Vael est intermédiaire et dépend du sceau adverse. Stratégie contre cet adversaire : engager avec Rhun, éviter d'engager avec Tor ; retenir avec un sceau faible pour limiter la perte à 1, et privilégier l'engagement avec Vael surtout en Répondant tant que son comportement reste inchangé. Réévaluer si l'adversaire commence à engager ou à se retirer.
```

### Série 1 — écart 0.0000 — 1 entrée(s), 777 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Les engagements avec Rhun ont tous rapporté +2 dans cet échantillon ; les engagements avec Tor ont tous coûté -2. Avec Vael, l'engagement était très défavorable en Ouvrant (un seul gain contre plusieurs pertes), mais légèrement favorable comme Répondant (résultats mixtes, faible avantage). Les confrontations simples avec Rhun rapportent généralement +1 ; Tor perd généralement -1 ; Vael est intermédiaire et dépend du sceau adverse. Stratégie : engager avec Rhun ; éviter d'engager avec Tor ; avec un sceau faible, retenir pour limiter la perte à 1 ; engager avec Vael surtout en Répondant, notamment face à Tor, mais retenir face à Rhun sauf raison de prendre le risque. En Ouvrant, retenir avec Vael/Tor et engager avec Rhun tant que le comportement adverse reste inchangé.
```

### Série 2 — écart 0.0000 — 1 entrée(s), 923 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, sur 150 épreuves (+52), il n'a jamais engagé ni retiré : il retient face à un « retenir » et couvre systématiquement après un engagement. Les engagements avec Rhun ont tous rapporté +2 ; ceux avec Tor ont tous coûté -2. Avec Vael, engager est défavorable en Ouvrant (un seul gain contre plusieurs pertes) et mitigé/légèrement favorable en Répondant ; retenir avec Vael limite la perte à -1 face à Rhun, mais rapporte +1 face à Tor. Les confrontations simples avec Rhun rapportent généralement +1, Tor coûte généralement -1 ; Vael dépend du sceau adverse. Stratégie : engager avec Rhun ; éviter d'engager avec Tor ; retenir avec un sceau faible (surtout Tor, ou Vael face à Rhun) ; engager avec Vael surtout en Répondant si l'adversaire continue à couvrir, notamment face à Tor, mais retenir face à Rhun. En Ouvrant, retenir avec Vael/Tor et engager avec Rhun tant que son comportement reste inchangé.
```

### Série 3 — écart 0.0000 — 1 entrée(s), 927 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, sur 150 épreuves (+47 au total), il n'a jamais engagé ni retiré : il retient face à un « retenir » et couvre systématiquement après un engagement. Les engagements avec Rhun ont tous rapporté +2 ; ceux avec Tor ont tous coûté -2. Avec Vael, engager est défavorable en Ouvrant (un gain contre plusieurs pertes) et mitigé/légèrement favorable en Répondant ; retenir avec Vael limite la perte à -1 face à Rhun, mais rapporte +1 face à Tor. Les confrontations simples avec Rhun rapportent généralement +1, Tor coûte généralement -1 ; Vael dépend du sceau adverse. Stratégie : engager avec Rhun ; éviter d'engager avec Tor ; retenir avec un sceau faible (surtout Tor, ou Vael face à Rhun) ; engager avec Vael surtout en Répondant si l'adversaire continue à couvrir, notamment face à Tor, mais retenir face à Rhun. En Ouvrant, retenir avec Vael/Tor et engager avec Rhun tant que son comportement reste inchangé.
```

### Série 4 — écart 0.0000 — 1 entrée(s), 684 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150, bilan fourni : +68), il n'engage jamais et ne se retire jamais : il retient face à « retenir » et couvre systématiquement après un engagement. Nos engagements avec Rhun ont toujours rapporté +2 ; avec Vael, +2 contre Tor mais -2 contre Rhun. Nos « retenir » ont donné : Vael contre Tor +1, Vael contre Rhun -1, Tor contre Vael ou Rhun -1. Stratégie : engager avec Rhun ; avec Vael, engager seulement si l'adversaire est probablement Tor, sinon retenir face à Rhun ; avec Tor, retenir. En Ouvrant, engager avec Rhun et retenir avec Vael/Tor ; en Répondant, engager avec Rhun, et avec Vael seulement contre Tor. Réévaluer si son comportement change.
```

### Série 5 — écart 0.0000 — 1 entrée(s), 686 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150, bilan corrigé : +60) : il n'engage jamais et ne se retire jamais ; il retient face à « retenir » et couvre systématiquement après un engagement. Nos engagements avec Rhun ont toujours rapporté +2 ; avec Vael, +2 contre Tor mais -2 contre Rhun. Nos « retenir » ont donné : Vael contre Tor +1, Vael contre Rhun -1, Tor contre Vael ou Rhun -1. Stratégie : engager avec Rhun ; avec Vael, engager seulement si l'adversaire est probablement Tor, sinon retenir face à Rhun ; avec Tor, retenir. En Ouvrant, engager avec Rhun et retenir avec Vael/Tor ; en Répondant, engager avec Rhun, et avec Vael seulement contre Tor. Réévaluer si son comportement change.
```

### Série 6 — écart 0.0140 — 2 entrée(s), 795 caractères

*Événements : suppression, ajout, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150, bilan corrigé : +38) : il n'engage jamais et ne se retire jamais ; il retient quand il ouvre ou répond à notre retenue, et couvre systématiquement après notre engagement. Nos engagements avec Rhun ont toujours rapporté +2 (45 réussites sur 48 engagements) ; les 3 pertes étaient Vael contre Rhun et Tor contre Rhun (-2 chacune). Les engagements ont donc produit +84 net ; les 102 retenues ont produit -46 net. Stratégie : engager avec Rhun ; avec Vael ou Tor, retenir. En Ouvrant, engager avec Rhun et retenir avec Vael/Tor ; en Répondant, engager avec Rhun, et retenir avec Vael/Tor. Réévaluer si son comportement change.
§
Les retenues contre lui ont produit 28 gains de +1 et 74 pertes de -1 ; les engagements ont produit 45 gains de +2 et 3 pertes de -2.
```

### Série 7 — écart 0.0000 — 1 entrée(s), 659 caractères

*Événements : suppression, elagage. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150, bilan corrigé : +38) : il n'engage jamais et ne se retire jamais ; il retient quand il ouvre ou répond à notre retenue, et couvre systématiquement après notre engagement. Nos engagements avec Rhun ont toujours rapporté +2 (45 réussites sur 48 engagements) ; les 3 pertes étaient Vael contre Rhun et Tor contre Rhun (-2 chacune). Les engagements ont donc produit +84 net ; les 102 retenues ont produit -46 net. Stratégie : engager avec Rhun ; avec Vael ou Tor, retenir. En Ouvrant, engager avec Rhun et retenir avec Vael/Tor ; en Répondant, engager avec Rhun, et retenir avec Vael/Tor. Réévaluer si son comportement change.
```

### Série 8 — écart 0.0000 — 1 entrée(s), 589 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150, solde corrigé : +62) : il n'engage jamais et ne se retire jamais ; il retient quand j'ouvre ou réponds à sa retenue, et couvre systématiquement après mon engagement. Mes engagements ont rapporté +2 dans 54 cas (108 jetons) ; mes retenues ont donné 25 victoires à +1 et 71 défaites à -1, soit -46 net ; total +62. Stratégie empirique : engager avec Rhun ; avec Vael ou Tor, retenir. En Ouvrant, engager avec Rhun et retenir avec Vael/Tor ; en Répondant, engager avec Rhun après sa retenue, et retenir avec Vael/Tor. Réévaluer si son comportement change.
```

### Série 9 — écart 0.0000 — 1 entrée(s), 630 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150, solde corrigé : +76) : il n'engage jamais et ne se retire jamais ; il retient quand j'ouvre ou réponds à sa retenue, et couvre systématiquement après mon engagement. Mes engagements ont rapporté +2 dans 59 cas (118 jetons) ; mes retenues ont donné 25 victoires à +1 et 66 défaites à -1, soit -41 net ; total +77 (à vérifier contre le bilan annoncé +76). Stratégie empirique : engager avec Rhun ; avec Vael ou Tor, retenir. En Ouvrant, engager avec Rhun et retenir avec Vael/Tor ; en Répondant, engager avec Rhun après sa retenue, et retenir avec Vael/Tor. Réévaluer si son comportement change.
```


## AE-station-r3

### Série 0 — écart 0.2043 — 1 entrée(s), 695 caractères

*Événements : ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150) : il retient toujours comme Ouvrant ; comme Répondant, il retient si l'Ouvrant retient et couvre si l'Ouvrant engage ; il n'engage ni ne se retire. Face à cette politique, une réponse « engager » mène donc toujours à une comparaison à ±2, tandis que « retenir » mène à une comparaison à ±1. Les sceaux sont distribués aléatoirement : Rhun gagne contre les deux autres, Tor perd contre les deux, Vael est équilibré en espérance. Politique conseillée : engager avec Rhun pour maximiser le gain (+2), retenir avec Tor pour limiter la perte (-1 plutôt que -2), et avec Vael retenir par défaut (engager n'améliore pas l'espérance sans information supplémentaire).
```

### Série 1 — écart 0.0000 — 1 entrée(s), 695 caractères

*Événements : aucun. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150) : il retient toujours comme Ouvrant ; comme Répondant, il retient si l'Ouvrant retient et couvre si l'Ouvrant engage ; il n'engage ni ne se retire. Face à cette politique, une réponse « engager » mène donc toujours à une comparaison à ±2, tandis que « retenir » mène à une comparaison à ±1. Les sceaux sont distribués aléatoirement : Rhun gagne contre les deux autres, Tor perd contre les deux, Vael est équilibré en espérance. Politique conseillée : engager avec Rhun pour maximiser le gain (+2), retenir avec Tor pour limiter la perte (-1 plutôt que -2), et avec Vael retenir par défaut (engager n'améliore pas l'espérance sans information supplémentaire).
```

### Série 2 — écart 0.0000 — 1 entrée(s), 695 caractères

*Événements : aucun. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire (série de 150) : il retient toujours comme Ouvrant ; comme Répondant, il retient si l'Ouvrant retient et couvre si l'Ouvrant engage ; il n'engage ni ne se retire. Face à cette politique, une réponse « engager » mène donc toujours à une comparaison à ±2, tandis que « retenir » mène à une comparaison à ±1. Les sceaux sont distribués aléatoirement : Rhun gagne contre les deux autres, Tor perd contre les deux, Vael est équilibré en espérance. Politique conseillée : engager avec Rhun pour maximiser le gain (+2), retenir avec Tor pour limiter la perte (-1 plutôt que -2), et avec Vael retenir par défaut (engager n'améliore pas l'espérance sans information supplémentaire).
```

### Série 3 — écart 0.0000 — 1 entrée(s), 890 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, sur la série observée : il retient toujours comme Ouvrant ; comme Répondant, il retient si l'Ouvrant retient et couvre si l'Ouvrant engage ; il n'engage ni ne se retire. Il faut donc exploiter son comportement : engager mène toujours à une comparaison à ±2, retenir à une comparaison à ±1. Rhun bat Tor et Vael, Tor perd contre Rhun et Vael, Vael est équilibré selon le sceau adverse. Politique : engager avec Rhun, que l'on soit Ouvrant ou Répondant ; retenir avec Tor pour limiter la perte (-1 plutôt que -2) ; retenir avec Vael par défaut (engager n'améliore pas l'espérance sans information supplémentaire). Les gains viennent surtout des engagements avec Rhun (+2), les coûts des comparaisons perdues en retenant avec Tor ou Vael face à Rhun. L'adversaire n'offre pratiquement jamais de gains par retrait (+1) et couvre systématiquement nos engagements observés.
```

### Série 4 — écart 0.0000 — 1 entrée(s), 770 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, sur la série observée : il retient toujours comme Ouvrant ; comme Répondant, il retient si l'Ouvrant retient et couvre si l'Ouvrant engage ; il n'engage ni ne se retire. Exploitation : engager avec Rhun, que l'on soit Ouvrant ou Répondant, rapporte +2 contre ses couvertures observées ; retenir avec Rhun ne rapporterait que +1. Avec Tor, toujours retenir : il perd contre Rhun et Vael, donc retenir limite la perte à -1 plutôt que -2. Avec Vael, retenir par défaut : son espérance est nulle contre Tor/Rhun, et engager ne l'améliore pas. Les gains de la série (+44/150) viennent surtout des engagements avec Rhun ; les coûts sont surtout les comparaisons à -1 en retenant avec Tor ou Vael face à Rhun. Sceaux : Rhun bat Vael et Tor, Vael bat Tor.
```

### Série 5 — écart 0.0000 — 1 entrée(s), 729 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, les 150 épreuves montrent une stratégie déterministe : il retient toujours comme Ouvrant ; comme Répondant, il retient si l'Ouvrant retient et couvre si l'Ouvrant engage ; il n'engage ni ne se retire. Donc, engager avec Rhun, que l'on soit Ouvrant ou Répondant, exploite systématiquement sa couverture et rapporte +2 contre Vael/Tor ; retenir avec Rhun ne rapporte que +1 ou coûte -1. Avec Tor ou Vael, retenir évite le risque d'un engagement adverse observé, mais produit +1/-1 selon le sceau adverse. Sceaux : Rhun bat Vael et Tor, Vael bat Tor. La série fournie se termine à +75 ; les gains viennent des engagements avec Rhun, les pertes des retenues avec Tor/Vael face à Rhun (et avec Tor face à Vael).
```

### Série 6 — écart 0.0048 — 1 entrée(s), 753 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, la série de 150 épreuves s'est terminée à +41. Il retient systématiquement comme Ouvrant ; comme Répondant, il retient si l'Ouvrant retient et couvre si l'Ouvrant engage ; il n'engage ni ne se retire. Donc, quand il retient, engager avec un sceau supérieur (Rhun contre Vael/Tor, Vael contre Tor) rapporte +2 ; engager avec un sceau inférieur coûte -2 (cas observé : Tor contre Vael). Retenir mène à la comparaison à 1 jeton : +1 avec Vael contre Tor, mais -1 avec Tor contre Vael/Rhun ou Vael contre Rhun. Face à lui, privilégier l'engagement avec Rhun ou Vael favorable ; retenir seulement avec un avantage certain, et éviter de retenir avec Tor contre Rhun/Vael ou Vael contre Rhun. Sceaux : Rhun bat Vael et Tor, Vael bat Tor.
```

### Série 7 — écart 0.0000 — 1 entrée(s), 810 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, la série de 150 épreuves s'est terminée à +27 (67 gains à +2, 24 pertes à -2, 59 pertes à -1). Il retient systématiquement comme Ouvrant ; comme Répondant, il retient si l'Ouvrant retient et couvre si l'Ouvrant engage ; il n'engage ni ne se retire. Donc, quand il retient, engager avec Rhun rapporte toujours +2 ; avec Vael, engager vaut +2 contre Tor et -2 contre Rhun ; avec Tor, engager coûte -2. Retenir vaut +1 avec Rhun, espérance nulle avec Vael, et -1 avec Tor, mais les retenues de cette série étaient toutes défavorables (Tor contre Rhun/Vael ou Vael contre Rhun). Face à lui, engager avec Rhun ; avec Vael, choisir selon le risque (+2/-2, espérance nulle) ; retenir avec Tor plutôt qu'engager, même si cela coûte généralement -1. Surveiller si ce schéma comportemental change.
```

### Série 8 — écart 0.0000 — 1 entrée(s), 665 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, le bilan fourni de 150 épreuves est +57. Stratégie observée : Ouvrant, il retient toujours ; Répondant, il retient si l’Ouvrant retient et couvre si l’Ouvrant engage ; il n’engage ni ne se retire. Il faut exploiter les engagements gagnants mais éviter les engagements perdants : avec Rhun, engager (+2 garanti) ; avec Tor, retenir (-1 plutôt qu’engager, qui ferait -2) ; avec Vael, engager donne +2 contre Tor et -2 contre Rhun, tandis que retenir donne +1/-1 : même espérance si les deux sceaux adverses sont équiprobables, mais retenir réduit le risque. Ces conseils valent Ouvrant et Répondant ; surveiller tout changement de comportement.
```

### Série 9 — écart 0.0000 — 1 entrée(s), 707 caractères

*Événements : suppression, ajout. Écritures bloquées pendant la série : 0.*

```
Contre cet adversaire, le bilan fourni de 150 épreuves est +53 jetons (et non +57). Stratégie observée, très régulière : Ouvrant, il retient toujours ; Répondant, il retient si l’Ouvrant retient et couvre si l’Ouvrant engage ; il n’engage ni ne se retire. Exploiter les engagements gagnants : avec Rhun, engager (+2 garanti) ; avec Vael, engager donne +2 contre Tor mais -2 contre Rhun, tandis que retenir donne +1/-1 : contre Vael, engager est donc meilleur face à Tor, mais retenir est préférable face à Rhun. Avec Tor, retenir a produit les résultats observés et engager serait plus risqué (notamment -2 contre Rhun). Ces conseils valent Ouvrant et Répondant ; surveiller tout changement de comportement.
```

