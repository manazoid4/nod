# nod pre-launch site
A static, accessible site under `site/`. Separate from firmware. Optimised for easy migration of copy and truthful, demonstrated footage to Kickstarter.

## Deploy
Create a Vercel project connected to `manazoid4/nod` with **Root Directory** `site`, **Framework Preset** Other (no build step), Production Branch `main`. Git pushes to main deploy automatically. No dependencies or secret keys required.

## Routes
- `/` — early NOD interest page, three scenario interactions and source links.
- `/readiness/` — noindex founder audit and launch gates. Public URL, not a private portal.

## Before a Kickstarter campaign
1. Replace illustrative keyboard UI with **actual photographed prototype** and test video. Kickstarter design-tech rules require clear real prototype demonstration, not CGI of missing functions.
2. Resolve go/no-go gates in `docs/audits/NOD-KICKSTARTER-2026-10-09.md` and update `/readiness/` facts.
3. Replace mailto with a real tested opt-in waitlist (privacy policy and double opt-in) or verified Kickstarter pre-launch link. Do not present the current email CTA as a one-click signup.
4. Set funding target, rewards, dates and shipping only after BOM, supplier quotes, taxes and delivery validation.
5. Check page content for claims before copying sections into Kickstarter's editor.

## Validation
No build needed. Open `site/index.html`, test mode-switch controls with keyboard, mobile at 360px and reduced-motion preferences. Check internal links, semantic landmarks and no JS errors.
