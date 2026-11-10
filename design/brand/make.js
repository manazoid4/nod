// Generates Piblo brand SVGs: icon (512), favicon (64), logo (horizontal), logo-mono.
const fs = require('fs');
const opentype = require('opentype.js');
const font = opentype.loadSync(__dirname + '/../../site/fonts/bricolage-grotesque-bold.ttf');
const C = { paper: '#fff4e0', ink: '#2a1a12', tomato: '#ee5a36', mint: '#8fdcb8', sun: '#ffc93c' };

// Buddy device drawn in a 512 box. bg=false gives a transparent version for the logo.
// Friendly faces on a bright screen (v1's pale eyes on a dark screen read as creepy).
const FACES = {
  // A: happy closed eyes + open grin
  happy: `<rect x="150" y="124" width="212" height="172" rx="30" fill="${C.paper}" stroke="${C.ink}" stroke-width="8"/>
    <circle cx="256" cy="212" r="64" fill="${C.tomato}" stroke="${C.ink}" stroke-width="8"/>
    <path d="M222 204 Q234 188 246 204 M266 204 Q278 188 290 204" fill="none" stroke="${C.ink}" stroke-width="9" stroke-linecap="round"/>
    <path d="M230 222 Q256 258 282 222 Z" fill="${C.ink}" stroke="${C.ink}" stroke-width="6" stroke-linejoin="round"/>
    <circle cx="214" cy="228" r="9" fill="${C.sun}"/><circle cx="298" cy="228" r="9" fill="${C.sun}"/>`,
  // B: round shiny eyes + wide smile
  bright: `<rect x="150" y="124" width="212" height="172" rx="30" fill="${C.paper}" stroke="${C.ink}" stroke-width="8"/>
    <circle cx="256" cy="212" r="64" fill="${C.tomato}" stroke="${C.ink}" stroke-width="8"/>
    <circle cx="233" cy="202" r="12" fill="${C.ink}"/><circle cx="279" cy="202" r="12" fill="${C.ink}"/>
    <circle cx="237" cy="197" r="4.5" fill="${C.paper}"/><circle cx="283" cy="197" r="4.5" fill="${C.paper}"/>
    <path d="M232 228 Q256 250 280 228" fill="none" stroke="${C.ink}" stroke-width="9" stroke-linecap="round"/>
    <circle cx="212" cy="228" r="8" fill="${C.sun}"/><circle cx="300" cy="228" r="8" fill="${C.sun}"/>`,
  // C: face drawn on the screen itself, Tamagotchi style
  screen: `<rect x="150" y="124" width="212" height="172" rx="30" fill="${C.sun}" stroke="${C.ink}" stroke-width="8"/>
    <circle cx="222" cy="198" r="15" fill="${C.ink}"/><circle cx="290" cy="198" r="15" fill="${C.ink}"/>
    <circle cx="227" cy="192" r="5.5" fill="${C.paper}"/><circle cx="295" cy="192" r="5.5" fill="${C.paper}"/>
    <path d="M228 232 Q256 262 284 232" fill="none" stroke="${C.ink}" stroke-width="10" stroke-linecap="round"/>
    <ellipse cx="192" cy="232" rx="13" ry="8" fill="${C.tomato}"/><ellipse cx="320" cy="232" rx="13" ry="8" fill="${C.tomato}"/>`,
};
let FACE = 'screen';
function device(bg = true, face = FACE) {
  const bgFill = face === 'screen' ? C.tomato : C.sun;
  return `${bg ? `<rect width="512" height="512" rx="112" fill="${bgFill}"/>` : ''}
  <g transform="rotate(-8 256 262)">
    <rect x="118" y="110" width="276" height="330" rx="58" fill="${C.ink}"/>
    <rect x="118" y="92" width="276" height="330" rx="58" fill="${C.mint}" stroke="${C.ink}" stroke-width="14"/>
    ${FACES[face]}
    ${[150, 206, 262, 318].map((x, i) => `<rect x="${x}" y="326" width="44" height="36" rx="11" fill="${i === 2 ? C.tomato : C.paper}" stroke="${C.ink}" stroke-width="6"/>`).join('\n    ')}
    <rect x="178" y="374" width="156" height="22" rx="11" fill="${C.paper}" stroke="${C.ink}" stroke-width="6"/>
  </g>`;
}

// Wordmark "piblo" as paths, with the i's dot replaced by a tomato talk dot.
function wordmark(size, x, baseline, color) {
  const glyphs = font.stringToGlyphs('piblo');
  let pen = x, out = '', dot = null;
  const scale = size / font.unitsPerEm;
  glyphs.forEach((g, i) => {
    if (i === 1) {
      // dotless i: draw only the stem part of the glyph (below x-height).
      const p = g.getPath(pen, baseline, size);
      const xh = (font.tables.os2.sxHeight || 520) * scale;
      const bb = g.getBoundingBox();
      p.commands = p.commands; // keep, then mask the dot with a clip below
      out += `<g clip-path="url(#stem)">${p.toSVG(2).replace('<path', `<path fill="${color}"`)}</g>`;
      dot = { cx: pen + ((bb.x1 + bb.x2) / 2) * scale, cy: baseline - xh - size * 0.17, r: size * 0.105, xh, stemX: pen };
    } else {
      out += g.getPath(pen, baseline, size).toSVG(2).replace('<path', `<path fill="${color}"`);
    }
    pen += g.advanceWidth * scale + (i < glyphs.length - 1 ? font.getKerningValue(g, glyphs[i + 1]) * scale : 0) - size * 0.01;
  });
  const clip = `<clipPath id="stem"><rect x="${dot.stemX - 50}" y="${baseline - dot.xh - size * 0.04}" width="${size}" height="${size}"/></clipPath>`;
  return { svg: out + `<circle cx="${dot.cx.toFixed(1)}" cy="${dot.cy.toFixed(1)}" r="${dot.r.toFixed(1)}" fill="${C.tomato}"/>`, clip, width: pen - x };
}

const out = (name, s) => fs.writeFileSync(__dirname + '/' + name, s.replace(/\n\s*\n/g, '\n'));

out('piblo-icon.svg', `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><title>Piblo</title>${device(true)}</svg>`);

out('piblo-favicon.svg', `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect x="3" y="3" width="58" height="58" rx="16" fill="${C.sun}" stroke="${C.ink}" stroke-width="5"/><circle cx="22" cy="27" r="5.5" fill="${C.ink}"/><circle cx="42" cy="27" r="5.5" fill="${C.ink}"/><circle cx="24" cy="25" r="2" fill="${C.paper}"/><circle cx="44" cy="25" r="2" fill="${C.paper}"/><path d="M23 38 Q32 47 41 38" fill="none" stroke="${C.ink}" stroke-width="4.5" stroke-linecap="round"/><ellipse cx="13" cy="38" rx="4.5" ry="3" fill="${C.tomato}"/><ellipse cx="51" cy="38" rx="4.5" ry="3" fill="${C.tomato}"/></svg>`);

for (const [name, color] of [['piblo-logo.svg', C.ink], ['piblo-logo-light.svg', C.paper]]) {
  const w = wordmark(300, 400, 290, color);
  const W = Math.ceil(400 + w.width + 30);
  out(name, `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} 380"><title>Piblo</title><defs>${w.clip}</defs><g transform="translate(-40 -50) scale(0.88)">${device(false)}</g>${w.svg}</svg>`);
}
console.log('ok');
for (const f of Object.keys(FACES)) out(`v-${f}.svg`, `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">${device(true, f)}</svg>`);
