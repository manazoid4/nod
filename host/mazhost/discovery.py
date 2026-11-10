"""UDP LAN discovery for Piblo device pairing (docs/protocol/DEVICE-PAIRING.md section 1).

Replies carry no secret. Never raises into Core: failures are logged and ignored.
"""
from __future__ import annotations

import json
import logging
import socket
import threading

from .security import is_lan_ip
from .version import CORE_VERSION

log = logging.getLogger("uvicorn.error")
DISCOVER_LINE = b"PIBLO-DISCOVER 1\n"


class DiscoveryResponder:
    def __init__(self, discovery_port: int, core_port: int) -> None:
        self.discovery_port = discovery_port
        self.core_port = core_port
        self.bound_port = 0
        self._sock: socket.socket | None = None

    def start(self) -> None:
        if self.discovery_port == 0 or self._sock is not None:
            return
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("0.0.0.0", self.discovery_port))
        except OSError as exc:
            log.warning("Piblo discovery disabled: %s", exc)
            return
        self._sock = sock
        self.bound_port = sock.getsockname()[1]
        threading.Thread(target=self._serve, args=(sock,), name="piblo-discovery", daemon=True).start()

    def stop(self) -> None:
        sock, self._sock = self._sock, None
        if sock is not None:
            sock.close()  # makes recvfrom raise, ending the thread

    def _serve(self, sock: socket.socket) -> None:
        reply = json.dumps(
            {"piblo": 1, "port": self.core_port, "name": socket.gethostname()[:32], "version": CORE_VERSION},
            separators=(",", ":"),
        ).encode() + b"\n"
        while self._sock is sock:
            try:
                data, (ip, port) = sock.recvfrom(256)
                if data == DISCOVER_LINE and is_lan_ip(ip):
                    sock.sendto(reply, (ip, port))
            except OSError:
                if self._sock is not sock:
                    return
            except Exception:  # noqa: BLE001 - must never crash Core
                log.exception("Piblo discovery error")
