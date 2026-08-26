"""Convertit `memoire/partie3.md` en un fichier que Word ouvre nativement.

Word n'interprète pas le Markdown : collé tel quel, il ressort avec ses `##`, ses
`**` et ses tableaux en tubes. Il ouvre en revanche le HTML et le convertit en
document réel — titres mappés sur les styles Titre 1/2/3, tableaux véritables,
gras et italiques préservés.

    "C:/Users/videt/anaconda3/python.exe" analyse/rendre-partie3-word.py

Produit `memoire/partie3-word.html`. Deux façons de s'en servir :

  1. Word → Fichier → Ouvrir → sélectionner le fichier, puis tout copier dans le
     mémoire (les figures suivent, les chemins étant relatifs).
  2. L'ouvrir dans un navigateur, Ctrl+A, Ctrl+C, coller dans Word.

La mise en forme est volontairement minimale : le document d'accueil impose ses
propres styles au collage, et un HTML trop stylé se colle mal.
"""

from __future__ import annotations

import re
from pathlib import Path

import markdown

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "memoire" / "partie3.md"
SORTIE = RACINE / "memoire" / "partie3-word.html"

#: Les appels de figure du Markdown, remplacés par l'image elle-même.
FIGURES = {
    "fig1-trajectoires.png": (
        "Figure 1 — Trajectoires d'adaptation : écart d'exploitation par série"
    ),
    "fig2-recitation.png": (
        "Figure 2 — Récitation ou exploitation : distance au comportement d'équilibre"
    ),
}

# Word applique ses propres styles aux titres ; on ne fixe ici que ce qu'il ne
# devine pas — les bordures de tableau et un peu de respiration.
STYLE = """
body { font-family: Cambria, Georgia, serif; font-size: 12pt; line-height: 1.4; }
table { border-collapse: collapse; margin: 12pt 0; }
th, td { border: 1px solid #000000; padding: 4pt 8pt; vertical-align: top; }
th { background: #eeeeee; text-align: left; }
blockquote { margin: 12pt 0 12pt 24pt; font-style: italic; }
figure { margin: 16pt 0; text-align: center; }
figure img { max-width: 100%; }
figcaption { font-size: 10pt; font-style: italic; margin-top: 6pt; }
code { font-family: Consolas, monospace; font-size: 10.5pt; }
"""


def preparer(texte: str) -> str:
    """Retire les notes de travail et remplace les appels de figure."""
    # La note d'état de rédaction n'appartient pas au mémoire.
    texte = re.sub(r"^> \*\*État de rédaction\*\*.*?\n\n", "", texte, flags=re.S | re.M)

    for fichier, legende in FIGURES.items():
        # « **Figure n — titre.** *(`memoire/figures/xxx.png`)* »
        motif = re.compile(
            r"\*\*Figure \d[^\n]*?\*\*\s*\*\(`memoire/figures/" + re.escape(fichier) + r"`\)\*"
        )
        remplacement = (
            f'<figure><img src="figures/{fichier}" alt="{legende}">'
            f"<figcaption>{legende}</figcaption></figure>"
        )
        texte, n = motif.subn(remplacement, texte)
        if not n:
            raise SystemExit(f"appel de figure introuvable pour {fichier}")
    return texte


def main() -> None:
    texte = preparer(SOURCE.read_text(encoding="utf8"))
    corps = markdown.markdown(
        texte,
        extensions=["tables", "md_in_html"],
        output_format="html",
    )
    # Word rend mieux les tableaux qui portent leurs attributs en dur.
    corps = corps.replace("<table>", '<table border="1" cellspacing="0" cellpadding="4">')

    page = (
        '<html><head><meta charset="utf-8">'
        "<title>Partie III — Résultats et analyses</title>"
        f"<style>{STYLE}</style></head><body>\n{corps}\n</body></html>\n"
    )
    SORTIE.write_text(page, encoding="utf8")

    mots = len(texte.split())
    print(f"écrit : {SORTIE.relative_to(RACINE)}")
    print(f"  {mots} mots · {corps.count('<table')} tableaux · {len(FIGURES)} figures")


if __name__ == "__main__":
    main()
