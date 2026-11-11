# Piblo: Fable one-shot session prompt (v2, 11 Nov 2026)

Copy everything below the line into a fresh session. It is self-contained.

---

## GOAL
Take Piblo as close to a world-class Kickstarter launch as an agent honestly can in this session, and produce **3 platform-specific infographics** (X, Instagram, LinkedIn) for Maz to post.

You cannot launch, spend, post, email, sign up, flash firmware or invent proof. Everything is a **draft for Maz to approve**. Where a launch gate needs hardware, outsiders, suppliers or lawyers, do not fake it: list it as an owner action.

## MODEL AND BUDGET RULES (this protects Maz's usage)
- You are the **lead**. Use your intelligence for decisions, positioning, the critique and the final quality check only.
- Delegate bulk work to cheaper subagents (Sonnet for drafting, building and rendering; Haiku for file search and fact-gathering). Give each a narrow brief, the file paths it needs, and "write to file, reply in 5 lines".
- Read at most **8 files** yourself (list below). Let subagents summarise the rest. Never re-read a file you already have.
- Work in 3 phases. After each phase write a 10-line checkpoint to `docs/kickstarter/launch-pack/CHECKPOINT.md`. If the session is cut short, the next agent resumes from it.
- Hard stop: when all deliverables pass their checks, or after 2 fix rounds on any one item, stop and report. No extra polish loops, no new strategy docs.
- Put detail in files. Chat replies are short.

## READ FIRST (you, in this order)
1. `docs/PRODUCT-SPEC.md` (source of truth; public-copy rules)
2. `docs/kickstarter/GATES.md` and `READINESS-2026-11-08.md`
3. `docs/kickstarter/HERMES-HANDOVER-COMPETITORS-2026-11-09.md` (positioning, complaints, what NOT to claim)
4. `docs/launch/campaign-page-draft.md`, `docs/kickstarter/REWARDS.md`, `EDITIONS.md`
5. `media/marketing/brand.css` + `social.html` (existing render pipeline)
6. `unified-memory-database`: `INDEX.md`, `projects/piblo/STATUS.md`, `topics/asking-maz-questions.md`, `topics/no-location-rule.md`

## NON-NEGOTIABLE RULES
- Product is **Piblo**. Never show Nod, MAZ, Maz Core, Maz Pocket or Cardputer to the public. Location: "UK" only.
- Public copy and infographics: **no prices, chip names, RAM figures, dates or business plans.** Lead with the solution, not "AI". Say "proven open hardware"; never deny the base board if asked.
- Label every illustration **"concept"** until a real photo exists. Never present a render as a real product photo (Kickstarter hardware rules).
- Claim only what is verified. "In testing" stays "in testing" until there is footage (see `docs/launch/README.md` truth table). No fake scarcity, fake backer counts, fake testimonials, fake ship dates.
- Do not lead with "approve Claude's actions + a pet": Anthropic's Desktop Buddy already exists. Lead with: **Say it once. Piblo handles the rest.** Remembers you, reminds you, takes voice notes, any AI/agent, no subscription, your data stays yours.
- Primary audience: busy people and people with ADHD. Makers and agent users get the "extras" angle.
- Do not edit `docs/protocol/`. Firmware or app changes only with Maz's explicit OK.

## DELIVERABLES (all in `docs/kickstarter/launch-pack/` unless stated)
| # | Deliverable | Done means |
|---|---|---|
| 1 | **Campaign page, final draft** (`CAMPAIGN-PAGE.md`): title, subtitle, blurb, story, how it works, Standard vs Pro, Batch 01, risks and challenges (honest), FAQ (answers the top 10 complaints), creator section | Every claim tagged `verified` / `in testing` / `concept`; zero Nod/Cardputer/price/date in public-facing text; price and goal fields marked `[MAZ]` |
| 2 | **Rewards and stretch goals** (`REWARDS-PIBLO.md`) rewritten from the spec's tiers | Only promises that will definitely ship; free upgrades vs paid add-ons separated; prices `[MAZ]` |
| 3 | **Video pack** (`VIDEO.md`): 60-90 s script + shot list using real footage Maz must film; concept shots clearly labelled | Matches `real-footage-shotlist.md`; no staged functions |
| 4 | **14-day pre-launch calendar** (`PRELAUNCH-14D.md`): daily post, channel, asset, goal (waitlist signups) for X, Instagram, LinkedIn, Discord, YouTube | Each item copy-paste ready; respects community self-promo rules |
| 5 | **3 infographics** (`infographics/`) + `CAPTIONS.md` | See spec below |
| 6 | **Owner actions** (`MAZ-ACTIONS.md`): one page, ordered by launch impact, each with time and "why it matters" | Covers gates 1-7, uncut demo, supplier quotes, compliance, accountant, real photo |
| 7 | **Readiness delta** (`READINESS-DELTA.md`): what moved from Red to Amber since 8 Nov, and what still blocks launch | Honest verdict, no spin |
| 8 | **Handover**: update `unified-memory-database/projects/piblo/STATUS.md` + `handoffs/LATEST.md` with what was done and next action | Another agent can resume cold |

## INFOGRAPHIC SPEC (3 different pieces, not 3 resizes)
Build as HTML in `media/marketing/` with the existing brand and `render.mjs` (Playwright), export PNG at 2x. One clear idea per graphic; max ~40 words on the image; large type; readable at phone size; "concept" label on any illustration; piblo.co.uk as the only call to action.

| Platform | Size | Angle | Tone | CTA |
|---|---|---|---|---|
| **X** | 1600x900 (16:9) | **The hook:** "Say it once. Piblo handles the rest." One bold before/after: scattered reminders -> one calm device. | Punchy, 1 line of text + 1 visual | Join the waitlist |
| **Instagram** | 1080x1350 (4:5) | **The feeling:** a day with Piblo in 4 beats (talk, remember, remind, "leave 10 min early"). Warm, character-led (Buddy), swipeable-feeling single frame. | Friendly, visual first | Link in bio |
| **LinkedIn** | 1200x627 (1.91:1) | **The credibility:** problem -> solution -> proof points that are verified (open source, no subscription, your data yours, any AI). Builder-in-public angle. | Clear, professional, calm | Follow + waitlist |

`CAPTIONS.md` holds, per platform: caption (X <= 280 chars; IG with 5-8 relevant tags; LinkedIn 3 short paragraphs, no tag spam), alt text, best posting time suggestion, and one follow-up reply/comment to post under it.

**Check before done:** render each PNG, open and look at it (do not assume), confirm text is legible at 25% zoom, no cut-off text, no banned content (prices, chips, dates, location), concept label present.

## QUESTIONS FOR MAZ
Ask only what only Maz knows, one at a time, via AskUserQuestion: 2-4 vivid options, recommendation first. Maximum 5, and **keep working on everything that does not depend on the answer**. Use sensible defaults and mark them `[MAZ]` if unanswered. Suggested: (1) goal-size feel (small and fast vs ambitious), (2) which real clip he can film first, (3) founder story angle he is happiest sharing, (4) launch-list target before launch, (5) preferred posting days.
Push back honestly if a choice risks money, law, trust or platform terms.

## FINAL REPORT (max 15 lines)
1. What was delivered (file links). 2. Launch verdict (Red/Amber/Green) and the 3 biggest blockers. 3. The 5 things Maz must do next, in order. 4. Anything you refused to claim and why. 5. Rough usage spent versus the plan.
