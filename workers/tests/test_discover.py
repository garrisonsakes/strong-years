"""workers/discover: source adapters parse fixture payloads, the crawler enforces robots / ToS / rate limits / no
cookies and never touches the network in tests, rows normalise to the posts.csv schema with scorecard genes, trends
find rising genes and cross-platform transfers, remake briefs pass the plagiarism guard and carry provenance."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import app
from common import config
from discover import crawl, genes as GN, normalize as N, remake as RM, sources as SRC, trends as TR
from growth import actions as A, allocator as AL, catalog as CAT, config as G, variants as V
from tests.conftest import AUTH

NOW = datetime(2026, 10, 2, 12, 0, tzinfo=timezone.utc)
FX = Path(__file__).parent / "fixtures" / "discover"
SINCE = NOW - timedelta(days=90)


def fx(name):
    p = FX / name
    return json.loads(p.read_text()) if p.suffix == ".json" else p.read_text()


class FakeNet:
    """url-prefix -> response; records every request; never touches a socket."""

    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def __call__(self, req):
        self.calls.append(req)
        for prefix, resp in self.routes.items():
            if req["url"].startswith(prefix):
                return resp
        return {"status": 404, "text": ""}


class Clock:
    def __init__(self):
        self.t, self.slept = 0.0, []

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


def crawler(routes, env=None, **kw):
    clk = Clock()
    net = FakeNet(routes)
    c = crawl.Crawler(net, kw.pop("run", None), env=env or {}, clock=clk, sleep=clk.sleep, **kw)
    return c, net, clk


# ------------------------------------------------------------------------------------------------ seeds
def test_seeds_60_queries_100_creators_all_to_verify():
    s = json.loads((config.SPEC_DIR / "data" / "discover" / "seeds.json").read_text())
    assert len(s["queries"]) == 60 and len({q["id"] for q in s["queries"]}) == 60
    assert len(s["creators"]) == 100 and len({c["id"] for c in s["creators"]}) == 100
    assert all(c["status"] == "to_verify" for c in s["creators"])
    assert {c["platform"] for c in s["creators"]} == set(SRC.PLATFORMS)
    assert all(q["id"].startswith("Q") for q in s["queries"]) and all(c["id"].startswith("C") for c in s["creators"])


# ------------------------------------------------------------------------------------------------ adapters
def test_youtube_api_search_then_videos_drops_long_and_keeps_engaged_views():
    yt = SRC.REGISTRY["youtube_api"]
    reqs = yt.requests({"id": "Q01", "query": "chair exercises for seniors"}, SINCE, NOW, {})
    assert reqs[0]["url"].startswith("https://www.googleapis.com/youtube/v3/search?") and "videoDuration=short" in reqs[0]["url"]
    assert "key=" not in reqs[0]["url"]                       # the key is added by the live fetcher only
    items, more = yt.parse(fx("youtube_search.json"), reqs[0])
    assert items == [] and len(more) == 1 and "id=yt1%2Cyt2%2Cytlong" in more[0]["url"]
    items, _ = yt.parse(fx("youtube_videos.json"), more[0])
    assert [i["id"] for i in items] == ["yt1", "yt2"]           # the 30-minute video is not a Short
    assert items[0]["views"] == 900000 and items[0]["duration_s"] == 42 and items[1]["engaged_views"] == 35000


def test_tiktok_research_windows_and_parse():
    tt = SRC.REGISTRY["tiktok_research"]
    reqs = tt.requests({"id": "Q02", "query": "balance"}, SINCE, NOW, {})
    assert len(reqs) == 4 and all(r["method"] == "POST" for r in reqs)         # <= 30 days per query
    for r in reqs:
        d0, d1 = (datetime.strptime(r["json"][k], "%Y%m%d") for k in ("start_date", "end_date"))
        assert (d1 - d0).days <= 30
    items, _ = tt.parse(fx("tiktok_research.json"), reqs[0])
    assert items[0]["views"] == 2500000 and items[0]["saves"] == 60000 and "Hips first" in items[0]["transcript"]
    assert items[0]["creator"] == "@fitover60" and items[0]["url"].endswith("/video/7400000000000000001")


def test_meta_graph_reels_only_no_views_and_other_official_parsers():
    ig = SRC.REGISTRY["meta_graph"]
    assert ig.requests({"id": "Q1", "query": "x"}, SINCE, NOW, {}) == []           # queries can't run on business_discovery
    r = ig.requests({"id": "C1", "type": "creator", "platform": "instagram", "handle": "@maangchi"}, SINCE, NOW,
                    {"IG_BUSINESS_USER_ID": "17841"})[0]
    from urllib.parse import unquote
    assert "business_discovery.username(maangchi)" in unquote(r["url"])
    items, _ = ig.parse(fx("ig_business_discovery.json"), r)
    assert len(items) == 1 and items[0]["views"] is None and items[0]["creator_followers"] == 1200000
    fb, _ = SRC.REGISTRY["meta_content_library"].parse(fx("meta_content_library.json"), {})
    assert fb[0]["platform"] == "facebook" and fb[0]["views"] == 3000000 and fb[0]["shares"] == 70000
    th, _ = SRC.REGISTRY["threads_api"].parse(fx("threads_search.json"), {})
    assert th[0]["platform"] == "threads" and th[0]["creator"] == "@agingwell"
    xs, _ = SRC.REGISTRY["x_api"].parse(fx("x_recent.json"), {})
    assert xs[0]["views"] == 1500000 and xs[0]["shares"] == 5200 and xs[0]["saves"] == 9000 and xs[0]["creator_followers"] == 500000


def test_ytdlp_metadata_only():
    y = SRC.REGISTRY["ytdlp"]
    r = y.requests({"id": "C2", "type": "creator", "platform": "youtube", "handle": "@GrowYoungFitness"}, SINCE, NOW, {})[0]
    assert "--skip-download" in r["argv"] and "--dump-json" in r["argv"]
    assert not set(r["argv"]) & set(SRC.YtDlp.FORBIDDEN)
    items, _ = y.parse(fx("ytdlp.jsonl"), r)
    assert [i["id"] for i in items] == ["yd1"] and items[0]["creator_followers"] == 300000


def test_public_page_parses_og_and_jsonld_only():
    items, _ = SRC.REGISTRY["public_page"].parse(fx("public_page.html"), {"url": "https://videos.example.org/v/abc123",
                                                                           "platform": "youtube", "seed": "Q9"})
    assert items[0]["views"] == 64000 and items[0]["likes"] == 2100 and items[0]["duration_s"] == 40
    assert "kitchen counter & hold on" in items[0]["title_or_caption"]


def test_chain_priority_official_first_only_with_credentials():
    assert [s.name for s in SRC.chain("youtube", {})] == ["ytdlp", "public_page"]
    assert [s.name for s in SRC.chain("youtube", {"YOUTUBE_API_KEY": "k"})] == ["youtube_api", "ytdlp", "public_page"]
    assert [s.name for s in SRC.chain("instagram", {"META_GRAPH_TOKEN": "t", "IG_BUSINESS_USER_ID": "1"})][0] == "meta_graph"
    assert [s.name for s in SRC.chain("tiktok", {})] == ["public_page"]


# ------------------------------------------------------------------------------------------------ crawler policy
def test_public_fallback_refuses_tos_blocked_hosts_without_any_request():
    c, net, _ = crawler({})
    for url in ("https://www.instagram.com/reel/x/", "https://www.tiktok.com/@a/video/1", "https://x.com/a/status/1",
                "https://www.facebook.com/reel/1", "https://www.threads.net/@a/post/1"):
        with pytest.raises(crawl.Refused, match="terms"):
            c.check({"kind": "public", "url": url})
    assert net.calls == []


def test_public_fallback_robots_allow_deny_unreachable_and_crawl_delay():
    page = {"status": 200, "text": fx("public_page.html")}
    c, net, clk = crawler({"https://ok.example.org/robots.txt": {"status": 200, "text": fx("robots_allow.txt")},
                           "https://ok.example.org/": page,
                           "https://no.example.org/robots.txt": {"status": 200, "text": fx("robots_deny.txt")},
                           "https://down.example.org/robots.txt": {"status": 503, "text": ""}})
    with pytest.raises(crawl.Refused, match="robots"):
        c.check({"kind": "public", "url": "https://no.example.org/v/1"})
    with pytest.raises(crawl.Refused, match="robots"):
        c.check({"kind": "public", "url": "https://down.example.org/v/1"})            # unreachable robots = disallow
    with pytest.raises(crawl.Refused, match="robots"):
        c.check({"kind": "public", "url": "https://ok.example.org/private/1"})
    for k in range(3):
        assert c._do({"kind": "public", "url": f"https://ok.example.org/v/{k}", "host": "ok.example.org"})
    assert clk.slept and all(s >= 5.0 - 1e-9 for s in clk.slept)                       # Crawl-delay: 5 honoured
    assert all("cookie" not in {h.lower() for h in (r.get("headers") or {})} for r in net.calls)


def test_https_only_no_cookies_no_cookie_flags_and_request_cap():
    c, _, _ = crawler({}, max_requests=1)
    with pytest.raises(crawl.Refused, match="https"):
        c.check({"kind": "api", "url": "http://www.googleapis.com/youtube/v3/search"})
    with pytest.raises(crawl.Refused, match="cookies"):
        c.check({"kind": "api", "url": "https://api.x.com/2/x", "headers": {"Cookie": "a=b"}})
    with pytest.raises(crawl.Refused, match="yt-dlp"):
        c.check({"kind": "ytdlp", "argv": ["yt-dlp", "--skip-download", "--cookies-from-browser", "chrome", "x"]})
    with pytest.raises(crawl.Refused, match="yt-dlp"):
        c.check({"kind": "ytdlp", "argv": ["yt-dlp", "x"]})                              # would download media
    c.n_requests = 1
    with pytest.raises(crawl.Refused, match="cap"):
        c.check({"kind": "api", "url": "https://api.x.com/2/x"})


def test_live_io_is_off_by_default(monkeypatch):
    monkeypatch.setattr(crawl, "LIVE", False)
    with pytest.raises(crawl.Refused, match="DISCOVER_LIVE"):
        crawl.live_fetcher({})({"url": "https://www.googleapis.com/youtube/v3/search"})
    with pytest.raises(crawl.Refused, match="DISCOVER_LIVE"):
        crawl.live_runner()(["yt-dlp", "--skip-download"])


def _routes():
    return {"https://www.googleapis.com/youtube/v3/search": {"status": 200, "json": fx("youtube_search.json")},
            "https://www.googleapis.com/youtube/v3/videos": {"status": 200, "json": fx("youtube_videos.json")},
            "https://open.tiktokapis.com/": {"status": 200, "json": fx("tiktok_research.json")}}


def test_run_daily_official_first_dedupe_budget_and_shortfall():
    env = {"YOUTUBE_API_KEY": "k", "TIKTOK_RESEARCH_TOKEN": "t"}
    seeds = {"queries": [{"id": "Q01", "query": "chair exercises for seniors"}, {"id": "Q02", "query": "mobility over 60"}],
             "creators": [{"id": "C001", "platform": "tiktok", "handle": "@unknown", "status": "to_verify"}]}
    c, net, _ = crawler(_routes(), env=env)
    res = crawl.run(seeds, c, now=NOW, platforms=("youtube", "tiktok"))
    ids = [(r["platform"], r["id"]) for r in res["rows"]]
    assert len(ids) == len(set(ids))                                                    # deduped across seeds
    assert {p for p, _ in ids} == {"youtube", "tiktok"} and res["counts"]["raw"] > res["counts"]["deduped"]
    assert res["shortfall"] == 500 - len(res["rows"])
    assert not any(r.get("kind") == "public" for r in net.calls)                       # official APIs answered
    assert {l["source"] for l in res["log"] if "items" in l} == {"youtube_api", "tiktok_research"}
    c2, _, _ = crawler(_routes(), env=env, cfg={"daily_max_posts": 2})
    assert len(crawl.run(seeds, c2, now=NOW, platforms=("youtube", "tiktok"))["rows"]) == 2


def test_unverified_creator_never_uses_public_fallback():
    seeds = {"queries": [], "creators": [{"id": "C9", "platform": "tiktok", "handle": "@maybe", "status": "to_verify",
                                          "url": "https://ok.example.org/v/1"}]}
    c, net, _ = crawler({"https://ok.example.org/": {"status": 200, "text": "User-agent: *\nAllow: /\n"}})
    crawl.run(seeds, c, now=NOW, platforms=("tiktok",))
    assert net.calls == []


def test_stream_mode_keeps_only_the_window():
    c, _, _ = crawler(_routes(), env={"YOUTUBE_API_KEY": "k"})
    res = crawl.run({"queries": [{"id": "Q01", "query": "x"}]}, c, now=datetime(2026, 9, 30, 16, 0, tzinfo=timezone.utc),
                    mode="stream", platforms=("youtube",))
    assert [r["id"] for r in res["rows"]] == ["yt1"] and res["shortfall"] == 0


# ------------------------------------------------------------------------------------------------ genes / normalize
@pytest.mark.parametrize("hook,g", [
    ("If you can't stand up without your hands, try this", "IF_EVERY"),
    ("It's not your knees. It's your hips.", "NOT_X"),
    ("Watch what happens when you do this", "WATCH"),
    ("Send this to your sister", "SHARE"),
    ("The myth about walking after 60", "MYTH"),
    ("Grab a chair. How many can you do in 30 seconds?", "TEST_NOW"),
    ("Towel, wall, chair: that's it", "OBJ3"),
    ("Sunday thoughts", "CUR"),
])
def test_grammar_rules(hook, g):
    assert GN.grammar(hook) == g


def test_genes_use_the_scorecard_decomposition():
    it = SRC.item(platform="tiktok", id="1", title_or_caption="Watch what happens when you stretch your hips every "
                  "morning over 60. Comment HIPS", duration_s=35)
    d = GN.derive(it)
    b = V.decompose({"master_id": "N-tiktok-1", "duration_s": 35.0, "hook_text": d["hook_line"], "body_text": "",
                     "hook_grammar": d["hook_grammar"], "pillar": d["pillar"], "format": d["format"], "cta_keyword": "HIPS"})
    assert (d["hook_family"], d["body_family"], d["close_family"]) == (b["hook"]["family"], b["body"]["family"], "HIPS")
    card = {"hook_family": d["hook_family"], "body_family": d["body_family"], "close_family": d["close_family"]}
    assert d["genes"] == A.genes_of(card) == ["hook:WATCH", f"body:{d['pillar']}:{d['format']}", "close:HIPS"]
    assert d["format"] in CAT.PILLAR_FORMATS[d["pillar"]] and d["lane"] == "movement"


def test_normalize_posts_csv_schema_and_relative_performance():
    hdr = (config.SPEC_DIR / "data" / "posts.csv").read_text().splitlines()[0].split(",")
    assert list(N.POSTS_CSV_COLUMNS) == hdr
    base = dict(platform="youtube", creator="@a", title_or_caption="chair exercise for seniors", duration_s=40)
    items = [SRC.item(id=f"v{k}", published_at=(NOW - timedelta(days=k)).isoformat(), views=v, **base)
             for k, v in enumerate([10000, 1000, 1000, 1000, 1000])]
    items.append(SRC.item(platform="instagram", id="ig1", creator="@b", likes=100, comments=10, published_at=NOW.isoformat(),
                          title_or_caption="balance over 60"))
    rows = N.rows(items, now=NOW)
    by = {r["id"]: r for r in rows}
    assert by["v0"]["rel_perf"] == 10.0 and by["v0"]["baseline"] == "creator"
    assert by["ig1"]["metric"] == "engagement" and by["ig1"]["metric_value"] == 120 and by["ig1"]["baseline"] == "niche"
    csv_row = N.posts_csv_row(by["v0"])
    assert list(csv_row) == list(N.POSTS_CSV_COLUMNS) and csv_row["platform"] == "YouTube" and csv_row["id"] == "youtube_v0"
    db = N.db_row(by["v0"])
    assert db["external_id"] == "v0" and db["genes"] and len(db["content_sha"]) == 64
    assert not any(k in db for k in ("video", "media", "thumbnail", "audio"))


# ------------------------------------------------------------------------------------------------ trends
def _row(plat, i, gene_hook, rel, days_ago, pillar="P05", fmt="F20", lane="movement", dur=35):
    return {"platform": plat, "id": f"{plat}{i}", "url": "", "account": "@a", "rel_perf": rel, "rel_niche": rel,
            "velocity_per_h": 100.0 * rel, "published_at": (NOW - timedelta(days=days_ago, hours=1)).isoformat(),
            "hook_grammar": gene_hook, "pillar": pillar, "format": fmt, "lane": lane, "duration_s": dur,
            "duration_bucket": "30-44s", "cta_keyword": "", "claim_strength": "none", "hook_line": "x",
            "hook_family": gene_hook, "body_family": f"{pillar}:{fmt}", "close_family": "close",
            "genes": [f"hook:{gene_hook}", f"body:{pillar}:{fmt}", "close:close"]}


def _trend_rows():
    rows = [_row("tiktok", i, "WATCH", 6.0, 1 + i % 3) for i in range(4)]             # rising on TikTok
    rows += [_row("tiktok", 10 + i, "WATCH", 1.0, 15 + i) for i in range(4)]          # ... vs its prior window
    rows += [_row("instagram", 20 + i, "MYTH", 5.0, 1 + i % 3, pillar="P15", fmt="F04") for i in range(3)]
    rows += [_row("instagram", 30 + i, "IF_EVERY", 0.6, 2, pillar="P02", fmt="F01") for i in range(3)]
    return rows


def test_transfer_opportunities_both_directions():
    out = TR.detect(_trend_rows(), now=NOW)
    to_ig = [o for o in out["opportunities"] if o["direction"] == "to_instagram"]
    from_ig = [o for o in out["opportunities"] if o["direction"] == "from_instagram"]
    assert any(o["gene"] == "hook:WATCH" and o["from_platform"] == "tiktok" and o["ig_state"] == "absent" for o in to_ig)
    assert any(o["gene"] == "hook:MYTH" and set(o["to_platforms"]) == {"tiktok", "x", "facebook"} for o in from_ig)
    assert not any(o["gene"] == "hook:IF_EVERY" for o in out["opportunities"])        # not rising anywhere
    w = next(t for t in out["rising_genes"] if t["gene"] == "hook:WATCH")
    assert w["lift"] >= 1.5 and len(w["top_posts"]) == 3


def test_feeds_sizes_windows_and_gate_refit():
    rows = _trend_rows() + [_row("youtube", 100 + i, "DEMO", 1.0 + i / 10, 0.5) for i in range(40)]
    out = TR.detect(rows, now=NOW)
    assert len(out["daily_top20"]) == 20 and len(out["weekly_top50"]) == 50
    cutoff = NOW - timedelta(hours=48)
    by = {f"{r['platform']}{r['id']}": r for r in rows}
    assert all(N.parse_dt(by[t["platform"] + t["id"]]["published_at"]) >= cutoff for t in out["daily_top20"])
    scores = [t["trend_score"] for t in out["weekly_top50"]]
    assert scores == sorted(scores, reverse=True)
    labels = [g["label_top_quartile"] for g in out["gate_refit"]]
    assert len(labels) == len(rows) and 0 < sum(labels) < len(labels)


def test_exploration_observations_feed_the_allocator_at_low_weight():
    out = TR.detect(_trend_rows(), now=NOW)
    obs = out["exploration_observations"]
    assert obs and all(o["weight"] == 0.2 and 0 <= o["reward"] <= 1 for o in obs)
    keyed = [o for o in obs if "arm_key" in o]
    assert keyed and all(set(AL.parse_arm_key(o["arm_key"])) == {"pillar", "grammar", "format", "speaker", "length"} for o in keyed)
    cfg = G.load()
    before = AL.hook_family_posterior([], cfg, NOW)["WATCH"]["mean"]
    after = AL.hook_family_posterior(obs, cfg, NOW)["WATCH"]["mean"]
    assert after > before


def test_velocity_from_reads():
    reads = [{"captured_at": "2026-10-02T10:00:00Z", "metric_value": 1000},
             {"captured_at": "2026-10-02T11:00:00Z", "metric_value": 4000}]
    assert TR.velocity_from_reads(reads) == 3000.0 and TR.velocity_from_reads(reads[:1]) is None


# ------------------------------------------------------------------------------------------------ remake briefs
def _src_row(**k):
    r = {"platform": "tiktok", "id": "7400000000000000001", "url": "https://www.tiktok.com/@fitover60/video/7400000000000000001",
         "account": "@fitover60", "crawled_at": NOW.isoformat(), "source": "tiktok_research", "rel_perf": 9.0,
         "hook_line": "Watch what happens when you do this every morning over 60",
         "title_or_caption": "Watch what happens when you do this every morning over 60 #mobility",
         "transcript": "Watch what happens when you do this every morning. Hips first. Comment HIPS for the plan.",
         "overlay_text": "", "pillar": "P05", "hook_grammar": "WATCH", "lane": "movement", "hook_family": "WATCH",
         "body_family": "P05:F20", "close_family": "HIPS"}
    r.update(k)
    return r


def test_remake_brief_shape_voice_bit_hooks_lane():
    b = RM.brief(_src_row(), now=NOW)
    assert b["mechanism"] and b["speaker"] == "CHANG" and "Chang" in b["angle"]
    assert b["running_bit"] in RM.BITS_BY_SPEAKER["CHANG"] and b["running_bit"] in CAT.RUNNING_BITS
    assert len(b["hooks"]) == 3 and len({h["grammar"] for h in b["hooks"]}) == 3
    assert all(len(h["hook"].split()) <= 16 for h in b["hooks"]) and b["lane"] == "movement"
    assert b["guard"]["ok"]
    kitchen = RM.brief(_src_row(pillar="P11", lane="insert", hook_grammar="KITCHEN_SERIES"), now=NOW)
    assert kitchen["speaker"] == "SUN" and kitchen["running_bit"] in RM.BITS_BY_SPEAKER["SUN"]


def test_plagiarism_guard_no_reused_line_no_7_word_shingle():
    src = _src_row()
    b = RM.brief(src, n_hooks=5, now=NOW)
    written = " ".join([h["hook"] for h in b["hooks"]] + [b["angle"], b["mechanism"], b["visual_concept"]])
    assert not (RM.shingles(written) & RM.shingles(RM.source_text(src)))
    # a source that already says our WATCH template line: that hook is dropped, the rest still fill the brief
    ours = RM.HOOK_TEMPLATES["WATCH"].format(obj="towel", topic="")
    stolen = _src_row(hook_line=ours, transcript=ours, title_or_caption=ours)
    hooks = RM.hooks_for(stolen, 3)
    assert ours not in [h["hook"] for h in hooks] and len(hooks) == 3
    g = RM.guard(["a totally new line", "It's what you stopped doing with the towel every day"],
                 "Honestly it's what you stopped doing with the towel every day, folks.")
    assert not g["ok"] and g["shared_shingles"]
    assert not RM.guard(["Hips first."], "Hips first. Comment now.")["ok"]                 # identical line reused


def test_queue_item_provenance_and_visual_concept_only():
    q = RM.queue_item(_src_row(), now=NOW)
    p = q["provenance"]
    assert p["platform"] == "tiktok" and p["external_id"] == "7400000000000000001" and len(p["content_sha"]) == 64
    assert q["must_pass"] == ["/compliance/scan", "llm_judge", "/uniqueness/check"]
    assert "http" not in json.dumps(q["brief"])                       # no source media / URL inside the brief
    assert RM.queue_item(_src_row(), n_hooks=5, now=NOW)["brief"]["hooks"].__len__() == 5


def test_queue_puts_transfers_first():
    rows = [_src_row(), _src_row(platform="youtube", id="yt9", pillar="P02", hook_grammar="IF_EVERY", lane="talking_head")]
    feeds = {"opportunities": [{"direction": "to_instagram", "gene": "hook:WATCH", "from_platform": "tiktok",
                                "evidence_post_ids": ["7400000000000000001"]}],
             "daily_top20": [{"platform": "youtube", "id": "yt9"}, {"platform": "tiktok", "id": "7400000000000000001"}]}
    q = RM.queue(rows, feeds, now=NOW)
    assert [x["reason"] for x in q] == ["transfer:to_instagram", "top_performer"] and q[0]["priority"] > q[1]["priority"]


def test_remake_hooks_pass_the_deterministic_compliance_scan():
    from compliance import scanner
    for p in RM.PILLAR_BRIEF:
        for h in RM.hooks_for({"pillar": p, "hook_grammar": "CUR"}, 5):
            res = scanner.scan(text=h["hook"])
            assert scanner.verdict_of(res) != "block", (p, h, res.get("hits"))


# ------------------------------------------------------------------------------------------------ API
@pytest.fixture
def client():
    return TestClient(app)


def test_api_end_to_end_offline(client):
    s = client.get("/discover/seeds", headers=AUTH).json()
    assert s["counts"] == {"queries": 60, "creators": 100, "to_verify": 100}
    pushed = [{"source": "tiktok_research", "payload": fx("tiktok_research.json"), "seed": "Q01"},
              {"source": "x_api", "payload": fx("x_recent.json")},
              {"source": "meta_content_library", "payload": fx("meta_content_library.json")},
              {"source": "nope", "payload": {}}]
    c = client.post("/discover/crawl", headers=AUTH, json={"payloads": pushed, "now": NOW.isoformat()}).json()
    assert c["counts"]["kept"] == 4 and c["skipped"] == [{"source": "nope", "reason": "unknown source"}]
    assert all(list(r) == list(N.POSTS_CSV_COLUMNS) for r in c["posts_csv"]) and len(c["niche_posts"]) == 4
    t = client.post("/discover/trends", headers=AUTH, json={"rows": c["rows"], "now": NOW.isoformat()}).json()
    assert set(t) >= {"daily_top20", "weekly_top50", "opportunities", "gate_refit", "exploration_observations"}
    r = client.post("/discover/remake", headers=AUTH, json={"rows": c["rows"], "feeds": t, "now": NOW.isoformat()}).json()
    assert r["count"] >= 1 and all(q["brief"]["guard"]["ok"] for q in r["remake_queue"])
    assert client.post("/discover/crawl", headers=AUTH, json={"live": True}).status_code == 409
    assert client.post("/discover/crawl", json={}).status_code in (401, 403)


def test_api_value_endpoint(client):
    card = {"post_id": "p1", "page_id": "A", "platform": "instagram",
            "scores": {"hook": 90, "shares": 85, "saves": 80, "conversion": 95}}
    body = {"cards": [card], "attribution": {"p1": {"views": 100000, "mrr_usd": 2500, "buyers": 40}}, "mode": "print",
            "posts": [{"post_id": "p1", "arm": {"pillar": "P01", "grammar": "IF_EVERY", "format": "F02", "speaker": "CHANG", "length": "M"}}],
            "pages": [{"id": "A", "slug": "changyin", "status": "active"}, {"id": "B", "slug": "sunyoon", "status": "active"}],
            "now": NOW.isoformat()}
    out = client.post("/discover/value", headers=AUTH, json=body).json()
    assert out["values"][0]["mode"] == "print" and out["plan"]["counts"]["go_hard"] == 1
    assert out["plan"]["boost_candidates"][0]["status"] == "held_until_spend_gate"
    assert client.post("/discover/value", headers=AUTH, json={**body, "mode": "yolo"}).status_code == 422
