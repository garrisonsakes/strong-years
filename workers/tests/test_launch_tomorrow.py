"""Launch-tomorrow cut (ENGINE_SAVAGE20 §B(b) 2–6 and #2): essential tests only, no rendering, no network.

  2 competitor corpus   uniqueness/external.check_external
  3 caption rules       compliance/caption_rules (+ fallback pack applies them)
  4 frame-1 OCR         qa/frame1.check_frame1 on synthetic frames (skips without tesseract)
  5 manual metrics CSV  growth/manual_import.normalize_manual_csv -> snapshots.build
  6 posted log          packager/fallback posted_log.csv -> read_posted_log -> join_posted_log
 10 hook pre-screen     growth/hook_prescreen plan / package / score
"""
from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont

from compliance import caption_rules
from growth import hook_prescreen, manual_import, snapshots
from packager import fallback
from qa import frame1, ocr
from uniqueness import external

ROOT = Path(__file__).resolve().parents[2]
FONT = Path(__file__).resolve().parents[1] / "fonts" / "Figtree-ExtraBold.ttf"


# ------------------------------------------------------------------ 2. competitor corpus
@pytest.fixture(scope="module")
def corpus():
    niche = [{"external_id": "N1", "title_or_caption": "drop two onions into a pot of boiling water and watch what happens to your knees"}]
    return external.CorpusIndex(external.load_corpus(niche_rows=niche))


def test_corpus_loads_posts_transcripts_and_niche_rows(corpus):
    srcs = {d["source"].split(":")[0] for d in corpus.docs}
    assert {"posts.csv", "niche_posts"} <= srcs
    assert len(corpus.docs) > 100


def test_copied_line_fails_the_gate_and_original_passes(corpus):
    copied = "Grandma says drop two onions into a pot of boiling water and watch what happens. Comment HEAL."
    r = external.check_external(copied, corpus)
    assert r["allow"] is False and any("7-word shingle" in x for x in r["reasons"])
    mine = "Chair against the wall. Arms crossed. Thirty seconds, count every full stand out loud."
    assert external.check_external(mine, corpus)["allow"] is True


def test_day1_posts_clear_the_competitor_corpus(corpus):
    plan = json.loads((ROOT / "production/launch_day/day1_plan.json").read_text(encoding="utf-8"))
    for p in plan["posts"]:
        r = external.check_external(p, corpus)
        assert r["allow"], (p["post_id"], r["reasons"])


# ------------------------------------------------------------------ 3. caption rules
def test_time_words_become_evergreen_but_safety_lines_stay():
    t, notes = caption_rules.rewrite_time_words("Try it today. Tonight before bed. That's for your doctor, today.")
    assert t == "Try it now. At night before bed. That's for your doctor, today."
    assert len(notes) == 2
    assert caption_rules.time_words("That one isn't for exercise. That's for your doctor, today.") == []


def test_handle_allowlist_blocks_foreign_handles_only():
    r = caption_rules.apply("Made with @changyin and @sunyoon.kitchen. Inspired by @yangmunus. mail team@strongyears.com")
    assert r["ok"] is False and r["blocked_handles"] == ["@yangmunus"]
    assert caption_rules.apply("Follow @changandsun.")["ok"] is True


def test_fallback_pack_rewrites_time_words_and_holds_foreign_handles(tmp_path):
    base = {"post_id": "S1", "page": "changyin", "platform": "ig", "variant_id": "S1-ig-v1", "is_aigc": True,
            "uniqueness": {"allow": True, "reasons": []}, "video": "https://cdn.example/S1.mp4",
            "caption": "Do this tonight. Chang Yin is an AI character. Not medical advice.", "hashtags": [],
            "first_comment": "Comment STRONG.", "scheduled_at": "2026-10-03T08:00:00-04:00"}
    m = fallback.build_pack("2026-10-03", [base, {**base, "platform": "fb", "variant_id": "S1-fb-v1",
                                                  "caption": base["caption"] + " h/t @yangmunus"}], tmp_path)
    assert [p["platform"] for p in m["packed"]] == ["ig"] and "handles" in m["held"][0]["reason"]
    cap = (tmp_path / "2026-10-03/changyin/ig/caption.txt").read_text()
    assert "tonight" not in cap.lower() and "at night" in cap


# ------------------------------------------------------------------ 4. frame-1 OCR
def _frame(text: str, fg=(255, 255, 255), bg=(20, 20, 20), size=96) -> Image.Image:
    img = Image.new("RGB", (1080, 1920), bg)
    y0, _ = frame1.hook_zone("ig")
    d, f = ImageDraw.Draw(img), ImageFont.truetype(str(FONT), size)
    for i, line in enumerate(text.split("\n")):
        d.text((90, y0 + 120 + i * int(size * 1.3)), line, font=f, fill=fg)
    return img


@pytest.mark.skipif(not ocr.available(), reason="tesseract not installed")
def test_frame1_passes_a_short_legible_hook_and_flags_bad_ones():
    ok = frame1.check_frame1(_frame("STAND UP\nNO HANDS"), "ig", expected="Stand up. No hands.")
    assert ok["ok"] is True, ok
    long = frame1.check_frame1(_frame("THIS HOOK HAS\nFAR TOO MANY WORDS\nFOR FRAME ONE", size=80), "ig")
    assert long["ok"] is False and any("words" in p for p in long["problems"])
    assert frame1.check_frame1(Image.new("RGB", (1080, 1920), (20, 20, 20)), "ig")["ok"] is False
    low = frame1.check_frame1(_frame("STAND UP", fg=(200, 200, 200), bg=(175, 175, 175)), "ig")
    assert low["ok"] is False
    wrong = frame1.check_frame1(_frame("SOUP NIGHT"), "ig", expected="Stand up. No hands.")
    assert any("does not match" in p for p in wrong["problems"])


# ------------------------------------------------------------------ 5 + 6. posted log -> manual metrics import
IG_EXPORT = """Post ID,Account ID,Account username,Account name,Description,Duration (sec),Publish time,Permalink,Post type,Views,Reach,Likes,Shares,Follows,Comments,Saves
18011,1784,changyin,Chang Yin,Chair test,44,10/03/2026 08:31,https://www.instagram.com/reel/DAbc123/,IG reel,"12,400",9100,610,88,41,57,230
"""
TT_EXPORT = """Video title,Video link,Post time,Total likes,Total comments,Total shares,Total views,Total play time,Average watch time,Watched full video,Add to favorites
Chair test,https://www.tiktok.com/@changyin/video/7400000000000000001,2026-10-03 09:10,300,22,15,5000,,12.5,0.31,40
"""
YT_EXPORT = """Content,Video title,Video publish time,Duration,Views,Average view duration,Average percentage viewed (%),Subscribers,Likes
Total,,,,9000,,,,
abcDEF12345,Chair test,"Oct 3, 2026",44,9000,0:00:20,45.4,12,300
"""


def test_manual_csv_exports_normalize_to_captures():
    ig = manual_import.normalize_manual_csv(IG_EXPORT, captured_at="2026-10-03T14:30:00-04:00")
    assert ig["format"] == "ig" and len(ig["rows"]) == 1
    row = ig["rows"][0]
    assert row["post"]["platform"] == "ig" and row["post"]["permalink"].endswith("/DAbc123/")
    assert row["capture"]["views"] == 12400 and row["capture"]["saves"] == 230
    tt = manual_import.normalize_manual_csv(TT_EXPORT, captured_at="2026-10-03T15:10:00-04:00")
    assert tt["format"] == "tt" and tt["rows"][0]["capture"]["views"] == 5000
    yt = manual_import.normalize_manual_csv(YT_EXPORT, captured_at="2026-10-04T09:00:00-04:00")
    assert yt["format"] == "yt" and len(yt["rows"]) == 1 and yt["rows"][0]["post"]["external_post_id"] == "abcDEF12345"
    with pytest.raises(ValueError):
        manual_import.normalize_manual_csv("foo,bar\n1,2\n")


def test_posted_log_joins_metrics_to_our_post_ids_and_snapshots_build(tmp_path):
    log = tmp_path / "posted_log.csv"
    fallback.write_posted_log_template(log, [
        {"post_id": "D1-CY-1", "page": "@changyin", "platform": "ig", "variant_id": "D1-CY-1-ig",
         "scheduled_at": "2026-10-03T08:30:00-04:00", "trial": "n", "status": "due"},
        {"post_id": "D1-CY-2", "page": "@changyin", "platform": "ig", "variant_id": "D1-CY-2-ig",
         "scheduled_at": "2026-10-03T12:30:00-04:00", "trial": "n", "status": "due"},
        {"post_id": "D1-CY-3", "page": "@changyin", "platform": "ig", "variant_id": "D1-CY-3-ig",
         "scheduled_at": "2026-10-03T19:00:00-04:00", "trial": "n", "status": "due"}])
    rows = list(csv.DictReader(log.open()))
    rows[0].update(status="posted", posted_at="2026-10-03T08:31:00-04:00", permalink="https://www.instagram.com/reel/DAbc123/",
                   posted_by="maria", ai_label="y")
    rows[1].update(status="posted", posted_at="2026-10-03T13:20:00-04:00", permalink="https://evil.example/reel/x",
                   posted_by="maria", ai_label="n")
    rows[2].update(status="skipped")
    with log.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fallback.POSTED_LOG_FIELDS)
        w.writeheader()
        w.writerows(rows)
    got = fallback.read_posted_log(log)
    assert [p["post_id"] for p in got["posted"]] == ["D1-CY-1"] and got["posted"][0]["external_post_id"] == "DAbc123"
    assert len(got["skipped"]) == 1 and any("permalink" in p for p in got["problems"])
    imp = manual_import.normalize_manual_csv(IG_EXPORT, captured_at="2026-10-03T14:30:00-04:00")
    matched, unmatched = manual_import.join_posted_log(imp["rows"], got["posted"])
    assert unmatched == [] and matched[0]["post"]["post_id"] == "D1-CY-1"
    snap = snapshots.build(matched[0]["post"], [matched[0]["capture"]],
                           now=datetime.fromisoformat("2026-10-03T15:00:00-04:00"))
    assert snap["horizons_available"] == [6] and snap["snapshots"][0]["platform"] == "instagram"
    assert snap["snapshots"][0]["published_at"] == "2026-10-03T08:31:00-04:00"   # the log's offset wins over the export


def test_posted_late_is_reported(tmp_path):
    p = tmp_path / "late.csv"
    fallback.write_posted_log_template(p, [{"post_id": "X", "page": "@changyin", "platform": "ig", "variant_id": "X-ig",
                                            "scheduled_at": "2026-10-03T08:30:00-04:00", "status": "posted"}])
    rows = list(csv.DictReader(p.open()))
    rows[0].update(posted_at="2026-10-03T09:30:00-04:00", permalink="https://www.instagram.com/reel/Q1/", posted_by="a", ai_label="y")
    with p.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fallback.POSTED_LOG_FIELDS)
        w.writeheader()
        w.writerows(rows)
    assert any("late" in x for x in fallback.read_posted_log(p)["problems"])


# ------------------------------------------------------------------ 10. hook pre-screen
HOOKS = [{"id": f"H{i:02d}", "hook": h, "page": pg, "speaker": sp, "rank_score": 1 - i / 100}
         for i, (h, pg, sp) in enumerate([
             ("If you use your hands to stand, try this tonight.", "CY", "CHANG"),
             ("Fifty years of soup. One rule.", "SK", "SUN"),
             ("Sit down. Stand up. No hands. How many?", "ST", "CHANG"),
             ("He hid the cookies. I found them.", "CS", "BOTH"),
             ("Your grip at 70 says more than you think.", "CY", "CHANG"),
             ("Too old to lift? Not at 74.", "ST", "CHANG"),
             ("This tea cures arthritis.", "SK", "SUN"),            # blocked claim: never probed
             ("Thanks @yangmunus for this one.", "CY", "CHANG"),     # foreign handle: never probed
             ("The 30-second chair test.", "CY", "CHANG"),
             ("Ginger in the porridge, every time.", "SK", "SUN"),
             ("Balance on one foot while the kettle boils.", "CY", "CHANG"),
             ("Three things I stopped doing at 70.", "CS", "BOTH"),
             ("Stand on one foot. Count.", "ST", "CHANG"),
         ])]


def test_prescreen_plans_top10_on_threads_and_x_and_scores_at_6h():
    probes = hook_prescreen.plan("2026-10-03", HOOKS)
    ids = {p["hook_id"] for p in probes}
    assert len(ids) == 10 and "H06" not in ids and "H07" not in ids
    assert {p["platform"] for p in probes} == {"th", "x"} and len(probes) == 20
    assert all(p["role"] == "text_probe" and "AI character" in p["text"] for p in probes)
    assert all("tonight" not in p["text"].lower() for p in probes)
    assert {p["scheduled_at"][11:16] for p in probes} == {"07:00", "19:00"}
    packed = hook_prescreen.package_probes(probes)
    assert all(x["platform"] in ("th", "x") and "http" not in (x["caption"] if x["platform"] == "x" else "") for x in packed)
    caps = {}
    for j, p in enumerate(probes):
        t0 = datetime.fromisoformat(p["scheduled_at"])
        likes = 80 if p["hook_id"] == "H02" else 5 + j % 3
        caps[p["probe_id"]] = [{"captured_at": (t0 + timedelta(hours=2)).isoformat(), "views": 100, "likes": 50},  # too early
                               {"captured_at": (t0 + timedelta(hours=6, minutes=5)).isoformat(), "views": 1000, "likes": likes}]
    s = hook_prescreen.score(probes, caps, render_n=6)
    assert s["render"][0] == "H02" and len(s["render"]) == 6 and s["pending"] == []
    assert s["ranked"][0]["beta_prior"]["alpha"] > s["ranked"][-1]["beta_prior"]["alpha"]
    due = hook_prescreen.read_due(probes, datetime.fromisoformat("2026-10-03T13:30:00-04:00"))
    assert {p["scheduled_at"][11:16] for p in due} == {"07:00"}
