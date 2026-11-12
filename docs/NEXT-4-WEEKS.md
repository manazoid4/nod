# Next 4 weeks (to about 8 Dec 2026)

Spec: `docs/PRODUCT-SPEC.md`. This file is the work list. It can change; update it rather than starting over.

## Done means

1. Site and Kickstarter page ready (site is the main call to action, linked with Instagram and Discord).
2. GPT-Live-style voice working on the device.
3. Memory (local-first, linked notes).
4. Agent builder ("ask Piblo to make an agent").
5. First-three-minutes flow and Buddy forms.

## Rules for every agent

- **Build on what exists.** Read the repo, open PRs, `docs/`, and the ledger before writing code. Do not re-engineer working parts.
- **Borrow before building.** Prefer permissively licensed GitHub code (MIT, BSD, Apache). Check licences; no AGPL code inside Piblo.
- **Spending:** strict cap; nothing is bought without Maz's explicit OK. Free models and free tiers first.
- One lead agent plus 2-3 helpers on separate lanes: engine, voice, site/brand. The lead merges and checks.
- Flashing firmware needs Maz's OK every time.

## First task: finish the voice

Start from:
- `host/mazhost/live_voice.py` (realtime voice bridge to the local omni model via llama-server).
- PR #75 (clearer speaker playback, live jitter fix): needs a listen test.
- The Liquid ~2B omni model Maz tested: keep it as the default unless something is clearly better.
- Pipecat (pipecat-ai/pipecat, BSD-2) for turn-taking, interruption and VAD; it has an ESP32 client.

Target: replies start in about a second, interrupt by just talking, natural voice, remembers earlier conversations.

Write down the exact model file and server command used, so anyone can reproduce it.
