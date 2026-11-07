# Handover: Claude visual sprint, 7 Nov 2026

**Lanes (agreed with Maz, no competing edits):**
- Hermes agent owns `site/index.html` content/structure, waitlist form, concepts section, SEO, `site/script.js`, tests (branch `site/nod-website-upgrade`, main checkout).
- Claude owns `media/marketing/` (new files only) and, after Hermes's PR merges, a small CSS-only polish PR on `site/styles.css`.

**Done:** three editable marketing assets in `media/marketing/` (announce 1080x1350, Kickstarter teaser 1920x1080, social 1080x1080 with Flip/Slide drawn as labelled concepts). Edit the HTML, run `node render.mjs` (needs playwright + Chrome) to rebuild `out/*.png`. Real renders from `media/stills/` are used; concept silhouettes are simple shapes, not device renders.

**Honesty:** no launch date, price or rewards on any asset; screens labelled as interface concept.

**Next:** merge Hermes's site PR, then CSS polish (type scale, mobile hero spacing, section rhythm), then verify Vercel (`nod-kickstarter.vercel.app`).

## Update, 7 Nov 16:45 (Claude Opus + 2 Sonnet agents)
- **Hermes work all merged:** #35 (site upgrade) and #37 (its leftover handoff docs). No open Hermes branches.
- **Waitlist is real (#38):** `site/api/waitlist.js` adds signups to the Resend segment **"Nod"** (separate from Maz Works/Maz Meats). Owner alert to info@mazworks.uk from signups@mazworks.uk. Vercel env set (prod+preview): RESEND_API_KEY (dedicated key "nod-kickstarter waitlist (Vercel)", revoke in Resend if needed), RESEND_SEGMENT_ID, SIGNUP_NOTIFY_EMAIL. Verified live: test signup landed in segment and alert sent. Test contact `info+nodtest@mazworks.uk` is still in the segment; delete it before the first broadcast.
- **Shorter homepage (#39):** desktop 10,365 → 6,930px, mobile 16,213 → 9,830px. Roadmap/ideas sections moved off the homepage (full roadmap at /roadmap/).
- **Tests:** `node --test site/tests/site.test.mjs site/tests/waitlist.test.mjs` (23 pass). CI runs both. Note: `node --test site/tests/` (directory) fails on Node 24, use file paths.
- **Next:** first Resend broadcast to the Nod segment when there is a real device clip; delete unused `.journey/.ideas/.ticket` CSS; `concepts/b/` still has an old mailto form.
