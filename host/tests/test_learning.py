from __future__ import annotations

import json

from mazhost.learning import Learning


class Clock:
    t = 1_763_000_000.0

    def __call__(self):
        return self.t


def test_skip_pattern_becomes_a_rule(tmp_path):
    learn = Learning(tmp_path, clock=Clock())
    learn.record("email_triage", "shown", "Delivery updates")
    for _ in range(3):
        learn.record("email_triage", "skipped", "Delivery updates")
    learn.record("email_triage", "corrected", "user prefers 10 minutes' warning")

    result = learn.rewrite_note("email_triage")
    assert result["rules"] == ["Skip delivery updates", "user prefers 10 minutes' warning"]

    note = learn.notes_for("email_triage")
    assert "# Email Triage — what Piblo has learned" in note
    assert "- Skip delivery updates" in note
    assert "- user prefers 10 minutes' warning" in note

    # not yet a pattern: 2 skips stay silent
    learn.record("email_triage", "skipped", "Receipts")
    learn.record("email_triage", "skipped", "Receipts")
    assert "Skip receipts" not in learn.rewrite_note("email_triage")["rules"]


def test_user_edit_survives_the_next_rewrite(tmp_path):
    learn = Learning(tmp_path, clock=Clock())
    for _ in range(3):
        learn.record("email_triage", "skipped", "Delivery updates")
    learn.rewrite_note("email_triage")

    path = tmp_path / "learning-email-triage.md"
    with path.open("a", encoding="utf-8") as fh:
        fh.write("- never summarise Mum's newsletters\n")
    learn.rewrite_note("email_triage")  # events unchanged or not, the edit stays

    note = learn.notes_for("email_triage")
    assert "- Skip delivery updates" in note          # managed rules still refresh
    assert "- never summarise Mum's newsletters" in note  # the edit won

    # a note written entirely by the user is all user content
    (tmp_path / "learning-speaks-first.md").write_text("Leave me alone before 9am\n", encoding="utf-8")
    learn.rewrite_note("speaks_first")
    assert "Leave me alone before 9am" in learn.notes_for("speaks_first")


def test_weekly_summary_lists_the_rules(tmp_path):
    clock = Clock()
    learn = Learning(tmp_path, clock=clock)
    for _ in range(3):
        learn.record("email_triage", "skipped", "Delivery updates")
    learn.record("speaks_first", "corrected", "user prefers 10 minutes' warning")
    learn.rewrite_note("email_triage")
    learn.rewrite_note("speaks_first")

    summary = learn.weekly_summary(clock.t)
    assert summary.startswith("Here's what I learned this week:")
    assert "- Email Triage: Skip delivery updates" in summary
    assert "- Speaks First: user prefers 10 minutes' warning" in summary

    # last week's events don't make this week's summary
    assert learn.weekly_summary(clock.t + 8 * 86400) == "Here's what I learned this week: nothing new yet."


def test_llm_summarises_into_the_same_note(tmp_path):
    class FakeLLM:
        def chat(self, messages, route):
            return json.dumps({"rules": ["skip delivery updates", "user prefers 10 minutes' warning"]}), "fake"

    learn = Learning(tmp_path, llm=FakeLLM(), clock=Clock())
    learn.record("email_triage", "skipped", "Delivery updates")
    result = learn.rewrite_note("email_triage")
    assert result["rules"] == ["skip delivery updates", "user prefers 10 minutes' warning"]
    assert "- skip delivery updates" in learn.notes_for("email_triage")

    class BrokenLLM:
        def chat(self, messages, route):
            raise RuntimeError("offline")

    learn = Learning(tmp_path, llm=BrokenLLM(), clock=Clock())
    for _ in range(3):
        learn.record("email_triage", "skipped", "Delivery updates")
    assert learn.rewrite_note("email_triage")["rules"] == ["Skip delivery updates"]  # counts took over


def test_unknown_event_kind_rejected(tmp_path):
    learn = Learning(tmp_path, clock=Clock())
    try:
        learn.record("email_triage", "loved")
        raise AssertionError("should have raised")
    except ValueError:
        pass
