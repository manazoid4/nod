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

test("homepage refuses fake device statuses and nonfunctional signup claims", () => {
  const html = contents["/"];
  assert.match(html, /display-connect">CONCEPT/);
  assert.doesNotMatch(html, /display-connect">.*READY/);
  assert.match(html, /there is no automated signup yet/);
  assert.match(html, /mailto:info@mazworks.uk\?subject=NOD%20launch%20updates/);
  assert.match(html, /NOT YET IMPLEMENTED/);
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