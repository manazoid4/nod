# Kickstarter launch readiness: 8 Nov 2026

Honest scorecard from repo evidence (`FEATURE_INVENTORY.md`, `GATES.md`, `docs/evidence/TEST-LEDGER-2026-10-11.md`, `EDITIONS.md`). RAG: Red = blocks launch, Amber = partly there, Green = fine. Nothing here has been checked with outside people; waitlist size is not knowable from the repo.

**Verdict: RED. Not ready to launch.** There is a working prototype link and a clearer site, but no proof of the lead use-cases on hardware, no supplier quote, no compliance work and no real footage.

| Area | RAG | Evidence and gap |
|---|---|---|
| Product (software) | Amber | Piblo Core and firmware exist with tests. Device column in `FEATURE_INVENTORY.md`: Wi-Fi link, screen mirror and Brain Dump verified on a real Cardputer; voice reply is slow and robotic (ledger #4); Smart Alerts, approvals, focus timers are code-complete but not device-verified. Piblo Buddy is not built. |
| Hardware evidence | Red | Only Cardputer ADV on the owner's desk. No Piblo enclosure printed or fit-tested, no physical approve/snooze button design beyond keyboard keys. |
| Video and film | Red | Site films are generated concept films, labelled as such. Kickstarter hardware rules want real prototype footage. Need uncut demo (Gate 7). |
| Campaign page | Amber | `CAMPAIGN.md` and `docs/launch/` drafts exist but still say Nod and old positioning. Site now matches new positioning. |
| Audience and waitlist | Amber | Real double-opt-in form via Resend works. Signup count not recorded in repo; check the Resend segment. Typical advice is a few thousand followers before launch; unknown here. |
| Manufacturing | Red | No supplier quote. Cost and price model exists as assumptions (`EDITIONS.md`). Aluminium and Wi-Fi antenna risk untested. |
| Compliance | Red | No UK/CE assessment. Rough cost £8k to £15k for a Wi-Fi battery device if the module certificate cannot be reused; battery transport (UN38.3) summary needed. |
| Pricing | Amber | £79 / £149 decided. 45% gross margin only reached at about 500+ units and unregistered VAT. Depends on two unquoted numbers. |
| Fulfilment | Red | No fulfilment partner, no battery-parcel shipping quotes, VAT/customs approach undecided. |

## Top 10 remaining tasks

| # | Task | Owner | Effort |
|---|---|---|---|
| 1 | Record uncut 10 to 30 s clips of ask, save a note, and one alert on the real Cardputer (Gate 1) | Maz + engineering | 1 day |
| 2 | Get M5Stack volume price and battery/radio certificates | Product | 2 hours to send, 1 week reply |
| 3 | Send CNC and print quote requests (STEP files, 100/250/500/1000), 3 to 5 suppliers | Product | 4 hours + design file prep 1 day |
| 4 | Prototype one aluminium shell and test Wi-Fi range with and without antenna window | Engineering | 3 to 4 weeks lead, 1 day test |
| 5 | Build physical approve/reject/snooze behaviour and Smart Alerts on the device, verify on hardware | Engineering | 3 to 5 days |
| 6 | Build and demonstrate Piblo Buddy states on device (idle, working, celebrating, sleeping, attention) | Engineering | 3 to 5 days |
| 7 | Print and fit-test the Original enclosure (Gate 4 case) | Maz | 1 to 2 days |
| 8 | Accountant call: VAT registration, import VAT from China, entity | Maz | 2 hours |
| 9 | Compliance lab quote (EMC + RED, module reuse) and UN38.3 position | Product | 3 hours + 1 week |
| 10 | Five outsider setup tests and fulfilment partner quotes (Gate 3) | Maz | 2 to 3 days |

Also pending: update `CAMPAIGN.md` and `REWARDS.md` from Nod to Piblo positioning once prices are confirmed, and read the free manufacturing research when it lands.
