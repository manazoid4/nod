# nod pre-launch site
A static, accessible site under `site/`. Separate from firmware. Optimised for easy migration of copy and truthful, demonstrated footage to Kickstarter.

## Deploy
Create a Vercel project connected to `manazoid4/nod` with **Root Directory** `site`, **Framework Preset** Other (no build step), Production Branch `main`. Git pushes to main deploy automatically. No dependencies or secret keys required.

## Routes
- `/` — early NOD interest page with three core interface scenarios, two interactive **non-functional proposed-workflow** illustrations (saved-video knowledge / Reel-to-Print), transparent limitations, FAQ and source links.
- `/readiness/` — noindex founder audit and launch gates. Public URL, not a private portal.

## Before a Kickstarter campaign
1. Replace illustrative keyboard UI with **actual photographed prototype** and test video. Kickstarter design-tech rules require clear real prototype demonstration, not CGI of missing functions.
2. Resolve go/no-go gates in `docs/audits/NOD-KICKSTARTER-2026-10-09.md` and update `/readiness/` facts.
3. Replace mailto with a real tested opt-in waitlist (privacy policy and double opt-in) or verified Kickstarter pre-launch link. Do not present the current email CTA as a one-click signup.
4. Set funding target, rewards, dates and shipping only after BOM, supplier quotes, taxes and delivery validation.
5. Check page content for claims before copying sections into Kickstarter's editor.

## Validation
No build needed. Open `site/index.html`, test mode-switch controls with keyboard, mobile at 360px and reduced-motion preferences. Check internal links, semantic landmarks and no JS errors.

## October concept showcase
The homepage contains a **concept-only** video learning and Reel-to-Print story. The tab switcher is an accessible, client-side illustration; it does **not** fetch Instagram data, download media, run models, slice files, access OctoPrint or trigger a printer. Keep every disclaimer and no-auto-print rule when iterating. An Instagram Saved JSON export generally supplies links, not other creators' Reel media. We must only ingest content with legitimate access/rights. A real proof would show original creator-linked/licensed STL and supervised physical print, plus timestamped audio/visual learning evidence. The Cardputer is a PC companion, not a standalone media GPU or printer.

## Deployment acceptance (October)
- Both sets of scenario tabs respond to mouse, touch, arrows, Home and End; ARIA selected/labelledby stays synchronised.
- All FAQ entries open with keyboard, nav anchors resolve, and reduced motion is respected.
- Test 360px / 390px / 768px / 1280px. No external image/fonts or third-party JS dependencies.
- Mailto launches email, **not** a fictitious signup; future Kickstarter waitlist requires actual backend, privacy policy and verified consent.
- Check Vercel production deployment SHA and custom-domain visitor accessibility separately (team SSO may protect vercel.app subdomains).
