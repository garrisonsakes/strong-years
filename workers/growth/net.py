"""SSRF-safe JSON calls to the platform analytics APIs (same policy as common/storage.fetch, AUDIT H9).

  * off unless GROWTH_LIVE_METRICS=1 (tests and fixture mode never reach this)
  * https only; the host must be on METRICS_ALLOWED_HOSTS (exact match, no wildcards: these are fixed API hosts)
  * every resolved IP must be public (no loopback / private / link-local / reserved / multicast)
  * redirects are refused, not followed; response bytes and time are capped
  * tokens travel in the Authorization header only, never in the URL (so they never land in access logs)
"""
from __future__ import annotations

import json
import re
import socket
from urllib.parse import urlparse

import httpx

from common.storage import _public_ip
from growth import config as G

MAX_BYTES = 2 * 1024 * 1024
TIMEOUT_S = 20.0


class NetPolicyError(ValueError):
    """Rejected by the growth network policy (maps to HTTP 422, no internals)."""


_ID_RX = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")


def safe_id(x) -> str:
    """A platform post/media id that may go into a URL path (AUDIT L13: never string-interpolate raw input)."""
    s = str(x or "")
    if not _ID_RX.match(s):
        raise NetPolicyError("invalid platform id")
    return s


def resolve(host: str, port: int) -> list[str]:  # pragma: no cover - replaced in tests; real DNS in production
    return [i[4][0] for i in socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)]


def check_url(url: str) -> None:
    u = urlparse(url)
    if u.scheme != "https":
        raise NetPolicyError("only https analytics URLs are allowed")
    host = (u.hostname or "").lower().rstrip(".")
    if not host or host not in G.METRICS_ALLOWED_HOSTS:
        raise NetPolicyError("analytics host is not on METRICS_ALLOWED_HOSTS")
    if u.username or u.password:
        raise NetPolicyError("credentials in URLs are not allowed")
    try:
        ips = resolve(host, u.port or 443)
    except OSError as e:
        raise NetPolicyError("analytics host does not resolve") from e
    if not ips or not all(_public_ip(ip) for ip in ips):
        raise NetPolicyError("analytics host resolves to a non-public address")


def request_json(method: str, url: str, *, token: str | None = None, params: dict | None = None,
                 body: dict | None = None, client: httpx.Client | None = None) -> dict:
    if not G.GROWTH_LIVE_METRICS:
        raise NetPolicyError("live metrics are disabled (GROWTH_LIVE_METRICS=0)")
    check_url(url)
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    own = client is None
    client = client or httpx.Client(timeout=TIMEOUT_S, follow_redirects=False)
    try:
        with client.stream(method, url, params=params, json=body, headers=headers) as r:
            if 300 <= r.status_code < 400:
                raise NetPolicyError("analytics API redirected: refused")
            buf = bytearray()
            for chunk in r.iter_bytes(1 << 15):
                buf += chunk
                if len(buf) > MAX_BYTES:
                    raise NetPolicyError("analytics response exceeds the byte cap")
            if r.status_code >= 400:
                raise NetPolicyError(f"analytics API error: HTTP {r.status_code}")
        try:
            data = json.loads(bytes(buf) or b"{}")
        except ValueError as e:
            raise NetPolicyError("analytics API returned non-JSON") from e
        if not isinstance(data, dict):
            raise NetPolicyError("analytics API returned an unexpected shape")
        return data
    except httpx.HTTPError as e:
        raise NetPolicyError(f"analytics request failed: {e.__class__.__name__}") from e
    finally:
        if own:
            client.close()
