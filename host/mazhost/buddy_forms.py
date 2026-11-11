"""Buddy's artwork and habit rules are plain data, in priority order."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from fastapi import APIRouter

FORMS_FILE = Path(__file__).with_name("data") / "buddy_forms.json"
PALETTE = ["paper", "ink", "tomato", "mint", "sun"]


def forms() -> list[dict]:
    return json.loads(FORMS_FILE.read_text(encoding="utf-8"))


def current_form(stats: dict) -> dict:
    """Stats with a ``_7d`` suffix cover the preceding seven days.

    The first matching non-default rule wins, so priority is editable in JSON.
    """
    available = forms()
    for form in available:
        rule = form["rule"]
        if rule.get("default"):
            continue
        value = stats.get(rule["metric"], 0)
        if "share_of" in rule:
            total = stats.get(rule["share_of"], 0)
            if total > 0 and value / total > rule["above"]:
                return form
        elif value >= rule["at_least"]:
            return form
    return next(form for form in available if form["rule"].get("default"))


def build_buddy_forms_router(stats_provider: Callable[[], dict] | None = None, onboarding=None) -> APIRouter:
    router = APIRouter(tags=["buddy"])

    @router.get("/buddy/form")
    def get_form():
        form = current_form(stats_provider() if stats_provider else {})
        if form["id"] == "seed" and onboarding:
            welcome_form = onboarding.state().get("first_form_id")
            form = next((item for item in forms() if item["id"] == welcome_form), form)
        return {key: form[key] for key in ("id", "name", "pixel_art")} | {"palette": PALETTE}

    return router
