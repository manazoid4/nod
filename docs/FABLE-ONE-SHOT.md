# Fable one-shot: make Piblo voice great and genuinely useful

Paste everything below the line into a single Fable session. Fable runs it start to finish.

---

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
5. **Catch me up**: a 2-minute spoken summary from notifications, calendar and saves; ends with "everything else can wait"; learns what to skip.
6. **Send it to Piblo**: Android share target -> captions first, local Whisper, small free/local model summary (target a few hundred tokens), filed into `library.py`; resurfaces saves when relevant.
7. **First three minutes** onboarding and **Buddy forms** (Seed, Monk, Tinkerer, Explorer, Night Owl, Sunny; each = pixel art + one rule).
8. **MCP connections** for Gmail, Calendar, Notion, GitHub, Hermes (use existing MCP servers).
9. **Teach Demo, refined** ("show me once"): the recording side already exists (device CAPTURE -> TEACH DEMO; `teach_capture.py`: screen + mic via ffmpeg, M marks, transcription, scene frames). Add the missing half: turn a recording into a reusable skill/agent (steps written in plain words from transcript + marks + frames), read it back for the user to confirm, then run it next time under the safety levels (computer actions always "ask on Piblo" until the user loosens it). Recordings stay local; offer pause and delete; never keep passwords visible in saved frames. Feeds the learning loop.

If the four weeks cannot fit everything, finish in this order and stop cleanly; never leave half-wired features.

### Phase 4: the Fable pass
Review every merged change end to end, as a user would. Fix rough edges, unify wording and sounds (soft warm chimes, soft clicks), make sure every feature feels like one product. Rerun all tests and the 10-turn voice script.

## Done means

- All automated tests green; voice evidence shows before/after numbers; median first audio about 1 s or better; typing never triggers a turn; persona tests pass.
- Each Phase 3 feature has at least one test and a short demo line in the PR.
- Feature branches, PRs with evidence, merged when green (host changes only; firmware waits for Maz's OK and listen test).
- `docs/PRODUCT-SPEC.md` and `docs/NEXT-4-WEEKS.md` updated with what is done.

## Report to Maz (5 short bullets max)

What now works (in plain words), the numbers, PR links, what needs his hands or ears (flash OK, listen test, phone permissions), and the next step.
