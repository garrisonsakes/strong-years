"""Offer routing (MONETIZATION_ENGINE.md §2): the data table, the shared vectors (same file the app test runs), the
DM qualify → route path, the hardship/group intents, and /dm/stats counting."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from dm import routing
from dm.api import conversation_stats
from dm.bot import Bot, Store, parse_webhook

HERE = Path(__file__).resolve().parent
VECTORS = json.loads((HERE / "fixtures" / "offer_routing_vectors.json").read_text())
T0 = datetime(2026, 10, 12, 15, 0, tzinfo=timezone.utc)


def test_table_is_consistent_and_the_app_copy_is_identical():
    t = routing.table()
    assert all(r["offer"] in t["offers"] for r in t["rules"])
    assert t["rules"][-1]["when"] == {}, "the last rule is the default"
    # Rules pick a family, never a price.
    assert not any(k in r for r in t["rules"] for k in ("price", "price_cents", "cell"))
    app_copy = HERE.parent.parent / "app" / "src" / "lib" / "offers" / "routing.json"
    assert app_copy.read_bytes() == routing.ROUTING_PATH.read_bytes()
    book = json.loads((HERE.parent / "dm" / "flows" / "book.json").read_text())
    pick = book["states"]["pick"]
    assert all(s in book["states"] for s in pick["routes"].values())


def test_shared_vectors():
    for v in VECTORS["routes"]:
        r = routing.route(v["ctx"])
        assert (r["offer"], r["rule"]) == (v["offer"], v["rule"]), v
        assert r.get("variant") == v.get("variant")
        assert (r.get("bump") or {}).get("frame") == v.get("bump_frame")
    for a in VECTORS["assign"]:
        assert routing.assign(a["exp"], a["subject"]) == a["arm"], a


def test_bumps_thank_you_and_winback_match_intent():
    assert routing.bump_for("knees")["frame"] == "wall_plan"
    assert routing.bump_for("kitchen")["frame"] == "grocery_lists"
    assert routing.thank_you_offer("e12", "knees") == "founding_monthly"
    assert routing.thank_you_offer("m12", "knees") == "kit"
    assert routing.thank_you_offer("m12", "kitchen") == "gift"
    assert [routing.winback(d)["offer"] for d in (5, 60, 400)] == ["rejoin", "winback_12", "winback_9"]


def _tap(b: Bot, sender: str, payload: str, mid: str) -> list[dict]:
    m = {"sender": {"id": sender}, "recipient": {"id": "IGPAGE"}, "timestamp": 1,
         "message": {"mid": mid, "text": "x", "quick_reply": {"payload": payload}}}
    out = []
    for ev in parse_webhook({"object": "instagram", "entry": [{"id": "IGPAGE", "time": 1, "messaging": [m]}]}):
        out += b.handle(ev, T0)
    return out


def _bot() -> Bot:
    return Bot(Store(":memory:"), domain="https://strongyears.com", mode="launch", exceptions=lambda *a, **k: {"status": "created"})


def test_two_questions_then_route_gift_group_and_answers_ride_to_b():
    b = _bot()
    q1 = _tap(b, "u1", "book:q_goal", "m1")
    assert "What matters most" in q1[0]["text"] and len(q1[0]["quick_replies"]) == 5
    q2 = _tap(b, "u1", "book:q_who|goal=knees", "m2")
    assert "who is it for" in q2[0]["text"]
    gift = _tap(b, "u1", "book:pick|audience=parent", "m3")
    assert "/b?t=FAMILY" in gift[0]["text"] and "&g=knees&a=parent" in gift[0]["text"]
    c = b.store.contact("ig:u1")
    assert c["answers"] == {"goal": "knees", "audience": "parent"} and c["last_route"]["offer"] == "gift"
    # A value outside the allow-list is ignored; self → the front end with the matched bump recorded.
    _tap(b, "u2", "book:q_who|goal=<script>", "m4")
    me = _tap(b, "u2", "book:pick|audience=self", "m5")
    assert "/b?t=BOOK" in me[0]["text"] and b.store.contact("ig:u2")["answers"] == {"audience": "self"}
    grp = _tap(b, "u3", "book:pick|audience=group", "m6")
    assert "/ask/group" in grp[0]["text"]


def test_hardship_message_goes_to_a_person_path_and_is_honest():
    b = _bot()
    acts = []
    m = {"sender": {"id": "u9"}, "recipient": {"id": "IGPAGE"}, "timestamp": 1, "message": {"mid": "h1", "text": "I can't afford that on my pension"}}
    for ev in parse_webhook({"object": "instagram", "entry": [{"id": "IGPAGE", "time": 1, "messaging": [m]}]}):
        acts += b.handle(ev, T0)
    assert "/ask/price" in acts[0]["text"] and "person" in acts[0]["text"]
    assert "AI characters" in acts[0]["text"]  # first reply carries the disclosure
    assert "hardship" in b.store.contact("ig:u9")["tags"]


def test_stats_count_conversations_and_arms():
    contacts = [
        {"flows_sent": {"book": T0.isoformat()}, "answers": {"goal": "knees"}, "last_route": {"offer": "front_end"}, "exposures": {"dm_qualify": "qualify2"}},
        {"flows_sent": {"book": "2026-09-01T00:00:00+00:00"}},
        {"flows_sent": {}},
    ]
    s = conversation_stats(contacts, T0, 7)
    assert s["conversations"] == 1 and s["qualified"] == 1 and s["routed"] == {"front_end": 1} and s["arms"] == {"dm_qualify": {"qualify2": 1}}
