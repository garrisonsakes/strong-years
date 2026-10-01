from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from common import disclosure
from packager.api import PackageRequest, run
from packager.packager import package
from tests.conftest import AUTH

SCRIPT = {"has_movement": True, "cta": {"keyword": "STRONG", "deliverable": "8-Minute Chair Builder"}, "evidence": ["E11"],
          "lines": [{"i": 1, "speaker": "chang", "text": "Chair against the wall. Breathe out as you stand."}]}
LLM = {
    "instagram": {"caption": "Can you pass the 30-second chair test?\nChair against a wall, arms crossed.\n"
                             "Comment STRONG and I'll DM you the 8-Minute Chair Builder.",
                  "hashtags": ["strengthafter60", "#FallPrevention", "#fyp", "#chairexercises", "#seniorfitness",
                               "#balance", "#over60"], "alt_text": "Older man doing chair stands"},
    "tiktok": {"caption": "30 second chair test for seniors: how many can you do? Comment STRONG for the plan and "
                          "share it with your mom tonight please, she will thank you later for sure", "hashtags": ["over60"],
               "is_aigc": False},
    "youtube": {"title": "Can You Pass This 30-Second Chair Test? The Test Doctors Use After 60 (Try It Tonight)",
                "description": "Chair against a wall. Comment STRONG for the plan.", "tags": ["#over60", "chair test"],
                "contains_synthetic_media": False},
    "facebook": {"caption": "How many did you get? Comment STRONG.", "hashtags": ["#a", "#over60", "#strength", "#x2"]},
    "threads": {"text": "Sun here. " + "He counts out loud. " * 40, "attach_video": False},
    "x": {"text": "Chair stand, 70–74: under 12 is below average (CDC STEADI). Test yours: https://example.com/t",
          "attach_video": True},
}


def _pk(**kw):
    return package(LLM, script=SCRIPT, page_slug="changyin", brief_id="1234567890abcdef",
                   site_base_url="https://changandsun.example", **kw)


def test_footer_addon_flags_and_limits():
    res = _pk()
    p, foot, addon = res["packaging"], disclosure.footer("en", False), disclosure.movement_addon("en")
    for pl, f in (("instagram", "caption"), ("tiktok", "caption"), ("youtube", "description"), ("facebook", "caption")):
        assert p[pl][f].endswith(foot), pl
        assert p[pl][f][: -len(foot)].rstrip().endswith(addon), pl
    assert "reviewed by licensed" not in p["instagram"]["caption"]
    assert p["tiktok"]["is_aigc"] is True and p["youtube"]["contains_synthetic_media"] is True
    assert len(p["youtube"]["title"]) <= 60 and len(p["x"]["text"]) <= 270 and len(p["threads"]["text"]) <= 450
    assert "http" not in p["x"]["text"]
    tt_body = p["tiktok"]["caption"].split("\n\n")[0]
    assert len(tt_body) <= 150


def test_hashtags_and_cta_routing():
    res = _pk()
    p = res["packaging"]
    assert "#fyp" not in p["instagram"]["hashtags"] and len(p["instagram"]["hashtags"]) == 5
    assert all(t.startswith("#") and t == t.lower() for t in p["instagram"]["hashtags"])
    assert "comment strong" not in p["tiktok"]["caption"].lower()      # no TikTok comment triggers in the US
    assert "link in bio" in p["tiktok"]["caption"].lower()
    assert "link in channel" in p["youtube"]["description"].lower()
    assert "comment strong" in p["instagram"]["caption"].lower()       # IG DM automation exists
    assert len(p["facebook"]["hashtags"]) <= 2


def test_reviewer_signed_footer():
    p = _pk(reviewer_signed=True)["packaging"]
    assert p["instagram"]["caption"].endswith(disclosure.footer("en", True))


def test_spanish_footer_and_addon():
    p = package(LLM, script=SCRIPT, locale="es-US")["packaging"]
    assert p["instagram"]["caption"].endswith(disclosure.footer("es", False))


def test_utm_links():
    links = _pk(post_ids={"instagram": "post-1"})["links"]
    q = parse_qs(urlparse(links["instagram"]).query)
    assert q == {"utm_source": ["ig"], "utm_medium": ["organic_short"], "utm_campaign": ["changyin"],
                 "utm_content": ["12345678-ig"], "pid": ["post-1"]}
    assert parse_qs(urlparse(links["tiktok"]).query)["utm_source"] == ["tt"]


def test_idempotent_footer_not_duplicated():
    once = _pk()["packaging"]
    twice = package(once, script=SCRIPT)["packaging"]
    assert twice["instagram"]["caption"].count(disclosure.footer("en", False)) == 1


def test_pass2_clean_and_dirty(judge_pass):
    ok = run(PackageRequest(packaging=LLM, script=SCRIPT, burned_in_text=["AI character", "CHAIR TEST"],
                            transcript="Chair against the wall. Breathe out as you stand.", page_slug="changyin"))
    assert ok["pass2_ok"], ok["pass2_issues"]
    dirty = {**LLM, "facebook": {"caption": "This drink will detox your liver overnight. Comment STRONG."}}
    bad = run(PackageRequest(packaging=dirty, script=SCRIPT, burned_in_text=["CHAIR TEST"]))
    ids = {i["id"] for i in bad["pass2_issues"]}
    assert not bad["pass2_ok"] and ("BC05" in ids or "SR3.1-05" in ids) and "REQUIRE" in ids   # claim + missing AI tag


def test_package_api(judge_pass):
    from app import app
    r = TestClient(app, headers=AUTH).post("/package", json={"packaging": LLM, "script": SCRIPT, "burned_in_text": ["AI character"]})
    assert r.status_code == 200 and r.json()["pass2_ok"] is True and r.json()["links"]["x"]
