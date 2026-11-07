// node render.mjs  (needs: npm i playwright, Chrome installed). Renders each HTML to ./out/*.png
import { chromium } from 'playwright';
import { mkdirSync } from 'fs';
import { resolve } from 'path';
import { pathToFileURL } from 'url';
mkdirSync('out', { recursive: true });
const sizes = { announce: [1080, 1350], teaser: [1920, 1080], social: [1080, 1080] };
const b = await chromium.launch({ channel: 'chrome' });
for (const [n, [w, h]] of Object.entries(sizes)) {
  const p = await b.newPage({ viewport: { width: w, height: h } });
  await p.goto(pathToFileURL(resolve(n + '.html')).href);
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300);
  await p.screenshot({ path: `out/piblo-${n}.png` });
  console.log(n);
}
await b.close();
