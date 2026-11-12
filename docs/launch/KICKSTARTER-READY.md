# Kickstarter readiness gates

Status is based only on evidence committed in this repository. `TODO` means the required proof is missing; `FAIL` means repo evidence shows the gate is not met. A plan or passing code test is not a real-device demonstration.

| Gate | Status | Proof required | Repo evidence / gap |
|---|---|---|---|
| Prototype shown as it exists | TODO | Unedited footage of the current physical prototype and its actual software; label concepts clearly. | `docs/evidence/TEST-LEDGER-2026-10-11.md` records device checks, not campaign footage. |
| Hardware/software dependencies clear | TODO | Show the paired computer and network/cloud use in each relevant flow, or disclose what is unfinished. | `docs/PRODUCT-SPEC.md` describes the product; no complete current demo is recorded. |
| Press, speak, note saved | TODO | Repeat the capture on camera; show the resulting note in the inbox and verify it remains after restart. | Ledger entry 5 records an earlier capture reaching the inbox; restart and current footage are missing. |
| Physical key approves a computer action | FAIL | A safe allow-listed action completes only after an authenticated physical press; deny, timeout and injected-key cases do not execute it. | `docs/ASK-ON-PIBLO.md` says signed decisions and rejecting network-injected approval keys are not implemented. |
| Focus timer is glanceable | TODO | On-device countdown and completion are readable without navigating; show a complete real session. | `FEATURE_INVENTORY.md` lists focus among device features, but has no physical verification for this flow. |
| Product claims match the prototype | TODO | A reviewed claim list maps each campaign statement to current, repeatable evidence; concept visuals are labelled. | `docs/PRODUCT-SPEC.md` sets copy rules; no campaign claim review is recorded. |
| Safety and fulfilment plan reviewed | TODO | Recorded assessment, test plan, responsibilities and a realistic path from prototype to delivery. | No completed review or plan is evidenced in the launch docs. |
| Audience demand demonstrated | TODO | Verifiable sign-up and campaign-interest results with source and conversion context. | Site code exists; no outcome report is committed. |
| Campaign media and rights cleared | TODO | Final real footage, owned/licensed assets and a complete reviewed campaign page. | No final campaign media or review is recorded. |

Kickstarter requires Design & Technology prototype demonstrations to reflect the product's current state. CGI or effects must not demonstrate functions that do not exist; show hardware/software integration and dependencies, or disclose what is unfinished. See [Kickstarter's rules](https://www.kickstarter.com/rules#projects-must-be-honest-and-clearly-presented).
