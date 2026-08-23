"""Harnais mémoire — trois conditions, un seul canal variable (PRD 2).

Couche entre l'arbitre (PRD 3) et l'agent : elle transforme « une décision de
jeu à prendre » en « un appel LLM correctement conditionné par la mémoire de
la condition en cours », et garantit que la **seule** différence entre les
trois conditions est le contenu du slot mémoire (décision D1).

    from harnais import Condition, InvocateurHermes, construire_harnais, creer_store

    store = creer_store(r"C:\\arene-runs\\AE-station-r2\\hermes-home",
                        home_source=r"C:\\Users\\videt\\AppData\\Local\\hermes")
    agent = construire_harnais(Condition.AE, InvocateurHermes(store), store)

    agent.ouvrir_session(0)
    decision = agent.decider(infoset)          # → action, sortie brute, méta
    frontiere = agent.fermer_session(0, recap) # → M_0, M_1, événements mémoire

Aucun module d'ici ne connaît les règles du jeu (PRD 1) ni les schémas de logs
(PRD 4) : il rend des objets, l'arbitre les assemble.
"""

from .canari import RapportCanari, canari, canari_fichier, stores_actifs
from .conditions import (
    CARACTERES_PAR_TOKEN,
    FENETRE_ICL_TOKENS,
    Condition,
    Decision,
    ErreurHarnais,
    Frontiere,
    Harnais,
    HarnaisAutoEcrit,
    HarnaisHistorique,
    HarnaisSansMemoire,
    construire_harnais,
)
from .gabarits import (
    HASH_REGLES,
    REGLES,
    VERSION_GABARITS,
    construire_prompt,
    ligne_recap,
    prompt_reflexion,
    recap_serie,
)
from .gel import EvenementMemoire, Snapshot, capturer, evenements_memoire, restaurer
from .hermes import Invocateur, InvocateurHermes, Reponse
from .parsing import RAPPEL_FORMAT, Parsing, extraire_action
from .stores import (
    LIMITE_NOTES,
    TOOLSET_MEMOIRE,
    TOOLSET_SANS_OUTIL,
    EchecCanari,
    ParametresModele,
    Store,
    auth_partagee_defaut,
    creer_store,
    marqueur_canari,
    verifier_isolation,
)

__all__ = [
    "CARACTERES_PAR_TOKEN",
    "FENETRE_ICL_TOKENS",
    "HASH_REGLES",
    "LIMITE_NOTES",
    "RAPPEL_FORMAT",
    "REGLES",
    "TOOLSET_MEMOIRE",
    "TOOLSET_SANS_OUTIL",
    "VERSION_GABARITS",
    "Condition",
    "Decision",
    "EchecCanari",
    "ErreurHarnais",
    "EvenementMemoire",
    "Frontiere",
    "Harnais",
    "HarnaisAutoEcrit",
    "HarnaisHistorique",
    "HarnaisSansMemoire",
    "Invocateur",
    "InvocateurHermes",
    "ParametresModele",
    "Parsing",
    "RapportCanari",
    "Reponse",
    "Snapshot",
    "Store",
    "canari",
    "canari_fichier",
    "capturer",
    "construire_harnais",
    "construire_prompt",
    "auth_partagee_defaut",
    "creer_store",
    "evenements_memoire",
    "extraire_action",
    "ligne_recap",
    "marqueur_canari",
    "prompt_reflexion",
    "recap_serie",
    "restaurer",
    "stores_actifs",
    "verifier_isolation",
]
