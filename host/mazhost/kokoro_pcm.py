"""LAN Kokoro endpoint for the device: GET /?text=... -> raw s16le mono 24 kHz PCM, streamed per sentence.

HTTP/1.0, no Content-Length, no chunking: the body ends when the connection closes.
Run standalone: python -m mazhost.kokoro_pcm --port 8880 (or set kokoro_pcm_port in Core).
"""

from __future__ import annotations

import argparse
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np

from .config import Settings
from .speakplan import split_sentences

log = logging.getLogger("uvicorn.error")
MAX_CHARS = 1000
RATE = 24000


def pcm16(audio) -> bytes:
    return (np.clip(np.asarray(audio, dtype=np.float32), -1.0, 1.0) * 32767).astype("<i2").tobytes()


class KokoroSynth:
    """Lazy Kokoro; synth(sentence) -> float32 samples at 24 kHz. Inference is serialized."""

    def __init__(self, settings: Settings) -> None:
        self.s = settings
        self._model = None
        self._lock = threading.Lock()

    def check(self) -> None:
        m, v = self.s.kokoro_model_path, self.s.kokoro_voices_path
        if not m or not v or not Path(m).expanduser().is_file() or not Path(v).expanduser().is_file():
            raise RuntimeError("Kokoro model files missing: set kokoro_model_path and kokoro_voices_path")

    def __call__(self, text: str):
        with self._lock:
            if self._model is None:
                from .tts import _use_cuda_if_present
                _use_cuda_if_present()
                from kokoro_onnx import Kokoro
                self._model = Kokoro(str(Path(self.s.kokoro_model_path).expanduser()),
                                     str(Path(self.s.kokoro_voices_path).expanduser()))
            audio, _ = self._model.create(text, voice=self.s.kokoro_voice,
                                          speed=self.s.kokoro_speed, lang="en-us")
            return audio


def make_server(synth, host: str, port: int) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"

        def log_message(self, *a):  # keep the console quiet
            pass

        def _fail(self, code: int, msg: str) -> None:
            body = msg.encode()
            self.send_response(code)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            text = " ".join(parse_qs(urlparse(self.path).query).get("text", [""])[0].split())
            if not text or len(text) > MAX_CHARS:
                return self._fail(400, f"text required, max {MAX_CHARS} chars")
            check = getattr(synth, "check", None)
            if check:
                try:
                    check()
                except RuntimeError as e:
                    return self._fail(503, str(e))
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            try:
                for sentence in split_sentences(text) or [text]:
                    self.wfile.write(pcm16(synth(sentence)))
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionError):
                pass
            except Exception:
                log.warning("kokoro_pcm synth failed", exc_info=True)  # headers sent; closing ends the body

    return ThreadingHTTPServer((host, port), Handler)


def serve_in_thread(settings: Settings) -> None:
    srv = make_server(KokoroSynth(settings), settings.bind, settings.kokoro_pcm_port)
    threading.Thread(target=srv.serve_forever, daemon=True, name="kokoro-pcm").start()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8880)
    ap.add_argument("--host", default=None)
    a = ap.parse_args()
    cfg = Settings()
    make_server(KokoroSynth(cfg), a.host or cfg.bind, a.port).serve_forever()
