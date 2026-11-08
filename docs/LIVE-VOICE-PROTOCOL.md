# Live voice protocol (device <-> Core)

Endpoint: `ws://<core>:8787/voice/live`. Auth: `Authorization: Bearer <token>` header, or `?token=<token>`.
Bad or missing token: Core accepts, then closes with code **4401**.

The device is a thin client. Core does turn detection (VAD), the model (LFM3-Omni realtime on llama-server)
and all resampling. The device is **half-duplex**: mic and speaker share one codec.

## Device -> Core

| Kind | Payload |
|------|---------|
| binary | PCM16 LE mono **16 kHz** mic audio, any frame size (about 40 ms = 1280 B) |
| text | `{"type":"hello","fw":"<ver>"}` once after connect |
| text | `{"type":"interrupt"}` user pressed a key to cut Piblo off |
| text | `{"type":"playback_done"}` device finished playing the reply |
| text | `{"type":"bye"}` end the session |

## Core -> Device

| Kind | Payload |
|------|---------|
| text | `{"type":"state","state":"listening"\|"thinking"\|"speaking"}` |
| text | `{"type":"stop"}` flush playback now |
| text | `{"type":"text","role":"user"\|"assistant","text":"..."}` optional transcript bits (Core currently sends assistant only) |
| text | `{"type":"error","message":"..."}` session stays open unless Core closes it |
| binary | reply audio PCM16 LE mono **16 kHz**, frames of 1280 B (40 ms); the last frame may be shorter |

## Turn flow

1. Core sends `state listening` right after connect. Device streams mic frames.
2. Core VAD waits for speech (>= 250 ms), keeps a 300 ms pre-roll, then ends the turn after
   `MAZ_LIVE_END_SILENCE_MS` (default 600) of silence. Core sends `state thinking`.
3. First reply audio: `state speaking`, then binary frames. Core paces them at real time, never more than
   ~400 ms (about 12 KB) ahead of playback, so the device never needs more than ~16 KB of buffer.
4. After the last frame Core waits for `playback_done` (timeout: audio duration + 1 s), then sends
   `state listening`.
5. Mic frames received while `thinking` or `speaking` are ignored (device may keep or stop sending them).
6. `interrupt` while `thinking` or `speaking`: Core cancels the model response, sends `stop`, then
   `state listening`. On `stop` the device must drop queued playback immediately.
7. If no audio arrives within 4 s of the end of the turn, Core sends
   `{"type":"error","message":"Piblo's PC is busy - close heavy apps"}` and keeps waiting.
8. If the model server is unreachable at connect, Core sends an `error` and closes with 1011.

Per-turn timings (`speech_ms`, `end_detect_ms`, `first_audio_ms`, `audio_s`, `rtf`) appear in `GET /core/timings`
with `"live": true`.
