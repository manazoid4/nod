# piblo.co.uk before and after: 8 Nov 2026

Screenshots (full page, Playwright, reduced motion): `before-390.png`, `before-1440.png`, `after-390.png`, `after-1440.png`.
Checks: no horizontal scroll at 390 px (scrollWidth 390 = viewport) and 1440 px. `node --test site/tests/site.test.mjs site/tests/waitlist.test.mjs`: 30 pass, 0 fail (no test edits needed).

| Area | Before | After |
|---|---|---|
| Page title, meta, share text | "Ask. Listen. Remember." / "Less screen. More life." / "pocket device for the things you'd lose" | "Your pocket companion for getting things done"; meta and JSON-LD drop "AI device" wording |
| Header CTA | Join the launch list | Get launch-day price |
| Hero | H1 "Ask. Listen. Remember." plus slogan and vague lede | One-line benefit H1 (remember, focus, get things done), plain lede on alerts and real buttons, one primary CTA, "Heading to Kickstarter" eyebrow, honest fine print |
| Everyday scenarios | None | New: Bins out tonight, Before the meeting, Say it save it; note that alerts and buttons are in development, only voice notes to a Windows PC shown so far |
| Piblo Buddy | None | New section: five moods (idle, working, celebrating, sleeping, needs you) as simple concept art, labelled "In development" and "not yet running on a real device" |
| Trust block | None | New "You own it. Really.": no mandatory subscription, open-source, yours long term, no lock-in; outside services may charge |
| Editions | None | New teaser: Piblo Original (planned £79) and Founder's Edition (planned £149, machined aluminium, numbered); labelled target prices; clip-on screen only "being explored" |
| Concept films | Two cards, hidden heading | Kept under visible "See the idea" heading; captions unchanged |
| FAQ | None | New: start date, price, shipping, what works today, monthly fee, where made |
| Waitlist | "Be there when Piblo launches" / Join the launch list | "Be first to see the launch-day price" / Get launch-day price; form, `/api/waitlist`, consent and honeypot `piblo_hp_field` unchanged |
| CTA repetition | One label in two places | Same "Get launch-day price" in header, hero, trust block and form |
| Files | `index.html`, `styles.css` | `index.html` rewritten, new `clarity.css` for new sections (no inline styles, CSP unchanged) |

Accessibility: heading order is h1, h2 sections, h3 cards; Buddy faces are inline SVG with labels; existing AA colour pairs reused; location shown only as "UK"; no phone number.

Claims checked against `FEATURE_INVENTORY.md`: no feature is stated as working on hardware except link to a Windows PC and saved voice notes (Device column ✅).
