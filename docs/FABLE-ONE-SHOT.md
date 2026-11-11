# Fable one-shot: finish Piblo as far as honestly possible, toward a world-class Kickstarter

Paste everything below the line into a single Fable session. Fable runs it start to finish.

---

## Session goal (read this first)

Get Piblo as close to launch-ready as one session honestly can, and leave Maz with **3 platform-specific infographics** (X, Instagram, LinkedIn). Voice, Ask on Piblo, voice typing, Where was I? and provable privacy are the product proof the campaign stands on. You cannot launch, post, spend, flash firmware or invent proof; anything needing hardware, outsiders, suppliers or lawyers goes on Maz's action list instead of being faked.

**Deliverables (the session is judged on these):**

| # | Deliverable | Done means |
|---|---|---|
| A | Ask on Piblo (host side) | Tests pass; one 3-line demo script |
| B | Voice typing | Tests pass; works offline |
| C | Park it / Where was I? | Tests pass; survives restart |
| D | Private mode + "How your data stays yours" page | Leak test fails on any non-local request; page text matches what the code enforces |
| E | Voice before/after numbers | Evidence in `docs/evidence/voice-<date>/` |
| F | `piblo-private` repo + ranked project-scan list | List has feature, code location, licence, port effort |
| G | Site wording audit | Tests green, 390 px and 1440 px checked |
| H | Kickstarter pack (Phase 4) | Campaign page draft, FAQ, honest risks, 14-day pre-launch calendar |
| I | 3 infographics + captions (Phase 4) | Rendered PNGs viewed and checked |
| J | `MAZ-ACTIONS.md` | One page: what only Maz can do next, ordered by launch impact |

## Run mode: one shot, unattended

Why this matters: Maz has a separate usage limit just for Fable and wants this whole job done in one run. He is not watching. Your first message back is his first look at any of it.

- **Resume first.** If `docs/evidence/CHECKPOINT.md` exists, read it and continue from it instead of starting over. A bare "continue" from Maz means exactly that.
- **Pre-flight, then no more stops.** Before any building, ask Maz at most 5 easy questions, one at a time (2-4 vivid options, recommendation first, only things only he knows, e.g. goal feel, founder story, first clip he can film). If he does not answer, use your recommended option and mark it `[MAZ]`. After pre-flight, run to the end. Pause only for something destructive or irreversible, a real scope change, or input only Maz can give (flash OK, spending, posting, listening tests). Then ask and end the turn; do not end on a promise.
- **When you have enough information to act, act.** Do not re-derive settled facts, re-litigate Maz's decisions, or narrate options you will not pursue. Give a recommendation, not a survey.
- **Do the simplest thing that works well.** No extra features, refactors, abstractions, fallbacks for cases that cannot happen, or designs for hypothetical futures. Build on what exists.
- **Protect the Fable limit.** Fable's own tokens go to planning, briefs, review, the verifier decisions and the final pass. Bulk building, scanning and drafting go to Opus, Sonnet and free-model helpers. Keep long-lived helpers (they keep their context and cost less than fresh ones) and talk to them asynchronously; do not block on the slowest one.
- **The builder never grades itself.** For every deliverable A to J, a separate fresh-context verifier (Opus or Sonnet) checks the real output against the "done means" column: the running tests, the actual rendered PNGs, the actual page at 390 px and 1440 px. It tries to prove the work fails. You decide on its report.
- **Your last message is a re-grounding, not a continuation.** Outcome first in one sentence, then the one or two things Maz must do, in plain full sentences with no working shorthand, arrow chains or labels you invented. Do not reproduce your reasoning in the response.

## Usage guard (Maz's weekly usage was at 96% on 11 Nov)

- You read at most 10 files yourself; helpers summarise the rest. Never re-read a file you already have.
- Put detail in files; chat replies stay short.
- Write a 10-line checkpoint to `docs/evidence/CHECKPOINT.md` after each phase so a cut-off session resumes without repeating work.
- Max 2 fix rounds on any single item, then log it and move on. No extra polish loops, no new strategy documents.
- If the Fable limit hits mid-run, the checkpoint must be good enough for any model or a later Fable session to resume cleanly. Finish in the order of the deliverables table (A to J). Never leave a feature half-wired.
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

## Also: two setup jobs

- **Private repo.** Create a new **private** GitHub repo `manazoid4/piblo-private` for anything that must not be public: prices and margins, budget, supplier quotes, Kickstarter internals, business plans. Move nothing secret into the public repo; link to the private repo from your report only.
- **Full project scan.** Scan all of Maz's GitHub repos (`gh repo list manazoid4 --limit 300`, then README, recent PRs and branches of the relevant ones; use free models for the scan). Many projects are unfinished but contain finished work (e.g. Recall/Feed Vault, maz-pocket, nod, agent-nudge, mazos-ui, hermes job hunter, khutba-io). Find features that already exist elsewhere and could become Piblo features cheaply. Output a short ranked list in `piblo-private` (feature, where the code is, licence, effort to port), and port only items that fit the top priorities.

## The work, in order

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

### Phase 4: Kickstarter pack and 3 infographics (Sonnet drafts, you judge)
Rules: product is Piblo; "UK" only for location; **no prices, chip names, RAM figures or dates in public copy or graphics** (prices in the campaign draft are `[MAZ]` placeholders); label every illustration "concept" until a real photo exists; claim only what the code and tests prove ("in testing" stays "in testing"); no fake scarcity, backer counts or testimonials. Lead with the solution, not "AI". Do not lead with "approve Claude's actions plus a pet": Anthropic's Desktop Buddy already does that. Lead with: remembers you, reminds you, voice typing, any AI, no subscription, your data stays yours.

- **Campaign pack** in `piblo-private` (it holds prices): page draft, Standard vs Pro, rewards and stretch goals from the spec, risks and challenges (honest), FAQ answering the complaints in `docs/kickstarter/HERMES-HANDOVER-COMPETITORS-2026-11-09.md`, 60-90 s video script and shot list matching `docs/launch/real-footage-shotlist.md`, 14-day pre-launch calendar.
- **Infographics**: three different pieces, not three resizes. Build as HTML in `media/marketing/` with the existing `brand.css` and `render.mjs`, export PNG at 2x, one idea each, about 40 words max, readable at phone size, CTA is piblo.co.uk only.

| Platform | Size | Angle | CTA |
|---|---|---|---|
| X | 1600x900 | The hook: "Say it once. Piblo handles the rest." Before/after of scattered reminders versus one calm device | Join the waitlist |
| Instagram | 1080x1350 | The feeling: a day with Piblo in four beats (talk, remember, remind, "leave 10 minutes early"), Buddy-led, warm | Link in bio |
| LinkedIn | 1200x627 | The credibility: problem, solution, verified proof points only (open source, no subscription, your data stays yours, any AI) | Follow and join the waitlist |

  Write `CAPTIONS.md`: per platform a caption (X up to 280 characters; Instagram with 5-8 relevant tags; LinkedIn three short paragraphs), alt text, and one follow-up comment. **Open and look at each PNG**, check legibility at 25% zoom, no cut-off text, no banned content, concept label present.
- **`MAZ-ACTIONS.md`**: ordered by launch impact: uncut demo footage, supplier and M5Stack quotes, compliance, accountant, five outsider setup tests, real photos, and the launch gates in `docs/kickstarter/GATES.md`. Update the 8 Nov readiness verdict honestly.
- Ask Maz at most 5 easy questions, one at a time (2-4 vivid options, recommendation first), and keep working while waiting.

### Phase 5: the Fable pass
Review every merged change end to end, as a user would. Fix rough edges, unify wording and sounds (soft warm chimes, soft clicks), make sure every feature feels like one product. Rerun all tests and the 10-turn voice script.

## Done means

- All automated tests green; voice evidence shows before/after numbers; median first audio about 1 s or better; typing never triggers a turn; persona tests pass.
- Each Phase 3 feature has at least one test and a short demo line in the PR.
- Feature branches, PRs with evidence, merged when green (host changes only; firmware waits for Maz's OK and listen test).
- `docs/PRODUCT-SPEC.md` and `docs/NEXT-4-WEEKS.md` updated with what is done.
- Deliverables A to J all present or explicitly logged as blocked with the reason.
- Handover written to `unified-memory-database` (`projects/piblo/STATUS.md` and `handoffs/LATEST.md`) so another agent resumes cold.

## Report to Maz (5 short bullets max)

What now works (in plain words), the numbers, PR links, the infographics (file paths), the launch verdict (Red/Amber/Green) with the top 3 blockers, what needs his hands or ears (flash OK, listen test, phone permissions, filming), and the next step.
