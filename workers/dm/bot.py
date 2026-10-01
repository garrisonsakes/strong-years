"""In-house Instagram / Messenger keyword → DM bot (replaces ManyChat; FUNNEL.md §4).

Flows are JSON state machines in dm/flows/ (one file per keyword, plus _global.json for intents and the crisis
protocol). The bot is a pure function of (inbound event, stored contact state, now): it returns actions and writes
them to an outbox; it never calls Meta itself (dm/sender.py delivers, and only with DM_SEND_ENABLED=1).

Rules enforced here (tests/test_dm_bot.py):
  - replies only to inbound: every action answers an inbound event, or is a flow follow-up inside the 24-hour window
    that the person's own last message opened; nothing is ever sent to someone who hasn't written or commented;
  - the first message any contact receives carries the AI disclosure (flows have it in DM 1; any other first reply
    gets the disclosure line prepended);
  - STOP / unsubscribe → opt-out recorded in the consent log, one confirmation, then silence; START re-opts in;
  - crisis language → automation paused, the 988 / 911 line (FUNNEL §4.14), an exceptions-queue item for a person;
  - de-duplication: an event is handled once; the same flow within 24 hours → public reply only, no second DM;
  - automation never uses message tags (HUMAN_AGENT is for a person's own replies only);
  - every offer link goes through /b (attribution: keyword, page, post id, mc_id, UTMs); lesson links carry the same.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

FLOWS_DIR = Path(__file__).resolve().parent / "flows"
EMAIL_RX = re.compile(r"^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,24}$")


# ------------------------------------------------------------------ flows
def load_flows(path: Path = FLOWS_DIR) -> tuple[dict[str, dict], dict]:
    flows = {}
    for p in sorted(path.glob("*.json")):
        if p.name.startswith("_"):
            continue
        f = json.loads(p.read_text(encoding="utf-8"))
        flows[f["flow_id"]] = f
    glob = json.loads((path / "_global.json").read_text(encoding="utf-8"))
    return flows, glob


def norm(text: str) -> str:
    t = (text or "").lower().strip()
    return re.sub(r"\s+", " ", t)


def _word_match(needle: str, hay: str) -> bool:
    if not re.search(r"\w", needle):          # emoji variants: plain containment
        return needle in hay
    return re.search(r"(?<!\w)" + re.escape(needle) + r"(?!\w)", hay) is not None


# ------------------------------------------------------------------ signature
def verify_signature(app_secret: str, body: bytes, header: str | None) -> bool:
    """X-Hub-Signature-256: sha256=<hex HMAC-SHA256(app secret, raw body)>. Fails closed."""
    if not app_secret or not header or not header.startswith("sha256="):
        return False
    mac = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, header[7:])


# ------------------------------------------------------------------ parsing
def parse_webhook(payload: dict) -> list[dict]:
    """Instagram (object=instagram) and Messenger (object=page) webhooks → normalized inbound events."""
    obj = payload.get("object")
    platform = "ig" if obj == "instagram" else "fb" if obj == "page" else None
    if not platform:
        return []
    out = []
    for entry in payload.get("entry") or []:
        page = str(entry.get("id") or "")
        for m in entry.get("messaging") or []:
            sender = str((m.get("sender") or {}).get("id") or "")
            if not sender or sender == page:
                continue
            ts = m.get("timestamp")
            msg = m.get("message") or {}
            if msg.get("is_echo"):
                continue
            base = {"platform": platform, "page": page, "sender": sender, "ts": ts}
            if m.get("postback"):
                pb = m["postback"]
                out.append({**base, "kind": "postback", "id": f"pb:{pb.get('mid') or sender}:{ts}",
                            "payload": str(pb.get("payload") or ""), "text": str(pb.get("title") or "")})
            elif msg:
                qr = (msg.get("quick_reply") or {}).get("payload")
                out.append({**base, "kind": "quick_reply" if qr else "message", "id": f"m:{msg.get('mid')}",
                            "payload": str(qr or ""), "text": str(msg.get("text") or "")[:2000]})
        for ch in entry.get("changes") or []:
            v = ch.get("value") or {}
            if ch.get("field") == "comments":  # Instagram
                frm = str((v.get("from") or {}).get("id") or "")
                if frm and frm != page:
                    out.append({"platform": platform, "page": page, "sender": frm, "ts": None, "kind": "comment",
                                "id": f"c:{v.get('id')}", "comment_id": str(v.get("id") or ""),
                                "post_id": str((v.get("media") or {}).get("id") or ""), "text": str(v.get("text") or "")[:2000]})
            elif ch.get("field") == "feed" and v.get("item") == "comment" and v.get("verb") == "add":  # Facebook
                frm = str((v.get("from") or {}).get("id") or "")
                if frm and frm != page:
                    out.append({"platform": platform, "page": page, "sender": frm, "ts": None, "kind": "comment",
                                "id": f"c:{v.get('comment_id')}", "comment_id": str(v.get("comment_id") or ""),
                                "post_id": str(v.get("post_id") or ""), "text": str(v.get("message") or "")[:2000]})
    return out


# ------------------------------------------------------------------ store (sqlite; ":memory:" in tests)
class Store:
    def __init__(self, path: str | None = None):
        p = path or os.environ.get("DM_DB_PATH") or str(Path(os.environ.get("OUTPUT_DIR", "out")) / "dm" / "dm.sqlite3")
        if p != ":memory:":
            Path(p).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(p, check_same_thread=False)
        self.db.executescript("""
          create table if not exists events (id text primary key, at text not null);
          create table if not exists contacts (key text primary key, data text not null);
          create table if not exists consent_log (id integer primary key autoincrement, key text not null,
                 kind text not null, detail text, at text not null);
          create table if not exists outbox (id integer primary key autoincrement, at text not null,
                 action text not null, status text not null default 'queued');
        """)

    def seen(self, event_id: str, now: datetime) -> bool:
        try:
            self.db.execute("insert into events(id, at) values (?, ?)", (event_id, now.isoformat()))
            self.db.commit()
            return False
        except sqlite3.IntegrityError:
            return True

    def contact(self, key: str) -> dict:
        row = self.db.execute("select data from contacts where key = ?", (key,)).fetchone()
        return json.loads(row[0]) if row else {"key": key, "tags": [], "flows_sent": {}, "kw_count": 0}

    def save(self, c: dict) -> None:
        self.db.execute("insert into contacts(key, data) values (?, ?) on conflict(key) do update set data = excluded.data",
                        (c["key"], json.dumps(c, sort_keys=True)))
        self.db.commit()

    def contacts(self) -> list[dict]:
        return [json.loads(r[0]) for r in self.db.execute("select data from contacts")]

    def consent(self, key: str, kind: str, detail: str, now: datetime) -> None:
        self.db.execute("insert into consent_log(key, kind, detail, at) values (?, ?, ?, ?)", (key, kind, detail, now.isoformat()))
        self.db.commit()

    def consent_rows(self, key: str | None = None) -> list[dict]:
        q = "select key, kind, detail, at from consent_log" + (" where key = ?" if key else "") + " order by id"
        return [dict(zip(("key", "kind", "detail", "at"), r)) for r in self.db.execute(q, (key,) if key else ())]

    def enqueue(self, action: dict, now: datetime) -> None:
        self.db.execute("insert into outbox(at, action) values (?, ?)", (now.isoformat(), json.dumps(action, sort_keys=True)))
        self.db.commit()

    def outbox(self) -> list[dict]:
        return [json.loads(r[0]) for r in self.db.execute("select action from outbox order by id")]


# ------------------------------------------------------------------ the bot
class Bot:
    def __init__(self, store: Store, *, domain: str | None = None, mode: str | None = None, flows_dir: Path = FLOWS_DIR,
                 exceptions=None):
        self.store = store
        self.flows, self.g = load_flows(flows_dir)
        self.domain = (domain or os.environ.get("SITE_BASE_URL") or "https://strongyears.com").rstrip("/")
        m = (mode or os.environ.get("DM_MODE") or ("launch" if os.environ.get("LAUNCH_MODE") == "live" else "runway")).lower()
        self.mode = "launch" if m in ("launch", "live") else "runway"
        if exceptions is None:
            from common import exceptions as exc_client
            exceptions = exc_client.post_exception
        self.post_exception = exceptions

    # -------- helpers
    def _active(self, f: dict) -> bool:
        return f.get("mode", "always") in ("always", self.mode)

    def match_keyword(self, text: str) -> dict | None:
        t = norm(text)
        if not t:
            return None
        hits = []
        for f in self.flows.values():
            for v in [f["keyword"].lower(), *f.get("variants", [])]:
                if _word_match(norm(v), t):
                    hits.append((len(v), f))
                    break
        if not hits:
            return None
        f = max(hits, key=lambda h: h[0])[1]
        # Mode routing: in the runway BOOK/JOIN become the waitlist; at launch WAITLIST becomes BOOK (FUNNEL §4.18/4.19).
        if not self._active(f):
            f = self.flows["waitlist"] if self.mode == "runway" else self.flows["book"]
        return f

    def _crisis(self, text: str) -> tuple[str, dict] | None:
        t = norm(text)
        for cat in ("self_harm", "medical", "abuse", "grief"):
            c = self.g["crisis"][cat]
            if any(_word_match(norm(m), t) for m in c["match"]):
                return cat, c
        return None

    def _intent(self, text: str) -> dict | None:
        t = norm(text).strip(" .!?")
        for it in self.g["intents"]:
            for m in it["match"]:
                if (it.get("exact") and t == m) or (not it.get("exact") and _word_match(m, t)):
                    return it
        return None

    def links(self, text: str, ev: dict, kw: str) -> str:
        q = {"mc_id": ev["sender"], "utm_source": ev["platform"], "utm_medium": "dm", "utm_campaign": kw.lower()}
        qs = "&".join(f"{k}={v}" for k, v in q.items())
        page = ev.get("page_handle") or ev.get("page") or ""
        b = f"{self.domain}/b?t={kw.upper()}&p={page}" + (f"&pid={ev['post_id']}" if ev.get("post_id") else "") + f"&{qs}"
        text = text.replace("{{B_LINK}}", b)
        return re.sub(r"\{\{L:(/[A-Za-z0-9/_-]*)\}\}", lambda m: f"{self.domain}{m.group(1)}?{qs}", text)

    def _render(self, text: str, ev: dict, c: dict, kw: str) -> str:
        text = self.links(text, ev, kw)
        return text.replace("{first_name}", c.get("first_name") or "there").replace("{email}", c.get("email") or "your inbox")

    def _disclose(self, c: dict, text: str, now: datetime) -> str:
        if c.get("disclosed_at"):
            return text
        c["disclosed_at"] = now.isoformat()
        if any(mk in text for mk in self.g["ai_disclosure_markers"]):
            return text
        return f"{self.g['sender_label']}: Chang Yin and Sun Yoon are AI characters, not real people.\n\n{text}"

    def _dm(self, ev: dict, c: dict, texts: list[str], now: datetime, kw: str, *, buttons=None, quick=None,
            flow: str | None = None, reply_to: str | None = None, safety: bool = False) -> list[dict]:
        out = []
        for i, t in enumerate(texts):
            body = self._disclose(c, self._render(t, ev, c, kw), now)
            a = {"type": "dm", "platform": ev["platform"], "page": ev["page"], "to": ev["sender"], "text": body,
                 "messaging_type": "RESPONSE", "in_reply_to": reply_to or ev["id"], "flow": flow, "safety": safety}
            if ev.get("kind") == "comment" and ev.get("comment_id"):
                a["private_reply_to_comment"] = ev["comment_id"]
            if i == len(texts) - 1:
                if buttons:
                    a["buttons"] = buttons
                if quick:
                    a["quick_replies"] = quick
            out.append(a)
        return out

    def _buttons(self, flow: dict, state: dict, ev: dict, c: dict) -> tuple[list, list]:
        btns, qrs = [], []
        for b in state.get("buttons") or []:
            if "link" in b:
                btns.append({"title": b["label_runway" if self.mode == "runway" else "label_launch"],
                             "url": self._render(b["link"], ev, c, flow["keyword"])})
            else:
                btns.append({"title": b["label"], "payload": f"{flow['flow_id']}:{b['next']}"})
        for q in state.get("quick_replies") or []:
            qrs.append({"title": q["label"], "payload": f"{flow['flow_id']}:{q['next']}"})
        return btns, qrs

    def _state_actions(self, flow: dict, sid: str, ev: dict, c: dict, now: datetime, reply_to: str | None = None) -> list[dict]:
        st = flow["states"][sid]
        c["flow_state"] = {"flow": flow["flow_id"], "state": sid}
        for t in st.get("tags") or []:
            if t not in c["tags"]:
                c["tags"].append(t)
        if st.get("handoff"):
            c["handoff_until"] = (now + timedelta(days=self.g["human_agent_tag_days"])).isoformat()
        btns, qrs = self._buttons(flow, st, ev, c)
        return self._dm(ev, c, st["dm"], now, flow["keyword"], buttons=btns or None, quick=qrs or None,
                        flow=flow["flow_id"], reply_to=reply_to)

    def _paused(self, c: dict, now: datetime) -> bool:
        for k in ("paused_until", "handoff_until"):
            if c.get(k) and datetime.fromisoformat(c[k]) > now:
                return True
        return False

    def _in_window(self, c: dict, now: datetime) -> bool:
        last = c.get("last_inbound_at")
        return bool(last) and now - datetime.fromisoformat(last) <= timedelta(hours=self.g["window_hours"])

    # -------- inbound
    def handle(self, ev: dict, now: datetime | None = None) -> list[dict]:
        now = now or datetime.now(timezone.utc)
        if self.store.seen(ev["id"], now):
            return []
        key = f"{ev['platform']}:{ev['sender']}"
        c = self.store.contact(key)
        c["last_inbound_at"] = now.isoformat()
        c["page"] = ev.get("page", "")
        for t in (f"src_{ev['platform']}",) + ((f"post_{ev['post_id']}",) if ev.get("post_id") else ()):
            if t not in c["tags"]:
                c["tags"].append(t)
        actions = self._handle(ev, c, now)
        self.store.save(c)
        for a in actions:
            self.store.enqueue(a, now)
        return actions

    def _handle(self, ev: dict, c: dict, now: datetime) -> list[dict]:
        text = ev.get("text") or ""
        # 1. Crisis first, always (a direct answer to their message, even if they opted out of automation).
        cr = self._crisis(text) if ev["kind"] in ("message", "comment") else None
        if cr:
            cat, spec = cr
            c["paused_until"] = (now + timedelta(days=spec["pause_days"])).isoformat()
            res = self.post_exception("crisis_escalation", f"DM {cat.replace('_', ' ')} ({ev['platform']})", source="dm",
                                      ref=hashlib.sha256(f"{ev['platform']}:{ev['sender']}".encode()).hexdigest()[:16],
                                      severity=spec["severity"], dedupe_key=f"dm-crisis:{ev['id']}",
                                      detail="Open the page inbox for this conversation. Staffed hours 07:00-23:00 ET: "
                                             "acknowledge within 15 minutes. Reply as '[First name] from the Strong Years team'.",
                                      payload={"category": cat, "platform": ev["platform"]})
            acts = self._dm(ev, c, spec["safety_dm"], now, "SAFETY", safety=True)
            acts.append({"type": "crisis_alert", "category": cat, "platform": ev["platform"], "in_reply_to": ev["id"],
                         "exception": res.get("status")})
            return acts
        # 2. STOP / START (exact words) and the other global intents.
        intent = self._intent(text) if ev["kind"] == "message" else None
        if intent and intent.get("action") == "opt_out":
            already = c.get("opted_out")
            c["opted_out"] = True
            c["followups"] = {}  # pending nudges/check-ins are dropped, not resumed after a later START
            self.store.consent(c["key"], "opt_out", f"keyword {norm(text)!r}", now)
            return [] if already else self._dm(ev, c, intent["dm"], now, "STOP")
        if intent and intent.get("action") == "opt_in":
            c["opted_out"] = False
            self.store.consent(c["key"], "opt_in", f"keyword {norm(text)!r}", now)
            return self._dm(ev, c, intent["dm"], now, "START")
        if c.get("opted_out"):
            return []
        if self._paused(c, now):
            return []  # a person has this conversation (crisis follow-up or human handoff)
        if intent:
            if intent.get("action") == "handoff":
                c["handoff_until"] = (now + timedelta(days=self.g["human_agent_tag_days"])).isoformat()
            texts = intent.get("dm") or intent.get(f"dm_{self.mode}") or []
            return self._dm(ev, c, texts, now, intent["id"].upper())
        # 3. Button / quick-reply taps continue a flow.
        if ev["kind"] in ("postback", "quick_reply") and ":" in (ev.get("payload") or ""):
            fid, sid = ev["payload"].split(":", 1)
            f = self.flows.get(fid)
            if f and sid in f["states"] and self._active(f):
                return self._state_actions(f, sid, ev, c, now)
            return []
        # 4. Email capture inside a flow.
        fs = c.get("flow_state") or {}
        f = self.flows.get(fs.get("flow", ""))
        if f and f["states"].get(fs.get("state", ""), {}).get("expect") == "email" and ev["kind"] == "message":
            email = text.strip()
            if EMAIL_RX.match(email):
                c["email"] = email.lower()
                nxt = f["states"][fs["state"]]["next"]
                acts = self._state_actions(f, nxt, ev, c, now)
                self.store.consent(c["key"], "email_opt_in", f"flow {f['flow_id']}: {acts[0]['text'][:300]}", now)
                acts.append({"type": "lead", "email": c["email"], "source": f"dm_{f['flow_id']}", "mc_id": ev["sender"],
                             "consent_text": acts[0]["text"], "in_reply_to": ev["id"]})
                return acts
            return self._dm(ev, c, ["That doesn't look like an email address. Could you type it again?"], now, f["keyword"])
        # 5. Keywords (comments and messages).
        f = self.match_keyword(text)
        if not f:
            return []
        kw_tag = f"kw_{f['flow_id']}"
        if kw_tag not in c["tags"]:
            c["tags"].append(kw_tag)
            c["kw_count"] = c.get("kw_count", 0) + 1
        c.setdefault("first_kw", f["keyword"])
        acts = []
        if ev["kind"] == "comment":
            pool = f.get("reply") or []
            if pool:
                pick = pool[int(hashlib.sha256(ev["id"].encode()).hexdigest(), 16) % len(pool)]
                acts.append({"type": "public_reply", "platform": ev["platform"], "comment_id": ev.get("comment_id"),
                             "text": pick.replace("{first_name}", "").replace(", .", ".").strip(), "in_reply_to": ev["id"]})
        last = c["flows_sent"].get(f["flow_id"])
        if last and now - datetime.fromisoformat(last) < timedelta(hours=self.g["dedup_hours"]):
            return acts  # same flow in the last 24 h: public reply only
        c["flows_sent"][f["flow_id"]] = now.isoformat()
        c["followups"] = {**(c.get("followups") or {}), f["flow_id"]: {"started_at": now.isoformat(), "done": []}}
        ev2 = {**ev, "post_id": ev.get("post_id")}
        return acts + self._state_actions(f, f["start"], ev2, c, now)

    # -------- follow-ups (nudge +20 min, check-in +22 h), only inside the person's own 24-hour window
    def due_followups(self, now: datetime | None = None) -> list[dict]:
        now = now or datetime.now(timezone.utc)
        out = []
        for c in self.store.contacts():
            if c.get("opted_out") or self._paused(c, now) or not self._in_window(c, now):
                continue
            platform, sender = c["key"].split(":", 1)
            changed = False
            for fid, fu in (c.get("followups") or {}).items():
                f = self.flows.get(fid)
                if not f or not self._active(f):
                    continue
                started = datetime.fromisoformat(fu["started_at"])
                for spec in f.get("followups") or []:
                    if spec["id"] in fu["done"] or now < started + timedelta(minutes=spec["after_minutes"]):
                        continue
                    fu["done"].append(spec["id"])
                    changed = True
                    if spec.get("unless") == "link_clicked" and c.get("link_clicked"):
                        continue
                    ev = {"platform": platform, "sender": sender, "page": c.get("page", ""), "id": f"fu:{fid}:{spec['id']}:{fu['started_at']}",
                          "kind": "followup"}
                    if spec.get("state"):
                        acts = self._state_actions(f, spec["state"], ev, c, now)
                    else:
                        acts = self._dm(ev, c, spec["dm"], now, f["keyword"], flow=fid)
                    for a in acts:
                        a["followup"] = spec["id"]
                        self.store.enqueue(a, now)
                    out.extend(acts)
            if changed:
                self.store.save(c)
        return out
