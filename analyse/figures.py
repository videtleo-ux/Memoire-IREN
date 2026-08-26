"""Figures de la partie III, tracées depuis `donnees/sessions.csv`.

Deux sorties, correspondant aux points 1 et 2 du plan d'analyse (§2.2.9 du
chapitre de méthode) :

  figures/fig1-trajectoires.png  — Écart(s) par série, un panneau par adversaire,
                                   les trois traitements sur les mêmes axes.
  figures/fig2-recitation.png    — référence récitée par série, même découpage.

⚠️ Les deux instruments ne sont pas indépendants. À adversaire fixé,
`écart(s) + référence récitée(s) = EV(meilleure réponse) − EV(équilibre)`, une
constante — l'écart d'un récitant. Vérifié exactement sur les 177 séries. La
figure 2 est donc un *recalage affine* de la figure 1, pas une seconde mesure :
elle est tracée parce qu'elle déplace le zéro sur le comportement du récitant,
ce qui rend lisible le franchissement de signe qui teste H2, et non parce
qu'elle ajouterait un degré de liberté. Le plan d'analyse prévoyait une
trajectoire dans le plan des deux instruments : elle ne peut être qu'une droite
de pente −1, et n'est donc pas produite.

    "C:/Users/videt/anaconda3/python.exe" analyse/figures.py
"""

from __future__ import annotations

import csv
import io
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RACINE = Path(__file__).resolve().parent.parent
SESSIONS = RACINE / "donnees" / "sessions.csv"
SORTIE = RACINE / "memoire" / "figures"

# Ordre de lecture : marge d'exploitation décroissante.
BOTS = ["Over-folder", "Station", "GTO"]
CONDITIONS = ["SM", "ICL", "AE"]

# L'écart d'un récitant, par adversaire (§2.2.2). C'est l'étalon de lecture.
ECART_RECITANT = {"Over-folder": 7 / 9, "Station": 1 / 9, "GTO": 0.0}

COULEUR = {"SM": "#9a9a9a", "ICL": "#c1651a", "AE": "#1f5fa8"}
LIBELLE = {
    "SM": "SM — sans mémoire",
    "ICL": "ICL — historique brut",
    "AE": "AE — mémoire auto-écrite",
}


def charger() -> dict[tuple[str, str, int], list[tuple[int, float, float]]]:
    """(bot, condition, réplication) -> [(série, écart, référence récitée)]."""
    series: dict[tuple[str, str, int], list[tuple[int, float, float]]] = defaultdict(list)
    with io.open(SESSIONS, encoding="utf8") as fh:
        for ligne in csv.DictReader(fh):
            cle = (ligne["bot"], ligne["condition"], int(ligne["replication"]))
            series[cle].append(
                (
                    int(ligne["session"]),
                    float(ligne["ecart"]),
                    float(ligne["reference_recite"]),
                )
            )
    for points in series.values():
        points.sort()
    return series


def moyenne_par_serie(
    series, bot: str, condition: str, indice: int
) -> tuple[list[int], list[float]]:
    """Moyenne inter-réplications, série par série, sur les séries observées partout."""
    par_serie: dict[int, list[float]] = defaultdict(list)
    for (b, c, _), points in series.items():
        if b == bot and c == condition:
            for s, ecart, recite in points:
                par_serie[s].append((ecart, recite)[indice])
    if not par_serie:
        return [], []
    n_repl = max(len(v) for v in par_serie.values())
    gardees = sorted(s for s, v in par_serie.items() if len(v) == n_repl)
    return gardees, [sum(par_serie[s]) / len(par_serie[s]) for s in gardees]


def figure_trajectoires(series) -> Path:
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))

    for ax, bot in zip(axes, BOTS):
        recitant = ECART_RECITANT[bot]
        ax.axhline(0, color="#333333", lw=1.1, zorder=1)
        if recitant > 0:
            ax.axhline(
                recitant,
                color="#333333",
                lw=1.0,
                ls=(0, (5, 3)),
                zorder=1,
            )
            ax.annotate(
                f"écart d'un récitant ({recitant:.3f})",
                xy=(0.98, recitant),
                xycoords=("axes fraction", "data"),
                ha="right",
                va="top",
                fontsize=7.5,
                color="#333333",
                xytext=(0, -3),
                textcoords="offset points",
            )

        for condition in CONDITIONS:
            couleur = COULEUR[condition]
            # Réplications individuelles, en filigrane.
            for (b, c, _), points in sorted(series.items()):
                if b == bot and c == condition:
                    xs = [p[0] for p in points]
                    ys = [p[1] for p in points]
                    ax.plot(xs, ys, color=couleur, lw=0.8, alpha=0.30, zorder=2)
            xs, ys = moyenne_par_serie(series, bot, condition, 0)
            if xs:
                ax.plot(
                    xs,
                    ys,
                    color=couleur,
                    lw=2.2,
                    marker="o",
                    ms=4,
                    zorder=3,
                    label=LIBELLE[condition],
                )

        ax.set_title(f"contre {bot}", fontsize=11)
        ax.set_xlabel("série")
        ax.set_xticks(range(0, 10, 2))
        ax.set_ylim(-0.05, 0.90)
        ax.grid(axis="y", color="#e6e6e6", lw=0.7, zorder=0)
        for cote in ("top", "right"):
            ax.spines[cote].set_visible(False)

    axes[0].set_ylabel("écart d'exploitation (jetons / manche)")
    axes[0].legend(frameon=False, fontsize=8.5, loc="center right")

    fig.suptitle(
        "Trajectoires d'adaptation — écart d'exploitation par série",
        fontsize=13,
        y=0.99,
    )
    fig.text(
        0.5,
        0.008,
        "Traits épais : moyenne des trois réplications. Traits fins : réplications individuelles. "
        "Zéro = exploitation optimale.\nLa condition SM s'arrête à la série 2 : sans mémoire, rien "
        "ne s'accumule d'une série à l'autre, et trois points suffisent à établir le niveau récité "
        "et sa dispersion (§2.2.6). La condition ICL n'a pas été jouée contre GTO (§2.2.7).",
        ha="center",
        fontsize=7.5,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.075, 1, 0.96))

    chemin = SORTIE / "fig1-trajectoires.png"
    fig.savefig(chemin, dpi=200)
    plt.close(fig)
    return chemin


def figure_recitation(series) -> Path:
    """La référence récitée par série : au-dessus de zéro, l'agent fait mieux que
    l'équilibre ; en dessous, moins bien. Le plafond est l'exploitation parfaite."""
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))

    for ax, bot in zip(axes, BOTS):
        # Le maximum de la référence récitée vaut l'écart d'un récitant (voir l'en-tête).
        maximum = ECART_RECITANT[bot]
        ax.axhline(0, color="#333333", lw=1.4, zorder=1)
        ax.annotate(
            "niveau d'un récitant",
            xy=(0.02, 0),
            xycoords=("axes fraction", "data"),
            xytext=(0, 3),
            textcoords="offset points",
            fontsize=7.5,
            color="#333333",
        )
        if maximum > 0:
            ax.axhline(maximum, color="#b03030", lw=1.1, ls=(0, (5, 3)), zorder=1)
            ax.annotate(
                f"exploitation maximale ({maximum:.3f})",
                xy=(0.98, maximum),
                xycoords=("axes fraction", "data"),
                ha="right",
                va="top",
                xytext=(0, -3),
                textcoords="offset points",
                fontsize=7.5,
                color="#b03030",
            )

        for condition in CONDITIONS:
            couleur = COULEUR[condition]
            for (b, c, _), points in sorted(series.items()):
                if b == bot and c == condition:
                    ax.plot(
                        [p[0] for p in points],
                        [p[2] for p in points],
                        color=couleur,
                        lw=0.8,
                        alpha=0.30,
                        zorder=2,
                    )
            xs, ys = moyenne_par_serie(series, bot, condition, 1)
            if xs:
                ax.plot(
                    xs,
                    ys,
                    color=couleur,
                    lw=2.2,
                    marker="o",
                    ms=4,
                    zorder=3,
                    label=LIBELLE[condition],
                )

        ax.set_title(f"contre {bot}", fontsize=11)
        ax.set_xlabel("série")
        ax.set_xticks(range(0, 10, 2))
        ax.grid(axis="y", color="#e6e6e6", lw=0.7, zorder=0)
        for cote in ("top", "right"):
            ax.spines[cote].set_visible(False)

    axes[0].set_ylabel("référence récitée (jetons / manche)")
    axes[0].legend(frameon=False, fontsize=8.5, loc="center right")

    fig.suptitle(
        "Récitation ou exploitation — distance au comportement d'équilibre",
        fontsize=13,
        y=0.99,
    )
    fig.text(
        0.5,
        0.008,
        "Un agent qui appliquerait l'équilibre resterait sur zéro quel que soit l'adversaire. "
        "Échelles propres à chaque panneau.\nLa condition SM s'arrête à la série 2 (§2.2.6). "
        "Recalage affine de la figure 1 : à adversaire fixé, les deux instruments somment à une "
        "constante.",
        ha="center",
        fontsize=7.5,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.075, 1, 0.96))

    chemin = SORTIE / "fig2-recitation.png"
    fig.savefig(chemin, dpi=200)
    plt.close(fig)
    return chemin


def main() -> None:
    SORTIE.mkdir(parents=True, exist_ok=True)
    series = charger()
    for chemin in (figure_trajectoires(series), figure_recitation(series)):
        print(f"écrit : {chemin.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
