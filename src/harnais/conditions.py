"""Les trois conditions mémoire : un seul harnais, trois contenus de slot.

C'est le cœur de l'ablation (PRD 2 §5). Les trois classes partagent
strictement le même chemin de code — même invocation `hermes -z`, même texte
de règles, même consigne de format, même parsing, même gel fichiers. Elles ne
diffèrent que par deux points :

- ce que `slot()` rend (rien / historique brut fenêtré / notes auto-écrites) ;
- ce que `fermer_session()` fait à la frontière (rien / accumuler le récap /
  faire réfléchir l'agent pour qu'il réécrive ses notes).

    | Condition | Slot                        | Frontière de série            |
    |-----------|-----------------------------|-------------------------------|
    | SM        | rubrique absente            | rien                          |
    | ICL       | `[HISTORIQUE …]`, fenêtré   | ajout du récap, sans LLM      |
    | AE        | `[VOS NOTES]`, snapshot gelé| réflexion → réécriture de M    |

Signature attendue (spec §5) : plate pour SM, dents de scie pour ICL,
escalier pour AE. Si le harnais introduisait la moindre asymétrie ailleurs
que dans le slot, ces signatures ne diraient plus rien.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Sequence

from moteur import Action, InfoSet, Position

from . import gabarits, gel
from .hermes import Invocateur, Reponse
from .parsing import RAPPEL_FORMAT, Parsing, extraire_action
from .stores import LIMITE_NOTES, TOOLSET_MEMOIRE, TOOLSET_SANS_OUTIL, Store

#: Fenêtre ICL (PRD 2 §5.1, paramètre figé du PRD 0 §3).
FENETRE_ICL_TOKENS = 6000

#: Conversion caractères → tokens. Hermes ne donne pas de tokeniseur au
#: harnais et le dépôt est sans dépendance : on borne la fenêtre sur une
#: estimation volontairement grossière mais **stable** (≈ 4 caractères par
#: token en français). Le pilote de calibrage confronte l'estimation aux
#: `input_tokens` réels du rapport d'usage et ajuste la constante si besoin.
CARACTERES_PAR_TOKEN = 4

#: Balisage d'appel d'outil émis **en clair** par certains modèles quand on ne
#: leur en donne aucun. Constaté sur `tencent/hy3:free` au canari du
#: 2026-08-21 : privé d'outils, il a écrit un `<tool_call:…>terminal…` au lieu
#: de répondre. L'appel est inerte — aucun outil n'existe — mais la sortie est
#: inexploitable et coûte une relance. Le drapeau alimente le taux de parsing,
#: critère de véto du pilote de calibrage (PRD 3 §7.1).
_MOTIF_PSEUDO_OUTIL = re.compile(r"<\s*tool_calls?\s*[:>]", re.IGNORECASE)


class Condition(Enum):
    SM = "SM"  # sans mémoire
    ICL = "ICL"  # historique brut réinjecté
    AE = "AE"  # auto-écrit (MEMORY.md natif d'Hermes)


class ErreurHarnais(RuntimeError):
    """Échec persistant d'invocation : la manche doit être rejouée à l'identique.

    Levée seulement après les relances de l'invocateur. L'arbitre l'attrape,
    logue la manche avec le drapeau `erreur_harnais` et la rejoue avec la
    même donne — jamais de manche silencieusement sautée (PRD 2 §3).
    """

    def __init__(self, reponse: Reponse):
        super().__init__(reponse.erreur or "échec d'invocation")
        self.reponse = reponse


@dataclass(frozen=True)
class Decision:
    """Une décision de jeu, avec tout ce que le tour doit loguer (PRD 4 §2)."""

    action: Action
    sortie_brute: str
    prompt: str
    parsing: Parsing
    flags: tuple[str, ...] = ()
    latence_ms: int = 0
    tokens_entree: int | None = None
    tokens_sortie: int | None = None
    modele: str | None = None
    invocations: int = 1


@dataclass(frozen=True)
class Frontiere:
    """Ce qui s'est passé à la fermeture d'une série (PRD 4 §3)."""

    m_s: str
    m_s1: str
    evenements: tuple[gel.EvenementMemoire, ...] = ()
    ecritures_intra_serie: int = 0
    sortie_reflexion: str = ""
    latence_ms: int = 0
    tokens_entree: int | None = None
    tokens_sortie: int | None = None


# --------------------------------------------------------------------------
# Harnais commun
# --------------------------------------------------------------------------


@dataclass
class Harnais:
    """Base commune aux trois conditions — ne s'instancie pas seule."""

    invocateur: Invocateur
    store: Store | None = None
    condition: Condition = field(init=False)

    _snapshot: gel.Snapshot = field(default_factory=lambda: gel.Snapshot({}), init=False)
    _ecritures: int = field(default=0, init=False)
    _serie: int = field(default=-1, init=False)

    # -- slot mémoire ------------------------------------------------------

    def slot(self) -> str | None:
        """Contenu de la rubrique mémoire, ou `None` si la rubrique est absente."""
        raise NotImplementedError

    def memoire_courante(self) -> str:
        """`M_s` sous forme de texte, tel qu'il part dans les logs de série."""
        return ""

    # -- cycle de vie d'une série -----------------------------------------

    def ouvrir_session(self, serie: int) -> str:
        """Charge `M_s` et le gèle. Rend `M_s` pour le log de série."""
        self._serie = serie
        self._ecritures = 0
        if self.store is not None:
            self._snapshot = gel.capturer(self.store.chemin)
        return self.memoire_courante()

    def avant_manche(self) -> tuple[str, ...]:
        """Restaure le snapshot gelé. Rend les fichiers qui avaient bougé.

        Appelée par l'arbitre **avant chaque manche** (PRD 3 §2) : c'est le
        verrou du gel intra-série (décision D2). Ce qu'elle rend est un
        observable, pas une erreur — l'agent a-t-il essayé d'écrire pendant
        qu'il jouait ?
        """
        if self.store is None:
            return ()
        modifies = gel.restaurer(self.store.chemin, self._snapshot)
        if modifies:
            self._ecritures += 1
        return modifies

    def fermer_session(self, serie: int, recap: str) -> Frontiere:
        """Frontière de série : met à jour le slot pour `M_{s+1}`."""
        raise NotImplementedError

    # -- décision de jeu ---------------------------------------------------

    def decider(
        self,
        infoset: InfoSet,
        historique: Sequence[tuple[Position, Action]] = (),
    ) -> Decision:
        """Fait jouer une décision à l'agent (PRD 2 §4).

        Une invocation ; sortie inexploitable → une relance avec rappel de
        format ; nouvel échec → action passive imposée, drapeau
        `action_par_defaut`. Le texte libre est conservé intégralement : c'est
        la matière du détecteur de dé-obfuscation (PRD 4 §4).
        """
        prompt = gabarits.construire_prompt(infoset, historique, self.slot())
        reponse = self._invoquer(prompt)
        action, parsing = extraire_action(reponse.texte, infoset.actions_legales)

        sorties = [reponse.texte]
        invocations = 1
        latence = reponse.latence_ms
        tokens_in, tokens_out = reponse.tokens_entree, reponse.tokens_sortie
        flags: list[str] = list(self._detecter_ecriture())
        flags.extend(_pseudo_outil(reponse.texte))

        if action is None:
            relance = self._invoquer(f"{prompt}\n\n{RAPPEL_FORMAT}")
            sorties.append(relance.texte)
            invocations += 1
            latence += relance.latence_ms
            tokens_in = _additionner(tokens_in, relance.tokens_entree)
            tokens_out = _additionner(tokens_out, relance.tokens_sortie)
            flags.extend(self._detecter_ecriture())
            flags.extend(_pseudo_outil(relance.texte))
            action, parsing = extraire_action(relance.texte, infoset.actions_legales)
            if action is None:
                action = infoset.action_passive
                parsing = Parsing.DEFAUT
                flags.append("action_par_defaut")
            else:
                parsing = Parsing.RELANCE

        return Decision(
            action=action,
            sortie_brute="\n\n--- relance ---\n\n".join(sorties),
            prompt=prompt,
            parsing=parsing,
            flags=tuple(flags),
            latence_ms=latence,
            tokens_entree=tokens_in,
            tokens_sortie=tokens_out,
            modele=reponse.modele,
            invocations=invocations,
        )

    # -- interne -----------------------------------------------------------

    def _invoquer(self, prompt: str, toolset: str = TOOLSET_SANS_OUTIL) -> Reponse:
        reponse = self.invocateur(prompt, toolset)
        if not reponse.ok:
            raise ErreurHarnais(reponse)
        return reponse

    def _detecter_ecriture(self) -> tuple[str, ...]:
        """Écriture mémoire pendant une manche : détectée, loguée, puis jetée.

        La restauration est faite ici, dans la foulée de la détection, et non
        laissée à `avant_manche` : les deux comptages se marcheraient sur les
        pieds, et une écriture doit disparaître au plus tôt — la décision
        suivante de la **même** manche doit lire `M_s`, pas ce que l'agent
        vient d'écrire.
        """
        if self.store is None:
            return ()
        if gel.restaurer(self.store.chemin, self._snapshot):
            self._ecritures += 1
            return ("ecriture_intra_serie",)
        return ()


def _pseudo_outil(texte: str) -> tuple[str, ...]:
    return ("sortie_pseudo_outil",) if _MOTIF_PSEUDO_OUTIL.search(texte or "") else ()


def _additionner(a: int | None, b: int | None) -> int | None:
    if a is None and b is None:
        return None
    return (a or 0) + (b or 0)


# --------------------------------------------------------------------------
# SM — sans mémoire
# --------------------------------------------------------------------------


@dataclass
class HarnaisSansMemoire(Harnais):
    """Plancher expérimental : contexte neuf à chaque manche, rien d'autre.

    Aucune rubrique mémoire dans le prompt — pas même une rubrique vide : une
    section « vos notes : (rien) » serait déjà une information sur l'existence
    d'une mémoire. Courbe attendue : plate.
    """

    def __post_init__(self) -> None:
        self.condition = Condition.SM

    def slot(self) -> str | None:
        return None

    def fermer_session(self, serie: int, recap: str) -> Frontiere:
        return Frontiere(m_s="", m_s1="", ecritures_intra_serie=self._ecritures)


# --------------------------------------------------------------------------
# ICL — historique brut réinjecté
# --------------------------------------------------------------------------


@dataclass
class HarnaisHistorique(Harnais):
    """Récaps bruts des séries passées, fenêtrés, figés pendant la série.

    Pas d'étape LLM à la frontière : l'arbitre empile le récap, la fenêtre
    évince les séries anciennes en bloc. C'est cette éviction qui produit le
    « dents de scie » attendu — jamais de série tronquée en son milieu, sinon
    on mesurerait un artefact de découpe et non un oubli.
    """

    fenetre_tokens: int = FENETRE_ICL_TOKENS

    def __post_init__(self) -> None:
        self.condition = Condition.ICL
        self._recaps: list[tuple[int, str]] = []
        self._gele: str = ""

    def ouvrir_session(self, serie: int) -> str:
        self._gele = self._fenetrer()
        return super().ouvrir_session(serie)

    def memoire_courante(self) -> str:
        return self._gele

    def slot(self) -> str | None:
        return gabarits.rubrique_slot(gabarits.ENTETE_SLOT_ICL, self._gele)

    def fermer_session(self, serie: int, recap: str) -> Frontiere:
        avant = self._gele
        self._recaps.append((serie, recap))
        return Frontiere(
            m_s=avant,
            m_s1=self._fenetrer(),
            ecritures_intra_serie=self._ecritures,
        )

    def _fenetrer(self) -> str:
        """Séries entières les plus récentes, dans la limite de la fenêtre."""
        budget = self.fenetre_tokens * CARACTERES_PAR_TOKEN
        retenus: list[str] = []
        for serie, recap in reversed(self._recaps):
            bloc = f"— série {serie} —\n{recap}"
            cout = len(bloc) + 2
            if retenus and cout > budget:
                break
            budget -= cout
            retenus.append(bloc)
        return "\n\n".join(reversed(retenus))


# --------------------------------------------------------------------------
# AE — notes auto-écrites (mémoire native d'Hermes)
# --------------------------------------------------------------------------


@dataclass
class HarnaisAutoEcrit(Harnais):
    """`MEMORY.md` d'Hermes, gelé pendant la série, réécrit à la frontière.

    Pendant les manches, la mémoire **native** est désactivée et le snapshot
    `M_s` est servi comme n'importe quel autre slot, en clair dans le prompt
    (PRD 2 §5.3) : les trois conditions traversent ainsi le même prompt
    système Hermes, et les prompts restent comparables octet à octet. La
    mémoire native n'est rallumée que le temps de l'unique invocation de
    réflexion, seul moment où l'agent tient la plume.
    """

    max_turns_reflexion: int = 8
    limite_notes: int = LIMITE_NOTES

    def __post_init__(self) -> None:
        self.condition = Condition.AE
        if self.store is None:
            raise ValueError("la condition AE exige un store Hermes isolé")
        self._notes_gelees: str = ""

    def ouvrir_session(self, serie: int) -> str:
        assert self.store is not None
        self._notes_gelees = gel.lire_notes(self.store.chemin)
        return super().ouvrir_session(serie)

    def memoire_courante(self) -> str:
        return self._notes_gelees

    def slot(self) -> str | None:
        return gabarits.rubrique_slot(gabarits.ENTETE_SLOT_AE, self._notes_gelees)

    def fermer_session(self, serie: int, recap: str) -> Frontiere:
        """Réflexion façon Reflexion : bilan → réécriture des notes (PRD 2 §5.2).

        La bascule de config est le seul endroit du projet où la mémoire
        native d'Hermes est active : elle est rallumée juste avant l'appel et
        éteinte juste après, y compris si l'appel échoue.
        """
        assert self.store is not None
        avant = gel.lire_notes(self.store.chemin)

        self.store.ecrire_config(
            memoire_native=True,
            max_turns=self.max_turns_reflexion,
            reasoning=self.store.parametres.reasoning_reflexion,
        )
        try:
            reponse = self._invoquer(gabarits.prompt_reflexion(recap), TOOLSET_MEMOIRE)
        finally:
            self.store.ecrire_config(memoire_native=False)

        apres = gel.lire_notes(self.store.chemin)
        return Frontiere(
            m_s=avant,
            m_s1=apres,
            evenements=gel.evenements_memoire(avant, apres, self.limite_notes),
            ecritures_intra_serie=self._ecritures,
            sortie_reflexion=reponse.texte,
            latence_ms=reponse.latence_ms,
            tokens_entree=reponse.tokens_entree,
            tokens_sortie=reponse.tokens_sortie,
        )


#: Fabrique : condition → classe de harnais.
HARNAIS: Mapping[Condition, type[Harnais]] = {
    Condition.SM: HarnaisSansMemoire,
    Condition.ICL: HarnaisHistorique,
    Condition.AE: HarnaisAutoEcrit,
}


def construire_harnais(
    condition: Condition,
    invocateur: Invocateur,
    store: Store | None = None,
) -> Harnais:
    """Instancie le harnais d'une condition (point d'entrée de l'arbitre)."""
    return HARNAIS[condition](invocateur=invocateur, store=store)


__all__ = [
    "CARACTERES_PAR_TOKEN",
    "FENETRE_ICL_TOKENS",
    "HARNAIS",
    "Condition",
    "Decision",
    "ErreurHarnais",
    "Frontiere",
    "Harnais",
    "HarnaisAutoEcrit",
    "HarnaisHistorique",
    "HarnaisSansMemoire",
    "construire_harnais",
]
