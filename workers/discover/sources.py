"""Source adapters, in priority order. Each one PLANS requests (pure dicts) and PARSES payloads into canonical niche
items; crawl.py decides which adapter runs, applies robots / rate limits and performs I/O through an injected fetcher.

Priority per platform (first available wins; the rest are fallbacks):
  1. Official APIs, credentialed only:
       youtube      YouTube Data API v3 search.list (type=video, videoDuration=short, order=viewCount, publishedAfter)
                    -> videos.list (snippet, statistics, contentDetails). `engagedViews` is a YouTube Analytics metric
                    available only for channels that authorise us; when a payload carries it, it is the denominator
                    (same rule as growth/scorecard.denominator), else viewCount.
       tiktok       TikTok Research API POST /v2/research/video/query/ (approved researchers only; keyword/username
                    conditions, <= 30-day windows, voice_to_text = transcript).
       instagram    Graph API business_discovery (public business/creator accounts, needs our own IG business user id)
                    and Meta Content Library exports where our access is approved.
       facebook     Meta Content Library (approved access) / Page Public Content Access where granted.
       threads      Threads API keyword_search (threads_keyword_search permission).
       x            X API v2 recent search (paid tier; public_metrics incl. impression_count; 7-day window).
  2. yt-dlp metadata (--dump-json --skip-download, never cookies, never media download): YouTube only by default.
  3. Public-page fallback: robots.txt-allowed pages on hosts whose ToS permits automated access, og:/JSON-LD
     metadata only. Hosts whose terms forbid automated collection are refused outright (config tos_blocked_hosts).
No adapter logs in, sends cookies, uses a private/internal API, bypasses a bot check, or downloads/re-hosts media.
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from urllib.parse import urlencode, urlparse

PLATFORMS = ("instagram", "facebook", "tiktok", "youtube", "threads", "x")

DEFAULTS = {
    "daily_min_posts": 500, "daily_max_posts": 1000, "window_days": 90, "stream_window_h": 2,
    "min_interval_s": {"default": 10.0, "www.googleapis.com": 0.2, "open.tiktokapis.com": 1.0,
                       "graph.facebook.com": 1.0, "graph.threads.net": 1.0, "api.x.com": 1.0},
    "user_agent": "StrongYearsNicheResearch/1.0 (+https://strongyears.example/research; metadata only)",
    "tos_blocked_hosts": ["instagram.com", "facebook.com", "threads.net", "threads.com", "x.com", "twitter.com",
                          "tiktok.com"],
    "ytdlp_platforms": ["youtube"],
    "shorts_max_s": 180,
}
ENV_KEYS = {"youtube_api": ("YOUTUBE_API_KEY",), "tiktok_research": ("TIKTOK_RESEARCH_TOKEN",),
            "meta_graph": ("META_GRAPH_TOKEN", "IG_BUSINESS_USER_ID"), "meta_content_library": ("META_MCL_TOKEN",),
            "threads_api": ("THREADS_TOKEN",), "x_api": ("X_BEARER_TOKEN",)}


def _iso(x) -> str | None:
    if x in (None, ""):
        return None
    if isinstance(x, (int, float)):
        return datetime.fromtimestamp(float(x), tz=timezone.utc).isoformat()
    s = str(x)
    if re.fullmatch(r"\d{8}", s):
        return f"{s[:4]}-{s[4:6]}-{s[6:]}T00:00:00+00:00"
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).isoformat()


def _int(x) -> int | None:
    try:
        return int(float(x)) if x not in (None, "") else None
    except (TypeError, ValueError):
        return None


def iso_duration_s(d: str | None) -> float | None:
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?", d or "")
    if not m or not any(m.groups()):
        return None
    dd, h, mi, s = (float(g) if g else 0.0 for g in m.groups())
    return dd * 86400 + h * 3600 + mi * 60 + s


def item(**kw) -> dict:
    """Canonical niche item (before normalize.py)."""
    base = {"platform": None, "source": None, "id": None, "url": None, "creator": None, "creator_followers": None,
            "published_at": None, "views": None, "engaged_views": None, "likes": None, "comments": None,
            "shares": None, "saves": None, "duration_s": None, "title_or_caption": "", "transcript": "",
            "overlay_text": "", "hashtags": "", "seed": None}
    base.update({k: v for k, v in kw.items() if k in base})
    if not base["hashtags"]:
        base["hashtags"] = " ".join(sorted(set(re.findall(r"#\w+", base["title_or_caption"] or ""))))
    return base


class Source:
    name = "base"
    platforms: tuple[str, ...] = ()
    kind = "api"                 # api | ytdlp | public

    def available(self, env: dict) -> bool:
        return all(env.get(k) for k in ENV_KEYS.get(self.name, ()))

    def requests(self, seed: dict, since: datetime, until: datetime, env: dict) -> list[dict]:
        return []

    def parse(self, payload, req: dict) -> tuple[list[dict], list[dict]]:
        """-> (items, follow-up requests)"""
        return [], []


def _req(source: str, url: str, *, method: str = "GET", params: dict | None = None, body: dict | None = None,
         seed: dict | None = None, auth: str | None = None, kind: str = "api", **extra) -> dict:
    full = url + ("?" + urlencode(params, doseq=True) if params else "")
    return {"source": source, "method": method, "url": full, "host": urlparse(url).hostname, "json": body,
            "auth_env": auth, "kind": kind, "seed": (seed or {}).get("id"), **extra}


# ------------------------------------------------------------------------------------------------ 1. official APIs
class YouTubeAPI(Source):
    name, platforms = "youtube_api", ("youtube",)
    BASE = "https://www.googleapis.com/youtube/v3/"

    def requests(self, seed, since, until, env):
        p = {"part": "snippet", "type": "video", "videoDuration": "short", "order": "viewCount", "maxResults": 50,
             "publishedAfter": since.strftime("%Y-%m-%dT%H:%M:%SZ"), "publishedBefore": until.strftime("%Y-%m-%dT%H:%M:%SZ")}
        if seed.get("type") == "creator" and seed.get("channel_id"):
            p["channelId"] = seed["channel_id"]
        else:
            p["q"] = seed.get("query") or seed.get("handle") or ""
        return [_req(self.name, self.BASE + "search", params=p, seed=seed, auth="YOUTUBE_API_KEY", step="search")]

    def parse(self, payload, req):
        payload = payload or {}
        if req.get("step") == "search":
            ids = [i.get("id", {}).get("videoId") for i in payload.get("items", []) if i.get("id", {}).get("videoId")]
            if not ids:
                return [], []
            return [], [_req(self.name, self.BASE + "videos", params={"part": "snippet,statistics,contentDetails",
                                                                       "id": ",".join(ids[:50])},
                             auth="YOUTUBE_API_KEY", step="videos", seed={"id": req.get("seed")})]
        out = []
        for v in payload.get("items", []):
            sn, st = v.get("snippet", {}), v.get("statistics", {})
            dur = iso_duration_s(v.get("contentDetails", {}).get("duration"))
            if dur is not None and dur > DEFAULTS["shorts_max_s"]:
                continue
            out.append(item(platform="youtube", source=self.name, id=v.get("id"),
                            url=f"https://www.youtube.com/shorts/{v.get('id')}", creator=sn.get("channelTitle"),
                            published_at=_iso(sn.get("publishedAt")), views=_int(st.get("viewCount")),
                            engaged_views=_int(st.get("engagedViews") or v.get("engagedViews")),
                            likes=_int(st.get("likeCount")), comments=_int(st.get("commentCount")), duration_s=dur,
                            title_or_caption=" ".join(x for x in (sn.get("title"), sn.get("description")) if x),
                            seed=req.get("seed")))
        return out, []


class TikTokResearch(Source):
    name, platforms = "tiktok_research", ("tiktok",)
    URL = "https://open.tiktokapis.com/v2/research/video/query/"
    FIELDS = ("id,video_description,create_time,username,view_count,like_count,comment_count,share_count,"
              "favorites_count,video_duration,hashtag_names,voice_to_text")

    def requests(self, seed, since, until, env):
        if seed.get("type") == "creator":
            cond = {"operation": "EQ", "field_name": "username", "field_values": [seed.get("handle", "").lstrip("@")]}
        else:
            cond = {"operation": "IN", "field_name": "keyword", "field_values": [seed.get("query", "")]}
        out, start = [], since
        while start < until:                          # the API allows at most 30 days per query
            end = min(until, datetime.fromtimestamp(start.timestamp() + 29 * 86400, tz=timezone.utc))
            out.append(_req(self.name, self.URL, method="POST", params={"fields": self.FIELDS}, seed=seed,
                            auth="TIKTOK_RESEARCH_TOKEN",
                            body={"query": {"and": [cond]}, "start_date": start.strftime("%Y%m%d"),
                                  "end_date": end.strftime("%Y%m%d"), "max_count": 100, "is_random": False}))
            start = end
        return out

    def parse(self, payload, req):
        out = []
        for v in ((payload or {}).get("data") or {}).get("videos", []):
            user = v.get("username") or ""
            out.append(item(platform="tiktok", source=self.name, id=str(v.get("id")),
                            url=f"https://www.tiktok.com/@{user}/video/{v.get('id')}", creator=f"@{user}" if user else None,
                            published_at=_iso(v.get("create_time")), views=_int(v.get("view_count")),
                            likes=_int(v.get("like_count")), comments=_int(v.get("comment_count")),
                            shares=_int(v.get("share_count")), saves=_int(v.get("favorites_count")),
                            duration_s=_int(v.get("video_duration")), title_or_caption=v.get("video_description") or "",
                            transcript=v.get("voice_to_text") or "",
                            hashtags=" ".join("#" + h for h in v.get("hashtag_names") or []), seed=req.get("seed")))
        return out, []


class MetaGraph(Source):
    """IG business_discovery for a seed creator's public media. Instagram does not expose other accounts' view counts
    here, so views stay None and relative performance runs on likes + comments (normalize.engagement)."""
    name, platforms = "meta_graph", ("instagram",)
    BASE = "https://graph.facebook.com/v23.0/"

    def requests(self, seed, since, until, env):
        if seed.get("type") != "creator" or seed.get("platform") != "instagram":
            return []
        h = seed.get("handle", "").lstrip("@")
        fields = (f"business_discovery.username({h}){{username,followers_count,media.limit(50)"
                  "{id,caption,like_count,comments_count,media_product_type,timestamp,permalink}}")
        return [_req(self.name, self.BASE + str(env.get("IG_BUSINESS_USER_ID", "IG_USER")), params={"fields": fields},
                     seed=seed, auth="META_GRAPH_TOKEN")]

    def parse(self, payload, req):
        bd = (payload or {}).get("business_discovery") or {}
        out = []
        for m in (bd.get("media") or {}).get("data", []):
            if m.get("media_product_type") not in (None, "REELS"):
                continue
            out.append(item(platform="instagram", source=self.name, id=m.get("id"), url=m.get("permalink"),
                            creator="@" + bd.get("username", ""), creator_followers=_int(bd.get("followers_count")),
                            published_at=_iso(m.get("timestamp")), likes=_int(m.get("like_count")),
                            comments=_int(m.get("comments_count")), title_or_caption=m.get("caption") or "",
                            seed=req.get("seed")))
        return out, []


class MetaContentLibrary(Source):
    """Meta Content Library (approved research access only). Requests are issued from Meta's own environment; this
    adapter PARSES exported results (n8n pushes them) and plans nothing on its own."""
    name, platforms = "meta_content_library", ("facebook", "instagram")

    def parse(self, payload, req):
        out = []
        for p in (payload or {}).get("data", []):
            plat = "instagram" if str(p.get("platform", "")).lower().startswith("insta") else "facebook"
            st = p.get("statistics") or {}
            out.append(item(platform=plat, source=self.name, id=str(p.get("id")), url=p.get("url"),
                            creator=p.get("owner_username") or p.get("owner_name"),
                            published_at=_iso(p.get("creation_time")), views=_int(st.get("views") or p.get("view_count")),
                            likes=_int(st.get("reactions") or p.get("reaction_count")),
                            comments=_int(st.get("comments") or p.get("comment_count")),
                            shares=_int(st.get("shares") or p.get("share_count")), title_or_caption=p.get("text") or "",
                            seed=req.get("seed")))
        return out, []


class ThreadsAPI(Source):
    name, platforms = "threads_api", ("threads",)
    URL = "https://graph.threads.net/v1.0/keyword_search"

    def requests(self, seed, since, until, env):
        if seed.get("type") == "creator":
            return []
        return [_req(self.name, self.URL, params={"q": seed.get("query", ""), "search_type": "TOP",
                                                  "fields": "id,text,timestamp,permalink,username,media_type",
                                                  "since": int(since.timestamp()), "until": int(until.timestamp())},
                     seed=seed, auth="THREADS_TOKEN")]

    def parse(self, payload, req):
        return [item(platform="threads", source=self.name, id=p.get("id"), url=p.get("permalink"),
                     creator="@" + (p.get("username") or ""), published_at=_iso(p.get("timestamp")),
                     title_or_caption=p.get("text") or "", seed=req.get("seed"))
                for p in (payload or {}).get("data", [])], []


class XAPI(Source):
    name, platforms = "x_api", ("x",)
    URL = "https://api.x.com/2/tweets/search/recent"

    def requests(self, seed, since, until, env):
        q = (f"from:{seed.get('handle', '').lstrip('@')}" if seed.get("type") == "creator" else f"({seed.get('query', '')})")
        return [_req(self.name, self.URL, params={"query": f"{q} has:videos -is:retweet lang:en", "max_results": 100,
                                                  "tweet.fields": "created_at,public_metrics,author_id",
                                                  "expansions": "author_id", "user.fields": "username,public_metrics"},
                     seed=seed, auth="X_BEARER_TOKEN")]

    def parse(self, payload, req):
        payload = payload or {}
        users = {u.get("id"): u for u in (payload.get("includes") or {}).get("users", [])}
        out = []
        for t in payload.get("data", []):
            pm, u = t.get("public_metrics") or {}, users.get(t.get("author_id"), {})
            out.append(item(platform="x", source=self.name, id=t.get("id"),
                            url=f"https://x.com/{u.get('username', 'i')}/status/{t.get('id')}",
                            creator="@" + u.get("username", "") if u else None,
                            creator_followers=_int((u.get("public_metrics") or {}).get("followers_count")),
                            published_at=_iso(t.get("created_at")), views=_int(pm.get("impression_count")),
                            likes=_int(pm.get("like_count")), comments=_int(pm.get("reply_count")),
                            shares=_int((pm.get("retweet_count") or 0) + (pm.get("quote_count") or 0)),
                            saves=_int(pm.get("bookmark_count")), title_or_caption=t.get("text") or "",
                            seed=req.get("seed")))
        return out, []


# ------------------------------------------------------------------------------------------------ 2. yt-dlp metadata
class YtDlp(Source):
    """Command plans for `yt-dlp` metadata only. crawl.py runs them through an injected runner (never in tests)."""
    name, platforms, kind = "ytdlp", ("youtube",), "ytdlp"
    FORBIDDEN = ("--cookies", "--cookies-from-browser", "--username", "--password", "--netrc", "-u", "-p")

    def available(self, env):
        return True

    def requests(self, seed, since, until, env):
        if seed.get("type") == "creator" and seed.get("platform") == "youtube":
            target = f"https://www.youtube.com/{seed['handle']}/shorts"
        else:
            target = f"ytsearch50:{seed.get('query', '')} shorts"
        argv = ["yt-dlp", "--skip-download", "--dump-json", "--no-playlist", "--ignore-errors", "--playlist-end", "50",
                "--dateafter", since.strftime("%Y%m%d"), "--sleep-requests", "2", "--no-cookies-from-browser", target]
        return [{"source": self.name, "kind": "ytdlp", "argv": argv, "host": "www.youtube.com",
                 "url": target if target.startswith("http") else "https://www.youtube.com/results",
                 "seed": seed.get("id")}]

    def parse(self, payload, req):
        rows = payload if isinstance(payload, list) else [json.loads(l) for l in str(payload or "").splitlines() if l.strip()]
        out = []
        for v in rows:
            if (v.get("duration") or 0) > DEFAULTS["shorts_max_s"]:
                continue
            out.append(item(platform="youtube", source=self.name, id=v.get("id"),
                            url=v.get("webpage_url") or f"https://www.youtube.com/shorts/{v.get('id')}",
                            creator=v.get("uploader_id") or v.get("channel"),
                            creator_followers=_int(v.get("channel_follower_count")),
                            published_at=_iso(v.get("timestamp") or v.get("upload_date")), views=_int(v.get("view_count")),
                            likes=_int(v.get("like_count")), comments=_int(v.get("comment_count")),
                            duration_s=v.get("duration"),
                            title_or_caption=" ".join(x for x in (v.get("title"), v.get("description")) if x),
                            seed=req.get("seed")))
        return out, []


# ------------------------------------------------------------------------------------------------ 3. public fallback
_META = re.compile(r'<meta\s+(?:property|name)=["\']([^"\']+)["\']\s+content=["\']([^"\']*)["\']', re.I)
_LD = re.compile(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', re.I | re.S)


class PublicPage(Source):
    """Public page metadata (og:/twitter:/JSON-LD VideoObject only). Used for seed URLs on hosts not in
    tos_blocked_hosts, after robots.txt allows the path. No login, no cookies, no JS execution, no media."""
    name, kind = "public_page", "public"
    platforms = PLATFORMS

    def available(self, env):
        return True

    def requests(self, seed, since, until, env):
        url = seed.get("url")
        if not url or not url.startswith("https://"):
            return []
        return [{"source": self.name, "kind": "public", "method": "GET", "url": url, "host": urlparse(url).hostname,
                 "seed": seed.get("id"), "platform": seed.get("platform")}]

    def parse(self, payload, req):
        text = payload if isinstance(payload, str) else ""
        meta = {k.lower(): html.unescape(v) for k, v in _META.findall(text)}
        stats = {}
        for blob in _LD.findall(text):
            try:
                d = json.loads(blob)
            except ValueError:
                continue
            for obj in d if isinstance(d, list) else [d]:
                if not isinstance(obj, dict) or obj.get("@type") not in ("VideoObject", "SocialMediaPosting"):
                    continue
                stats.setdefault("published_at", obj.get("uploadDate") or obj.get("datePublished"))
                stats.setdefault("duration_s", iso_duration_s(obj.get("duration")))
                stats.setdefault("creator", (obj.get("author") or {}).get("name") if isinstance(obj.get("author"), dict) else None)
                for s in obj.get("interactionStatistic") or []:
                    t = str((s.get("interactionType") or {}).get("@type") if isinstance(s.get("interactionType"), dict)
                            else s.get("interactionType"))
                    n = _int(s.get("userInteractionCount"))
                    key = "views" if "Watch" in t else "likes" if "Like" in t else "comments" if "Comment" in t \
                        else "shares" if "Share" in t else None
                    if key:
                        stats[key] = n
        if not meta and not stats:
            return [], []
        url = meta.get("og:url") or req.get("url")
        return [item(platform=req.get("platform"), source=self.name, id=url.rstrip("/").rsplit("/", 1)[-1], url=url,
                     creator=stats.get("creator"), published_at=_iso(stats.get("published_at")),
                     views=stats.get("views"), likes=stats.get("likes"), comments=stats.get("comments"),
                     shares=stats.get("shares"), duration_s=stats.get("duration_s"),
                     title_or_caption=" ".join(x for x in (meta.get("og:title"), meta.get("og:description")) if x),
                     seed=req.get("seed"))], []


REGISTRY: dict[str, Source] = {s.name: s for s in (YouTubeAPI(), TikTokResearch(), MetaGraph(), MetaContentLibrary(),
                                                   ThreadsAPI(), XAPI(), YtDlp(), PublicPage())}
PRIORITY: dict[str, tuple[str, ...]] = {
    "youtube": ("youtube_api", "ytdlp", "public_page"),
    "tiktok": ("tiktok_research", "public_page"),
    "instagram": ("meta_graph", "meta_content_library", "public_page"),
    "facebook": ("meta_content_library", "public_page"),
    "threads": ("threads_api", "public_page"),
    "x": ("x_api", "public_page"),
}


def chain(platform: str, env: dict) -> list[Source]:
    """Sources to use for one platform, in priority order, skipping official APIs we hold no credentials for."""
    return [REGISTRY[n] for n in PRIORITY.get(platform, ()) if REGISTRY[n].available(env)]
