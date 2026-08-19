"""Oracle de tests du moteur — T1 à T9 (PRD 1 §7).

Valeurs par manche, moyennées J1/J2, re-dérivées analytiquement le 2026-08-19.
La suite doit les reproduire **exactement** : tout est en `Fraction`, aucun
`pytest.approx` — les 1/18 et 7/9 attendus sont exacts, et une comparaison
approchée masquerait précisément le genre d'erreur que ce module doit exclure.

Toute erreur ici invalide silencieusement les 27 runs : cette suite passe
avant le moindre appel API.
"""

from __future__ import annotations

import random
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

import pytest

from moteur import (
    ACTIONS_LEGALES,
    BOTS,
    CARTES,
    DONNES,
    GTO,
    INFOSETS,
    OVER_FOLDER,
    STATION,
    Action,
    Contexte,
    InfoSet,
    Position,
    completer_politique,
    construire_politique,
    decideur_depuis_politique,
    ecart,
    ecart_recitation,
    ev,
    ev_moyenne,
    gto,
    infosets_atteignables,
    infosets_de_position,
    jouer_manche,
    meilleure_reponse,
    numero,
    politique_pure,
    valider_politique,
)
from moteur.lexique import textes_destines_a_lagent, violations_obfuscation

#: α balayés partout où l'invariance sur la famille d'équilibres est testée.
ALPHAS = (Fraction(0), Fraction(1, 6), Fraction(1, 3))

RACINE = Path(__file__).resolve().parents[1]


# ==========================================================================
# T1 — valeur du jeu
# ==========================================================================


@pytest.mark.parametrize("alpha", ALPHAS)
def test_t1_valeur_du_jeu(alpha: Fraction) -> None:
    """ev(GTO, GTO, J1) = −1/18, invariant sur α ∈ [0, 1/3]."""
    assert ev(gto(alpha), gto(alpha), Position.J1) == Fraction(-1, 18)


@pytest.mark.parametrize("alpha", ALPHAS)
def test_t1_somme_nulle(alpha: Fraction) -> None:
    """Contrepartie J2 : le jeu est à somme nulle, l'EV moyennée est donc nulle."""
    pi = gto(alpha)
    assert ev(pi, pi, Position.J2) == Fraction(1, 18)
    assert ev_moyenne(pi, pi) == 0


# ==========================================================================
# T2 — GTO est un équilibre (tranche la constante contestée du §4)
# ==========================================================================


@pytest.mark.parametrize("alpha", ALPHAS)
def test_t2_ecart_gto_nul(alpha: Fraction) -> None:
    """ecart(GTO, GTO) = 0 exactement : GTO n'est exploitable par personne."""
    assert ecart(gto(alpha), gto(alpha)) == 0


def test_t2_tranche_la_constante_contestee() -> None:
    """Le test T2 **échoue** avec la valeur 1/3 écrite en §2 de la spec pour la
    couverture de J1 avec C1, et passe avec α + 1/3 = 2/3 (décision D6).

    C'est l'arbitre automatique de la constante : on vérifie ici les deux
    branches, pour que la variante fautive ne puisse pas revenir sans casser
    la suite.
    """
    correcte = gto(Fraction(1, 3))
    assert correcte[InfoSet(Position.J1, CARTES[1], Contexte.FACE_MISE_APRES_CHECK)] == Fraction(2, 3)
    assert ecart(correcte, correcte) == 0

    fautive = construire_politique(
        {
            **dict(correcte),
            InfoSet(Position.J1, CARTES[1], Contexte.FACE_MISE_APRES_CHECK): Fraction(1, 3),
        }
    )
    assert ecart(fautive, fautive) > 0, "la variante à 1/3 doit être exploitable"


# ==========================================================================
# T3 / T4 — meilleure réponse aux bots déterministes
# ==========================================================================


def test_t3_meilleure_reponse_station() -> None:
    """+1/3 par manche : C2 mise et se fait payer (+2) ; C1 indifférent (0) ;
    C0 check et perd 1. Identique dans les deux positions."""
    resultat = meilleure_reponse(STATION)
    assert resultat.ev == Fraction(1, 3)
    assert ev(resultat.politique, STATION, Position.J1) == Fraction(1, 3)
    assert ev(resultat.politique, STATION, Position.J2) == Fraction(1, 3)


def test_t3_exploit_station_est_bien_la_valeur() -> None:
    """L'exploit annoncé par la spec §3 : ne jamais bluffer, miser le jeton
    fort pour la valeur. La meilleure réponse doit le retenir."""
    pol = meilleure_reponse(STATION).politique
    assert pol[InfoSet(Position.J1, CARTES[2], Contexte.OUVERTURE)] == 1  # value-bet
    assert pol[InfoSet(Position.J1, CARTES[0], Contexte.OUVERTURE)] == 0  # jamais de bluff
    assert pol[InfoSet(Position.J2, CARTES[2], Contexte.APRES_CHECK)] == 1
    assert pol[InfoSet(Position.J2, CARTES[0], Contexte.APRES_CHECK)] == 0


def test_t4_meilleure_reponse_over_folder() -> None:
    """+1 par manche : miser toute carte, l'adversaire se retire (+1), dans
    les deux positions."""
    resultat = meilleure_reponse(OVER_FOLDER)
    assert resultat.ev == Fraction(1)
    assert ev(resultat.politique, OVER_FOLDER, Position.J1) == Fraction(1)
    assert ev(resultat.politique, OVER_FOLDER, Position.J2) == Fraction(1)


def test_t4_indifference_tranchee_en_passif() -> None:
    """Avec C2 face à Over-folder, miser et checker valent exactement 1/3 :
    la convention figée retient l'action passive et logue le cas — sans que
    l'EV totale (+1) en soit affectée."""
    resultat = meilleure_reponse(OVER_FOLDER)
    indifferents = set(resultat.indifferences)
    assert InfoSet(Position.J1, CARTES[2], Contexte.OUVERTURE) in indifferents
    for ifs in indifferents:
        assert resultat.politique[ifs] == 0, "une indifférence doit être tranchée en passif"
    assert resultat.ev == Fraction(1)


# ==========================================================================
# T5 / T6 — écart d'un réciteur GTO : le discriminateur central
# ==========================================================================


def test_t5_valeur_pinnee() -> None:
    """T5 : ecart(GTO, Station) = 1/9 à α = 1/3 — la valeur qui compte, celle
    de la campagne."""
    assert ecart(GTO, STATION) == Fraction(1, 9)


def test_t6_valeur_pinnee() -> None:
    """T6 : ecart(GTO, Over-folder) = 7/9 à α = 1/3."""
    assert ecart(GTO, OVER_FOLDER) == Fraction(7, 9)


@pytest.mark.parametrize("alpha", ALPHAS)
def test_t5_ecart_gto_contre_station_selon_alpha(alpha: Fraction) -> None:
    """2/9 − α/3 (PRD 1 §7.1).

    Fuite en J1 = α/3 (bluffs C0 payés à chaque fois) + (1/3 − α) (sous-mise
    de valeur : C2 n'est misé qu'avec proba 3α face à un adversaire qui paie
    toujours) = 1/3 − 2α/3. Fuite en J2 = 1/9, indépendante de α — les
    fréquences de J2 sont des constantes d'indifférence. Moyenne des deux.
    """
    assert ecart(gto(alpha), STATION) == Fraction(2, 9) - alpha / 3


@pytest.mark.parametrize("alpha", ALPHAS)
def test_t6_ecart_gto_contre_over_folder_selon_alpha(alpha: Fraction) -> None:
    """8/9 − α/3 (PRD 1 §7.1).

    En J1 face à un Over-folder, C2 rapporte +1 qu'on mise ou non (mise →
    retrait, check → abattage gagné) : la fuite ne vient que de C1, jamais
    volé, et de C0, volé à fréquence α seulement, soit 1/3 + 2(1−α)/3 =
    1 − 2α/3. Fuite en J2 = 7/9, constante. Moyenne des deux.
    """
    assert ecart(gto(alpha), OVER_FOLDER) == Fraction(8, 9) - alpha / 3


def test_t5_t6_asymetrie_du_reciteur() -> None:
    """Discriminateur de la spec §3 : un réciteur saigne **dans les deux
    sens**, 7 fois plus fort contre Over-folder que contre Station — asymétrie
    qu'on doit retrouver dans les courbes réelles."""
    contre_station = ecart(GTO, STATION)
    contre_over_folder = ecart(GTO, OVER_FOLDER)
    assert contre_station > 0 and contre_over_folder > 0
    assert contre_over_folder == 7 * contre_station


def test_reference_recitee() -> None:
    """La référence « récité » du PRD 1 §6.2 : nulle pour GTO lui-même,
    strictement positive pour une politique qui exploite vraiment."""
    for bot in BOTS.values():
        assert ecart_recitation(GTO, bot) == 0
        assert ecart_recitation(meilleure_reponse(bot).politique, bot) >= 0
    assert ecart_recitation(meilleure_reponse(STATION).politique, STATION) == Fraction(1, 9)
    assert ecart_recitation(meilleure_reponse(OVER_FOLDER).politique, OVER_FOLDER) == Fraction(7, 9)


# ==========================================================================
# T7 — structure
# ==========================================================================


def test_t7_enumeration_des_infosets() -> None:
    """12 info-sets, 6 par position, numérotation 1–12 dans l'ordre du PRD."""
    assert len(INFOSETS) == 12
    assert len(set(INFOSETS)) == 12
    assert len(infosets_de_position(Position.J1)) == 6
    assert len(infosets_de_position(Position.J2)) == 6
    assert [numero(ifs) for ifs in INFOSETS] == list(range(1, 13))
    assert all(ifs.position is Position.J1 for ifs in INFOSETS[:6])
    assert all(ifs.contexte is Contexte.OUVERTURE for ifs in INFOSETS[:3])
    assert all(ifs.contexte is Contexte.FACE_MISE for ifs in INFOSETS[9:])


def test_t7_politiques_valides() -> None:
    """Les politiques de référence sont totales et à valeurs dans [0, 1]."""
    for pi in (*BOTS.values(), *(gto(a) for a in ALPHAS)):
        valider_politique(pi)
        assert len(pi) == 12
        assert all(0 <= p <= 1 for p in pi.values())


def test_t7_politique_invalide_rejetee() -> None:
    with pytest.raises(ValueError):
        construire_politique({ifs: Fraction(2) for ifs in INFOSETS})
    with pytest.raises(ValueError):
        valider_politique({ifs: Fraction(0) for ifs in INFOSETS[:11]})


def test_t7_atteignabilite() -> None:
    """12 info-sets atteignables contre GTO ; exactement 6 contre Station et
    Over-folder, qui ne misent jamais → une seule décision LLM par manche."""
    assert len(infosets_atteignables(GTO)) == 12
    for bot in (STATION, OVER_FOLDER):
        atteignables = infosets_atteignables(bot)
        assert len(atteignables) == 6
        assert all(
            ifs.contexte in (Contexte.OUVERTURE, Contexte.APRES_CHECK) for ifs in atteignables
        )
        inatteignables = set(INFOSETS) - atteignables
        assert {numero(ifs) for ifs in inatteignables} == {4, 5, 6, 10, 11, 12}


def test_t7_actions_legales_uniquement() -> None:
    """Toute manche jouée n'émet que des actions légales, et l'arbre a la
    bonne profondeur (≤ 3 décisions)."""
    alea = random.Random(20260819)
    politiques = [GTO, STATION, OVER_FOLDER]
    for pi_j1, pi_j2 in product(politiques, repeat=2):
        d1 = decideur_depuis_politique(pi_j1, alea)
        d2 = decideur_depuis_politique(pi_j2, alea)
        for carte_j1, carte_j2 in DONNES:
            resultat = jouer_manche(d1, d2, carte_j1, carte_j2)
            assert 2 <= len(resultat.historique) <= 3
            for ifs, action in resultat.historique:
                assert action in ACTIONS_LEGALES[ifs.contexte]
            assert abs(resultat.gain_j1) in (1, 2)


def test_t7_donne_invalide_rejetee() -> None:
    alea = random.Random(1)
    d = decideur_depuis_politique(GTO, alea)
    with pytest.raises(ValueError):
        jouer_manche(d, d, CARTES[0], CARTES[0])


def test_t7_manche_simulee_coherente_avec_ev() -> None:
    """Pont entre le calcul exact et le déroulement effectif : la moyenne
    empirique des manches doit converger vers `ev` (tolérance de Monte-Carlo).
    Garde-fou contre une divergence entre l'arbre de `jouer_manche` et celui
    de `_ev_j1_sur_donne`."""
    alea = random.Random(4242)
    d1 = decideur_depuis_politique(GTO, alea)
    d2 = decideur_depuis_politique(STATION, alea)
    donnes = random.Random(7)
    total = 0
    manches = 20_000
    for _ in range(manches):
        carte_j1, carte_j2 = donnes.choice(DONNES)
        total += jouer_manche(d1, d2, carte_j1, carte_j2).gain_j1
    empirique = total / manches
    attendu = float(ev(GTO, STATION, Position.J1))
    assert abs(empirique - attendu) < 0.05


# ==========================================================================
# T8 — obfuscation (non-régression)
# ==========================================================================


def test_t8_aucune_chaine_interdite_dans_les_textes_agent() -> None:
    """Aucun texte servi à l'agent ne contient de chaîne interdite (PRD 1 §2).

    La couverture grandit automatiquement : PRD 2 enrichira
    `textes_destines_a_lagent()` avec les gabarits de prompt.
    """
    for etiquette, texte in textes_destines_a_lagent().items():
        violations = violations_obfuscation(texte)
        assert not violations, f"{etiquette} : {violations}"


def test_t8_detecteur_reellement_mordant() -> None:
    """Le détecteur doit attraper les cas qu'il est censé attraper — sinon
    T8 passerait pour de mauvaises raisons."""
    assert violations_obfuscation("Il s'agit en fait du Kuhn poker")
    assert violations_obfuscation("le roi bat la dame")
    assert violations_obfuscation("you hold the King")
    assert violations_obfuscation("la carte 3 est la meilleure")
    assert violations_obfuscation("bluffer une fois sur trois")
    # Faux positifs à éviter : les montants des règles restent dicibles.
    assert not violations_obfuscation("Droit d'entrée : 1 jeton chacun.")
    assert not violations_obfuscation("Rhun bat Vael, Vael bat Tor.")


def test_t8_pas_de_chaine_interdite_dans_les_gabarits() -> None:
    """Balaie les gabarits de rendu sur disque dès qu'ils existeront (PRD 2).
    Sans dossier, le test est vacuement vrai : il s'activera tout seul."""
    dossiers = [RACINE / "src" / "rendu", RACINE / "src" / "harnais" / "gabarits"]
    fichiers = [f for d in dossiers if d.exists() for f in d.rglob("*") if f.is_file()]
    for fichier in fichiers:
        violations = violations_obfuscation(fichier.read_text(encoding="utf-8"))
        assert not violations, f"{fichier} : {violations}"


def test_t8_lexique_conforme_a_la_decision_d5() -> None:
    """Le lexique figé par D5 ne doit pas dériver sans décision explicite."""
    from moteur.lexique import ACTIONS, JETONS, NOM_DU_JEU

    assert NOM_DU_JEU == "L'Épreuve des Trois Sceaux"
    assert [JETONS[c] for c in CARTES] == ["Tor", "Vael", "Rhun"]
    assert [ACTIONS[a] for a in (Action.CHECK, Action.BET, Action.CALL, Action.FOLD)] == [
        "retenir",
        "engager",
        "couvrir",
        "se retirer",
    ]


# ==========================================================================
# T9 — meilleure réponse sur politique arbitraire
# ==========================================================================


def _politique_aleatoire(alea: random.Random) -> dict[InfoSet, Fraction]:
    """Probabilités rationnelles exactes, incluant les bornes 0 et 1."""
    return {ifs: Fraction(alea.randint(0, 12), 12) for ifs in INFOSETS}


def test_t9_ecart_positif_et_nul_sur_la_meilleure_reponse() -> None:
    """Sur 1 000 politiques aléatoires : ecart(π, bot) ≥ 0 pour les 3 bots, et
    ecart(meilleure_reponse(bot), bot) = 0."""
    alea = random.Random(20260819)
    for nom, bot in BOTS.items():
        mr = meilleure_reponse(bot)
        assert ecart(mr.politique, bot) == 0, nom
        for _ in range(1_000):
            pi = construire_politique(_politique_aleatoire(alea))
            assert ecart(pi, bot) >= 0, (nom, pi)


def test_t9_meilleure_reponse_a_une_politique_arbitraire() -> None:
    """Condition nécessaire pour traiter les π̂ bruitées réelles : la meilleure
    réponse doit être exacte face à n'importe quel adversaire, pas seulement
    les 3 bots."""
    alea = random.Random(31415)
    for _ in range(200):
        adverse = construire_politique(_politique_aleatoire(alea))
        mr = meilleure_reponse(adverse)
        assert ecart(mr.politique, adverse) == 0
        for _ in range(5):
            pi = construire_politique(_politique_aleatoire(alea))
            assert ev_moyenne(pi, adverse) <= mr.ev


def test_t9_verification_par_enumeration_exhaustive() -> None:
    """Contre-vérification indépendante de l'induction arrière : la meilleure
    réponse à une position est la meilleure des 2⁶ = 64 politiques pures.

    Deux chemins de calcul distincts doivent donner la même valeur — c'est ce
    qui autorise à faire confiance à l'induction arrière sur les π̂ réelles.
    """
    alea = random.Random(2718)
    adversaires = [GTO, STATION, OVER_FOLDER] + [
        construire_politique(_politique_aleatoire(alea)) for _ in range(25)
    ]
    for adverse in adversaires:
        attendu = meilleure_reponse(adverse).ev
        par_position = []
        for position in (Position.J1, Position.J2):
            miens = infosets_de_position(position)
            meilleur = max(
                ev(politique_pure(agressifs), adverse, position)
                for taille in range(len(miens) + 1)
                for agressifs in combinations(miens, taille)
            )
            par_position.append(meilleur)
        assert attendu == sum(par_position) / 2


# ==========================================================================
# Conventions annexes (PRD 1 §6.3)
# ==========================================================================


def test_completion_des_infosets_non_observes() -> None:
    """Les entrées non observées de π̂ sont posées à la valeur GTO, et la liste
    est rendue pour le drapeau `infosets_non_observes` des logs (PRD 4)."""
    observes = {ifs: Fraction(1) for ifs in infosets_atteignables(STATION)}
    pi, non_observes = completer_politique(observes)
    assert len(non_observes) == 6
    assert {numero(ifs) for ifs in non_observes} == {4, 5, 6, 10, 11, 12}
    for ifs in non_observes:
        assert pi[ifs] == GTO[ifs]


def test_completion_naffecte_pas_la_mesure() -> None:
    """Justification de la convention : les info-sets inatteignables face au
    bot concerné n'affectent ni l'EV ni l'écart, quelle que soit la valeur
    qu'on y met. On le vérifie plutôt que de l'affirmer."""
    alea = random.Random(161803)
    for bot in (STATION, OVER_FOLDER):
        observes = {ifs: Fraction(alea.randint(0, 12), 12) for ifs in infosets_atteignables(bot)}
        pi_gto, _ = completer_politique(observes)
        pi_autre = construire_politique(
            {**dict(pi_gto), **{ifs: Fraction(alea.randint(0, 12), 12) for ifs in INFOSETS if ifs not in observes}}
        )
        assert ev_moyenne(pi_gto, bot) == ev_moyenne(pi_autre, bot)
        assert ecart(pi_gto, bot) == ecart(pi_autre, bot)


def test_aucune_dependance_flottante_dans_les_ev() -> None:
    """Critère d'acceptation 1 : arithmétique exacte de bout en bout."""
    assert isinstance(ev(GTO, STATION, Position.J1), Fraction)
    assert isinstance(ev_moyenne(GTO, STATION), Fraction)
    assert isinstance(ecart(GTO, STATION), Fraction)
    assert isinstance(meilleure_reponse(GTO).ev, Fraction)
