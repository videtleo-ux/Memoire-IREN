"""Boucle d'un run : séries, manches, frontières, clôture (PRD 3 §2).

L'arbitre n'invente rien. Il tient les trois couches déjà construites à leurs
places respectives et garantit ce qu'aucune d'elles ne peut garantir seule :

- le moteur (PRD 1) règle les manches et mesure — il ne sait pas d'où viennent
  les cartes ;
- le harnais (PRD 2) fait parler l'agent sous la bonne condition mémoire — il
  ne sait pas ce qu'est une série ;
- le journal (PRD 4) écrit et valide — il ne sait pas ce qu'il faut écrire.

Ce que l'arbitre ajoute, et que personne d'autre ne fait :

1. **Les donnes communes.** Elles sont dérivées de la graine de campagne, pas
   tirées : deux conditions au même (r, s, k) voient les mêmes sceaux, octet
   pour octet (§4, `alea`).
2. **Le gel.** `avant_manche()` est appelé avant *chaque* manche, y compris
   avant chaque nouvelle tentative après un échec de harnais (décision D2).
3. **L'atomicité de la manche.** Les tours d'une manche ne sont écrits qu'une
   fois la manche terminée. Un échec en cours de manche laisse donc les logs
   propres et la manche est rejouée **avec la même donne** (PRD 2 §3) — jamais
   une demi-manche orpheline dans `turns.jsonl`, qui ferait échouer le rejeu.
4. **La frontière.** Récap canonique → mise à jour du slot → π̂ → écart →
   plateau → ligne de série → état de run, dans cet ordre.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from harnais import (
    Condition,
    Decision,
    ErreurHarnais,
    Harnais,
    InvocateurHermes,
    ParametresModele,
    Store,
    construire_harnais,
    creer_store,
)
from harnais.canari import canari, canari_fichier, stores_actifs
from harnais.gel import decouper_entrees
from journal import (
    ContexteRun,
    EtatReel,
    EvenementSession,
    EvenementTour,
    JournalRun,
    analyser,
)
from journal.deobfuscation import Drapeau
from moteur import (
    BOTS,
    Action,
    Decideur,
    InfoSet,
    Position,
    ResultatManche,
    decideur_depuis_politique,
    jouer_manche,
    numero,
)

from . import alea, etat as etat_module, integrite, mesure, recap

#: Manches par série (paramètre figé du PRD 0 §3, revalidé au pilote).
K_DEFAUT = 200

#: Séries par run (PRD 3 §3). SM n'a rien à accumuler : 3 points suffisent à
#: établir le plancher plat et sa variance. ICL et AE s'arrêtent au plateau,
#: bornés des deux côtés — le maximum ci-dessous borne le coût, et le minimum
#: de 8 séries est porté par le critère lui-même
#: (`mesure.SERIES_MIN_PLATEAU`), qui refuse d'évaluer avant : assez de points
#: pour distinguer plat, dents de scie et escalier même si la courbe se
#: stabilise vite.
SERIES_SM = 3
SERIES_MAX = 20

#: Tentatives d'une même manche avant abandon du run. Une manche échoue quand
#: le harnais renonce après ses propres relances (réseau, timeout) : on la
#: rejoue à donne identique. Au-delà, ce n'est plus un incident, c'est une
#: panne — et continuer produirait un run dont personne ne saurait quoi faire.
TENTATIVES_MANCHE = 3


class ErreurArbitre(RuntimeError):
    """Le run ne peut pas continuer sans produire des données douteuses."""


def racine_defaut() -> Path:
    """Racine des données de runs, **hors OneDrive** (décision D7).

    Des centaines d'écritures fichiers par série et un clone de `HERMES_HOME`
    par run sous synchronisation cloud, c'est des verrous et des conflits
    garantis.
    """
    return Path("C:/arene-runs") if os.name == "nt" else Path.home() / "arene-runs"


def identifiant(condition: Condition, bot: str, replication: int) -> str:
    """`run_id` normalisé du PRD 3 §1 : `{condition}-{bot}-r{réplication}`."""
    return f"{condition.value}-{bot.lower()}-r{replication}"


@dataclass(frozen=True)
class ConfigRun:
    """Tout ce qui définit un run, et rien de ce qui en dépend."""

    condition: Condition
    bot: str  # clé de `moteur.BOTS`
    replication: int
    machine: str = "inconnue"
    K: int = K_DEFAUT
    graine: str = alea.GRAINE_CAMPAGNE
    series_max: int | None = None  # None → règle du PRD 3 §3
    racine: Path = field(default_factory=racine_defaut)
    parametres: ParametresModele = field(default_factory=ParametresModele)

    def __post_init__(self) -> None:
        if self.bot not in BOTS:
            raise ValueError(f"bot inconnu : {self.bot!r} (attendu {sorted(BOTS)})")
        if self.K < 2 or self.K % 2:
            raise ValueError(f"K doit être pair et ≥ 2 (alternance des positions), reçu {self.K}")

    @property
    def run_id(self) -> str:
        return identifiant(self.condition, self.bot, self.replication)

    @property
    def dossier(self) -> Path:
        return Path(self.racine) / self.run_id

    @property
    def dossier_logs(self) -> Path:
        return self.dossier / "logs"

    @property
    def dossier_store(self) -> Path:
        return self.dossier / "hermes-home"

    @property
    def series_prevues(self) -> int:
        if self.series_max is not None:
            return self.series_max
        return SERIES_SM if self.condition is Condition.SM else SERIES_MAX

    def contexte(self) -> ContexteRun:
        return ContexteRun(
            run_id=self.run_id,
            condition=self.condition.value,
            bot=self.bot,
            replication=self.replication,
            machine=self.machine,
            modele=self.parametres.modele,
        )


# --------------------------------------------------------------------------
# Une manche jouée
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PriseDeDecision:
    """Une décision de l'agent, avec son rang dans le déroulé de la manche."""

    rang: int  # index dans `resultat.historique`
    infoset: InfoSet
    decision: Decision


@dataclass(frozen=True)
class MancheJouee:
    numero: int
    position: Position
    donne: alea.Donne
    resultat: ResultatManche
    decisions: Sequence[PriseDeDecision]
    tentatives: int

    @property
    def gain_agent(self) -> int:
        return recap.gain_agent(self.resultat, self.position)


# --------------------------------------------------------------------------
# L'arbitre
# --------------------------------------------------------------------------


@dataclass
class Arbitre:
    """Joue un run complet. Construit par `preparer_run`, jamais à la main."""

    config: ConfigRun
    agent: Harnais
    journal: JournalRun
    etat: etat_module.EtatRun
    store: Store | None = None
    marqueur_temoin: str | None = None
    autres_stores: Sequence[Path] = ()
    home_global: Path | None = None
    #: Rappel appelé après chaque série close — le point d'accroche du commit
    #: Git aux frontières de série (PRD 4 §1) et de l'affichage de progression.
    apres_serie: Callable[[Mapping[str, Any]], None] | None = None

    # -- boucle de run -----------------------------------------------------

    def jouer(self) -> etat_module.EtatRun:
        """Joue les séries restantes et rend l'état final du run."""
        for serie in range(self.etat.prochaine_session, self.config.series_prevues):
            ligne = self.jouer_serie(serie)
            if self.apres_serie is not None:
                self.apres_serie(ligne)
            if self._arret_au_plateau(serie):
                break
        return self.etat

    def _arret_au_plateau(self, serie: int) -> bool:
        """SM va jusqu'au bout de ses 3 séries : il n'y a pas de plateau à
        attendre d'une condition qui n'accumule rien."""
        if self.config.condition is Condition.SM:
            return False
        declare = self.etat.plateau_declare_a
        return declare is not None and serie >= declare + mesure.MARGE_PLATEAU

    # -- une série ---------------------------------------------------------

    def jouer_serie(self, serie: int) -> Mapping[str, Any]:
        """Ouvre, joue K manches, ferme, mesure, logue. Rend la ligne écrite."""
        m_s = self.agent.ouvrir_session(serie)
        recapitulateur = recap.Recapitulateur()
        tours: list[Mapping[str, Any]] = []
        positions = {"J1": 0, "J2": 0}
        defauts = {"actions_par_defaut": 0, "relances": 0, "erreurs_harnais": 0}
        tokens = {"in": 0, "out": 0}
        drapeaux: list[Drapeau] = []

        for k in range(1, self.config.K + 1):
            manche = self.jouer_manche(serie, k)
            positions[manche.position.value] += 1
            recapitulateur.ajouter(k, manche.position, manche.resultat)
            defauts["erreurs_harnais"] += manche.tentatives - 1
            for prise in manche.decisions:
                _cumuler(defauts, tokens, prise.decision)
                drapeaux.extend(analyser(prise.decision.sortie_brute, "sortie", k))
            for evenement in self._evenements_manche(serie, manche):
                tours.append(self.journal.ecrire_tour(evenement))

        texte_recap = recapitulateur.texte()
        frontiere = self.agent.fermer_session(serie, texte_recap)
        tokens["in"] += frontiere.tokens_entree or 0
        tokens["out"] += frontiere.tokens_sortie or 0
        drapeaux.extend(analyser(m_s, "slot"))
        drapeaux.extend(analyser(frontiere.m_s1, "memoire"))
        drapeaux.extend(analyser(frontiere.sortie_reflexion, "sortie"))

        resultat = mesure.mesurer_serie(tours, recapitulateur.gains, BOTS[self.config.bot])
        self.etat.ecarts.append(float(resultat.mesures.ecart_exploitation))
        plateau = mesure.evaluer_plateau(self.etat.ecarts)
        if plateau.declare and self.etat.plateau_declare_a is None:
            self.etat.plateau_declare_a = serie

        ligne = self.journal.ecrire_session(
            EvenementSession(
                session=serie,
                K=self.config.K,
                positions=positions,
                memoire=self._bloc_memoire(m_s, frontiere, texte_recap),
                pi_hat=resultat.pi_hat_json(),
                mesures=resultat.mesures,
                defauts=defauts,
                drapeaux_deobfuscation=[d.en_json() for d in drapeaux],
                plateau=plateau.en_json(),
                hash_donnes=alea.hash_donnes(
                    self.config.graine, self.config.replication, serie, self.config.K
                ),
                cout_session_tokens=tokens,
            )
        )
        self.etat.derniere_session_close = serie
        self.etat.enregistrer(self.config.dossier)
        return ligne

    def _bloc_memoire(self, m_s: str, frontiere, texte_recap: str) -> dict[str, Any]:
        """Bloc `memoire` du log de série (PRD 4 §3).

        Le récap y figure en entier : c'est le contenu même de la mémoire en
        condition ICL, la matière exacte de la réflexion en AE, et ce qui
        permet de reconstruire la fenêtre ICL après un plantage (`etat`).

        `gel_rompu` compare le snapshot pris à l'ouverture à ce que le harnais
        relit à la fermeture. Les deux doivent coïncider : s'ils divergent,
        c'est que le verrou du gel intra-série a lâché, et la série ne mesure
        plus ce qu'elle prétend mesurer.
        """
        return {
            "M_s": frontiere.m_s,
            "M_s1": frontiere.m_s1,
            "evenements": [{"type": e.type, "detail": e.detail} for e in frontiere.evenements],
            "ecritures_intra_serie": frontiere.ecritures_intra_serie,
            "entrees_m_s": len(decouper_entrees(frontiere.m_s)),
            "entrees_m_s1": len(decouper_entrees(frontiere.m_s1)),
            "recap": texte_recap,
            "sortie_reflexion": frontiere.sortie_reflexion,
            "gel_rompu": frontiere.m_s != m_s,
        }

    # -- une manche --------------------------------------------------------

    def jouer_manche(self, serie: int, numero_manche: int) -> MancheJouee:
        """Joue une manche, en la rejouant à l'identique si le harnais lâche.

        La donne et le flux du bot sont dérivés des mêmes coordonnées à chaque
        tentative : une manche rejouée est rigoureusement la même manche, pas
        une nouvelle (PRD 2 §3).
        """
        donne = alea.donne(
            self.config.graine, self.config.replication, serie, numero_manche
        )
        position = alea.position_agent(numero_manche)
        carte_j1, carte_j2 = (
            (donne.agent, donne.bot) if position is Position.J1 else (donne.bot, donne.agent)
        )

        derniere: ErreurHarnais | None = None
        for tentative in range(1, TENTATIVES_MANCHE + 1):
            self.agent.avant_manche()
            decisions: list[PriseDeDecision] = []
            deroule: list[tuple[Position, Action]] = []
            bot = decideur_depuis_politique(
                BOTS[self.config.bot],
                alea.flux_bot(
                    self.config.graine, self.config.replication, serie, numero_manche
                ),
            )
            agent_decideur, bot_decideur = self._decideurs(decisions, deroule, bot)
            try:
                resultat = jouer_manche(
                    agent_decideur if position is Position.J1 else bot_decideur,
                    agent_decideur if position is Position.J2 else bot_decideur,
                    carte_j1,
                    carte_j2,
                )
            except ErreurHarnais as echec:
                derniere = echec
                continue
            return MancheJouee(
                numero=numero_manche,
                position=position,
                donne=donne,
                resultat=resultat,
                decisions=decisions,
                tentatives=tentative,
            )

        raise ErreurArbitre(
            f"série {serie}, manche {numero_manche} : {TENTATIVES_MANCHE} tentatives "
            f"en échec ({derniere}) — le run s'arrête plutôt que de trouer les données"
        ) from derniere

    def _decideurs(
        self,
        decisions: list[PriseDeDecision],
        deroule: list[tuple[Position, Action]],
        bot: Decideur,
    ) -> tuple[Decideur, Decideur]:
        """Les deux décideurs servis au moteur, qui tiennent le déroulé à jour.

        Le moteur ne transmet pas l'historique aux décideurs (il n'en a pas
        besoin pour régler la manche) ; le harnais, lui, en a besoin pour
        rendre la vue servie à l'agent. On le reconstitue donc ici, dans
        l'ordre d'appel — qui est celui de l'arbre.
        """

        def decideur_agent(infoset: InfoSet) -> Action:
            decision = self.agent.decider(infoset, tuple(deroule))
            decisions.append(PriseDeDecision(len(deroule), infoset, decision))
            deroule.append((infoset.position, decision.action))
            return decision.action

        def decideur_bot(infoset: InfoSet) -> Action:
            action = bot(infoset)
            deroule.append((infoset.position, action))
            return action

        return decideur_agent, decideur_bot

    def _evenements_manche(self, serie: int, manche: MancheJouee) -> list[EvenementTour]:
        """Un événement par décision de l'agent (PRD 4 §2).

        `historique_final` et `resultat_manche` ne sont posés que sur la
        dernière décision : quand le bot répond *après* elle, sa réponse ne
        figure nulle part ailleurs et la manche ne serait pas re-règlable
        depuis les seuls logs (PRD 4 §7.1).
        """
        sequence = [action.value for _, action in manche.resultat.historique]
        evenements: list[EvenementTour] = []
        for rang_decision, prise in enumerate(manche.decisions, start=1):
            dernier = rang_decision == len(manche.decisions)
            flags = list(prise.decision.flags)
            if manche.tentatives > 1:
                flags.append("erreur_harnais")
            evenements.append(
                EvenementTour(
                    session=serie,
                    manche=manche.numero,
                    decision=rang_decision,
                    etat_reel=EtatReel(
                        carte_agent=int(manche.donne.agent),
                        carte_bot=int(manche.donne.bot),
                        carte_ecartee=int(manche.donne.ecartee),
                        position_agent=manche.position.value,
                        historique=sequence[: prise.rang],
                    ),
                    infoset=str(prise.infoset),
                    infoset_numero=numero(prise.infoset),
                    vue_servie=prise.decision.prompt,
                    sortie_brute=prise.decision.sortie_brute,
                    action_parsee=prise.decision.action.value,
                    parsing=prise.decision.parsing.value,
                    resultat_manche=manche.gain_agent if dernier else None,
                    historique_final=sequence if dernier else None,
                    flags=flags,
                    tokens={
                        "in": prise.decision.tokens_entree,
                        "out": prise.decision.tokens_sortie,
                    },
                    latence_ms=prise.decision.latence_ms,
                )
            )
        return evenements

    # -- clôture -----------------------------------------------------------

    def clore(self) -> integrite.RapportIntegrite:
        """Vérifications d'intégrité de fin de run (PRD 3 §8), écrites au log."""
        rapport = integrite.verifier_run(
            dossier_logs=self.config.dossier_logs,
            graine=self.config.graine,
            K=self.config.K,
            replication=self.config.replication,
            run_id=self.config.run_id,
            racine=self.config.racine,
            store=self.store,
            marqueur_temoin=self.marqueur_temoin,
            autres_stores=self.autres_stores,
            home_global=self.home_global,
        )
        rapport.ecrire(self.config.dossier_logs)
        return rapport


def _cumuler(
    defauts: dict[str, int], tokens: dict[str, int], decision: Decision
) -> None:
    """Compteurs de qualité d'une série (PRD 4 §3).

    Une relance se compte sur le nombre d'invocations, pas sur le statut de
    parsing : une décision aboutie après relance et une décision tombée au
    défaut ont toutes deux coûté deux appels, et c'est ce coût-là que le
    pilote de calibrage regarde.
    """
    if "action_par_defaut" in decision.flags:
        defauts["actions_par_defaut"] += 1
    if decision.invocations > 1:
        defauts["relances"] += decision.invocations - 1
    tokens["in"] += decision.tokens_entree or 0
    tokens["out"] += decision.tokens_sortie or 0


# --------------------------------------------------------------------------
# Préparation d'un run (§2 « préparer_run »)
# --------------------------------------------------------------------------


def preparer_run(
    config: ConfigRun,
    invocateur=None,
    home_source: Path | str | None = None,
    canari_reel: bool = True,
    home_global: Path | str | None = None,
) -> Arbitre:
    """Crée (ou reprend) l'arborescence d'un run et rend l'arbitre prêt à jouer.

    Run neuf : store isolé cloné du home de la machine, canari d'isolation
    (PRD 2 §6) — deux appels API, et le run est refusé s'il échoue —, témoin
    posé pour la clôture, `M_0` vide.

    Reprise : le store et les logs sont retrouvés tels quels, l'état est
    recalé sur `sessions.jsonl`, les tours d'une série entamée puis
    interrompue sont écartés, et la fenêtre ICL est reconstruite depuis les
    récaps logués. On ne reprend jamais en milieu de série (PRD 3 §8).
    """
    config.dossier.mkdir(parents=True, exist_ok=True)
    neuf = not config.dossier_store.exists() or not any(config.dossier_store.iterdir())

    if neuf:
        store = creer_store(config.dossier_store, config.parametres, home_source)
    else:
        store = Store(chemin=config.dossier_store, parametres=config.parametres)
        store.ecrire_config()  # configuration de manche : mémoire native éteinte

    if invocateur is None:
        invocateur = InvocateurHermes(store, config.parametres)

    voisins = [chemin for chemin in stores_actifs(config.racine) if chemin != store.chemin]

    etat = etat_module.EtatRun.charger(config.dossier) or etat_module.EtatRun(
        run_id=config.run_id,
        condition=config.condition.value,
        bot=config.bot,
        replication=config.replication,
        machine=config.machine,
        graine=config.graine,
        K=config.K,
        sessions_max=config.series_prevues,
    )
    etat.sessions_max = config.series_prevues  # une reprise peut rehausser le plafond

    if neuf:
        rapport_canari = (
            canari(store, config.run_id, invocateur, voisins, home_global)
            if canari_reel
            else canari_fichier(store, config.run_id, voisins, home_global)
        )
        etat.canari = {
            "marqueur": rapport_canari.marqueur,
            "ecriture_confirmee": rapport_canari.ecriture_confirmee,
            "ecriture_bloquee_en_manche": rapport_canari.ecriture_bloquee_en_manche,
            "reel": canari_reel,
        }
        etat.canari["temoin"] = integrite.poser_temoin(store, config.run_id)

    etat_module.synchroniser(etat, config.dossier_logs)
    agent = construire_harnais(config.condition, invocateur, store)

    ecartes = etat_module.ecarter_tours_abandonnes(
        config.dossier_logs,
        etat.prochaine_session,
        tentative=len(etat.abandons) + 1,
    )
    if ecartes:
        etat.abandons.append({"session": etat.prochaine_session, "tours_ecartes": ecartes})

    if config.condition is Condition.ICL:
        _reconstruire_fenetre_icl(agent, config.dossier_logs)

    etat.enregistrer(config.dossier)
    return Arbitre(
        config=config,
        agent=agent,
        journal=JournalRun(config.dossier_logs, config.contexte()),
        etat=etat,
        store=store,
        marqueur_temoin=etat.canari.get("temoin"),
        autres_stores=voisins,
        home_global=Path(home_global) if home_global is not None else None,
    )


def _reconstruire_fenetre_icl(agent: Harnais, dossier_logs: Path) -> None:
    """Rejoue les frontières ICL déjà passées, depuis les récaps logués.

    La fenêtre ICL vit en mémoire vive : après un plantage, il faut la
    reconstituer. On passe par l'interface publique du harnais plutôt que par
    ses attributs — `fermer_session` en condition ICL n'appelle aucun modèle,
    c'est un pur empilement de texte, donc rejouable à coût nul.
    """
    for serie, texte in etat_module.recaps_logues(dossier_logs):
        agent.fermer_session(serie, texte)


# --------------------------------------------------------------------------
# Matrice de campagne (PRD 3 §1 et §8)
# --------------------------------------------------------------------------


def matrice_campagne(
    replications: int = 3,
    conditions: Sequence[Condition] = tuple(Condition),
    bots: Sequence[str] = tuple(BOTS),
) -> list[str]:
    """Les identifiants des runs de la campagne : 3 conditions × 3 bots × N."""
    return [
        identifiant(condition, bot, replication)
        for condition in conditions
        for bot in bots
        for replication in range(1, replications + 1)
    ]


__all__ = [
    "K_DEFAUT",
    "SERIES_MAX",
    "SERIES_SM",
    "TENTATIVES_MANCHE",
    "Arbitre",
    "ConfigRun",
    "ErreurArbitre",
    "MancheJouee",
    "PriseDeDecision",
    "identifiant",
    "matrice_campagne",
    "preparer_run",
    "racine_defaut",
]
