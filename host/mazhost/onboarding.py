"""A resumable, entirely skippable first conversation with Piblo."""
from __future__ import annotations

import json
import threading
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel, Field

STEPS = (
    ("name", "Hi, I'm Piblo. What should I call you?"),
    ("day", "How's your day going?"),
    ("forget", "What's one thing you always forget?"),
    ("goal", "What are you working towards?"),
    ("watch_this", "Watch this."),
    ("first_form", "Buddy is growing with you."),
)


class Answer(BaseModel):
    text: str = Field(max_length=2000)


class Onboarding:
    def __init__(self, data_dir: Path) -> None:
        self.path = Path(data_dir) / "onboarding.json"
        self._lock = threading.Lock()

    def _load(self) -> dict:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            data = {}
        # A malformed existing file must not be silently overwritten.
        if not isinstance(data, dict):
            raise ValueError("invalid_onboarding_state")
        return data

    def _view(self, data: dict) -> dict:
        index = data.get("index", 0)
        complete = index >= len(STEPS)
        step, prompt = ("complete", "You're ready, Piblo is with you.") if complete else STEPS[index]
        return {**data, "step": step, "prompt": prompt, "complete": complete,
                "can_skip": not complete}

    def state(self) -> dict:
        with self._lock:
            return self._view(self._load())

    def _advance(self, text: str | None) -> dict:
        with self._lock:
            data = self._load()
            index = data.get("index", 0)
            if index >= len(STEPS):
                return self._view(data)
            step = STEPS[index][0]
            event = {}
            if text is None:
                data.setdefault("skipped", []).append(step)
            else:
                text = text.strip()
                if step in ("name", "day", "goal"):
                    data[step] = text
                    if step == "goal" and "wish" in data:
                        data["wish"]["goal"] = text
                elif step == "forget":
                    # agent_builder is not shipped yet; keep the wish for it.
                    data["wish"] = {"text": text}
                elif step == "watch_this":
                    data["watch_played"] = True
                    event["play_watch_this"] = True
                elif step == "first_form":
                    data["first_form_id"] = "explorer"
                    event["form_change"] = {"from": "seed", "to": "explorer"}
            data["index"] = index + 1
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            tmp.replace(self.path)
            return {**self._view(data), **event}

    def answer(self, text: str) -> dict:
        return self._advance(text)

    def skip(self) -> dict:
        return self._advance(None)


def build_onboarding_router(onboarding: Onboarding) -> APIRouter:
    router = APIRouter(prefix="/onboarding", tags=["onboarding"])

    @router.get("")
    def state():
        return onboarding.state()

    @router.post("/answer")
    def answer(body: Answer):
        return onboarding.answer(body.text)

    @router.post("/skip")
    def skip():
        return onboarding.skip()

    return router
