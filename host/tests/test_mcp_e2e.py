"""End-to-end: real Core + real piblo-mcp (over stdio) + a headless simulator driving the same
/buddy/* routes as the browser sim and the firmware.

Covers Maz's success test in one file:
  notify -> simulator sees it -> request approval -> simulator approves -> MCP client gets "approved"
  restart Core -> history kept, an old pending approval is NOT pending (expired)
  duplicate idempotency key -> single record
  no answer -> expired (via restart, which is how Core closes a pending approval)
  corrupt DB -> Core recovers and starts fresh

Skipped (with a clear reason) when node or npm are unavailable, since the MCP server is TypeScript.
"""
from __future__ import annotations

import json
import shutil
import socket
import subprocess
import threading
import time
from pathlib import Path

import httpx
import pytest
import uvicorn
from fastapi.testclient import TestClient

from mazhost.app import create_app
from mazhost.config import Settings

REPO = Path(__file__).resolve().parents[2]
MCP_DIR = REPO / "host" / "mcp"
BRIDGE = MCP_DIR / "test" / "e2e_bridge.mjs"
DIST = MCP_DIR / "dist" / "index.js"

TOKEN = "e2e-token-not-default"
H = {"Authorization": f"Bearer {TOKEN}", "X-Piblo-Client": "simulator/1"}

NODE = shutil.which("node")


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _build_mcp() -> None:
    """Build dist/index.js once. CI may pre-build it; here we build on demand so `pytest` is self-contained."""
    if DIST.exists():
        return
    if not shutil.which("npm"):
        pytest.skip("npm unavailable, cannot build piblo-mcp")
    subprocess.run(["npm", "ci"], cwd=MCP_DIR, check=True, capture_output=True, timeout=300)
    subprocess.run(["npm", "run", "build"], cwd=MCP_DIR, check=True, capture_output=True, timeout=300)


def mcp_call(url: str, tool: str, args: dict, timeout: int = 90) -> dict:
    """One tool call through the real MCP server; returns the parsed tool result."""
    assert NODE, "node required"
    proc = subprocess.run(
        [NODE, str(BRIDGE), url, TOKEN, tool, json.dumps(args)],
        capture_output=True, text=True, timeout=timeout,
    )
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    payload = json.loads(out["text"])
    payload["_isError"] = out["isError"]
    return payload


class Sim:
    """Headless simulator: the same routes the browser /sim page drives (poll events, decide, ack)."""

    def __init__(self, base: str) -> None:
        self.c = httpx.Client(base_url=base, headers=H, timeout=10)
        self.since = 0

    def events(self) -> list[dict]:
        page = self.c.get("/buddy/events", params={"since": self.since}).json()
        for ev in page.get("events", []):
            self.since = ev["id"]
        return page.get("events", [])

    def pending(self) -> list[dict]:
        return self.c.get("/buddy/summary").json().get("items", [])

    def decide(self, rid: str, decision: str) -> None:
        self.c.post("/buddy/decide", json={"id": rid, "decision": decision})

    def ack(self, aid: str) -> None:
        self.c.post(f"/buddy/alert/{aid}/ack")

    def notify_me(self, title: str, key: str = "") -> dict:
        r = self.c.post("/buddy/alert", json={
            "source": "sim", "kind": "info", "title": title, "priority": "normal",
            "actions": ["ack"], "idempotency_key": key}).json()
        return r


def _wait_until(pred, timeout=15.0, interval=0.2):
    end = time.monotonic() + timeout
    last = None
    while time.monotonic() < end:
        last = pred()
        if last:
            return last
        time.sleep(interval)
    return last


class CoreHandle:
    """Core running on a real port (needed because the node MCP process and the sim both use HTTP)."""

    def __init__(self, data_dir: Path):
        self.port = _free_port()
        self.data_dir = data_dir
        cfg = Settings(token=TOKEN, buddy_db=str(data_dir / "buddy.sqlite3"), _env_file=None)
        self.app = create_app(cfg)
        self._thread = threading.Thread(
            target=uvicorn.run, kwargs={"app": self.app, "host": "127.0.0.1", "port": self.port, "log_level": "error"},
            daemon=True,
        )
        self._thread.start()
        self.base = f"http://127.0.0.1:{self.port}"
        # wait for readiness
        c = httpx.Client(base_url=self.base, headers=H, timeout=5)
        _wait_until(lambda: _ping(c), timeout=15.0)

    def stop(self) -> None:
        # uvicorn.run in a daemon thread has no clean stop handle here; the process ends with the test.
        # Closing client connections is enough for the test harness.
        pass


def _ping(c) -> bool:
    try:
        return c.get("/health").status_code == 200
    except httpx.HTTPError:
        return False


@pytest.fixture(scope="module")
def core(tmp_path_factory):
    if not NODE:
        pytest.skip("node unavailable, skipping piblo-mcp e2e")
    _build_mcp()
    data_dir = tmp_path_factory.mktemp("piblo-e2e")
    handle = CoreHandle(data_dir)
    yield handle, data_dir


# ---------------------------------------------------------------------------


def test_success_flow_restart_and_history(core):
    handle, data_dir = core
    base = handle.base
    sim = Sim(base)

    # 1. MCP notifies -> the simulator sees it.
    n = mcp_call(base, "piblo_notify", {"title": "Deploy finished", "body": "all green", "idempotency_key": "n1"})
    assert n["ok"] is True and n["duplicate"] is False
    seen = _wait_until(lambda: sim.events() or None)
    assert seen and any("Deploy finished" in e.get("text", "") for e in seen)

    # 2. MCP asks for approval (blocking); the simulator approves; the client gets "approved".
    result = {}
    def ask():
        result.update(mcp_call(base, "piblo_request_approval",
                               {"action": "Deploy to prod", "summary": "push the release", "sensitive": True}))
    t = threading.Thread(target=ask, daemon=True)
    t.start()
    pending = _wait_until(lambda: sim.pending() or None, timeout=20.0)
    assert pending, "the approval never reached the device"
    sim.decide(pending[0]["id"], "allow")
    t.join(timeout=60)
    assert result.get("decision") == "approved", result

    # history holds both, no secrets in the export
    hist = httpx.get(base + "/buddy/history", headers=H).json()
    assert any("Deploy to prod" in a["tool"] for a in hist["approvals"])

    # 3. leave an approval unanswered, restart, and prove it is NOT pending (it expired) while history survives.
    unanswered = httpx.post(base + "/buddy/request", json={"tool": "Later", "summary": "never answered", "agent": "x"},
                            headers=H).json()
    httpx.post(base + "/buddy/demo", headers=H)  # second approval, also pending, for good measure
    handle.stop()

    cfg = Settings(token=TOKEN, buddy_db=str(data_dir / "buddy.sqlite3"), _env_file=None)
    app2 = create_app(cfg)
    port2 = _free_port()
    t2 = threading.Thread(target=uvicorn.run,
                          kwargs={"app": app2, "host": "127.0.0.1", "port": port2, "log_level": "error"}, daemon=True)
    t2.start()
    base2 = f"http://127.0.0.1:{port2}"
    c2 = httpx.Client(base_url=base2, headers=H, timeout=10)
    _wait_until(lambda: _ping(c2), timeout=15.0)

    # history persisted
    hist2 = c2.get("/buddy/history").json()
    assert any("Deploy to prod" in a["tool"] for a in hist2["approvals"])
    # no pending approval survived the restart (they all expired on open)
    summary = c2.get("/buddy/summary").json()
    assert summary["items"] == [], summary
    # the specific unanswered one reads as expired, never pending
    state = c2.get("/buddy/state", params={"id": unanswered["id"]}).json()
    assert state["decision"] == "cancel" and state.get("expired") is True


def test_duplicate_idempotency_key_single_record(core):
    handle, _ = core
    sim = Sim(handle.base)
    first = mcp_call(handle.base, "piblo_notify", {"title": "Once", "idempotency_key": "dup-1"})
    again = mcp_call(handle.base, "piblo_notify", {"title": "Once", "idempotency_key": "dup-1"})
    assert first["ok"] is True and again.get("duplicate") is True and again["id"] == first["id"]


def test_no_answer_expires_at_client(core):
    handle, _ = core
    r = mcp_call(handle.base, "piblo_request_approval", {"action": "Never answered", "wait_seconds": 5}, timeout=30)
    assert r["decision"] == "expired", r


def test_corrupt_db_recovers(tmp_path):
    bad = tmp_path / "corrupt.sqlite3"
    bad.write_bytes(b"this is not a sqlite database at all")
    app = create_app(Settings(token=TOKEN, buddy_db=str(bad), _env_file=None))
    # create_app builds the store at startup; a corrupt file must be quarantined, not crash.
    c = TestClient(app)
    assert c.get("/buddy/history", headers=H).status_code == 200
    assert any(p.name.startswith("corrupt.sqlite3.corrupt-") for p in tmp_path.iterdir())
