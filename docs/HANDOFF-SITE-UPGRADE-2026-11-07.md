# Nod Site Upgrade — Handoff

**Date:** 7 November 2026
**Git SHA (production):** cdfcac954eced8a38af6f347050b70ccf1941cff
**Branch:** main (merged via PR #35)
**Deployment:** https://nod-kickstarter.vercel.app/ — live and serving

## What changed

### New: Waitlist form
- inline name + email form with consent checkbox
- generates a mailto link via JavaScript with structured body (name, email, consent)
- ready for future Notion/Vercel serverless backend
- honest disclosure: "Clicking sends a pre-addressed email. We are working on an automated signup"

### New: Hardware concepts (Flip, Slide, Snap)
- "Designs under investigation" section between How It Works and Roadmap
- three concept cards in Concept A palette (tomato, sun, mint)
- explicit disclaimer: not prototyped, costed or scheduled — Nod project focused on Cardputer ADV software

### Improved: SEO
- JSON-LD Product schema structured data
- tighter meta description and OG description

### Improved: Navigation
- "Concepts" replaces "Progress" in main nav (reduces clutter for visitors)
- mobile nav also updated

### Improved: Hero CTA
- "Join the launch list" points to waitlist section instead of direct mailto
- cleaner fine print

### Tests
- 10/10 passing (adapted for new form pattern and JSON-LD)

## Not done / remaining

1. **Automated waitlist backend** — needs either:
   - Notion integration token stored in Vercel env vars (integration exists but needs sharing with a database)
   - Airtable connect + Vercel function
   - Form backend (Formspree, etc.)
   Maz needs to create the integration and share a database

2. **Vercel preview** — CI deploy hooks work; preview URLs auto-generate on PR

3. **No firmware or Nod Core changes** made

## Next practical steps

1. Set up a Notion database for waitlist entries, share with existing integration
2. Create `api/waitlist.js` Vercel serverless function
3. Update form action to POST to the function instead of JS mailto
4. Real Cardputer device clips for hero video
5. Kickstarter content in docs/kickstarter/
