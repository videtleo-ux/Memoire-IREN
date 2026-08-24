# Construit la page de resultats a partir de donnees.json.
import json
from pathlib import Path

S = Path(__file__).parent
donnees = json.loads((S / "donnees.json").read_text(encoding="utf-8"))
CIBLE = S / "resultats.html"

PAGE = """<title>Courbes d'adaptation</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:wght@600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root {
  --ground:#FBFBFC; --surface:#F4F6F7; --surface-2:#E8ECEF;
  --ink:#14181F; --ink-2:#4B5560; --ink-3:#727E8A;
  --rule:#D8DDE2; --grid:#E4E8EB; --axe:#C2C9D0;
  --ae:#2a78d6; --sm:#eb6834; --icl:#1baf7a;  /* palette categorielle validee */
  --serif:"Spectral", Georgia, serif;
  --sans:"IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono:"IBM Plex Mono", ui-monospace, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --ground:#0F1216; --surface:#171C22; --surface-2:#1F262E;
    --ink:#E7EBF0; --ink-2:#A9B4BF; --ink-3:#7E8994;
    --rule:#29313A; --grid:#232A32; --axe:#39424C;
    --ae:#3987e5; --sm:#d95926; --icl:#199e70;
  }
}
:root[data-theme="dark"] {
  --ground:#0F1216; --surface:#171C22; --surface-2:#1F262E;
  --ink:#E7EBF0; --ink-2:#A9B4BF; --ink-3:#7E8994;
  --rule:#29313A; --grid:#232A32; --axe:#39424C;
  --ae:#3987e5; --sm:#d95926; --icl:#199e70;
}
* { box-sizing:border-box; }
body { margin:0; background:var(--ground); color:var(--ink);
  font-family:var(--sans); font-size:16px; line-height:1.68; }
.wrap { max-width:1000px; margin:0 auto; padding:0 1.6rem 5rem; }

header.tete { border-bottom:1px solid var(--rule); background:var(--surface); }
.tete .wrap { padding-top:3.2rem; padding-bottom:2.4rem; }
.eyebrow { font-family:var(--mono); font-size:.72rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--ink-3); margin-bottom:.7rem; }
h1 { font-family:var(--serif); font-weight:700; font-size:clamp(2rem,4.2vw,2.9rem);
  line-height:1.13; margin:0 0 .7rem; letter-spacing:-.015em; text-wrap:balance; }
.chapo { font-size:1.1rem; color:var(--ink-2); max-width:62ch; margin:0; }
.meta { display:flex; flex-wrap:wrap; gap:.4rem 1.5rem; margin-top:1.2rem;
  font-family:var(--mono); font-size:.75rem; color:var(--ink-3); }

h2 { font-family:var(--serif); font-weight:600; font-size:1.6rem;
  margin:3.4rem 0 .4rem; padding-top:1.5rem; border-top:1px solid var(--rule); }
h2 + .sous { color:var(--ink-2); margin:0 0 1.6rem; max-width:64ch; }
h3 { font-family:var(--sans); font-weight:600; font-size:1rem; margin:2rem 0 .5rem; }
p { margin:0 0 1.05rem; max-width:68ch; }

/* stat tiles */
.tiles { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
  gap:1px; background:var(--rule); border:1px solid var(--rule); margin:2rem 0 0; }
.tile { background:var(--ground); padding:1.2rem 1.3rem; }
.tile .lab { font-size:.8rem; color:var(--ink-2); margin-bottom:.35rem; }
.tile .val { font-family:var(--sans); font-weight:600; font-size:2.1rem;
  line-height:1.1; letter-spacing:-.02em; }
.tile .sub { font-family:var(--mono); font-size:.73rem; color:var(--ink-3); margin-top:.3rem; }

/* legende */
.legende { display:flex; gap:1.4rem; align-items:center; flex-wrap:wrap;
  margin:1.6rem 0 .4rem; font-size:.85rem; color:var(--ink-2); }
.cle { display:inline-flex; align-items:center; gap:.45rem; }
.cle i { width:18px; height:2px; border-radius:1px; display:inline-block; }
.cle.ref i { height:0; border-top:1.5px dashed var(--axe); width:18px; }

/* figure */
.grille { display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr));
  gap:1.6rem; margin:.6rem 0 0; }
.panneau { border:1px solid var(--rule); background:var(--ground); padding:.9rem .8rem .5rem; position:relative; }
.panneau h4 { margin:0 0 .1rem; font-size:.95rem; font-weight:600; }
.panneau .note { font-family:var(--mono); font-size:.7rem; color:var(--ink-3); margin:0 0 .3rem; }
svg { display:block; width:100%; height:auto; overflow:visible; }
.axe-txt { font-family:var(--mono); font-size:9px; fill:var(--ink-3); }
.fin-lab { font-family:var(--mono); font-size:10px; font-weight:500; fill:var(--ink-2); }

.infobulle { position:absolute; pointer-events:none; opacity:0; transition:opacity .12s;
  background:var(--ink); color:var(--ground); font-family:var(--mono); font-size:.72rem;
  padding:.45rem .6rem; border-radius:3px; white-space:nowrap; z-index:5; line-height:1.5; }
@media (prefers-reduced-motion:reduce){ .infobulle{ transition:none; } }

/* tableaux */
.tableau { overflow-x:auto; margin:1.4rem 0; }
table { border-collapse:collapse; width:100%; font-size:.87rem;
  font-variant-numeric:tabular-nums; }
th { font-family:var(--mono); font-size:.7rem; font-weight:500; letter-spacing:.07em;
  text-transform:uppercase; color:var(--ink-3); text-align:left;
  padding:.55rem .7rem; border-bottom:1px solid var(--axe); white-space:nowrap; }
td { padding:.55rem .7rem; border-bottom:1px solid var(--rule); }
td.num { text-align:right; font-family:var(--mono); }
tr:last-child td { border-bottom:0; }
.pastille { display:inline-block; width:9px; height:9px; border-radius:50%;
  margin-right:.45rem; vertical-align:baseline; }

details { border:1px solid var(--rule); padding:.9rem 1.1rem; margin:1.6rem 0; background:var(--surface); }
summary { cursor:pointer; font-weight:500; font-size:.9rem; }
details[open] summary { margin-bottom:.8rem; }

blockquote { margin:1.2rem 0; padding:1rem 1.2rem; background:var(--surface);
  border-left:3px solid var(--axe); font-size:.93rem; }
blockquote p:last-child { margin-bottom:0; }
blockquote cite { display:block; margin-top:.5rem; font-family:var(--mono);
  font-size:.72rem; font-style:normal; color:var(--ink-3); }
code { font-family:var(--mono); font-size:.87em; background:var(--surface-2);
  padding:.08em .32em; border-radius:2px; }
.pied { border-top:1px solid var(--rule); margin-top:3.5rem; padding-top:1.4rem;
  font-family:var(--mono); font-size:.73rem; color:var(--ink-3); }
:focus-visible { outline:2px solid var(--ae); outline-offset:2px; }
</style>

<header class="tete"><div class="wrap">
  <div class="eyebrow">Mémoire M2 · IREN · campagne des 22-24 août 2026</div>
  <h1>Courbes d'adaptation</h1>
  <p class="chapo">Ce que la mémoire persistante change au jeu d'un agent LLM,
  mesuré sur 26 550 manches à donnes appariées. Sans mémoire, l'écart ne bouge pas.
  Avec, il tombe à l'optimum théorique — et la façon dont la mémoire est tenue
  décide de la vitesse à laquelle il y arrive.</p>
  <div class="meta">
    <span>24 exécutions · 177 séries · 26 550 manches</span>
    <span>gpt-5.6-luna · K = 150</span>
    <span>intégrité 24/24 · rejeu 24/24</span>
    <span>47,27 $</span>
  </div>
</div></header>

<div class="wrap">

  <div class="tiles" id="tiles"></div>

  <h2>H1 — l'adaptation vient de la mémoire</h2>
  <p class="sous">Écart d'exploitation par série : ce que l'agent laisse sur la table
  à chaque manche, faute d'exploiter parfaitement son adversaire. Zéro = exploitation
  optimale. Les trois panneaux partagent la même échelle — l'écart de marge entre
  adversaires est lui-même un résultat.</p>

  <div class="legende">
    <span class="cle"><i style="background:var(--ae)"></i> AE — mémoire auto-écrite (10 séries)</span>
    <span class="cle"><i style="background:var(--icl)"></i> ICL — historique brut (10 séries)</span>
    <span class="cle"><i style="background:var(--sm)"></i> SM — sans mémoire (3 séries)</span>
    <span class="cle ref"><i></i> écart d'un récitant d'équilibre</span>
    <span style="color:var(--ink-3)">trait épais : moyenne des 3 réplications · traits fins : réplications</span>
  </div>

  <div class="grille" id="figures"></div>

  <p style="margin-top:1.6rem">Les neuf paires vont dans le même sens, avec une
  dispersion inter-réplications de l'ordre du centième. La ligne sans mémoire ne
  décroît jamais : elle mesure ce que le modèle produit de sa seule mémorisation,
  sans expérience de cet adversaire — et ce niveau est <em>au-dessus</em> de l'écart
  d'un récitant contre Station comme contre GTO.</p>

  <h2>H2 — l'adaptation exploite, elle ne récite pas</h2>
  <p class="sous">La référence récitée mesure la distance au comportement d'un agent
  qui appliquerait l'équilibre. Un récitant y reste à zéro quel que soit l'adversaire ;
  un exploiteur s'en écarte positivement, et son maximum théorique est connu d'avance.</p>

  <div class="tableau"><table>
    <thead><tr><th>Adversaire</th><th>SM</th><th>AE (séries 7-9)</th><th>Maximum théorique</th><th>Atteint</th></tr></thead>
    <tbody id="h2"></tbody>
  </table></div>

  <p>Contre les deux adversaires exploitables, l'agent à mémoire atteint
  <strong>exactement la valeur maximale de l'exploitation</strong> — 7/9 contre
  Over-folder, 1/9 contre Station. Il ne récite pas l'équilibre : il s'en écarte dans
  la direction que chaque adversaire commande, et jusqu'à l'optimum. Sans mémoire, il
  est <em>en dessous</em> de l'équilibre contre Station et contre GTO.</p>

  <p><strong>Le contrôle négatif tient.</strong> Contre GTO, la référence récitée reste
  négative sur toutes les séries : l'agent ne gagne jamais plus que l'équilibre face à
  un adversaire à l'équilibre. La baisse de l'écart qu'on y observe malgré tout n'est
  pas un artefact — elle est absente en condition sans mémoire, sur les mêmes donnes et
  le même calcul. Contre GTO il n'y a rien à exploiter : la mémoire n'y sert qu'à cesser
  de se tromper, et l'écart baisse sans jamais se stabiliser à zéro.</p>

  <h2>H3 — le mécanisme de rétention compte, mais pas partout</h2>
  <p class="sous">ICL reçoit exactement la même matière qu'AE — le récapitulatif brut
  des séries passées — mais sans étape de synthèse : l'expérimentateur empile, la
  fenêtre évince par séries entières, aucun appel au modèle n'a lieu à la frontière.
  Seul le mécanisme de rétention diffère.</p>

  <div class="tableau"><table>
    <thead><tr><th>Adversaire</th><th>ICL</th><th>AE</th><th>Effet ICL − AE</th><th>IC 95 %</th><th>Conclusion</th></tr></thead>
    <tbody id="h3"></tbody>
  </table></div>

  <p>Le mécanisme de rétention ne départage les deux mémoires que là où la tâche
  exige une politique <strong>différenciée selon la carte</strong>. Contre
  Over-folder, la stratégie optimale tient en une règle unique — engager quel que
  soit le sceau — et un historique brut la maintient aussi bien qu'une note
  synthétisée. Contre Station, où il faut cesser de bluffer <em>et</em> miser pour la
  valeur au seul sceau supérieur, la synthèse fait la différence.</p>

  <p><strong>Le mécanisme observé n'est pas celui qui était anticipé.</strong> Le
  protocole prévoyait pour ICL un profil d'oubli en dents de scie, produit par
  l'éviction des séries anciennes à la saturation de la fenêtre. Rien de tel
  n'apparaît. ICL <em>rampe</em> : une descente lente, bruitée, étalée sur dix séries,
  qui ne verrouille jamais zéro — là où AE fait une marche unique et immédiate dès la
  première réflexion, et n'en bouge plus. La différence porte sur la vitesse et la
  complétude de l'adaptation, non sur sa rétention.</p>

  <h2>Ce que l'agent s'écrit</h2>
  <p class="sous">Les notes tiennent en une seule entrée, jamais saturée. Elles nomment
  la régularité adverse, en déduisent la politique, et l'appliquent.</p>

  <blockquote><p>« Il n'a jamais engagé ni couvert. Ouvrant, il a toujours retenu ;
  Répondant, il s'est toujours retiré face à notre engagement. Nos 150 engagements ont
  donc tous rapporté +1, sans coût ni révélation des sceaux. »</p>
  <cite>AE-over-folder-r2, frontière de la série 9 — écart 0,000</cite></blockquote>

  <p>Deux imperfections méritent d'être relevées, et alimentent directement H4. Un run
  sur trois contre Over-folder <strong>inverse les rôles</strong> dans sa description
  (« il a toujours engagé » alors que le bot n'a jamais misé : 795 <code>check</code>,
  1 400 <code>fold</code>, zéro <code>bet</code> dans les journaux) tout en jouant la
  stratégie optimale — le comportement est juste, son explication est fausse. Et l'agent
  traite systématiquement sa note antérieure comme une erreur à corriger
  (« remplace l'ancien −13 ») plutôt que comme le résultat d'une série passée : il écrase
  au lieu d'accumuler.</p>

  <h2>Contrôles de validité</h2>
  <div class="tableau"><table>
    <thead><tr><th>Contrôle</th><th>Résultat</th></tr></thead>
    <tbody>
      <tr><td>Rejeu de complétude (chaque manche re-réglée depuis les seuls journaux)</td><td>18 / 18</td></tr>
      <tr><td>Intégrité de clôture (donnes, positions, appariement, isolation)</td><td>18 / 18</td></tr>
      <tr><td>Actions imposées par défaut · relances de format · erreurs de harnais</td><td>0 · 0 · 0</td></tr>
      <tr><td>Ruptures du gel intra-série (sur 117 séries)</td><td>0</td></tr>
      <tr><td>Équilibre des positions Ouvrant / Répondant</td><td>8 775 / 8 775</td></tr>
      <tr><td>Reconnaissance du jeu source (covariable, sur 17 550 sorties)</td><td>96 signalements</td></tr>
    </tbody>
  </table></div>

  <details>
    <summary>Toutes les valeurs — écart d'exploitation par série</summary>
    <div class="tableau"><table id="donnees-table">
      <thead><tr><th>Adversaire</th><th>Condition</th><th>Répl.</th><th>Série</th><th class="num">Écart</th></tr></thead>
      <tbody></tbody>
    </table></div>
  </details>

  <div class="pied">
    Données : C:\\arene-runs\\csv\\sessions.csv · notes intégrales : notes-ae.md ·
    journaux bruts : un dossier par exécution.<br>
    Reste à jouer : la condition ICL, qui porte H3.
  </div>
</div>

<script>
const D = __DONNEES__;
const NOMS = {"Over-folder":"Over-folder","Station":"Station","GTO":"GTO (contrôle négatif)"};
const YMAX = 0.85, W = 340, H = 250;
const M = {l:38, r:46, t:10, b:30};   // r laisse la place aux etiquettes de fin
const px = s => M.l + s*(W-M.l-M.r)/9;
const py = v => M.t + (1 - v/YMAX)*(H-M.t-M.b);

// --- stat tiles ---
document.getElementById('tiles').innerHTML = D.synthese.map(s => `
  <div class="tile">
    <div class="lab">${NOMS[s.bot].replace(' (contrôle négatif)','')}</div>
    <div class="val">${s.reduction.toFixed(3).replace('.',',')}</div>
    <div class="sub">jeton/manche récupéré · ${s.sm.toFixed(3).replace('.',',')} → ${s.ae.toFixed(3).replace('.',',')}</div>
  </div>`).join('');

// --- H2 ---
document.getElementById('h2').innerHTML = D.synthese.map(s => `
  <tr><td>${NOMS[s.bot]}</td>
    <td class="num">${s.ref_sm >= 0 ? '+' : '−'}${Math.abs(s.ref_sm).toFixed(3).replace('.',',')}</td>
    <td class="num"><strong>${s.ref_ae >= 0 ? '+' : '−'}${Math.abs(s.ref_ae).toFixed(3).replace('.',',')}</strong></td>
    <td class="num">${s.ref_max > 0 ? '+' + s.ref_max.toFixed(3).replace('.',',') : '0 (plafond)'}</td>
    <td>${s.ref_max > 0 ? Math.round(100*s.ref_ae/s.ref_max) + ' %' : 'jamais dépassé'}</td></tr>`).join('');

// --- H3 ---
document.getElementById('h3').innerHTML = D.synthese.filter(s => s.h3 !== null).map(s => {
  const net = Math.abs(s.h3) > s.h3_ic;
  const f = v => (v>=0?'+':'−') + Math.abs(v).toFixed(4).replace('.',',');
  return `<tr><td>${NOMS[s.bot]}</td>
    <td class="num">${s.h3_icl.toFixed(4).replace('.',',')}</td>
    <td class="num">${s.h3_ae.toFixed(4).replace('.',',')}</td>
    <td class="num"><strong>${f(s.h3)}</strong></td>
    <td class="num">± ${s.h3_ic.toFixed(4).replace('.',',')}</td>
    <td>${net ? 'l'intervalle exclut zéro : <strong>AE l'emporte</strong>' : 'l'intervalle contient zéro : indistinguable'}</td></tr>`;
}).join('');

// --- figures ---
function chemin(points){ return points.map((p,i)=>(i?'L':'M')+px(p[0]).toFixed(1)+' '+py(p[1]).toFixed(1)).join(' '); }

document.getElementById('figures').innerHTML = D.bots.map(bot => {
  const c = D.cellules[bot];
  let g = '';
  // Une etiquette de fin n'est posee que si aucune autre serie ne se termine a
  // la meme abscisse : ICL et AE finissent tous deux en serie 9, et des
  // etiquettes empilees se detacheraient de leurs courbes (cf. marks-and-anatomy).
  // La valeur reste lisible au survol, dans les tuiles et dans la vue tableau.
  const finDe = {};
  for (const cond of ['SM','ICL','AE']) {
    const m = c[cond].moyenne;
    if (m.length > 1) finDe[cond] = m[m.length-1][0];
  }
  const isole = cond => Object.entries(finDe)
    .filter(([k,v]) => k !== cond && v === finDe[cond]).length === 0;
  // grille horizontale
  for (let v=0; v<=0.8; v+=0.2)
    g += `<line x1="${M.l}" y1="${py(v).toFixed(1)}" x2="${W-M.r}" y2="${py(v).toFixed(1)}" stroke="var(--grid)" stroke-width="1"/>`
       + `<text class="axe-txt" x="${M.l-6}" y="${(py(v)+3).toFixed(1)}" text-anchor="end">${v.toFixed(1).replace('.',',')}</text>`;
  // ligne du recitant (un seuil, pas une grille)
  if (c.recitant > 0)
    g += `<line x1="${M.l}" y1="${py(c.recitant).toFixed(1)}" x2="${W-M.r}" y2="${py(c.recitant).toFixed(1)}" stroke="var(--axe)" stroke-width="1.5" stroke-dasharray="4 3"/>`;
  // axe x
  g += `<line x1="${M.l}" y1="${py(0)}" x2="${W-M.r}" y2="${py(0)}" stroke="var(--axe)" stroke-width="1"/>`;
  for (const s of [0,3,6,9])
    g += `<text class="axe-txt" x="${px(s).toFixed(1)}" y="${H-M.b+16}" text-anchor="middle">${s}</text>`;
  // series : replications fines puis moyenne epaisse
  for (const cond of ['SM','ICL','AE']) {
    const col = cond==='AE' ? 'var(--ae)' : cond==='ICL' ? 'var(--icl)' : 'var(--sm)';
    for (const t of c[cond].traces)
      if (t.points.length>1) g += `<path d="${chemin(t.points)}" fill="none" stroke="${col}" stroke-width="1" opacity=".3" stroke-linejoin="round"/>`;
    const m = c[cond].moyenne;
    if (m.length < 2) continue;   // GTO n'a pas de condition ICL
    g += `<path d="${chemin(m)}" fill="none" stroke="${col}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>`;
    const fin = m[m.length-1];
    g += `<circle cx="${px(fin[0]).toFixed(1)}" cy="${py(fin[1]).toFixed(1)}" r="4" fill="${col}" stroke="var(--ground)" stroke-width="2"/>`;
    if (isole(cond))
      g += `<text class="fin-lab" x="${(px(fin[0])+7).toFixed(1)}" y="${(py(fin[1])+3.5).toFixed(1)}">${fin[1].toFixed(3).replace('.',',')}</text>`;
  }
  return `<div class="panneau" data-bot="${bot}">
    <h4>${NOMS[bot]}</h4>
    <p class="note">écart d'un récitant : ${c.recitant>0 ? c.recitant.toFixed(3).replace('.',',') : '0'}</p>
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Écart d'exploitation par série contre ${bot}">${g}</svg>
    <div class="infobulle"></div>
  </div>`;
}).join('');

// --- survol : valeurs de la serie la plus proche ---
document.querySelectorAll('.panneau').forEach(pan => {
  const bot = pan.dataset.bot, c = D.cellules[bot];
  const svg = pan.querySelector('svg'), bulle = pan.querySelector('.infobulle');
  const lire = (cond, s) => { const t = c[cond].moyenne.find(p=>p[0]===s); return t ? t[1] : null; };
  svg.addEventListener('pointermove', e => {
    const r = svg.getBoundingClientRect();
    const xu = (e.clientX - r.left) / r.width * W;
    let s = Math.round((xu - M.l) * 9 / (W-M.l-M.r));
    s = Math.max(0, Math.min(9, s));
    const ae = lire('AE', s), sm = lire('SM', s), icl = lire('ICL', s);
    if (ae === null && sm === null && icl === null) { bulle.style.opacity = 0; return; }
    const f = v => v===null ? '—' : v.toFixed(3).replace('.',',');
    bulle.innerHTML = `série ${s}<br>AE ${f(ae)}<br>ICL ${f(icl)}<br>SM ${f(sm)}`;
    bulle.style.opacity = 1;
    bulle.style.left = Math.min(r.width - 92, Math.max(0, (px(s)/W)*r.width + 10)) + 'px';
    bulle.style.top = '38px';
  });
  svg.addEventListener('pointerleave', () => bulle.style.opacity = 0);
});

// --- vue tableau ---
const corps = document.querySelector('#donnees-table tbody');
const rows = [];
for (const bot of D.bots) for (const cond of ['AE','ICL','SM'])
  for (const t of D.cellules[bot][cond].traces)
    for (const [s,e] of t.points)
      rows.push(`<tr><td>${bot}</td><td><span class="pastille" style="background:var(--${cond.toLowerCase()})"></span>${cond}</td><td>r${t.repl}</td><td>${s}</td><td class="num">${e.toFixed(4).replace('.',',')}</td></tr>`);
corps.innerHTML = rows.join('');
</script>
"""

CIBLE.write_text(PAGE.replace("__DONNEES__", json.dumps(donnees, ensure_ascii=False)), encoding="utf-8")
print("ecrit :", CIBLE, CIBLE.stat().st_size, "octets")
