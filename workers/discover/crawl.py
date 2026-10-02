"""Crawl orchestration: seeds x platforms -> source chain (sources.PRIORITY) -> requests -> items -> dedupe ->
top performers within the daily budget (500-1,000/day) or the hourly stream window.

All I/O goes through injected callables, so tests run with fixtures and no network:
  fetch(req)  -> {"status": int, "json": ..., "text": str}     (HTTP; crawl adds no cookies, the live fetcher refuses them)
  run(argv)   -> str                                             (yt-dlp metadata JSON lines)
  clock()     -> float seconds;  sleep(s) -> None               (rate limiting)
Live use needs DISCOVER_LIVE=1 (live_fetcher / live_runner refuse otherwise).

Politeness and terms, enforced here, not left to the caller:
  * public_page requests: host must not be in tos_blocked_hosts, robots.txt must allow the path for our user agent
    (robots fetch failure = disallow), Crawl-delay honoured, per-host minimum interval, https only, no auth/cookies
  * every request: per-host token spacing (min_interval_s), a hard request cap per run
  * yt-dlp: metadata flags only; any cookie / credential flag is refused
"""
from __future__ import annotations

import os
import time
import urllib.robotparser
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from discover import normalize, sources as SRC

LIVE = os.environ.get("DISCOVER_LIVE", "0") == "1"


class Refused(Exception):
    pass


def _host_blocked(host: str | None, cfg: dict) -> bool:
    h = (host or "").lower()
    return any(h == b or h.endswith("." + b) for b in cfg["tos_blocked_hosts"])


class Crawler:
    def __init__(self, fetch=None, run=None, *, env: dict | None = None, cfg: dict | None = None, clock=None,
                 sleep=None, max_requests: int = 5000):
        self.fetch, self.run = fetch, run
        self.env = dict(env if env is not None else os.environ)
        self.cfg = {**SRC.DEFAULTS, **(cfg or {})}
        self.clock, self.sleep = clock or time.monotonic, sleep or time.sleep
        self.max_requests = max_requests
        self.last: dict[str, float] = {}
        self.robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.log: list[dict] = []
        self.n_requests = 0

    # ---------------------------------------------------------------- politeness
    def _interval(self, host: str) -> float:
        mi = self.cfg["min_interval_s"]
        base = float(mi.get(host, mi["default"]))
        rp = self.robots.get(host)
        cd = rp.crawl_delay(self.cfg["user_agent"]) if rp else None
        return max(base, float(cd or 0))

    def _wait(self, host: str):
        gap = self._interval(host)
        if host in self.last:
            due = self.last[host] + gap - self.clock()
            if due > 0:
                self.sleep(due)
        self.last[host] = self.clock()

    def _robots(self, host: str) -> urllib.robotparser.RobotFileParser | None:
        if host in self.robots:
            return self.robots[host]
        rp = None
        try:
            self._wait(host)
            self.n_requests += 1
            r = self.fetch({"source": "robots", "method": "GET", "url": f"https://{host}/robots.txt", "host": host,
                            "kind": "robots"})
            if r and int(r.get("status", 0)) == 200:
                rp = urllib.robotparser.RobotFileParser()
                rp.parse(str(r.get("text") or "").splitlines())
            elif r and 400 <= int(r.get("status", 0)) < 500:
                rp = urllib.robotparser.RobotFileParser()     # RFC 9309: 4xx = no restrictions
                rp.parse([])
        except Exception:      # noqa: BLE001  unreachable robots.txt = disallow (RFC 9309 §2.3.1.4)
            rp = None
        self.robots[host] = rp
        return rp

    def check(self, req: dict) -> None:
        """Raise Refused for anything outside policy."""
        if self.n_requests >= self.max_requests:
            raise Refused("request cap reached")
        if req.get("kind") == "ytdlp":
            bad = [a for a in req["argv"] if a in SRC.YtDlp.FORBIDDEN]
            if bad or "--skip-download" not in req["argv"]:
                raise Refused(f"yt-dlp flags not allowed: {bad or 'download'}")
            return
        url = req.get("url") or ""
        if not url.startswith("https://"):
            raise Refused("https only")
        hdrs = {k.lower() for k in (req.get("headers") or {})}
        if "cookie" in hdrs or (req.get("kind") == "public" and "authorization" in hdrs):
            raise Refused("no cookies / auth on public pages")
        if req.get("kind") == "public":
            host = urlparse(url).hostname or ""
            if _host_blocked(host, self.cfg):
                raise Refused(f"{host}: terms forbid automated collection")
            rp = self._robots(host)
            if rp is None or not rp.can_fetch(self.cfg["user_agent"], url):
                raise Refused(f"robots.txt disallows {url}")

    # ---------------------------------------------------------------- one request
    def _do(self, req: dict):
        self.check(req)
        self.n_requests += 1
        if req.get("kind") == "ytdlp":
            if self.run is None:
                raise Refused("no yt-dlp runner")
            return self.run(req["argv"])
        self._wait(req.get("host") or "")
        r = self.fetch(req) if self.fetch else None
        if not r or int(r.get("status", 0)) != 200:
            raise Refused(f"HTTP {r.get('status') if r else 'none'}")
        return r.get("json") if r.get("json") is not None else r.get("text")

    def collect(self, seed: dict, platform: str, since: datetime, until: datetime, *,
                allow_public: bool = True) -> list[dict]:
        """First source in the platform chain that yields items wins; later ones are fallbacks."""
        for src in SRC.chain(platform, self.env):
            if src.kind == "public" and not allow_public:
                continue
            items, queue = [], src.requests({**seed, "platform": seed.get("platform") or platform}, since, until, self.env)
            ok = False
            while queue:
                req = queue.pop(0)
                try:
                    payload = self._do(req)
                except Refused as e:
                    self.log.append({"seed": seed.get("id"), "platform": platform, "source": src.name, "refused": str(e)})
                    continue
                ok = True
                got, more = src.parse(payload, req)
                items += got
                queue += more
            if ok and items:
                self.log.append({"seed": seed.get("id"), "platform": platform, "source": src.name, "items": len(items)})
                return items
        return []


def seed_targets(seeds: dict, platforms=SRC.PLATFORMS) -> list[tuple[dict, str]]:
    """(seed, platform) pairs: queries run on every platform; creators on their own platform. A creator still marked
    to_verify is crawled only through an official API or yt-dlp (which resolve the handle), never the public fallback."""
    out = []
    for q in seeds.get("queries", []):
        for p in platforms:
            out.append(({**q, "type": "query"}, p))
    for c in seeds.get("creators", []):
        if c.get("platform") in platforms:
            out.append(({**c, "type": "creator"}, c["platform"]))
    return out


def dedupe(items: list[dict]) -> list[dict]:
    """One row per (platform, id); a repeat keeps the richer read (more filled metrics, then more views)."""
    best: dict[tuple, dict] = {}
    for it in items:
        if not it.get("id") or not it.get("platform"):
            continue
        k = (it["platform"], str(it["id"]))
        filled = sum(it.get(f) is not None for f in ("views", "likes", "comments", "shares", "saves"))
        cur = best.get(k)
        if cur is None or (filled, it.get("views") or 0) > cur[0]:
            best[k] = ((filled, it.get("views") or 0), it)
    return [v[1] for v in best.values()]


def run(seeds: dict, crawler: Crawler, *, now: datetime | None = None, mode: str = "daily",
        platforms=SRC.PLATFORMS) -> dict:
    """mode daily: last window_days, keep the top daily_max_posts by relative performance (report shortfall under
    daily_min_posts). mode stream: last stream_window_h hours, keep everything new (velocity snapshots)."""
    cfg = crawler.cfg
    now = now or datetime.now(timezone.utc)
    since = now - (timedelta(hours=float(cfg["stream_window_h"])) if mode == "stream" else timedelta(days=int(cfg["window_days"])))
    raw = []
    for seed, platform in seed_targets(seeds, platforms):
        unverified = seed.get("type") == "creator" and seed.get("status") == "to_verify"
        raw += crawler.collect(seed, platform, since, now, allow_public=not unverified)
    items = [i for i in dedupe(raw) if (normalize.parse_dt(i.get("published_at")) or now) >= since]
    rows = normalize.rows(items, now=now)
    rows = [r for r in rows if r["niche_match"] or r.get("seed_kind") == "creator"]
    rows.sort(key=lambda r: (-(r["rel_perf"] or 0), -(r["views"] or 0), r["platform"], r["id"]))
    if mode == "daily":
        rows = rows[: int(cfg["daily_max_posts"])]
    return {"mode": mode, "since": since.isoformat(), "until": now.isoformat(), "rows": rows,
            "counts": {"raw": len(raw), "deduped": len(items), "kept": len(rows), "requests": crawler.n_requests,
                       "refused": sum(1 for l in crawler.log if "refused" in l),
                       "by_platform": {p: sum(1 for r in rows if r["platform"] == p) for p in platforms}},
            "shortfall": max(0, int(cfg["daily_min_posts"]) - len(rows)) if mode == "daily" else 0,
            "log": crawler.log}


# ---------------------------------------------------------------- live I/O (refuses unless DISCOVER_LIVE=1)
def public_host_ok(host: str) -> bool:
    """A public-page seed may only point at a routable internet host: no literal loopback/link-local/private
    addresses, no `localhost`, and every resolved address must be global (metadata endpoints and LAN hosts refused)."""
    import ipaddress
    import socket

    h = (host or "").strip("[]").lower()
    if not h or h == "localhost" or h.endswith(".localhost") or h.endswith(".internal") or h.endswith(".local"):
        return False
    try:
        return ipaddress.ip_address(h).is_global
    except ValueError:
        pass
    try:
        infos = socket.getaddrinfo(h, 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False
    addrs = {ipaddress.ip_address(i[4][0]) for i in infos}
    return bool(addrs) and all(a.is_global for a in addrs)


class _RefuseRedirect(__import__("urllib.request").request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):   # noqa: D401
        raise Refused(f"redirect refused ({code} -> {urlparse(newurl).hostname})")


_opener = __import__("urllib.request").request.build_opener(_RefuseRedirect())


def live_fetcher(env: dict | None = None, timeout_s: float = 20.0, max_bytes: int = 2_000_000):
    """urllib fetcher: https only, no cookie jar, no redirects to other hosts, bearer/key from env by name only."""
    import json as _json
    import urllib.request

    env = dict(env if env is not None else os.environ)

    def fetch(req: dict) -> dict:
        if not LIVE and env.get("DISCOVER_LIVE") != "1":
            raise Refused("DISCOVER_LIVE is off")
        url = req["url"]
        if not url.startswith("https://"):
            raise Refused("https only")
        headers = {"User-Agent": SRC.DEFAULTS["user_agent"], "Accept": "application/json, text/html;q=0.8"}
        if req.get("auth_env") == "YOUTUBE_API_KEY":
            url += ("&" if "?" in url else "?") + "key=" + env["YOUTUBE_API_KEY"]
        elif req.get("auth_env"):
            headers["Authorization"] = "Bearer " + env[req["auth_env"]]
        data = _json.dumps(req["json"]).encode() if req.get("json") is not None else None
        if data:
            headers["Content-Type"] = "application/json"
        host = urlparse(url).hostname or ""
        if req.get("kind") == "public" and not public_host_ok(host):
            raise Refused(f"{host}: not a public internet host")
        r = urllib.request.Request(url, data=data, headers=headers, method=req.get("method", "GET"))
        # Round 6: redirects are refused BEFORE they are followed (a redirect to another host, or to a private
        # address, would otherwise be fetched, bearer header included, before the old post-hoc check ran).
        with _opener.open(r, timeout=timeout_s) as resp:       # noqa: S310  https checked above
            if urlparse(resp.geturl()).hostname != host:
                raise Refused("cross-host redirect")
            body = resp.read(max_bytes + 1)[:max_bytes].decode("utf-8", "replace")
            ctype = resp.headers.get("Content-Type", "")
            return {"status": resp.status, "text": body,
                    "json": _json.loads(body) if "json" in ctype else None}
    return fetch


def live_runner(timeout_s: float = 300.0):
    import subprocess

    def run(argv: list[str]) -> str:
        if not LIVE:
            raise Refused("DISCOVER_LIVE is off")
        return subprocess.run(argv, capture_output=True, text=True, timeout=timeout_s, check=False).stdout
    return run


def from_payloads(pushed: list[dict], *, now: datetime | None = None, mode: str = "daily", cfg: dict | None = None) -> dict:
    """Offline path (default): n8n (or a researcher export) pushes raw source payloads [{source, payload, request?}];
    they are parsed by the same adapters, deduped, normalised and budgeted exactly like a live run."""
    c = {**SRC.DEFAULTS, **(cfg or {})}
    now = now or datetime.now(timezone.utc)
    since = now - (timedelta(hours=float(c["stream_window_h"])) if mode == "stream" else timedelta(days=int(c["window_days"])))
    raw, skipped = [], []
    for p in pushed or []:
        src = SRC.REGISTRY.get(str(p.get("source")))
        if src is None:
            skipped.append({"source": p.get("source"), "reason": "unknown source"})
            continue
        req = {"step": "videos", "seed": p.get("seed"), "platform": p.get("platform"), "url": p.get("url"),
               **(p.get("request") or {})}
        got, _ = src.parse(p.get("payload"), req)
        raw += got
    items = [i for i in dedupe(raw) if (normalize.parse_dt(i.get("published_at")) or now) >= since]
    rows = [r for r in normalize.rows(items, now=now) if r["niche_match"] or r.get("seed_kind") == "creator"]
    rows.sort(key=lambda r: (-(r["rel_perf"] or 0), -(r["views"] or 0), r["platform"], r["id"]))
    if mode == "daily":
        rows = rows[: int(c["daily_max_posts"])]
    return {"mode": mode, "since": since.isoformat(), "until": now.isoformat(), "rows": rows, "skipped": skipped,
            "counts": {"raw": len(raw), "deduped": len(items), "kept": len(rows),
                       "by_platform": {p: sum(1 for r in rows if r["platform"] == p) for p in SRC.PLATFORMS}},
            "shortfall": max(0, int(c["daily_min_posts"]) - len(rows)) if mode == "daily" else 0}
