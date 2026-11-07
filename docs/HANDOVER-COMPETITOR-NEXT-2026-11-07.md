# Nod handover for orchestrator — competitor analysis + next stages

**Prepared:** 7 Nov 2026 (Hermes) · **For:** Claude (orchestrating multi-agent Nod workflow)
**Branch of truth:** `recover/nod-v1.0.2` · **Repo:** github.com/manazoid4/nod (public — no secrets/IPs/SSIDs)

---

## 1. Where Nod is RIGHT NOW (verified this session)

CI status checked live via `gh pr checks` — all four real PRs are **green**:

| PR | Branch | What | CI |
|---|---|---|---|
| #16 | `recover/nod-v1.0.2` | Recover v1.0.2 (the build on the device) into Nod | ✅ both build jobs pass |
| #17 | `fw/talk-circle-home` | Port PR #15 + big talk-circle Home | ✅ build pass |
| #18 | `site/two-concepts` | Concept A live as the site | ✅ build + source-contract pass |
| #19 | `core/desktop-app` | Electron Nod Core app (draft) | ✅ build pass |
| #15 | `maz/loving-keller-s71uz3` | **[DO NOT MERGE]** consumer Home/site/film built on old v0.8.0 base | legacy — superseded by #17 |

**Action:** PR #16 is green and was the gate for the whole recovery. Merge #16 first, then review #17/#18/#19 against it. Close #15 after #17 lands (it's built on the wrong base).

Decisions already locked by Maz (do not re-litigate):
- Brand = **Concept A "Toy-shop warm"** (cream, mint, tomato-orange, sun-yellow) — `design/tokens-a.css`.
- Windows app = **Electron + tray + onboarding over the existing Python Core** (not a browser page).
- Device Home = **big colourful talk circle**; voice must feel live (ChatGPT/Claude-like).
- **Borrow from NucleoOS** (r/CardPuter, v0.7.3) — licence check first, credit it: first-boot installer w/ SHA-256+resume, "Back to M5Launcher", device-served web page.
- **The concept mockups are NOT accurate to the real Cardputer ADV** (240x135 screen above 4x14 keyboard, USB-C, speaker grille). Use real photos / correct geometry; keep "Concept" label until real photos exist.

---

## 2. Competitor complaints → Nod's edge (research, 7 Nov)

Pattern across every competitor: complaints trace to **five root causes** — and Nod already counters each. Build marketing and roadmap around these.

| Root complaint | Who suffers it | Nod's counter |
|---|---|---|
| **Subscription lock-in** | Plaud ($240/yr), Wispr Flow ($15/mo), Rabbit/Humane (mandatory sub), Pocket AI | Free models (Groq STT, free LLM, local Kokoro TTS). No subscription. |
| **Cloud/privacy dependence** | Pocket AI ("complete security failure" thread), Wispr Flow (past privacy episode), Kode Dot (Gemini-only) | Local STT (faster-whisper 0.37s) + local Kokoro TTS + fail-closed approvals. Open source. |
| **"Why isn't this an app" / replaces your phone** | Rabbit R1 ($199), Humane Pin ($699) | Augments your existing phone/PC — one-key approve/capture, not a phone replacement. |
| **Gadget you shelf, not a daily tool** | Kode Dot (hacker multitool), Codex Micro (desk-bound, Codex-only) | Daily-driver habit: talk, capture, approve your agents from your pocket. |
| **Bad power/battery** | Kode Dot (500mAh), Codex Micro (wired desk), Pocket AI (no battery indicator) | Power lane below: deep sleep + battery gauge + efficient audio. |

**Specific named competitors:**
- **Kode Dot** (ESP32-S3, $~, 2.13" touchscreen, 500mAh, IR/NFC/RFID/GPIO, Gemini-only AI): positioned as Flipper-Zero-style *maker toy*. r/esp32 asks if it "hides too much" to learn on. It's a tinker gadget, not a voice sidekick — Nod wins on daily usefulness + open any-model AI.
- **Codex Micro** ($230): not plug-and-play, sold out, Codex-only, desk-bound. Nod: pocket, any agent, ~$79–119.
- **Plaud Note / Pocket AI**: subscription, no display (original Note), proprietary cable, dim light, noisy-room transcription. Nod: physical keys + screen, free, on-device.
- **Wispr Flow**: cloud-only, 2000 words/wk free, privacy episode. Nod Flow dictation: free, local.
- **Violoop** ($399): closed, screen-grabbing, phone approvals. Nod: open, physical Y/N key.

---

## 3. Maz's new ideas → three feature lanes (next stages)

### Lane A — Provider abstraction: OpenAI / OpenRouter endpoints (Core)
**Why:** unlock ChatGPT-quality voice + any-model freedom, kill cloud lock-in complaints.
**Do:** in `host/mazhost/` (`llm.py`, `config.py`, `tts.py`, `stt.py`) add a clean OpenAI-compatible provider layer: `base_url` + `api_key` + model id → works for OpenAI, OpenRouter, Gemini, Groq, local Ollama/LM Studio/Kokoro-FastAPI (already `/v1/audio/speech` compatible).
- Priority: streaming TTS via OpenRouter `/api/v1/audio/speech` + streaming chat (voice research doc recommends this; Fish is the current 3.4s bottleneck).
- Acceptance: one `.env` swap moves the whole voice path between `kokoro` (local) ↔ `openai` ↔ `openrouter` without code changes; timed first-audio logged.

### Lane B — Board HAL: multiple ESP32 targets (firmware)
**Why:** Maz wants more boards; codebase already has experimental display profiles (240x135 Cardputer, 480x320 template).
**Do:** introduce a thin board abstraction (screen size/resolution, key matrix, IMU presence, battery). Target list: Cardputer ADV (240x135), M5Stack CoreS3, StickC Plus2, AtomS3, ESP32-S3-BOX, T-Display S3. Keep one `src/apps/nod_home.cpp` rendering against the HAL, not hardcoded pixels.
- Acceptance: `pio run -e` green for ≥2 boards; Home renders correctly at both resolutions (screenshot evidence); no feature regression on Cardputer.

### Lane C — Power: battery + low-power wake (firmware)
**Why:** direct answer to the "500mAh / no battery gauge" competitor complaints; better-than-Kode power story.
**Do:** deep-sleep between interactions, battery % on Home via `charge_monitor`, wake-on-key + optional wake-word, efficient audio (stream PCM, no full-WAV round-trips). 
- Acceptance: idle current measured (mA) before/after; battery % correct vs multimeter; wake from sleep <1s on key press.

---

## 4. Recommended order for the multi-agent workflow

1. **Merge #16** (green, unblocks everything). Close #15 after #17 lands.
2. **Voice-first** (Lane A, Option A from `docs/evidence/VOICE-RESEARCH-2026-11.md`): local Kokoro streaming + LLM sentence streaming + chunked PCM. This is the single biggest "feels like ChatGPT" win and it's £0. Do the 3 × 15-min decision tests first (headphones test, Kokoro first-byte on GTX 1660 Ti, one HeyGen-free latency test).
3. **Board HAL** (Lane B) in parallel with **Power** (Lane C) — one firmware agent, one test agent.
4. **Replace inaccurate device imagery** (real Cardputer photos) + finish Concept A site (#18).
5. **NucleoOS-style installer** ideas (after licence check).

**Worker split suggestion:** Agent 1 = Core/voice (Lane A) · Agent 2 = firmware HAL+power (Lanes B+C) · Agent 3 = site/imagery + NucleoOS licence audit. Three agents, one reviewer each; never two leads on one lane.

---

## 5. Do not
- Commit secrets/IPs/SSIDs (repo is public). Mark firmware features green without device proof. Flash without M5Launcher rollback. Present stylised mockups as the real device. Open a new PR while >5 open.

## 6. Definition of done (each stage)
CI green **and** screenshots/device evidence, not "built". Update `NOD_STATUS.md` and Notion "Nod · Mission Control" after each verified milestone.
