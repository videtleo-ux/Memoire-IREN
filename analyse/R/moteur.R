# =============================================================================
# moteur.R — Le jeu de Kuhn, réécrit en R, indépendamment de `src/moteur`.
# =============================================================================
#
# Ce fichier ne lit aucune donnée. Il contient uniquement l'arithmétique du jeu :
# une politique, l'espérance d'une politique contre une autre, la meilleure
# réponse exacte, et les deux instruments de mesure du mémoire.
#
# POURQUOI LE RÉÉCRIRE ALORS QUE `src/moteur` EXISTE ET EST TESTÉ ?
# Parce que les tests T1-T9 vérifient le moteur Python contre une dérivation
# analytique écrite par la même main : une erreur commune aux deux ne s'y verrait
# pas. C'est l'angle mort déclaré au §3 d'AUDIT.md. Un second chemin de calcul,
# dans un autre langage, écrit depuis les règles du jeu et non depuis le code
# Python, referme cet angle mort. Si les deux coïncident au 1e-12, l'instrument
# de mesure du mémoire est vérifié par recoupement.
#
# CONVENTIONS, identiques à celles du dispositif :
#   - trois jetons ordonnés 0 < 1 < 2 (Tor < Vael < Rhun dans le vocabulaire servi
#     à l'agent ; ici on garde les entiers, l'obfuscation est une couche de rendu) ;
#   - J1 ouvre, J2 répond ; l'arène alterne, donc TOUT est moyenné sur les deux
#     positions ;
#   - une POLITIQUE est un vecteur nommé de 12 nombres dans [0,1] : la probabilité
#     de l'action AGRESSIVE à chaque ensemble d'information. Agressif = engager
#     (bet) ou couvrir (call) ; passif = retenir (check) ou se retirer (fold) ;
#   - les 6 donnes ordonnées (carte de J1, carte de J2) sont équiprobables.

# -----------------------------------------------------------------------------
# 1. Les 12 ensembles d'information
# -----------------------------------------------------------------------------
# Un ensemble d'information = « qui je suis, ce que je tiens, ce qui s'est déjà
# dit ». C'est le seul endroit où une politique peut se distinguer.
#
#   J1/Cc/ouverture              J1 parle en premier          -> retenir | engager
#   J1/Cc/face_mise_apres_check  J1 a retenu, J2 a engagé      -> retirer | couvrir
#   J2/Cc/apres_check            J2 après le retenu de J1      -> retenir | engager
#   J2/Cc/face_mise              J2 face à l'engagement de J1  -> retirer | couvrir

INFOSETS <- c(
  paste0("J1/C", 0:2, "/ouverture"),
  paste0("J1/C", 0:2, "/face_mise_apres_check"),
  paste0("J2/C", 0:2, "/apres_check"),
  paste0("J2/C", 0:2, "/face_mise")
)

# Les 6 donnes ordonnées : c1 = carte de J1, c2 = carte de J2, c1 != c2.
DONNES <- expand.grid(c2 = 0:2, c1 = 0:2)
DONNES <- DONNES[DONNES$c1 != DONNES$c2, c("c1", "c2")]
P_DONNE <- 1 / nrow(DONNES) # 1/6

# Gain à l'abattage, du point de vue du premier joueur cité.
# `mise` vaut 1 (personne n'a engagé) ou 2 (un engagement a été couvert).
gain <- function(a, b, mise) if (a > b) mise else -mise

politique <- function(valeurs) {
  stopifnot(setequal(names(valeurs), INFOSETS), all(valeurs >= 0 & valeurs <= 1))
  valeurs[INFOSETS]
}

# -----------------------------------------------------------------------------
# 2. Les politiques de référence
# -----------------------------------------------------------------------------

# L'équilibre de Kuhn est une FAMILLE à un paramètre, alpha dans [0, 1/3].
# Le protocole fige alpha = 1/3 (le membre qui exploite le mieux les deux
# adversaires biaisés : le récitant auquel l'agent est comparé est donc le plus
# fort que la théorie autorise, pas le plus commode).
#
# ATTENTION à la constante contestée (PRD 1 §4, décision D6) : J1 couvre le
# jeton moyen à alpha + 1/3, soit 2/3 à alpha = 1/3 — et NON 1/3, qui est la
# valeur du cas alpha = 0. La vérification est en bas de ce fichier : à 1/3 le
# test `ecart(gto, gto) == 0` échoue, à 2/3 il passe. Le moteur s'auto-vérifie.
gto <- function(alpha = 1 / 3) {
  stopifnot(alpha >= 0, alpha <= 1 / 3)
  politique(c(
    "J1/C0/ouverture" = alpha,     # bluff du jeton faible
    "J1/C1/ouverture" = 0,
    "J1/C2/ouverture" = 3 * alpha, # engagement de valeur
    "J1/C0/face_mise_apres_check" = 0,
    "J1/C1/face_mise_apres_check" = alpha + 1 / 3, # <- la constante tranchée
    "J1/C2/face_mise_apres_check" = 1,
    "J2/C0/apres_check" = 1 / 3,
    "J2/C1/apres_check" = 0,
    "J2/C2/apres_check" = 1,
    "J2/C0/face_mise" = 0,
    "J2/C1/face_mise" = 1 / 3, # constante d'indifférence, indépendante d'alpha
    "J2/C2/face_mise" = 1
  ))
}

# Les deux bots biaisés n'engagent JAMAIS ; ils diffèrent par leur réponse à un
# engagement. Leurs fuites sont exactement opposées, et c'est tout le plan de
# test : aucune stratégie fixe ne peut exploiter les deux.
bot_uniforme <- function(p_ouverture, p_face_mise) {
  v <- setNames(numeric(12), INFOSETS)
  face <- grepl("face_mise", INFOSETS)
  v[face] <- p_face_mise
  v[!face] <- p_ouverture
  politique(v)
}

BOTS <- list(
  "GTO"         = gto(1 / 3),
  "Station"     = bot_uniforme(0, 1), # n'engage jamais, couvre toujours
  "Over-folder" = bot_uniforme(0, 0)  # n'engage jamais, se retire toujours
)

# -----------------------------------------------------------------------------
# 3. L'espérance exacte — aucune simulation
# -----------------------------------------------------------------------------
# Six donnes, un arbre de profondeur trois : on énumère tout. C'est l'argument
# central du choix du jeu de Kuhn (§2.2.1 du chapitre de méthode) — la mesure
# n'a pas d'intervalle de confiance parce qu'elle n'est pas une estimation.

ev_j1_sur_donne <- function(c1, c2, pj1, pj2) {
  p_bet_j1  <- pj1[[paste0("J1/C", c1, "/ouverture")]]
  p_call_j1 <- pj1[[paste0("J1/C", c1, "/face_mise_apres_check")]]
  p_bet_j2  <- pj2[[paste0("J2/C", c2, "/apres_check")]]
  p_call_j2 <- pj2[[paste0("J2/C", c2, "/face_mise")]]

  # J1 engage : J2 se retire (+1) ou couvre (abattage à 2).
  v_mise <- (1 - p_call_j2) * 1 + p_call_j2 * gain(c1, c2, 2)
  # J1 retient puis J2 engage : J1 se retire (-1) ou couvre (abattage à 2).
  v_check_puis_mise <- (1 - p_call_j1) * (-1) + p_call_j1 * gain(c1, c2, 2)
  # J1 retient : J2 retient (abattage à 1) ou engage (branche ci-dessus).
  v_check <- (1 - p_bet_j2) * gain(c1, c2, 1) + p_bet_j2 * v_check_puis_mise

  p_bet_j1 * v_mise + (1 - p_bet_j1) * v_check
}

# EV de J1, moyennée sur les 6 donnes.
ev_j1 <- function(pj1, pj2) {
  P_DONNE * sum(mapply(ev_j1_sur_donne, DONNES$c1, DONNES$c2,
                       MoreArgs = list(pj1 = pj1, pj2 = pj2)))
}

# EV de `a` contre `b`, moyennée sur les deux positions.
# Le jeu est à somme nulle : l'EV de `a` assis en J2 est l'opposé de l'EV de `b`
# assis en J1. Une seule fonction suffit donc.
ev_moyenne <- function(a, b) (ev_j1(a, b) - ev_j1(b, a)) / 2

# -----------------------------------------------------------------------------
# 4. La meilleure réponse exacte
# -----------------------------------------------------------------------------
# Induction arrière sur POIDS CONTREFACTUELS : le poids d'un ensemble
# d'information de l'agent est la probabilité que la nature et l'ADVERSAIRE SEUL
# amènent le jeu jusque-là. La politique de l'agent est délibérément ignorée —
# c'est ce qui rend la maximisation valide ensemble par ensemble, indépendamment.
#
# Convention d'indifférence FIGÉE (PRD 1 §6.2) : à égalité exacte des deux
# valeurs, on retient l'action PASSIVE. D'où les `>` stricts. Cette convention
# compte : contre Station, huit des douze ensembles sont des points
# d'indifférence exacts.
meilleure_reponse <- function(b) {
  pol <- setNames(numeric(12), INFOSETS)
  ev_pos1 <- 0
  ev_pos2 <- 0

  # --- L'agent est J1, l'adversaire est J2 -----------------------------------
  for (c in 0:2) {
    autres <- setdiff(0:2, c)
    g1 <- sapply(autres, function(d) gain(c, d, 1))
    g2 <- sapply(autres, function(d) gain(c, d, 2))

    # Ensemble profond d'abord : J1 a retenu, J2 a engagé. Le poids est la
    # probabilité que J2 engage après un retenu.
    q <- sapply(autres, function(d) b[[paste0("J2/C", d, "/apres_check")]])
    poids <- P_DONNE * q
    v_fold <- sum(poids * -1)
    v_call <- sum(poids * g2)
    couvre <- v_call > v_fold
    pol[[paste0("J1/C", c, "/face_mise_apres_check")]] <- as.numeric(couvre)
    # Valeur, par carte adverse, de la décision retenue en aval :
    gain_aval <- if (couvre) g2 else rep(-1, length(autres))

    # Puis l'ouverture, qui intègre la valeur du nœud aval.
    r <- sapply(autres, function(d) b[[paste0("J2/C", d, "/face_mise")]])
    v_check <- sum(P_DONNE * ((1 - q) * g1 + q * gain_aval))
    v_bet   <- sum(P_DONNE * ((1 - r) * 1 + r * g2))
    pol[[paste0("J1/C", c, "/ouverture")]] <- as.numeric(v_bet > v_check)
    ev_pos1 <- ev_pos1 + max(v_check, v_bet)
  }

  # --- L'agent est J2, l'adversaire est J1 -----------------------------------
  # Les deux décisions de J2 sont terminales de son point de vue, et leurs poids
  # partitionnent les donnes (J1 a engagé, ou J1 a retenu).
  for (c in 0:2) {
    autres <- setdiff(0:2, c)
    g1 <- sapply(autres, function(d) gain(c, d, 1))
    g2 <- sapply(autres, function(d) gain(c, d, 2))
    u  <- sapply(autres, function(d) b[[paste0("J1/C", d, "/ouverture")]])

    poids <- P_DONNE * u
    v_fold <- sum(poids * -1)
    v_call <- sum(poids * g2)
    pol[[paste0("J2/C", c, "/face_mise")]] <- as.numeric(v_call > v_fold)
    ev_pos2 <- ev_pos2 + max(v_fold, v_call)

    poids2 <- P_DONNE * (1 - u)
    v2 <- sapply(autres, function(d) b[[paste0("J1/C", d, "/face_mise_apres_check")]])
    v_check <- sum(poids2 * g1)
    v_bet   <- sum(poids2 * ((1 - v2) * 1 + v2 * g2))
    pol[[paste0("J2/C", c, "/apres_check")]] <- as.numeric(v_bet > v_check)
    ev_pos2 <- ev_pos2 + max(v_check, v_bet)
  }

  list(politique = politique(pol), ev = (ev_pos1 + ev_pos2) / 2)
}

# -----------------------------------------------------------------------------
# 5. Les deux instruments de mesure du mémoire
# -----------------------------------------------------------------------------
# Ils regardent la MÊME politique observée depuis deux référentiels opposés, et
# ils vont en sens inverse : l'écart doit descendre, la référence récitée monter.
#
# Leur somme est une constante propre à chaque adversaire, EV(BR) - EV(GTO) :
# 0 contre GTO, 1/9 contre Station, 7/9 contre Over-folder. D'où le §3.3.1 :
# contre GTO, `récitée = -écart`, ce ne sont donc PAS deux verrous indépendants.

# Ce que l'agent laisse sur la table à chaque manche. >= 0, nul ssi il joue une
# meilleure réponse. NE DÉPEND PAS d'alpha : il se mesure contre la meilleure
# réponse, dont l'espérance est indépendante de l'équilibre choisi. C'est ce qui
# rend H1 et H3 insensibles au choix d'alpha.
ecart <- function(pi_agent, bot) meilleure_reponse(bot)$ev - ev_moyenne(pi_agent, bot)

# De combien l'agent bat un pur récitant de l'équilibre. Un récitant y reste à 0
# quel que soit l'adversaire ; un exploiteur s'en écarte positivement.
# DÉPEND d'alpha (par EV(GTO)) : c'est l'ÉCHELLE de cette mesure qui est
# conditionnelle au choix du protocole, cf. §3.3.2.
reference_recitee <- function(pi_agent, bot, alpha = 1 / 3) {
  ev_moyenne(pi_agent, bot) - ev_moyenne(gto(alpha), bot)
}

# -----------------------------------------------------------------------------
# 6. Complétion de pi-chapeau
# -----------------------------------------------------------------------------
# Contre Station et Over-folder, qui n'engagent jamais, six ensembles ne sont
# JAMAIS atteints : l'agent n'y décide pas, donc aucune fréquence n'y est
# observable. Convention figée du protocole : on les comble à la valeur
# d'équilibre. Cela n'affecte NI l'EV NI l'écart (leur poids contrefactuel est
# nul) ; le choix GTO évite seulement d'inventer une agressivité fantôme dans les
# analyses descriptives de pi-chapeau.
completer <- function(p_observee, alpha = 1 / 3) {
  plein <- gto(alpha)
  vus <- intersect(names(p_observee), INFOSETS)
  plein[vus] <- p_observee[vus]
  politique(plein)
}

# -----------------------------------------------------------------------------
# 7. Auto-vérification du moteur — l'équivalent des tests T1-T9
# -----------------------------------------------------------------------------
# Trois propriétés qui doivent tenir par théorie. Si l'une casse, tout ce qui
# suit dans les autres fichiers est faux.
verifier_moteur <- function(tol = 1e-12) {
  g <- gto(1 / 3)
  ok <- c(
    # T1 — valeur du jeu : J1 perd 1/18 par manche à l'équilibre (von Neumann).
    "valeur du jeu = -1/18"      = abs(ev_j1(g, g) - (-1 / 18)) < tol,
    # T2 — l'équilibre est inexploitable par lui-même. C'EST LE TEST QUI TRANCHE
    # la constante contestée : il échoue si l'on met 1/3 au lieu de 2/3.
    "ecart(GTO, GTO) = 0"        = abs(ecart(g, g)) < tol,
    # T3 — l'EV de la meilleure réponse aux deux bots biaisés, connue à la main.
    "EV(BR | Station) = 1/3"     = abs(meilleure_reponse(BOTS$Station)$ev - 1 / 3) < tol,
    "EV(BR | Over-folder) = 1"   = abs(meilleure_reponse(BOTS$`Over-folder`)$ev - 1) < tol,
    # T4 — l'écart d'un récitant contre chaque bot : 0, 1/9, 7/9.
    "ecart recitant | Station"   = abs(ecart(g, BOTS$Station) - 1 / 9) < tol,
    "ecart recitant | Overfold"  = abs(ecart(g, BOTS$`Over-folder`) - 7 / 9) < tol,
    # T5 — la meilleure réponse est bien une politique pure (0 ou 1 partout).
    "BR est pure"                = all(meilleure_reponse(BOTS$Station)$politique %in% c(0, 1)),
    # T6 — l'argument du §3.3.2, dans les deux sens.
    # (a) l'ÉCART est alpha-libre : alpha n'entre pas dans son calcul, seulement
    #     la politique observée et la meilleure réponse au bot. Un agent qui joue
    #     la meilleure réponse a un écart nul, quel que soit l'équilibre de
    #     référence — H1 et H3 sont donc insensibles au choix d'alpha.
    "ecart(BR) = 0 sans alpha"   = abs(ecart(meilleure_reponse(BOTS$Station)$politique,
                                             BOTS$Station)) < tol,
    # (b) la RÉFÉRENCE RÉCITÉE, elle, change d'échelle avec alpha : 1/9 à
    #     alpha = 1/3, 2/9 à alpha = 0. C'est pourquoi ces valeurs-là sont
    #     rapportées comme conditionnelles au choix du protocole.
    "recitee max | a = 1/3"      = abs(reference_recitee(meilleure_reponse(BOTS$Station)$politique,
                                                         BOTS$Station, 1 / 3) - 1 / 9) < tol,
    "recitee max | a = 0"        = abs(reference_recitee(meilleure_reponse(BOTS$Station)$politique,
                                                         BOTS$Station, 0) - 2 / 9) < tol
  )
  ok
}
