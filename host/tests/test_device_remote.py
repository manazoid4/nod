"""Remote device control: PNG encoder and /api/key forwarding."""
import struct
import zlib

import httpx
import pytest

from mazhost.config import Settings
from mazhost.core import CoreError, MazCore


def _service(handler, **kw):
    settings = Settings(token="t" * 32, cardputer_url="http://piblo.local", **kw)
    return MazCore(settings, client=httpx.Client(transport=httpx.MockTransport(handler)))


def _chunks(png):
    pos = 8
    out = {}
    while pos < len(png):
        (length,) = struct.unpack(">I", png[pos:pos + 4])
        kind = png[pos + 4:pos + 8]
        data = png[pos + 8:pos + 8 + length]
        out.setdefault(kind.decode(), []).append(data)
        pos += 12 + length
    return out


def test_png_encoder_produces_valid_png():
    frame = b"\x00" * (240 * 135 * 2)
    png = MazCore.rgb565_to_png(frame)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    chunks = _chunks(png)
    # IHDR: 240x135, 8-bit, truecolor RGB (no alpha).
    assert struct.unpack(">IIBBBBB", chunks["IHDR"][0]) == (240, 135, 8, 2, 0, 0, 0)
    # IDAT: one filter byte + 3 bytes per pixel per scanline, decompresses cleanly.
    assert len(chunks["IDAT"]) == 1
    raw = zlib.decompress(chunks["IDAT"][0])
    assert len(raw) == 135 * (1 + 240 * 3)
    assert set(chunks) == {"IHDR", "IDAT", "IEND"}


def test_png_encoder_rejects_wrong_sized_frame():
    with pytest.raises(CoreError):
        MazCore.rgb565_to_png(b"\x00" * 100)


def test_key_route_forwards_to_device():
    got = {}

    def handler(request):
        got["path"] = request.url.path
        got["body"] = request.content.decode()
        got["token"] = request.headers.get("X-MAZ-Token")
        return httpx.Response(200, json={"ok": True, "sent": 9})

    svc = _service(handler)
    out = svc.cardputer_key("down right*7 esc")
    assert got["path"] == "/api/key"
    assert got["body"] == "keys=down+right%2A7+esc"
    assert got["token"] == "t" * 32
    assert out == {"ok": True, "sent": 9}