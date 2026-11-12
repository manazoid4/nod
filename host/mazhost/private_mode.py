"""Private mode: Piblo Core makes no internet requests while it is on.

When private mode is on, Core permits requests only to
loopback, RFC1918/private-LAN, link-local, IPv6 loopback/ULA, ``localhost`` and
``.local`` (mDNS) hosts are allowed. Every httpx client Core creates goes through
``client()``/``async_client()`` here, so a request can only reach a socket after
``guard()`` has passed it. Raw ``httpx.get``/``httpx.post``/… must go through
``get()``/``post()`` too, and the static test in ``test_private_mode.py`` fails
the build if any other module under ``host/mazhost/`` constructs a client or
calls httpx directly. See PRIVATE-MODE.md for the resolver and runtime limits.
"""

from __future__ import annotations

import ipaddress
import json
import threading
from pathlib import Path
from urllib.parse import urlsplit

import httpx


class PrivateModeError(RuntimeError):
    """Raised when private mode blocks a non-local (outbound) request."""


_lock = threading.Lock()
_persistence_lock = threading.Lock()
_enabled = False


def enabled() -> bool:
    with _lock:
        return _enabled


def set_enabled(value: bool) -> None:
    global _enabled
    with _lock:
        _enabled = bool(value)


# --- persistence ---

def _data_dir(settings) -> Path:
    if settings.data_dir:
        return Path(settings.data_dir).expanduser()
    return Path(__file__).resolve().parent.parent / "data"  # host/data in the install dir


def _prefs_file(settings) -> Path:
    return _data_dir(settings) / "settings.json"


def init(settings) -> bool:
    """Set the runtime state from the persisted pref, falling back to MAZ_PRIVATE_MODE."""
    value = bool(settings.private_mode)
    try:
        path = _data_dir(settings) / "private-mode.json"
        if not path.exists():
            path = _prefs_file(settings)
        data = json.loads(path.read_text("utf-8"))
        if isinstance(data, dict) and "private_mode" in data:
            value = bool(data["private_mode"])
    except (OSError, ValueError):
        pass
    set_enabled(value)
    return value


def save(settings, value: bool) -> None:
    """Flip private mode and persist it so it survives a restart (no reboot needed)."""
    path = _data_dir(settings) / "private-mode.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with _persistence_lock:
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"private_mode": bool(value)}, indent=2), "utf-8")
        tmp.replace(path)
        set_enabled(value)


# --- local-address check -------------------------------------------------

def _host(url: str) -> str:
    """Extract the host of a URL or bare hostname (lowercase, no brackets, no port).

    Handles bare IPv6 (``::1``) that ``urlsplit`` mis-parses as host/port.
    """
    url = url.strip()
    if "://" in url:
        try:
            return (urlsplit(url).hostname or "").lower()
        except ValueError:
            return ""
    authority = url.split("/", 1)[0].split("?")[0].split("#")[0]
    if authority.startswith("["):
        end = authority.find("]")
        return authority[1:end] if end != -1 else authority[1:]
    try:  # literal IP first, so bare IPv6 "::1" is not mistaken for host:port
        ipaddress.ip_address(authority.split("%")[0])
        return authority.split("%")[0]
    except ValueError:
        pass
    return authority.rsplit(":", 1)[0]


def is_local_url(url: str) -> bool:
    """True for loopback, RFC1918, link-local, IPv6 loopback/ULA, localhost, .local.

    Hostnames that are not literal IPs and not ``localhost``/``.local`` count as
    NOT local. No DNS lookup is ever performed here.
    """
    host = _host(url or "").strip().lower().rstrip(".")
    if not host:
        return False
    if host == "localhost" or host.endswith(".local"):
        # .local trusts the host resolver/mDNS: a misconfigured or hostile resolver
        # can return a public IP. This is a request guard, not an OS firewall.
        return True
    try:
        ip = ipaddress.ip_address(host.split("%")[0])
    except ValueError:
        return False  # a real hostname that is not localhost/.local → not local
    if getattr(ip, "ipv4_mapped", None):
        ip = ip.ipv4_mapped
    return bool(ip.is_loopback or ip.is_private or ip.is_link_local)


def guard(url: str) -> None:
    """Raise when private mode is on and ``url`` is not local."""
    if enabled() and not is_local_url(url):
        host = (urlsplit(url if "://" in url else "//" + url).hostname) or url
        raise PrivateModeError(f"private mode: outbound request blocked: {host}")


def guard_subprocess(name: str, *, local: bool = False) -> None:
    """Unknown code/CLIs cannot be constrained by Core's HTTP transport guard."""
    if enabled() and not local:
        raise PrivateModeError(f"PRIVATE_MODE: subprocess blocked: {name}")


# --- guarded transports and clients --------------------------------------

class GuardedTransport(httpx.BaseTransport):
    def __init__(self, transport: httpx.BaseTransport | None = None) -> None:
        self._transport = transport or httpx.HTTPTransport()

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        guard(str(request.url))
        return self._transport.handle_request(request)


class GuardedAsyncTransport(httpx.AsyncBaseTransport):
    def __init__(self, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._transport = transport or httpx.AsyncHTTPTransport()

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        guard(str(request.url))
        return await self._transport.handle_async_request(request)


def client(**kwargs) -> httpx.Client:
    transport = kwargs.pop("transport", None)
    return httpx.Client(transport=GuardedTransport(transport), **kwargs)


def async_client(**kwargs) -> httpx.AsyncClient:
    transport = kwargs.pop("transport", None)
    return httpx.AsyncClient(transport=GuardedAsyncTransport(transport), **kwargs)


def get(url: str, **kwargs) -> httpx.Response:
    """Guarded one-shot GET (replaces bare ``httpx.get`` in non-transport call sites)."""
    guard(url)
    return httpx.get(url, **kwargs)


# --- privacy status ------------------------------------------------------

def cloud_services(settings) -> list[str]:
    """Names of cloud services configured for use (only meaningful when private mode is off)."""
    services: list[str] = []
    if settings.groq_key or settings.groq_api_key:
        services.append("Groq")
    if settings.openrouter_api_key:
        services.append("OpenRouter")
    if settings.cloud_key:
        services.append("Cloud")
    if settings.fish_api_key:
        services.append("Fish TTS")
    if settings.autoupdate:
        services.append("Self-update (GitHub)")
    if settings.bridge_enabled:
        services.append("GitHub bridge")
    return services
