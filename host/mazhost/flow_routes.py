"""Flow settings API: input mode, cleanup engine, personal dictionary, recent dictations.

Settings live beside the dictionary in ``flow_dir/settings.json`` and are applied to the
running Flow service in memory, so a change takes effect on the next dictation without a
Core restart. Unknown/absent keys fall back to the config's own defaults.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

INPUT_MODES = ("paste", "type")
CLEANUPS = ("auto", "rules", "groq", "local")
STT_CHOICES = ("auto", "parakeet", "whisper")
DEFAULTS = {"input_mode": "paste", "press_enter": False, "cleanup": "auto", "stt": "auto"}
LATENCY_KEEP = 50


# ---------------------------------------------------------------- persistence
def settings_path(flow) -> Path:
    return Path(flow.dir) / "settings.json"


def read_settings(flow) -> dict:
    path = settings_path(flow)
    data = dict(DEFAULTS)
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        stored = {}
    if isinstance(stored, dict):
        for key in DEFAULTS:
            if key in stored:
                data[key] = stored[key]
    return data


def write_settings(flow, data: dict) -> None:
    path = settings_path(flow)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=".settings-", suffix=".json")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def apply_settings(flow, data: dict) -> None:
    """Push the stored choices onto the live Flow settings object."""
    s = flow.s
    cleanup = data.get("cleanup", "auto")
    if cleanup == "rules":
        s.flow_cloud, s.flow_cleanup_llm = False, False
    elif cleanup == "groq":
        s.flow_cleanup_llm = False
        s.flow_cloud = True
    elif cleanup == "local":
        s.flow_cloud, s.flow_cleanup_llm = False, True
    stt = data.get("stt", "auto")
    if stt in ("parakeet", "whisper"):
        s.stt_provider = stt


def effective_cleanup(flow) -> str:
    """What the next dictation will actually use, given keys and current flags."""
    s = flow.s
    if getattr(s, "flow_cloud", False) and (s.groq_api_key or getattr(s, "groq_key", "")):
        return "groq"
    if getattr(s, "flow_cleanup_llm", False):
        return "local"
    return "rules"


# ---------------------------------------------------------------- dictionary
def dictionary_path(flow) -> Path:
    return Path(flow.dir) / "dictionary.txt"


def save_words(flow, words: list[str]) -> None:
    path = dictionary_path(flow)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(words) + ("\n" if words else ""), encoding="utf-8")
    flow.words = words


def clean_word(word: str) -> str:
    word = " ".join(str(word).split())
    if not word or len(word) > 64:
        raise HTTPException(400, "word must be 1-64 characters")
    if any(not (ch.isalnum() or ch in " -'._&+") for ch in word):
        raise HTTPException(400, "word has unsupported characters")
    return word


# ---------------------------------------------------------------- latency log
def recent_dictations(flow, limit: int = 10) -> list[dict]:
    path = Path(flow.dir) / "latency.log"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[-LATENCY_KEEP:]
    except OSError:
        return []
    rows = []
    for line in reversed(lines):
        if "dictate" not in line:
            continue
        fields = _fields(line)
        rows.append(
            {
                "when": line.split(" ")[0],
                "intent": fields.get("intent", ""),
                "stt_ms": _int(fields.get("stt")),
                "clean_ms": _int(fields.get("clean")),
                "total_ms": _int(fields.get("total")),
                "cleanup": fields.get("via", ""),
                "stt_engine": fields.get("stt_via", ""),
                "chars": _int(fields.get("chars")),
            }
        )
        if len(rows) >= limit:
            break
    return rows


def _int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


_FIELD = re.compile(r"(\w+)=(\S+)")


def _fields(line: str) -> dict:
    return dict(_FIELD.findall(line))


# ---------------------------------------------------------------- insertion
def insert_text(text: str, enter: bool = False, flow=None) -> str:
    """Insert dictated text into whatever window has focus. Returns the mode used."""
    mode = read_settings(flow).get("input_mode", "paste") if flow is not None else "paste"
    if mode == "type":
        type_text(text)
        if enter:
            _tap(0x0D)
        return "type"
    from .flow import paste as paste_text

    paste_text(text, enter)
    return "paste"


def type_text(text: str) -> None:
    """Send literal characters as unicode key events (no clipboard touched)."""
    import ctypes
    from ctypes import wintypes

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                    ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]

    class INPUT(ctypes.Structure):
        class _U(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT)]

        _anonymous_ = ("u",)
        _fields_ = [("type", wintypes.DWORD), ("u", _U)]

    u = ctypes.windll.user32
    KEYEVENTF_UNICODE, KEYEVENTF_KEYUP = 0x0004, 0x0002
    units = text.encode("utf-16-le")
    for index in range(0, len(units), 2):
        code = int.from_bytes(units[index:index + 2], "little")
        for flags in (KEYEVENTF_UNICODE, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP):
            event = INPUT(type=1, ki=KEYBDINPUT(0, code, flags, 0, None))
            u.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT))


def _tap(*vks: int) -> None:
    import ctypes

    u = ctypes.windll.user32
    time.sleep(0.03)
    for vk in vks:
        u.keybd_event(vk, 0, 0, 0)
    for vk in reversed(vks):
        u.keybd_event(vk, 0, 2, 0)


def foreground_window() -> dict:
    import ctypes
    from ctypes import wintypes

    u = ctypes.windll.user32
    hwnd = u.GetForegroundWindow()
    length = u.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    u.GetWindowTextW(hwnd, buffer, length + 1)
    return {"hwnd": int(hwnd or 0), "title": buffer.value}


# ---------------------------------------------------------------- API
class FlowSettingsIn(BaseModel):
    input_mode: Literal["paste", "type"] | None = None
    press_enter: bool | None = None
    cleanup: Literal["auto", "rules", "groq", "local"] | None = None
    stt: Literal["auto", "parakeet", "whisper"] | None = None


class WordIn(BaseModel):
    word: str = Field(min_length=1, max_length=64)


def build_flow_router(flow) -> APIRouter:
    apply_settings(flow, read_settings(flow))
    api = APIRouter(tags=["flow"])

    def settings_view() -> dict:
        stored = read_settings(flow)
        return {
            **stored,
            "effective_cleanup": effective_cleanup(flow),
            "stt_engine": getattr(flow.s, "stt_provider", ""),
            "has_groq_key": bool(flow.s.groq_api_key or getattr(flow.s, "groq_key", "")),
            "dictionary_count": len(flow.words),
            "dir": str(flow.dir),
        }

    @api.get("/flow/settings")
    def get_settings():
        return settings_view()

    @api.patch("/flow/settings")
    def patch_settings(body: FlowSettingsIn):
        stored = read_settings(flow)
        for key, value in body.model_dump(exclude_none=True).items():
            stored[key] = value
        write_settings(flow, stored)
        apply_settings(flow, stored)
        return settings_view()

    @api.get("/flow/dictionary")
    def get_dictionary():
        return {"words": flow.words}

    @api.post("/flow/dictionary")
    def add_word(body: WordIn):
        word = clean_word(body.word)
        if word.lower() not in {w.lower() for w in flow.words}:
            save_words(flow, [*flow.words, word])
        return {"words": flow.words}

    @api.delete("/flow/dictionary/{word}")
    def remove_word(word: str):
        keep = [w for w in flow.words if w.lower() != word.strip().lower()]
        if len(keep) != len(flow.words):
            save_words(flow, keep)
        return {"words": flow.words}

    @api.get("/flow/status")
    def status():
        rows = recent_dictations(flow)
        totals = sorted(r["total_ms"] for r in rows if r["total_ms"])
        p95 = totals[min(len(totals) - 1, int(len(totals) * 0.95))] if totals else 0
        errors = []
        path = Path(flow.dir) / "errors.log"
        try:
            errors = path.read_text(encoding="utf-8").splitlines()[-5:]
        except OSError:
            pass
        return {
            "recent": rows,
            "count": len(rows),
            "avg_total_ms": round(sum(totals) / len(totals)) if totals else 0,
            "p95_total_ms": p95,
            "errors": errors,
            "effective_cleanup": effective_cleanup(flow),
        }

    @api.get("/flow/target")
    def target():
        try:
            return foreground_window()
        except Exception:  # noqa: BLE001 - non-Windows or no window
            return {"hwnd": 0, "title": ""}

    return api