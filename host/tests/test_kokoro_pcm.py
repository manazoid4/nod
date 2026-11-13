import http.client
import threading

import numpy as np

from mazhost.kokoro_pcm import RATE, make_server


def _get(port, path):
    c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    c.request("GET", path)
    r = c.getresponse()
    return r, r.read()


def _serve(synth):
    srv = make_server(synth, "127.0.0.1", 0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def test_pcm_body_http10_no_chunking():
    calls = []

    def fake(sentence):
        calls.append(sentence)
        return np.full(RATE // 10, 0.5, dtype=np.float32)

    srv = _serve(fake)
    try:
        r, body = _get(srv.server_port, "/?text=Hello%20there.%20How%20are%20you%3F")
    finally:
        srv.shutdown()
    assert r.status == 200 and r.version == 10
    assert r.getheader("Transfer-Encoding") is None and r.getheader("Content-Length") is None
    assert calls == ["Hello there.", "How are you?"]
    assert len(body) == 2 * (RATE // 10) * 2
    assert np.frombuffer(body, "<i2")[0] == 16383


def test_bad_input_400_and_missing_model_503():
    srv = _serve(lambda s: np.zeros(10, dtype=np.float32))
    try:
        assert _get(srv.server_port, "/?text=")[0].status == 400
        assert _get(srv.server_port, "/")[0].status == 400
        assert _get(srv.server_port, "/?text=" + "a" * 1001)[0].status == 400
    finally:
        srv.shutdown()

    class Missing:
        def check(self):
            raise RuntimeError("Kokoro model files missing")

    srv = _serve(Missing())
    try:
        r, body = _get(srv.server_port, "/?text=hi")
    finally:
        srv.shutdown()
    assert r.status == 503 and b"missing" in body
