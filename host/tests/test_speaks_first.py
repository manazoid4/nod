from __future__ import annotations

from datetime import datetime

from mazhost.buddy import Buddy
from mazhost.learning import Learning
from mazhost.speaks_first import SpeaksFirst, StaticTransport


class Clock:
    def __init__(self, t: float) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t


def at(day: str, hhmm: str) -> float:
    return datetime.fromisoformat(f"{day}T{hhmm}:00").timestamp()


DAY = "2026-11-11"


def setup(minutes=20, buffer=5, warn=10, focus=None, learning=None, start="10:00"):
    clock = Clock(at(DAY, "08:00"))
    buddy = Buddy()
    sf = SpeaksFirst(buddy, focus=focus, transport=StaticTransport(minutes),
                     learning=learning, clock=clock, buffer_minutes=buffer, warn_minutes=warn)
    event = {"title": "Dentist", "start": at(DAY, start), "location": "High Street"}
    return sf, buddy, clock, event


def titles(buddy):
    return [a["title"] for a in buddy.alerts()["alerts"]]


def test_leave_now_fires_at_the_right_minute(tmp_path):
    sf, buddy, clock, event = setup()
    # leave at 10:00 - 20 travel - 5 buffer = 09:35
    clock.t = at(DAY, "09:34")
    assert sf.check([event], now=clock.t)["posted"] == []
    assert titles(buddy) == []
    clock.t = at(DAY, "09:35")
    assert sf.check([event], now=clock.t)["posted"] == ["Leave now for Dentist"]
    assert "Leave now for Dentist" in titles(buddy)


def test_no_duplicate_nudges(tmp_path):
    sf, buddy, clock, event = setup()
    clock.t = at(DAY, "09:35")
    sf.check([event], now=clock.t)
    assert sf.check([event], now=clock.t)["posted"] == []
    assert titles(buddy).count("Leave now for Dentist") == 1


def test_meeting_in_10(tmp_path):
    sf, buddy, clock, event = setup()
    clock.t = at(DAY, "09:50")
    result = sf.check([event], now=clock.t)
    assert "Meeting in 10: Dentist" in result["posted"]
    # started events stay silent
    clock.t = at(DAY, "10:01")
    assert sf.check([event], now=clock.t)["posted"] == []


def test_iso_calendar_strings_work(tmp_path):
    sf, buddy, clock, _ = setup()
    clock.t = at(DAY, "09:35")
    iso = {"title": "Dentist", "start": f"{DAY}T10:00:00", "location": "High Street"}
    assert "Leave now for Dentist" in sf.check([iso], now=clock.t)["posted"]


def test_deadline_today(tmp_path):
    sf, buddy, clock, _ = setup()
    clock.t = at(DAY, "08:00")
    deadlines = [{"title": "Tax return", "due": at(DAY, "23:59")},
                 {"title": "Tomorrow thing", "due": at("2026-11-12", "09:00")}]
    result = sf.check([], deadlines, now=clock.t)
    assert result["posted"] == ["Deadline today: Tax return"]
    assert sf.check([], deadlines, now=clock.t)["posted"] == []  # once only


class FakeFocus:
    def __init__(self):
        self.on = True

    def muted(self):  # brief contract: focus.muted()
        return self.on


def test_focus_holds_non_urgent_but_not_leave_now(tmp_path):
    focus = FakeFocus()
    sf, buddy, clock, event = setup(focus=focus)
    clock.t = at(DAY, "09:34")
    result = sf.check([], [{"title": "Tax return", "due": at(DAY, "23:59")}], now=clock.t)
    assert result["held"] == ["Deadline today: Tax return"] and result["posted"] == []
    assert titles(buddy) == []  # held back, not posted

    clock.t = at(DAY, "09:35")
    result = sf.check([event], now=clock.t)
    assert result["posted"] == ["Leave now for Dentist"]  # leave-now is urgent

    clock.t = at(DAY, "09:50")
    result = sf.check([event], now=clock.t)
    assert result["held"] == ["Meeting in 10: Dentist"]   # meeting-in-10 is not
    assert titles(buddy).count("Deadline today: Tax return") == 0  # held nudges stay held

    focus.on = False  # sprint over: held nudges flush on the next check
    result = sf.check([], now=clock.t)
    assert set(result["posted"]) == {"Deadline today: Tax return", "Meeting in 10: Dentist"}
    assert titles(buddy).count("Deadline today: Tax return") == 1


def test_learning_note_sets_warning_minutes(tmp_path):
    learn = Learning(tmp_path)
    (tmp_path / "learning-speaks-first.md").write_text(
        "# Speaks First\n- user prefers 15 minutes' warning\n", encoding="utf-8")
    sf, buddy, clock, event = setup(learning=learn)
    clock.t = at(DAY, "09:44")
    assert sf.check([event], now=clock.t)["posted"] == ["Leave now for Dentist"]  # travel, not warning
    clock.t = at(DAY, "09:45")
    assert "Meeting in 15: Dentist" in sf.check([event], now=clock.t)["posted"]
