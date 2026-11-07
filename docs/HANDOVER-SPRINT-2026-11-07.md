# Handover: Claude visual sprint, 7 Nov 2026

**Lanes (agreed with Maz, no competing edits):**
- Hermes agent owns `site/index.html` content/structure, waitlist form, concepts section, SEO, `site/script.js`, tests (branch `site/nod-website-upgrade`, main checkout).
- Claude owns `media/marketing/` (new files only) and, after Hermes's PR merges, a small CSS-only polish PR on `site/styles.css`.

**Done:** three editable marketing assets in `media/marketing/` (announce 1080x1350, Kickstarter teaser 1920x1080, social 1080x1080 with Flip/Slide drawn as labelled concepts). Edit the HTML, run `node render.mjs` (needs playwright + Chrome) to rebuild `out/*.png`. Real renders from `media/stills/` are used; concept silhouettes are simple shapes, not device renders.

**Honesty:** no launch date, price or rewards on any asset; screens labelled as interface concept.

**Next:** merge Hermes's site PR, then CSS polish (type scale, mobile hero spacing, section rhythm), then verify Vercel (`nod-kickstarter.vercel.app`).
