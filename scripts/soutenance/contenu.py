# -*- coding: utf-8 -*-
"""Contenu des slides 2-6 et 8-11, tiré de « Mémoire Videt Léo IREN.pdf »."""
from deck import (Ids, band, build, card, logos, picture, po, table_card, tile,
                  title)

X0, W0 = 457200, 8229600
TOP, BOT = 960120, 4434840

C3_W, C3 = 2590800, (457200, 3276600, 6096000)
C2_W, C2 = 3977640, (457200, 4709160)

# Colonnes des slides de résultats : figure à gauche, deux cartes à droite.
LFT_X, LFT_W = 457200, 4663440
RGT_X, RGT_W = 5257800, 3429000
RGT_Y1, RGT_Y2, RGT_H = 960120, 2788920, 1645920


# --------------------------------------------------------------------------- #
def slide2() -> str:
    i = Ids(200)
    h = 2468880
    s = logos(i) + title(i, "1. Motivations")
    s += card(i, C3[0], TOP, C3_W, h, "Le fait", [
        ("lead", "Les modèles de langage ne produisent plus seulement du texte."),
        ("bul", "Agents autonomes :", "ils négocient des contrats, enchérissent, fixent des prix, arbitrent des allocations."),
        ("bul", "Face à d'autres agents", "dont les intérêts divergent des leurs."),
        ("bul", "L'enjeu est économique :", "la nature de leur rationalité détermine les équilibres qui se forment sur les marchés."),
    ])
    s += card(i, C3[1], TOP, C3_W, h, "Le manque", [
        ("lead", "On sait que ces modèles jouent bien. On ne sait pas pourquoi."),
        ("bul", "Les évaluations stratégiques", "établissent qu'ils tiennent la comparaison en information imparfaite."),
        ("bul", "Elles sont statiques :", "donnes indépendantes, aucune capitalisation de l'expérience."),
        ("bul", "Elles ne séparent pas", "une stratégie construite d'une règle récitée."),
    ])
    s += card(i, C3[2], TOP, C3_W, h, "L'occasion", [
        ("lead", "Un développement parallèle rend la distinction mesurable."),
        ("bul", "La mémoire persistante :", "l'agent synthétise son expérience en langue naturelle et relit sa synthèse."),
        ("bul", "Validée sans adversaire", "— dans des environnements coopératifs ou solitaires."),
        ("bul", "Or c'est le canal", "par lequel un agent construirait le modèle de son adversaire, pour s'en écarter et gagner davantage."),
    ])
    s += band(i, X0, 3566160, W0, 868680, "Question de recherche",
              "Dans un environnement stratégique à information imparfaite, un agent LLM "
              "autonome équipé d'une mémoire persistante développe-t-il une adaptation "
              "comportementale s'apparentant à une stratégie ?", text_sz=1200)
    return build(s)


# --------------------------------------------------------------------------- #
def slide3() -> str:
    i = Ids(300)
    h = BOT - TOP
    s = logos(i) + title(i, "2. Revue de littérature — le socle")
    s += card(i, C3[0], TOP, C3_W, h, "Mesurer, pas décrire", [
        ("lead", "Économie comportementale et expérimentale"),
        ("bul", None, "Substituer à l'Homo œconomicus un agent psychologiquement situé (Jacquemet & L'Haridon, 2016)."),
        ("bul", None, "Le laboratoire comme instrument de preuve : contrôle de l'environnement de choix, assignation aléatoire, incitations réelles (Jacquemet & Le Lec, 2017)."),
        ("bul", None, "Le biais devient un écart systématique à une norme — un objet structuré, non une erreur aléatoire."),
        ("bul", None, "Scission tripartite de la rationalité (Cot & Ferey, 2016) : l'optimalité dépend du cadre qui la juge."),
    ])
    s += card(i, C3[1], TOP, C3_W, h, "Du laboratoire humain\nau laboratoire artificiel", [
        ("lead", "Machine Behavior et Homo silicus"),
        ("bul", "Rahwan et al. (2019) :", "étudier les machines comme une classe d'acteurs, pas comme du code — leur comportement émergent n'est pas formalisable analytiquement."),
        ("bul", "Horton et al. (2026) :", "le LLM comme modèle computationnel implicite de l'humain, doté par le langage d'une dotation et de croyances."),
        ("bul", None, "Deux lectures ouvertes : simuler l'humain, ou observer une entité artificielle pour elle-même."),
        ("bul", None, "Le risque nommé par les deux : la mémorisation superficielle."),
    ])
    s += card(i, C3[2], TOP, C3_W, h, "Le terrain", [
        ("lead", "Jeux à information imparfaite et poker de Kuhn"),
        ("bul", None, "Borel (1938) → von Neumann (1944) → Kuhn (1950) : le bluff est rationnel, l'équilibre est en stratégies mixtes."),
        ("bul", None, "Douze ensembles d'information : l'équilibre bayésien parfait est calculable exactement — famille indexée par α ∈ [0, 1/3] (Loriente & Diez, 2023)."),
        ("bul", "GTBench (Duan et al., 2024) :", "les LLM échouent en information complète, sont compétitifs en information imparfaite."),
        ("bul", "La tension centrale :", "GTO, robuste et non exploitable, contre exploitatif, qui punit la faille adverse."),
    ])
    return build(s)


# --------------------------------------------------------------------------- #
def slide4() -> str:
    i = Ids(400)
    h = BOT - TOP
    s = logos(i) + title(i, "2. Revue de littérature — le manque")
    s += card(i, C3[0], TOP, C3_W, h, "Le gradient de persistance", [
        ("lead", "Trois façons d'adapter un modèle, trois compromis"),
        ("bul", "ICL —", "la fenêtre de contexte comme mémoire de travail volatile. Flexible, mais tout s'effondre à la fermeture de la session."),
        ("bul", "Gestion sémantique —", "résumer pour ne pas saturer, au prix des micro-signaux quantitatifs (Chen et al., 2026)."),
        ("bul", "RL et fine-tuning —", "permanent, mais rigide, coûteux, et imitant passivement les biais du jeu de données."),
        ("bul", "Le compromis :", "le contextuel est flexible mais volatile, le paramétrique permanent mais rigide. Aucun ne convient à un agent qui doit apprendre son adversaire en jouant."),
    ])
    s += card(i, C3[1], TOP, C3_W, h, "La mémoire auto-rédigée", [
        ("lead", "Le paradigme qui lève la contradiction"),
        ("bul", "Voyager (Wang et al., 2023) :", "l'expérience stockée en programmes réutilisables, jamais en poids."),
        ("bul", "Reflexion (Shinn et al., 2023) :", "l'agent analyse son échec, rédige une auto-réflexion en langue naturelle, la relit au tour suivant."),
        ("bul", "Une frontière commune :", "ces architectures sont validées dans des environnements qui ne cherchent jamais à tromper l'agent."),
        ("bul", "Le point commun :", "l'expérience est inscrite en langue naturelle ou en code, jamais dans les poids — donc lisible, auditable, et révisable par l'agent lui-même."),
    ])
    s += card(i, C3[2], TOP, C3_W, h, "Le manque, et le positionnement", [
        ("lead", "Le terrain adversarial reste fragmenté"),
        ("bul", "Richelieu, MemGPT, Readable Minds :", "information quasi publique, critères d'ingénierie, ou GTO non calculable."),
        ("bul", "Trois dimensions confondues :", "biais de décision, stratégie GTO, stratégie exploitative. Ce travail les instrumente séparément."),
        ("bul", None, "Sans mémoire persistante, un agent est structurellement condamné à l'équilibre défensif : il ne peut pas estimer la déviation adverse."),
        ("bul", "D'où ce travail :", "un agent à mémoire auto-rédigée, face à un adversaire dont la déviation doit être découverte puis punie."),
    ])
    return build(s)


# --------------------------------------------------------------------------- #
def slide5() -> str:
    i = Ids(500)
    h1, y2, h2 = 1874520, 2926080, 1508760
    s = logos(i) + title(i, "3. Méthodologie — le dispositif")
    s += card(i, C3[0], TOP, C3_W, h1, "La tâche", [
        ("bul", "Poker de Kuhn canonique :", "3 cartes, 1 jeton d'ante, une mise, 12 ensembles d'information."),
        ("bul", "Vocabulaire réécrit partout :", "sceaux « Tor ≺ Vael ≺ Rhun », actions « retenir / engager / couvrir / se retirer »."),
        ("bul", "Valeur induite (Smith, 1976) :", "gain saillant, monotone, dominant."),
    ], body_sz=850, spc=400)
    s += card(i, C3[1], TOP, C3_W, h1, "Les trois adversaires", [
        ("bul", "GTO —", "l'équilibre exact (α = 1/3). Rien à exploiter : le contrôle négatif."),
        ("bul", "Station —", "ne mise jamais, paie toujours. Exploit : ne jamais bluffer."),
        ("bul", "Over-folder —", "ne mise jamais, se couche toujours. Exploit : tout engager."),
        ("bul", "Fuites opposées :", "aucune stratégie fixe ne peut satisfaire les deux."),
    ], body_sz=850, spc=400)
    s += card(i, C3[2], TOP, C3_W, h1, "Les trois traitements", [
        ("lead", "Modèle et harnais tenus constants."),
        ("bul", "SM —", "aucune rubrique mémoire. Le degré zéro."),
        ("bul", "ICL —", "les récapitulatifs passés empilés, fenêtre de 52 000 caractères (trois séries)."),
        ("bul", "AE —", "le fichier de notes que l'agent lit et réécrit lui-même."),
    ], body_sz=850, spc=400)
    s += card(i, X0, y2, W0, h2, "La série — l'horloge de l'adaptation", [
        ("bul", "Une série = K = 150 manches jouées sous un état mémoire fixe.", "Un point de courbe correspond à un état mémoire, et à un seul ; sinon l'écart calculé perdrait son sujet."),
        ("bul", "Gel :", "la mémoire est capturée à l'ouverture, figée pendant la série, mise à jour à la seule frontière ; contexte neuf à chaque manche. Les écritures intra-série sont détectées, enregistrées, puis annulées."),
        ("bul", "Appariement :", "les trois traitements d'une même réplication reçoivent les mêmes distributions, manche par manche — nombres aléatoires communs. Alternance de position déterministe, mesures moyennées sur les deux positions."),
    ], body_sz=800, spc=320)
    return build(s)


# --------------------------------------------------------------------------- #
def slide6() -> str:
    i = Ids(600)
    y1, y2, h = 960120, 2788920, 1645920
    s = logos(i) + title(i, "3. Méthodologie — la mesure")
    s += card(i, C2[0], y1, C2_W, h, "L'écart d'exploitation", [
        ("formula", "Écart = EV(meilleure réponse) − EV(politique observée)"),
        ("bul", "Exact :", "six distributions, arbre de profondeur trois, énumération complète en arithmétique rationnelle. Aucune simulation, aucun intervalle de confiance sur la mesure."),
        ("bul", "Insensible à la chance :", "il porte sur la politique, pas sur les gains réalisés."),
        ("bul", "En jetons par manche.", "Zéro signifie exploitation optimale."),
    ], body_sz=850, spc=350)
    s += card(i, C2[1], y1, C2_W, h, "La référence récitée", [
        ("formula", "Référence = EV(politique observée) − EV(équilibre)"),
        ("bul", "L'instrument de H2 :", "un récitant y reste à zéro quel que soit l'adversaire ; un exploiteur s'en écarte positivement."),
        ("bul", "Pourquoi elle est nécessaire :", "on ne peut pas garantir que l'agent ignore l'équilibre, donc on mesure explicitement sa distance à lui."),
        ("bul", "À adversaire fixé,", "les deux mesures n'ont qu'un degré de liberté : un recalage affine de pente −1."),
    ], body_sz=850, spc=350)
    s += table_card(i, C2[0], y2, C2_W, h, "L'échelle de lecture",
                    ["Adversaire", "Joueur parfait", "Récitant", "Réf. récitée max"],
                    [["Over-folder", "1,0000", "0,2222", "+0,7778"],
                     ["Station", "0,3333", "0,2222", "+0,1111"],
                     ["GTO", "0,0000", "0,0000", "0"]],
                    [1.5, 1.15, 1.0, 1.35], body_sz=850)
    s += card(i, C2[1], y2, C2_W, h, "La campagne exécutée", [
        ("bul", "24 exécutions ·", "177 séries · 26 550 manches · 27 290 décisions de l'agent."),
        ("bul", "Paramètres :", "gpt-5.6-luna, effort medium, K = 150, 3 réplications, graine de campagne unique."),
        ("bul", "Coût :", "47,27 $, sur deux jours et une machine unique."),
        ("bul", "Vérification :", "225 tests automatisés, un oracle analytique du moteur de mesure, et un rejeu intégral depuis les seuls journaux — 24 sur 24."),
    ], body_sz=850, spc=350)
    return build(s)


# --------------------------------------------------------------------------- #
def slide8() -> str:
    i = Ids(800)
    s = logos(i) + title(i, "5. Résultats — H1 : l'adaptation vient de la mémoire")
    s += picture(i, "rId5", 762000, 914400, 7620000, 2743200)
    ty, th = 3749040, 685800
    for x, lbl, val, sub in (
            (C3[0], "Over-folder", "0,704 → 0,000", "réduction +0,704 · 3 réplications sur 3"),
            (C3[1], "Station", "0,222 → 0,002", "réduction +0,220 · 2 réplications à zéro exact"),
            (C3[2], "GTO", "0,187 → 0,008", "réduction +0,178 · rien à exploiter ici")):
        s += tile(i, x, ty, C3_W, th, lbl, val, sub)
    return build(s)


# --------------------------------------------------------------------------- #
def slide9() -> str:
    i = Ids(900)
    s = logos(i) + title(i, "5. Résultats — H2 : elle exploite, elle ne récite pas")
    fig_h = int(LFT_W / 2.0)
    s += picture(i, "rId5", LFT_X, TOP, LFT_W, fig_h)
    cy = TOP + fig_h + po(0.14)
    s += card(i, LFT_X, cy, LFT_W, BOT - cy, "Le contrôle négatif", [
        ("bul", "39 séries contre l'adversaire à l'équilibre :", "la référence récitée n'est jamais positive, l'écart jamais négatif."),
        ("bul", "Six séries atteignent exactement zéro", "— une meilleure réponse à l'équilibre, la valeur du jeu encaissée. Aucune ne dépasse."),
    ], body_sz=850, spc=300)
    s += card(i, RGT_X, RGT_Y1, RGT_W, RGT_H, "L'asymétrie, le test décisif", [
        ("bul", "Sans mémoire :", "0,285 · 0,307 · 0,355 selon l'adversaire, pour un écart-type d'échantillonnage de 0,031. Rien ne les distingue, et c'est une propriété du dispositif."),
        ("bul", "Avec mémoire :", "1,000 contre Over-folder, 0,004 contre Station. Trois réponses à la même situation, dont deux diamétralement opposées."),
        ("bul", "Aucune application de l'équilibre", "ne produit ce contraste : l'équilibre est un objet fixe, calculé contre un adversaire supposé jouer lui-même l'équilibre."),
    ], head_sz=1200, body_sz=800, spc=300, pad=po(0.15))
    s += table_card(i, RGT_X, RGT_Y2, RGT_W, RGT_H, "L'amplitude, sur son maximum",
                    ["Adversaire", "SM", "AE", "Max", "Atteint"],
                    [["Over-folder", "+0,074", "+0,778", "+0,778", "100 %"],
                     ["Station", "−0,111", "+0,110", "+0,111", "99 %"],
                     ["GTO", "−0,187", "−0,024", "0", "—"]],
                    [1.45, 1.0, 1.0, 1.0, 0.95], head_sz=1200, body_sz=750,
                    pad=po(0.15), bold_col=2,
                    note="AE : moyenne des séries 7 à 9. Le maximum est celui d'une meilleure réponse.")
    return build(s)


# --------------------------------------------------------------------------- #
def slide10() -> str:
    i = Ids(1000)
    s = logos(i) + title(i, "5. Résultats — H3 : le mécanisme de rétention")
    fig_h = int(LFT_W / (1600 / 720))
    s += picture(i, "rId5", LFT_X, TOP, LFT_W, fig_h)
    cy = TOP + fig_h + po(0.14)
    s += table_card(i, LFT_X, cy, LFT_W, BOT - cy,
                    "Les quatre décisions qui décident, contre Station",
                    ["Décision", "Meilleure rép.", "ICL", "AE"],
                    [["Engager le sceau faible — Ouvrant", "0,000", "0,065", "0,006"],
                     ["Engager le sceau faible — Répondant", "0,000", "0,091", "0,009"],
                     ["Engager le sceau fort — Ouvrant", "1,000", "0,973", "1,000"],
                     ["Engager le sceau fort — Répondant", "1,000", "0,941", "1,000"]],
                    [3.3, 1.1, 0.8, 0.8], head_sz=1200, body_sz=800, bold_col=3)
    s += card(i, RGT_X, RGT_Y1, RGT_W, RGT_H, "Ni la vitesse, ni l'oubli", [
        ("bul", "Effet apparié ICL − AE :", "+0,0381 contre Station (IC 95 % ± 0,0148, exclut zéro) ; +0,0039 contre Over-folder (contient zéro)."),
        ("bul", "Aucun décrochage à la saturation.", "Les deux chutent à la première frontière, dans les mêmes proportions."),
        ("bul", "AE se verrouille sur zéro :", "23 des 27 séries suivantes à écart exactement nul. ICL n'atteint jamais zéro."),
        ("bul", "H3 est vérifiée, mais sous condition :", "le mécanisme ne départage les deux mémoires que contre l'un des deux adversaires exploitables."),
    ], head_sz=1200, body_sz=800, spc=280, pad=po(0.15))
    s += card(i, RGT_X, RGT_Y2, RGT_W, RGT_H, "Une règle, ou deux", [
        ("bul", "Over-folder :", "une seule règle, positive. Les deux mécanismes l'extraient intégralement."),
        ("bul", "Station :", "deux règles, dont une négative. Un engagement perdant figure dans l'historique comme une manche parmi 150 ; rien ne rassemble ces occurrences en interdiction."),
        ("bul", "L'apport est plus étroit que prévu :", "la synthèse ne retient ni mieux ni plus longtemps — elle achève l'induction."),
    ], head_sz=1200, body_sz=800, spc=280, pad=po(0.15))
    return build(s)


# --------------------------------------------------------------------------- #
def slide11() -> str:
    i = Ids(1100)
    s = logos(i) + title(i, "5. Résultats — H4 : ce que l'adaptation coûte")
    fig_h = int(LFT_W / (1800 / 680))
    s += picture(i, "rId5", LFT_X, TOP, LFT_W, fig_h)
    cy = TOP + fig_h + po(0.14)
    s += table_card(i, LFT_X, cy, LFT_W, BOT - cy,
                    "Ce que les quatre-vingt-dix notes contiennent",
                    ["Recherché dans les notes", "Occurrences"],
                    [["Un pourcentage (« 33 % »)", "0"],
                     ["Une proportion en toutes lettres (« un tiers »)", "0"],
                     ["Une fréquence prescrite pour sa propre action", "0"],
                     ["Quantificateurs catégoriques (toujours, jamais)", "221"],
                     ["Quantificateurs gradués (souvent, parfois)", "228"]],
                    [4.2, 1.0], head_sz=1200, body_sz=800, bold_col=1)
    s += card(i, RGT_X, RGT_Y1, RGT_W, RGT_H, "La dégénérescence", [
        ("bul", "Contre l'adversaire à l'équilibre,", "bien jouer exige d'engager le sceau faible une fois sur trois, et de façon imprévisible."),
        ("bul", "Sans mémoire :", "les fréquences se tiennent autour de 28 %, pour un optimum à 33 %."),
        ("bul", "Dès qu'une note existe :", "des fréquences extrêmes plus d'une série sur deux. Il n'a pas oublié comment jouer — il a cessé de tirer au sort."),
    ], head_sz=1200, body_sz=800, spc=280, pad=po(0.15))
    s += card(i, RGT_X, RGT_Y2, RGT_W, RGT_H, "Le même mécanisme", [
        ("bul", None, "Ce qui rend la mémoire auto-écrite supérieure — contraindre l'agent à formuler une règle — est exactement ce qui la rend incapable de randomiser. Une règle écrite en langue naturelle est déterministe."),
        ("bul", "Coût déduit, non mesuré :", "face à des bots figés, abandonner le mélange ne coûte rien. Un adversaire capable de s'ajuster est hors périmètre."),
        ("bul", None, "Un agent doté de mémoire est un meilleur exploiteur et un adversaire plus prévisible."),
    ], head_sz=1200, body_sz=800, spc=280, pad=po(0.15))
    return build(s)


SLIDES = {2: slide2, 3: slide3, 4: slide4, 5: slide5, 6: slide6,
          8: slide8, 9: slide9, 10: slide10, 11: slide11}

# Figures à embarquer, par numéro de slide (rId5).
FIGURES = {8: "fig1-trajectoires.png", 9: "fig2-asymetrie.png",
           10: "fig4-zoom.png", 11: "fig5-degenerescence.png"}
