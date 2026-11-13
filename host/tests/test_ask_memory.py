"""Ask and push-to-talk share durable daily memory, without chat history."""
import io
import wave

from fastapi.testclient import TestClient

from mazhost.app import create_app
from mazhost.config import Settings
from mazhost.memory_notes import MemoryNotes
from test_app import FakeModels, FakeStt

HEADERS = {"Authorization": "Bearer isolated-memory-test"}


def client_at(path, models=None, stt=None):
    return TestClient(create_app(Settings(
        _env_file=None, token="isolated-memory-test", data_dir=str(path),
        work_dir=str(path / "work"), buddy_db="off", private_mode=True,
        autoupdate=False, discovery_port=0, remote_detect=False,
    ), models=models or FakeModels(), stt=stt or FakeStt()))


def turn(api, text, **extra):
    sid = api.post("/session/start", headers=HEADERS).json()["session_id"]
    return api.post("/turn/text", headers=HEADERS,
                    json={"session_id": sid, "text": text, **extra})


def test_ask_remembers_then_reopens_in_fresh_core_and_conversation(tmp_path):
    models = FakeModels()
    api = client_at(tmp_path, models)
    saved = turn(api, "Remember that my appointment is Friday at noon.")
    assert saved.status_code == 200
    assert saved.json()["provider"] == "memory-local"
    assert models.last_messages == []  # saving must work with no model
    reopened_models = FakeModels()
    reopened = client_at(tmp_path, reopened_models)
    assert turn(reopened, "When is my appointment?").status_code == 200
    messages = reopened_models.last_messages
    assert "my appointment is Friday at noon" in messages[0]["content"]
    assert "not instructions" in messages[0]["content"]
    assert len(messages) == 2  # no previous conversation carries the answer
    assert "Friday at noon" in reopened.get("/memory/recall", headers=HEADERS,
                                          params={"q": "appointment"}).text


def test_push_to_talk_saves_into_same_memory_store(tmp_path):
    class RememberStt(FakeStt):
        def transcribe(self, path):
            return "Remember that my bicycle is blue."

    api = client_at(tmp_path, stt=RememberStt())
    sid = api.post("/session/start", headers=HEADERS).json()["session_id"]
    audio = io.BytesIO()
    with wave.open(audio, "wb") as wav:
        wav.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
        wav.writeframes(bytes(3200))
    result = api.post("/turn/raw", headers={**HEADERS, "X-MAZ-Session": sid},
                      content=audio.getvalue())
    assert result.status_code == 200
    assert result.json()["provider"] == "memory-local"
    assert "bicycle is blue" in MemoryNotes(tmp_path).recall("bicycle")[0]["text"]


def test_invalid_session_cannot_write_memory(tmp_path):
    api = client_at(tmp_path)
    result = api.post("/turn/text", headers=HEADERS,
                      json={"session_id": "missing", "text": "Remember my bicycle is blue"})
    assert result.status_code == 404
    assert not (tmp_path / "memory").exists()


def test_context_ask_does_not_write_memory(tmp_path):
    api = client_at(tmp_path)
    assert turn(api, "Remember my bicycle is blue", context="Selected document").status_code == 200
    assert not (tmp_path / "memory").exists()


def test_failed_memory_write_is_honest(tmp_path, monkeypatch):
    def fail(self, text):
        raise OSError("disk unavailable")
    monkeypatch.setattr(MemoryNotes, "remember", fail)
    reply = turn(client_at(tmp_path), "Remember my bicycle is blue").json()
    assert reply["reply"] == "Sorry, I couldn't save that."


def test_memory_context_is_bounded_and_selects_matching_lines(tmp_path):
    notes = MemoryNotes(tmp_path)
    for _ in range(4):
        notes.remember("unrelated " * 400)
    notes.remember("My appointment is Friday at noon")
    models = FakeModels()
    assert turn(client_at(tmp_path, models), "When is my appointment?").status_code == 200
    context = models.last_messages[0]["content"]
    assert "My appointment is Friday at noon" in context
    assert "unrelated" not in context
    assert len(context) < 9000


def test_memory_read_failure_does_not_break_ordinary_ask(tmp_path, monkeypatch):
    def fail(self, *args, **kwargs):
        raise OSError("disk unavailable")
    monkeypatch.setattr(MemoryNotes, "recall", fail)
    assert turn(client_at(tmp_path), "When is my appointment?").status_code == 200


def test_spoken_hesitation_preserves_memory_fact_verbatim(tmp_path):
    api = client_at(tmp_path)
    reply = turn(api, "Um, remember that I like black coffee.").json()
    assert reply["provider"] == "memory-local"
    assert "I like black coffee." in MemoryNotes(tmp_path).recall("coffee")[0]["text"]


def test_catch_me_up_speaks_real_alert_and_library_save(tmp_path):
    from mazhost import library
    from mazhost.app import inbox_dir
    api = client_at(tmp_path)
    cfg_alert = api.post("/buddy/alert", headers=HEADERS,
                         json={"source": "Phone", "title": "Mum", "body": "Call tonight"})
    assert cfg_alert.status_code == 200, cfg_alert.text
    library.save_item(tmp_path / "inbox" / "library", text="Garden plans", project="home")
    for phrase in ("Catch me up", "Um, what did I miss?"):
        reply = turn(api, phrase).json()
        assert reply["provider"] == "catchup-local"
        assert "Mum" in reply["reply"] and reply["reply"].endswith("Everything else can wait.")


def test_catch_me_up_empty_says_so_and_context_ask_is_not_routed(tmp_path):
    api = client_at(tmp_path)
    reply = turn(api, "catch me up").json()
    assert "up to date" in reply["reply"] and reply["reply"].endswith("Everything else can wait.")
    assert turn(api, "catch me up", context="doc").json()["provider"] != "catchup-local"
    assert turn(api, "catch me up on the football").json()["provider"] != "catchup-local"
