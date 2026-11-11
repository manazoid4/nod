# Fable one-shot: build Piblo's launch machine (product proof, community, private command centre)

Paste everything below the line into a single Fable session. Fable runs it start to finish.

---

## Mission

Make Piblo the pocket AI device people are already waiting to back: a real, working, open product and a real, warm community, so the Kickstarter funds in minutes, the way Kode Dot (kode.diy) did (a goal of EUR 4,387 funded in 5 minutes, about US$2.7M in the end, with 180+ visual assets, a small number of very relevant creators and a stretch-goal ladder the community reordered) and Flipper Zero did (US$1M on day one, then a Discord of 100K+). Set the bar high. Do not think small.

**Beat Anthropic's Fable 5.2 voice-hub video (9 Nov, 697K views).** That video shows a one-paragraph prompt becoming an early prototype board. Piblo's answer is what it cannot show: a **real device in a real hand doing three real things uncut** (approve an agent action with a physical press, voice typing into any app, "Where was I?"), **open source, no subscription, your data provably stays yours**, and **a community that helped shape it**. Everything you produce should make that contrast obvious.

You cannot launch, post, spend, flash firmware or invent proof. Everything outward-facing is a draft or a built-and-ready asset for Maz to approve. Ambition never overrides honesty: no fake counts, scarcity, testimonials, dates or demos. Where a launch gate needs hardware, outsiders, suppliers or lawyers, list it as a Maz action.

**Honest maths to plan around (do not fudge it):** Kickstarter says 1-5% of an email list typically pledges; Kode Dot funded in minutes because a tiny goal met a warm list; CardputerZero had 5,000+ followers plus US$1 reservations before it raised US$1.9M. "Funded instantly" therefore needs two things: a goal Maz chooses small enough to be hit by the warm list, **but never below what it truly costs to deliver a first batch** (Kode Dot was criticised for a goal so small it looked unserious), and a list big enough to hit it. Model both (private repo, `finance/`), recommend a launch gate (list size, Discord size, proof assets done) and a goal, and mark both `[MAZ]`.

**Deliverables (the session is judged on these):**

| # | Deliverable | Done means |
|---|---|---|
| A | Ask on Piblo (host side) | Tests pass; one 3-line demo script |
| B | Voice typing | Tests pass; works offline |
| C | Park it / Where was I? | Tests pass; survives restart |
| D | Private mode + "How your data stays yours" page | Leak test fails on any non-local request; page text matches what the code enforces |
| E | Voice before/after numbers | Evidence in `docs/evidence/voice-<date>/` |
| F | `piblo-private`: the command centre (see below) | A new agent or Maz can open the repo cold and know the goal, the milestones, this week's tasks and the marketing plan within 5 minutes |
| G | Project scan: finished work in other repos that becomes Piblo features | Ranked list: feature, code location, licence, port effort |
| H | Site wording audit | Tests green, 390 px and 1440 px checked |
| I | Community engine (Phase 4): Discord blueprint, free-value drops, weekly content system | First 2 weeks fully drafted, weeks 3-8 outlined, all copy-paste ready |
| J | Kickstarter pack (Phase 4): page draft, rewards, community-voted stretch ladder, FAQ, honest risks | Every claim tagged verified / in testing / concept; prices `[MAZ]` |
| K | Flagship film plan + first assets (Phase 4) | Script, shot list, thumbnail and 3 platform infographics rendered and checked |
| L | Free Piblo for PC beta pack (Phase 4) | Host-side features packaged so waitlist members can really use them before launch; release itself waits for Maz's OK |
| M | `MAZ-ACTIONS.md` | One page: what only Maz can do next, ordered by launch impact |

## Run mode: one shot, unattended

Why this matters: Maz has a separate usage limit just for Fable and wants this whole job done in one run. He is not watching. Your first message back is his first look at any of it.

- **Resume first.** If `docs/evidence/CHECKPOINT.md` exists, read it and continue from it instead of starting over. A bare "continue" from Maz means exactly that.
- **Permissions already granted by Maz (11 Nov): do not ask for these.**
  - Search anything: use every search and fetch tool available (WebSearch, Parallel, Firecrawl, TinyFish, Exa, GitHub, YouTube pages and transcripts), not just one; cross-check important facts across at least two.
  - Read all of Maz's GitHub repos and branches; create feature branches and PRs; create the private repo `manazoid4/piblo-private`; merge host-side PRs when tests are green.
  - Install and use permissively licensed tools; use free-tier models.
  - Still ask first, every time, for: spending money, flashing firmware, posting or emailing anything publicly, deleting or force-pushing, and anything that sends Maz's data off his machines.
- **Interview style for pre-flight** (Anthropic's own advice): one question at a time, only where the answer would change what you build.
- **Pre-flight, then no more stops.** Before any building, ask Maz at most 5 easy questions, one at a time (2-4 vivid options, recommendation first, only things only he knows, e.g. goal feel, founder story, first clip he can film). If he does not answer, use your recommended option and mark it `[MAZ]`. After pre-flight, run to the end. Pause only for something destructive or irreversible, a real scope change, or input only Maz can give (flash OK, spending, posting, listening tests). Then ask and end the turn; do not end on a promise.
- **When you have enough information to act, act.** Do not re-derive settled facts, re-litigate Maz's decisions, or narrate options you will not pursue. Give a recommendation, not a survey.
- **Do the simplest thing that works well.** No extra features, refactors, abstractions, fallbacks for cases that cannot happen, or designs for hypothetical futures. Build on what exists.
- **Protect the Fable limit.** Fable's own tokens go to planning, briefs, review, the verifier decisions and the final pass. Bulk building, scanning and drafting go to Opus, Sonnet and free-model helpers. Keep long-lived helpers (they keep their context and cost less than fresh ones) and talk to them asynchronously; do not block on the slowest one.
- **The builder never grades itself.** For every deliverable A to M, a separate fresh-context verifier (Opus or Sonnet) checks the real output against the "done means" column: the running tests, the actual rendered PNGs, the actual page at 390 px and 1440 px. It tries to prove the work fails. You decide on its report.
- **Ground every claim in evidence.** Before reporting progress, audit each claim against a tool result from this session. Report only work you can point to; say plainly what is not yet verified.
- **Log surprises, keep going.** Keep `docs/evidence/implementation-notes.md`. When reality forces you off the plan, pick the conservative option, write it under "Deviations" with the reason, and continue. Record one short lesson per item (what was corrected or confirmed, and why it mattered) so a later run starts smarter.
- **Do not end on a promise.** Before ending a turn, check your last paragraph: if it is a plan, a question you could answer yourself or a promise ("I'll..."), do that work now with tool calls.
- **Your last message is a re-grounding, not a continuation.** Outcome first in one sentence, then the one or two things Maz must do, in plain full sentences with no working shorthand, arrow chains or labels you invented. Do not reproduce your reasoning in the response.

## Usage guard (Maz's weekly usage was at 96% on 11 Nov)

- You read at most 10 files yourself; helpers summarise the rest. Never re-read a file you already have.
- Put detail in files; chat replies stay short.
- Write a 10-line checkpoint to `docs/evidence/CHECKPOINT.md` after each phase so a cut-off session resumes without repeating work.
- Max 2 fix rounds on any single item, then log it and move on. No extra polish loops, no new strategy documents.
- If the Fable limit hits mid-run, the checkpoint must be good enough for any model or a later Fable session to resume cleanly. If the limit looks tight, protect this order: A-E (product proof), F (private repo), K (film plan and 3 infographics), I and J (community and Kickstarter), L, M, then G and H. Never leave a feature half-wired.
- Run at high effort, not max.

You are **Fable, the lead** for Piblo (repo `manazoid4/piblo`, Windows laptop, owner Maz). You run this as **one execution**. Your job is to orchestrate, review and polish. **You do not write the bulk code yourself.** That keeps Maz's usage low.

## How you work

| Who | Does what |
|---|---|
| **You (Fable)** | Read context, split the work, write the briefs, review every diff, fix what's wrong, make the final product feel polished ("the Fable touch"), merge, report. |
| **Opus 5.5 subagents** | Hard parts: voice turn-taking and barge-in, the learning loop, the agent builder. |
| **Sonnet 5.5 subagents** | Bounded builds and tests: features with clear specs, test harnesses, fixtures, docs. |
| **Free models** (OpenRouter free tier, Groq free, OpenCode/Hermes on MazPC with free models) | Bulk and cheap work: scouting the repo, writing fixtures, drafting tests, first-pass reviews, summarising logs. |

Rules for helpers: at most 3 running at once; each gets its own git worktree and branch; each brief states goal, files, acceptance test, and limits; each returns a diff plus test output, never a plan. One lane per helper: **voice**, **features**, **tests/QA**.

## Hard rules

- **Build on what exists.** Read before writing. Do not re-engineer working parts.
- **Borrow before building.** Permissively licensed code only (MIT, BSD, Apache). **No AGPL code in Piblo.** Note every borrowed source in the PR.
- **Spend nothing.** No purchases, no paid models, no paid APIs without Maz's explicit OK. Free tiers only.
- **Never flash firmware** without Maz's explicit OK each time. Host-side (Core) changes are fine.
- **Public repo:** no prices, budgets, business plans, tokens or IP addresses in commits.
- Product name is Piblo; never show Nod, MAZ or Cardputer to users (`AGENTS.md`).
- Keep `docs/PRODUCT-SPEC.md` as the source of truth; if you change a decision, update it there.

## Read first (helpers can summarise for you)

1. `docs/PRODUCT-SPEC.md`, `docs/NEXT-4-WEEKS.md`, `AGENTS.md`.
2. `docs/VOICE-SETUP.md` (model on MazPC, SSH tunnel, known issues) and `docs/VOICE-SPRINT-BRIEF.md` (voice targets, test script, automated tests).
3. Core modules that already exist and must be reused: `live_voice.py`, `live_brain.py` (memory, model switching, OpenRouter -> Ollama -> local fallback), `library.py` (saves + search index), `buddy.py` + `buddy_store.py` (agent approval queue), `needs.py` (needs-you queue, three tiers), `nudge.py`, `focus.py`, `braindump.py`, `skill_vault.py`, `agent_runner.py`, `workflows.py`, `phone_control.py`, `authority.py`, plus the Android app in `android/`.
4. Open PRs and recent merged PRs on piblo; the latest ledger entries in the private memory repo if you can reach it.

## State on 11 Nov (from Maz)

- Voice now sounds smooth (no crackle). It still needs fine-tuning.
- It answered "what's on today?" with its model name (cloud brain had no key; omni fallback had no Piblo persona).
- Keyboard taps are detected as speech (energy-only VAD).
- Model: LFM3-Omni-2B on MazPC via llama-server; reach it from the laptop with the SSH tunnel in `docs/VOICE-SETUP.md`.

## Top priorities (Maz, 11 Nov): do these first, everything else after

1. **Ask on Piblo, hardware-wallet style.** Like confirming a Bitcoin transaction on a Ledger/Trezor: Piblo is the trust anchor. Any agent's consequential action (email, calendar, purchase, delete, deploy) is shown **on Piblo's own screen** in plain words (who, what, amount, where), and only a physical press on Piblo confirms it; the computer alone cannot approve. Deny, voice edit ("yes but change the subject"), Pause-all, Undo where reversible, batch non-urgent requests during Focus. Reuse `buddy.py`, `needs.py`, `authority.py` and the firmware approval screens. Agent-agnostic (Claude Code, Codex, Hermes, MCP). Beat Anthropic's Claude Desktop Buddy (ideas only; its licence is unclear).
2. **Voice typing** (item 11 below).
3. **Where was I? / Park it** (item 13 below, plus instant "Park: ..." capture via `braindump.py`).
4. **Private voice and memory on the host PC, provably.** For Standard, all voice and memory run on the paired computer, not the device (saves device compute) and not on any server. Prove it: a "Private mode" where Core makes **zero outbound internet connections** (enforced in code, covered by a test that fails on any non-local request), no data retention outside the user's own folders, an on-screen privacy indicator, and a plain-words "How your data stays yours" page for the site. Cloud AI stays optional and clearly labelled when used. Never claim more than the code enforces.

Pro-only versions (on-device voice/memory, Replay with KVM) are saved for later; do not build them now.

Clarifications that avoid wasted work:
- "Zero outbound connections" means no traffic leaves the user's own machines. Loopback and the SSH tunnel to the user's own PC are allowed; anything else fails the test.
- Ask on Piblo: firmware stays untouched without Maz's OK. Build and test the host side and the protocol contract with a simulated key press; the device screens already exist. Protocol changes in `docs/protocol/` go through the orchestrator (see `AGENTS.md`), so propose them, do not silently edit.
- Never write "no servers" or "zero retention" on the site beyond what the code and tests enforce (the waitlist, for example, does use a mail provider).

## Private repo: the command centre (`manazoid4/piblo-private`)

Create it **private**. It is where Maz and every agent (Claude, Codex, OpenCode, Hermes, others) go to know what Piblo is, where it stands and what to do next. Nothing secret goes into the public repo. Make it excellent:

```
README.md        one page: what Piblo is, the mission, the 3 launch gates, links to everything
AGENTS.md        rules for any agent: read order, public-copy rules, what needs Maz, how to claim and finish a task, how to hand over
NOW.md           this week only: top 5 tasks, owner, status, blockers (rewritten every week)
ROADMAP.md       milestones M0-M9 with exit criteria (see below)
decisions/       one short file per decision (what, why, date, who); ADR style
launch/          gates, goal and list-size model, Kickstarter page draft, rewards, stretch ladder, FAQ, risks
marketing/       strategy, weekly content calendar, templates, assets index, 8-week plan, per-platform playbooks
community/       Discord blueprint, roles, rules, events, free-value library, moderation, backer-voting process
product/         spec mirror, feature list with status (works / in testing / concept), scan results
finance/         unit economics, goal model, supplier quotes, budget (private numbers live here)
suppliers/       RFQ drafts, quotes, M5Stack outreach, compliance notes
evidence/        links to proof: test runs, device clips, numbers
handoffs/        dated hand-over notes, newest first
```

Also set up on GitHub: **milestones** M0-M9 with due dates, **issues** for every concrete task labelled by lane (`product`, `marketing`, `community`, `hardware`, `legal-finance`, `maz-only`), a **Project board** (Backlog, This week, Doing, Verify, Done), issue and PR templates, and a weekly "Piblo week" issue that lists the content that must ship. Every issue states: goal, done-means, who can do it (agent or Maz), and links.

**Milestones (adjust only with reasons, record in `decisions/`):**
- M0 Foundations: private repo live, truth table, public-copy rules, Discord blueprint approved.
- M1 Proof: Ask on Piblo, voice typing, Where was I?, Private mode working on the real device and PC, uncut clips filmed.
- M2 Community seed: Discord open, free PC beta released to the first members, weekly content running.
- M3 Flagship film and site: film published, site wording done, waitlist double opt-in proven.
- M4 Build in public: first outsider setup tests, supplier quotes in, case printed and fit-tested.
- M5 Community co-design: backers vote on Buddy forms, voices and the stretch ladder.
- M6 Compliance and economics locked: goal and prices set by Maz from real quotes.
- M7 Pre-launch page live and list at target.
- M8 Launch and day-one plan rehearsed.
- M9 Campaign weeks and fulfilment plan.

**Project scan (deliverable G).** Scan all of Maz's GitHub repos (`gh repo list manazoid4 --limit 300`, then READMEs, recent PRs and branches of the relevant ones; use free models for the scan). Many projects are unfinished but contain finished work (e.g. Recall/Feed Vault, maz-pocket, nod, agent-nudge, mazos-ui, hermes job hunter, khutba-io, receptionist work). Find features that already exist elsewhere and could become Piblo features cheaply. Output a ranked list in `piblo-private/product/` (feature, where the code is, licence, effort to port), and port only items that fit the top priorities.

## The work, in order

### Phase 0: stand up the command centre (30 minutes of effort, do it first)
Create `piblo-private` with `README.md`, `AGENTS.md`, `NOW.md`, `ROADMAP.md` (M0-M9), the GitHub milestones and labels, and the Project board. From here on, every task you run is an issue, and `NOW.md` plus `docs/evidence/CHECKPOINT.md` are updated after each phase. Fill the rest of the repo in Phase 4.

### Phase 1: test harness first (Sonnet + free models)
Build the automated voice tests from `docs/VOICE-SPRINT-BRIEF.md` ("Automated tests"): WAV fixtures including **typing with no speech**, turn-detection tests, persona tests, latency over the real `/voice/live` WebSocket, word-accuracy tracking, results to `docs/evidence/voice-<date>/`. Run a **baseline** before any change.

### Phase 2: voice to GPT-Live level (Opus lead, Sonnet tests)
In order: persona and memory on every path (never names the model); real speech detection so typing never triggers a turn (Silero VAD or similar, permissive licence); smarter end-of-turn (no cut-offs on pauses, no awkward silence); barge-in by just talking (mic key as backup); first audio about 1 s; short check-back only when unsure before actions; free working brain configured. Keep the LFM3-Omni-2B model unless tests prove something better. One change at a time; keep only measured improvements.

### Phase 3: make it useful (Opus for the loop and builder, Sonnet for the rest)
Wire these into live voice, reusing the modules above:
1. **Memory**: "like I said yesterday" works; Obsidian-style linked Markdown notes, local-first.
2. **Agent builder**: "Piblo, make me an agent that ..." creates a saved agent (skill file + schedule), with the three safety levels (just do it / ask on Piblo via key press / never).
3. **Learning loop (every feature)**: Hermes-style. Watch what the user skips, acts on or corrects; rewrite the per-user skill note; use it next time; weekly "here's what I learned", editable. Borrow from Nous Research's Hermes Agent (MIT); do not depend on it.
4. **Speaks first (time and travel)**: leave-now, meeting in 10, deadlines, commute delays (free public transport or calendar data).
5. **Catch me up + Filter**: a 2-minute spoken summary from notifications, calendar and saves; ends with "everything else can wait"; learns what to skip. The same notification feed also works live as a **filter**: family calling gets through at once, deliveries show quietly, social media stays silent; reply to supported messages with short preset responses (key press to send). Uses the Android app's notification access, with the owner's permission.
6. **Send it to Piblo**: Android share target -> captions first, local Whisper, small free/local model summary (target a few hundred tokens), filed into `library.py`; resurfaces saves when relevant.
   **Include YouTube links** (Maz's idea, 11 Nov): share a YouTube link to Piblo and it fetches the captions (`yt-dlp` and the video's own subtitles first; no audio download when captions exist), falls back to local `whisper.cpp` only when there are none, then makes a short local summary and files the full transcript, searchable ("what did that video say about X?", "read me the 3-line version"). Reuse the approach of MIT projects `KIRVO-REPORTING/video-to-notes`, `jamesbubenik/VidSift` and `tcsenpai/youlama` (ideas and permissive code only; check each licence; the summary model must be permissive, since some popular small models are non-commercial; do not bundle a GPL ffmpeg build). Private mode note: fetching a link the user asked for is the only allowed outbound request, and it is labelled on screen; processing stays local. Stay within YouTube's terms: prefer captions, no bulk downloading.
7. **First three minutes** onboarding and **Buddy forms** (Seed, Monk, Tinkerer, Explorer, Night Owl, Sunny; each = pixel art + one rule).
8. **MCP connections** for Gmail, Calendar, Notion, GitHub, Hermes (use existing MCP servers).
9. **Teach Demo, refined** ("show me once"): the recording side already exists (device CAPTURE -> TEACH DEMO; `teach_capture.py`: screen + mic via ffmpeg, M marks, transcription, scene frames). Add the missing half: turn a recording into a reusable skill/agent (steps written in plain words from transcript + marks + frames), read it back for the user to confirm, then run it next time under the safety levels (computer actions always "ask on Piblo" until the user loosens it). Recordings stay local; offer pause and delete; never keep passwords visible in saved frames. Feeds the learning loop. **Replay**: a learned routine (e.g. "when I finish work: message my partner, open my journey home, phone on silent") can be saved as **one physical shortcut** on Piblo, run across supported PC, phone and smart-home integrations, and **shared** with other users as a template.
10. **Anywhere ("Where was I?")**: retrieves your last document, unfinished task, saved link or reminder from memory, the library and recent PC activity, and offers to send it to your phone. Keep it small; build on memory and `library.py`.

13. **Polish existing features (do not rebuild)**: Brain Dump becomes "Out of your head" (hold, speak, saved and linked); Focus sprint powers Buddy's Monk form; the needs-you queue (`needs.py`, three tiers) becomes the "Ask on Piblo" approvals screen; dictation and phone approvals: check they still work, then polish.
11. **Voice typing that beats Wispr Flow, completely free**: hold a Piblo key, speak, release, and the text lands in whatever app has focus on the paired computer (and phone, via the Android app). Copy the approach of Handy (`cjpais/Handy`, MIT): Silero VAD, local Parakeet V3 (CPU) or Whisper (GPU), paste into the focused field with clipboard restore, a personal dictionary, optional cleanup by a small local model ("make this an email"). Reuse existing dictation and phone-text code. Beat Flow on: free, offline and private, a physical button you can press from across the room, learns your words (learning loop), works on phone and computer. Bonus: the same Silero VAD fixes keyboard taps being heard as speech in live voice. If useful, the device can also act as a USB keyboard (the board has native USB); check before relying on it.
12. **Piblo Rescue**: when your phone dies, Piblo still shows selected offline info: key contacts, travel details, saved notes and emergency instructions, stored on the device and synced when connected. Works without a subscription. Ideas to review: HID-Fi (HID automation; check its licence) and FunModularKeyboard (AGPL: ideas only, do not copy code).

If everything cannot fit, follow the usage guard above: finish in deliverable order and stop cleanly.

### Phase 3b: website wording audit (Sonnet drafts, you finish)
Maz likes the site's design, colours and logo: **keep them**. The wording is nowhere near done and most features are missing. Audit `site/` (homepage, timeline, roadmap) against `docs/PRODUCT-SPEC.md`:
- Lead with solutions in plain words, not "AI". Tagline stays: "Say it once. Piblo handles the rest."
- Add the real features clearly: talks like a person, remembers, little helpers (agent builder), speaks first (time and travel), catch me up, send it to Piblo, show me once (Teach Demo), voice typing, out of your head, focus, Buddy forms, Piblo Rescue, connects to your stuff, works with any AI, your memory stays yours.
- Mark what works today vs what's coming (honest labels); no prices, chip names or dates; hardware stays "proven open hardware".
- Not too much text, not too vague: someone from an Instagram post should understand Piblo in 10 seconds on a phone, then join the launch list or the Discord.
- Run the site tests and `mw-site-gate`, check 390 px and 1440 px in a real browser, then merge.

### Phase 4: community and launch engine (Sonnet drafts, you set the bar and judge)

Rules for all public-facing output: product is Piblo; "UK" only for location; **no prices, chip names, RAM figures or dates in public copy or graphics** (they live in `piblo-private`); label every illustration "concept" until a real photo exists; claim only what the code and tests prove ("in testing" stays "in testing"); no fake scarcity, backer counts or testimonials. Lead with the solution, not "AI". Do not lead with "approve Claude's actions plus a pet": Anthropic's Desktop Buddy already does that. Lead with: remembers you, reminds you, voice typing, any AI, no subscription, your data stays yours, and a physical key that keeps you in charge.

**Quality bar:** a stranger who sees one Piblo asset can say what it does in 10 seconds, and it looks like it came from a funded studio (Apple polish, Teenage Engineering character, Flipper community warmth). Reject anything generic.

**1. Community blueprint (Flipper Zero and Kode Dot, adapted to Piblo)** in `community/`: Discord channel map (start-here, announcements, build-log, show-your-piblo, voice-typing-help, ideas-and-votes, agents-and-skills, buddy-forms, dev-corner, off-topic), roles (Founder, Early Backer, Builder, Helper), onboarding flow (welcome message, 3 questions, first free gift), moderation and self-promo rules, weekly rhythm, and GitHub Discussions for weighted feature requests (Flipper's fix for noise: top-voted, concrete requests reviewed weekly). Plan an open **catalogue** later for community Buddy forms, skills and agent templates, so the community builds the moat.

**2. Free value engine.** Every week the community gets something genuinely useful, free, whether or not they back Piblo: a skill or agent template pack, an Obsidian starter vault for memory, a voice-typing setup guide, an ADHD focus routine, a "leave on time" travel checklist, a build log with real numbers, a behind-the-scenes clip, and a live build-along or AMA. Write the first 8 as a library in `community/free-value/` with a publishing order.

**3. Weekly content system** in `marketing/`. Every week, minimum: **2 short videos** (one real device clip, one explainer), **3 images or infographics** (one per platform angle), **1 build-log post with real numbers**, **1 free-value drop**, **1 live or Discord event**, **1 community poll** that feeds a real decision (names, Buddy forms, stretch order), and **1 summary email** to the waitlist. Draft weeks 1-2 completely (copy, alt text, shot lists, posting times for X, Instagram, LinkedIn, YouTube, Discord, Reddit communities that allow it) and outline weeks 3-8. Add a creator plan: 10 highly relevant small creators (ADHD productivity, maker, open-source AI, Flipper and Cardputer communities) with a respectful, value-first approach; do not contact anyone, draft only.

**4. Flagship film plan.** One 60-90 s film (plus 15 s and 30 s cuts) built on three uncut real-device moments: approve with a press, voice typing, "Where was I?". Script, shot list matching `docs/launch/real-footage-shotlist.md`, thumbnail options, captions. Concept shots stay labelled. Tell Maz exactly which clips to film first and how.

**5. Three infographics** (three different pieces, not three resizes). Build as HTML in `media/marketing/` with `brand.css` and `render.mjs`, export PNG at 2x, one idea each, about 40 words max, readable at phone size, CTA is piblo.co.uk only, and make them the first three templates of the weekly system.

| Platform | Size | Angle | CTA |
|---|---|---|---|
| X | 1600x900 | The hook: "Say it once. Piblo handles the rest." Before/after of scattered reminders versus one calm device | Join the waitlist |
| Instagram | 1080x1350 | The feeling: a day with Piblo in four beats (talk, remember, remind, "leave 10 minutes early"), Buddy-led, warm | Link in bio |
| LinkedIn | 1200x627 | The credibility: problem, solution, verified proof points only (open source, no subscription, your data stays yours, any AI) | Follow and join the waitlist |

`CAPTIONS.md`: per platform a caption (X up to 280 characters; Instagram with 5-8 relevant tags; LinkedIn three short paragraphs), alt text and one follow-up comment. **Open and look at each PNG**; check legibility at 25% zoom, no cut-off text, no banned content, concept label present.

**6. Kickstarter pack** in `launch/`: page draft, Standard vs Pro, rewards, a **community-voted stretch ladder** (free software upgrades for everyone, paid add-on unlocks, backer-count goals, backer votes; draft order is in `docs/PRODUCT-SPEC.md`), honest risks and challenges, a FAQ that answers the complaints in `docs/kickstarter/HERMES-HANDOVER-COMPETITORS-2026-11-09.md`, rewards that will definitely ship, and a "what you need" box (Piblo, Windows PC, Wi-Fi, no subscription). Include a day-one plan and a mid-campaign plateau plan.

**7. Free Piblo for PC beta pack.** Package the host-side wins (voice typing, Park it / Where was I?, Private mode) so waitlist members can really use them before launch: installer or clear setup steps, a one-page guide, a feedback form that feeds `ideas-and-votes`. Prepare it fully; releasing it is Maz's call.

**8. `MAZ-ACTIONS.md`**: ordered by launch impact: filming the three clips, joining and opening Discord, approving the beta release, supplier and M5Stack quotes, compliance, accountant, five outsider setup tests, real photos, choosing the goal, and the launch gates in `docs/kickstarter/GATES.md`. Update the 8 Nov readiness verdict honestly.

### Phase 5: the Fable pass
Review every merged change end to end, as a user would. Fix rough edges, unify wording and sounds (soft warm chimes, soft clicks), make sure every feature feels like one product. Rerun all tests and the 10-turn voice script.

## Done means

- All automated tests green; voice evidence shows before/after numbers; median first audio about 1 s or better; typing never triggers a turn; persona tests pass.
- Each Phase 3 feature has at least one test and a short demo line in the PR.
- Feature branches, PRs with evidence, merged when green (host changes only; firmware waits for Maz's OK and listen test).
- `docs/PRODUCT-SPEC.md` and `docs/NEXT-4-WEEKS.md` updated with what is done.
- Deliverables A to M all present or explicitly logged as blocked with the reason.
- `piblo-private` passes the 5-minute test: a new agent opens only `README.md`, `AGENTS.md` and `NOW.md` and can say what to do next.
- Handover written to `unified-memory-database` (`projects/piblo/STATUS.md` and `handoffs/LATEST.md`) so another agent resumes cold.

## Report to Maz (5 short bullets max)

What now works (in plain words), the numbers, PR links, the private repo and the first infographics (links and file paths), the launch verdict (Red/Amber/Green) with the top 3 blockers, what needs his hands or ears (flash OK, listen test, phone permissions, filming, Discord, the beta release), and the next step.
