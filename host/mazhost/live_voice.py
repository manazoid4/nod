"""Live voice: bridge a thin Cardputer to LFM3-Omni's OpenAI-Realtime socket (llama-server).

The device streams 16 kHz mic PCM and plays 16 kHz reply PCM; everything heavy (turn detection,
the model, 24k->16k resampling) happens here. Wire contract: docs/LIVE-VOICE-PROTOCOL.md.
llama.cpp has no VAD, so Core decides when the user's turn ends.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import time
from collections import deque

import numpy as np
from fastapi import WebSocket
from starlette.routing import WebSocketRoute
from websockets.asyncio.client import connect

from .config import Settings

log = logging.getLogger("mazhost.live")

IN_RATE, OUT_RATE = 16000, 24000
BLOCK = 640  # 20 ms of 16 kHz PCM16 mono, in bytes (320 samples)
BLOCK_MS = 20
FRAME = 1280  # 40 ms reply frame to the device, bytes
AHEAD_S = 0.4  # never run further than this ahead of real-time playback
MIN_SPEECH_MS = 250
PREROLL_MS = 300
FIRST_AUDIO_LIMIT_S = 4.0
INSTRUCTIONS = ("You are Piblo, a friendly, warm and calm voice assistant on a tiny pocket device. "
                "Never name or reveal your model. Keep replies short and spoken. "
                "Respond with interleaved text and audio.")


def boost(pcm: bytes, gain: float) -> bytes:
    """Scale PCM16 by gain with hard clipping (the device mic is ~20 dB quiet)."""
    x = np.frombuffer(pcm[: len(pcm) // 2 * 2], "<i2").astype(np.float32) * gain
    return np.clip(x, -32768, 32767).astype("<i2").tobytes()


class Vad:
    """Energy VAD: adaptive noise floor, 300 ms pre-roll, min-speech gate, silence hangover."""

    MIN_RMS = 700.0  # int16 rms after live_mic_gain; boosted ADV room noise reaches ~400, speech 1000+

    def __init__(self, end_silence_ms: int) -> None:
        self.end_blocks = max(1, end_silence_ms // BLOCK_MS)
        self.floor = 150.0
        self.reset()

    def reset(self) -> None:
        self._buf = b""
        self._pre: deque[bytes] = deque(maxlen=PREROLL_MS // BLOCK_MS + MIN_SPEECH_MS // BLOCK_MS)
        self._run = 0
        self.speaking = False
        self._silence = 0
        self._loud = 0
        self.last_loud_at = 0.0

    def feed(self, pcm: bytes) -> tuple[list[bytes], bool]:
        """Return (blocks to forward to the model, turn_ended). Blocks flow only once speech began."""
        out: list[bytes] = []
        self._buf += pcm
        ended = False
        while len(self._buf) >= BLOCK and not ended:
            blk, self._buf = self._buf[:BLOCK], self._buf[BLOCK:]
            rms = float(np.sqrt(np.mean(np.frombuffer(blk, "<i2").astype(np.float32) ** 2)))
            loud = rms > max(self.floor * 3, self.MIN_RMS)
            if not self.speaking:
                if not loud:  # floor tracks quiet blocks only, so speech cannot raise it
                    self.floor += (rms - self.floor) * 0.05
                self._pre.append(blk)
                self._run = self._run + 1 if loud else 0
                if self._run >= MIN_SPEECH_MS // BLOCK_MS:
                    self.speaking = True
                    self._silence = self._loud = 0
                    out.extend(self._pre)
                    self._pre.clear()
                    self.last_loud_at = time.monotonic()
                continue
            out.append(blk)
            if loud:
                self._silence = 0
                self._loud += 1
                self.last_loud_at = time.monotonic()
            else:
                self._silence += 1
                ended = self._silence >= self.end_blocks
        return out, ended

    @property
    def speech_ms(self) -> int:
        return (self._loud + MIN_SPEECH_MS // BLOCK_MS) * BLOCK_MS


def _speaker_band(taps: int = 481, low: float = 220.0, high: float = 6800.0, rate: int = OUT_RATE) -> np.ndarray:
    """Windowed-sinc band-pass for the Cardputer's tiny speaker, designed at the model's 24 kHz."""
    n = np.arange(taps) - (taps - 1) / 2

    def lowpass(fc: float) -> np.ndarray:
        return 2 * fc / rate * np.sinc(2 * fc / rate * n)

    return ((lowpass(high) - lowpass(low)) * np.blackman(taps)).astype(np.float32)


SPEAKER_BAND = _speaker_band()


class Resampler24to16:
    """Streaming 24k->16k (output length = 2/3 of input), band-limited for the device speaker.

    The band-pass runs before decimation: without it, 8-12 kHz model output aliases into 4-8 kHz
    (harsh, gritty sibilance), and sub-220 Hz energy only makes the 1 W speaker rattle.
    """

    def __init__(self) -> None:
        self._buf = np.zeros(0, np.float32)
        self._t = 0.0  # next output position, in input samples relative to _buf[0]
        self._hist = np.zeros(len(SPEAKER_BAND) - 1, np.float32)  # filter state across chunks

    def feed(self, pcm: bytes) -> bytes:
        x = np.concatenate([self._hist, np.frombuffer(pcm, "<i2").astype(np.float32)])
        self._hist = x[len(x) - len(self._hist):]
        self._buf = np.concatenate([self._buf, np.convolve(x, SPEAKER_BAND, "valid")])
        if len(self._buf) < 2:
            return b""
        ts = np.arange(self._t, len(self._buf) - 1 + 1e-9, OUT_RATE / IN_RATE)
        if not len(ts):
            return b""
        out = np.interp(ts, np.arange(len(self._buf)), self._buf)
        nxt = ts[-1] + OUT_RATE / IN_RATE
        drop = min(int(nxt), len(self._buf) - 1)
        self._buf, self._t = self._buf[drop:], nxt - drop
        return np.clip(out, -32768, 32767).astype("<i2").tobytes()


class LiveBridge:
    """One device session: owns the upstream realtime socket and the per-turn state machine."""

    def __init__(self, ws: WebSocket, cfg: Settings, timings=None) -> None:
        self.ws, self.cfg, self.timings = ws, cfg, timings
        self.url = cfg.llamacpp_url.replace("http", "ws", 1).rstrip("/") + "/v1/realtime"
        self.vad = Vad(cfg.live_end_silence_ms)
        self.gain = cfg.live_mic_gain
        self.holdoff = cfg.live_listen_holdoff_ms / 1000
        self._mute_until = 0.0
        self.state = "listening"
        self.up = None
        self._reader: asyncio.Task | None = None
        self._player: asyncio.Task | None = None
        self._q: asyncio.Queue[bytes | None] = asyncio.Queue()
        self._rs = Resampler24to16()
        self._played = asyncio.Event()
        self._guard: asyncio.TimerHandle | None = None
        self._need_reset = False
        self._t: dict = {}

    # ---- device side -----------------------------------------------------
    async def run(self) -> None:
        try:
            await self._connect()
        except Exception as error:  # model server down: tell the device, do not crash Core
            log.warning("live: model server unavailable: %s", error)
            await self._send({"type": "error", "message": "Piblo's brain is offline"})
            await self.ws.close(1011)
            return
        await self._set_state("listening")
        try:
            while True:
                msg = await self.ws.receive()
                if msg["type"] == "websocket.disconnect":
                    break
                if msg.get("bytes") is not None:
                    await self._mic(msg["bytes"])
                elif msg.get("text") is not None:
                    if await self._control(msg["text"]):
                        break
        finally:
            self._end_turn_tasks()
            if self._reader:
                self._reader.cancel()
            if self.up:
                await self.up.close()
            try:
                await self.ws.close()
            except RuntimeError:  # already closed by the device
                pass

    async def _control(self, raw: str) -> bool:
        try:
            kind = json.loads(raw).get("type")
        except (ValueError, AttributeError):
            return False
        if kind == "interrupt" and self.state != "listening":
            await self._interrupt()
        elif kind == "playback_done":
            self._played.set()
        elif kind == "hello":
            log.info("live: device hello %s", raw[:80])
        return kind == "bye"

    async def _mic(self, pcm: bytes) -> None:
        if self.state != "listening":
            return  # half-duplex: the codec is playing, mic is not ours
        if time.monotonic() < self._mute_until:
            return  # tail of our own reply / codec switch noise: never a user turn
        if self.gain != 1.0:
            pcm = boost(pcm, self.gain)
        blocks, ended = self.vad.feed(pcm)
        if blocks:
            await self._up_send({"type": "input_audio_buffer.append",
                                 "audio": base64.b64encode(b"".join(blocks)).decode()})
        if ended:
            await self._start_turn()

    async def _start_turn(self) -> None:
        now = time.monotonic()
        self._t = {"create": now, "speech_ms": self.vad.speech_ms,
                   "end_detect_ms": round((now - self.vad.last_loud_at) * 1000), "audio_bytes": 0}
        self.vad.reset()
        self._rs = Resampler24to16()
        self._q = asyncio.Queue()
        self._played.clear()
        await self._set_state("thinking")
        await self._up_send({"type": "response.create"})
        self._guard = asyncio.get_running_loop().call_later(FIRST_AUDIO_LIMIT_S, self._slow)

    def _slow(self) -> None:
        if self.state == "thinking":
            log.warning("live: no audio %.0fs after response.create", FIRST_AUDIO_LIMIT_S)
            asyncio.ensure_future(self._send({"type": "error",
                                              "message": "Piblo's PC is busy - close heavy apps"}))

    async def _interrupt(self) -> None:
        self._end_turn_tasks()
        await self._up_send({"type": "response.cancel"})
        await self._send({"type": "stop"})
        await self._set_state("listening")
        self.vad.reset()

    def _end_turn_tasks(self) -> None:
        if self._guard:
            self._guard.cancel()
            self._guard = None
        if self._player and self._player is not asyncio.current_task():
            self._player.cancel()
        self._player = None

    async def _set_state(self, state: str) -> None:
        if state == "listening" and self.state != "listening":
            self._mute_until = time.monotonic() + self.holdoff
            self.vad.reset()
        self.state = state
        await self._send({"type": "state", "state": state})

    async def _send(self, obj: dict) -> None:
        try:
            await self.ws.send_text(json.dumps(obj))
        except Exception:  # device already gone; run() sees the disconnect
            pass

    # ---- model side ------------------------------------------------------
    async def _connect(self) -> None:
        self.up = await connect(self.url, max_size=None, open_timeout=5)
        json.loads(await self.up.recv())  # session.created
        await self.up.send(json.dumps({"type": "session.update", "session": {
            "type": "realtime", "instructions": INSTRUCTIONS, "output_modalities": ["text", "audio"]}}))
        json.loads(await self.up.recv())  # session.updated
        self._need_reset = False
        self._reader = asyncio.create_task(self._read_up())

    async def _up_send(self, obj: dict) -> None:
        if self._need_reset or self.up is None:  # cancel was refused or socket died: fresh session
            if self._reader:
                self._reader.cancel()
            if self.up:
                await self.up.close()
            await self._connect()
        await self.up.send(json.dumps(obj))

    async def _read_up(self) -> None:
        try:
            async for raw in self.up:
                await self._on_up(json.loads(raw))
        except asyncio.CancelledError:
            raise
        except Exception as error:
            log.warning("live: upstream closed: %s", error)
        self._need_reset = True

    async def _on_up(self, ev: dict) -> None:
        kind = ev.get("type", "")
        if kind == "error":
            log.warning("live: upstream error %s", ev.get("error"))
            self._need_reset = True  # unsure what state the session is in (e.g. cancel refused)
            if self.state != "listening":
                await self._send({"type": "error", "message": "Piblo's brain hit a snag"})
                await self._interrupt()
        elif self.state == "listening":
            return  # stale events from a cancelled response
        elif kind == "response.output_text.delta":
            await self._send({"type": "text", "role": "assistant", "text": ev.get("delta", "")})
        elif kind == "response.output_audio.delta":
            pcm = self._rs.feed(base64.b64decode(ev.get("delta", "")))
            if pcm and "first" not in self._t:
                self._t["first"] = time.monotonic()
                self._guard and self._guard.cancel()
                await self._set_state("speaking")
                self._player = asyncio.create_task(self._play())
            if pcm:
                self._q.put_nowait(pcm)
        elif kind == "response.done":
            self._t["done"] = time.monotonic()
            self._q.put_nowait(None)
            if "first" not in self._t:  # model produced no audio: nothing to wait for
                self._end_turn_tasks()
                await self._set_state("listening")

    async def _play(self) -> None:
        """Pace reply frames to the device (<= AHEAD_S ahead), then wait for playback_done."""
        buf, n, sent, t0 = bytearray(), 0, 0, time.monotonic()

        async def push(frame: bytes) -> None:
            nonlocal n, sent
            await asyncio.sleep(max(0.0, t0 + n * 0.04 - AHEAD_S - time.monotonic()))
            await self.ws.send_bytes(frame)
            n += 1
            sent += len(frame)

        while (chunk := await self._q.get()) is not None:
            buf += chunk
            while len(buf) >= FRAME:
                await push(bytes(buf[:FRAME]))
                del buf[:FRAME]
        if buf:
            await push(bytes(buf))
        audio_s = sent / (IN_RATE * 2)
        try:
            await asyncio.wait_for(self._played.wait(), max(0.0, t0 + audio_s + 1 - time.monotonic()))
        except asyncio.TimeoutError:
            log.info("live: playback_done timeout")
        self._log_turn(audio_s)
        self._player = None
        await self._set_state("listening")

    def _log_turn(self, audio_s: float) -> None:
        t = self._t
        gen_s = t.get("done", time.monotonic()) - t["create"]
        row = {"live": True, "speech_ms": t["speech_ms"], "end_detect_ms": t["end_detect_ms"],
               "first_audio_ms": round((t["first"] - t["create"]) * 1000),
               "audio_s": round(audio_s, 2), "rtf": round(gen_s / audio_s, 2) if audio_s else None}
        log.info("live_turn %s", row)
        if self.timings is not None:
            self.timings.add(row)


def install_live_voice(api, cfg: Settings, security, timings=None) -> None:
    """Register /voice/live. Plain Starlette route: the app-wide HTTP auth dependency can't take a WebSocket."""

    async def endpoint(ws: WebSocket) -> None:
        token = ws.query_params.get("token")
        auth = ws.headers.get("authorization") or (f"Bearer {token}" if token else None)
        await ws.accept()
        if not security.token_ok(auth):
            await ws.close(4401)
            return
        await LiveBridge(ws, cfg, timings).run()

    api.router.routes.append(WebSocketRoute("/voice/live", endpoint))
