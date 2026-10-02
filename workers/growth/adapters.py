"""Platform metrics adapters -> one raw capture shape.

Each adapter has:
  parse(raw, *, duration_s=None) -> dict   pure: the platform's JSON -> canonical counters (fixture-driven tests)
  fetch(post, token, client=None) -> dict  live: one SSRF-checked GET (growth/net.py), only with GROWTH_LIVE_METRICS=1

A capture is {"captured_at": iso, <COUNTERS...>, "avg_watch_pct": float|None, "missing": [fields the platform does
not expose]}. Counters the platform does not expose are left out and listed in `missing` (never faked as 0), so the
scorer can drop those components instead of scoring them as zero. keyword_comments / optins / members never come
from a platform API: they are DB rollups (comments, dm_leads, orders.attributed_post_id) merged in growth/snapshots.

API references (Sept 2026): IG Graph v22 media insights (views, reach, likes, comments, shares, saved,
profile_visits, follows, ig_reels_avg_watch_time, total_interactions); FB Graph video insights
(post_video_views / fb_reels_total_plays, post_video_avg_time_watched [ms], post_video_social_actions); TikTok
/v2/video/query (view_count, like_count, comment_count, share_count) and the Business API (average_time_watched,
full_video_watched_rate, profile_views?); YouTube Analytics v2 reports (views, likes, comments, shares,
subscribersGained, averageViewPercentage, averageViewDuration); Threads media insights (views, likes, replies,
reposts, quotes, shares); X /2/tweets public_metrics + non_public_metrics (impression_count, like_count,
reply_count, retweet_count, quote_count, bookmark_count, user_profile_clicks, url_link_clicks).
"""
from __future__ import annotations

from datetime import datetime, timezone

from growth import config as G
from growth import net

PLATFORM_COUNTERS = ("views", "reach", "likes", "comments", "shares", "saves", "profile_visits", "link_clicks", "follows")


def _n(x) -> int | None:
    v = G.num(x, lo=0, hi=1e13)
    return None if v is None else int(v)


def _pct(x) -> float | None:
    """A watch percentage as 0..100, accepting 0..1 fractions too."""
    v = G.num(x, lo=0)
    if v is None:
        return None
    if v <= 1.0:
        v *= 100.0
    return min(100.0, v)


def _watch_pct_from_seconds(avg_s, duration_s) -> float | None:
    a, d = G.num(avg_s, lo=0), G.num(duration_s, lo=0.5)
    if a is None or d is None:
        return None
    return min(100.0, 100.0 * a / d)


def _capture(values: dict, *, captured_at, missing: list[str], source: str, scorecard: dict | None = None) -> dict:
    out = {"captured_at": _iso(captured_at), "source": source, "missing": sorted(set(missing))}
    sc = {k: v for k, v in (scorecard or {}).items() if v is not None}
    if sc:
        out["scorecard"] = sc            # extra inputs for growth/scorecard.py (hook hold, retention curve, ...)
    for k in PLATFORM_COUNTERS:
        if k in values and values[k] is not None:
            out[k] = values[k]
        elif k not in out["missing"]:
            out["missing"].append(k)
    out["missing"] = sorted(set(out["missing"]))
    out["avg_watch_pct"] = values.get("avg_watch_pct")
    return out


def _iso(x) -> str:
    if isinstance(x, datetime):
        return (x if x.tzinfo else x.replace(tzinfo=timezone.utc)).isoformat()
    if x is None:
        return datetime.now(timezone.utc).isoformat()
    return str(x)


def _graph_insights(raw: dict) -> dict:
    """Meta Graph insights list -> {metric_name: value}. Accepts 'values[0].value', 'total_value.value' and
    breakdown-free 'value' shapes."""
    out = {}
    for item in (raw.get("data") or []):
        name = item.get("name")
        if not name:
            continue
        val = None
        if isinstance(item.get("total_value"), dict):
            val = item["total_value"].get("value")
        elif item.get("values"):
            last = item["values"][-1]
            val = last.get("value") if isinstance(last, dict) else last
        elif "value" in item:
            val = item["value"]
        if isinstance(val, dict):            # breakdown dict: sum the leaves
            val = sum(v for v in val.values() if isinstance(v, (int, float)))
        out[name] = val
    return out


# ---------------------------------------------------------------- Instagram (Reels)
IG_METRICS = ("views,reach,likes,comments,shares,saved,profile_visits,follows,ig_reels_avg_watch_time,total_interactions,"
              "reels_skip_rate")   # reels_skip_rate: share of viewers who skip in the first 3 s ("in development") [S17]


def ig_parse(raw: dict, *, duration_s: float | None = None, captured_at=None) -> dict:
    m = _graph_insights(raw)
    vals = {"views": _n(m.get("views", m.get("plays"))), "reach": _n(m.get("reach")), "likes": _n(m.get("likes")),
            "comments": _n(m.get("comments")), "shares": _n(m.get("shares")), "saves": _n(m.get("saved", m.get("saves"))),
            "profile_visits": _n(m.get("profile_visits")), "follows": _n(m.get("follows")),
            "avg_watch_pct": _watch_pct_from_seconds((m.get("ig_reels_avg_watch_time") or 0) / 1000.0
                                                     if m.get("ig_reels_avg_watch_time") is not None else None, duration_s)}
    return _capture(vals, captured_at=captured_at, missing=["link_clicks"], source="instagram_graph",
                    scorecard={"skip_rate": None if _pct(m.get("reels_skip_rate")) is None else _pct(m.get("reels_skip_rate")) / 100.0})


def ig_fetch(post: dict, token: str, client=None) -> dict:
    url = f"https://graph.facebook.com/v22.0/{net.safe_id(post['external_post_id'])}/insights"
    raw = net.request_json("GET", url, token=token, params={"metric": IG_METRICS}, client=client)
    return ig_parse(raw, duration_s=post.get("duration_s"))


# ---------------------------------------------------------------- Facebook (Reels / video posts)
FB_METRICS = ("fb_reels_total_plays,post_video_views,post_impressions_unique,post_video_avg_time_watched,"
              "post_video_social_actions,post_reactions_like_total,post_video_followers,"
              "post_video_retention_graph,blue_reels_play_count")   # retention graph + first plays [S16]


def fb_retention_curve(raw: dict, duration_s: float | None) -> list[list[float]] | None:
    """post_video_retention_graph (lifetime): {"0": 1.0, "1": 0.93, ...} keyed by bucket (the share of viewers still
    watching). Buckets are seconds for Reels; with 40+ buckets on a long video they are percent-of-length steps, so
    they are mapped onto seconds when duration_s is known. Returns [[t_s, fraction], ...] sorted by t."""
    for item in raw.get("data") or []:
        if item.get("name") != "post_video_retention_graph":
            continue
        v = (item.get("values") or [{}])[-1]
        g = v.get("value") if isinstance(v, dict) else None
        if not isinstance(g, dict) or not g:
            return None
        pts = []
        for k, val in g.items():
            t, f = G.num(k, lo=0), G.num(val, lo=0)
            if t is not None and f is not None:
                pts.append([t, f / 100.0 if f > 1.0 else f])
        pts.sort()
        d = G.num(duration_s, lo=0.5)
        if d and len(pts) >= 40 and pts[-1][0] > d:          # percent-of-length buckets -> seconds
            last = pts[-1][0] or 1.0
            pts = [[round(t / last * d, 3), f] for t, f in pts]
        return pts or None
    return None


def fb_parse(raw: dict, *, duration_s: float | None = None, captured_at=None) -> dict:
    m = _graph_insights(raw)
    social = m.get("post_video_social_actions") if isinstance(m.get("post_video_social_actions"), dict) else {}
    raw_social = {}
    for item in raw.get("data") or []:
        if item.get("name") == "post_video_social_actions":
            v = (item.get("values") or [{}])[-1]
            raw_social = v.get("value") if isinstance(v, dict) and isinstance(v.get("value"), dict) else {}
    social = raw_social or social or {}
    views = m.get("fb_reels_total_plays", m.get("post_video_views"))
    vals = {"views": _n(views), "reach": _n(m.get("post_impressions_unique")),
            "likes": _n(m.get("post_reactions_like_total", social.get("LIKE"))),
            "comments": _n(social.get("COMMENT")), "shares": _n(social.get("SHARE")),
            "follows": _n(m.get("post_video_followers")),
            "avg_watch_pct": _watch_pct_from_seconds((m["post_video_avg_time_watched"] or 0) / 1000.0
                                                     if m.get("post_video_avg_time_watched") is not None else None, duration_s)}
    curve = fb_retention_curve(raw, duration_s)
    return _capture(vals, captured_at=captured_at, missing=["saves", "profile_visits", "link_clicks"], source="facebook_graph",
                    scorecard={"retention_curve": curve, "first_plays": _n(m.get("blue_reels_play_count")),
                               "hold_3s": _curve_hold(curve, 3.0)})


def _curve_hold(curve, t: float) -> float | None:
    if not curve:
        return None
    prev = curve[0]
    for p in curve:
        if p[0] >= t:
            if p[0] == prev[0]:
                return p[1]
            return prev[1] + (p[1] - prev[1]) * (t - prev[0]) / (p[0] - prev[0])
        prev = p
    return curve[-1][1]


def fb_fetch(post: dict, token: str, client=None) -> dict:
    url = f"https://graph.facebook.com/v22.0/{net.safe_id(post['external_post_id'])}/insights"
    raw = net.request_json("GET", url, token=token, params={"metric": FB_METRICS}, client=client)
    return fb_parse(raw, duration_s=post.get("duration_s"))


# ---------------------------------------------------------------- TikTok
def tt_parse(raw: dict, *, duration_s: float | None = None, captured_at=None, video_id: str | None = None) -> dict:
    vids = ((raw.get("data") or {}).get("videos")) or raw.get("videos") or ([raw] if "view_count" in raw else [])
    v = next((x for x in vids if video_id is None or str(x.get("id")) == str(video_id)), vids[0] if vids else {})
    watch = v.get("average_time_watched")
    pct = _pct(v.get("full_video_watched_rate")) if v.get("full_video_watched_rate") is not None else None
    vals = {"views": _n(v.get("view_count")), "likes": _n(v.get("like_count")), "comments": _n(v.get("comment_count")),
            "shares": _n(v.get("share_count")), "saves": _n(v.get("favorite_count", v.get("collect_count"))),
            "reach": _n(v.get("reach")), "profile_visits": _n(v.get("profile_views")),
            "avg_watch_pct": _watch_pct_from_seconds(watch, duration_s or v.get("duration")) if watch is not None else pct}
    missing = ["link_clicks", "follows"]
    return _capture(vals, captured_at=captured_at, missing=missing, source="tiktok_open_api")


def tt_fetch(post: dict, token: str, client=None) -> dict:
    url = "https://open.tiktokapis.com/v2/video/query/"
    fields = "id,view_count,like_count,comment_count,share_count,duration"
    raw = net.request_json("POST", url + f"?fields={fields}", token=token,
                           body={"filters": {"video_ids": [net.safe_id(post["external_post_id"])]}}, client=client)
    return tt_parse(raw, duration_s=post.get("duration_s"), video_id=post["external_post_id"])


# ---------------------------------------------------------------- YouTube (Analytics API v2)
YT_METRICS = "views,engagedViews,likes,comments,shares,subscribersGained,averageViewPercentage,averageViewDuration"


def yt_parse(raw: dict, *, duration_s: float | None = None, captured_at=None) -> dict:
    cols = [c.get("name") for c in raw.get("columnHeaders") or []]
    rows = raw.get("rows") or []
    m: dict = {}
    if cols and rows:
        # sum over rows when the report is dimensioned (e.g. by day); ratios are averaged
        for row in rows:
            for c, v in zip(cols, row):
                if c in ("averageViewPercentage", "averageViewDuration"):
                    m.setdefault(c, []).append(v)
                elif isinstance(v, (int, float)):
                    m[c] = m.get(c, 0) + v
        for c in ("averageViewPercentage", "averageViewDuration"):
            if c in m and m[c]:
                m[c] = sum(m[c]) / len(m[c])
    elif isinstance(raw.get("statistics"), dict):          # Data API fallback: videos.list statistics
        s = raw["statistics"]
        m = {"views": s.get("viewCount"), "likes": s.get("likeCount"), "comments": s.get("commentCount")}
    pct = _pct(m.get("averageViewPercentage")) if m.get("averageViewPercentage") is not None else \
        _watch_pct_from_seconds(m.get("averageViewDuration"), duration_s)
    vals = {"views": _n(m.get("views")), "likes": _n(m.get("likes")), "comments": _n(m.get("comments")),
            "shares": _n(m.get("shares")), "follows": _n(m.get("subscribersGained")), "avg_watch_pct": pct}
    return _capture(vals, captured_at=captured_at, missing=["reach", "saves", "profile_visits", "link_clicks"],
                    source="youtube_analytics", scorecard={"engaged_views": _n(m.get("engagedViews"))})


def yt_fetch(post: dict, token: str, client=None, *, start: str, end: str) -> dict:
    url = "https://youtubeanalytics.googleapis.com/v2/reports"
    raw = net.request_json("GET", url, token=token, client=client,
                           params={"ids": "channel==MINE", "startDate": start, "endDate": end, "metrics": YT_METRICS,
                                   "filters": f"video=={net.safe_id(post['external_post_id'])}"})
    return yt_parse(raw, duration_s=post.get("duration_s"))


# ---------------------------------------------------------------- Threads
TH_METRICS = "views,likes,replies,reposts,quotes,shares"


def threads_parse(raw: dict, *, duration_s: float | None = None, captured_at=None) -> dict:
    m = _graph_insights(raw)
    reposts, quotes = _n(m.get("reposts")), _n(m.get("quotes"))
    shares = None
    if m.get("shares") is not None:
        shares = _n(m.get("shares"))
    elif reposts is not None or quotes is not None:
        shares = (reposts or 0) + (quotes or 0)
    vals = {"views": _n(m.get("views")), "likes": _n(m.get("likes")), "comments": _n(m.get("replies")), "shares": shares}
    return _capture(vals, captured_at=captured_at,
                    missing=["reach", "saves", "profile_visits", "link_clicks", "follows", "avg_watch_pct"],
                    source="threads_graph")


def threads_fetch(post: dict, token: str, client=None) -> dict:
    url = f"https://graph.threads.net/v1.0/{net.safe_id(post['external_post_id'])}/insights"
    raw = net.request_json("GET", url, token=token, params={"metric": TH_METRICS}, client=client)
    return threads_parse(raw)


# ---------------------------------------------------------------- X
def x_parse(raw: dict, *, duration_s: float | None = None, captured_at=None, tweet_id: str | None = None) -> dict:
    data = raw.get("data")
    if isinstance(data, list):
        t = next((x for x in data if tweet_id is None or str(x.get("id")) == str(tweet_id)), data[0] if data else {})
    elif isinstance(data, dict):
        t = data
    else:
        t = raw
    pub, npub, org = t.get("public_metrics") or {}, t.get("non_public_metrics") or {}, t.get("organic_metrics") or {}
    impressions = pub.get("impression_count", org.get("impression_count"))
    shares = None
    if pub.get("retweet_count") is not None or pub.get("quote_count") is not None:
        shares = (_n(pub.get("retweet_count")) or 0) + (_n(pub.get("quote_count")) or 0)
    vals = {"views": _n(impressions), "likes": _n(pub.get("like_count")), "comments": _n(pub.get("reply_count")),
            "shares": shares, "saves": _n(pub.get("bookmark_count")),
            "profile_visits": _n(npub.get("user_profile_clicks", org.get("user_profile_clicks"))),
            "link_clicks": _n(npub.get("url_link_clicks", org.get("url_link_clicks")))}
    return _capture(vals, captured_at=captured_at, missing=["reach", "follows", "avg_watch_pct"], source="x_api_v2")


def x_fetch(post: dict, token: str, client=None) -> dict:
    url = f"https://api.x.com/2/tweets/{net.safe_id(post['external_post_id'])}"
    raw = net.request_json("GET", url, token=token, client=client,
                           params={"tweet.fields": "public_metrics,non_public_metrics,organic_metrics"})
    return x_parse(raw, tweet_id=post["external_post_id"])


PARSERS = {"instagram": ig_parse, "facebook": fb_parse, "tiktok": tt_parse, "youtube": yt_parse,
           "threads": threads_parse, "x": x_parse}
FETCHERS = {"instagram": ig_fetch, "facebook": fb_fetch, "tiktok": tt_fetch, "youtube": yt_fetch,
            "threads": threads_fetch, "x": x_fetch}


def register(platform: str, parse_fn, fetch_fn) -> None:
    """Add a platform adapter (e.g. an X/Grok analytics adapter later). parse_fn(raw, *, duration_s=None, captured_at=None)
    -> capture dict via _capture(); fetch_fn(post, token, client=None, **kw) -> capture, using growth.net.request_json only
    (so the SSRF policy and the GROWTH_LIVE_METRICS switch apply). The host must also be on METRICS_ALLOWED_HOSTS."""
    if not (callable(parse_fn) and callable(fetch_fn)):
        raise TypeError("adapter functions must be callable")
    PARSERS[platform] = parse_fn
    FETCHERS[platform] = fetch_fn


def parse(platform: str, raw: dict, **kw) -> dict:
    if platform not in PARSERS:
        raise ValueError(f"unknown platform: {platform}")
    if not isinstance(raw, dict):
        raise ValueError("raw metrics payload must be a JSON object")
    return PARSERS[platform](raw, **kw)


def fetch(platform: str, post: dict, token: str, client=None, **kw) -> dict:
    """Live pull. Refused unless GROWTH_LIVE_METRICS=1 (growth/net.py raises NetPolicyError)."""
    if platform not in FETCHERS:
        raise ValueError(f"unknown platform: {platform}")
    if not G.GROWTH_LIVE_METRICS:
        raise net.NetPolicyError("live metrics are disabled (GROWTH_LIVE_METRICS=0)")
    return FETCHERS[platform](post, token, client, **kw)
