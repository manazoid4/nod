# Voice sprint brief: make Piblo's voice feel GPT-Live level

Paste everything below the line into the agent that will do the work.

---

You are the voice engineer for **Piblo**, a small calm device you talk to like a person (repo: `github.com/manazoid4/piblo`, Windows PC, Maz is the owner). Your one job tonight: make live conversation on the real device feel as good as ChatGPT's voice mode, **by improving what already exists**. Do not start a new voice stack.

## Read first (15 minutes, no code yet)

1. `docs/PRODUCT-SPEC.md` (what Piblo is) and `docs/NEXT-4-WEEKS.md` (rules).
2. `AGENTS.md`: how to see and drive the real device with `python scripts/piblo_remote.py` (status, screen, keys, open). Look at screenshots before claiming anything works.
3. `docs/LIVE-VOICE-PROTOCOL.md`: the wire contract between device and Core. Do not change it without saying so in the PR.
4. `host/mazhost/live_voice.py`: device <-> Core <-> llama-server realtime bridge. Core does the turn detection (llama.cpp has no VAD).
5. `host/mazhost/live_brain.py`: LFM3 hears and speaks; a cloud model can think (OpenRouter -> Ollama -> LFM3 fallback); noise filter, voice commands, memory context, sentence cutting.
6. `host/mazhost/config.py`: live settings, especially `live_end_silence_ms` (450), `live_mic_gain` (10.0), `live_listen_holdoff_ms` (600), brain mode.
7. Tests: `host/tests/test_live_voice.py`, `test_fastvoice.py`, `test_device_live.py`, `test_voices.py`.
8. Open PR #75 (speaker clarity: M5Unified 0.2.20 + live jitter fix). It needs a listen test on the device.

Write down, in `docs/VOICE-SETUP.md`, the exact model file, llama-server build and start command currently used, so anyone can reproduce the setup. If you cannot find them on this PC, ask Maz.

## Target (from Maz)

In priority order:
1. **Speed and accuracy.** First audio of the reply starts in about 1 second or less after you stop talking. It understands what you said, including mumbling, background noise and changing your mind mid-sentence.
2. **Perfect timing.** Never cuts you off mid-thought; never leaves an awkward silence.
3. **Interrupt by just talking.** It stops speaking when you talk over it. The mic key also stops it instantly.
4. **Human sound.** Natural voice, including small breaths, not a reading voice.
5. **Remembers.** "Like I said yesterday..." works across sessions.
6. **When unsure, a short check-back** ("Call Mum or call Tom?"), only when it matters, mainly before actions.

Out of scope tonight: emotion matching, new hardware, buying anything, redesigning the protocol.

## Decisions already made (do not reopen)

- Keep the all-in-one **Liquid ~2B omni model** Maz tested (natural voice). Add a dedicated speech-to-text model only where you prove the omni model fails.
- Agent-agnostic and model-agnostic: any brain via OpenRouter or local; free models first; nothing paid without Maz's OK.
- Borrow before building. Pipecat (`pipecat-ai/pipecat`, BSD-2: Silero VAD, smart turn detection, interruption handling) is the first place to look for turn-taking and barge-in code. Check every licence. **No AGPL code in Piblo.**
- Flashing firmware needs Maz's explicit OK every time. Ask before flashing.

## Plan

1. **Baseline (no changes).** Run the current live voice on the device and measure, 10 turns each:
   - time from end of speech to first reply audio (log it in Core);
   - false turn ends (cut you off), missed turn ends (silence);
   - interruptions that worked vs failed;
   - word accuracy on the test script below.
   Save numbers to `docs/evidence/voice-<date>/baseline.md`.
2. **Biggest win first.** Fix the worst measured number. Likely candidates, check in this order:
   - Turn detection: replace or tune the fixed 450 ms silence rule with a VAD plus a smarter end-of-turn check (Pipecat's smart-turn or Silero VAD).
   - Latency: stream the first clause to TTS as early as possible (`first_clause` already exists), keep the model warm, check resampling and buffering cost.
   - Barge-in: echo from the speaker next to the mic. Compare the existing holdoff approach with echo cancellation or speaker-reference gating; keep whichever measures better.
   - Accuracy: mic gain and noise filter tuning; only then consider a dedicated STT fallback.
3. **One change at a time.** After each change, rerun the same 10-turn test. Keep a change only if it measurably improves the target and does not break the others.
4. **Memory and check-back.** Confirm cross-session memory works in live voice; add the short check-back for uncertain action requests.
5. **Regression tests.** Add unit tests for any new logic (turn detection decisions, barge-in state, check-back trigger). Run `python -m pytest host/tests -q` and keep it green.

## Test script (read aloud, 10 turns)

1. "Hey Piblo, what's on today?"
2. Mumble: "uh can you, um, remind me to, to call Mum later"
3. With TV or music in the background: "What time is it?"
4. Change of mind: "Set a timer for ten, no, fifteen minutes."
5. Long pause mid-sentence: "I need to... (2 seconds) ...buy milk."
6. Interrupt Piblo halfway through a long answer: "Stop, actually tell me the weather."
7. "Like I said yesterday, what was the thing I forgot?"
8. Ambiguous action: "Message Tom" (should check back if unsure).
9. Fast talker: one long run-on sentence with three requests.
10. Quiet voice from 1 metre away.

## Done means

- Measured before and after numbers in `docs/evidence/voice-<date>/`.
- First audio about 1 second or less on most turns; no cut-offs on turns 2 and 5; interruption works on turn 6; turn 8 checks back.
- `docs/VOICE-SETUP.md` lets anyone reproduce the setup.
- Tests green; a PR on a feature branch with the numbers in the description. Do not merge firmware changes without Maz's listen test.

## Report to Maz (5 short bullets max)

What changed, the before/after numbers, the PR link, anything that needs his ears or hands (listen test, flash OK), the next step.
