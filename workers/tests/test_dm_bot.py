"""DM bot (workers/dm): flows, disclosure, window, STOP/consent, dedup, attribution via /b, crisis → exceptions + 988,
replies only to inbound, signature verification, Meta webhook fixtures."""
from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app import app
from dm.bot import Bot, Store, load_flows, parse_webhook, verify_signature

T0 = datetime(2026, 10, 12, 15, 0, tzinfo=timezone.utc)
SECRET = "test-app-secret"


def ig_comment(cid: str, sender: str, text: str, media: str = "M1", page: str = "IGPAGE") -> dict:
    return {"object": "instagram", "entry": [{"id": page, "time": 1, "changes": [
        {"field": "comments", "value": {"id": cid, "text": text, "from": {"id": sender, "username": "ruth"}, "media": {"id": media}}}]}]}


def ig_dm(mid: str, sender: str, text: str = "", payload: str | None = None, page: str = "IGPAGE", postback: bool = False) -> dict:
    m: dict = {"sender": {"id": sender}, "recipient": {"id": page}, "timestamp": 1}
    if postback:
        m["postback"] = {"mid": mid, "payload": payload, "title": text}
    else:
        m["message"] = {"mid": mid, "text": text, **({"quick_reply": {"payload": payload}} if payload else {})}
    return {"object": "instagram", "entry": [{"id": page, "time": 1, "messaging": [m]}]}


@pytest.fixture()
def bot():
    calls = []
    b = Bot(Store(":memory:"), domain="https://strongyears.com", mode="runway",
            exceptions=lambda *a, **k: calls.append((a, k)) or {"status": "created"})
    b.calls = calls
    return b


def run(b: Bot, payload: dict, now=T0) -> list[dict]:
    out = []
    for ev in parse_webhook(payload):
        out += b.handle(ev, now)
    return out


def test_flows_cover_the_funnel_keywords_and_every_dm1_discloses():
    flows, g = load_flows()
    kws = {f["keyword"] for f in flows.values()}
    assert {"STRONG", "BACK", "SLEEP", "SOUP", "BALANCE", "KNEES", "BREATH", "BEGIN", "GUT", "TEST", "FAMILY",
            "JOIN", "WAITLIST", "BOOK"} == kws
    for f in flows.values():
        first = f["states"][f["start"]]["dm"][0]
        assert "(automated)" in first and "AI character" in first, f["flow_id"]
        for sid, st in f["states"].items():
            for b in st.get("buttons", []) + st.get("quick_replies", []):
                assert "link" in b or b["next"] in f["states"], (f["flow_id"], sid)
    assert "988" in g["crisis"]["self_harm"]["safety_dm"][0] and "911" in g["crisis"]["self_harm"]["safety_dm"][0]
    assert "7am to 11pm Eastern" in g["crisis"]["self_harm"]["safety_dm"][0]


def test_comment_keyword_public_reply_and_private_dm_with_disclosure_and_attribution(bot):
    acts = run(bot, ig_comment("c1", "U1", "STRONG please!", media="REEL9"))
    assert [a["type"] for a in acts] == ["public_reply", "dm"]
    assert "http" not in acts[0]["text"]                        # never a link in public
    dm1 = acts[1]
    assert dm1["private_reply_to_comment"] == "c1" and dm1["in_reply_to"] == "c:c1"
    assert dm1["text"].startswith("Hi there! This is Chang Yin's team assistant (automated)")
    tap = run(bot, ig_dm("m2", "U1", "Yes, send it", payload="strong:dm2", postback=True))
    assert "https://strongyears.com/s/l1?mc_id=U1&utm_source=ig&utm_medium=dm&utm_campaign=strong" in tap[0]["text"]
    ck = bot._state_actions(bot.flows["strong"], "ck1", {"platform": "ig", "sender": "U1", "page": "IGPAGE", "id": "x", "post_id": "REEL9"},
                            bot.store.contact("ig:U1"), T0)
    url = ck[0]["buttons"][0]["url"]
    assert url.startswith("https://strongyears.com/b?t=STRONG&p=IGPAGE&pid=REEL9&mc_id=U1")
    assert ck[0]["buttons"][0]["title"] == "Get first access (free)"      # runway label


def test_dedup_event_and_same_flow_within_24h(bot):
    assert len(run(bot, ig_comment("c1", "U1", "strong"))) == 2
    assert run(bot, ig_comment("c1", "U1", "strong")) == []                 # same event id
    again = run(bot, ig_comment("c2", "U1", "STRONG"), now=T0 + timedelta(hours=2))
    assert [a["type"] for a in again] == ["public_reply"]                   # public reply only
    other = run(bot, ig_comment("c3", "U1", "soup"), now=T0 + timedelta(hours=3))
    assert [a["type"] for a in other] == ["public_reply", "dm"]             # a different flow still goes
    assert run(bot, ig_comment("c4", "U1", "strong"), now=T0 + timedelta(hours=25))[1]["type"] == "dm"


def test_stop_consent_log_and_silence_then_start(bot):
    run(bot, ig_comment("c1", "U2", "BACK"))
    stop = run(bot, ig_dm("m1", "U2", "STOP"))
    assert len(stop) == 1 and "won't get more automated messages" in stop[0]["text"]
    assert run(bot, ig_comment("c2", "U2", "SLEEP"), now=T0 + timedelta(hours=30)) == []
    assert run(bot, ig_dm("m2", "U2", "stop")) == []                        # one confirmation only
    assert run(bot, ig_dm("m3", "U2", "START"))[0]["text"].startswith("You're back on")
    assert [r["kind"] for r in bot.store.consent_rows("ig:U2")] == ["opt_out", "opt_out", "opt_in"]
    assert bot.due_followups(T0 + timedelta(minutes=30)) == []              # STOP dropped the pending nudge for good


def test_crisis_pauses_automation_posts_exception_and_sends_988(bot):
    acts = run(bot, ig_dm("m1", "U3", "some days I just want to die"))
    assert "988" in acts[0]["text"] and acts[0]["safety"] is True
    assert acts[-1]["type"] == "crisis_alert"
    (args, kw), = bot.calls
    assert args[0] == "crisis_escalation" and kw["severity"] == "critical"
    assert "die" not in json.dumps(kw)                                     # no message text leaves the bot
    assert run(bot, ig_comment("c9", "U3", "STRONG"), now=T0 + timedelta(hours=1)) == []   # paused


def test_first_reply_without_flow_gets_the_disclosure_and_runway_price_has_no_price(bot):
    acts = run(bot, ig_dm("m1", "U4", "how much does it cost?"))
    assert "AI characters" in acts[0]["text"] and "$" not in acts[0]["text"]
    assert "/b?t=PRICE" in acts[0]["text"]


def test_mode_routing_book_in_runway_is_the_waitlist_and_waitlist_at_launch_is_book():
    b = Bot(Store(":memory:"), mode="runway", exceptions=lambda *a, **k: {})
    assert b.match_keyword("BOOK please")["flow_id"] == "waitlist"
    b2 = Bot(Store(":memory:"), mode="launch", exceptions=lambda *a, **k: {})
    assert b2.match_keyword("waitlist")["flow_id"] == "book"
    assert b2.match_keyword("JOIN")["flow_id"] == "join"


def test_email_capture_logs_consent_and_queues_lead(bot):
    run(bot, ig_comment("c1", "U5", "STRONG"))
    run(bot, ig_dm("m1", "U5", "Yes, send it", payload="strong:dm2", postback=True))
    run(bot, ig_dm("m2", "U5", "Yes, email it", payload="strong:email_ask"))
    acts = run(bot, ig_dm("m3", "U5", "ruth@example.com"))
    assert acts[-1]["type"] == "lead" and acts[-1]["source"] == "dm_strong"
    assert [r["kind"] for r in bot.store.consent_rows("ig:U5")] == ["email_opt_in"]


def test_followups_only_inside_the_window_and_every_action_answers_an_inbound(bot):
    run(bot, ig_comment("c1", "U6", "TEST"))
    nudge = bot.due_followups(T0 + timedelta(minutes=21))
    assert [a["followup"] for a in nudge] == ["nudge"]
    check = bot.due_followups(T0 + timedelta(minutes=1321))
    assert [a["followup"] for a in check] == ["checkin"]
    run(bot, ig_comment("c2", "U7", "SOUP"))
    assert bot.due_followups(T0 + timedelta(hours=30)) == []                # window closed: nothing
    for a in bot.store.outbox():
        assert a.get("in_reply_to"), a
        assert "tag" not in a and a.get("messaging_type", "RESPONSE") == "RESPONSE"


def test_signature_and_webhook_endpoint(monkeypatch):
    body = json.dumps(ig_comment("cX", "U8", "BREATH")).encode()
    sig = "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    assert verify_signature(SECRET, body, sig) and not verify_signature(SECRET, body + b" ", sig)
    assert not verify_signature("", body, sig)
    import dm.api as api
    monkeypatch.setattr(api, "_bot", Bot(Store(":memory:"), exceptions=lambda *a, **k: {}))
    c = TestClient(app)
    assert c.post("/dm/webhook", content=body, headers={"X-Hub-Signature-256": sig}).status_code == 503   # no secret: closed
    monkeypatch.setenv("META_APP_SECRET", SECRET)
    assert c.post("/dm/webhook", content=body, headers={"X-Hub-Signature-256": "sha256=00"}).status_code == 401
    r = c.post("/dm/webhook", content=body, headers={"X-Hub-Signature-256": sig})
    assert r.status_code == 200 and r.json()["actions"] == 2
    monkeypatch.setenv("DM_VERIFY_TOKEN", "vt")
    assert c.get("/dm/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "vt", "hub.challenge": "42"}).text == "42"
    assert c.get("/dm/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "no", "hub.challenge": "42"}).status_code == 403


def test_messenger_feed_comment_fixture_parses():
    payload = {"object": "page", "entry": [{"id": "PAGE1", "changes": [{"field": "feed", "value": {
        "item": "comment", "verb": "add", "comment_id": "P_1", "post_id": "PAGE1_77", "message": "SOUP", "from": {"id": "F1", "name": "Ann"}}}]}]}
    evs = parse_webhook(payload)
    assert evs[0]["platform"] == "fb" and evs[0]["post_id"] == "PAGE1_77" and evs[0]["kind"] == "comment"
    assert parse_webhook({"object": "page", "entry": [{"id": "PAGE1", "messaging": [{"sender": {"id": "PAGE1"}, "message": {"mid": "e", "is_echo": True}}]}]}) == []
