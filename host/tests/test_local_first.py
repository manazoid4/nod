"""MAZ_BRAIN_ORDER=local_first: local llama.cpp first, bounded, then free cloud."""
from __future__ import annotations

import socket
import time

import httpx
import pytest

from mazhost.config import Settings
from mazhost.errors import ErrorCode, RouteError
from mazhost.llm import LOCAL_FIRST_CHAIN, Models

LOCAL = "http://127.0.0.1:8080"
MSG = [{"role": "user", "content": "hi"}]


def settings(**values):
    base = dict(
        token="test-token-that-is-not-default",
        local_engine="llamacpp",
        llamacpp_url=LOCAL,
        llamacpp_model="lfm3",
        llamacpp_backup_model="maz-fast",  # label on the SAME server, like MAZPC
        brain_order="local_first",
        local_first_timeout_s=5.0,
        groq_key="g",
        groq_models="groq-a,groq-b,groq-c",
        openrouter_api_key="o",
        _env_file=None,
    )
    base.update(values)
    return Settings(**base)


def completion(text: str, model: str = "m") -> httpx.Response:
    return httpx.Response(200, json={"model": model, "choices": [{"message": {"content": text}}]})


class Upstream:
    """Mock transport: per-host behaviour + a log of every request."""

    def __init__(self, *, health=200, local="local says hi", groq="groq says hi", openrouter="or says hi"):
        self.health, self.local, self.groq, self.openrouter = health, local, groq, openrouter
        self.calls: list[str] = []
        self.local_timeout: float | None = None

    @staticmethod
    def _act(action, ok):
        if isinstance(action, Exception):
            raise action
        if isinstance(action, int):
            return httpx.Response(action, json={"error": "x"})
        return ok(action)

    def __call__(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        self.calls.append(f"{request.method} {url}")
        if url == f"{LOCAL}/health":
            return self._act(self.health, lambda _: httpx.Response(200, json={"status": "ok"}))
        if url == f"{LOCAL}/v1/chat/completions":
            self.local_timeout = request.extensions["timeout"]["read"]
            return self._act(self.local, completion)
        if "api.groq.com" in url:
            return self._act(self.groq, completion)
        if "openrouter.ai" in url:
            return self._act(self.openrouter, completion)
        return httpx.Response(404)

    def hits(self, fragment: str) -> int:
        return sum(fragment in c for c in self.calls)


def models(up: Upstream, **values) -> Models:
    return Models(settings(**values), client=httpx.Client(transport=httpx.MockTransport(up)))


def test_chain_is_local_first_and_drops_same_server_backup():
    chain = models(Upstream())._effective_auto_chain()
    assert chain[0] == "local_fast"
    assert chain[1:4] == ("groq", "groq_alt", "groq_3")
    assert chain.index("openrouter") > chain.index("groq_3")
    assert "local_smart" not in chain  # maz-fast is the same llama-server
    assert set(chain) <= set(LOCAL_FIRST_CHAIN)


def test_default_order_is_unchanged_cloud_first():
    m = Models(settings(brain_order="cloud_first"))
    assert m._effective_auto_chain()[0] == "groq"
    assert m._effective_auto_chain()[-2:] == ("local_fast", "local_smart")


def test_a_local_answers_first():
    up = Upstream()
    m = models(up)
    text, provider = m.chat(MSG, "auto")
    assert (text, provider) == ("local says hi", "local:lfm3")
    assert up.hits("api.groq.com") == 0
    assert up.local_timeout == 5.0  # bounded by MAZ_LOCAL_FIRST_TIMEOUT_S
    route = m._last_route
    assert route["active"] == "local_fast" and route["fallback"] is False
    assert route["order"] == "local_first"
    assert [a["stage"] for a in route["attempts"]] == ["local_fast"]


def test_b_local_timeout_falls_back_to_groq():
    up = Upstream(local=httpx.ReadTimeout("slow"))
    m = models(up)
    text, provider = m.chat(MSG, "auto")
    assert text == "groq says hi" and provider.startswith("groq:")
    route = m._last_route
    assert route["active"] == "groq" and route["fallback"] is True
    assert route["fallback_reason"] == ErrorCode.UPSTREAM_TIMEOUT.value
    assert route["attempts"][0] == {"stage": "local_fast", "error": "UPSTREAM_TIMEOUT", "ms": route["attempts"][0]["ms"]}


def test_c_local_down_skips_generation_fast():
    up = Upstream(health=httpx.ConnectError("refused"))
    m = models(up)
    started = time.perf_counter()
    text, _ = m.chat(MSG, "auto")
    assert text == "groq says hi"
    assert up.hits(f"{LOCAL}/v1/chat/completions") == 0  # never waited on generation
    assert m._last_route["attempts"][0]["error"] == ErrorCode.LOCAL_UNAVAILABLE.value
    assert m._last_route["attempts"][0]["ms"] < 300
    assert time.perf_counter() - started < 1.0


def test_c_loading_server_503_is_skipped():
    up = Upstream(health=503)
    text, _ = models(up).chat(MSG, "auto")
    assert text == "groq says hi" and up.hits(f"{LOCAL}/v1/chat/completions") == 0


def test_c_real_dead_port_costs_under_300ms():
    # Real socket, no mock: a closed loopback port. Windows retries a refused
    # loopback SYN for ~2 s, so the 250 ms health ceiling is what keeps this fast.
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    m = Models(settings(llamacpp_url=f"http://127.0.0.1:{port}"))
    started = time.perf_counter()
    assert m._local_stage_healthy("local_fast") is False
    assert time.perf_counter() - started < 0.3


def test_groq_down_then_openrouter_free():
    up = Upstream(local=httpx.ReadTimeout("slow"), groq=500)
    m = models(up)
    text, provider = m.chat(MSG, "auto")
    assert text == "or says hi" and provider.startswith("openrouter:")
    assert [a["stage"] for a in m._last_route["attempts"]] == ["local_fast", "groq", "groq_alt", "groq_3", "openrouter"]


def test_d_all_down_is_a_clear_error(caplog):
    up = Upstream(health=httpx.ConnectError("refused"), groq=500, openrouter=503)
    m = models(up)
    with caplog.at_level("INFO", logger="uvicorn.error.brain"):
        with pytest.raises(RouteError) as caught:
            m.chat(MSG, "auto")
    assert caught.value.code == ErrorCode.ROUTE_UNAVAILABLE
    assert m._last_route["active"] == "degraded" and m._last_route["ok"] is False
    assert all("error" in a for a in m._last_route["attempts"])
    assert "brain: order=local_first active=degraded ok=False" in caplog.text
    assert "local_fast:LOCAL_UNAVAILABLE" in caplog.text


def test_paid_cloud_only_when_configured_and_independent():
    plain = models(Upstream())._effective_auto_chain()
    assert "cloud" not in plain  # no cloud_key -> never tried (cloud_url default != 9router, but key empty)
    with_cloud = Models(settings(cloud_key="c"))._effective_auto_chain()
    assert with_cloud.index("cloud") > with_cloud.index("openrouter")


def test_distinct_backup_server_keeps_local_smart_last():
    m = Models(settings(llamacpp_backup_url="http://127.0.0.1:8081"))
    assert m._effective_auto_chain()[-1] == "local_smart"


def test_every_auto_turn_logs_stage_and_latency(caplog):
    m = models(Upstream())
    with caplog.at_level("INFO", logger="uvicorn.error.brain"):
        m.chat(MSG, "auto")
    assert "active=local_fast ok=True" in caplog.text and "local_fast:ok:" in caplog.text
