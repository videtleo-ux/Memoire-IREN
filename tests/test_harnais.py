"""Suite du harnais mémoire — critères d'acceptation du PRD 2 §8.

Aucun appel API : l'invocateur est substitué par un double en mémoire. Ce que
la suite garde sous contrôle, c'est ce qu'aucun log ne rattrapera après coup —
l'équité entre conditions, l'isolation des runs, le gel intra-série et
l'obfuscation des textes servis.
"""

from __future__ import annotations

from itertools import permutations, product
from pathlib import Path

import pytest

from harnais import (
    Condition,
    ErreurHarnais,
    HarnaisAutoEcrit,
    HarnaisHistorique,
    HarnaisSansMemoire,
    Parsing,
    Reponse,
    Store,
    construire_harnais,
    creer_store,
    extraire_action,
    marqueur_canari,
    verifier_isolation,
)
from harnais import gabarits, gel
from harnais.stores import EchecCanari, TOOLSET_MEMOIRE, TOOLSET_SANS_OUTIL
from moteur import (
    CARTES,
    INFOSETS,
    Action,
    Carte,
    Contexte,
    InfoSet,
    Position,
    jouer_manche,
)
from moteur.lexique import rendre_action, textes_destines_a_lagent, violations_obfuscation


# ==========================================================================
# Outils de test
# ==========================================================================


class InvocateurFactice:
    """Double de `hermes -z` : rend des réponses scriptées, note les appels."""

    def __init__(self, *textes: str, echec: bool = False):
        self.textes = list(textes) or ["ACTION: retenir"]
        self.echec = echec
        self.appels: list[tuple[str, str]] = []
        self.effet_de_bord = None  # callable(store) déclenché à chaque appel

    def __call__(self, prompt: str, toolset: str = TOOLSET_SANS_OUTIL) -> Reponse:
        self.appels.append((prompt, toolset))
        if self.effet_de_bord is not None:
            self.effet_de_bord()
        texte = self.textes[min(len(self.appels) - 1, len(self.textes) - 1)]
        return Reponse(
            texte="" if self.echec else texte,
            code_retour=1 if self.echec else 0,
            latence_ms=12,
            tentatives=3 if self.echec else 1,
            tokens_entree=800,
            tokens_sortie=40,
            modele="modele-de-test",
            erreur="sortie vide" if self.echec else None,
        )

    @property
    def prompts(self) -> list[str]:
        return [prompt for prompt, _ in self.appels]


SORTIES_DECHEC = [
    # Relevé le 2026-08-21 en basculant sur un modèle payant sans crédits :
    # `hermes -z` termine avec le code 0 et imprime l'erreur sur stdout.
    "API call failed after 3 retries: HTTP 404: Model 'openai/gpt-5.6-luna' "
    "requires available credits. Your account balance is too low.",
    "Error: HTTP 429: too many requests",
    "Rate limit exceeded, retry later",
]


@pytest.mark.parametrize("texte", SORTIES_DECHEC)
def test_h_echec_fournisseur_rendu_sur_stdout_detecte(texte):
    """Un échec de fournisseur déguisé en réponse ne doit jamais passer pour
    une décision de l'agent : sans ce filet, la série se remplit de manches
    `action_par_defaut` **loguées comme des données**."""
    from harnais.hermes import echec_fournisseur

    assert echec_fournisseur(texte) is not None


def test_h_vraie_reponse_de_modele_non_prise_pour_un_echec():
    """Le filet ne doit pas mordre sur une délibération légitime."""
    from harnais.hermes import echec_fournisseur

    for texte in [
        "Mon sceau Rhun domine les deux autres.\nACTION: engager",
        "Je retiens, l'adversaire n'a pas engagé.\nACTION: retenir",
        "Le résultat de l'épreuve précédente a échoué à m'éclairer.\nACTION: couvrir",
    ]:
        assert echec_fournisseur(texte) is None, texte


def _store(tmp_path: Path, nom: str = "store") -> Store:
    return creer_store(tmp_path / nom)


IFS_OUVERTURE = InfoSet(Position.J1, Carte.C1, Contexte.OUVERTURE)
IFS_FACE_MISE = InfoSet(Position.J2, Carte.C1, Contexte.FACE_MISE)


# ==========================================================================
# H1 — obfuscation de tous les textes servis (prolonge T8 du PRD 1)
# ==========================================================================


def test_h1_textes_declares_sans_motif_interdit():
    """Le registre du lexique contient bien les gabarits, et rien n'y fuite."""
    textes = textes_destines_a_lagent()
    assert "gabarit.regles" in textes, "les gabarits doivent s'enregistrer à l'import"
    for etiquette, texte in textes.items():
        assert violations_obfuscation(texte) == (), f"{etiquette} : {violations_obfuscation(texte)}"


def test_h1_prompts_de_tous_les_infosets_sans_motif_interdit():
    """Les 12 info-sets, avec et sans slot, produisent des prompts propres."""
    slots = [None, gabarits.rubrique_slot(gabarits.ENTETE_SLOT_AE, "notes libres")]
    for infoset, slot in product(INFOSETS, slots):
        prompt = gabarits.construire_prompt(infoset, (), slot)
        assert violations_obfuscation(prompt) == (), f"{infoset} : {violations_obfuscation(prompt)}"


def test_h1_recaps_exhaustifs_sans_motif_interdit():
    """Toutes les manches possibles, résumées, restent obfusquées.

    Balayage exhaustif : 6 donnes × 2 positions × tous les déroulés. C'est le
    texte le plus exposé (chiffres de solde collés à des noms de sceau), donc
    celui qu'on énumère plutôt qu'on échantillonne.
    """
    for (carte_j1, carte_j2), position in product(permutations(CARTES, 2), Position):
        for sequence in _sequences_possibles():
            ligne = _ligne_depuis_sequence(carte_j1, carte_j2, position, sequence, numero=137)
            assert violations_obfuscation(ligne) == (), ligne


def _sequences_possibles() -> list[tuple[Action, ...]]:
    return [
        (Action.CHECK, Action.CHECK),
        (Action.CHECK, Action.BET, Action.FOLD),
        (Action.CHECK, Action.BET, Action.CALL),
        (Action.BET, Action.FOLD),
        (Action.BET, Action.CALL),
    ]


def _ligne_depuis_sequence(carte_j1, carte_j2, position_agent, sequence, numero):
    file = list(sequence)
    resultat = jouer_manche(lambda _: file.pop(0), lambda _: file.pop(0), carte_j1, carte_j2)
    carte_agent = carte_j1 if position_agent is Position.J1 else carte_j2
    carte_adverse = carte_j2 if position_agent is Position.J1 else carte_j1
    solde = resultat.gain_j1 if position_agent is Position.J1 else -resultat.gain_j1
    return gabarits.ligne_recap(
        numero,
        position_agent,
        carte_agent,
        [(ifs.position, action) for ifs, action in resultat.historique],
        carte_adverse if resultat.abattage else None,
        solde,
    )


def test_h1_recap_ne_fuite_jamais_un_sceau_non_devoile():
    """Manche close par un retrait : le sceau adverse n'apparaît nulle part.

    Critère PRD 3 §10.5. Une fuite ici donnerait à l'agent une information que
    la table ne lui a pas donnée — et gonflerait son écart sans qu'aucun log
    ne le signale.
    """
    for (carte_j1, carte_j2), position in product(permutations(CARTES, 2), Position):
        for sequence in ((Action.BET, Action.FOLD), (Action.CHECK, Action.BET, Action.FOLD)):
            ligne = _ligne_depuis_sequence(carte_j1, carte_j2, position, sequence, 1)
            carte_adverse = carte_j2 if position is Position.J1 else carte_j1
            assert "non dévoilé" in ligne
            # Le sceau de l'agent peut légitimement apparaître ; celui de
            # l'adversaire, jamais — sauf s'il détient le même nom, cas exclu
            # par la donne.
            fragment = ligne.split("votre sceau")[1].split(",", 1)[1]
            from moteur.lexique import rendre_carte

            assert rendre_carte(carte_adverse) not in fragment


# ==========================================================================
# H2 — équité inter-conditions (PRD 2 §8.1)
# ==========================================================================


def test_h2_prompts_identiques_hors_slot():
    """À info-set égal, les 3 conditions ne diffèrent que par le slot."""
    sans = gabarits.construire_prompt(IFS_OUVERTURE, (), None)
    icl = gabarits.construire_prompt(
        IFS_OUVERTURE, (), gabarits.rubrique_slot(gabarits.ENTETE_SLOT_ICL, "récap")
    )
    ae = gabarits.construire_prompt(
        IFS_OUVERTURE, (), gabarits.rubrique_slot(gabarits.ENTETE_SLOT_AE, "notes")
    )

    for prompt in (sans, icl, ae):
        assert prompt.startswith(gabarits.REGLES)
        assert prompt.endswith(gabarits.rubrique_tache(IFS_OUVERTURE.actions_legales))
    assert _sans_slot(icl) == sans
    assert _sans_slot(ae) == sans


def _sans_slot(prompt: str) -> str:
    rubriques = [r for r in prompt.split("\n\n") if not r.startswith(("[HISTORIQUE", "[VOS NOTES"))]
    return "\n\n".join(rubriques)


def test_h2_hash_des_regles_stable():
    """Le hash logué est celui du texte servi, et il ne bouge pas."""
    from hashlib import sha256

    attendu = "sha256:" + sha256(gabarits.REGLES.encode("utf-8")).hexdigest()[:16]
    assert gabarits.HASH_REGLES == attendu


def test_h2_les_trois_conditions_traversent_le_meme_code(tmp_path):
    """Même invocateur, même toolset, même consigne — seul le slot change."""
    prompts = {}
    for condition, fabrique in (
        (Condition.SM, lambda inv: HarnaisSansMemoire(invocateur=inv)),
        (Condition.ICL, lambda inv: HarnaisHistorique(invocateur=inv)),
        (Condition.AE, lambda inv: HarnaisAutoEcrit(invocateur=inv, store=_store(tmp_path, condition.value))),
    ):
        invocateur = InvocateurFactice("ACTION: engager")
        harnais = fabrique(invocateur)
        harnais.ouvrir_session(0)
        harnais.decider(IFS_OUVERTURE)
        prompts[condition] = invocateur.prompts[0]
        assert invocateur.appels[0][1] == TOOLSET_SANS_OUTIL

    assert _sans_slot(prompts[Condition.ICL]) == prompts[Condition.SM]
    assert _sans_slot(prompts[Condition.AE]) == prompts[Condition.SM]


# ==========================================================================
# H3 — parsing (PRD 2 §4)
# ==========================================================================


@pytest.mark.parametrize(
    "sortie, attendu, statut",
    [
        ("ACTION: couvrir", Action.CALL, Parsing.OK),
        ("blabla\nACTION: se retirer", Action.FOLD, Parsing.OK),
        ("**ACTION:** couvrir", Action.CALL, Parsing.OK),
        ("ACTION : COUVRIR.", Action.CALL, Parsing.OK),
        ("action: se retirer", Action.FOLD, Parsing.OK),
        ("Je vais couvrir.", Action.CALL, Parsing.REPLI),
        ("je préfère me retirer", Action.FOLD, Parsing.REPLI),
        ("je vais couvrir, non, je me retire", Action.FOLD, Parsing.REPLI),
        ("ACTION: engager", None, Parsing.DEFAUT),  # illégale à cet info-set
        ("aucune idée", None, Parsing.DEFAUT),
        ("", None, Parsing.DEFAUT),
    ],
)
def test_h3_extraction_action(sortie, attendu, statut):
    action, parsing = extraire_action(sortie, IFS_FACE_MISE.actions_legales)
    assert (action, parsing) == (attendu, statut)


def test_h3_ligne_action_prime_sur_le_texte_libre():
    """Le format imposé fait foi, même si le texte libre dit autre chose."""
    action, parsing = extraire_action(
        "je pense couvrir\nACTION: se retirer", IFS_FACE_MISE.actions_legales
    )
    assert (action, parsing) == (Action.FOLD, Parsing.OK)


def test_h3_tous_les_termes_du_lexique_sont_reconnus():
    for infoset in INFOSETS:
        for action in infoset.actions_legales:
            sortie = f"ACTION: {rendre_action(action)}"
            assert extraire_action(sortie, infoset.actions_legales) == (action, Parsing.OK)


def test_h3_relance_puis_defaut_passif():
    """Sortie inexploitable deux fois → action passive + drapeau (PRD 2 §4)."""
    invocateur = InvocateurFactice("bla", "toujours bla")
    harnais = HarnaisSansMemoire(invocateur=invocateur)
    decision = harnais.decider(IFS_FACE_MISE)

    assert decision.action is IFS_FACE_MISE.action_passive
    assert decision.parsing is Parsing.DEFAUT
    assert "action_par_defaut" in decision.flags
    assert decision.invocations == 2
    assert gabarits.REGLES in invocateur.prompts[1], "la relance rejoue le prompt entier"
    assert "[FORMAT]" in invocateur.prompts[1]
    assert decision.tokens_entree == 1600, "les tokens des deux appels s'additionnent"


def test_h3_relance_reussie():
    invocateur = InvocateurFactice("bla", "ACTION: couvrir")
    decision = HarnaisSansMemoire(invocateur=invocateur).decider(IFS_FACE_MISE)
    assert (decision.action, decision.parsing) == (Action.CALL, Parsing.RELANCE)
    assert "action_par_defaut" not in decision.flags


def test_h3_sortie_brute_integralement_conservee():
    """Le texte libre est la matière du détecteur de dé-obfuscation (PRD 4)."""
    invocateur = InvocateurFactice("mon raisonnement complet\nACTION: couvrir")
    decision = HarnaisSansMemoire(invocateur=invocateur).decider(IFS_FACE_MISE)
    assert "mon raisonnement complet" in decision.sortie_brute


def test_h3_pseudo_appel_doutil_signale():
    """Sortie constatée au canari du 2026-08-21 sur le modèle gratuit : privé
    d'outils, il écrit un appel d'outil en clair au lieu de répondre."""
    sortie = "<tool_calls:6124c78e>\n<tool_call:6124c78e>terminal`\ncommand`\nmkdir -p /tmp"
    invocateur = InvocateurFactice(sortie, "ACTION: couvrir")
    decision = HarnaisSansMemoire(invocateur=invocateur).decider(IFS_FACE_MISE)

    assert "sortie_pseudo_outil" in decision.flags
    assert decision.parsing is Parsing.RELANCE, "la relance rattrape le coup"


def test_h3_sortie_normale_ne_declenche_pas_le_drapeau():
    invocateur = InvocateurFactice("je réfléchis puis\nACTION: couvrir")
    decision = HarnaisSansMemoire(invocateur=invocateur).decider(IFS_FACE_MISE)
    assert "sortie_pseudo_outil" not in decision.flags


def test_h3_echec_persistant_leve_erreur_harnais():
    """La manche doit être rejouée à l'identique, jamais sautée (PRD 2 §3)."""
    harnais = HarnaisSansMemoire(invocateur=InvocateurFactice(echec=True))
    with pytest.raises(ErreurHarnais):
        harnais.decider(IFS_OUVERTURE)


# ==========================================================================
# H4 — isolation par run (PRD 2 §8.2)
# ==========================================================================


def test_h4_store_neuf_est_vierge_et_configure(tmp_path):
    store = _store(tmp_path)
    assert store.notes.read_text(encoding="utf-8") == ""
    config = store.config.read_text(encoding="utf-8")
    assert 'memory_enabled: false' in config, "mémoire native éteinte pendant les manches"
    assert 'user_profile_enabled: false' in config, "USER.md neutralisé"
    assert "nudge_interval: 0" in config, "pas de revue d'arrière-plan"
    assert "creation_nudge_interval: 0" in config, "pas de skills auto-créées"


def test_h4_store_refuse_un_dossier_deja_peuple(tmp_path):
    _store(tmp_path)
    with pytest.raises(ValueError):
        creer_store(tmp_path / "store")


def test_h4_canari_deux_runs_simultanes(tmp_path):
    """Deux stores en parallèle : les marqueurs ne se contaminent pas."""
    global_home = tmp_path / "global"
    gel.ecrire_notes(global_home, "mémoire de la machine")
    run_a, run_b = _store(tmp_path, "a"), _store(tmp_path, "b")

    marqueur_a, marqueur_b = marqueur_canari("A-r1"), marqueur_canari("B-r1")
    gel.ecrire_notes(run_a.chemin, marqueur_a)
    gel.ecrire_notes(run_b.chemin, marqueur_b)

    verifier_isolation(run_a, marqueur_a, [run_b.chemin], global_home)
    verifier_isolation(run_b, marqueur_b, [run_a.chemin], global_home)


def test_h4_canari_detecte_une_fuite(tmp_path):
    """Un marqueur retrouvé ailleurs = run refusé, pas un avertissement."""
    run_a, run_b = _store(tmp_path, "a"), _store(tmp_path, "b")
    marqueur = marqueur_canari("A-r1")
    gel.ecrire_notes(run_a.chemin, marqueur)
    gel.ecrire_notes(run_b.chemin, f"contaminé : {marqueur}")

    with pytest.raises(EchecCanari, match="pas isolés"):
        verifier_isolation(run_a, marqueur, [run_b.chemin])


def test_h4_canari_detecte_une_ecriture_hors_store(tmp_path):
    run = _store(tmp_path, "a")
    with pytest.raises(EchecCanari, match="marqueur absent"):
        verifier_isolation(run, marqueur_canari("A-r1"))


def test_h4_canari_par_invocation_laisse_le_store_vierge(tmp_path):
    """Le marqueur écrit par l'agent est vérifié, puis effacé : `M_0` est vide."""
    from harnais.canari import canari

    store = _store(tmp_path)
    invocateur = InvocateurFactice("enregistré", "je ne peux pas")
    invocateur.effet_de_bord = lambda: _ecrire_marqueur_si_reflexion(store, invocateur)

    rapport = canari(store, "AE-station-r2", invocateur)

    assert rapport.ecriture_confirmee
    assert rapport.ecriture_bloquee_en_manche is True
    assert gel.lire_notes(store.chemin) == "", "M_0 doit rester vierge"
    assert "memory_enabled: false" in store.config.read_text(encoding="utf-8")


def _ecrire_marqueur_si_reflexion(store, invocateur):
    """Simule le comportement d'Hermes : il n'écrit que si l'outil mémoire est là."""
    prompt, toolset = invocateur.appels[-1]
    if toolset == TOOLSET_MEMOIRE:
        gel.ecrire_notes(store.chemin, prompt.split("\n\n")[1])


def test_h4_canari_refuse_une_ecriture_possible_en_manche(tmp_path):
    """Si la mémoire reste écrivable pendant les manches, le gel ne vaut rien."""
    from harnais.canari import canari

    store = _store(tmp_path)
    invocateur = InvocateurFactice("enregistré", "noté aussi")
    # Écrit quel que soit le toolset : exactement la régression que ce canari
    # doit intercepter (config mal posée, clé renommée en amont…).
    invocateur.effet_de_bord = lambda: gel.ecrire_notes(
        store.chemin, f"{invocateur.appels[-1][0].split(chr(10) * 2)[1]} #{len(invocateur.appels)}"
    )
    with pytest.raises(EchecCanari, match="configuration de manche"):
        canari(store, "AE-station-r2", invocateur)


def test_h4_canari_echoue_si_lagent_necrit_rien(tmp_path):
    """Écriture non aboutie = isolation non prouvée = run refusé."""
    from harnais.canari import canari

    store = _store(tmp_path)
    with pytest.raises(EchecCanari, match="marqueur absent"):
        canari(store, "AE-station-r2", InvocateurFactice("enregistré"))


def test_h4_canari_fichier_ne_pretend_pas_prouver_lecriture(tmp_path):
    from harnais.canari import canari_fichier

    rapport = canari_fichier(_store(tmp_path), "SM-station-r1")
    assert rapport.ecriture_confirmee is False


def test_h4_stores_actifs_listes(tmp_path):
    from harnais.canari import stores_actifs

    for nom in ("run-a", "run-b"):
        creer_store(tmp_path / nom / "hermes-home")
    assert [p.parent.name for p in stores_actifs(tmp_path)] == ["run-a", "run-b"]


# ==========================================================================
# H5 — gel intra-série (PRD 2 §8.3, décision D2)
# ==========================================================================


def test_h5_modification_en_cours_de_serie_est_annulee(tmp_path):
    """MEMORY.md modifié pendant la série → la manche suivante voit toujours M_s."""
    store = _store(tmp_path)
    gel.ecrire_notes(store.chemin, "note initiale")
    harnais = HarnaisAutoEcrit(invocateur=InvocateurFactice("ACTION: retenir"), store=store)
    m_s = harnais.ouvrir_session(0)

    gel.ecrire_notes(store.chemin, "note écrite en douce pendant la série")
    modifies = harnais.avant_manche()

    assert modifies == ("MEMORY.md",), "l'écriture doit être détectée avant d'être jetée"
    assert gel.lire_notes(store.chemin) == "note initiale"
    assert harnais.slot().endswith(m_s), "le slot sert toujours le snapshot gelé"


def test_h5_ecriture_pendant_une_decision_est_loguee(tmp_path):
    """L'agent qui écrit pendant qu'il joue : jeté, mais observé."""
    store = _store(tmp_path)
    gel.ecrire_notes(store.chemin, "M_s")
    invocateur = InvocateurFactice("ACTION: retenir")
    harnais = HarnaisAutoEcrit(invocateur=invocateur, store=store)
    harnais.ouvrir_session(0)
    invocateur.effet_de_bord = lambda: gel.ecrire_notes(store.chemin, "je note ça")

    decision = harnais.decider(IFS_OUVERTURE)

    assert "ecriture_intra_serie" in decision.flags
    assert gel.lire_notes(store.chemin) == "M_s"


def test_h5_fichier_cree_en_cours_de_serie_est_supprime(tmp_path):
    """Un canal mémoire apparu en cours de série n'a pas plus de droits."""
    store = _store(tmp_path)
    harnais = HarnaisAutoEcrit(invocateur=InvocateurFactice(), store=store)
    harnais.ouvrir_session(0)

    (gel.dossier_memoire(store.chemin) / "USER.md").write_text("profil", encoding="utf-8")
    harnais.avant_manche()

    assert not (gel.dossier_memoire(store.chemin) / "USER.md").exists()


def test_h5_serie_sans_ecriture_ne_declenche_rien(tmp_path):
    store = _store(tmp_path)
    gel.ecrire_notes(store.chemin, "stable")
    harnais = HarnaisAutoEcrit(invocateur=InvocateurFactice("ACTION: retenir"), store=store)
    harnais.ouvrir_session(0)
    decision = harnais.decider(IFS_OUVERTURE)
    assert decision.flags == ()
    assert harnais.avant_manche() == ()


# ==========================================================================
# H6 — les trois conditions (PRD 2 §5, §8.5)
# ==========================================================================


def test_h6_sm_ne_montre_aucune_trace_du_passe():
    invocateur = InvocateurFactice("ACTION: retenir")
    harnais = HarnaisSansMemoire(invocateur=invocateur)
    harnais.ouvrir_session(0)
    harnais.decider(IFS_OUVERTURE)
    harnais.fermer_session(0, "récap de la série 0 : beaucoup d'informations")
    harnais.ouvrir_session(1)
    harnais.decider(IFS_OUVERTURE)

    for prompt in invocateur.prompts:
        assert "[VOS NOTES]" not in prompt
        assert "[HISTORIQUE" not in prompt
        assert "récap" not in prompt
    assert invocateur.prompts[0] == invocateur.prompts[1], "contexte strictement neuf"


def test_h6_icl_accumule_a_la_frontiere_et_ne_bouge_pas_intra_serie():
    invocateur = InvocateurFactice("ACTION: retenir")
    harnais = HarnaisHistorique(invocateur=invocateur)

    harnais.ouvrir_session(0)
    harnais.decider(IFS_OUVERTURE)
    assert "(rien pour l'instant)" in invocateur.prompts[-1]

    harnais.fermer_session(0, "récap-série-0")
    # La fermeture ne doit rien changer tant que la série suivante n'est pas
    # ouverte : le slot est gelé, pas vivant.
    assert "récap-série-0" not in harnais.slot()

    harnais.ouvrir_session(1)
    harnais.decider(IFS_OUVERTURE)
    harnais.decider(IFS_OUVERTURE)
    assert "récap-série-0" in invocateur.prompts[-1]
    assert invocateur.prompts[-1] == invocateur.prompts[-2], "slot figé intra-série"


def test_h6_icl_frontiere_sans_appel_llm():
    """L'accumulation ICL est mécanique : aucune étape de modèle (PRD 2 §5)."""
    invocateur = InvocateurFactice("ACTION: retenir")
    harnais = HarnaisHistorique(invocateur=invocateur)
    harnais.ouvrir_session(0)
    harnais.fermer_session(0, "récap")
    assert invocateur.appels == []


def test_h6_icl_fenetre_evince_les_series_entieres():
    """La fenêtre garde des séries entières, jamais un demi-récap."""
    harnais = HarnaisHistorique(invocateur=InvocateurFactice(), fenetre_tokens=100)
    for serie in range(6):
        harnais.ouvrir_session(serie)
        harnais.fermer_session(serie, f"récap-{serie} " + "x" * 200)

    harnais.ouvrir_session(6)
    slot = harnais.memoire_courante()
    assert "récap-5" in slot, "la série la plus récente est toujours là"
    assert "récap-0" not in slot, "les séries anciennes sont évincées"
    for serie in range(6):
        if f"récap-{serie}" in slot:
            assert slot.count("x" * 200) >= 1, "une série retenue l'est en entier"


def test_h6_ae_slot_est_le_snapshot_gele(tmp_path):
    store = _store(tmp_path)
    gel.ecrire_notes(store.chemin, "il couvre toujours")
    invocateur = InvocateurFactice("ACTION: engager")
    harnais = HarnaisAutoEcrit(invocateur=invocateur, store=store)
    harnais.ouvrir_session(3)
    harnais.decider(IFS_OUVERTURE)

    assert "[VOS NOTES]" in invocateur.prompts[0]
    assert "il couvre toujours" in invocateur.prompts[0]


def test_h6_ae_ne_voit_jamais_le_recap_pendant_les_manches(tmp_path):
    store = _store(tmp_path)
    invocateur = InvocateurFactice("ACTION: retenir", "noté", "ACTION: retenir")
    harnais = HarnaisAutoEcrit(invocateur=invocateur, store=store)
    harnais.ouvrir_session(0)
    harnais.decider(IFS_OUVERTURE)
    harnais.fermer_session(0, "RECAP-SECRET")
    harnais.ouvrir_session(1)
    harnais.decider(IFS_OUVERTURE)

    prompts_de_manche = [p for p, t in invocateur.appels if t == TOOLSET_SANS_OUTIL]
    assert all("RECAP-SECRET" not in p for p in prompts_de_manche)
    prompts_de_reflexion = [p for p, t in invocateur.appels if t == TOOLSET_MEMOIRE]
    assert len(prompts_de_reflexion) == 1
    assert "RECAP-SECRET" in prompts_de_reflexion[0]


def test_h6_ae_memoire_native_rallumee_seulement_pour_la_reflexion(tmp_path):
    """La bascule de config est le seul moment où Hermes peut écrire."""
    store = _store(tmp_path)
    invocateur = InvocateurFactice("ACTION: retenir", "noté")
    etats: list[tuple[str, bool]] = []
    invocateur.effet_de_bord = lambda: etats.append(
        (
            invocateur.appels[-1][1],
            "memory_enabled: true" in store.config.read_text(encoding="utf-8"),
        )
    )
    harnais = HarnaisAutoEcrit(invocateur=invocateur, store=store)
    harnais.ouvrir_session(0)
    harnais.decider(IFS_OUVERTURE)
    harnais.fermer_session(0, "récap")

    assert etats == [(TOOLSET_SANS_OUTIL, False), (TOOLSET_MEMOIRE, True)]
    assert "memory_enabled: false" in store.config.read_text(encoding="utf-8"), (
        "la mémoire native doit être éteinte dès la réflexion terminée"
    )


def test_h6_ae_config_restauree_meme_si_la_reflexion_echoue(tmp_path):
    store = _store(tmp_path)
    harnais = HarnaisAutoEcrit(invocateur=InvocateurFactice(echec=True), store=store)
    harnais.ouvrir_session(0)
    with pytest.raises(ErreurHarnais):
        harnais.fermer_session(0, "récap")
    assert "memory_enabled: false" in store.config.read_text(encoding="utf-8")


def test_h6_ae_exige_un_store():
    with pytest.raises(ValueError, match="store"):
        HarnaisAutoEcrit(invocateur=InvocateurFactice())


def test_h6_fabrique_par_condition(tmp_path):
    store = _store(tmp_path)
    assert isinstance(construire_harnais(Condition.SM, InvocateurFactice()), HarnaisSansMemoire)
    assert isinstance(construire_harnais(Condition.ICL, InvocateurFactice()), HarnaisHistorique)
    assert isinstance(
        construire_harnais(Condition.AE, InvocateurFactice(), store), HarnaisAutoEcrit
    )


# ==========================================================================
# H7 — événements mémoire à la frontière (PRD 2 §5.2, PRD 4 §3)
# ==========================================================================


def test_h7_frontiere_ae_diffe_les_entrees(tmp_path):
    store = _store(tmp_path)
    gel.ecrire_notes(store.chemin, "entrée A\n§\nentrée B")
    invocateur = InvocateurFactice("j'ai mis à jour mes notes")
    harnais = HarnaisAutoEcrit(invocateur=invocateur, store=store)
    harnais.ouvrir_session(0)
    invocateur.effet_de_bord = lambda: gel.ecrire_notes(
        store.chemin, "entrée A\n§\nentrée C"
    )

    frontiere = harnais.fermer_session(0, "récap")

    types = {(e.type, e.detail) for e in frontiere.evenements}
    assert ("suppression", "entrée B") in types
    assert ("ajout", "entrée C") in types
    assert frontiere.m_s == "entrée A\n§\nentrée B"
    assert frontiere.m_s1 == "entrée A\n§\nentrée C"
    assert frontiere.sortie_reflexion == "j'ai mis à jour mes notes"


def test_h7_elagage_et_overflow_signales():
    trois = "a\n§\nb\n§\nc"
    assert any(e.type == "elagage" for e in gel.evenements_memoire(trois, "a"))
    assert not any(e.type == "elagage" for e in gel.evenements_memoire("a", trois))

    trop_long = "x" * 3000
    evenements = gel.evenements_memoire("", trop_long, limite_caracteres=2200)
    assert any(e.type == "overflow" for e in evenements)


def test_h7_notes_videes_ne_comptent_pas_pour_un_elagage():
    """Notes entièrement effacées : c'est une suppression, pas un élagage."""
    evenements = gel.evenements_memoire("a\n§\nb", "")
    assert {e.type for e in evenements} == {"suppression"}


def test_h7_sm_et_icl_ne_produisent_aucun_evenement_memoire(tmp_path):
    sm = HarnaisSansMemoire(invocateur=InvocateurFactice())
    sm.ouvrir_session(0)
    assert sm.fermer_session(0, "récap").evenements == ()

    icl = HarnaisHistorique(invocateur=InvocateurFactice())
    icl.ouvrir_session(0)
    assert icl.fermer_session(0, "récap").evenements == ()


# ==========================================================================
# H8 — invocateur réel (surface, sans appel réseau)
# ==========================================================================


def test_h8_environnement_purge_les_variables_hermes(monkeypatch, tmp_path):
    """Une variable `HERMES_*` du shell rerouterait le run en silence."""
    from harnais.hermes import _environnement

    monkeypatch.setenv("HERMES_MODEL", "modele-pirate")
    monkeypatch.setenv("HERMES_KANBAN_BOARD", "autre")
    monkeypatch.setenv("PATH", "/chemin")

    env = _environnement(_store(tmp_path))

    assert env["HERMES_HOME"] == str(tmp_path / "store")
    assert "HERMES_MODEL" not in env
    assert "HERMES_KANBAN_BOARD" not in env
    assert env["PATH"] == "/chemin"


def test_h8_reponse_en_echec_nest_pas_ok():
    assert not Reponse(texte="", code_retour=1, latence_ms=0, tentatives=3, erreur="boum").ok
    assert not Reponse(texte="   ", code_retour=0, latence_ms=0, tentatives=1).ok
    assert Reponse(texte="ACTION: retenir", code_retour=0, latence_ms=0, tentatives=1).ok
