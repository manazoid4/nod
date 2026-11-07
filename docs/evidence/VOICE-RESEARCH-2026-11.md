# Nod voice: making it feel live (research, 7 Nov 2026)

No code changed. Sources are linked inline. Items marked UNVERIFIED are my estimates or rest on a single secondary source.

## 0. What exists in the repo today (read from `origin/integrate/nod-voice-host-20261011`)
- `host/mazhost/speakplan.py`: `SpeakPlanner` splits the reply into sentences and synthesises them in parallel on a 4-thread pool. The device fetches each with `GET /speak?id=..&part=N`. So the reply is sentence-chunked, but each sentence is a whole WAV, fetched over HTTP. Nothing streams bytes.
- `host/mazhost/tts.py`: providers `fish` (cloud), `kokoro` (`kokoro_onnx`, in-process) and `windows`. The default is `fish`. Kokoro is wired but has not been measured. `kokoro_onnx` runs on CPU unless `onnxruntime-gpu` is installed.
- `host/mazhost/stt.py`: local faster-whisper. 0.37 s measured, fine.
- Firmware `src/audio/voice.cpp`: ping-pong buffers into `M5.Speaker.playRaw`, so it can already play while downloading. Barge-in and full duplex are not in the audio path.
- The measured 4.4 s to first audio breaks down as upload 1.26 + STT 0.37 + LLM 0.6 + TTS 3.4 (Fish via OpenRouter/cloud, not streamed). TTS is about 75% of the wait. The weak Wi-Fi upload is about 25%.

## 1. Is the Cardputer ADV good enough?
Verdict: yes for push-to-talk conversation, no for hands-free full-duplex (see the speaker/mic caveat below).

Specs ([M5Stack docs](https://docs.m5stack.com/en/core/Cardputer-Adv)):
- ESP32-S3FN8 at 240 MHz, 8 MB flash. The chip name implies no PSRAM (my inference). One secondary site claims 8 MB PSRAM, which conflicts. Either way, stream audio in small chunks.
- ES8311 codec, MEMS mic with 65 dB SNR, NS4150B amp, 8 ohm 1 W speaker.
- 3.5 mm jack on the side. Inserting a plug disables the speaker amp automatically ([M5 docs](https://docs.m5stack.com/en/core/Cardputer-Adv), [review](https://techonlinuxstuff.wordpress.com/2026/07/09/m5stack-cardputer-adv-review-the-pocket-esp32-s3-computer-just-got-serious-upgrades/)).
- A [YouTube test](https://www.youtube.com/watch?v=WGvPaLOEGOI) confirms the jack switches output. A [Make: review](https://makezine.com/article/technology/microcontrollers/review-m5stack-cardputer-adv-version-esp32-s3/) exists. I found no published voice-assistant benchmarks. The quality verdict below is engineering inference, not community measurement.

What to expect:
- Mic: 65 dB SNR is decent for 16 kHz speech held close, and STT at 0.37 s worked. With the mic a few cm from a keyboard and a 1 W speaker in a 19 mm case, expect echo and speaker-to-mic feedback. This is the main reason full duplex is a bad fit without headphones.
- Speaker: a 1 W driver in a tiny cavity has little bass and rolls off hard below about 400 Hz. Any voice sounds thin, and that adds to "robotic". So part of the "unnatural" complaint is the hardware, not only the TTS. Test by playing the same WAV through the jack into headphones. If it sounds natural there, the voice is fine and the speaker is the limit.
- Cheap upgrades:
  1. Headphones or a small powered speaker on the 3.5 mm jack (about £5-10). Biggest quality gain, and it also lets you do hands-free later without echo.
  2. A Bluetooth speaker on the PC instead of the device. Core already runs on the PC, so replying through PC speakers costs nothing.
  3. Output EQ in Core: high-pass at about 300 Hz, a gentle boost at 1-3 kHz, a limiter, and a lower playback gain to avoid amp clipping. A few lines of numpy/scipy, free.
  4. A Grove I2S speaker/amp is possible (Grove port is G1/G2) but needs firmware work. Not worth it before trying the jack.

## 2. Options landscape (as of Nov 2026)

### OpenRouter (the owner asked for this)
- Dedicated endpoints exist: `/api/v1/audio/speech` (TTS) and `/api/v1/audio/transcriptions` (STT: Whisper, GPT-4o Transcribe, Chirp 3, Groq Whisper). TTS providers: OpenAI GPT-4o Mini TTS, Gemini Flash TTS, Mistral Voxtral Mini TTS ([announcement](https://openrouter.ai/blog/announcements/announcing-audio-apis/)).
- Audio-in/audio-out chat models exist via `/chat/completions` with `modalities: ["text","audio"]` and `stream: true` ([docs](https://openrouter.ai/docs/guides/overview/multimodal/audio)). These are paid and not a true duplex "realtime" session.
- There is no realtime WebSocket (speech-to-speech) API on OpenRouter that I could find. For true realtime you go direct to OpenAI or Google.
- Free voice models: the roster lists `fish-audio/s2.1-pro-free:free` and `heygen/heygen-voice-1-turbo:free` as free speech models ([tracker, 6 Nov](https://klymentiev.com/blog/openrouter-free-tier)). Fish is what you already use. OpenRouter's own page says it has no public standard endpoint ([model page](https://openrouter.ai/fish-audio/s2.1-pro-free:free)). It returns raw MP3/PCM bytes, so streaming the response body is possible but your measurement of 3.4 s first byte says it is not low latency. HeyGen Turbo free is UNVERIFIED; worth one 5-minute test.
- Free limits: 20 requests/min, 50/day (1,000/day after a one-off $10 credit purchase). Providers 429 often. Free tier is not dependable for a voice product.

### OpenAI Realtime
- gpt-realtime-2.1 costs $32/1M audio input tokens and $64/1M audio output tokens (mini: $10 and $20), roughly $0.02-0.11 per minute ([Fora Soft](https://www.forasoft.com/blog/article/openai-realtime-api-pricing)). Best-in-class duplex and barge-in. About 10 minutes of talk a day is roughly £3-15/month depending on model and caching. Over budget for the £5 target unless used lightly (the mini model fits).

### Gemini Live API (the one free speech-to-speech option)
- Free tier lists Gemini Live, Flash TTS and Transcribe as free of charge ([summary, 22 Oct](https://dev.to/hassann/gemini-api-free-tier-in-2026-limits-models-and-when-you-get-billed-4081)). Google no longer publishes per-model numbers. Check the limits in your own AI Studio project.
- It is a stateful WebSocket with native audio in and out, VAD and barge-in; claims latency under 500 ms ([tutorial](https://eastondev.com/blog/en/posts/ai/20260227-gemini-live-api-tutorial/)). Audio-only sessions are limited to 15 minutes without compression ([session docs](https://ai.google.dev/gemini-api/docs/live-api/session-management)). The API is in preview.
- Catches: free-tier prompts and audio can be used by Google and read by human reviewers. For UK/EEA users, Google says only Paid Services may be used when making API clients available to users. A personal device for Maz is fine; do not ship it to customers on a free key. It also replaces the Core LLM, so Nod's own brain and tools would need to go through Gemini function-calling.

### Groq
- Whisper STT is fast, and Groq is available as an OpenRouter transcription provider. Not needed since local STT is 0.37 s.
- PlayAI TTS was retired on 31 Dec 2025 and replaced by Orpheus ([notice](https://referencesource.org/ai-model-deprecation-and-retirement/playai-tts/)). The free Orpheus limits are 10 RPM, 100 requests/day and 3,600 tokens/day ([listing](https://horizonlux.com/tools/ai-models/free/groq-canopylabs-orpheus-v1-english)). That is only a few dozen replies a day. Preview, and Groq's terms say not for consumer use. Fine as a tester, not as the backbone.

### Paid streaming TTS (fast but not free)
- First-audio medians: ElevenLabs Flash v2.5 about 190 ms, Cartesia Sonic 3.6 about 290 ms, OpenAI TTS over 2 s ([Fora Soft/Coval, Oct 2026](https://www.forasoft.com/learn/ai-for-video-engineering/articles-ai/streaming-tts-kokoro-elevenlabs-turbo-openai-tts)). Other benchmark sites quote 85-135 ms TTFB ([voiceaibench](https://voiceaibench.com/)); treat the numbers as a ballpark.
- Price per 1M characters: ElevenLabs Flash about $50, Cartesia and Deepgram Aura-2 about $30 ([comparison](https://www.nineninesix.ai/blog/tts-api-pricing-comparison-2026)). At about 300 characters per reply and 100 replies/month that is about 30k characters = $1-1.5. Real cost is the plan minimum, not usage. Free-tier allowances (ElevenLabs ~10k credits/month, Cartesia, Deepgram credit) are UNVERIFIED; check before relying on them.

### Local on the GTX 1660 Ti PC
- Kokoro-82M: Kokoro-FastAPI reports about 300 ms streaming first audio on GPU, ~3 GB VRAM, OpenAI-compatible `/v1/audio/speech` with chunked streaming ([repo](https://github.com/remsky/Kokoro-FastAPI), [article](https://localaimaster.com/blog/local-tts-api-server-kokoro-fastapi)). Under 1 s on an Apple M3 Pro CPU. A 1660 Ti (6 GB, no tensor cores) should do first audio in about 0.3-0.6 s for a short sentence. UNVERIFIED on this machine, but it is the cheapest experiment. Naturalness is clearly better than Windows SAPI/Piper and is the best free open voice for its size. It is still a step below ElevenLabs/ChatGPT voice, with flatter emotion.
- Piper: very fast on CPU, slightly more robotic than Kokoro. A good fallback.
- Orpheus 3B (local): more expressive, but about 3B parameters will not stream in real time on 6 GB VRAM. Skip.

## 3. Recommended architecture

Where the time goes: ChatGPT-style "live" feel needs first audio under about 1.5 s and the ability to interrupt. Push-to-talk can reach the first; true duplex is the second and is not worth it on this hardware without headphones.

### Option A (recommended): local streaming pipeline, Kokoro on GPU, token-streamed sentences
Latency budget: upload about 0 (stream the mic while held) + STT 0.3 (run STT when button is released, or partial) + LLM first sentence 0.4 + Kokoro first chunk 0.3-0.5 = about 1.0-1.3 s. Cost: £0.

Core changes:
1. Run Kokoro-FastAPI (Docker or the `kokoro-onnx` GPU build) as a local service. Change `tts.py` to stream the response body from `localhost:8880/v1/audio/speech?stream` (`response_format=pcm`) instead of writing a WAV per sentence.
2. Stream the LLM (`stream=true`) and cut on the first sentence boundary (`speakplan.split_sentences`). Start TTS on sentence 1 while the LLM is still generating sentence 2. This is the biggest single win after replacing Fish, since the LLM is only about 0.6 s total.
3. Replace `GET /speak?part=N` with one chunked HTTP response (or WebSocket) per turn that sends raw 16/24 kHz mono PCM as it arrives. Keep sentence order. This removes per-sentence request overhead on weak Wi-Fi.
4. Keep Fish as a fallback only (already the configured fallback logic).
5. Add output EQ/limiter (see section 1) in the PCM path.
6. Warm Kokoro and Whisper on Core start; keep the model resident.

Firmware changes (small):
- Play PCM from a chunked response as it arrives. `voice.cpp` already ping-pongs buffers, so mostly swap the source from "whole WAV file" to "socket stream".
- Upload: send mic PCM over a WebSocket or chunked POST while the key is held, so the 1.26 s upload overlaps with speaking. Core runs STT the moment the button is released.
- Optional barge-in: pressing the talk key during playback sends a "stop" and flushes the playback buffer. This is cheap half-duplex interrupt and needs no AEC.

### Option B: Gemini Live for a "real" ChatGPT-voice-mode feel (free, riskier)
Core becomes a WebSocket bridge: device mic PCM goes to Gemini Live, Gemini audio comes back, Core relays to the device. You get native speech-to-speech, sub-second response, VAD and server-side interruption for $0 on the free tier.
- Cost: £0 on the free tier for personal use. Data can be reviewed by Google. Not usable for customers in the UK on a free key.
- Effort: high. It replaces Core's STT/LLM/TTS path and your own LLM/tools. Preview API, 15-minute session limit, reconnect logic, echo control for hands-free use (headphones needed).
- Use it as an optional "Live mode" next to Option A, not as the only path.

### Option C: paid streaming TTS on the existing pipeline (ElevenLabs Flash or Cartesia)
Same changes as Option A, but the TTS is a streaming WebSocket call. First audio about 1.0-1.2 s total, the most natural voice, about £1-4/month at light use. Do this if Kokoro's voice is not good enough after listening to it through headphones.

## Ranked table

| Rank | Option | First-audio latency | Naturalness | Monthly cost | Effort |
|---|---|---|---|---|---|
| 1 | A. Local Kokoro (GPU) + LLM sentence streaming + chunked PCM to device | ~1.0-1.5 s (est.) | Good, not ChatGPT-level | £0 | Medium (Core ~2 days, firmware small) |
| 2 | C. Streaming paid TTS (ElevenLabs Flash / Cartesia) on same pipeline | ~1.0-1.3 s | Very good | ~£1-4 | Medium (same as A) |
| 3 | B. Gemini Live speech-to-speech (free tier) | ~0.5-1 s, with real barge-in | Very good | £0 (personal use only) | High |

OpenAI Realtime is excluded from the top 3 because it is about £3-15 or more per month; it is the benchmark for feel. OpenRouter has no realtime API and its free TTS (Fish) is what is slow today.

## Decision test before building (15 minutes each)
1. Play one Fish WAV and one Kokoro WAV through headphones into the jack. If both sound fine there, the speaker is the main problem and EQ/headphones fix most of the "robotic" complaint.
2. Run Kokoro-FastAPI on the 1660 Ti and time first byte for a 12-word sentence. Under 0.6 s means Option A is go.
3. Try `heygen/heygen-voice-1-turbo:free` once on OpenRouter for latency (UNVERIFIED).

## Not checked
- Real Kokoro first-byte on the GTX 1660 Ti (not measured here).
- Current free allowances for ElevenLabs, Cartesia and Deepgram (only paid pricing was confirmed).
- Gemini Live free-tier per-minute limits (Google no longer publishes them; read your AI Studio project).
- No hardware tests on the Cardputer were run; the speaker/mic judgements are inference from specs.
