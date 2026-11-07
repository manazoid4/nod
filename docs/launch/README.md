# Piblo launch kit

Status: DRAFT for the owner. Nothing here is live. Prepared 7 Nov 2026.

Piblo was called "Nod" in the repo, firmware, site and docs. The rename has not been done in code. Every source file cited below still says Nod. Treat "Piblo" as the new public name and "Nod" as the old one.

## Files

| File | What it is |
|---|---|
| `campaign-page-draft.md` | Kickstarter page draft, Piblo brand, verified claims only |
| `press-kit.md` | Boilerplate (50/100/200 words), fact sheet, asset list |
| `social-launch-posts.md` | 6 short posts pointing to the waitlist |
| `flow-prompts.md` | 6 Google Flow (Veo) prompts for labelled concept visuals |
| `real-footage-shotlist.md` | How to film the real prototype so concept footage can be replaced |

## What is true today (the only basis for any claim)

Sources: `docs/ROADMAP.md`, `docs/NOD-DEVICE-AND-CORE.md`, `docs/kickstarter/GATES.md`, `docs/HANDOVER-SPRINT-2026-11-07.md`.

| Claim | Status | Evidence |
|---|---|---|
| The hub (Core) answers questions through free cloud AI, switching provider when one fails | Verified | `docs/ROADMAP.md` "Verified" |
| The device connects to the hub over Wi-Fi and stays in sync | Verified | `docs/ROADMAP.md` "Verified" |
| Wireless firmware updates | Verified | `docs/ROADMAP.md` "Verified" |
| Firmware compiles for Cardputer ADV (1,460,865 of 1,572,864 bytes) | Verified (build only) | `docs/NOD-DEVICE-AND-CORE.md` |
| Core tests: 65 pass, 1 fails (needs PowerShell `pwsh`) | Verified on Linux | `docs/NOD-DEVICE-AND-CORE.md` |
| Charging screen, typed notes | Built, not confirmed on a device | `docs/NOD-DEVICE-AND-CORE.md`; site "Device test pending" |
| Hold-to-talk voice, voice capture, agent status, confirmed PC actions | In live testing | `docs/ROADMAP.md` "In progress" |
| Approvals (yes/no on device) | To verify. Zero unapproved runs not yet proven | `docs/kickstarter/GATES.md` gate 2 |
| Flip, Slide, Snap, touchscreen, accessories, larger screen, Today screen | Concept only | `site/index.html`, `docs/kickstarter/CAMPAIGN.md` |
| Big talk-circle Home | Built on an unmerged branch (PR #17), not confirmed on device | `docs/HANDOVER-COMPETITOR-NEXT-2026-11-07.md` |

Note: `CAMPAIGN.md` lists voice, capture, approvals and timers as "working in the prototype" from the owner's brief, but also says to confirm each on video first. `ROADMAP.md` lists them as in testing. This kit follows the stricter source: they are "in testing" until there is footage.

## Kickstarter readiness checklist

Status key: done / missing / needs owner.

### Launch gates (from `docs/kickstarter/GATES.md`)

| # | Item | Status | Evidence or gap |
|---|---|---|---|
| G1 | Three workflows on uncut video on the real device | missing | Gate marked IN PROGRESS. No uncut footage in repo. See `real-footage-shotlist.md` |
| G2 | 100 approval trials, 95% complete, zero unauthorised runs, threat-model note | missing | Marked NOT MET. No trial log |
| G3 | Five outsider novice setup tests | needs owner | Needs five real people |
| G4 | Product format decided, two written supplier quotes, one printed case that fits | missing | `site/index.html` says case "not printed or fit-tested". `hardware/case/nod_case.scad` exists as CAD only |
| G5 | UK compliance assessment (radio/EMC, UN38.3 battery, WEEE, GPSR) | needs owner | Marked NOT MET. Needs professional advice |
| G6 | Unit economics from real quotes | missing | `docs/kickstarter/ECONOMICS.csv` inputs blank by design |
| G7 | Uncut demo plus real double opt-in signups | missing | Signup is real (`site/api/waitlist.js`, Resend segment "Nod") but no uncut demo, and the signup count is not recorded anywhere |

### Campaign assets and admin

| Item | Status | Evidence or gap |
|---|---|---|
| Waitlist that stores signups with consent | done | `docs/HANDOVER-SPRINT-2026-11-07.md` (PR #38, tested live) |
| Privacy notice page | done | `site/privacy/index.html`. Check it covers voice audio and AI providers (GATES.md requires this) |
| Honest status and readiness pages | done | `site/readiness/`, `site/roadmap/` |
| Concept films labelled as concept | done | `docs/NOD-FILMS.md`, site captions |
| Real device photos or footage | missing | `docs/HANDOVER-COMPETITOR-NEXT-2026-11-07.md` says to keep the Concept label until real photos exist |
| Piblo rename in firmware, Core, site, films, repo | done | PRs #41–#43 (7 Nov 2026): site, films, OG, device/Core display names, repo renamed to manazoid4/piblo. Legacy storage/update identifiers kept on purpose for compatibility |
| piblo.co.uk live and pointing at the site | done | Live over HTTPS since 7 Nov 2026; www redirects (308) to the apex; canonical, OG and sitemap use https://piblo.co.uk |
| Trademark / name clearance for "Piblo" | needs owner | Nothing in the repo. Check the UK IPO register and Kickstarter |
| Reward tiers with real prices, limits, shipping | missing | `docs/kickstarter/REWARDS.md` is all TBD |
| Funding goal and campaign length | needs owner | Depends on G6 |
| Delivery timeline | missing | Evidence-based dates only, after quotes |
| Creator bio, team description, "what if I am unavailable" plan | needs owner | Placeholders in `CAMPAIGN.md` |
| Individual or business, VAT position, accountant | needs owner | `LAUNCH-CHECKLIST.md` |
| Kickstarter identity check, bank details, submit for review, press Launch | needs owner | Cannot be delegated (`LAUNCH-CHECKLIST.md`) |
| Prelaunch page on Kickstarter | needs owner | Do not invent a follower count |
| Waitlist test contact deleted before first broadcast | done | Test contacts removed 7 Nov 2026 after the live signup test; segment holds real signups only |
| Merge state of PRs #16 to #19 (v1.0.2 base, talk-circle Home, Concept A site, desktop app) | needs owner | Listed green in `HANDOVER-COMPETITOR-NEXT-2026-11-07.md`. Current merge state not re-checked here |
| Outsider-ready setup guide for Windows | missing | Gate 3 depends on it. Desktop Core app is a draft PR #19 |
| Security review or threat-model note | missing | Gate 2 |
| Licence and credit check for borrowed ideas (Claude Desktop Buddy MIT, NucleoOS) | needs owner | Handover says licence check first |

## Rules used in this kit

- "Designed in the UK" only. No town, address or region.
- No prices, rewards, dates or specs beyond what the sources state. Gaps are marked `TODO-owner`.
- Every concept visual carries the label "Concept render, not final hardware".
- The Cardputer ADV is M5Stack's product. Say so. Piblo is not affiliated with M5Stack or Anthropic.
