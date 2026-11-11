"""Private mode: Core makes zero outbound internet connections when it is on.

The proof test monkeypatches the socket entry points so any non-local
connect/DNS attempt fails the test, then boots the app and exercises every main
path. The static test makes it impossible for future code to bypass the guard by
constructing an httpx client or calling httpx directly outside private_mode.py.
"""
from __future__ import annotations

import asyncio
import ipaddress
import re
import socket
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from mazhost import private_mode
from mazhost.app import create_app
from mazhost.config import Settings
from mazhost.core import MazCore
from mazhost.errors import ErrorCode, RouteError
from mazhost.live_brain import LiveBrain
from mazhost.llm import Models
from mazhost.nudge import NudgeClient
from mazhost.selfupdate import SelfUpdater
from mazhost.telemetry import SystemTelemetry

TOKEN = "test-token-that-is-not-default"


@pytest.fixture(autouse=True)
def _reset_private_mode():
    """Private mode is module-global state; never let one test leak it into another."""
    private_mode.set_enabled(False)
    yield
    private_mode.set_enabled(False)


# ---------------------------------------------------------------- is_local_url

@pytest.mark.parametrize(
    "url,expected",
    [
        # loopback
        ("127.0.0.1", True),
        ("http://127.0.0.1:8080/api/tags", True),
        ("localhost", True),
        ("http://localhost:8787", True),
        # RFC1918
        ("192.168.1.50", True),
        ("http://192.168.1.50", True),
        ("10.0.0.1", True),
        ("172.16.0.1", True),
        ("172.31.255.255", True),
        # link-local
        ("169.254.1.1", True),
        # mDNS
        ("foo.local", True),
        ("http://foo.local:11434", True),
        # IPv6 loopback + ULA
        ("::1", True),
        ("[::1]", True),
        ("http://[::1]:8080", True),
        ("fd00::1", True),
        ("http://[fd00::1]", True),
        # public / non-local
        ("8.8.8.8", False),
        ("http://8.8.8.8", False),
        ("172.32.0.1", False),  # just outside RFC1918
        ("example.com", False),
        ("http://example.com", False),
        ("https://api.groq.com", False),
    ],
)
def test_is_local_url(url, expected):
    assert private_mode.is_local_url(url) is expected


# ------------------------------------------------------------- static choke test


def test_no_direct_httpx_calls_outside_private_mode():
    mazhost = Path(__file__).resolve().parents[1] / "mazhost"
    forbidden = re.compile(
        r"httpx\.(Client|AsyncClient|get|post|request|stream|delete|put|patch|head|options)\s*\("
    )
    offenders: dict[str, list[str]] = {}
    for path in sorted(mazhost.glob("*.py")):
        if path.name == "private_mode.py":
            continue  # the choke point itself is allowed to build clients
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if forbidden.search(line):
                offenders.setdefault(path.name, []).append(f"{i}: {line.strip()}")
    assert not offenders, (
        "direct httpx construction/calls outside private_mode.py bypass the guard:\n"
        + "\n".join(f"{name}: {hits}" for name, hits in sorted(offenders.items()))
    )


# ------------------------------------------------------------------- helpers


class _FakeStt:
    def available(self) -> bool:
        return True

    def transcribe(self, _path) -> str:
        return "hi"

    def transcribe_prompted(self, _path, _prompt) -> str:
        return "hi"

    def transcribe_turn(self, _path) -> str:
        return "hi"


class _FakePC:
    available = True

    def perform(self, action: str):
        return SimpleNamespace(action=action, label=f"did {action}")


def _local_llm(request: httpx.Request) -> httpx.Response:
    if "/health" in str(request.url):
        return httpx.Response(200, json={"status": "ok"})
    return httpx.Response(
        200, json={"model": "lfm3", "choices": [{"message": {"content": "local says hi"}}]}
    )


def _benign(_request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={})


def _forbidden(request: httpx.Request) -> httpx.Response:
    raise AssertionError(f"unexpected outbound request: {request.url}")


def _settings(tmp_path: Path, **overrides) -> Settings:
    base = dict(
        token=TOKEN,
        private_mode=True,
        data_dir=str(tmp_path),
        _env_file=None,
        local_engine="llamacpp",
        llamacpp_url="http://127.0.0.1:8080",
        llamacpp_model="lfm3",
        llamacpp_backup_model="",
        discovery_port=0,
        remote_detect=False,
    )
    base.update(overrides)
    return Settings(**base)


def _block_nonlocal(monkeypatch) -> None:
    """Fail the test the moment any code resolves/connects to a non-local address."""
    real_getaddrinfo = socket.getaddrinfo
    real_connect = socket.socket.connect
    real_create = socket.create_connection

    def is_local(host) -> bool:
        h = str(host).split("%")[0]
        try:
            ip = ipaddress.ip_address(h)
        except ValueError:
            low = h.lower().rstrip(".")
            return low == "localhost" or low.endswith(".local")
        if getattr(ip, "ipv4_mapped", None):
            ip = ip.ipv4_mapped
        return bool(ip.is_loopback or ip.is_private or ip.is_link_local)

    def guarded_getaddrinfo(host, port, *args, **kwargs):
        if not is_local(host):
            raise AssertionError(f"non-local getaddrinfo: {host}")
        return real_getaddrinfo(host, port, *args, **kwargs)

    def guarded_connect(self, address, *args, **kwargs):
        host = address[0] if isinstance(address, (tuple, list)) else address
        if not is_local(host):
            raise AssertionError(f"non-local connect: {host}")
        return real_connect(self, address, *args, **kwargs)

    def guarded_create_connection(address, *args, **kwargs):
        host = address[0] if isinstance(address, (tuple, list)) else address
        if not is_local(host):
            raise AssertionError(f"non-local create_connection: {host}")
        return real_create(address, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket, "create_connection", guarded_create_connection)


# ------------------------------------------------------------------ proof test


def test_private_mode_blocks_every_outbound_path(monkeypatch, tmp_path):
    _block_nonlocal(monkeypatch)
    cfg = _settings(tmp_path)
    private_mode.init(cfg)  # enabled from settings.private_mode=True

    models = Models(cfg, client=private_mode.client(transport=httpx.MockTransport(_local_llm)))
    core = MazCore(cfg, client=private_mode.client(transport=httpx.MockTransport(_benign)))
    telemetry = SystemTelemetry(cfg, client=private_mode.client(transport=httpx.MockTransport(_benign)))
    nudge = NudgeClient(cfg, client=private_mode.client(transport=httpx.MockTransport(_benign)))
    updater = SelfUpdater(enabled=True, http=private_mode.client(transport=httpx.MockTransport(_forbidden)))

    app = create_app(
        cfg,
        stt=_FakeStt(),
        models=models,
        core=core,
        telemetry=telemetry,
        nudge=nudge,
        pc=_FakePC(),
        updater=updater,
    )

    with TestClient(app) as c:
        h = {"Authorization": f"Bearer {TOKEN}"}

        # health: the device/status poll payload carries the flag
        health = c.get("/health", headers=h)
        assert health.status_code == 200
        assert health.json()["private_mode"] is True

        # chat/ask via a fake local engine (MockTransport), local-only routing
        sid = c.post("/session/start", headers=h).json()["session_id"]
        turn = c.post("/turn/text", headers=h, json={"session_id": sid, "route": "auto", "text": "hi"})
        assert turn.status_code == 200
        assert turn.json()["provider"] == "local:lfm3"
        assert turn.json()["reply"] == "local says hi"

        # an explicit cloud route is refused with a clear code, never dialled
        blocked = c.post(
            "/turn/text", headers=h,
            json={"session_id": sid, "route": "cloud", "text": "hi"},
        )
        assert blocked.status_code == 403
        assert blocked.json()["error"] == ErrorCode.PRIVATE_MODE.value

        # needs queue (its `gh pr list` must skip, not dial GitHub)
        assert c.get("/needs", headers=h).status_code == 200

    # self-update tick: skipped cleanly, no GitHub call
    result = updater.check()
    assert result["last_result"] == "skipped_private_mode"

    # telemetry tick: local-only probes (mocked here), no crash
    assert telemetry.snapshot()["ok"] is True

    # live brain model list: OpenRouter fetch is skipped in private mode
    assert asyncio.run(LiveBrain(cfg)._models()) == []


def test_private_mode_off_keeps_cloud_route(monkeypatch, tmp_path):
    """When private mode is off, an explicit cloud route still works (guard is a no-op)."""
    cfg = _settings(tmp_path, private_mode=False)
    private_mode.init(cfg)

    def cloud(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"model": "cloud-model", "choices": [{"message": {"content": "cloud says hi"}}]})

    models = Models(
        Settings(
            token=TOKEN, private_mode=False, _env_file=None,
            cloud_key="k", cloud_url="https://api.example.com/v1", cloud_model="cloud-model",
        ),
        client=httpx.Client(transport=httpx.MockTransport(cloud)),
    )
    text, provider = models.chat([{"role": "user", "content": "hi"}], "cloud")
    assert text == "cloud says hi"
    assert provider == "cloud"


def test_no_local_engine_is_a_clear_error():
    cfg = _settings(Path("unused"), llamacpp_model="", llamacpp_backup_model="")
    private_mode.set_enabled(True)
    m = Models(cfg)
    with pytest.raises(RouteError) as caught:
        m.chat([{"role": "user", "content": "hi"}], "auto")
    assert caught.value.code == ErrorCode.PRIVATE_MODE


# -------------------------------------------------------------- privacy routes


def test_privacy_endpoint_flips_and_reports(tmp_path):
    cfg = _settings(tmp_path, private_mode=False)
    private_mode.init(cfg)
    app = create_app(cfg, stt=_FakeStt(), pc=_FakePC())
    h = {"Authorization": f"Bearer {TOKEN}"}

    with TestClient(app) as c:
        assert c.get("/privacy").status_code == 401  # bearer-protected like the rest

        off = c.get("/privacy", headers=h)
        assert off.status_code == 200
        assert off.json()["private_mode"] is False
        assert off.json()["outbound"] == "cloud_optional"

        on = c.post("/privacy", headers=h, json={"private_mode": True})
        assert on.status_code == 200
        assert on.json()["private_mode"] is True
        assert on.json()["outbound"] == "none"
        assert on.json()["cloud_services_in_use"] == []

        # persisted: a fresh init from the same data dir still reports private
        private_mode.init(cfg)
        assert private_mode.enabled() is True
        assert c.get("/privacy", headers=h).json()["private_mode"] is True

        back = c.post("/privacy", headers=h, json={"private_mode": False})
        assert back.json()["private_mode"] is False
