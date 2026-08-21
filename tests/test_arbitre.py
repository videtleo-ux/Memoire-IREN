"""Suite de l'arbitre — critères d'acceptation du PRD 3 §10.

Aucun appel API : l'invocateur `hermes -z` est substitué par un double en
mémoire, comme dans `tests/test_harnais.py`. Ce que cette suite garde sous
contrôle, ce sont les invariants d'orchestration qu'**aucun log ne rattrapera
après coup** :

- A2, l'appariement des donnes entre conditions — le plus important de tous :
  si deux conditions ne voient pas les mêmes sceaux à (r, s, k) égal, la
  réduction de variance sur laquelle repose toute la comparaison n'aura jamais
  existé, et rien dans les résultats ne le dira ;
- A3, la reprise sur incident — une donne sautée ou jouée deux fois fausse π̂
  sans laisser de trace visible ;
- A5, l'absence de fuite d'un sceau non dévoilé — l'agent apprendrait sur une
  information que la table ne lui a pas donnée.
"""

from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

import pytest

from arbitre import (
    Condition,
    ConfigRun,
    ErreurArbitre,
    EtatRun,
    affecter_machines,
    donne,
    evaluer_plateau,
    flux_bot,
    hash_donnes,
    identifiant,
    matrice_campagne,
    pente_regression,
    position_agent,
    preparer_run,
    sequence_donnes,
)
from arbitre import cli
from arbitre.etat import FICHIER_TOURS_ABANDONNES
from arbitre.integrite import FICHIER_TEMOIN, poser_temoin, verifier_temoin
from arbitre.recap import ligne_manche
from arbitre.run import TENTATIVES_MANCHE
from harnais import Reponse, Store
from harnais.stores import EchecCanari, TOOLSET_MEMOIRE, TOOLSET_SANS_OUTIL
from journal import generer, lire_sessions, lire_tours, rejouer_run
from moteur import Action, Carte, Position, jouer_manche
from moteur.lexique import rendre_carte, violations_obfuscation


# ==========================================================================
# Outils de test
# ==========================================================================


class CrashSimule(RuntimeError):
    """Coupure brutale au milieu d'une série — le `kill -9` du PRD 3 §10.3."""


class InvocateurFactice:
    """Double de `hermes -z` qui *joue* réellement, en lisant le prompt servi.

    Il ne connaît ni l'info-set ni l'état interne de l'arbitre : il extrait le
    sceau et les actions légales du texte, exactement comme le ferait le
    modèle. Une divergence entre la vue servie et la réalité se traduirait donc
    par une action illégale, que le moteur refuserait — c'est voulu.
    """

    def __init__(
        self,
        store: Store | None = None,
        echecs: int = 0,
        charabia: int = 0,
        crash_apres: int | None = None,
        notes: str = "",
    ):
        self.store = store
        self.echecs = echecs
        self.charabia = charabia
        self.crash_apres = crash_apres
        self.notes = notes
        self.appels: list[tuple[str, str]] = []
        self.effet_de_bord = None  # callable() déclenché à chaque appel de manche

    def __call__(self, prompt: str, toolset: str = TOOLSET_SANS_OUTIL) -> Reponse:
        self.appels.append((prompt, toolset))
        rang = len(self.appels)
        if self.crash_apres is not None and rang > self.crash_apres:
            raise CrashSimule(f"coupure simulée au {rang}ᵉ appel")
        if rang <= self.echecs:
            return self._reponse("", erreur="sortie vide")
        if toolset == TOOLSET_MEMOIRE:
            if self.store is not None and self.notes:
                self.store.notes.write_text(self.notes, encoding="utf-8")
            return self._reponse("J'ai mis mes notes à jour.")
        if self.effet_de_bord is not None:
            self.effet_de_bord()
        if rang <= self.echecs + self.charabia:
            return self._reponse("Hmm, difficile à dire.")
        return self._reponse(f"Je pèse le pour et le contre.\nACTION: {choisir(prompt)}")

    def _reponse(self, texte: str, erreur: str | None = None) -> Reponse:
        return Reponse(
            texte=texte,
            code_retour=1 if erreur else 0,
            latence_ms=7,
            tentatives=1,
            tokens_entree=800,
            tokens_sortie=40,
            modele="modele-de-test",
            erreur=erreur,
        )

    @property
    def prompts(self) -> list[str]:
        return [prompt for prompt, _ in self.appels]


def choisir(prompt: str) -> str:
    """Politique lisible et déterministe, lue depuis le prompt servi.

    Engage avec le sceau supérieur, couvre dès le sceau intermédiaire : assez
    exploitante pour que l'écart ne soit ni nul ni maximal, donc assez
    discriminante pour un test de mesure.
    """
    sceau = re.search(r"Votre sceau : (\w+)", prompt).group(1)
    passive, agressive = re.findall(r"« (.+?) »", prompt.split("[TÂCHE]")[-1])
    if agressive == "couvrir":
        return agressive if sceau in ("Vael", "Rhun") else passive
    return agressive if sceau == "Rhun" else passive


def _config(tmp_path: Path, condition: Condition, bot: str, K: int = 20, series: int = 1, **kw):
    return ConfigRun(
        condition=condition,
        bot=bot,
        replication=kw.pop("replication", 1),
        machine="machine-de-test",
        K=K,
        series_max=series,
        racine=tmp_path,
        **kw,
    )


def _arbitre(config: ConfigRun, invocateur: InvocateurFactice | None = None):
    """Prépare un run avec canari **fichier** : aucun appel API dans la suite."""
    fabrique = invocateur
    if fabrique is None:
        fabrique = InvocateurFactice()
    arbitre = preparer_run(config, invocateur=fabrique, canari_reel=False)
    fabrique.store = arbitre.store
    return arbitre


def _jouer(tmp_path: Path, condition: Condition, bot: str, K: int = 20, series: int = 1, **kw):
    config = _config(tmp_path, condition, bot, K, series, **kw)
    arbitre = _arbitre(config)
    arbitre.jouer()
    return arbitre


def _tours(config: ConfigRun) -> list[dict]:
    return list(lire_tours(config.dossier_logs))


def _series(config: ConfigRun) -> list[dict]:
    return list(lire_sessions(config.dossier_logs))


# ==========================================================================
# A1 — mini-run de bout en bout (PRD 3 §10.1)
# ==========================================================================


def test_a1_mini_run_produit_des_logs_complets(tmp_path):
    """1 série, K = 20, Station, SM : le jalon d'intégration du PRD 3 §10.1."""
    arbitre = _jouer(tmp_path, Condition.SM, "Station", K=20, series=1)
    config = arbitre.config

    tours = _tours(config)
    series = _series(config)
    assert len(series) == 1
    assert {t["manche"] for t in tours} == set(range(1, 21))
    # Station ne mise jamais : exactement une décision d'agent par manche (PRD 1 §3).
    assert len(tours) == 20
    assert all(t["vue_servie"] and t["sortie_brute"] for t in tours)


def test_a1_ecart_calculable_et_rejouable(tmp_path):
    """L'écart est fini, positif, et le rejeu depuis les seuls logs le retrouve."""
    arbitre = _jouer(tmp_path, Condition.SM, "Station", K=20, series=1)
    (serie,) = _series(arbitre.config)

    assert serie["mesures"]["ecart_exploitation"] >= 0
    assert serie["mesures"]["exact"]["ecart_exploitation"]
    assert serie["hash_donnes"].startswith("sha256:")
    rapport = rejouer_run(arbitre.config.dossier_logs)
    assert rapport.ok, rapport.anomalies


def test_a1_integrite_verte_et_csv_generables(tmp_path):
    """Clôture : rapport d'intégrité vert, puis CSV dérivés lisibles."""
    arbitre = _jouer(tmp_path, Condition.SM, "Station", K=20, series=1)
    rapport = arbitre.clore()
    assert rapport.ok, rapport.anomalies
    assert rapport.controles["temoin_isolation"] == "intact"

    compte = generer(tmp_path, tmp_path / "csv")
    assert compte["sessions"] == 1
    assert (tmp_path / "csv" / "sessions.csv").read_text(encoding="utf-8").count("\n") == 2


def test_a1_pi_hat_reflete_la_politique_jouee(tmp_path):
    """L'agent factice engage le sceau supérieur et rien d'autre : π̂ doit le dire."""
    arbitre = _jouer(tmp_path, Condition.SM, "Station", K=40, series=1)
    (serie,) = _series(arbitre.config)
    pi_hat = serie["pi_hat"]

    for cle, valeurs in pi_hat.items():
        if not isinstance(valeurs, dict):
            continue
        attendu = 1.0 if cle.split("/")[1] == "C2" else 0.0
        assert valeurs["p"] == attendu, cle
    # Station ne mise jamais : les 6 info-sets « face à une mise » restent vides.
    assert len(pi_hat["infosets_non_observes"]) == 6


def test_a1_condition_ae_logue_sa_frontiere(tmp_path):
    """La frontière AE écrit les notes et le diff d'entrées part dans les logs."""
    config = _config(tmp_path, Condition.AE, "Station", K=4, series=2)
    invocateur = InvocateurFactice(notes="Il couvre systématiquement.")
    arbitre = _arbitre(config, invocateur)
    arbitre.jouer()

    series = _series(config)
    assert series[0]["memoire"]["M_s"] == ""
    assert series[0]["memoire"]["M_s1"] == "Il couvre systématiquement."
    assert {e["type"] for e in series[0]["memoire"]["evenements"]} == {"ajout"}
    assert series[0]["memoire"]["entrees_m_s1"] == 1
    # La série suivante ouvre sur ces notes, et le prompt de manche les sert.
    assert series[1]["memoire"]["M_s"] == "Il couvre systématiquement."
    manches = [p for p in invocateur.prompts if "[ÉPREUVE EN COURS]" in p]
    assert "(rien pour l'instant)" in manches[0]
    assert "Il couvre systématiquement." in manches[-1]


# ==========================================================================
# A2 — appariement des donnes entre conditions (PRD 3 §10.2)
# ==========================================================================


def test_a2_donnes_identiques_entre_deux_conditions(tmp_path):
    """Deux conditions au même (r, s) reçoivent des donnes octet-pour-octet
    identiques. C'est le critère qu'aucun log ne rattrape après coup."""
    sm = _jouer(tmp_path, Condition.SM, "GTO", K=20, series=1)
    icl = _jouer(tmp_path, Condition.ICL, "GTO", K=20, series=1)

    def donnes(config):
        return {
            (t["session"], t["manche"]): (
                t["etat_reel"]["carte_agent"],
                t["etat_reel"]["carte_bot"],
                t["etat_reel"]["carte_ecartee"],
                t["etat_reel"]["position_agent"],
            )
            for t in _tours(config)
        }

    assert donnes(sm.config) == donnes(icl.config)
    assert _series(sm.config)[0]["hash_donnes"] == _series(icl.config)[0]["hash_donnes"]


def test_a2_bot_gto_fait_les_memes_tirages(tmp_path):
    """Même agent, même donne ⇒ le bot stochastique joue exactement pareil."""
    sm = _jouer(tmp_path, Condition.SM, "GTO", K=20, series=1)
    ae = _jouer(tmp_path, Condition.AE, "GTO", K=20, series=1)

    def deroules(config):
        return {
            t["manche"]: t["historique_final"]
            for t in _tours(config)
            if t["historique_final"] is not None
        }

    assert deroules(sm.config) == deroules(ae.config)


def test_a2_donnes_communes_aux_trois_bots(tmp_path):
    """Les mêmes mains, seule la politique adverse change (PRD 3 §4)."""
    sequences = {
        bot: [
            (t["etat_reel"]["carte_agent"], t["etat_reel"]["carte_bot"])
            for t in sorted(_tours(_jouer(tmp_path, Condition.SM, bot, K=10).config),
                            key=lambda t: (t["manche"], t["decision"]))
            if t["decision"] == 1
        ]
        for bot in ("Station", "Over-folder", "GTO")
    }
    assert sequences["Station"] == sequences["Over-folder"] == sequences["GTO"]


def test_a2_replications_differentes_donnent_des_donnes_differentes(tmp_path):
    """Chaque réplication a ses propres donnes : sinon N = 3 mesurerait la
    même main trois fois et l'intervalle serait un mirage."""
    r1 = sequence_donnes("graine", 1, 0, 40)
    r2 = sequence_donnes("graine", 2, 0, 40)
    assert r1 != r2


def test_a2_donne_est_une_fonction_pure_des_coordonnees():
    """Aucun état de générateur ne circule : même appel, même résultat."""
    assert donne("g", 2, 3, 17) == donne("g", 2, 3, 17)
    assert donne("g", 2, 3, 17) != donne("h", 2, 3, 17)
    for k in range(1, 50):
        d = donne("g", 1, 0, k)
        assert {d.agent, d.bot, d.ecartee} == {Carte.C0, Carte.C1, Carte.C2}


def test_a2_flux_bot_reproductible_et_distinct_du_flux_des_donnes():
    a = [flux_bot("g", 1, 0, 5).random() for _ in range(3)]
    b = [flux_bot("g", 1, 0, 5).random() for _ in range(3)]
    assert a == b
    assert flux_bot("g", 1, 0, 5).random() != flux_bot("g", 1, 0, 6).random()


def test_a2_hash_donnes_stable_et_sensible():
    assert hash_donnes("g", 1, 0, 20) == hash_donnes("g", 1, 0, 20)
    assert hash_donnes("g", 1, 0, 20) != hash_donnes("g", 1, 1, 20)
    assert hash_donnes("g", 1, 0, 20) != hash_donnes("g", 1, 0, 22)


# ==========================================================================
# A3 — reprise sur incident (PRD 3 §10.3)
# ==========================================================================


def test_a3_reprise_apres_coupure_en_milieu_de_serie(tmp_path):
    """Coupure brutale pendant la série 1 : la série est rejouée entière,
    aucune donne sautée ni dupliquée sur l'ensemble du run."""
    config = _config(tmp_path, Condition.ICL, "Station", K=10, series=2)
    # 10 appels pour la série 0, puis 4 manches de la série 1 avant la coupure.
    premier = InvocateurFactice(crash_apres=14)
    arbitre = _arbitre(config, premier)
    with pytest.raises(CrashSimule):
        arbitre.jouer()

    assert len(_series(config)) == 1  # seule la série 0 est close
    assert len({t["manche"] for t in _tours(config) if t["session"] == 1}) == 4

    reprise = _arbitre(config, InvocateurFactice())
    assert reprise.etat.prochaine_session == 1
    reprise.jouer()

    tours = _tours(config)
    for serie in (0, 1):
        manches = [t["manche"] for t in tours if t["session"] == serie and t["decision"] == 1]
        assert sorted(manches) == list(range(1, 11)), f"série {serie}"
    assert len(_series(config)) == 2
    assert reprise.clore().ok
    assert rejouer_run(config.dossier_logs).ok


def test_a3_tours_abandonnes_conserves_et_marques(tmp_path):
    """Rien n'est détruit : les tours de la tentative avortée sont déplacés,
    marqués, et sortis du fichier canonique pour qu'il reste rejouable."""
    config = _config(tmp_path, Condition.SM, "Station", K=10, series=1)
    arbitre = _arbitre(config, InvocateurFactice(crash_apres=3))
    with pytest.raises(CrashSimule):
        arbitre.jouer()

    _arbitre(config, InvocateurFactice()).jouer()

    abandonnes = [
        json.loads(ligne)
        for ligne in (config.dossier_logs / FICHIER_TOURS_ABANDONNES)
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len(abandonnes) == 3
    assert all(t["abandonnee"] and t["tentative"] == 1 for t in abandonnes)
    assert {t["manche"] for t in _tours(config)} == set(range(1, 11))


def test_a3_reprise_reconstruit_la_fenetre_icl(tmp_path):
    """La fenêtre ICL vit en mémoire vive : après coupure, elle se reconstruit
    depuis les récaps logués, sans le moindre appel au modèle."""
    config = _config(tmp_path, Condition.ICL, "Station", K=4, series=2)
    arbitre = _arbitre(config, InvocateurFactice(crash_apres=4))
    with pytest.raises(CrashSimule):
        arbitre.jouer()

    suivant = InvocateurFactice()
    reprise = _arbitre(config, suivant)
    reprise.jouer()

    recap_serie_0 = _series(config)[0]["memoire"]["recap"]
    assert recap_serie_0.splitlines()[0] in suivant.prompts[0]
    assert _series(config)[1]["memoire"]["M_s"].endswith(recap_serie_0)


def test_a3_etat_run_recale_sur_les_logs(tmp_path):
    """Les logs font foi : un `etat_run.json` en retard est corrigé, pas suivi."""
    config = _config(tmp_path, Condition.SM, "Station", K=4, series=2)
    _arbitre(config).jouer()

    etat = EtatRun.charger(config.dossier)
    etat.derniere_session_close = 0  # simule un plantage entre les deux écritures
    etat.enregistrer(config.dossier)

    assert _arbitre(config, InvocateurFactice()).etat.derniere_session_close == 1


def test_a3_etat_run_illisible_ne_bloque_pas(tmp_path):
    """Un fichier d'état tronqué ne doit pas empêcher de repartir des logs."""
    config = _config(tmp_path, Condition.SM, "Station", K=4, series=2)
    _arbitre(config).jouer()
    (config.dossier / "etat_run.json").write_text("{tronqué", encoding="utf-8")

    assert _arbitre(config, InvocateurFactice()).etat.derniere_session_close == 1


# ==========================================================================
# A4 — équilibre des positions (PRD 3 §10.4)
# ==========================================================================


def test_a4_positions_exactement_equilibrees(tmp_path):
    arbitre = _jouer(tmp_path, Condition.SM, "Station", K=20, series=1)
    (serie,) = _series(arbitre.config)
    assert serie["positions"] == {"J1": 10, "J2": 10}


def test_a4_alternance_stricte_manche_par_manche(tmp_path):
    arbitre = _jouer(tmp_path, Condition.SM, "Station", K=20, series=1)
    for tour in _tours(arbitre.config):
        attendu = "J1" if tour["manche"] % 2 else "J2"
        assert tour["etat_reel"]["position_agent"] == attendu


def test_a4_alternance_independante_de_tout_le_reste():
    assert [position_agent(k) for k in range(1, 5)] == [
        Position.J1,
        Position.J2,
        Position.J1,
        Position.J2,
    ]


def test_a4_k_impair_refuse():
    """K impair rendrait l'équilibre des positions impossible : on refuse tôt."""
    with pytest.raises(ValueError, match="pair"):
        ConfigRun(condition=Condition.SM, bot="Station", replication=1, K=21)


# ==========================================================================
# A5 — le récap ne fuite jamais un sceau non dévoilé (PRD 3 §10.5)
# ==========================================================================


def test_a5_recap_dune_manche_close_par_retrait(tmp_path):
    """Manche jouée contre Over-folder : l'agent engage, le bot se retire,
    les sceaux ne sont pas comparés — le récap doit se taire."""
    file = [Action.BET, Action.FOLD]
    resultat = jouer_manche(lambda _: file.pop(0), lambda _: file.pop(0), Carte.C0, Carte.C2)
    ligne = ligne_manche(7, Position.J1, resultat)
    assert "non dévoilé" in ligne
    assert rendre_carte(Carte.C2) not in ligne


def test_a5_aucune_fuite_sur_un_run_entier(tmp_path):
    """Contre Over-folder, l'agent qui engage gagne sans abattage : on vérifie
    sur toutes les manches que le sceau adverse n'apparaît jamais."""
    arbitre = _jouer(tmp_path, Condition.ICL, "Over-folder", K=20, series=1)
    (serie,) = _series(arbitre.config)
    lignes = {
        int(re.match(r"épreuve (\d+)", ligne).group(1)): ligne
        for ligne in serie["memoire"]["recap"].splitlines()
        if ligne.startswith("épreuve")
    }
    assert len(lignes) == 20

    for tour in _tours(arbitre.config):
        if tour["historique_final"] is None:
            continue
        abattage = tour["historique_final"][-1] in ("check", "call")
        ligne = lignes[tour["manche"]]
        sceau_adverse = rendre_carte(Carte(tour["etat_reel"]["carte_bot"]))
        if abattage:
            assert sceau_adverse in ligne
        else:
            assert "non dévoilé" in ligne
            assert sceau_adverse not in ligne


def test_a5_recap_reste_obfusque(tmp_path):
    """Le récap est servi à l'agent : il tombe sous le filet d'obfuscation."""
    arbitre = _jouer(tmp_path, Condition.ICL, "GTO", K=20, series=1)
    (serie,) = _series(arbitre.config)
    assert violations_obfuscation(serie["memoire"]["recap"]) == ()


# ==========================================================================
# Gel de la mémoire, échecs de harnais, défauts de parsing
# ==========================================================================


def test_gel_restaure_avant_chaque_manche(tmp_path):
    """L'agent qui écrit pendant qu'il joue : l'écriture est jetée, mais loguée."""
    config = _config(tmp_path, Condition.AE, "Station", K=4, series=1)
    invocateur = InvocateurFactice()
    arbitre = _arbitre(config, invocateur)
    invocateur.effet_de_bord = lambda: arbitre.store.notes.write_text(
        "note clandestine", encoding="utf-8"
    )
    arbitre.jouer()

    (serie,) = _series(config)
    assert serie["memoire"]["ecritures_intra_serie"] == 4
    assert serie["memoire"]["gel_rompu"] is False
    assert serie["memoire"]["M_s"] == ""
    assert any("ecriture_intra_serie" in t["flags"] for t in _tours(config))


def test_erreur_harnais_rejoue_la_manche_avec_la_meme_donne(tmp_path):
    """Un échec persistant ne saute jamais une manche : elle est rejouée à
    l'identique, et le drapeau part dans les logs."""
    config = _config(tmp_path, Condition.SM, "Station", K=4, series=1)
    _arbitre(config, InvocateurFactice(echecs=2)).jouer()

    tours = _tours(config)
    premiere = next(t for t in tours if t["manche"] == 1)
    attendue = donne(config.graine, config.replication, 0, 1)
    assert premiere["etat_reel"]["carte_agent"] == int(attendue.agent)
    assert "erreur_harnais" in premiere["flags"]
    assert _series(config)[0]["defauts"]["erreurs_harnais"] == 2
    assert len({t["manche"] for t in tours}) == 4


def test_erreur_harnais_persistante_arrete_le_run(tmp_path):
    """Au-delà des tentatives, on s'arrête : un run troué ne sert à personne."""
    config = _config(tmp_path, Condition.SM, "Station", K=4, series=1)
    arbitre = _arbitre(config, InvocateurFactice(echecs=TENTATIVES_MANCHE + 1))
    with pytest.raises(ErreurArbitre, match="tentatives"):
        arbitre.jouer()


def test_action_par_defaut_exclue_de_pi_hat(tmp_path):
    """Une action imposée par le harnais dit quelque chose du harnais, pas de
    la politique de l'agent : elle est comptée à part, jamais dans π̂."""
    config = _config(tmp_path, Condition.SM, "Station", K=4, series=1)
    _arbitre(config, InvocateurFactice(charabia=2)).jouer()

    (serie,) = _series(config)
    assert serie["defauts"]["actions_par_defaut"] == 1
    assert serie["defauts"]["relances"] == 1
    effectifs = sum(v["n"] for v in serie["pi_hat"].values() if isinstance(v, dict))
    assert effectifs == 3


# ==========================================================================
# Critère de plateau (PRD 3 §6.2)
# ==========================================================================


def test_plateau_pas_evalue_avant_huit_series():
    assert evaluer_plateau([0.5] * 7).evalue is False
    assert evaluer_plateau([0.5] * 8).evalue is True


def test_plateau_declare_sur_une_courbe_stabilisee():
    plateau = evaluer_plateau([0.9, 0.7, 0.5, 0.4, 0.31, 0.30, 0.30, 0.29])
    assert plateau.declare is True


def test_plateau_refuse_pendant_une_descente():
    plateau = evaluer_plateau([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2])
    assert plateau.evalue and not plateau.declare
    assert plateau.pente < -0.02


def test_plateau_refuse_sur_des_dents_de_scie():
    """Pente nulle, dispersion forte : c'est de l'oubli périodique, pas un
    plateau — le critère à deux volets est là exactement pour ça."""
    plateau = evaluer_plateau([0.5, 0.2, 0.5, 0.2, 0.5, 0.2, 0.5, 0.2])
    assert plateau.evalue and not plateau.declare
    assert plateau.dispersion >= 0.05


def test_pente_regression_sur_une_droite_connue():
    assert pente_regression([1.0, 2.0, 3.0, 4.0]) == pytest.approx(1.0)
    assert pente_regression([4.0, 3.0, 2.0, 1.0]) == pytest.approx(-1.0)
    assert pente_regression([2.0]) == 0.0


def test_arret_au_plateau_avec_marge(tmp_path):
    """Le run s'arrête `MARGE_PLATEAU` séries après la déclaration, pas avant
    (spec §6 : « plateau + marge »)."""
    config = _config(tmp_path, Condition.ICL, "Station", K=4, series=20)
    arbitre = _arbitre(config)
    arbitre.jouer()

    series = _series(config)
    declarees = [s["session"] for s in series if s["plateau"]["declare"]]
    assert declarees, "l'agent factice est constant : le plateau doit se déclarer"
    assert series[-1]["session"] == declarees[0] + 2


def test_sm_ne_sarrete_jamais_au_plateau(tmp_path):
    """SM n'accumule rien : ses 3 séries se jouent jusqu'au bout."""
    arbitre = _jouer(tmp_path, Condition.SM, "Station", K=4, series=None)
    assert len(_series(arbitre.config)) == 3


# ==========================================================================
# Intégrité de clôture (PRD 3 §8)
# ==========================================================================


def test_integrite_detecte_des_donnes_dappariement_rompu(tmp_path):
    """Une empreinte de donnes falsifiée doit être vue à la clôture."""
    arbitre = _jouer(tmp_path, Condition.SM, "Station", K=4, series=1)
    chemin = arbitre.config.dossier_logs / "sessions.jsonl"
    ligne = json.loads(chemin.read_text(encoding="utf-8"))
    ligne["hash_donnes"] = "sha256:falsifie"
    chemin.write_text(json.dumps(ligne, ensure_ascii=False) + "\n", encoding="utf-8")

    rapport = arbitre.clore()
    assert not rapport.ok
    assert any("empreinte de donnes" in a for a in rapport.anomalies)


def test_integrite_compare_les_runs_apparies(tmp_path):
    """Deux runs de la même réplication sous la même racine se contrôlent l'un
    l'autre — c'est le seul contrôle qui prouve l'appariement a posteriori."""
    sm = _jouer(tmp_path, Condition.SM, "Station", K=4, series=1)
    icl = _jouer(tmp_path, Condition.ICL, "Station", K=4, series=1)
    rapport = icl.clore()
    assert rapport.ok, rapport.anomalies
    assert sm.config.run_id in rapport.controles["runs_apparies"]


def test_integrite_detecte_une_serie_incomplete(tmp_path):
    arbitre = _jouer(tmp_path, Condition.SM, "Station", K=4, series=1)
    chemin = arbitre.config.dossier_logs / "turns.jsonl"
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    chemin.write_text("\n".join(lignes[:-1]) + "\n", encoding="utf-8")

    rapport = arbitre.clore()
    assert any("manches loguées" in a for a in rapport.anomalies)


def test_temoin_disolation_detecte_une_fuite(tmp_path):
    """Le témoin retrouvé ailleurs = deux runs partagent un store."""
    store = Store(chemin=tmp_path / "store")
    voisin = tmp_path / "voisin"
    (voisin / "memories").mkdir(parents=True)
    marqueur = poser_temoin(store, "SM-station-r1")

    verifier_temoin(store, marqueur, autres_stores=[voisin])
    (voisin / "memories" / "MEMORY.md").write_text(marqueur, encoding="utf-8")
    with pytest.raises(EchecCanari, match="isolés"):
        verifier_temoin(store, marqueur, autres_stores=[voisin])


def test_temoin_disolation_detecte_un_store_remplace(tmp_path):
    store = Store(chemin=tmp_path / "store")
    marqueur = poser_temoin(store, "SM-station-r1")
    (store.chemin / FICHIER_TEMOIN).unlink()
    with pytest.raises(EchecCanari, match="témoin"):
        verifier_temoin(store, marqueur)


# ==========================================================================
# Affichage du run (régression)
# ==========================================================================


def test_affichage_survit_a_une_console_cp1252(tmp_path, monkeypatch):
    """Le premier mini-run est tombé **avant le moindre appel API** : la console
    Windows est en cp1252 et l'en-tête contenait un « ≤ ». On dégrade
    désormais l'affichage plutôt que le run — les journaux, eux, restent en
    UTF-8, écrits par le journal et non par ici."""
    arbitre = _jouer(tmp_path, Condition.SM, "Station", K=4, series=1)
    (serie,) = _series(arbitre.config)
    serie = dict(serie)
    # Une anomalie d'intégrité cite des caractères qu'on ne peut pas prévoir.
    serie["plateau"] = {"declare": "π̂ ≠ 0"}

    console = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", newline="")
    monkeypatch.setattr(sys, "stdout", console)
    cli._console_tolerante()
    cli._tracer(serie)  # ne doit pas lever


def test_entete_de_run_encodable_en_cp1252(tmp_path):
    """Nos propres chaînes, elles, doivent passer sans filet : le filet est là
    pour les textes qu'on ne maîtrise pas, pas pour excuser les nôtres."""
    config = _config(tmp_path, Condition.SM, "Station", K=4, series=1)
    entete = f"run {config.run_id} — K={config.K}, séries au plus {config.series_prevues}"
    entete.encode("cp1252")


# ==========================================================================
# Orchestration de campagne (PRD 3 §1 et §8)
# ==========================================================================


def test_matrice_de_campagne_couvre_27_runs():
    runs = matrice_campagne()
    assert len(runs) == 27 == len(set(runs))
    assert identifiant(Condition.AE, "Station", 2) == "AE-station-r2"


def test_affectation_machines_reproductible_et_equilibree():
    runs = matrice_campagne()
    a = affecter_machines(runs, ["victus", "mac-m2"])
    assert a == affecter_machines(runs, ["victus", "mac-m2"])
    assert sorted(a) == sorted(runs)
    assert abs(sum(1 for m in a.values() if m == "victus") - 27 / 2) <= 1


def test_affectation_mono_machine():
    """Sans Mac opérationnel, la campagne est mono-machine : l'effet-machine
    disparaît avec elle, l'affectation reste loguée."""
    assert set(affecter_machines(matrice_campagne(), ["victus"]).values()) == {"victus"}
