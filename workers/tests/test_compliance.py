import json
import re

import httpx
import pytest
from fastapi.testclient import TestClient

from common import config
from compliance import judge as J
from compliance import rules as R
from compliance import scanner, selftest
from compliance.__main__ import main as cli
from tests.conftest import AUTH

BLOCK, PASS = selftest.cases()


def test_spec_cases_parsed_from_safety_rules():
    assert len(BLOCK) == 10 and len(PASS) == 3
    assert all(ev for _, ev, _ in PASS), "pass cases carry their evidence IDs"


@pytest.mark.parametrize("text,ev,note", BLOCK, ids=[f"block{i + 1}" for i in range(len(BLOCK))])
def test_safety_rules_10_must_block(text, ev, note):
    r = scanner.scan(text=text, evidence=ev)
    assert r["verdict"] == "block", (text, r)
    assert r["blocks"]


@pytest.mark.parametrize("text,ev,note", PASS, ids=[f"pass{i + 1}" for i in range(len(PASS))])
def test_safety_rules_11_must_pass(text, ev, note):
    r = scanner.scan(text=text, evidence=ev)
    assert r["verdict"] == "pass", (text, r)


def test_selftest_runner_and_cli(capsys):
    assert selftest.run()["all_ok"]
    assert cli(["selftest"]) == 0
    assert "ALL OK" in capsys.readouterr().out


def test_rule_sources_load_and_compile():
    rules = R.all_rules()
    ids = {r.id for r in rules}
    assert {f"BC{i:02d}" for i in range(1, 23)} <= ids                 # blocked_claims.json
    assert len([i for i in ids if re.fullmatch(r"SR3\.1-\d\d", i)]) == 19   # SAFETY_RULES §3.1 lines
    for r in rules:
        assert isinstance(r.rx, re.Pattern)


def _myth_script(ost="MYTH ✗ DETOX TEA", evidence=("E24",), pillar="P15", spoken="Detox tea? No. Your liver already has a job."):
    return {"id": "T1", "pillar": pillar, "myth_bust": pillar == "P15", "evidence": list(evidence), "has_movement": False,
            "beats": [{"vo": spoken, "ost": ost}, {"vo": "Fiber has evidence. Go up slowly and drink water.", "ost": ""}]}


def test_myth_bust_exception_defers_to_llm():
    r = scanner.scan(_myth_script())
    assert r["verdict"] == "pass" and r["mbex_candidates"] and r["requires_llm_confirmation"]
    # regex alone can't pass it: without the judge it routes to a human
    assert scanner.combine_with_judge(r, None)["verdict"] == "human"
    assert scanner.combine_with_judge(r, {"status": "ok", "verdict": "pass", "confidence": 0.95})["verdict"] == "pass"


def test_myth_bust_needs_label_evidence_and_pillar():
    assert scanner.scan(_myth_script(ost="DETOX TEA? NO."))["verdict"] == "block"          # (c) no MYTH/✗ marker
    assert scanner.scan(_myth_script(evidence=()))["verdict"] == "block"                  # (d) no evidence
    assert scanner.scan(_myth_script(pillar="P10"))["verdict"] == "block"                 # (a) not a myth-bust


def test_myth_bust_never_covers_cure_or_medication():
    s = _myth_script(spoken="Onion water cures diabetes? No.", ost="MYTH ✗ ONION WATER")
    assert scanner.scan(s)["verdict"] == "block"
    s = _myth_script(spoken="Stop taking your pills? Never.", ost="MYTH ✗")
    r = scanner.scan(s)
    assert any(b["rule"] in ("BC04", "SR3.1-15") for b in r["blocks"]) or r["verdict"] in ("block", "revise")


@pytest.mark.parametrize("text", ["Never hold your breath. Breathe out as you stand.",
                                  "Sit-ups for a strong core? Not for older spines.",
                                  "It isn't an instant fix. Over weeks, on average.",
                                  "Can't decide alone? A real counselor helps. Not me. I'm AI.",
                                  "If you can't decide, a licensed counselor can help."])
def test_negation_and_referral_context_pass(text):
    assert scanner.scan(text=text)["blocks"] == []


@pytest.mark.parametrize("text,rule", [("I'm a real person, not a cartoon.", "D-04"),
                                       ("As a physical therapist, I see this every day.", "BC07"),
                                       ("Ancient wisdom from the monastery.", "D-07"),
                                       ("Comment STRONG to fix your knees.", "S-01"),
                                       ("Yang Mun gets this wrong.", "D-09"),
                                       ("Skip breakfast for 16 hours.", "F-FAST")])
def test_identity_commerce_food_blocks(text, rule):
    r = scanner.scan(text=text)
    assert r["verdict"] == "block" and rule in {b["rule"] for b in r["blocks"]}, r["blocks"]


def _move_script(**kw):
    s = {"id": "M1", "pillar": "P02", "has_movement": True, "movement_tags": ["sit_to_stand"], "evidence": ["E11"],
         "regression": "hands on thighs", "beats": [
             {"vo": "Chair against the wall. Sit and stand. Breathe out as you stand.", "ost": "Chair AGAINST the wall"},
             {"vo": "Comment STRONG for the chair builder.", "ost": "Comment STRONG"}]}
    s.update(kw)
    return s


def test_movement_complete_script_passes_and_auto_inserts_addon():
    r = scanner.scan(_move_script())
    assert r["verdict"] == "pass", r
    assert any("movement_addon" in a for a in r["auto_inserted"])


def test_movement_missing_support_regression_breath():
    s = _move_script(regression="", beats=[{"vo": "Sit and stand ten times. Go.", "ost": "10 stands"}])
    r = scanner.scan(s)
    miss = " ".join(r["required_missing"])
    assert r["verdict"] == "revise"
    assert "M-01" in miss and "M-02" in miss and "M-04" in miss


def test_contraindication_tags():
    r = scanner.scan(_move_script(movement_tags=["spinal_flexion_loaded"]))
    assert r["verdict"] == "block"
    r = scanner.scan(_move_script(movement_tags=["sit_to_stand", "floor_transfer"]))
    assert any("floor_transfer" in m for m in r["required_missing"])


def test_food_caution_and_red_flag_and_evidence_numbers():
    s = {"id": "F1", "pillar": "P11", "evidence": ["E32"], "movement_tags": ["honey"],
         "beats": [{"vo": "Honey in warm water for a cough.", "ost": ""}]}
    assert any("honey" in m for m in scanner.scan(s)["required_missing"])
    s = {"id": "R1", "pillar": "P14", "evidence": ["E47"], "beats": [{"vo": "Calf swelling and redness after a flight?", "ost": ""}]}
    assert any(m.startswith("§4.3") for m in scanner.scan(s)["required_missing"])
    s = {"id": "N1", "pillar": "P16", "evidence": ["E37"], "beats": [{"vo": "Over 300,000 people were studied.", "ost": ""}]}
    assert any(x["rule"] == "C-01" for x in scanner.scan(s)["rewrites"])
    s["beats"] = [{"vo": "148 studies, 308,849 people.", "ost": ""}]
    assert not any(x["rule"] == "C-01" for x in scanner.scan(s)["rewrites"])


def test_reviewer_gate():
    t = "Every video is reviewed by licensed professionals."
    assert "§7-reviewer" in {b["rule"] for b in scanner.scan(text=t)["blocks"]}
    assert "§7-reviewer" not in {b["rule"] for b in scanner.scan(text=t, reviewer_signed=True)["blocks"]}


def test_pass2_disclosure_checks():
    from common import disclosure
    good = {"instagram": {"caption": "Try the chair test.\n\n" + disclosure.movement_addon("en") + "\n\n" +
                          disclosure.footer("en", False)},
            "tiktok": {"caption": "x " + disclosure.footer("en", False), "is_aigc": True},
            "x": {"text": "Chair stands: a CDC screening test."}}
    r = scanner.scan(None, pass_no=2, packaging=good, has_movement=False, burned_in_text=["AI character"])
    assert r["verdict"] == "pass", r
    bad = {"instagram": {"caption": "no footer here"}, "tiktok": {"caption": "x", "is_aigc": False},
           "youtube": {"description": "d", "contains_synthetic_media": False},
           "x": {"text": "read https://example.com"}}
    r = scanner.scan(None, pass_no=2, packaging=bad, burned_in_text=["CHAIR TEST"])
    rules = {b["rule"] for b in r["blocks"]}
    assert r["verdict"] == "block" and "D-01/§5.2" in rules and "PIPELINE §2.2" in rules
    assert any(m.startswith("D-02") for m in r["required_missing"])
    assert any(m.startswith("D-03") for m in r["required_missing"])


def test_judge_skipped_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    j = J.judge({"id": "x"}, [])
    assert j["status"] == "skipped" and "ANTHROPIC_API_KEY" in j["reason"]


def test_judge_request_and_parse_with_mock_transport():
    seen = {}

    def handler(req: httpx.Request):
        seen["body"] = json.loads(req.content)
        seen["headers"] = req.headers
        out = {"verdict": "pass", "confidence": 0.93, "risk_tier": "green", "checks": []}
        return httpx.Response(200, json={"content": [{"type": "text", "text": "```json\n" + json.dumps(out) + "\n```"}]})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    j = J.judge({"id": "S1", "lines": []}, [{"id": "BC05"}], client=client, api_key="test-key", market="US")
    assert j["status"] == "ok" and j["verdict"] == "pass"
    b = seen["body"]
    assert b["temperature"] == 0 and b["model"].startswith("claude-")
    assert "compliance and safety judge" in b["system"][0]["text"] and b["system"][0]["cache_control"]
    assert "BC05" in b["messages"][0]["content"] and seen["headers"]["x-api-key"] == "test-key"


def test_judge_http_error_routes_human():
    client = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(529, text="overloaded")))
    j = J.judge({"id": "S1"}, [], client=client, api_key="k")
    assert j["status"] == "error" and j["verdict"] == "human"


def test_combine_rules():
    blocked = scanner.scan(text="Detox your liver.")
    assert scanner.combine_with_judge(blocked, {"status": "ok", "verdict": "pass", "confidence": 1})["verdict"] == "block"
    clean = scanner.scan(text="Walk after dinner.")
    assert scanner.combine_with_judge(clean, {"status": "ok", "verdict": "pass", "confidence": 0.5})["verdict"] == "human"


def test_data_content_scripts_scan(data_scripts):
    """Every script in data/content/scripts.json scans cleanly (no crash) and most pass deterministically.
    (The file is regenerated by the content build; assertions on specific IDs only apply while those scripts exist.)"""
    by_id = {s["id"]: s for s in data_scripts}
    res = {sid: scanner.combine_with_judge(scanner.scan(s), None)["verdict"] for sid, s in by_id.items()}
    assert len(res) >= 60
    assert set(res.values()) <= {"pass", "revise", "human", "block"}
    assert sum(v == "pass" for v in res.values()) / len(res) >= 0.5
    known = {"S34": ("Detox tea", "block"), "S47": ("instantly", "pass"), "S13": ("sit-ups", "pass"),
             "S46": ("forgive", "pass")}
    for sid, (title_part, want) in known.items():
        if sid in by_id and title_part.lower() in by_id[sid].get("title", "").lower():
            assert res[sid] == want, (sid, res[sid])


def test_api_scan_and_selftest(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from app import app
    c = TestClient(app, headers=AUTH)
    r = c.post("/compliance/scan", json={"text": "Hold your breath and push!"})
    assert r.status_code == 200 and r.json()["verdict"] == "block" and r.json()["final"]["verdict"] == "block"
    r = c.post("/compliance/scan", json={"script": _move_script(), "pass": 1, "judge": True})
    assert r.json()["judge"]["status"] in ("skipped", "ok", "error")
    assert c.get("/compliance/selftest").json()["all_ok"]


# --- BLITZ canon CX-GUAR: "guarantee" allowed only as the refund-policy phrase --------------------------------------
GUAR_ALLOWED = [
    "Founding membership: first month charged today. 14-day money-back guarantee. Cancel online anytime.",
    "There's a money-back guarantee on your first membership charge.",
    "It comes with a 14-day money back guarantee: tap Refund in your account within 14 days.",
    "The 14-Day Money-Back Guarantee.",
]
GUAR_BLOCKED = [
    "Guaranteed results in two weeks.",
    "I guarantee you'll sleep through the night.",
    "We guarantee it works.",
    "Stronger legs, guaranteed.",
    "Our money-back guarantee you'll sleep better.",
    "A money-back guarantee that your knees stop aching.",
    "Stronger legs in 14 days, or use the 14-day money-back guarantee.",
    "14-day money-back guarantee if you don't feel better.",
]


@pytest.mark.parametrize("text", GUAR_ALLOWED)
def test_refund_guarantee_phrase_allowed(text):
    r = scanner.scan(text=text)
    assert r["verdict"] == "pass", r["regex_hits"]
    assert not any(h["id"] in ("BC14", "BC23", "SR3.1-12") for h in r["regex_hits"])


@pytest.mark.parametrize("text", GUAR_BLOCKED)
def test_guarantee_in_health_outcome_context_blocked(text):
    r = scanner.scan(text=text)
    assert r["verdict"] == "block", r
    assert {h["id"] for h in r["regex_hits"]} & {"BC14", "BC23", "SR3.1-12"}


def test_outcome_guarantee_never_myth_bust_exempt():
    s = _myth_script(spoken="Money-back guarantee you'll sleep better? No.", ost="MYTH ✗ GUARANTEED SLEEP")
    r = scanner.scan(s)
    assert any(b["rule"] == "BC23" for b in r["blocks"]), r


def test_blocked_claims_json_regexes_carry_the_whitelist():
    """The raw JSON regexes (n8n Regex Pre-Scan, tools/build_content.py) apply the same exception on their own."""
    pats = {p["id"]: re.compile(p["regex"], re.I) for p in R.blocked_claims_doc()["patterns"]}
    bc14 = next(p for p in R.blocked_claims_doc()["patterns"] if p["id"] == "BC14")
    assert bc14["allowed_phrases"] == ["14-day money-back guarantee", "money-back guarantee"]
    for t in GUAR_ALLOWED:
        assert not pats["BC14"].search(t) and not pats["BC23"].search(t), t
    for t in GUAR_BLOCKED:
        assert pats["BC14"].search(t) or pats["BC23"].search(t), t


def test_safety_rules_31_line_carries_the_whitelist():
    rule = next(r for r in R.all_rules() if r.id == "SR3.1-12")
    assert "money.back" in rule.pattern and not rule.mbex
    for t in GUAR_ALLOWED:
        assert not rule.rx.search(t), t
    for t in GUAR_BLOCKED:
        assert rule.rx.search(t), t
    # the embedded fallback copy stays verbatim with SAFETY_RULES.md
    assert R.parse_safety_31(None) == R.parse_safety_31(R._safety_rules_text())


def test_build_content_banned_list_whitelists_refund_phrase():
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_content", config.SPEC_DIR / "tools" / "build_content.py")
    bc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bc)
    assert bc.GUARANTEE_RX in bc.BANNED
    for t in GUAR_ALLOWED:
        assert not re.search(bc.GUARANTEE_RX, t.lower()), t
        assert not bc.blocked_claims_scan("T", {"x": t}), t
    for t in GUAR_BLOCKED:
        assert re.search(bc.GUARANTEE_RX, t.lower()) or bc.blocked_claims_scan("T", {"x": t}), t


# --- Paid ads (data/content/ad_scripts.json) are scanned field by field -------------------------------------------
def _ad(**kw):
    a = {"id": "A99", "hook_variants_first_2s": ["Thirty seconds. One chair."],
         "body": [{"t": "2-8", "vo_or_action": "Chang: 'Arms crossed. Stand all the way up.'", "on_screen_text": "Chair test"}],
         "primary_text": "Chang Yin (an AI character) does the chair test.\nFounding membership: {{FOUNDING_PRICE}}/month, "
                         "first month charged today, renews monthly until you cancel. Cancel online anytime. "
                         "14-day money-back guarantee.",
         "headline": "30 seconds. One chair.", "end_card": "Founding membership · 14-day money-back guarantee",
         "compliance_note": "internal: never 'guaranteed results'"}
    a.update(kw)
    return a


def test_ad_fields_are_scanned():
    r = scanner.scan(_ad())
    assert r["verdict"] == "pass", r
    assert scanner.scan(_ad(headline="Guaranteed stronger legs"))["verdict"] == "block"
    assert scanner.scan(_ad(primary_text="Detox your joints."))["verdict"] == "block"
    bad = _ad(body=[{"t": "2-8", "vo_or_action": "Hold your breath and push!", "on_screen_text": ""}])
    assert scanner.scan(bad)["verdict"] == "block"


def test_full_library_passes(data_scripts):
    ads = json.loads((config.SPEC_DIR / "data" / "content" / "ad_scripts.json").read_text())
    res = {s["id"]: scanner.combine_with_judge(scanner.scan(s), None)["verdict"] for s in data_scripts + ads}
    assert len(res) == len(data_scripts) + len(ads)
    assert {k: v for k, v in res.items() if v != "pass"} == {}


def test_cli_scan_multiple_files(tmp_path, capsys):
    out = tmp_path / "report.json"
    spec = config.SPEC_DIR / "data" / "content"
    assert cli(["scan", str(spec / "scripts.json"), str(spec / "ad_scripts.json"), "--json", str(out), "--strict"]) == 0
    rep = json.loads(out.read_text())
    assert rep["total"] == len(rep["results"]) and len(rep["files"]) == 2
