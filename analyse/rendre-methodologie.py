# Rend le chapitre de methode en page consultable.
# Le Markdown du depot reste la source ; ce script ne fait que le mettre en page.
import html
import re
from pathlib import Path

import markdown

SOURCE = Path(
    "C:/Users/videt/OneDrive/Bureau/Fac/Master 2 - IREN/"
    "Exercices de recherches/Exercice 3 Mémoire/Code/memoire/methodologie.md"
)
CIBLE = Path(__file__).with_name("methodologie.html")

texte = SOURCE.read_text(encoding="utf-8")

# L'en-tete du document est repris dans le bandeau : on le retire du corps.
lignes = texte.splitlines()
debut = next(i for i, l in enumerate(lignes) if l.startswith("> **Note de structure"))
note_structure = lignes[debut][2:].strip()
corps_md = "\n".join(lignes[debut + 1 :]).lstrip("\n").lstrip("-").lstrip("\n")

md = markdown.Markdown(extensions=["tables", "toc", "sane_lists", "attr_list"])
corps = md.convert(corps_md)

# --- structure : ce qui porte une information devient une classe -----------
# Les hypotheses sont une typologie (H1..H4), pas une decoration.
corps = re.sub(r'<p><strong>(H[1-4] —)', r'<p class="hyp"><strong>\1', corps)
# Enonce, mesure et refutation arrivent en un seul paragraphe : on rend la
# structure visible sans toucher au texte.
corps = re.sub(
    r"<em>(Mesure|Réfutation)</em>\s*:",
    r'<br><em class="lab">\1</em> :',
    corps,
)
# Les trois canaux de contamination : ce sont des defauts trouves, pas des sections.
corps = re.sub(
    r"<p><strong>(Le premier|Le second|Le troisième) tenait",
    r'<p class="canal"><strong>\1 tenait',
    corps,
)
# Les deux definitions d'instrument sont des formules, pas des citations.
def _formule(m):
    interieur = m.group(1)
    # Le test porte sur le texte, pas sur le HTML : un attribut href= ferait
    # passer un simple lien pour une definition d'instrument.
    texte = re.sub(r"<.*?>", "", interieur)
    if "=" in texte and len(texte) < 260:
        return f'<div class="formule">{interieur}</div>'
    return m.group(0)

corps = re.sub(r"<blockquote>\s*<p>(.*?)</p>\s*</blockquote>", _formule, corps, flags=re.S)
corps = corps.replace("<blockquote>", '<blockquote class="note">')

# --- sommaire : h2 et h3 ---------------------------------------------------
entrees = re.findall(r'<h([23]) id="([^"]+)">(.*?)</h[23]>', corps, flags=re.S)
items = []
for niveau, ancre, titre in entrees:
    titre = re.sub(r"<.*?>", "", titre).strip()
    items.append(f'<li class="n{niveau}"><a href="#{ancre}">{html.escape(titre)}</a></li>')
sommaire = "\n".join(items)

GABARIT = """<title>Arène de Kuhn</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<style>
:root {{
  --ground:#FBFBFC; --surface:#F1F3F5; --surface-2:#E8ECEF;
  --ink:#14181F; --ink-2:#4B5560; --ink-3:#727E8A;
  --rule:#D8DDE2; --rule-fort:#B9C1C9;
  --accent:#0F4C5C; --accent-soft:#E2EDF0;
  --alerte:#A34A28; --alerte-soft:#F6EAE4;
  --serif:"Spectral", Georgia, "Times New Roman", serif;
  --sans:"IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono:"IBM Plex Mono", ui-monospace, "SF Mono", Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#0F1216; --surface:#171C22; --surface-2:#1F262E;
    --ink:#E7EBF0; --ink-2:#A9B4BF; --ink-3:#7E8994;
    --rule:#29313A; --rule-fort:#3A444F;
    --accent:#63B2C6; --accent-soft:#13272E;
    --alerte:#DB8F6C; --alerte-soft:#2B1E18;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#0F1216; --surface:#171C22; --surface-2:#1F262E;
  --ink:#E7EBF0; --ink-2:#A9B4BF; --ink-3:#7E8994;
  --rule:#29313A; --rule-fort:#3A444F;
  --accent:#63B2C6; --accent-soft:#13272E;
  --alerte:#DB8F6C; --alerte-soft:#2B1E18;
}}

* {{ box-sizing:border-box; }}
body {{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:var(--sans); font-size:17px; line-height:1.72;
  -webkit-font-smoothing:antialiased;
}}

/* ---- bandeau ---- */
.tete {{
  border-bottom:1px solid var(--rule);
  background:var(--surface);
}}
.tete-in {{
  max-width:1180px; margin:0 auto; padding:3.4rem 2rem 2.6rem;
  display:flex; flex-direction:column; gap:.9rem;
}}
.eyebrow {{
  font-family:var(--mono); font-size:.72rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--accent);
}}
.tete h1 {{
  font-family:var(--serif); font-weight:700; font-size:clamp(2.1rem,4.4vw,3.1rem);
  line-height:1.12; margin:0; text-wrap:balance; letter-spacing:-.015em;
}}
.chapo {{
  font-family:var(--serif); font-size:1.16rem; line-height:1.6;
  color:var(--ink-2); max-width:60ch; margin:0;
}}
.meta {{
  display:flex; flex-wrap:wrap; gap:.5rem 1.4rem; margin-top:.5rem;
  font-family:var(--mono); font-size:.76rem; color:var(--ink-3);
}}
.meta a {{ color:var(--accent); }}

/* ---- mise en page ---- */
.page {{
  max-width:1180px; margin:0 auto; padding:0 2rem 6rem;
  display:grid; grid-template-columns:1fr; gap:3rem;
}}
@media (min-width:1080px) {{
  .page {{ grid-template-columns:15rem 1fr; gap:4rem; }}
  .sommaire {{
    position:sticky; top:0; align-self:start;
    max-height:100vh; overflow-y:auto; padding:2.8rem 0 2rem;
  }}
}}
.sommaire h2 {{
  font-family:var(--mono); font-size:.7rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--ink-3);
  margin:0 0 .9rem; font-weight:500;
}}
.sommaire ul {{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:.1rem; }}
.sommaire a {{
  display:block; padding:.24rem 0 .24rem .75rem;
  border-left:2px solid var(--rule);
  color:var(--ink-2); text-decoration:none; font-size:.83rem; line-height:1.4;
}}
.sommaire a:hover {{ color:var(--accent); border-left-color:var(--accent); }}
.sommaire .n3 a {{ padding-left:1.6rem; font-size:.79rem; color:var(--ink-3); }}

.corps {{ padding-top:2.8rem; max-width:70ch; }}

/* ---- typographie ---- */
.corps h2 {{
  font-family:var(--serif); font-weight:600; font-size:1.85rem; line-height:1.2;
  margin:3.6rem 0 1.1rem; padding-top:1.6rem; border-top:1px solid var(--rule);
  text-wrap:balance; letter-spacing:-.01em;
}}
.corps h2:first-child {{ margin-top:0; border-top:0; padding-top:0; }}
.corps h3 {{
  font-family:var(--serif); font-weight:600; font-size:1.3rem;
  margin:2.6rem 0 .7rem; text-wrap:balance;
}}
.corps h4 {{
  font-family:var(--sans); font-weight:600; font-size:1rem;
  margin:2rem 0 .5rem; color:var(--accent);
}}
.corps p {{ margin:0 0 1.15rem; }}
.corps strong {{ font-weight:600; }}
.corps a {{ color:var(--accent); text-underline-offset:2px; }}
.corps ul, .corps ol {{ margin:0 0 1.3rem; padding-left:1.3rem; }}
.corps li {{ margin-bottom:.45rem; }}
.corps hr {{ border:0; border-top:1px solid var(--rule); margin:3rem 0; }}
code {{
  font-family:var(--mono); font-size:.86em;
  background:var(--surface-2); padding:.1em .35em; border-radius:2px;
}}

/* ---- hypotheses : une typologie, pas un ornement ---- */
.hyp {{
  font-size:1.06rem; margin:2.2rem 0 .5rem; padding-left:.9rem;
  border-left:3px solid var(--accent);
}}
.hyp em.lab {{
  font-family:var(--mono); font-style:normal; font-size:.72rem;
  letter-spacing:.09em; text-transform:uppercase; color:var(--ink-3);
}}
.hyp br {{ line-height:2.4; }}

/* ---- canaux de contamination : des defauts trouves ---- */
.canal {{
  background:var(--alerte-soft); border-left:3px solid var(--alerte);
  padding:1rem 1.2rem; margin:1.4rem 0;
}}
.canal strong:first-child {{ color:var(--alerte); }}

/* ---- notes de protocole ---- */
blockquote.note {{
  margin:1.8rem 0; padding:1.1rem 1.3rem;
  background:var(--surface); border-left:3px solid var(--rule-fort);
}}
blockquote.note p:last-child {{ margin-bottom:0; }}

/* ---- formules : les deux instruments ---- */
.formule {{
  font-family:var(--serif); font-size:1.12rem; text-align:center;
  background:var(--accent-soft); color:var(--ink);
  padding:1.2rem 1rem; margin:1.8rem 0; border-top:1px solid var(--accent);
  border-bottom:1px solid var(--accent);
}}
.formule strong {{ font-weight:600; }}

/* ---- tableaux : des donnees, donc des chiffres alignes ---- */
.tableau {{ overflow-x:auto; margin:1.6rem 0; }}
table {{
  border-collapse:collapse; width:100%; font-size:.88rem;
  font-variant-numeric:tabular-nums;
}}
th {{
  font-family:var(--mono); font-size:.72rem; font-weight:500;
  letter-spacing:.08em; text-transform:uppercase; color:var(--ink-3);
  text-align:left; padding:.6rem .8rem; border-bottom:1px solid var(--rule-fort);
  white-space:nowrap;
}}
td {{
  padding:.62rem .8rem; border-bottom:1px solid var(--rule);
  vertical-align:top; line-height:1.55;
}}
tr:last-child td {{ border-bottom:0; }}
td code {{ background:none; padding:0; color:var(--accent); }}

.pied {{
  max-width:1180px; margin:0 auto; padding:2rem 2rem 4rem;
  font-family:var(--mono); font-size:.74rem; color:var(--ink-3);
  border-top:1px solid var(--rule);
}}
:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
@media (prefers-reduced-motion:reduce) {{ * {{ animation:none !important; transition:none !important; }} }}
</style>

<header class="tete">
  <div class="tete-in">
    <div class="eyebrow">Mémoire de M2 · IREN · 2025-2026 · Chapitre 2</div>
    <h1>Méthodologie</h1>
    <p class="chapo">Mesurer si la mémoire persistante d'un agent LLM produit une adaptation
    stratégique — et si cette adaptation exploite l'adversaire ou récite l'équilibre.
    Le protocole décrit ici est celui qui a tourné : 24 exécutions, 26 550 manches.</p>
    <div class="meta">
      <span>Version définitive · août 2026</span>
      <span>Protocole exécuté du 22 au 24 août 2026</span>
      <span><a href="https://github.com/videtleo-ux/Memoire-IREN">github.com/videtleo-ux/Memoire-IREN</a></span>
    </div>
  </div>
</header>

<div class="page">
  <nav class="sommaire">
    <h2>Sommaire</h2>
    <ul>
{sommaire}
    </ul>
  </nav>
  <main class="corps">
    <blockquote class="note"><p>{note}</p></blockquote>
{corps}
  </main>
</div>

<footer class="pied">
  Chapitre de méthode — dispositif, journaux et suite de tests publics.
</footer>
"""

page = GABARIT.format(
    sommaire=sommaire,
    corps=corps,
    note=markdown.markdown(note_structure).replace("<p>", "").replace("</p>", ""),
)
# Les tableaux doivent pouvoir defiler sans emporter la page.
page = page.replace("<table>", '<div class="tableau"><table>').replace(
    "</table>", "</table></div>"
)
CIBLE.write_text(page, encoding="utf-8")
print("ecrit :", CIBLE, len(page), "octets")
print("entrees de sommaire :", len(items))
