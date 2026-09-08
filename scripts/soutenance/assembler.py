# -*- coding: utf-8 -*-
"""Réécrit Soutenance.pptx : slides 2-6 et 8-11, figures, harmonisation 7 et 12.

HISTORIQUE, ET DESTRUCTIF. Depuis le 8 septembre 2026, la source du deck est
Soutenance.pptx lui-même, édité dans PowerPoint ; contenu.py ne le décrit plus.
Ce script repart du squelette et réécrit l'archive entière : il effacerait donc
toutes les retouches faites à la main. D'où la garde de main() — voir le README.
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from contenu import FIGURES, SLIDES  # noqa: E402

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent.parent
PPTX = RACINE / "Soutenance.pptx"
FIGDIR = RACINE / "memoire" / "figures"
# Le squelette versionné : la maquette d'origine (thème, polices embarquées,
# logos, slides 7 et 12). Chaque build repart de lui, jamais du fichier produit.
SAUVEGARDE = ICI / "Soutenance-squelette.pptx"

REL_IMG = ("http://schemas.openxmlformats.org/officeDocument/2006/"
           "relationships/image")


def rels_avec_figure(xml: str, cible: str) -> str:
    ajout = (f'<Relationship Id="rId5" Type="{REL_IMG}" Target="../media/{cible}"/>')
    return xml.replace("</Relationships>", ajout + "</Relationships>")


def harmoniser_slide7(xml: str) -> str:
    """Aligne le chrome des cartes sur celui de la slide 12."""
    xml = xml.replace('val="F9FAFB"', f'val="FDFBF7"')
    xml = xml.replace('val="E5E7EB"', 'val="E5E5E5"')
    xml = xml.replace('<a:gd fmla="val 3333" name="adj"/>',
                      '<a:gd fmla="val 2285" name="adj"/>')
    return xml


BARRE = ('<p:sp><p:nvSpPr><p:cNvPr id="{id}" name="Accent {id}"/><p:cNvSpPr/>'
         '<p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="0" y="0"/>'
         '<a:ext cx="38100" cy="{h}"/></a:xfrm><a:prstGeom prst="roundRect">'
         '<a:avLst><a:gd fmla="val 50000" name="adj"/></a:avLst></a:prstGeom>'
         '<a:solidFill><a:srgbClr val="{c}"/></a:solidFill>'
         '<a:ln><a:noFill/></a:ln></p:spPr><p:txBody>'
         '<a:bodyPr anchorCtr="0" anchor="ctr" bIns="0" lIns="0" spcFirstLastPara="1" '
         'rIns="0" tIns="0" wrap="square"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
         '<a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l">'
         '<a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/>'
         '</a:spcAft><a:buNone/></a:pPr><a:r><a:t></a:t></a:r><a:endParaRPr/></a:p>'
         '</p:txBody></p:sp>')


def harmoniser_slide12(xml: str) -> str:
    """Ajoute la barre d'accent bordeaux dans chaque carte, comme sur la slide 7."""
    xml = xml.replace('lIns="190500"', 'lIns="228600"')
    xml = xml.replace('indent="-295275" lvl="0" marL="457200"',
                      'indent="-205740" lvl="0" marL="205740"')
    couleurs = ["993333", "1E3A8A"]  # la carte « next steps » est bleue
    sortie, curseur, ident = [], 0, 900
    for m in re.finditer(r"<p:grpSp>", xml):
        debut = m.start()
        chext = re.search(r'<a:chExt cx="(\d+)" cy="(\d+)"/>', xml[debut:debut + 700])
        fin_bg = xml.index("</p:sp>", debut) + len("</p:sp>")
        ident += 1
        sortie.append(xml[curseur:fin_bg])
        sortie.append(BARRE.format(id=ident, h=chext.group(2),
                                   c=couleurs[min(ident - 901, 1)]))
        curseur = fin_bg
    sortie.append(xml[curseur:])
    return "".join(sortie)


GARDE = """\
REFUS — ce script écraserait Soutenance.pptx.

La source du deck est Soutenance.pptx lui-même depuis le 8 septembre 2026 : il
s'édite dans PowerPoint. contenu.py est resté à l'état de la génération et ne
décrit plus les slides. Réassembler depuis le squelette effacerait toutes les
retouches faites à la main.

Pour changer les notes de présentateur, c'est notes.py, qui ne touche pas aux
slides. Pour retoucher une slide, c'est PowerPoint (style dans deck.py).

Si tu veux vraiment repartir de zéro depuis contenu.py, en connaissance de
cause : sauvegarde d'abord Soutenance.pptx, puis relance avec --force."""


def main() -> None:
    if "--force" not in sys.argv[1:]:
        raise SystemExit(GARDE)
    if not SAUVEGARDE.exists():
        raise SystemExit(f"squelette introuvable : {SAUVEGARDE}")
    source = zipfile.ZipFile(SAUVEGARDE)
    entrees = {n: source.read(n) for n in source.namelist()}
    source.close()

    for numero, fabrique in SLIDES.items():
        entrees[f"ppt/slides/slide{numero}.xml"] = fabrique().encode("utf8")

    for numero, fichier in FIGURES.items():
        cible = f"fig-slide{numero}.png"
        entrees[f"ppt/media/{cible}"] = (FIGDIR / fichier).read_bytes()
        cle = f"ppt/slides/_rels/slide{numero}.xml.rels"
        entrees[cle] = rels_avec_figure(entrees[cle].decode("utf8"), cible).encode("utf8")

    entrees["ppt/slides/slide7.xml"] = harmoniser_slide7(
        entrees["ppt/slides/slide7.xml"].decode("utf8")).encode("utf8")
    entrees["ppt/slides/slide12.xml"] = harmoniser_slide12(
        entrees["ppt/slides/slide12.xml"].decode("utf8")).encode("utf8")

    with zipfile.ZipFile(PPTX, "w", zipfile.ZIP_DEFLATED) as sortie:
        for nom, donnees in entrees.items():
            sortie.writestr(nom, donnees)
    print("Soutenance.pptx réécrite :", len(entrees), "parties")


if __name__ == "__main__":
    main()
