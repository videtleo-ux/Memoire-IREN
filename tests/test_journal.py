"""Suite du logging — critères d'acceptation du PRD 4 §7.

Le test central est J5 : un run synthétique complet est joué avec le moteur,
logué, puis **rejoué depuis les seuls JSONL**. S'il manque quoi que ce soit
dans les logs pour re-régler les manches et retrouver l'écart, le rejeu le
dit. C'est la garantie « tout est reconstructible » de la spec §9.
"""

from __future__ import annotations

import csv
import json
from fractions import Fraction
from itertools import cycle, permutations
from pathlib import Path

import pytest

from harnais import gabarits
from journal import (
    ContexteRun,
    Drapeau,
    EtatReel,
    EvenementSession,
    EvenementTour,
    JournalRun,
    LigneInvalide,
    Mesures,
    analyser,
    compter,
    generer,
    lire_sessions,
    lire_tours,
    rejouer_run,
)
from journal.deobfuscation import NIVEAU_DEOBFUSCATION, NIVEAU_RECITATION
from journal.derives import COLONNES_SESSIONS
from moteur import (
    CARTES,
    STATION,
    Action,
    Carte,
    Contexte,
    InfoSet,
    Position,
    completer_politique,
    decideur_depuis_politique,
    ecart,
    ecart_recitation,
    ev_moyenne,
    jouer_manche,
    meilleure_reponse,
    numero,
)


# ==========================================================================
# Fabrique d'un run synthétique complet
# ==========================================================================


def _politique_agent(infoset: InfoSet) -> Action:
    """Agent déterministe et lisible : engage avec le sceau supérieur, couvre
    dès le sceau intermédiaire. Assez exploitant pour que l'écart ne soit ni
    nul ni maximal — donc assez discriminant pour un test de mesure."""
    if infoset.contexte in (Contexte.OUVERTURE, Contexte.APRES_CHECK):
        return Action.BET if infoset.carte is Carte.C2 else Action.CHECK
    return Action.CALL if infoset.carte >= Carte.C1 else Action.FOLD


def _contexte(condition: str = "SM") -> ContexteRun:
    return ContexteRun(
        run_id=f"{condition}-station-r1",
        condition=condition,
        bot="Station",
        replication=1,
        machine="victus",
        modele="modele-de-test",
    )


def fabriquer_run(dossier: Path, K: int = 6, condition: str = "SM") -> JournalRun:
    """Joue K manches contre Station et logue tout, tours et série.

    Le bot est déterministe : la manche est entièrement reproductible depuis
    les cartes et la séquence d'actions, ce que le rejeu doit retrouver.
    """
    journal = JournalRun(dossier, _contexte(condition))
    donnes = cycle(permutations(CARTES, 2))
    bot = decideur_depuis_politique(STATION, __import__("random").Random(0))

    agressives: dict[InfoSet, int] = {}
    effectifs: dict[InfoSet, int] = {}
    resultats: list[int] = []
    positions = {"J1": 0, "J2": 0}

    for manche in range(1, K + 1):
        position_agent = Position.J1 if manche % 2 else Position.J2
        positions[position_agent.value] += 1
        carte_j1, carte_j2 = next(donnes)
        resultat = jouer_manche(
            _politique_agent if position_agent is Position.J1 else bot,
            _politique_agent if position_agent is Position.J2 else bot,
            carte_j1,
            carte_j2,
        )
        gain_agent = (
            resultat.gain_j1 if position_agent is Position.J1 else -resultat.gain_j1
        )
        resultats.append(gain_agent)

        sequence = [action.value for _, action in resultat.historique]
        decisions_agent = [
            (rang, ifs, action)
            for rang, (ifs, action) in enumerate(resultat.historique)
            if ifs.position is position_agent
        ]
        for numero_decision, (rang, ifs, action) in enumerate(decisions_agent, start=1):
            effectifs[ifs] = effectifs.get(ifs, 0) + 1
            if action is ifs.action_agressive:
                agressives[ifs] = agressives.get(ifs, 0) + 1
            dernier = numero_decision == len(decisions_agent)
            carte_agent = carte_j1 if position_agent is Position.J1 else carte_j2
            carte_bot = carte_j2 if position_agent is Position.J1 else carte_j1
            journal.ecrire_tour(
                EvenementTour(
                    session=0,
                    manche=manche,
                    decision=numero_decision,
                    etat_reel=EtatReel(
                        carte_agent=int(carte_agent),
                        carte_bot=int(carte_bot),
                        carte_ecartee=int(_ecartee(carte_j1, carte_j2)),
                        position_agent=position_agent.value,
                        historique=sequence[:rang],
                    ),
                    infoset=str(ifs),
                    infoset_numero=numero(ifs),
                    vue_servie=gabarits.construire_prompt(
                        ifs, [(i.position, a) for i, a in resultat.historique[:rang]]
                    ),
                    sortie_brute=f"je choisis.\nACTION: {action.value}",
                    action_parsee=action.value,
                    parsing="ok",
                    resultat_manche=gain_agent if dernier else None,
                    historique_final=sequence if dernier else None,
                    tokens={"in": 800, "out": 40},
                    latence_ms=1200,
                )
            )

    pi_partielle = {ifs: Fraction(agressives.get(ifs, 0), n) for ifs, n in effectifs.items()}
    pi_hat, non_observes = completer_politique(pi_partielle)
    journal.ecrire_session(
        EvenementSession(
            session=0,
            K=K,
            positions=positions,
            memoire={"M_s": "", "M_s1": "", "evenements": [], "ecritures_intra_serie": 0},
            pi_hat={
                **{
                    str(ifs): {"p": float(pi_partielle[ifs]), "n": effectifs[ifs]}
                    for ifs in effectifs
                },
                "infosets_non_observes": [str(i) for i in non_observes],
            },
            mesures=Mesures(
                ecart_exploitation=ecart(pi_hat, STATION),
                reference_recite=ecart_recitation(pi_hat, STATION),
                ev_pi_hat=ev_moyenne(pi_hat, STATION),
                ev_br=meilleure_reponse(STATION).ev,
                ev_realisee=sum(resultats) / len(resultats),
            ),
            defauts={"actions_par_defaut": 0, "relances": 0, "erreurs_harnais": 0},
            hash_donnes="sha256:donnes-de-test",
            cout_session_tokens={"in": 800 * K, "out": 40 * K},
        )
    )
    return journal


def _ecartee(carte_j1: Carte, carte_j2: Carte) -> Carte:
    (restante,) = [c for c in CARTES if c not in (carte_j1, carte_j2)]
    return restante


# ==========================================================================
# J1 — écriture et relecture JSONL
# ==========================================================================


def test_j1_champs_communs_sur_chaque_ligne(tmp_path):
    fabriquer_run(tmp_path / "logs")
    lignes = list(lire_tours(tmp_path / "logs")) + list(lire_sessions(tmp_path / "logs"))
    assert lignes
    for ligne in lignes:
        for champ in ("run_id", "condition", "bot", "replication", "machine", "modele"):
            assert ligne[champ], champ
        assert ligne["hash_regles"] == gabarits.HASH_REGLES
        assert ligne["horodatage"].endswith("+00:00"), "horodatage UTC, comparable entre machines"


def test_j1_append_only(tmp_path):
    dossier = tmp_path / "logs"
    fabriquer_run(dossier, K=2)
    avant = len(list(lire_tours(dossier)))
    fabriquer_run(dossier, K=2)
    assert len(list(lire_tours(dossier))) == 2 * avant


def test_j1_utf8_et_json_valide(tmp_path):
    """Relisible d'un trait, accents compris, sur les deux machines (§7.4)."""
    dossier = tmp_path / "logs"
    fabriquer_run(dossier, K=2)
    brut = (dossier / "turns.jsonl").read_text(encoding="utf-8")
    assert "Épreuve" in brut, "pas d'échappement ASCII : les logs se relisent tels quels"
    for ligne in brut.splitlines():
        json.loads(ligne)


def test_j1_ligne_tronquee_leve(tmp_path):
    dossier = tmp_path / "logs"
    fabriquer_run(dossier, K=2)
    with (dossier / "turns.jsonl").open("a", encoding="utf-8") as fichier:
        fichier.write('{"run_id": "tronq\n')
    with pytest.raises(ValueError, match="JSON invalide"):
        list(lire_tours(dossier))


# ==========================================================================
# J2 — validation en écriture (PRD 4 §7.5)
# ==========================================================================


def _tour_valide() -> EvenementTour:
    ifs = InfoSet(Position.J1, Carte.C1, Contexte.OUVERTURE)
    return EvenementTour(
        session=0,
        manche=1,
        decision=1,
        etat_reel=EtatReel(1, 0, 2, "J1", []),
        infoset=str(ifs),
        infoset_numero=numero(ifs),
        vue_servie="prompt",
        sortie_brute="ACTION: retenir",
        action_parsee="check",
        parsing="ok",
        resultat_manche=1,
        historique_final=["check", "check"],
    )


def test_j2_tour_valide_passe(tmp_path):
    JournalRun(tmp_path, _contexte()).ecrire_tour(_tour_valide())


def test_j2_condition_inconnue_refusee(tmp_path):
    contexte = ContexteRun("x", "AUTRE", "Station", 1, "victus", "m")
    with pytest.raises(LigneInvalide, match="condition"):
        JournalRun(tmp_path, contexte).ecrire_tour(_tour_valide())


def test_j2_donne_incoherente_refusee(tmp_path):
    tour = _tour_valide()
    casse = EvenementTour(**{**tour.__dict__, "etat_reel": EtatReel(1, 1, 2, "J1", [])})
    with pytest.raises(LigneInvalide, match="donne incohérente"):
        JournalRun(tmp_path, _contexte()).ecrire_tour(casse)


def test_j2_vue_servie_vide_refusee(tmp_path):
    tour = _tour_valide()
    casse = EvenementTour(**{**tour.__dict__, "vue_servie": "   "})
    with pytest.raises(LigneInvalide, match="vue_servie"):
        JournalRun(tmp_path, _contexte()).ecrire_tour(casse)


def test_j2_parsing_inconnu_refuse(tmp_path):
    tour = _tour_valide()
    casse = EvenementTour(**{**tour.__dict__, "parsing": "peut-être"})
    with pytest.raises(LigneInvalide, match="parsing"):
        JournalRun(tmp_path, _contexte()).ecrire_tour(casse)


def _session_valide(**remplacements) -> EvenementSession:
    base = dict(
        session=0,
        K=4,
        positions={"J1": 2, "J2": 2},
        memoire={},
        pi_hat={},
        mesures=Mesures(
            ecart_exploitation=Fraction(1, 9),
            reference_recite=Fraction(0),
            ev_pi_hat=Fraction(1, 4),
            ev_br=Fraction(1, 3),
            ev_realisee=0.25,
        ),
        defauts={"actions_par_defaut": 0, "relances": 0, "erreurs_harnais": 0},
    )
    return EvenementSession(**{**base, **remplacements})


def test_j2_positions_desequilibrees_refusees(tmp_path):
    with pytest.raises(LigneInvalide, match="positions"):
        JournalRun(tmp_path, _contexte()).ecrire_session(
            _session_valide(positions={"J1": 3, "J2": 2})
        )


def test_j2_ecart_negatif_refuse(tmp_path):
    """L'écart est un maximum moins une valeur : il ne peut pas être négatif."""
    mesures = Mesures(
        ecart_exploitation=Fraction(-1, 9),
        reference_recite=Fraction(0),
        ev_pi_hat=Fraction(1, 2),
        ev_br=Fraction(1, 3),
        ev_realisee=0.5,
    )
    with pytest.raises(LigneInvalide, match="négatif"):
        JournalRun(tmp_path, _contexte()).ecrire_session(_session_valide(mesures=mesures))


def test_j2_mesures_exactes_conservees(tmp_path):
    """Les fractions partent aussi en exact : la revérification reste possible."""
    JournalRun(tmp_path, _contexte()).ecrire_session(_session_valide())
    (ligne,) = list(lire_sessions(tmp_path))
    assert ligne["mesures"]["exact"]["ecart_exploitation"] == "1/9"
    assert ligne["mesures"]["ecart_exploitation"] == pytest.approx(1 / 9)


# ==========================================================================
# J3 — détecteur de dé-obfuscation (PRD 4 §7.3)
# ==========================================================================


@pytest.mark.parametrize(
    "texte, niveau",
    [
        ("En fait c'est du poker", NIVEAU_DEOBFUSCATION),
        ("This is Kuhn poker", NIVEAU_DEOBFUSCATION),
        ("il a le roi", NIVEAU_DEOBFUSCATION),
        ("he holds the queen", NIVEAU_DEOBFUSCATION),
        ("la carte suivante", NIVEAU_DEOBFUSCATION),
        ("je mise gros", NIVEAU_DEOBFUSCATION),
        ("il faut bluffer un tiers du temps", NIVEAU_RECITATION),
        ("la stratégie de Nash", NIVEAU_RECITATION),
        ("l'équilibre GTO impose alpha = 1/3", NIVEAU_RECITATION),
        ("je bluffe 33 % du temps", NIVEAU_RECITATION),
    ],
)
def test_j3_vrais_positifs(texte, niveau):
    drapeaux = analyser(texte)
    assert any(d.niveau == niveau for d in drapeaux), drapeaux


@pytest.mark.parametrize(
    "texte",
    [
        "Tor, Vael et Rhun sont les trois sceaux",
        "j'ai retenu, puis l'autre a engagé",
        "je couvre parce qu'il engage tout le temps",
        "qu'il se retire ou qu'il couvre, j'ai le sceau supérieur",
        gabarits.REGLES,
        gabarits.CONSIGNE_REFLEXION,
    ],
)
def test_j3_vrais_negatifs(texte):
    """Vocabulaire obfusqué pur : aucun drapeau — y compris nos propres textes.

    Le piège que ce test verrouille : « trois » ne doit pas déclencher « roi »,
    et « j'ai » / « qu'il » ne doivent pas déclencher l'abréviation de rang.
    """
    assert analyser(texte) == ()


def test_j3_extrait_contient_le_motif():
    (drapeau,) = [d for d in analyser("blabla " * 30 + "kuhn" + " suite" * 30) if d.regle == r"\bkuhn\b"]
    assert "kuhn" in drapeau.extrait
    assert len(drapeau.extrait) < 200, "extrait borné : on ne recopie pas la sortie entière"


def test_j3_source_et_manche_reportees():
    """Un hit dans le canal mémoire se propage à toutes les séries suivantes."""
    (drapeau,) = analyser("c'est du poker", source="memoire", manche=88)
    assert (drapeau.source, drapeau.manche) == ("memoire", 88)
    assert drapeau.en_json()["niveau"] == NIVEAU_DEOBFUSCATION


def test_j3_comptage_par_niveau():
    drapeaux = analyser("c'est du poker, il faut bluffer un tiers du temps")
    compte = compter(drapeaux)
    assert compte[NIVEAU_DEOBFUSCATION] >= 1
    assert compte[NIVEAU_RECITATION] >= 2


def test_j3_aucune_censure():
    """Le détecteur observe : il ne modifie ni ne masque le texte."""
    texte = "c'est du poker"
    assert analyser(texte) != ()
    assert texte == "c'est du poker"


# ==========================================================================
# J4 — CSV dérivés (PRD 4 §5)
# ==========================================================================


def test_j4_sessions_csv(tmp_path):
    fabriquer_run(tmp_path / "run1" / "logs", K=4)
    fabriquer_run(tmp_path / "run2" / "logs", K=4, condition="ICL")
    compte = generer(tmp_path, tmp_path / "csv")

    assert compte["sessions"] == 2
    with (tmp_path / "csv" / "sessions.csv").open(encoding="utf-8", newline="") as fichier:
        lignes = list(csv.DictReader(fichier))
    assert list(lignes[0]) == list(COLONNES_SESSIONS)
    assert {l["condition"] for l in lignes} == {"SM", "ICL"}
    assert float(lignes[0]["ecart"]) >= 0


def test_j4_infosets_csv_une_ligne_par_infoset_observe(tmp_path):
    fabriquer_run(tmp_path / "run" / "logs", K=6)
    generer(tmp_path, tmp_path / "csv")
    with (tmp_path / "csv" / "infosets.csv").open(encoding="utf-8", newline="") as fichier:
        lignes = list(csv.DictReader(fichier))
    assert lignes
    assert all(int(l["n"]) > 0 for l in lignes)
    assert "infosets_non_observes" not in {l["infoset"] for l in lignes}


def test_j4_memoire_csv_seulement_pour_ae(tmp_path):
    fabriquer_run(tmp_path / "sm" / "logs", K=2, condition="SM")
    fabriquer_run(tmp_path / "ae" / "logs", K=2, condition="AE")
    compte = generer(tmp_path, tmp_path / "csv")
    assert compte["memoire"] == 1


def test_j4_csv_regenerable_a_lidentique(tmp_path):
    fabriquer_run(tmp_path / "run" / "logs", K=4)
    generer(tmp_path, tmp_path / "csv")
    premier = (tmp_path / "csv" / "sessions.csv").read_text(encoding="utf-8")
    generer(tmp_path, tmp_path / "csv")
    assert (tmp_path / "csv" / "sessions.csv").read_text(encoding="utf-8") == premier


def test_j4_pas_de_ligne_vide_sous_windows(tmp_path):
    """`newline=""` : sans lui, R lirait une ligne vide sur deux."""
    fabriquer_run(tmp_path / "run" / "logs", K=2)
    generer(tmp_path, tmp_path / "csv")
    brut = (tmp_path / "csv" / "sessions.csv").read_bytes()
    assert b"\r\r\n" not in brut


# ==========================================================================
# J5 — « tout est reconstructible » (PRD 4 §7.1)
# ==========================================================================


def test_j5_rejeu_dun_run_complet(tmp_path):
    """Le test central : re-régler chaque manche et retrouver l'écart."""
    dossier = tmp_path / "logs"
    fabriquer_run(dossier, K=12)
    rapport = rejouer_run(dossier)
    assert rapport.anomalies == []
    assert (rapport.manches, rapport.sessions) == (12, 1)


def test_j5_resultat_fausse_detecte(tmp_path):
    dossier = tmp_path / "logs"
    fabriquer_run(dossier, K=6)
    _corrompre(dossier / "turns.jsonl", lambda t: t.get("resultat_manche") is not None, "resultat_manche", 99)
    rapport = rejouer_run(dossier)
    assert any("résultat rejoué" in a for a in rapport.anomalies)


def test_j5_historique_final_manquant_detecte(tmp_path):
    """Sans la séquence complète, la manche n'est pas re-règlable."""
    dossier = tmp_path / "logs"
    fabriquer_run(dossier, K=6)
    _corrompre(dossier / "turns.jsonl", lambda t: t.get("historique_final"), "historique_final", None)
    rapport = rejouer_run(dossier)
    assert any("historique_final" in a for a in rapport.anomalies)


def test_j5_ecart_fausse_detecte(tmp_path):
    dossier = tmp_path / "logs"
    fabriquer_run(dossier, K=6)
    lignes = list(lire_sessions(dossier))
    lignes[0]["mesures"]["exact"]["ecart_exploitation"] = "5/7"
    lignes[0]["mesures"]["ecart_exploitation"] = 5 / 7
    (dossier / "sessions.jsonl").write_text(
        json.dumps(lignes[0], ensure_ascii=False) + "\n", encoding="utf-8"
    )
    rapport = rejouer_run(dossier)
    assert any("écart logué" in a for a in rapport.anomalies)


def test_j5_effectif_fausse_detecte(tmp_path):
    dossier = tmp_path / "logs"
    fabriquer_run(dossier, K=6)
    lignes = list(lire_sessions(dossier))
    cle = next(c for c, v in lignes[0]["pi_hat"].items() if isinstance(v, dict))
    lignes[0]["pi_hat"][cle]["n"] += 3
    (dossier / "sessions.jsonl").write_text(
        json.dumps(lignes[0], ensure_ascii=False) + "\n", encoding="utf-8"
    )
    rapport = rejouer_run(dossier)
    assert any("effectif" in a for a in rapport.anomalies)


def test_j5_manches_par_defaut_exclues_de_pi_hat(tmp_path):
    """Une action imposée par le harnais ne dit rien de la politique de l'agent."""
    from journal.rejouer import estimer_pi_hat

    ifs = InfoSet(Position.J1, Carte.C0, Contexte.OUVERTURE)
    tours = [
        {"infoset": str(ifs), "action_parsee": "bet", "flags": []},
        {"infoset": str(ifs), "action_parsee": "check", "flags": ["action_par_defaut"]},
    ]
    pi_hat, effectifs = estimer_pi_hat(tours)
    assert effectifs[ifs] == 1
    assert pi_hat[ifs] == Fraction(1)


def test_j5_session_sans_tour_detectee(tmp_path):
    dossier = tmp_path / "logs"
    fabriquer_run(dossier, K=2)
    (dossier / "turns.jsonl").write_text("", encoding="utf-8")
    rapport = rejouer_run(dossier)
    assert any("sans aucun tour" in a for a in rapport.anomalies)


def _corrompre(chemin: Path, predicat, champ: str, valeur) -> None:
    lignes = [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]
    for ligne in lignes:
        if predicat(ligne):
            ligne[champ] = valeur
            break
    chemin.write_text(
        "\n".join(json.dumps(l, ensure_ascii=False) for l in lignes) + "\n", encoding="utf-8"
    )
