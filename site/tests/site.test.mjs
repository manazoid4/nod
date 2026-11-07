import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";
import vm from "node:vm";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const pages = ["/", "/roadmap/", "/readiness/", "/privacy/"];
const contents = Object.fromEntries(pages.map(path => [path, readFileSync(join(root, path, "index.html"), "utf8")]));
const attrs = (html, name) => [...html.matchAll(new RegExp(name + '="([^"]+)"', "g"))].map(match => match[1]);
const ids = html => new Set(attrs(html, "id"));
const locallyResolve = pathname => pathname.endsWith("/") ? join(root, pathname, "index.html") : join(root, pathname);

test("all four pages have navigation, semantic structure and an indexed identity", () => {
  for (const [path, html] of Object.entries(contents)) {
    assert.match(html, /<html lang="en-GB">/);
    assert.equal((html.match(/<main id="main">/g) || []).length, 1, path);
    assert.equal((html.match(/<h1\b/g) || []).length, 1, path);
    assert.match(html, /<meta name="description"/, path);
    assert.match(html, /<link rel="canonical"/, path);
    assert.match(html, /<details class="mobile-menu">/, path);
    assert.match(html, /<nav class="mobile-menu-links" aria-label="Mobile navigation">/, path);
    assert.match(html, /<a class="skip-link" href="#main">/, path);
  }
});

test("all internal paths, static assets and hash targets resolve locally", () => {
  for (const [page, html] of Object.entries(contents)) {
    for (const url of [...attrs(html, "href"), ...attrs(html, "src")]) {
      if (/^(https?:|mailto:|tel:|data:)/.test(url)) continue;
      const [location, fragment] = url.split("#", 2);
      const route = location.startsWith("/") ? location : location ? (page + location) : page;
      if (location) assert.ok(existsSync(locallyResolve(route)), page + " missing " + route);
      if (fragment) {
        const linked = contents[route];
        if (linked) assert.ok(ids(linked).has(fragment), page + " missing #" + fragment + " on " + route);
      }
    }
  }
});

test("all external new-tab links protect the opener", () => {
  for (const html of Object.values(contents)) {
    for (const tag of html.match(/<a\s+[^>]*target="_blank"[^>]*>/g) || []) {
      assert.match(tag, /rel="[^"]*noopener[^"]*noreferrer[^"]*"/);
    }
  }
});

test("21 unique published roadmap packages, four stages, no misleading shipped claims", () => {
  const html = contents["/roadmap/"];
  const numbers = [...html.matchAll(/class="work-id">(\d+)<\/span>/g)].map(x => Number(x[1]));
  assert.equal(numbers.length, 21);
  assert.deepEqual(numbers.sort((a,b) => a-b), Array.from({length:21}, (_,i) => i+1));
  assert.equal((html.match(/class="road-phase"/g) || []).length, 4);
  for (const key of ["foundation", "experience", "new", "launch"]) assert.ok(html.includes('data-phase-section="' + key + '"'));
  assert.match(html, /PROPOSED, NOT WORKING/);
  assert.match(html, /Reel-to-model detective/);
  assert.match(html, /Saved-video importer/);
  assert.doesNotMatch(html, /NOT CLAIMED AS SHIPPED/);
});

test("homepage refuses fake device statuses and is honest about signup", () => {
  const html = contents["/"];
  assert.match(html, /screen-concept">CONCEPT/);
    assert.doesNotMatch(html, /screen-concept">.*READY/);
    assert.match(html, /automated signup|pre-addressed email/);
    assert.match(html, /mailto:info@mazworks.uk/);
    assert.match(html, /not yet implemented/i);
    assert.match(html, /human|person|You check the printer/i);
    assert.match(html, /href="\/roadmap\/"/);
});

test("all authored JS passes parse validation and no inline event handlers ship", () => {
  for (const filename of ["script.js", "roadmap/roadmap.js"]) execFileSync(process.execPath, ["--check", join(root, filename)]);
  for (const html of Object.values(contents)) assert.doesNotMatch(html, /\son[a-z]+\s*=/i);
});

test("roadmap interactive filters select correct count and reset cleanly", () => {
  const filters = ["all", "foundation", "experience", "new", "launch"];
  const weights = [0,5,8,6,2];
  const buttons = filters.map(stage => ({dataset:{filter:stage},attributes:{},setAttribute(k,v){this.attributes[k]=v;},addEventListener(k,fn){this[k]=fn;}}));
  const sections = filters.slice(1).map((stage,i) => ({dataset:{phaseSection:stage},hidden:false,querySelectorAll(){return Array(weights[i+1]).fill({});}}));
  const count = {textContent:""};
  const document = {querySelectorAll(q){return q==="[data-filter]" ? buttons : sections;},getElementById(){return count;}};
  vm.runInNewContext(readFileSync(join(root,"roadmap/roadmap.js"),"utf8"), {document});
  assert.equal(count.textContent, "21");
  buttons[3].click();assert.equal(count.textContent,"6");assert.equal(buttons[3].attributes["aria-pressed"],"true");
  assert.equal(sections.filter(x=>!x.hidden).length,1);
  buttons[0].click();assert.equal(count.textContent,"21");assert.ok(sections.every(x=>!x.hidden));
});

test("Vercel defensive headers and sitemap exclude private-readiness indexing", () => {
  const config = JSON.parse(readFileSync(join(root, "vercel.json"), "utf8"));
  const headers = Object.fromEntries(config.headers[0].headers.map(x => [x.key, x.value]));
  for (const key of ["Content-Security-Policy","Referrer-Policy","X-Frame-Options","X-Content-Type-Options","Permissions-Policy"]) assert.ok(headers[key]);
  assert.match(headers["Content-Security-Policy"], /script-src 'self'/);
  assert.match(headers["Content-Security-Policy"], /frame-ancestors 'none'/);
  assert.doesNotMatch(headers["Content-Security-Policy"], /unsafe-inline|unsafe-eval/);
  const sitemap=readFileSync(join(root,"sitemap.xml"),"utf8");
  assert.match(sitemap, /\/roadmap\//);assert.doesNotMatch(sitemap, /\/readiness\//);
  assert.match(contents["/readiness/"], /noindex,follow/);
});
test("live site (concept A) and concept B: labelled concept, CSP-safe, honest waitlist, tokens in sync, AA contrast", () => {
  const lum = h => { const c = [1,3,5].map(i => parseInt(h.slice(i,i+2),16)/255).map(v => v <= .03928 ? v/12.92 : ((v+.055)/1.055)**2.4); return .2126*c[0]+.7152*c[1]+.0722*c[2]; };
  const ratio = (a,b) => { const [x,y] = [lum(a),lum(b)]; return (Math.max(x,y)+.05)/(Math.min(x,y)+.05); };
  const pairs = { a: [["#2a1a12","#fff4e0"],["#5b4336","#fbe3bd"],["#2a1a12","#ee5a36"],["#b3301a","#fff4e0"],["#0d6e4f","#fff4e0"],["#2a1a12","#ffc93c"]],
                  b: [["#202328","#ece9e1"],["#4a4e57","#dcd8cc"],["#202328","#f2b705"],["#0b6666","#ece9e1"],["#2fd3c0","#202328"],["#f2b705","#202328"]] };
  for (const [dir, k] of [["", "a"], ["concepts/b", "b"]]) {
    const html = readFileSync(join(root, dir, "index.html"), "utf8");
    assert.match(html, /CONCEPT/);
        assert.match(html, /mailto:info@mazworks.uk/);
        assert.match(html, /We are working on an automated signup|not an automatic mailing list yet|pre-addressed email/);
    assert.doesNotMatch(html, /\son[a-z]+\s*=|style=|<style|<script(?![^>]*(?:\ssrc=|\s+type="application\/ld\+json"))/i);
    assert.equal(readFileSync(join(root, dir, "tokens.css"), "utf8"), readFileSync(join(root, "..", "design", "tokens-" + k + ".css"), "utf8"));
    assert.match(readFileSync(join(root, dir, "styles.css"), "utf8"), /prefers-reduced-motion/);
    for (const [fg,bg] of pairs[k]) assert.ok(ratio(fg,bg) >= 4.5, k + " " + fg + " on " + bg);
  }
});
test("films: muted, labelled as concepts, lazy, and small enough for mobile", async () => {
  const { statSync } = await import("node:fs");
  const html = contents["/"];
  const videos = html.match(/<video\b[^>]*>/g) || [];
  assert.ok(videos.length >= 3);
  for (const tag of videos) {
    assert.match(tag, /\smuted\b/, "no video may play with sound by default");
    assert.match(tag, /\splaysinline\b/);
    assert.match(tag, /poster="\/media\/[^"]+\.jpg"/);
    assert.match(tag, /preload="(none|metadata)"/);
    assert.doesNotMatch(tag, /\sautoplay\b/, "autoplay is handled in script.js so reduced-motion is respected");
  }
  assert.match(html, /screen-concept">CONCEPT<\/span> film/);
  assert.match(html, /Not printed or fit-tested yet/);
  assert.match(html, /screen is simulated/);
  assert.match(html, /isn't made in Britain/);
  for (const src of html.match(/\/media\/[\w.-]+\.(mp4|webp|jpg)/g)) assert.ok(statSync(join(root, src)).size < 3_000_000, src + " is over 3 MB");
});
