# -*- coding: utf-8 -*-
"""Briques XML pour Soutenance.pptx — reprend le design system du fichier.

Titre    Playfair Display SemiBold 26 pt #993333, x 0,5" y 0,35"
Carte    roundRect adj 2285, fond #FDFBF7, filet #E5E5E5, barre d'accent bordeaux
Corps    Inter — titre de carte Playfair Display gras, puces ● Inter
"""
from __future__ import annotations

EMU = 914400


def po(x: float) -> int:
    return int(round(x * EMU))


BORD = "993333"
CARD_BG = "FDFBF7"
CARD_LN = "E5E5E5"
TXT = "333333"
MUTED = "5B6570"
WHITE = "FFFFFF"
PLAYFAIR = "Playfair Display"
PLAYFAIR_SB = "Playfair Display SemiBold"
INTER = "Inter"


def esc(t: str) -> str:
    # Espaces insécables devant la ponctuation double et dans les guillemets,
    # sinon PowerPoint coupe la ligne avant « » », « : » ou « ? ».
    t = (t.replace("« ", "« ").replace(" »", " »")
          .replace(" :", " :").replace(" ;", " ;")
          .replace(" ?", " ?").replace(" !", " !")
          .replace(" %", " %").replace(" $", " $"))
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _font(name: str) -> str:
    return (f'<a:latin typeface="{name}"/><a:ea typeface="{name}"/>'
            f'<a:cs typeface="{name}"/><a:sym typeface="{name}"/>')


def run(text: str, sz: int, color: str = TXT, bold: bool = False,
        font: str = INTER, italic: bool = False) -> str:
    b = ' b="1"' if bold else ' b="0"'
    i = ' i="1"' if italic else ''
    return (f'<a:r><a:rPr{b}{i} lang="fr" sz="{sz}">'
            f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{_font(font)}'
            f'</a:rPr><a:t>{esc(text)}</a:t></a:r>')


def para(runs: str, spc_before: int = 0, bullet: str | None = None,
         mar_l: int = 0, indent: int = 0, algn: str = "l",
         bul_color: str = TXT, bul_sz: int = 900, line: int | None = None) -> str:
    if bullet:
        bu = (f'<a:buClr><a:srgbClr val="{bul_color}"/></a:buClr>'
              f'<a:buSzPts val="{bul_sz}"/><a:buFont typeface="{INTER}"/>'
              f'<a:buChar char="{bullet}"/>')
    else:
        bu = '<a:buNone/>'
    ln = f'<a:lnSpc><a:spcPct val="{line}"/></a:lnSpc>' if line else ''
    return (f'<a:p><a:pPr indent="{indent}" lvl="0" marL="{mar_l}" rtl="0" algn="{algn}">'
            f'{ln}<a:spcBef><a:spcPts val="{spc_before}"/></a:spcBef>'
            f'<a:spcAft><a:spcPts val="0"/></a:spcAft>{bu}</a:pPr>{runs}</a:p>')


def _body(paras: str, l=171450, t=171450, r=171450, b=171450, anchor="t") -> str:
    return (f'<p:txBody><a:bodyPr anchorCtr="0" anchor="{anchor}" bIns="{b}" lIns="{l}" '
            f'spcFirstLastPara="1" rIns="{r}" tIns="{t}" wrap="square"><a:noAutofit/>'
            f'</a:bodyPr><a:lstStyle/>{paras}</p:txBody>')


EMPTY_BODY = ('<p:txBody><a:bodyPr anchorCtr="0" anchor="ctr" bIns="0" lIns="0" '
              'spcFirstLastPara="1" rIns="0" tIns="0" wrap="square"><a:noAutofit/></a:bodyPr>'
              '<a:lstStyle/><a:p><a:pPr indent="0" lvl="0" marL="0" rtl="0" algn="l">'
              '<a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/>'
              '</a:spcAft><a:buNone/></a:pPr><a:r><a:t></a:t></a:r><a:endParaRPr/></a:p></p:txBody>')


class Ids:
    def __init__(self, start: int = 200):
        self.n = start

    def __call__(self) -> int:
        self.n += 1
        return self.n


def shape(ids: Ids, x, y, w, h, geom: str, sppr_extra: str, body: str,
          txbox: bool = False) -> str:
    i = ids()
    tb = ' txBox="1"' if txbox else ''
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="Shape {i}"/>'
            f'<p:cNvSpPr{tb}/><p:nvPr/></p:nvSpPr><p:spPr>'
            f'<a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'{geom}{sppr_extra}</p:spPr>{body}</p:sp>')


RECT = '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'


def round_rect(adj: int = 2285) -> str:
    return (f'<a:prstGeom prst="roundRect"><a:avLst>'
            f'<a:gd fmla="val {adj}" name="adj"/></a:avLst></a:prstGeom>')


def fill_ln(fill: str, line: str | None = None, w: int = 9525) -> str:
    f = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>'
    if line:
        l = (f'<a:ln cap="flat" cmpd="sng" w="{w}"><a:solidFill>'
             f'<a:srgbClr val="{line}"/></a:solidFill><a:prstDash val="solid"/><a:round/>'
             f'<a:headEnd len="sm" w="sm" type="none"/><a:tailEnd len="sm" w="sm" type="none"/></a:ln>')
    else:
        l = '<a:ln><a:noFill/></a:ln>'
    return f + l


NOFILL = '<a:noFill/><a:ln><a:noFill/></a:ln>'

# --------------------------------------------------------------------------- #
#  Composants                                                                  #
# --------------------------------------------------------------------------- #


def title(ids: Ids, text: str) -> str:
    """Titre de slide, aux coordonnées exactes des slides existantes."""
    p = para(run(text, 2600, BORD, font=PLAYFAIR_SB))
    body = _body(p, l=0, t=0, r=0, b=0, anchor="ctr")
    return shape(ids, 457200, 320040, 8229600, 502800, RECT, NOFILL, body)


def logos(ids: Ids) -> str:
    out = []
    for rid, x, y, w, h in (("rId3", 7069653, 4768707, 975794, 324442),
                            ("rId4", 8110420, 4727450, 921506, 324441)):
        i = ids()
        out.append(
            f'<p:pic><p:nvPicPr><p:cNvPr id="{i}" name="Logo {i}"/>'
            f'<p:cNvPicPr preferRelativeResize="0"/><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"><a:alphaModFix/></a:blip>'
            f'<a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr>'
            f'<a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'{RECT}<a:noFill/><a:ln><a:noFill/></a:ln></p:spPr></p:pic>')
    return "".join(out)


def picture(ids: Ids, rid: str, x, y, w, h) -> str:
    i = ids()
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{i}" name="Figure {i}"/>'
            f'<p:cNvPicPr preferRelativeResize="0"/><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"><a:alphaModFix/></a:blip>'
            f'<a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr>'
            f'<a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'{RECT}<a:noFill/><a:ln><a:noFill/></a:ln></p:spPr></p:pic>')


def _card_chrome(ids: Ids, x, y, w, h) -> str:
    """Fond + barre d'accent bordeaux (posés en coordonnées absolues)."""
    bg = shape(ids, x, y, w, h, round_rect(), fill_ln(CARD_BG, CARD_LN), EMPTY_BODY)
    bar = shape(ids, x, y, 38100, h, round_rect(50000), fill_ln(BORD), EMPTY_BODY)
    return bg + bar


def card(ids: Ids, x, y, w, h, heading: str | None, blocks: list,
         head_sz: int = 1300, body_sz: int = 900, spc: int = 500,
         pad: int = 171450) -> str:
    """blocks : ('lead', txt) | ('bul', label, txt) | ('bul', None, txt) | ('kv', k, v)"""
    paras = []
    if heading:
        paras.append(para(run(heading, head_sz, BORD, bold=True, font=PLAYFAIR)))
    first = not heading
    for blk in blocks:
        sb = 0 if first else spc
        first = False
        kind = blk[0]
        if kind == "lead":
            paras.append(para(run(blk[1], body_sz, MUTED), spc_before=sb + 100))
        elif kind == "bul":
            label, txt = blk[1], blk[2]
            r = ""
            if label:
                r += run(label, body_sz, TXT, bold=True)
                if txt:
                    r += run(" " + txt, body_sz, TXT)
            else:
                r += run(txt, body_sz, TXT)
            paras.append(para(r, spc_before=sb, bullet="●", mar_l=205740,
                              indent=-205740, bul_sz=body_sz - 100))
        elif kind == "plain":
            paras.append(para(run(blk[1], body_sz, TXT), spc_before=sb))
        elif kind == "formula":
            paras.append(para(run(blk[1], body_sz + 50, BORD, bold=True),
                              spc_before=sb + 100, algn="ctr"))
    body = _body("".join(paras), l=pad + 57150, t=pad, r=pad, b=pad)
    return _card_chrome(ids, x, y, w, h) + shape(ids, x, y, w, h, RECT, NOFILL, body,
                                                 txbox=True)


def table_card(ids: Ids, x, y, w, h, heading: str, cols: list[str],
               rows: list[list[str]], widths: list[float], head_sz: int = 1300,
               body_sz: int = 800, pad: int = 171450,
               bold_col: int | None = None, note: str | None = None) -> str:
    """Tableau rendu en colonnes de zones de texte (fiable à l'affichage)."""
    out = [_card_chrome(ids, x, y, w, h)]
    head_h = po(0.30) if heading else 0
    if heading:
        body = _body(para(run(heading, head_sz, BORD, bold=True, font=PLAYFAIR)),
                     l=pad + 57150, t=pad, r=pad, b=0)
        out.append(shape(ids, x, y, w, head_h + pad, RECT, NOFILL, body, txbox=True))
    inner_x = x + pad + 57150
    inner_w = w - 2 * pad - 57150
    top = y + pad + head_h + (po(0.10) if heading else 0)
    note_h = po(0.26) if note else 0
    total = sum(widths)
    cx = inner_x
    for j, cw in enumerate(widths):
        colw = int(inner_w * cw / total)
        algn = "l" if j == 0 else "r"
        paras = [para(run(cols[j], body_sz - 50, BORD, bold=True), algn=algn,
                      line=90000)]
        for r in rows:
            bold = (bold_col is not None and j == bold_col)
            paras.append(para(run(r[j], body_sz, TXT, bold=bold), spc_before=280,
                              algn=algn, line=90000))
        body = _body("".join(paras), l=0, t=0, r=0, b=0)
        out.append(shape(ids, cx, top, colw, h - (top - y) - pad - note_h, RECT,
                         NOFILL, body, txbox=True))
        cx += colw
    if note:
        body = _body(para(run(note, body_sz - 100, MUTED, italic=True)),
                     l=0, t=0, r=0, b=0)
        out.append(shape(ids, inner_x, y + h - pad - note_h, inner_w, note_h,
                         RECT, NOFILL, body, txbox=True))
    return "".join(out)


def band(ids: Ids, x, y, w, h, label: str, text: str, text_sz: int = 1250) -> str:
    """Bandeau bordeaux pour un énoncé fort."""
    paras = [para(run(label.upper(), 750, "E9C9C9", bold=True), algn="ctr"),
             para(run(text, text_sz, WHITE, font=PLAYFAIR, bold=True), spc_before=350,
                  algn="ctr", line=105000)]
    body = _body("".join(paras), l=po(0.3), t=po(0.16), r=po(0.3), b=po(0.16),
                 anchor="ctr")
    bg = shape(ids, x, y, w, h, round_rect(), fill_ln(BORD), EMPTY_BODY)
    return bg + shape(ids, x, y, w, h, RECT, NOFILL, body, txbox=True)


def tile(ids: Ids, x, y, w, h, label: str, value: str, sub: str) -> str:
    avant, apres = value.split("→")
    valeur = (run(avant.strip() + " ", 1500, TXT, font=PLAYFAIR, bold=True)
              + run("→", 1300, BORD, font=INTER, bold=True)
              + run(" " + apres.strip(), 1500, TXT, font=PLAYFAIR, bold=True))
    paras = [para(run(label, 800, BORD, bold=True), algn="ctr"),
             para(valeur, spc_before=180, algn="ctr"),
             para(run(sub, 750, MUTED), spc_before=150, algn="ctr")]
    body = _body("".join(paras), l=po(0.1), t=po(0.09), r=po(0.1), b=po(0.09),
                 anchor="ctr")
    bg = shape(ids, x, y, w, h, round_rect(), fill_ln(CARD_BG, CARD_LN), EMPTY_BODY)
    return bg + shape(ids, x, y, w, h, RECT, NOFILL, body, txbox=True)


SLIDE_OPEN = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:mv="urn:schemas-microsoft-com:mac:vml" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
    'xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
    'xmlns:dgm="http://schemas.openxmlformats.org/drawingml/2006/diagram" '
    'xmlns:o="urn:schemas-microsoft-com:office:office" '
    'xmlns:v="urn:schemas-microsoft-com:vml" '
    'xmlns:pvml="urn:schemas-microsoft-com:office:powerpoint" '
    'xmlns:com="http://schemas.openxmlformats.org/drawingml/2006/compatibility" '
    'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" '
    'xmlns:p15="http://schemas.microsoft.com/office/powerpoint/2012/main" '
    'xmlns:ahyp="http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor">'
    '<p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
    '</p:bgPr></p:bg><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name="Shape 1"/>'
    '<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm>'
    '<a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/>'
    '<a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>')

SLIDE_CLOSE = ('</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')


def build(shapes: str) -> str:
    return SLIDE_OPEN + shapes + SLIDE_CLOSE
