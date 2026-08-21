"""Gabarits de prompt servis à l'agent (PRD 2 §4).

**Tout** ce que l'agent lit — règles, vue d'une épreuve, consigne de format,
récap de série, consigne de réflexion — est produit ici, et nulle part
ailleurs. Le module est purement textuel : aucun appel réseau, aucun état.

Deux invariants que les tests vérifient :

1. **Obfuscation** (PRD 1 §2, D5) : aucun gabarit ne contient un motif de
   `moteur.lexique.MOTIFS_INTERDITS`. Les textes sont déclarés à
   `lexique.enregistrer_textes` pour entrer dans le balayage T8.
2. **Équité inter-conditions** (PRD 2 §8.1) : `construire_prompt` assemble les
   mêmes rubriques dans le même ordre pour les trois conditions ; seule la
   rubrique « slot mémoire » varie, et elle est absente en condition SM.

Le texte des règles est versionné et haché (`HASH_REGLES`) : le hash part dans
chaque ligne de log (PRD 4 §1) et prouve après coup que les 27 runs ont vu le
même énoncé.
"""

from __future__ import annotations

import hashlib
from typing import Mapping, Sequence

from moteur import Action, Carte, InfoSet, Position
from moteur.lexique import DOMINANCE, NOM_DU_JEU, enregistrer_textes, rendre_carte

VERSION_GABARITS = "1.0"

#: Rôles à la table, en vocabulaire obfusqué. « Ouvrant » = J1 (il parle
#: avant l'autre), « Répondant » = J2. Les labels ordinaux (premier,
#: deuxième…) sont proscrits par le filet d'obfuscation.
ROLES: Mapping[Position, str] = {
    Position.J1: "l'Ouvrant",
    Position.J2: "le Répondant",
}

#: Verbes d'action conjugués, au présent, selon l'acteur — le même temps que
#: les lignes de récap (PRD 2 §5.1), pour que l'agent lise partout la même
#: langue.
_VERBES_AGENT: Mapping[Action, str] = {
    Action.CHECK: "vous retenez",
    Action.BET: "vous engagez",
    Action.CALL: "vous couvrez",
    Action.FOLD: "vous vous retirez",
}

_VERBES_ADVERSAIRE: Mapping[Action, str] = {
    Action.CHECK: "l'autre retient",
    Action.BET: "l'autre engage",
    Action.CALL: "l'autre couvre",
    Action.FOLD: "l'autre se retire",
}


# --------------------------------------------------------------------------
# Règles — texte canonique, unique, haché
# --------------------------------------------------------------------------

REGLES = f"""[RÈGLES DU JEU]
{NOM_DU_JEU}

Deux personnes s'affrontent, épreuve après épreuve, toujours les mêmes.
Le coffre contient trois sceaux : Tor, Vael, Rhun.
{DOMINANCE}

Déroulement d'une épreuve :
- Chacun verse 1 jeton dans la réserve commune, sans exception.
- On attribue au hasard un sceau à chacun ; le sceau restant est mis de côté
  et n'est montré à personne.
- Chacun voit son propre sceau, jamais celui de l'autre.
- L'un des deux ouvre l'échange : on l'appelle l'Ouvrant. L'autre, le
  Répondant, parle ensuite. Les rôles alternent d'une épreuve à la suivante.

Les quatre actions :
- « retenir » : ne rien ajouter à la réserve et passer la parole.
- « engager » : ajouter 1 jeton à la réserve, ce qui oblige l'autre à répondre.
- « couvrir » : après un engagement de l'autre, ajouter 1 jeton à son tour ;
  les deux sceaux sont alors dévoilés et comparés.
- « se retirer » : après un engagement de l'autre, renoncer ; l'autre emporte
  la réserve et les sceaux ne sont pas dévoilés.

Les trois enchaînements possibles :
- L'Ouvrant retient, le Répondant retient : les sceaux sont dévoilés, celui
  qui détient le sceau supérieur emporte la réserve — solde +1 pour lui,
  -1 pour l'autre.
- L'Ouvrant retient, le Répondant engage : l'Ouvrant se retire — solde -1
  pour lui, +1 pour l'autre — ou couvre, et les sceaux sont dévoilés — solde
  +2 pour celui qui détient le sceau supérieur, -2 pour l'autre.
- L'Ouvrant engage : le Répondant se retire — solde +1 pour l'Ouvrant, -1
  pour l'autre — ou couvre, et les sceaux sont dévoilés — solde +2 pour celui
  qui détient le sceau supérieur, -2 pour l'autre.

Les soldes se comptent en jetons. Votre but est d'en accumuler le plus
possible sur l'ensemble des épreuves."""


def _hacher(texte: str) -> str:
    return "sha256:" + hashlib.sha256(texte.encode("utf-8")).hexdigest()[:16]


#: Empreinte du texte de règles, loguée à chaque tour et à chaque session
#: (PRD 4 §1). Toute divergence entre deux runs est visible dans les logs.
HASH_REGLES = _hacher(REGLES)


# --------------------------------------------------------------------------
# Rubriques du prompt de manche
# --------------------------------------------------------------------------

#: En-têtes des slots mémoire. La condition SM n'en pose aucun (PRD 2 §5).
ENTETE_SLOT_ICL = "[HISTORIQUE DES SÉRIES PRÉCÉDENTES]"
ENTETE_SLOT_AE = "[VOS NOTES]"


def rubrique_slot(entete: str, contenu: str) -> str:
    """Assemble une rubrique de slot mémoire. Contenu vide → rubrique quand
    même posée, avec une mention explicite : une série sans notes doit rester
    distinguable, dans les logs, d'une condition sans slot du tout."""
    corps = contenu.strip() or "(rien pour l'instant)"
    return f"{entete}\n{corps}"


def rendre_historique(
    historique: Sequence[tuple[Position, Action]],
    position_agent: Position,
) -> str:
    """Déroulé de l'épreuve en cours, du point de vue de l'agent."""
    if not historique:
        return "Rien n'a encore été joué : c'est à vous d'ouvrir."
    fragments = [
        (_VERBES_AGENT if position is position_agent else _VERBES_ADVERSAIRE)[action]
        for position, action in historique
    ]
    return " ; ".join(fragments) + "."


def rubrique_epreuve(
    infoset: InfoSet,
    historique: Sequence[tuple[Position, Action]] = (),
) -> str:
    """Rubrique « épreuve en cours » : rôle, sceau détenu, déroulé.

    L'info-set porte déjà le rôle et le sceau ; l'historique n'ajoute que la
    formulation. Rien d'autre n'est servi : pas de numéro d'épreuve, pas de
    solde courant, pas de trace des épreuves passées — c'est ce qui rend la
    condition SM réellement sans mémoire (PRD 2 §8.5).
    """
    return (
        "[ÉPREUVE EN COURS]\n"
        f"Vous êtes {ROLES[infoset.position]}.\n"
        f"Votre sceau : {rendre_carte(infoset.carte)}.\n"
        f"Déroulé : {rendre_historique(historique, infoset.position)}"
    )


def rubrique_tache(actions_legales: Sequence[Action]) -> str:
    """Consigne de format (PRD 2 §4) : une action, sur la dernière ligne."""
    from moteur.lexique import rendre_action  # local : évite un cycle d'import

    choix = " ou ".join(f"« {rendre_action(a)} »" for a in actions_legales)
    return (
        "[TÂCHE]\n"
        f"Choisissez exactement une action : {choix}.\n"
        "Vous pouvez réfléchir librement avant de répondre, mais la DERNIÈRE "
        "ligne de votre réponse doit être exactement :\n"
        "ACTION: <l'action choisie>"
    )


def construire_prompt(
    infoset: InfoSet,
    historique: Sequence[tuple[Position, Action]] = (),
    slot: str | None = None,
) -> str:
    """Prompt complet d'une décision de jeu (PRD 2 §4).

    `slot` est la **seule** source de variation entre les trois conditions :
    `None` en SM (rubrique absente), historique fenêtré en ICL, snapshot des
    notes en AE. Le reste est octet-pour-octet identique — c'est le critère
    d'acceptation PRD 2 §8.1.
    """
    rubriques = [REGLES]
    if slot is not None:
        rubriques.append(slot)
    rubriques.append(rubrique_epreuve(infoset, historique))
    rubriques.append(rubrique_tache(infoset.actions_legales))
    return "\n\n".join(rubriques)


# --------------------------------------------------------------------------
# Récap de série et consigne de réflexion
# --------------------------------------------------------------------------


def ligne_recap(
    numero_epreuve: int,
    position_agent: Position,
    carte_agent: Carte,
    historique: Sequence[tuple[Position, Action]],
    carte_adverse: Carte | None,
    solde: int,
) -> str:
    """Une épreuve résumée en une ligne (PRD 2 §5.1, PRD 3 §5).

    `carte_adverse` vaut `None` quand les sceaux n'ont pas été dévoilés : la
    ligne dit alors « sceau adverse non dévoilé ». Ne jamais fuiter un sceau
    non montré est un critère d'acceptation (PRD 3 §10.5) — la fuite
    donnerait à l'agent une information que la table ne lui a pas donnée.
    """
    actions = ", ".join(
        (_VERBES_AGENT if position is position_agent else _VERBES_ADVERSAIRE)[action]
        for position, action in historique
    )
    adverse = (
        f"sceau adverse : {rendre_carte(carte_adverse)}"
        if carte_adverse is not None
        else "sceau adverse non dévoilé"
    )
    return (
        f"épreuve {numero_epreuve} : {ROLES[position_agent]}, "
        f"votre sceau {rendre_carte(carte_agent)}, {actions}, {adverse}, "
        f"solde {solde:+d}"
    )


def recap_serie(lignes: Sequence[str], solde_total: int) -> str:
    """Récap canonique d'une série close (PRD 3 §5, décision D8).

    Ce texte **unique** sert de matière à la réflexion AE et d'unité
    d'accumulation ICL. Il ne contient ni conseil, ni statistique agrégée par
    info-set, ni interprétation : distiller la fuite de l'adversaire est le
    travail de l'agent, pas celui de l'arbitre.
    """
    corps = "\n".join(lignes)
    return (
        f"{corps}\n"
        f"Bilan : {len(lignes)} épreuves, solde cumulé {solde_total:+d} jetons."
    )


#: Le récap seul suffirait à la réflexion (PRD 2 §5.2 : « prompt = récap +
#: consigne »), mais rappeler les règles à la frontière coûte ~300 tokens une
#: fois par série — négligeable devant K = 200 manches — et évite que l'agent
#: rédige ses notes sans le référentiel du jeu. Choix documenté, réversible
#: en basculant cette constante à False.
INCLURE_REGLES_DANS_REFLEXION = True

CONSIGNE_REFLEXION = """[TÂCHE]
Vous venez d'achever une série d'épreuves contre cet adversaire, et vous en
affronterez d'autres contre lui. Relisez le bilan ci-dessus : qu'est-ce qui
vous a rapporté des jetons, qu'est-ce qui vous en a coûté, et que pouvez-vous
dire de la façon de jouer de votre adversaire ?

Mettez vos notes persistantes à jour en conséquence, avec votre outil de
mémoire : ajoutez ce qui vous fera gagner davantage la prochaine fois,
retirez ce qui s'est révélé faux ou sans usage. Ces notes sont tout ce que
vous conserverez : vous ne reverrez pas ce bilan. Leur taille est limitée,
c'est donc à vous de choisir ce qui mérite d'y rester.

Terminez par une phrase disant ce que vous avez retenu."""


def prompt_reflexion(recap: str) -> str:
    """Prompt de la frontière de série en condition AE (PRD 2 §5.2)."""
    rubriques = [REGLES] if INCLURE_REGLES_DANS_REFLEXION else []
    rubriques.append(f"[BILAN DE LA SÉRIE ACHEVÉE]\n{recap}")
    rubriques.append(CONSIGNE_REFLEXION)
    return "\n\n".join(rubriques)


# --------------------------------------------------------------------------
# Déclaration au filet d'obfuscation (T8)
# --------------------------------------------------------------------------

enregistrer_textes(
    {
        "gabarit.regles": REGLES,
        "gabarit.consigne_reflexion": CONSIGNE_REFLEXION,
        "gabarit.entete_slot_icl": ENTETE_SLOT_ICL,
        "gabarit.entete_slot_ae": ENTETE_SLOT_AE,
        **{f"gabarit.role.{p.value}": nom for p, nom in ROLES.items()},
        **{f"gabarit.verbe_agent.{a.value}": v for a, v in _VERBES_AGENT.items()},
        **{f"gabarit.verbe_adverse.{a.value}": v for a, v in _VERBES_ADVERSAIRE.items()},
    }
)


__all__ = [
    "CONSIGNE_REFLEXION",
    "ENTETE_SLOT_AE",
    "ENTETE_SLOT_ICL",
    "HASH_REGLES",
    "INCLURE_REGLES_DANS_REFLEXION",
    "REGLES",
    "ROLES",
    "VERSION_GABARITS",
    "construire_prompt",
    "ligne_recap",
    "prompt_reflexion",
    "recap_serie",
    "rendre_historique",
    "rubrique_epreuve",
    "rubrique_slot",
    "rubrique_tache",
]
