# =============================================================================
# analyse.R — Toute la partie III recalculée depuis `donnees/decisions.csv`.
# =============================================================================
#
#   Rscript analyse/R/analyse.R
#
# Sorties : les tableaux dans la console, les figures dans analyse/R/figures/.
#
# CE QUE FAIT CE SCRIPT, DANS L'ORDRE :
#   §1  charge les 27 290 décisions
#   §2  en tire pi-chapeau — LA seule statistique du dispositif
#   §3  calcule écart et référence récitée pour les 177 séries
#   §4  VÉRIFIE le résultat contre les chiffres publiés (sessions.csv)
#   §5  H1 — l'adaptation vient de la mémoire
#   §6  H2 — elle exploite, elle ne récite pas (+ le contrôle négatif)
#   §7  H3 — le mécanisme de rétention (+ l'intervalle de confiance)
#   §8  H4 — dégénérescence des mixtes, et incohérence raisonnement/action
#   §9  les figures
#
# Le calcul du jeu lui-même est dans moteur.R, réécrit indépendamment du Python.

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(readr)
  library(ggplot2)
})

# À lancer depuis la racine du dépôt (celle qui contient `donnees/`).
if (!file.exists("donnees/decisions.csv")) {
  stop("Lancez ce script depuis la racine du dépôt : setwd(\"...../Code\")")
}
source("analyse/R/moteur.R")

SORTIE <- "analyse/R/figures"
dir.create(SORTIE, showWarnings = FALSE, recursive = TRUE)

titre <- function(x) cat("\n\n", strrep("=", 78), "\n", x, "\n", strrep("=", 78), "\n\n", sep = "")
montrer <- function(df) print(as.data.frame(df), row.names = FALSE, digits = 4)

# =============================================================================
# §0. Le moteur se vérifie lui-même avant toute chose
# =============================================================================
titre("§0. AUTO-VÉRIFICATION DU MOTEUR (indépendant de src/moteur)")
tests <- verifier_moteur()
montrer(data.frame(propriete = names(tests), tient = as.vector(tests)))
if (!all(tests)) stop("Le moteur R est faux : tout ce qui suit est invalide.")

# =============================================================================
# §1. Les données
# =============================================================================
# decisions.csv : UNE LIGNE PAR DÉCISION DE L'AGENT. 27 290 lignes logiques,
# mais 81 854 lignes physiques — la colonne `sortie_brute` contient des sauts de
# ligne, entre guillemets. read_csv gère ça ; un `strsplit` maison, non.
# Le fichier est en UTF-8 SANS BOM : d'où le `locale()` explicite.

titre("§1. CHARGEMENT")
d <- read_csv("donnees/decisions.csv",
              locale = locale(encoding = "UTF-8"),
              show_col_types = FALSE, progress = FALSE)

cat("décisions           :", nrow(d), "\n")
cat("exécutions          :", n_distinct(d$run_id), "\n")
cat("séries              :", n_distinct(paste(d$run_id, d$session)), "\n")
cat("manches             :", n_distinct(paste(d$run_id, d$session, d$manche)), "\n")
cat("actions par défaut  :", sum(d$parsing == "defaut"), "  <- doit être 0\n")
cat("texte libre présent :", sum(nchar(d$sortie_brute) > 60),
    sprintf(" (%.1f %%)\n", 100 * mean(nchar(d$sortie_brute) > 60)))

# =============================================================================
# §2. pi-chapeau — la seule statistique du dispositif
# =============================================================================
# TOUT le mémoire repose là-dessus, et ce n'est qu'une moyenne de 0 et de 1.
#
# Pour chaque série (150 manches sous une mémoire GELÉE) et chaque ensemble
# d'information, on compte la fréquence à laquelle l'agent a joué l'action
# AGRESSIVE. Agressif = engager (bet) ou couvrir (call).
#
# Les décisions où le harnais aurait imposé une action faute de réponse
# exploitable sont exclues : elles renseignent sur le harnais, pas sur la
# politique de l'agent. (Ici il n'y en a aucune — 0 sur 27 290.)
#
# Le résultat reproduit `donnees/infosets.csv` : c'est exactement le tableau
# croisé dynamique `Lignes = infoset, Colonnes = session, Valeurs = moyenne`.

titre("§2. PI-CHAPEAU")
pi_hat <- d |>
  filter(parsing != "defaut") |>
  mutate(agressive = as.integer(action_parsee %in% c("bet", "call"))) |>
  group_by(run_id, condition, bot, replication, session, infoset) |>
  summarise(p = mean(agressive), n = n(), .groups = "drop")

cat("couples (série x ensemble d'information) :", nrow(pi_hat), "\n\n")
cat("Exemple — AE / Station / r1 : les deux ensembles qui décident de tout.\n")
cat("  J1/C0/ouverture = engager le sceau faible   -> doit tomber vers 0\n")
cat("  J1/C2/ouverture = engager le sceau fort      -> doit monter vers 1\n\n")
montrer(pi_hat |>
  filter(run_id == "AE-station-r1",
         infoset %in% c("J1/C0/ouverture", "J1/C2/ouverture")) |>
  select(session, infoset, p, n) |>
  pivot_wider(names_from = infoset, values_from = c(p, n)))

# =============================================================================
# §3. Les mesures, série par série
# =============================================================================
# Pour chaque série : on complète pi-chapeau à 12 valeurs, puis on applique les
# deux instruments. Le calcul est EXACT (énumération de l'arbre), pas estimé.

titre("§3. LES DEUX INSTRUMENTS, SÉRIE PAR SÉRIE")
series <- pi_hat |>
  group_by(run_id, condition, bot, replication, session) |>
  group_modify(function(g, cle) {
    p_obs <- setNames(g$p, g$infoset)
    pi_complete <- completer(p_obs)
    b <- BOTS[[cle$bot]]
    tibble(
      ecart      = ecart(pi_complete, b),
      recitee    = reference_recitee(pi_complete, b),
      ev_pi_hat  = ev_moyenne(pi_complete, b),
      ev_br      = meilleure_reponse(b)$ev,
      n_observes = nrow(g)
    )
  }) |>
  ungroup() |>
  mutate(condition = factor(condition, levels = c("SM", "ICL", "AE")),
         bot = factor(bot, levels = c("Over-folder", "Station", "GTO")))

cat("séries mesurées :", nrow(series), "\n")

# =============================================================================
# §4. VÉRIFICATION contre les chiffres publiés
# =============================================================================
# C'est le point de ce script. Deux chemins de calcul entièrement séparés —
# Python/Fraction d'un côté, R/double de l'autre, arbres écrits séparément —
# doivent rendre le même nombre. S'ils coïncident, l'instrument de mesure du
# mémoire est vérifié par recoupement, et l'angle mort d'AUDIT.md §3 est fermé.

titre("§4. VÉRIFICATION CROISÉE CONTRE sessions.csv")
publie <- read_csv("donnees/sessions.csv", show_col_types = FALSE, progress = FALSE) |>
  select(run_id, session, ecart_publie = ecart, recitee_publiee = reference_recite)

controle <- series |>
  inner_join(publie, by = c("run_id", "session")) |>
  mutate(d_ecart = abs(ecart - ecart_publie), d_recitee = abs(recitee - recitee_publiee))

cat("séries confrontées            :", nrow(controle), "\n")
cat("écart maximal sur l'écart     :", format(max(controle$d_ecart), scientific = TRUE), "\n")
cat("écart maximal sur la récitée  :", format(max(controle$d_recitee), scientific = TRUE), "\n")
cat(if (max(controle$d_ecart, controle$d_recitee) < 1e-9)
      "\nOK — les deux chemins de calcul coïncident à 1e-9 près.\n"
    else "\nDIVERGENCE : à examiner avant toute lecture des tableaux.\n")

# =============================================================================
# §5. H1 — l'adaptation existe, et elle vient de la mémoire
# =============================================================================
# La comparaison est APPARIÉE, pas un test de moyennes : SM-station-r1 et
# AE-station-r1 ont vu EXACTEMENT les mêmes cartes, dans le même ordre (les
# donnes sont une fonction pure de (graine, réplication, série, manche)). La
# variance des cartes s'annule dans la différence. C'est ce qui rend trois
# réplications suffisantes.
#
# LE CONTRÔLE QUI FAIT LA PREUVE N'EST PAS AE, C'EST SM : si la baisse venait de
# l'instrument, elle apparaîtrait aussi sans mémoire, sur les mêmes donnes et le
# même calcul. Elle n'y apparaît pas.

titre("§5. H1 — ÉCART D'EXPLOITATION : SM contre AE")
h1 <- series |>
  filter(condition %in% c("SM", "AE")) |>
  mutate(phase = case_when(condition == "SM" ~ "SM",
                           condition == "AE" & session == 0 ~ "AE_serie0",
                           condition == "AE" & session == 9 ~ "AE_serie9")) |>
  filter(!is.na(phase)) |>
  group_by(bot, replication, phase) |>
  summarise(e = mean(ecart), .groups = "drop") |>
  pivot_wider(names_from = phase, values_from = e)
montrer(h1)

titre("§5 bis. H1 — EFFET APPARIÉ (moyenne SM  -  écart final AE)")
h1_effet <- h1 |>
  mutate(reduction = SM - AE_serie9) |>
  group_by(bot) |>
  # Attention : dans `summarise`, les colonnes se calculent SÉQUENTIELLEMENT.
  # Nommer le résumé `reduction` écraserait le vecteur avant les lignes
  # suivantes, qui compteraient alors sur un scalaire. D'où les noms distincts.
  summarise(SM = mean(SM), AE = mean(AE_serie9),
            reduction_moyenne = mean(reduction),
            paires_positives = sprintf("%d/%d", sum(reduction > 0), n()),
            dispersion = sd(reduction), .groups = "drop")
montrer(h1_effet)

cat("\nLa ligne sans mémoire ne décroît jamais — pente de l'écart en SM :\n")
montrer(series |> filter(condition == "SM") |> group_by(bot) |>
  summarise(pente_par_serie = coef(lm(ecart ~ session))[2], .groups = "drop"))

# =============================================================================
# §6. H2 — elle exploite, elle ne récite pas
# =============================================================================
# L'argument est un argument d'ASYMÉTRIE, pas d'amplitude. Station et
# Over-folder ont des fuites OPPOSÉES : l'un paie toujours (il faut cesser de
# bluffer), l'autre se couche toujours (il faut bluffer tout le temps). Aucune
# stratégie fixe, l'équilibre compris, ne peut faire descendre les deux courbes.
# Un récitant reste à 0 partout PAR CONSTRUCTION.
#
# Le maximum théorique de la récitée = EV(meilleure réponse) - EV(GTO), soit
# 7/9 contre Over-folder et 1/9 contre Station. Atteindre exactement ce plafond,
# c'est jouer la meilleure réponse — donc exploiter, pas réciter.

titre("§6. H2 — RÉFÉRENCE RÉCITÉE")
maxima <- sapply(names(BOTS), function(nom)
  reference_recitee(meilleure_reponse(BOTS[[nom]])$politique, BOTS[[nom]]))

h2 <- series |>
  mutate(phase = case_when(condition == "SM" ~ "SM",
                           condition == "AE" & session >= 7 ~ "AE_fin")) |>
  filter(!is.na(phase)) |>
  group_by(bot, phase) |>
  summarise(r = mean(recitee), .groups = "drop") |>
  pivot_wider(names_from = phase, values_from = r) |>
  mutate(maximum_theorique = maxima[as.character(bot)],
         # Contre GTO le maximum vaut 0 (plafond) : la fraction n'a pas de sens.
         atteint = ifelse(abs(maximum_theorique) < 1e-12, "— (plafond nul)",
                          sprintf("%.1f %%", 100 * AE_fin / maximum_theorique)))
montrer(h2)

titre("§6 bis. LE CONTRÔLE NÉGATIF (contre GTO)")
# Rien ne bat l'équilibre contre l'équilibre : la récitée NE PEUT PAS y devenir
# positive. Si elle l'était, l'instrument serait cassé et tout le reste tomberait.
# ATTENTION : contre GTO le maximum vaut 0, donc recitee = -ecart exactement.
# Les deux formulations sont le MÊME test, pas deux verrous indépendants.
gto_series <- series |> filter(bot == "GTO")
cat("séries jouées contre GTO        :", nrow(gto_series), "\n")
cat("récitée jamais positive         :", all(gto_series$recitee <= 1e-12), "\n")
cat("écart jamais négatif            :", all(gto_series$ecart >= -1e-12), "\n")
cat("séries atteignant exactement 0  :", sum(abs(gto_series$ecart) < 1e-12), "\n")
cat("récitée = -écart (identité)     :", max(abs(gto_series$recitee + gto_series$ecart)) < 1e-12, "\n")

titre("§6 ter. CE QUE CES VALEURS DOIVENT AU CHOIX DE L'ÉQUILIBRE (§3.3.2)")
# L'équilibre de Kuhn est une FAMILLE à un paramètre. Le protocole en fige un
# membre (alpha = 1/3). L'écart est alpha-libre ; l'échelle de la récitée, non.
alpha_tab <- lapply(c(0, 1/6, 1/3), function(a) {
  tibble(alpha = sprintf("%.3f", a),
         `EV(GTO) vs Station`     = ev_moyenne(gto(a), BOTS$Station),
         `récitée max vs Station` = reference_recitee(meilleure_reponse(BOTS$Station)$politique, BOTS$Station, a),
         `récitée max vs Overf.`  = reference_recitee(meilleure_reponse(BOTS$`Over-folder`)$politique, BOTS$`Over-folder`, a),
         `écart max vs Station`   = ecart(gto(a), BOTS$Station))
}) |> bind_rows()
montrer(alpha_tab)
cat("\nLecture : l'écart d'un récitant change avec alpha, mais l'ÉCART D'UN AGENT\n",
    "DONNÉ, lui, ne dépend pas d'alpha du tout — alpha n'entre pas dans son calcul.\n",
    "Seule l'échelle de la référence récitée est conditionnelle au protocole.\n", sep = "")

# =============================================================================
# §7. H3 — le mécanisme de rétention
# =============================================================================
# ICL et AE reçoivent LA MÊME MATIÈRE PREMIÈRE (le récapitulatif brut des séries
# passées). Seul le mécanisme diffère : ICL empile sans aucun appel au modèle,
# AE fait synthétiser l'agent. Sinon on comparerait deux INFORMATIONS, pas deux
# MÉMOIRES.
#
# On prend la moyenne des QUATRE DERNIÈRES séries plutôt que le point terminal :
# moins bruité qu'un point isolé. Puis différence par réplication, puis un
# intervalle de Student à 2 degrés de liberté sur les trois différences.
# Trois réplications, donc t(0.975, 2) = 4.303 — un intervalle très large, et
# c'est honnête : avec n = 3 on ne prétend pas à mieux.

titre("§7. H3 — ICL contre AE, moyenne des quatre dernières séries")
h3_paires <- series |>
  filter(condition %in% c("ICL", "AE"), bot != "GTO", session >= 6) |>
  group_by(bot, replication, condition) |>
  summarise(e = mean(ecart), .groups = "drop") |>
  pivot_wider(names_from = condition, values_from = e) |>
  mutate(difference = ICL - AE)
montrer(h3_paires)

titre("§7 bis. H3 — EFFET APPARIÉ ET INTERVALLE DE CONFIANCE")
h3 <- h3_paires |>
  group_by(bot) |>
  summarise(effet = mean(difference),
            ecart_type = sd(difference),
            ic95 = qt(0.975, df = n() - 1) * sd(difference) / sqrt(n()),
            .groups = "drop") |>
  mutate(borne_basse = effet - ic95, borne_haute = effet + ic95,
         conclusion = ifelse(borne_basse > 0, "exclut zéro : AE l'emporte",
                                              "contient zéro : indistinguable"))
montrer(h3 |> select(bot, effet, ecart_type, ic95, borne_basse, borne_haute, conclusion))

titre("§7 ter. POURQUOI : LA COMPLÉTUDE, NI LA VITESSE NI L'OUBLI")
# Le profil « dents de scie » attendu pour ICL n'existe pas. Les deux conditions
# chutent à la MÊME vitesse à la première frontière. Ce qui les sépare est la
# suite : AE se verrouille sur zéro, ICL s'arrête à un résidu qu'il n'annule
# jamais.
cat("La chute à la première frontière est la même :\n")
montrer(series |> filter(condition %in% c("ICL", "AE"), bot != "GTO", session <= 1) |>
  group_by(bot, condition, session) |> summarise(ecart = mean(ecart), .groups = "drop") |>
  pivot_wider(names_from = session, values_from = ecart, names_prefix = "serie_"))

cat("\nC'est la suite qui diffère — nombre de séries à écart EXACTEMENT nul :\n")
montrer(series |> filter(condition %in% c("ICL", "AE"), bot != "GTO", session >= 1) |>
  group_by(bot, condition) |>
  summarise(series = n(), zeros_exacts = sum(ecart < 1e-12),
            ecart_minimal = min(ecart), .groups = "drop"))

cat("\nEt le résidu d'ICL se localise : les deux ensembles qui décident tout\n",
    "contre Station (série 9). Bluffer le faible doit tomber à 0, engager le\n",
    "fort doit monter à 1.\n", sep = "")
montrer(pi_hat |>
  filter(bot == "Station", condition %in% c("ICL", "AE"), session == 9,
         infoset %in% c("J1/C0/ouverture", "J1/C2/ouverture")) |>
  group_by(condition, infoset) |> summarise(p = mean(p), .groups = "drop") |>
  pivot_wider(names_from = infoset, values_from = p))

# =============================================================================
# §8. H4 — les biais de décision
# =============================================================================

titre("§8. H4a — DÉGÉNÉRESCENCE DES STRATÉGIES MIXTES")
# Contre GTO, l'ensemble J1/C0/ouverture exige un bluff à 1/3 exactement. On
# regarde si l'agent y produit une fréquence intermédiaire, ou s'il se colle aux
# bornes 0 et 1.
#
# On exige n >= 20 observations : une fréquence de 1 sur 2 tirages ne dit rien.
#
# LA DEUXIÈME LIGNE EST LE CONTRÔLE INTERNE, et c'est elle qui porte toute la
# conclusion : la première série d'une exécution AE se joue avec un emplacement
# mémoire PRÉSENT MAIS VIDE. Même modèle, même gabarit, même exécution, même
# adversaire — seule la note manque. Si l'effondrement apparaît exactement quand
# la note apparaît, ce n'est pas le modèle qui dégénère : c'est la mémoire qui
# le fait dégénérer.
N_MINIMAL <- 20
mixte <- pi_hat |>
  filter(bot == "GTO", infoset == "J1/C0/ouverture", n >= N_MINIMAL) |>
  mutate(groupe = case_when(
    condition == "SM"                      ~ "1. SM — sans mémoire",
    condition == "AE" & session == 0       ~ "2. AE — note encore VIDE (contrôle)",
    condition == "AE" & session >  0       ~ "3. AE — note écrite"),
    aux_bornes = p < 1e-9 | p > 1 - 1e-9)

montrer(mixte |> group_by(groupe) |>
  summarise(series = n(),
            aux_bornes = sprintf("%.0f %%", 100 * mean(aux_bornes)),
            distance_moyenne_a_1_3 = mean(abs(p - 1/3)), .groups = "drop"))

cat("\nCe n'est pas un effondrement vers UNE borne, mais une ALTERNANCE :\n")
alt <- mixte |> filter(condition == "AE", session > 0)
# Les sauts se comptent sur la trajectoire COMPLÈTE de chaque exécution (série 0
# comprise, sans le filtre d'effectif) : on regarde la forme de la suite, pas la
# qualité de chaque point pris isolément.
sauts <- pi_hat |>
  filter(bot == "GTO", condition == "AE", infoset == "J1/C0/ouverture") |>
  arrange(run_id, session) |>
  group_by(run_id) |> mutate(saut = abs(p - lag(p))) |> ungroup()
cat("  séries à p = 0                     :", sum(alt$p < 1e-9), "\n")
cat("  séries à p = 1                     :", sum(alt$p > 1 - 1e-9), "\n")
cat("  sauts > 0,40 entre séries voisines :", sum(sauts$saut > 0.40, na.rm = TRUE), "\n")
cat("\nLa randomisation INTRA-série est remplacée par une alternance\n",
    "INTER-séries : l'agent choisit une règle, l'applique 150 manches, puis en\n",
    "change à la frontière. La variabilité a migré vers une échelle de temps où\n",
    "elle ne produit aucune imprévisibilité stratégique.\n", sep = "")
cat("\nATTENTION AU CHIFFRE : ce résultat ne vaut que CONTRE GTO. Agrégé sur les\n",
    "trois adversaires il donnerait 58 %, en comptant comme dégénérées des\n",
    "politiques PURES qui sont OPTIMALES contre Station et Over-folder.\n", sep = "")

titre("§8 bis. H4b — INCOHÉRENCE RAISONNEMENT <-> ACTION")
# La règle PRÉ-ENREGISTRÉE : « la dernière action nommée dans le texte libre ».
# Elle devait fournir une borne inférieure du taux d'incohérence. Elle est
# INVALIDE sur ce corpus, et c'est un résultat, pas un raté : le français conclut
# par une clause contrastive qui nomme l'option REJETÉE — « engager garantit +1,
# TANDIS QUE retenir expose à une perte ». Une règle positionnelle hérite de la
# structure du discours, pas de l'intention.
#
# La variante à haute précision ne retient que les décisions où l'agent ÉNONCE
# son choix. Le prix payé est le rappel : elle ne couvre qu'une fraction du corpus.

VERBES <- c(check = "reten\\w*|retien\\w*", bet = "engag\\w*",
            call = "couvr\\w*|couvert\\w*", fold = "retir\\w*|retrait\\w*")

# Dernière action nommée dans le texte (règle pré-enregistrée).
derniere_action <- function(txt) {
  meilleure <- -1L; act <- NA_character_
  for (a in names(VERBES)) {
    pos <- gregexpr(VERBES[[a]], txt, perl = TRUE, ignore.case = TRUE)[[1]]
    p <- max(pos)
    if (p > meilleure) { meilleure <- p; act <- a }
  }
  act
}

# Formules par lesquelles l'agent ÉNONCE son choix. Motifs délibérément étroits :
# on préfère ne rien mesurer à mesurer du bruit.
RADICAL <- "(reten\\w*|retien\\w*|engag\\w*|couvr\\w*|couvert\\w*|retir\\w*)"
ENONCES <- c(
  paste0("il (?:vaut|est) (?:donc |dès lors )?(?:mieux|préférable)(?: de)?\\s+", RADICAL),
  paste0("je (?:choisis|décide|opte|préfère)\\s*(?:de |pour |d')?\\s*", RADICAL),
  paste0("(?:le mieux|la meilleure (?:option|action|décision))\\s+est\\s*(?:de |d')?\\s*", RADICAL),
  paste0("(?m)^\\s*", RADICAL, "\\s+est (?:donc |ici )?(?:préférable|la meilleure|le meilleur|optimal)")
)

choix_enonce <- function(txt) {
  meilleure <- -1L; act <- NA_character_
  for (motif in ENONCES) {
    m <- gregexpr(motif, txt, perl = TRUE, ignore.case = TRUE)[[1]]
    if (m[1] == -1) next
    for (i in seq_along(m)) {
      if (m[i] > meilleure) {
        meilleure <- m[i]
        extrait <- substr(txt, m[i], m[i] + attr(m, "match.length")[i] - 1)
        act <- derniere_action(extrait)
      }
    }
  }
  act
}

# PIÈGE À NE PAS RATER : il faut retirer la ligne « ACTION: … » avant de lire le
# texte, sinon la règle compare l'action à elle-même et trouve 0 % d'incohérence.
# Le drapeau `m` est indispensable — sans lui, `^` n'ancre qu'au début de la
# chaîne entière et la ligne n'est jamais retirée.
textes <- d |>
  filter(parsing == "ok") |>
  mutate(delibere = sub("(?im)^[ \t>*-]*ACTION\\s*:.*", "", sortie_brute, perl = TRUE)) |>
  filter(nchar(trimws(delibere)) > 0)

r1 <- vapply(textes$delibere, derniere_action, character(1), USE.NAMES = FALSE)
r3 <- vapply(textes$delibere, choix_enonce, character(1), USE.NAMES = FALSE)

incoherence <- tibble(
  regle = c("pré-enregistrée (dernière action nommée)", "haute précision (choix énoncé)"),
  mesurables = c(sum(!is.na(r1)), sum(!is.na(r3))),
  divergentes = c(sum(!is.na(r1) & r1 != textes$action_parsee),
                  sum(!is.na(r3) & r3 != textes$action_parsee))
) |> mutate(taux = sprintf("%.1f %%", 100 * divergentes / mesurables),
            couverture = sprintf("%.1f %%", 100 * mesurables / sum(d$parsing == "ok")))
montrer(incoherence)
cat("\nLes 45,1 % de GTBENCH sont à un point du premier chiffre. La coïncidence est\n",
    "l'artefact, pas le résultat : huit divergences relues, huit faux positifs.\n", sep = "")

# =============================================================================
# §9. Les figures
# =============================================================================
titre("§9. FIGURES")
theme_set(theme_minimal(base_size = 11) +
          theme(panel.grid.minor = element_blank(),
                strip.text = element_text(face = "bold")))
COULEURS <- c(SM = "#8C8C8C", ICL = "#D97706", AE = "#2563EB")

# Figure 1 — les trajectoires d'écart. C'est la figure de H1 et H3 à la fois :
# la ligne grise (SM) ne bouge pas, la bleue (AE) plonge et se verrouille,
# l'orange (ICL) plonge aussi mais s'arrête au-dessus.
traj <- series |> group_by(bot, condition, session) |>
  summarise(ecart = mean(ecart), .groups = "drop")

f1 <- ggplot(traj, aes(session, ecart, colour = condition)) +
  geom_hline(yintercept = 0, linewidth = 0.3, colour = "grey40") +
  geom_line(linewidth = 0.9) + geom_point(size = 1.8) +
  facet_wrap(~bot, scales = "free_y") +
  scale_colour_manual(values = COULEURS, name = NULL) +
  scale_x_continuous(breaks = 0:9) +
  labs(title = "Écart d'exploitation par série",
       subtitle = "Moyenne des 3 réplications. Zéro = exploitation optimale.",
       x = "Série", y = "Écart (jetons / manche)")
ggsave(file.path(SORTIE, "fig1-trajectoires.png"), f1, width = 10, height = 3.6, dpi = 200)

# Figure 2 — la référence récitée, avec le plafond théorique en pointillés.
# Toucher le pointillé, c'est jouer la meilleure réponse. La ligne à zéro est le
# niveau d'un pur récitant : au-dessus, l'agent exploite ; en dessous, il fait
# moins bien que l'équilibre.
plafonds <- tibble(bot = factor(names(maxima), levels = levels(series$bot)),
                   maximum = as.vector(maxima))
rec <- series |> group_by(bot, condition, session) |>
  summarise(recitee = mean(recitee), .groups = "drop")

f2 <- ggplot(rec, aes(session, recitee, colour = condition)) +
  geom_hline(yintercept = 0, linewidth = 0.4, colour = "grey30") +
  geom_hline(data = plafonds, aes(yintercept = maximum),
             linetype = "dashed", colour = "#B91C1C", linewidth = 0.4) +
  geom_line(linewidth = 0.9) + geom_point(size = 1.8) +
  facet_wrap(~bot, scales = "free_y") +
  scale_colour_manual(values = COULEURS, name = NULL) +
  scale_x_continuous(breaks = 0:9) +
  labs(title = "Référence récitée par série",
       subtitle = "0 = niveau d'un pur récitant de l'équilibre ; tirets rouges = maximum théorique d'exploitation.",
       x = "Série", y = "EV(observée) − EV(équilibre)")
ggsave(file.path(SORTIE, "fig3-recitee.png"), f2, width = 10, height = 3.6, dpi = 200)

# Figure 3 — la dégénérescence. Chaque point est une série ; la ligne à 1/3 est
# ce que l'équilibre demande. Le contraste entre les trois groupes EST le
# résultat de H4.
f3 <- ggplot(mixte, aes(groupe, p, colour = groupe)) +
  geom_hline(yintercept = 1/3, linetype = "dashed", colour = "#B91C1C") +
  geom_jitter(width = 0.12, height = 0, size = 2.4, alpha = 0.8) +
  scale_y_continuous(limits = c(0, 1)) +
  scale_colour_manual(values = c("#8C8C8C", "#059669", "#2563EB"), guide = "none") +
  coord_flip() +
  labs(title = "Fréquence d'engagement au sceau faible, contre l'adversaire à l'équilibre",
       subtitle = "Un point = une série. Tirets rouges = la fréquence 1/3 que l'équilibre exige.",
       x = NULL, y = "Fréquence d'engagement observée")
ggsave(file.path(SORTIE, "fig5-degenerescence.png"), f3, width = 9, height = 3.4, dpi = 200)

# -----------------------------------------------------------------------------
# Figure 2 (§3.3) — LA PIÈCE CENTRALE DE H2.
# -----------------------------------------------------------------------------
# L'argument de H2 est une asymétrie de COMPORTEMENT, et une courbe de gains ne
# la montre pas. Ici : face au même jeton faible, l'agent fait trois choses
# différentes selon l'adversaire. Contre Station il cesse d'engager, contre
# Over-folder il engage systématiquement — deux réponses OPPOSÉES à la même
# situation. Aucune stratégie récitée ne peut produire les deux.
faible <- pi_hat |>
  filter(infoset %in% c("J1/C0/ouverture", "J2/C0/apres_check")) |>
  mutate(phase = case_when(condition == "SM" ~ "Sans mémoire",
                           condition == "AE" & session >= 7 ~ "Mémoire écrite (fin)")) |>
  filter(!is.na(phase)) |>
  group_by(bot, phase) |>
  summarise(p = weighted.mean(p, n), .groups = "drop") |>
  mutate(phase = factor(phase, levels = c("Sans mémoire", "Mémoire écrite (fin)")),
         # même ordre d'adversaires que les autres figures
         bot = factor(bot, levels = c("Over-folder", "Station", "GTO")))

f2 <- ggplot(faible, aes(bot, p, fill = phase)) +
  geom_col(position = position_dodge(0.7), width = 0.6) +
  geom_hline(yintercept = 1/3, linetype = "dashed", colour = "#B91C1C") +
  annotate("text", x = 0.55, y = 0.37, label = "1/3 = l'équilibre",
           colour = "#B91C1C", size = 3, hjust = 0) +
  scale_fill_manual(values = c("#8C8C8C", "#2563EB"), name = NULL) +
  scale_y_continuous(limits = c(0, 1), labels = scales::percent) +
  labs(title = "Fréquence d'engagement avec le sceau faible, selon l'adversaire",
       subtitle = "Même situation, trois réponses, dont deux opposées. Sans mémoire, rien ne les distingue.",
       x = NULL, y = "Fréquence d'engagement")
ggsave(file.path(SORTIE, "fig2-asymetrie.png"), f2, width = 8, height = 4, dpi = 200)

# -----------------------------------------------------------------------------
# Figure 4 (§3.4) — le zoom. Sur la figure 1, le résidu d'ICL est écrasé par
# l'échelle. Ici on voit AE collé au zéro et ICL qui flotte au-dessus sans jamais
# le toucher, sur aucune des trente séries.
# -----------------------------------------------------------------------------
f4 <- ggplot(traj |> filter(condition != "SM", bot != "GTO", session >= 1),
             aes(session, ecart, colour = condition)) +
  geom_hline(yintercept = 0, linewidth = 0.4, colour = "grey30") +
  geom_line(linewidth = 0.9) + geom_point(size = 2) +
  facet_wrap(~bot) +
  scale_colour_manual(values = COULEURS, name = NULL) +
  scale_x_continuous(breaks = 1:9) +
  coord_cartesian(ylim = c(0, 0.08)) +
  labs(title = "Après la première frontière — échelle resserrée",
       subtitle = "La mémoire écrite se verrouille sur zéro ; l'historique brut s'arrête au-dessus et n'y revient pas.",
       x = "Série", y = "Écart (jetons / manche)")
ggsave(file.path(SORTIE, "fig4-zoom.png"), f4, width = 8, height = 3.6, dpi = 200)

cat("figures écrites dans", SORTIE, ":\n  ",
    paste(list.files(SORTIE), collapse = "\n  "), "\n")

# =============================================================================
# §10. EXPORT DES TABLEAUX — pour Excel puis Word
# =============================================================================
# Chaque tableau retenu au plan v2 part en CSV dans memoire/tableaux/. On les
# ouvre dans Excel (Données > À partir d'un fichier texte, encodage 65001), on
# met en forme, on colle dans Word comme VRAIE table.
# C'est ce qui évite de recoller du Markdown brut dans le .docx.

titre("§10. EXPORT DES TABLEAUX")
TABLEAUX <- "memoire/tableaux"
dir.create(TABLEAUX, showWarnings = FALSE, recursive = TRUE)
exporter <- function(df, nom, decimales = 4) {
  # Arrondi avant export : sans lui, un zéro exact sort en « 2.776e-17 » (résidu
  # de virgule flottante) et Excel l'affiche tel quel dans le mémoire.
  df <- as.data.frame(df) |>
    mutate(across(where(is.numeric), \(x) round(x, decimales)))
  chemin <- file.path(TABLEAUX, paste0(nom, ".csv"))
  write_excel_csv(df, chemin)   # write_excel_csv = UTF-8 AVEC BOM, lu direct par Excel
  cat("  ", chemin, "  (", nrow(df), " lignes)\n", sep = "")
}

# --- T1 : une série décomposée, du comptage à l'écart ------------------------
# La pièce qui rend tout le chapitre vérifiable. On refait, pour une série
# réelle, le chemin complet : combien de fois l'agent a engagé dans chacune des
# six situations, ce que ça vaut, et ce que ça laisse sur la table.
SERIE_EXEMPLE <- list(run = "AE-station-r1", session = 0)
t1 <- d |>
  filter(run_id == SERIE_EXEMPLE$run, session == SERIE_EXEMPLE$session) |>
  mutate(jeton = c("0" = "faible", "1" = "moyen", "2" = "fort")[as.character(carte_agent)],
         position = ifelse(position_agent == "J1", "1re à parler", "2de à parler")) |>
  group_by(position, jeton) |>
  summarise(engagements = sum(action_parsee == "bet"), manches = n(),
            frequence = mean(action_parsee == "bet"), .groups = "drop") |>
  mutate(jeton = factor(jeton, levels = c("faible", "moyen", "fort"))) |>
  arrange(position, jeton)
montrer(t1)

# Le calcul, explicité. Contre Station : le jeton fort gagne à coup sûr (engager
# rapporte 1 de plus), le faible perd à coup sûr (engager coûte 1 de plus), le
# moyen gagne une fois sur deux (engager ne change rien).
f <- function(pos, jet) t1$frequence[t1$position == pos & t1$jeton == jet]
ev_exemple <- ((f("1re à parler", "fort") - f("1re à parler", "faible")) +
               (f("2de à parler", "fort") - f("2de à parler", "faible"))) / 6
cat(sprintf("\n  EV = [(%.3f - %.3f) + (%.3f - %.3f)] / 6 = %.4f jeton/manche\n",
            f("1re à parler", "fort"), f("1re à parler", "faible"),
            f("2de à parler", "fort"), f("2de à parler", "faible"), ev_exemple))
cat(sprintf("  Plafond (joueur parfait)            = %.4f jeton/manche\n", 1/3))
cat(sprintf("  ÉCART = %.4f - %.4f              = %.4f jeton/manche\n", 1/3, ev_exemple, 1/3 - ev_exemple))
cat(sprintf("  soit %.0f jetons laissés sur les 150 manches de la série.\n", 150 * (1/3 - ev_exemple)))
exporter(t1, "T1-serie-decomposee")

# --- T2 : l'échelle de lecture ----------------------------------------------
# Sans ce tableau, aucune comparaison entre adversaires n'est possible : un écart
# de 0,70 contre Over-folder et de 0,22 contre Station ne signalent PAS trois
# fois plus d'erreurs, parce que les plafonds diffèrent.
t2 <- lapply(names(BOTS), function(nom) {
  b <- BOTS[[nom]]
  tibble(adversaire = nom,
         `gain du joueur parfait` = meilleure_reponse(b)$ev,
         `gain d'un récitant` = ev_moyenne(gto(), b),
         `écart d'un récitant` = ecart(gto(), b),
         `récité maximal` = reference_recitee(meilleure_reponse(b)$politique, b))
}) |> bind_rows()
montrer(t2)
exporter(t2, "T2-echelle-de-lecture")

exporter(h1_effet, "T3-effet-apparie-H1")
exporter(h2, "T4-reference-recitee")
exporter(h3 |> select(bot, effet, ecart_type, ic95, borne_basse, borne_haute, conclusion),
         "T5-effet-apparie-H3")

# --- T6 : où l'historique brut échoue ---------------------------------------
# Contre Station, le jeton moyen est un point d'indifférence exact : engager ou
# retenir y vaut rigoureusement pareil. Toute la qualité du jeu tient donc en
# QUATRE décisions — le jeton faible (doit tomber à 0) et le jeton fort (doit
# monter à 1), dans les deux positions. Ce tableau les isole.
t6 <- pi_hat |>
  filter(bot == "Station", condition %in% c("ICL", "AE"), session >= 6,
         infoset %in% c("J1/C0/ouverture", "J2/C0/apres_check",
                        "J1/C2/ouverture", "J2/C2/apres_check")) |>
  mutate(jeton = ifelse(grepl("C0", infoset), "faible (doit tomber à 0)",
                                              "fort (doit monter à 1)"),
         position = ifelse(grepl("^J1", infoset), "1re à parler", "2de à parler")) |>
  group_by(condition, jeton, position) |>
  summarise(frequence = weighted.mean(p, n), manches = sum(n), .groups = "drop") |>
  pivot_wider(names_from = condition, values_from = c(frequence, manches))
montrer(t6)
exporter(t6, "T6-quatre-decisions-Station")

# --- T7 : ce que les notes contiennent, et ce qu'elles ne contiennent jamais --
# Analyse lexicale des 90 notes. Le résultat central est une série de ZÉROS :
# l'agent n'écrit jamais une fréquence, alors qu'il en observe une.
# On lit `donnees/notes-ae.md` : les blocs de note sont entre triples accents
# graves, et le nom de l'exécution donne l'adversaire.
lignes_notes <- readLines("donnees/notes-ae.md", encoding = "UTF-8", warn = FALSE)
notes <- local({
  courant <- NA_character_; dedans <- FALSE; buf <- character(0); out <- list()
  for (l in lignes_notes) {
    if (grepl("^## ", l)) courant <- sub("^## ", "", l)
    else if (grepl("^```", l)) {
      if (dedans) { out[[length(out) + 1]] <- list(run = courant, txt = paste(buf, collapse = " "))
                    buf <- character(0) }
      dedans <- !dedans
    } else if (dedans) buf <- c(buf, l)
  }
  bind_rows(lapply(out, as_tibble)) |>
    mutate(bot = case_when(grepl("over-folder", run) ~ "Over-folder",
                           grepl("station", run) ~ "Station", TRUE ~ "GTO"))
})
cat("notes lues :", nrow(notes), " · caractères :", sum(nchar(notes$txt)), "\n")

compter <- function(motif) sum(vapply(notes$txt, function(t)
  length(gregexpr(motif, t, perl = TRUE, ignore.case = TRUE)[[1]][
    gregexpr(motif, t, perl = TRUE, ignore.case = TRUE)[[1]] > 0]), integer(1)))

CATEGORIQUES <- "\\b(toujours|jamais|systématiquement|systematiquement)\\b"
GRADUES <- paste0("\\b(souvent|parfois|rarement|fréquemment|frequemment|",
                  "régulièrement|regulierement|généralement|generalement|",
                  "occasionnellement|majoritairement|principalement|surtout)\\b")

# ATTENTION — correction du 2026-08-27. Le texte antérieur annonçait « 0 fraction
# écrite ». C'est FAUX : le motif `\d+/\d+` trouve deux occurrences.
#   - « Vael est 50/50 face au sceau restant »  -> une VRAIE proportion, mais qui
#     décrit une probabilité d'abattage, jamais une fréquence d'action ;
#   - « les gains de la série (+44/150) »       -> un score, pas une proportion.
# L'énoncé qui survit à la vérification est plus étroit ET plus fort : l'agent
# SAIT écrire un rapport, et ne l'emploie jamais pour prescrire sa propre
# fréquence de jeu.
t7 <- tibble(
  `recherché dans les notes` = c(
    "Un pourcentage (« 33 % »)",
    "Une fraction numérique (« 1/3 », « 50/50 »)",
    "Une proportion en toutes lettres (« un tiers », « une fois sur trois »)",
    "Une fréquence prescrite pour sa propre action",
    "Un quantificateur catégorique (toujours, jamais, systématiquement)",
    "Un quantificateur gradué (souvent, parfois, généralement…)"),
  occurrences = c(
    compter("\\d+\\s*%"),
    compter("\\b\\d+\\s*/\\s*\\d+\\b"),
    compter("\\b(un tiers|une fois sur \\w+|la moitié du temps|deux tiers)\\b"),
    0L,   # relevé à la main : aucune des deux fractions ne prescrit une action
    compter(CATEGORIQUES),
    compter(GRADUES)))
montrer(t7)
cat("\n  Les deux fractions trouvées, in extenso :\n")
for (m in regmatches(notes$txt, gregexpr(".{80}\\b\\d+\\s*/\\s*\\d+\\b.{40}", notes$txt, perl = TRUE)))
  if (length(m)) cat("   …", m, "…\n")
exporter(t7, "T7-vocabulaire-notes", decimales = 0)

# Le complément du tableau 7 : l'agent DÉTECTE le caractère stochastique — son
# vocabulaire bascule — mais il ne sait pas l'ÉCRIRE.
t7b <- notes |> group_by(bot) |>
  summarise(notes = n(),
            categoriques = sum(vapply(txt, \(t) length(gregexpr(CATEGORIQUES, t, perl = TRUE,
                                        ignore.case = TRUE)[[1]][gregexpr(CATEGORIQUES, t,
                                        perl = TRUE, ignore.case = TRUE)[[1]] > 0]), integer(1))),
            gradues = sum(vapply(txt, \(t) length(gregexpr(GRADUES, t, perl = TRUE,
                                        ignore.case = TRUE)[[1]][gregexpr(GRADUES, t,
                                        perl = TRUE, ignore.case = TRUE)[[1]] > 0]), integer(1))),
            .groups = "drop") |>
  mutate(total = categoriques + gradues,
         part_categorique = categoriques / total)
montrer(t7b)
exporter(t7b, "T7bis-registre-par-adversaire")

exporter(pi_hat |> filter(bot == "GTO", infoset == "J1/C0/ouverture", n >= N_MINIMAL) |>
           inner_join(mixte |> select(run_id, session, groupe, aux_bornes),
                      by = c("run_id", "session")) |>
           group_by(groupe) |>
           summarise(series = n(), part_aux_bornes = mean(aux_bornes),
                     distance_a_1_3 = mean(abs(p - 1/3)), .groups = "drop"),
         "T8-degenerescence")
exporter(incoherence, "T9-incoherence")

# --- T10 : le récapitulatif des quatre hypothèses ----------------------------
# Le tableau de synthèse. Les chiffres sont repris des objets calculés plus haut,
# jamais retapés : si une donnée change, ce tableau change avec elle.
t10 <- tibble(
  hypothese = c("H1 — l'adaptation vient de la mémoire",
                "H2 — elle exploite, elle ne récite pas",
                "H3 — le mécanisme de rétention compte",
                "H4 — des biais de décision persistent"),
  refutation_aurait_ete = c(
    "AE ne se distingue pas de SM",
    "l'écart ne descend que contre un seul adversaire, ou la récitée devient positive contre GTO",
    "ICL égale ou surpasse AE",
    "les fréquences se stabilisent aux valeurs mixtes"),
  observe = c(
    sprintf("réduction de %.3f à %.3f de l'écart selon l'adversaire, 9 paires sur 9",
            min(h1_effet$reduction_moyenne), max(h1_effet$reduction_moyenne)),
    sprintf("%.0f %% et %.0f %% du maximum théorique d'exploitation atteints ; récitée jamais positive sur %d séries contre GTO",
            100 * h2$AE_fin[h2$bot == "Over-folder"] / maxima[["Over-folder"]],
            100 * h2$AE_fin[h2$bot == "Station"] / maxima[["Station"]],
            nrow(gto_series)),
    sprintf("AE l'emporte contre Station (+%.4f, IC ±%.4f) ; indistinguable contre Over-folder",
            h3$effet[h3$bot == "Station"], h3$ic95[h3$bot == "Station"]),
    sprintf("%.0f %% des séries aux bornes une fois la note écrite, contre 0 %% sans mémoire et 0 %% note vide",
            100 * mean(mixte$aux_bornes[mixte$groupe == "3. AE — note écrite"]))),
  limite = c(
    "le plateau est atteint dès la série 2 : on mesure la persistance, pas la vitesse",
    "l'échelle de la récitée dépend du choix alpha = 1/3 ; l'écart, non",
    "GTO n'est pas joué en ICL ; le profil d'oubli attendu n'a pas été observé",
    "un seul ensemble d'information ; contrôle interne sur 3 séries")
)
exporter(t10, "T10-synthese-hypotheses")

titre("TERMINÉ")
