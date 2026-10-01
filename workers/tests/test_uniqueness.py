from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from common import config, media
from uniqueness import audiofp, guard, phash, textsim
from tests.conftest import AUTH

SCRIPT_A = ("Sit down. Stand up. No hands. How many in thirty seconds? Chair against the wall. Arms crossed. "
            "Men seventy to seventy-four, under twelve is below average. Your number is the one that matters. "
            "Comment STRONG for the chair builder.")
SCRIPT_NEAR = ("Sit down. Stand up. No hands. How many in thirty seconds? Put the chair against the wall. Arms crossed. "
               "Men seventy to seventy-four, under twelve is below average. Your number matters most. "
               "Comment LEGS for the chair plan.")
SCRIPT_DIFF = ("Two kiwis a day did about as well as prunes for constipation in a small study of seventy-five people. "
               "Cut in half and spoon it out. Go up slowly and drink water. Comment GUT for the fiber ladder.")


@pytest.fixture(scope="module")
def near_dup(master):
    """Same master re-encoded with a small crop/brightness change (what a lazy 'variant' would look like)."""
    out = config.WORK_DIR / "near_dup.mp4"
    media.ffmpeg(["-i", master["local_path"], "-vf", "crop=iw*0.96:ih*0.96,scale=1080:1920,eq=brightness=0.03",
                  "-c:v", "libx264", "-preset", "superfast", "-c:a", "aac", str(out)])
    return out


@pytest.fixture(scope="module")
def distinct(synth, tmp_path_factory):
    d = tmp_path_factory.mktemp("distinct")
    out = d / "distinct.mp4"
    media.ffmpeg(["-f", "lavfi", "-i", "mandelbrot=s=540x960:r=30", "-f", "lavfi", "-i",
                  "flite=text='Two kiwis a day did as well as prunes in a small study':voice=slt", "-t", "8",
                  "-vf", "scale=1080:1920", "-c:v", "libx264", "-preset", "superfast", "-c:a", "aac", "-shortest", str(out)])
    return out


def test_phash_identical_near_and_distinct(master, near_dup, distinct):
    a = master["phash_seq"]
    assert phash.seq_overlap(a, a) == 1.0
    assert phash.seq_overlap(a, phash.video_phash_seq(near_dup)) > 0.4
    assert phash.seq_overlap(a, phash.video_phash_seq(distinct)) < 0.4


def test_phash_image_hash_is_stable(tmp_path):
    from PIL import Image
    img = Image.fromarray((np.random.default_rng(1).random((128, 128)) * 255).astype("uint8"))
    img.save(tmp_path / "a.png")
    img.resize((64, 64)).resize((128, 128)).save(tmp_path / "b.png")
    assert phash.hamming(phash.phash_image(tmp_path / "a.png"), phash.phash_image(tmp_path / "b.png")) <= 10


@pytest.mark.parametrize("method", ["chromaprint", "spectral"])
def test_audio_fingerprint_same_vs_different(master, near_dup, distinct, method):
    if method == "chromaprint" and not audiofp.chromaprint_available():
        pytest.skip("ffmpeg built without chromaprint")
    fa = audiofp.fingerprint(master["local_path"], method)
    assert audiofp.similarity(fa, audiofp.fingerprint(near_dup, method)) >= 0.8
    assert audiofp.similarity(fa, audiofp.fingerprint(distinct, method)) < 0.8


def test_text_similarity_measures():
    assert textsim.tfidf_cosine(SCRIPT_A, SCRIPT_NEAR) > 0.8
    assert textsim.tfidf_cosine(SCRIPT_A, SCRIPT_DIFF) < 0.3
    assert textsim.minhash_jaccard(SCRIPT_A, SCRIPT_A) == 1.0
    run, words = textsim.longest_shared_run(SCRIPT_A, SCRIPT_NEAR)
    assert run > 6
    # safety/CTA lines don't count as copying
    s1 = "Walk after dinner. Stop if you feel chest pain, dizziness, or sharp pain. Comment WALK for the plan."
    s2 = "Carry the groceries. Stop if you feel chest pain, dizziness, or sharp pain. Comment CARRY for the plan."
    assert textsim.longest_shared_run(s1, s2)[0] <= 6


def _cand(**kw):
    c = {"id": "c1", "page_id": "pageA", "platform": "all", "script_text": SCRIPT_A,
         "scheduled_at": "2026-10-05T09:35:00+00:00", "idea_id": "idea1", "brief_id": "b1"}
    c.update(kw)
    return c


def test_guard_denies_near_duplicate_on_sibling_page(master, near_dup):
    sib = {"id": "s1", "page_id": "pageB", "platform": "instagram", "script_text": SCRIPT_NEAR,
           "phash_seq": phash.video_phash_seq(near_dup), "audio_fp": audiofp.fingerprint(near_dup),
           "scheduled_at": "2026-10-04T09:40:00+00:00", "idea_id": "idea1"}
    r = guard.check(_cand(phash_seq=master["phash_seq"], audio_fp=master["audio_fp"]), [sib])
    kinds = {x.split(":")[0] for x in r["reasons"]}
    assert not r["allow"] and {"text", "lexical", "visual", "audio", "stagger"} <= kinds


def test_guard_allows_distinct_and_same_page_crosspost(master, distinct):
    sib = {"id": "s2", "page_id": "pageB", "platform": "instagram", "script_text": SCRIPT_DIFF,
           "phash_seq": phash.video_phash_seq(distinct), "audio_fp": audiofp.fingerprint(distinct),
           "scheduled_at": "2026-10-01T15:40:00+00:00", "idea_id": "idea9"}
    same_page_other_platform = {"id": "s3", "page_id": "pageA", "platform": "tiktok", "script_text": SCRIPT_A,
                                "phash_seq": master["phash_seq"], "audio_fp": master["audio_fp"],
                                "scheduled_at": "2026-10-05T10:00:00+00:00", "idea_id": "idea1"}
    r = guard.check(_cand(platform="instagram", phash_seq=master["phash_seq"], audio_fp=master["audio_fp"]),
                    [sib, same_page_other_platform])
    assert r["allow"], r["reasons"]


def test_stagger_rule():
    base = {"id": "s", "page_id": "pageB", "script_text": SCRIPT_DIFF, "idea_id": "idea1"}
    ok = guard.check(_cand(script_text=""), [{**base, "scheduled_at": "2026-10-02T15:40:00+00:00"}])
    assert ok["allow"], ok["reasons"]                                                    # 65.9 h, different hour
    close = guard.check(_cand(script_text=""), [{**base, "scheduled_at": "2026-10-04T13:00:00+00:00"}])
    assert not close["allow"] and "48 h" in close["reasons"][0]
    same_hour = guard.check(_cand(script_text=""), [{**base, "scheduled_at": "2026-10-01T09:05:00+00:00"}])
    assert not same_hour["allow"] and "slot hour" in same_hour["reasons"][0]


def test_uniqueness_api(master):
    from app import app
    c = TestClient(app, headers=AUTH)
    r = c.post("/uniqueness/check", json={"candidate": _cand(video_url=master["local_path"]),
                                          "siblings": [{"id": "x", "page_id": "pageB", "script_text": SCRIPT_DIFF}]})
    body = r.json()
    assert r.status_code == 200 and body["allow"] and body["siblings_source"] == "request"
    r = c.post("/uniqueness/check", json={"candidate": _cand()})
    assert r.json()["allow"] and r.json()["checked"] == 0
