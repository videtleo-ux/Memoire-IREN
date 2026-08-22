# Orchestration d'une tranche de campagne (PRD 3 §8 : l'unite parallelisable
# est le RUN, jamais la serie — les series d'un run sont sequentielles parce
# que M_s depend de M_{s-1}).
#
# Trois points qui ne sont pas cosmetiques :
#
# 1. Les lancements sont decales de 30 s. Le canari d'isolation de chaque run
#    ne voit que les stores DEJA crees : demarrer six runs a la meme seconde
#    rend le controle croise vide au demarrage (CONTEXT.md §4 quinquies). Le
#    decalage donne a chaque canari les voisins des precedents.
# 2. Chaque run ecrit ses CSV dans SON dossier. `generer()` balaie toute la
#    racine et reecrit les fichiers en entier : deux runs qui closent une
#    serie en meme temps se marcheraient dessus. Les CSV d'analyse sont
#    regeneres une fois, a la fin, par `python -m journal.derives`.
# 3. `--series` n'est jamais passe : la regle du PRD s'applique seule (SM = 3
#    series, AE = plateau constate, plafond 16). Forcer un compte remplacerait
#    un critere scientifique par une contrainte d'ordonnancement.
#
# Le script est relançable : un run deja termine repart, constate ses series
# closes et s'arrete ; un run interrompu reprend a sa derniere frontiere.
#
# LANCEMENT — en processus detache, pour qu'il survive a la fermeture du
# terminal (une tranche dure une dizaine d'heures) :
#
#   $s = "<...>\scripts\lancer-campagne.ps1"
#   Start-Process powershell.exe -WindowStyle Hidden -PassThru `
#       -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-File","`"$s`""
#
# Les guillemets internes autour de $s ne sont pas decoratifs : le chemin du
# depot contient des espaces, et sans eux powershell.exe recoit un chemin
# tronque, ne trouve pas le fichier et meurt sans rien ecrire — silencieux,
# puisque la sortie n'est encore redirigee nulle part.
#
# PREALABLE — l'authentification Nous Portal doit etre valide AVANT le
# lancement : chaque store clone `auth.json` a sa creation. Un jeton mort fait
# echouer les 18 runs sur leur canari, l'un apres l'autre. A verifier par
# `hermes auth status nous` (doit dire « logged in »), a reparer par
# `hermes portal login`.

$ErrorActionPreference = "Stop"

# Depuis scripts/ — evite d'ecrire en dur un chemin qui contient des accents,
# que PowerShell 5.1 relit mal selon l'encodage du fichier.
$Depot    = Split-Path $PSScriptRoot -Parent
$Python   = "C:\Users\videt\anaconda3\python.exe"
$Racine   = "C:\arene-runs"
$HomeSrc  = "C:\Users\videt\AppData\Local\hermes"
$Modele   = "openai/gpt-5.6-luna"
$K        = 150
# 3 et non 5 : a cinq exécutions de front, le compte Nous Portal a heurte sa
# limite de debit apres ~1 h 50 (« rate limit active — resets in 7m 39s »), ce
# qui a arrete cinq runs d'un coup le 2026-08-22. Le harnais sait desormais
# patienter le temps annonce (harnais.hermes.delai_rate_limit), mais mieux vaut
# ne pas provoquer la limite : trois runs tiennent ~14 appels/minute.
$Front    = 3
$Decalage = 30

$env:PYTHONPATH = Join-Path $Depot "src"

$Journaux = Join-Path $Racine "lancements"
New-Item -ItemType Directory -Force $Journaux | Out-Null
$Log = Join-Path $Journaux "orchestration.log"

function Ecrire($texte) {
    $ligne = "{0}  {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $texte
    Add-Content -Path $Log -Value $ligne -Encoding utf8
}

# AE avant SM : les runs les plus longs d'abord (le plus court chemin vers la
# fin quand un pool de largeur fixe traite des taches de durees inegales).
# Bots entrelaces par replication : si la tranche doit s'arreter en route, ce
# sont des replications entieres qui sont acquises, pas des moities.
$File = @()
foreach ($condition in @("AE", "SM")) {
    foreach ($replication in 1..3) {
        foreach ($bot in @("Station", "Over-folder", "GTO")) {
            $File += [pscustomobject]@{
                Condition = $condition; Bot = $bot; Replication = $replication
            }
        }
    }
}

Ecrire ("tranche SM+AE : {0} runs, K={1}, modele {2}, {3} de front" -f $File.Count, $K, $Modele, $Front)

$enCours = @()
$suivant = 0

while ($suivant -lt $File.Count -or $enCours.Count -gt 0) {

    foreach ($termine in @($enCours | Where-Object { $_.Proc.HasExited })) {
        Ecrire ("fini  {0} (code {1})" -f $termine.Id, $termine.Proc.ExitCode)
    }
    $enCours = @($enCours | Where-Object { -not $_.Proc.HasExited })

    if ($suivant -lt $File.Count -and $enCours.Count -lt $Front) {
        $tache = $File[$suivant]
        $id = "{0}-{1}-r{2}" -f $tache.Condition, $tache.Bot.ToLower(), $tache.Replication

        $arguments = @(
            "-m", "arbitre",
            "--condition", $tache.Condition,
            "--bot", $tache.Bot,
            "--replication", $tache.Replication,
            "--K", $K,
            "--modele", $Modele,
            "--racine", $Racine,
            "--home-source", $HomeSrc,
            "--machine", "victus",
            "--csv", (Join-Path $Racine "csv-partiels\$id")
        )

        $proc = Start-Process -FilePath $Python -ArgumentList $arguments `
            -WorkingDirectory $Depot `
            -RedirectStandardOutput (Join-Path $Journaux "$id.out") `
            -RedirectStandardError  (Join-Path $Journaux "$id.err") `
            -WindowStyle Hidden -PassThru

        Ecrire ("lance {0} (pid {1})" -f $id, $proc.Id)
        $enCours += [pscustomobject]@{ Id = $id; Proc = $proc }
        $suivant++
        Start-Sleep -Seconds $Decalage
    }
    else {
        Start-Sleep -Seconds 15
    }
}

Ecrire "tranche terminee"
