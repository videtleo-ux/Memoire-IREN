"""Convertit `memoire/partie3.md` en un vrai document Word.

    "C:/Users/videt/anaconda3/python.exe" analyse/rendre-partie3-docx.py

Produit `memoire/partie3.docx`. Les titres portent les styles Word intégrés
(Titre 1/2/3), donc ils prennent l'apparence du document d'accueil au collage ;
les tableaux portent « Grille du tableau » ; les figures sont insérées à leur
place, mises à la largeur d'une page A4 avec marges.

Le Markdown reste la source. Une correction faite directement dans Word sera
écrasée à la prochaine régénération : la reporter dans `partie3.md`.
"""

from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "memoire" / "partie3.md"
FIGURES = RACINE / "memoire" / "figures"
SORTIE = RACINE / "memoire" / "partie3.docx"

#: Largeur utile d'une page A4 (21 cm) avec des marges de 2,5 cm.
LARGEUR_FIGURE = Cm(16)

LEGENDES = {
    "fig1-trajectoires.png": (
        "Figure 1 — Trajectoires d'adaptation : écart d'exploitation par série"
    ),
    "fig2-recitation.png": (
        "Figure 2 — Récitation ou exploitation : distance au comportement d'équilibre"
    ),
}

APPEL_FIGURE = re.compile(
    r"^\*\*Figure \d[^\n]*?\*\*\s*\*\(`memoire/figures/([^`]+)`\)\*\s*$"
)

#: Découpe une ligne en fragments formatés. L'ordre compte : le gras avant
#: l'italique, sans quoi `**` serait lu comme deux `*`.
FRAGMENTS = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)")


def ecrire_texte(paragraphe, texte: str) -> None:
    """Ajoute `texte` au paragraphe en respectant gras, italique et code."""
    for morceau in FRAGMENTS.split(texte):
        if not morceau:
            continue
        if morceau.startswith("**") and morceau.endswith("**"):
            paragraphe.add_run(morceau[2:-2]).bold = True
        elif morceau.startswith("*") and morceau.endswith("*"):
            paragraphe.add_run(morceau[1:-1]).italic = True
        elif morceau.startswith("`") and morceau.endswith("`"):
            run = paragraphe.add_run(morceau[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(10)
        else:
            paragraphe.add_run(morceau)


def cellules(ligne: str) -> list[str]:
    return [c.strip() for c in ligne.strip().strip("|").split("|")]


def ajouter_tableau(doc: Document, lignes: list[str]) -> None:
    entetes = cellules(lignes[0])
    corps = [cellules(x) for x in lignes[2:]]
    table = doc.add_table(rows=1, cols=len(entetes))
    table.style = "Table Grid"
    for cellule, texte in zip(table.rows[0].cells, entetes):
        cellule.paragraphs[0].text = ""
        run = cellule.paragraphs[0].add_run(texte)
        run.bold = True
    for rangee in corps:
        cells = table.add_row().cells
        for cellule, texte in zip(cells, rangee):
            cellule.paragraphs[0].text = ""
            ecrire_texte(cellule.paragraphs[0], texte)
    doc.add_paragraph()


def ajouter_citation(doc: Document, lignes: list[str]) -> None:
    """Un bloc `>` : le corps en style Citation, la source en petit italique."""
    corps = [x[2:] if x.startswith("> ") else x[1:] for x in lignes]
    source = None
    if corps and corps[-1].lstrip().startswith("—"):
        source = corps.pop().lstrip()
    p = doc.add_paragraph(style="Quote")
    ecrire_texte(p, " ".join(x.strip() for x in corps if x.strip()))
    if source:
        ps = doc.add_paragraph()
        ps.paragraph_format.left_indent = Cm(1.5)
        ecrire_texte(ps, source)
        for run in ps.runs:
            run.italic = True
            run.font.size = Pt(9)


def ajouter_figure(doc: Document, fichier: str) -> None:
    chemin = FIGURES / fichier
    if not chemin.exists():
        raise SystemExit(f"figure introuvable : {chemin}")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(chemin), width=LARGEUR_FIGURE)
    legende = doc.add_paragraph(LEGENDES.get(fichier, fichier))
    legende.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in legende.runs:
        run.italic = True
        run.font.size = Pt(9)


def convertir(texte: str) -> Document:
    doc = Document()
    lignes = texte.split("\n")
    i = 0
    while i < len(lignes):
        ligne = lignes[i]
        nu = ligne.strip()

        if not nu or nu == "---":
            i += 1
            continue

        # Note de travail : n'appartient pas au mémoire.
        if nu.startswith("> **État de rédaction**"):
            while i < len(lignes) and lignes[i].strip().startswith(">"):
                i += 1
            continue

        figure = APPEL_FIGURE.match(nu)
        if figure:
            ajouter_figure(doc, figure.group(1))
            i += 1
            continue

        if nu.startswith("#"):
            niveau = len(nu) - len(nu.lstrip("#"))
            doc.add_heading(nu.lstrip("#").strip(), level=min(niveau, 4))
            i += 1
            continue

        if nu.startswith("|"):
            bloc = []
            while i < len(lignes) and lignes[i].strip().startswith("|"):
                bloc.append(lignes[i])
                i += 1
            if len(bloc) >= 2:
                ajouter_tableau(doc, bloc)
            continue

        if nu.startswith(">"):
            bloc = []
            while i < len(lignes) and lignes[i].strip().startswith(">"):
                bloc.append(lignes[i].strip())
                i += 1
            ajouter_citation(doc, bloc)
            continue

        puce = re.match(r"^[-*]\s+(.*)$", nu)
        numero = re.match(r"^\d+\.\s+(.*)$", nu)
        if puce or numero:
            style = "List Bullet" if puce else "List Number"
            contenu = (puce or numero).group(1)
            i += 1
            # Une entrée de liste peut se poursuivre sur les lignes indentées.
            while i < len(lignes) and lignes[i].startswith("   ") and lignes[i].strip():
                contenu += " " + lignes[i].strip()
                i += 1
            ecrire_texte(doc.add_paragraph(style=style), contenu)
            continue

        # Paragraphe ordinaire : replier les retours à la ligne du Markdown.
        bloc = []
        while i < len(lignes) and lignes[i].strip() and not re.match(
            r"^\s*([#|>-]|\d+\.\s)", lignes[i]
        ):
            bloc.append(lignes[i].strip())
            i += 1
        if bloc:
            ecrire_texte(doc.add_paragraph(), " ".join(bloc))

    return doc


def main() -> None:
    doc = convertir(SOURCE.read_text(encoding="utf8"))
    doc.save(SORTIE)
    tableaux = len(doc.tables)
    titres = sum(1 for p in doc.paragraphs if p.style.name.startswith("Heading"))
    print(f"écrit : {SORTIE.relative_to(RACINE)}")
    print(f"  {titres} titres · {tableaux} tableaux · {len(LEGENDES)} figures")


if __name__ == "__main__":
    main()
