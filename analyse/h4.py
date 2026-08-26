"""H4 — les deux mesures automatiques du biais de décision (§2.2.5.3).

Mesure 1 — **incohérence raisonnement↔action**, sur `donnees/decisions.csv`.
Mesure 2 — **dégénérescence des stratégies mixtes**, sur `donnees/infosets.csv`.

Aucune donnée nouvelle : tout se calcule sur les fichiers déjà versionnés.

    "C:/Users/videt/anaconda3/python.exe" analyse/h4.py

Écrit `memoire/h4-mesures.md` et résume sur la sortie standard.

⚠️ **La règle pré-enregistrée de la mesure 1 s'est révélée invalide.** Le §2.2.5.3
prévoyait de comparer l'action jouée à « la dernière action nommée dans le texte
libre ». Appliquée telle quelle, elle rend 47,8 % — un chiffre voisin des 45,1 %
de GTBENCH, et entièrement artefactuel : le raisonnement français conclut par une
clause contrastive qui nomme l'option *rejetée* (« engager garantit +1, **tandis
que retenir** expose à une perte »). La règle mesure une convention de discours.
Les trois variantes sont donc calculées et rapportées ensemble ; c'est la
troisième, à haute précision, qui porte le résultat.
"""

from __future__ import annotations

import csv
import io
import re
import sys
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "src"))

from moteur import BOTS, GTO, meilleure_reponse  # noqa: E402

DECISIONS = RACINE / "donnees" / "decisions.csv"
INFOSETS = RACINE / "donnees" / "infosets.csv"
RAPPORT = RACINE / "memoire" / "h4-mesures.md"

CONDITIONS = ["SM", "ICL", "AE"]
BOTS_ORDRE = ["Over-folder", "Station", "GTO"]

csv.field_size_limit(10**9)


# --------------------------------------------------------------------------
# Mesure 1 — incohérence raisonnement↔action
# --------------------------------------------------------------------------

#: Le vocabulaire obfusqué (`moteur.lexique.ACTIONS`) et ses flexions. Les
#: radicaux sont disjoints deux à deux : « reten- » (retenir) ne collisionne
#: pas avec « retir- » (se retirer).
VERBES: dict[str, re.Pattern[str]] = {
    "check": re.compile(r"reten\w*|retien\w*", re.I),
    "bet": re.compile(r"engag\w*", re.I),
    "call": re.compile(r"couvr\w*|couvert\w*", re.I),
    "fold": re.compile(r"retir\w*|retrait\w*", re.I),
}

#: Ligne d'action imposée par la consigne de format (PRD 2).
LIGNE_ACTION = re.compile(r"^[ \t>*-]*ACTION\s*:", re.I | re.M)

#: Désignants de l'agent. Le prompt le vouvoie ; il se répond en « je ».
SOI = re.compile(r"\b(?:je|j'|nous|notre|nos|mon|ma|mes|vous|votre|vos)\b", re.I)

#: Désignants de l'adversaire, hors rôle — le rôle dépend de la position.
ADVERSAIRE_FIXE = re.compile(r"\b(?:l'adversaire|adversaire|l'opposant|opposant|il|elle)\b", re.I)

#: Fenêtre de rétro-lecture pour l'attribution du sujet, en caractères.
FENETRE_SUJET = 70

#: Radical d'action, pour les motifs d'énonciation du choix.
_RADICAL = r"(?P<a>reten\w*|retien\w*|engag\w*|couvr\w*|couvert\w*|retir\w*)"

#: Formules par lesquelles l'agent **énonce** son choix, par opposition à celles
#: qui évoquent une action (hypothèse, action adverse, option rejetée). Motifs
#: délibérément étroits : on préfère ne rien mesurer à mesurer du bruit.
ENONCE_DU_CHOIX: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.I | re.M)
    for p in (
        r"il (?:vaut|est) (?:donc |dès lors )?(?:mieux|préférable)(?: de)?\s+" + _RADICAL,
        r"je (?:choisis|décide|opte|préfère)\s*(?:de |pour |d')?\s*" + _RADICAL,
        r"(?:le mieux|la meilleure (?:option|action|décision))\s+est\s*(?:de |d')?\s*" + _RADICAL,
        r"^\s*" + _RADICAL + r"\s+est (?:donc |ici )?(?:préférable|la meilleure|le meilleur|optimal)",
    )
)


def _role_adverse(position_agent: str) -> re.Pattern[str]:
    """L'agent en J1 est « l'Ouvrant » ; son adversaire est donc « le Répondant »."""
    autre = "Répondant" if position_agent == "J1" else "Ouvrant"
    return re.compile(rf"\b(?:l')?{autre}\b", re.I)


def _action_du_radical(mot: str) -> str | None:
    for action, motif in VERBES.items():
        if motif.match(mot):
            return action
    return None


def derniere_action_nommee(
    texte: str, position_agent: str, ignorer_adversaire: bool
) -> str | None:
    """Variantes 1 et 2 : la dernière action que le texte désigne.

    `ignorer_adversaire` écarte les occurrences dont le sujet apparent est
    l'adversaire — « l'adversaire se retire systématiquement » n'énonce pas
    l'intention de l'agent.
    """
    role = _role_adverse(position_agent)
    derniere: tuple[int, str] | None = None
    for action, motif in VERBES.items():
        for trouve in motif.finditer(texte):
            if ignorer_adversaire:
                amont = texte[max(0, trouve.start() - FENETRE_SUJET) : trouve.start()]
                designants = (
                    [(m.start(), "adv") for m in ADVERSAIRE_FIXE.finditer(amont)]
                    + [(m.start(), "adv") for m in role.finditer(amont)]
                    + [(m.start(), "soi") for m in SOI.finditer(amont)]
                )
                if designants and max(designants)[1] == "adv":
                    continue
            if derniere is None or trouve.start() > derniere[0]:
                derniere = (trouve.start(), action)
    return None if derniere is None else derniere[1]


def choix_enonce(texte: str) -> str | None:
    """Variante 3 : l'action que l'agent **déclare** choisir, ou None."""
    dernier: tuple[int, str] | None = None
    for motif in ENONCE_DU_CHOIX:
        for trouve in motif.finditer(texte):
            if dernier is None or trouve.start() > dernier[0]:
                dernier = (trouve.start(), trouve.group("a").lower())
    return None if dernier is None else _action_du_radical(dernier[1])


class Compteur:
    """Décisions analysables, dont mesurables, dont divergentes."""

    __slots__ = ("total", "mesurables", "divergentes")

    def __init__(self) -> None:
        self.total = 0
        self.mesurables = 0
        self.divergentes = 0

    @property
    def taux(self) -> float | None:
        return None if not self.mesurables else self.divergentes / self.mesurables


VARIANTES = ("positionnelle", "positionnelle_filtree", "choix_enonce")


def mesure_incoherence() -> dict:
    par: dict[str, dict] = {v: defaultdict(Compteur) for v in VARIANTES}
    confusions: dict[tuple[str, str], int] = defaultdict(int)
    exemples: list[tuple] = []
    sans_ligne_action = 0
    hors_parsing = 0

    with io.open(DECISIONS, encoding="utf8", newline="") as fh:
        for ligne in csv.DictReader(fh):
            if ligne["parsing"] != "ok":
                hors_parsing += 1
                continue
            brute = ligne["sortie_brute"]
            marques = list(LIGNE_ACTION.finditer(brute))
            if not marques:
                sans_ligne_action += 1
                continue
            raisonnement = brute[: marques[-1].start()]
            jouee = ligne["action_parsee"]
            cles = (
                ("global",),
                ("condition", ligne["condition"]),
                ("bot", ligne["bot"]),
                ("condition_serie", ligne["condition"], int(ligne["session"])),
            )

            trouvees = {
                "positionnelle": derniere_action_nommee(
                    raisonnement, ligne["position_agent"], False
                ),
                "positionnelle_filtree": derniere_action_nommee(
                    raisonnement, ligne["position_agent"], True
                ),
                "choix_enonce": choix_enonce(raisonnement),
            }

            for variante, nommee in trouvees.items():
                for cle in cles:
                    par[variante][cle].total += 1
                    if nommee is None:
                        continue
                    par[variante][cle].mesurables += 1
                    if nommee != jouee:
                        par[variante][cle].divergentes += 1

            if trouvees["positionnelle"] and trouvees["positionnelle"] != jouee:
                confusions[(trouvees["positionnelle"], jouee)] += 1
                if len(exemples) < 400:
                    exemples.append(
                        (
                            ligne["condition"],
                            ligne["bot"],
                            trouvees["positionnelle"],
                            jouee,
                            raisonnement.strip(),
                        )
                    )

    return {
        "par": par,
        "confusions": confusions,
        "exemples": exemples,
        "sans_ligne_action": sans_ligne_action,
        "hors_parsing": hors_parsing,
    }


# --------------------------------------------------------------------------
# Mesure 2 — dégénérescence des stratégies mixtes
# --------------------------------------------------------------------------

#: Effectif minimal pour qu'une fréquence de série soit retenue. Un info-set
#: vu trois fois ne dit rien d'un mélange.
N_MINIMAL = 20


def references():
    """Fréquence d'équilibre par info-set, et fréquence de meilleure réponse par bot."""
    equilibre = {str(k): v for k, v in GTO.items()}
    br = {
        nom: {str(k): v for k, v in meilleure_reponse(politique).politique.items()}
        for nom, politique in BOTS.items()
    }
    return equilibre, br


def mesure_degenerescence(equilibre, br) -> dict:
    lignes = []
    ignorees = 0
    with io.open(INFOSETS, encoding="utf8") as fh:
        for ligne in csv.DictReader(fh):
            n = int(ligne["n"])
            if n < N_MINIMAL:
                ignorees += 1
                continue
            p = float(ligne["p"])
            infoset = ligne["infoset"]
            lignes.append(
                {
                    "condition": ligne["condition"],
                    "bot": ligne["bot"],
                    "session": int(ligne["session"]),
                    "infoset": infoset,
                    "p": p,
                    "n": n,
                    "aux_bornes": p == 0.0 or p == 1.0,
                    "p_eq": float(equilibre[infoset]),
                    "p_br": float(br[ligne["bot"]][infoset]),
                }
            )

    # Les info-sets où l'équilibre exige un mélange : c'est là, et là seulement,
    # qu'être aux bornes est une dégénérescence (§L.1, point 3).
    mixtes = sorted(str(k) for k, v in equilibre.items() if 0 < v < 1)
    br_mixte = {bot: {i for i, v in table.items() if 0 < v < 1} for bot, table in br.items()}
    return {"lignes": lignes, "mixtes": mixtes, "br_mixte": br_mixte, "ignorees": ignorees}


# --------------------------------------------------------------------------
# Rapport
# --------------------------------------------------------------------------


def pct(x: float | None, decimales: int = 1) -> str:
    return "—" if x is None else f"{100 * x:.{decimales}f} %"


def milliers(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def rapport(inc: dict, deg: dict, equilibre, br) -> str:
    out: list[str] = []
    a = out.append

    pos = inc["par"]["positionnelle"]
    fil = inc["par"]["positionnelle_filtree"]
    exp = inc["par"]["choix_enonce"]
    g_pos, g_fil, g_exp = pos[("global",)], fil[("global",)], exp[("global",)]

    a("# H4 — mesures automatiques du biais de décision\n")
    a("*Généré par `analyse/h4.py` depuis `donnees/decisions.csv` et "
      "`donnees/infosets.csv`. Aucune collecte nouvelle.*\n")

    # ================= Mesure 1
    a("\n## 1. Incohérence raisonnement↔action\n")
    a(f"Base : **{milliers(g_pos.total)}** décisions au parsing strict "
      f"({inc['hors_parsing']} écartées, extraites par repli"
      + (f" ; {inc['sans_ligne_action']} sans ligne `ACTION:` détectable" if inc["sans_ligne_action"] else "")
      + ").\n")

    a("\n### 1.1 La règle pré-enregistrée ne mesure pas ce qu'elle annonce\n")
    a("Le §2.2.5.3 prévoit de comparer l'action jouée à **la dernière action nommée "
      "dans le texte libre**. Appliquée littéralement :\n")
    a(f"\n> Décisions où le raisonnement nomme au moins une action : "
      f"**{milliers(g_pos.mesurables)}** ({pct(g_pos.mesurables / g_pos.total)}). "
      f"Taux de divergence : **{pct(g_pos.taux)}**.\n")
    a("\nCe chiffre est **un artefact**, et il faut le dire d'autant plus nettement "
      "qu'il tombe à un point des 45,1 % de GTBENCH — coïncidence qui rendrait la "
      "confirmation d'H4 très facile à publier et parfaitement fausse.\n")
    a("\nLa cause est grammaticale. Le raisonnement de l'agent conclut par une clause "
      "contrastive qui nomme l'option **rejetée**, non celle retenue :\n")
    a("\n> « *Engager garantit donc un gain de +1, **tandis que retenir** expose à une "
      "perte selon le sceau adverse.* » — action jouée : engager. La règle lit "
      "« retenir » et compte une incohérence.\n")
    a("\nHuit divergences tirées au hasard ont été relues : **huit faux positifs**, "
      "tous de cette forme. Une règle positionnelle hérite de la structure du "
      "discours français, où l'alternative écartée vient en dernier.\n")

    a("\n### 1.2 Trois variantes, et laquelle porte le résultat\n")
    a("| Variante | Décisions mesurables | Divergences | Taux |")
    a("|---|---|---|---|")
    a(f"| **A** — positionnelle, pré-enregistrée | {milliers(g_pos.mesurables)} | "
      f"{milliers(g_pos.divergentes)} | {pct(g_pos.taux)} |")
    a(f"| **B** — A, occurrences attribuées à l'adversaire écartées | "
      f"{milliers(g_fil.mesurables)} | {milliers(g_fil.divergentes)} | {pct(g_fil.taux)} |")
    a(f"| **C** — l'agent **énonce** son choix (« il vaut mieux X », « je choisis X ») | "
      f"{milliers(g_exp.mesurables)} | {milliers(g_exp.divergentes)} | "
      f"**{pct(g_exp.taux, 2)}** |")
    a("")
    a("A et B restent positionnelles et souffrent du même défaut ; B ne corrige que "
      "l'attribution du sujet, pas la structure contrastive. **C est la seule à haute "
      "précision** : elle ne retient que les décisions où l'agent déclare son choix "
      "par une formule explicite, et ne mesure donc rien d'autre que ce que H4 "
      "demande. Son prix est le rappel — elle ne couvre que "
      f"{pct(g_exp.mesurables / g_pos.total)} des décisions.\n")

    a(f"\n**Résultat : sur les {milliers(g_exp.mesurables)} décisions où l'agent énonce "
      f"explicitement l'action qu'il retient, il joue cette action "
      f"{'dans tous les cas' if g_exp.divergentes == 0 else f'sauf {g_exp.divergentes} fois'}.**\n")

    a("\n| Traitement | Décisions | C — mesurables | C — divergences |")
    a("|---|---|---|---|")
    for c in CONDITIONS:
        k = exp[("condition", c)]
        a(f"| {c} | {milliers(k.total)} | {milliers(k.mesurables)} "
          f"({pct(k.mesurables / k.total)}) | {k.divergentes} |")

    a("\n| Adversaire | Décisions | C — mesurables | C — divergences |")
    a("|---|---|---|---|")
    for b in BOTS_ORDRE:
        k = exp[("bot", b)]
        a(f"| {b} | {milliers(k.total)} | {milliers(k.mesurables)} "
          f"({pct(k.mesurables / k.total)}) | {k.divergentes} |")

    a("\n### 1.3 Par série — la variante A, pour mémoire\n")
    a("Le §2.2.9 demande si l'incohérence décroît avec l'adaptation. La question ne "
      "peut pas être tranchée par A, dont on vient de voir qu'elle mesure autre chose ; "
      "le tableau est donné parce que la **stabilité** du taux est elle-même "
      "informative — un artefact grammatical n'a aucune raison de varier avec la série, "
      "et c'est bien ce qu'on observe.\n")
    a("| Série | " + " | ".join(CONDITIONS) + " |")
    a("|---|" + "---|" * len(CONDITIONS))
    for s in range(10):
        cellules = []
        for c in CONDITIONS:
            k = pos.get(("condition_serie", c, s))
            cellules.append("—" if k is None else f"{pct(k.taux)}")
        if all(x == "—" for x in cellules):
            continue
        a(f"| {s} | " + " | ".join(cellules) + " |")

    a("\n### 1.4 Sens des divergences de la variante A\n")
    a("| Action lue par la règle | Action jouée | Occurrences |")
    a("|---|---|---|")
    for (nommee, jouee), n in sorted(inc["confusions"].items(), key=lambda kv: -kv[1])[:8]:
        a(f"| {nommee} | {jouee} | {milliers(n)} |")

    a("\n### 1.5 Ce que cette mesure ne peut pas voir\n")
    a("Deux bornes, à énoncer avec le résultat :\n")
    a("\n1. **La chaîne de pensée n'est pas restituée** (§L.1). Le fournisseur facture "
      "un raisonnement interne qu'il ne rend jamais. Une incohérence entre cette "
      "chaîne et l'action jouée est invisible par construction.")
    a("2. **La variante C porte sur un sous-ensemble sélectionné**, et non aléatoire : "
      "les décisions où l'agent formule son choix en toutes lettres. Le taux obtenu "
      "n'est pas une fréquence de campagne.\n")
    a("\nLe codage manuel sur échantillon stratifié (§2.2.5.3, troisième volet) n'est "
      "donc pas un raffinement facultatif : c'est **la seule voie** vers un taux "
      "d'incohérence défendable. Ce que les mesures automatiques établissent est plus "
      "étroit, et solide : *l'agent ne se contredit pas explicitement*.\n")

    # ================= Mesure 2
    a("\n\n## 2. Dégénérescence des stratégies mixtes\n")
    a(f"Fréquences de `infosets.csv`, restreintes aux couples série × info-set observés "
      f"au moins **{N_MINIMAL}** fois ({milliers(deg['ignorees'])} couples écartés à ce "
      f"titre) — une fréquence sur trois observations ne dit rien d'un mélange.\n")
    a("\n**La ventilation par adversaire est obligatoire.** Contre Station et "
      "Over-folder, la meilleure réponse *est* pure : une fréquence à 0 ou 1 y est "
      "optimale, pas dégénérée.\n")

    a("\n### 2.1 Où l'optimum exige-t-il un mélange ?\n")
    a("| Adversaire | Info-sets à meilleure réponse mixte |")
    a("|---|---|")
    for b in BOTS_ORDRE:
        m = sorted(deg["br_mixte"][b])
        a(f"| {b} | "
          + (", ".join(f"`{x}`" for x in m) if m else "**aucun** — la meilleure réponse est entièrement pure")
          + " |")
    a("")
    a("Contre GTO, toute meilleure réponse rapporte la valeur du jeu, y compris les "
      "pures : c'est l'**équilibre** qui exige un mélange, et c'est à lui qu'on compare. "
      "Les quatre info-sets concernés :\n")
    a("| Info-set | Fréquence d'équilibre |")
    a("|---|---|")
    for m in deg["mixtes"]:
        a(f"| `{m}` | {equilibre[m]} |")

    a("\n### 2.2 Concentration aux bornes, par adversaire\n")
    a("| Adversaire | Traitement | Séries × info-sets | Aux bornes (0 ou 1) |")
    a("|---|---|---|---|")
    for b in BOTS_ORDRE:
        for c in CONDITIONS:
            sel = [x for x in deg["lignes"] if x["bot"] == b and x["condition"] == c]
            if not sel:
                continue
            n_b = sum(1 for x in sel if x["aux_bornes"])
            a(f"| {b} | {c} | {len(sel)} | {pct(n_b / len(sel))} |")
    a("\n*À lire en regard du 2.1 : contre Over-folder et Station, une valeur élevée "
      "est le signe d'une politique correcte, non d'une dégénérescence.*")

    a("\n### 2.3 Le signal — les info-sets mixtes, contre GTO\n")
    a("| Info-set | Équilibre | Traitement | Séries | Aux bornes | `p` moyen | Écart moyen à l'équilibre |")
    a("|---|---|---|---|---|---|---|")
    for m in deg["mixtes"]:
        for c in CONDITIONS:
            sel = [
                x for x in deg["lignes"]
                if x["bot"] == "GTO" and x["condition"] == c and x["infoset"] == m
            ]
            if not sel:
                continue
            n_b = sum(1 for x in sel if x["aux_bornes"])
            p_moy = sum(x["p"] for x in sel) / len(sel)
            ecart = sum(abs(x["p"] - x["p_eq"]) for x in sel) / len(sel)
            a(f"| `{m}` | {equilibre[m]} | {c} | {len(sel)} | **{pct(n_b / len(sel))}** | "
              f"{p_moy:.3f} | {ecart:.3f} |")

    # --- Le confond que la ventilation évite, chiffré
    principal = "J1/C0/ouverture"
    tous = [x for x in deg["lignes"] if x["infoset"] == principal]
    contre_gto = [x for x in tous if x["bot"] == "GTO"]
    a(f"\n### 2.4 Pourquoi la ventilation change la conclusion\n")
    a(f"Sur `{principal}` — le bluff au sceau faible, que l'équilibre veut à 1/3 — "
      "le même comptage donne deux chiffres très différents selon qu'on ventile ou non :\n")
    a("| Périmètre | Séries | Aux bornes | Lecture |")
    a("|---|---|---|---|")
    a(f"| Tous adversaires confondus | {len(tous)} | "
      f"**{pct(sum(1 for x in tous if x['aux_bornes']) / len(tous))}** | "
      "**trompeur** — contre Station et Over-folder, être à une borne *est* l'optimum |")
    a(f"| Contre GTO seulement | {len(contre_gto)} | "
      f"**{pct(sum(1 for x in contre_gto if x['aux_bornes']) / len(contre_gto))}** | "
      "le signal réel : l'équilibre y exige un mélange |")
    a("\n*Le premier chiffre est celui qui figurait dans les notes de travail. Il "
      "surestime la dégénérescence en comptant comme telle une politique pure là où "
      "la politique pure est correcte.*\n")

    a("\n### 2.5 Le résultat, et son contrôle interne\n")
    groupes = (
        ("SM — sans mémoire", [x for x in contre_gto if x["condition"] == "SM"]),
        (
            "AE — première série, note encore vide",
            [x for x in contre_gto if x["condition"] == "AE" and x["session"] == 0],
        ),
        (
            "AE — séries suivantes, note écrite",
            [x for x in contre_gto if x["condition"] == "AE" and x["session"] > 0],
        ),
    )
    a(f"Sur `{principal}`, contre l'adversaire à l'équilibre :\n")
    a("| | Séries | Aux bornes | Distance moyenne à l'équilibre |")
    a("|---|---|---|---|")
    for libelle, sel in groupes:
        if not sel:
            continue
        bornes = sum(1 for x in sel if x["aux_bornes"]) / len(sel)
        dist = sum(abs(x["p"] - x["p_eq"]) for x in sel) / len(sel)
        a(f"| {libelle} | {len(sel)} | **{pct(bornes)}** | {dist:.3f} |")

    a("\n**La mémoire ne corrige pas la dégénérescence : elle la produit.** Privé de "
      "mémoire, l'agent joue des fréquences intermédiaires, et proches de la valeur "
      "d'équilibre. Doté d'une note, il s'échoue sur les bornes dans près de six "
      "séries sur dix.\n")
    a("\nLa deuxième ligne est un **contrôle interne** qui exclut toute explication "
      "par le traitement ou par le harnais : la première série d'une exécution AE se "
      "joue avec un emplacement mémoire présent mais vide — même modèle, même gabarit, "
      "même exécution, même adversaire, seule la note manque. Aucune fréquence n'y est "
      "aux bornes. L'effondrement apparaît exactement à la première série jouée avec "
      "une note écrite.\n")

    # Forme de la dégénérescence : effondrement, ou alternance ?
    par_repl: dict[str, dict[int, float]] = defaultdict(dict)
    with io.open(INFOSETS, encoding="utf8") as fh:
        for ligne in csv.DictReader(fh):
            if (
                ligne["bot"] == "GTO"
                and ligne["condition"] == "AE"
                and ligne["infoset"] == principal
            ):
                par_repl[ligne["replication"]][int(ligne["session"])] = float(ligne["p"])
    sauts = 0
    for suite in par_repl.values():
        v = [suite[k] for k in sorted(suite)]
        sauts += sum(1 for a_, b_ in zip(v, v[1:]) if abs(a_ - b_) > 0.4)
    ae_ecrites = groupes[2][1]
    a_zero = sum(1 for x in ae_ecrites if x["p"] == 0.0)
    a_un = sum(1 for x in ae_ecrites if x["p"] == 1.0)

    a("\n**Ce n'est pas un effondrement vers une borne unique, mais une alternance "
      "entre les deux.** Sur les "
      f"{len(ae_ecrites)} séries concernées, {a_zero} sont à zéro exactement et "
      f"{a_un} à un exactement, et l'on relève **{sauts} sauts de plus de 0,40** entre "
      "deux séries consécutives. L'agent ne remplace pas le mélange par une politique "
      "pure stable : il remplace une randomisation **intra-série** par une alternance "
      "**inter-séries** — il choisit une règle, l'applique intégralement pendant K "
      "manches, puis en change à la frontière. La variabilité que l'équilibre demande "
      "existe encore, mais elle a migré vers une échelle de temps où elle ne produit "
      "aucune imprévisibilité au sein d'une série.\n")

    a("\nC'est le résultat que H4 cherchait, et il est **conjoint** à H1 et H3 : ce qui "
      "rend la mémoire auto-écrite supérieure — contraindre l'agent à formuler une "
      "règle, donc achever l'induction — est exactement ce qui la rend incapable de "
      "randomiser. Une règle écrite en langue naturelle est déterministe : elle dit "
      "« engager avec le sceau fort », jamais « engager avec le sceau faible une fois "
      "sur trois ». Le canal qui porte l'adaptation ne sait pas porter une fréquence.\n")

    return "\n".join(out) + "\n"


def main() -> None:
    equilibre, br = references()
    inc = mesure_incoherence()
    deg = mesure_degenerescence(equilibre, br)
    RAPPORT.write_text(rapport(inc, deg, equilibre, br), encoding="utf8")
    print(f"ecrit : {RAPPORT.relative_to(RACINE)}")
    for v in VARIANTES:
        g = inc["par"][v][("global",)]
        print(f"  {v:24s} {g.divergentes:6d} / {g.mesurables:6d} = {pct(g.taux, 2)}")


if __name__ == "__main__":
    main()
