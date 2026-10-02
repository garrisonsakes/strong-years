#!/usr/bin/env python3
"""Calendar export of posting slots (ENGINE_SAVAGE20 §B(b) item 7, SL-26.3).

  python3 tools/slots_ics.py [--date YYYY-MM-DD] [--out DIR] [--tomorrow-platforms ig_reels,fb_reels] [--week-platforms all]
  python3 tools/posting_rules.py --ics [same flags]
  python3 tools/slots_ics.py --canon6 [--date D]   CANON 6 topology (tools/topology.py): one .ics per account

Writes one .ics per page for the launch day (`<page>_tomorrow.ics`) and for the 7 days from it (`<page>_week.ics`)
from data/content/posting_plan_90d.csv. Posters subscribe on their phone: each event is one placement with a
10-minute alarm, the file id, the script, the CTA keyword, trial or feed, and the skip rule (more than 30 min late →
skip, never post late). --date defaults to the date of the next 08:00 ET. Times are America/New_York (TZID), so the
phone shows the right local time. Offline; writes files only.
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
PLAN = ROOT / "data" / "content" / "posting_plan_90d.csv"
ET = ZoneInfo("America/New_York")
PLATFORM_NAME = {"ig_reels": "Instagram Reel", "fb_reels": "Facebook Reel", "tiktok": "TikTok", "yt_shorts": "YouTube Short",
                 "threads": "Threads", "x": "X", "ig_trial": "Instagram Trial Reel", "fb_text": "Facebook text",
                 "fb_photo": "Facebook photo", "ig_story": "Instagram Story", "fb_long": "Facebook long cut"}
VTIMEZONE = """BEGIN:VTIMEZONE
TZID:America/New_York
BEGIN:DAYLIGHT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
DTSTART:19700308T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
DTSTART:19701101T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE"""


def next_launch_date(now: datetime | None = None) -> date:
    now = (now or datetime.now(ET)).astimezone(ET)
    eight = now.replace(hour=8, minute=0, second=0, microsecond=0)
    return (eight if now < eight else eight + timedelta(days=1)).date()


def _esc(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line: str) -> str:
    out, b = [], line.encode("utf-8")
    while len(b) > 75:
        cut = 75
        while (b[cut] & 0xC0) == 0x80:      # never split a UTF-8 sequence
            cut -= 1
        out.append(b[:cut].decode())
        b = b" " + b[cut:]
    out.append(b.decode())
    return "\r\n".join(out)


def event(r: dict, stamp: str) -> list[str]:
    h, m = map(int, r["slot_et"].split(":"))
    start = datetime.fromisoformat(r["date"]).replace(hour=h, minute=m)
    plat = PLATFORM_NAME.get(r["platform"], r["platform"])
    trial = r["platform"] == "ig_trial" or (r.get("variant_role") or "").upper() == "TEST"
    desc = "\n".join([
        f"File: {r.get('file_id', '')}", f"Script: {r.get('script_id') or 'GEN-needed'} · {r.get('seconds', '')} s",
        f"CTA keyword: {r.get('cta_keyword') or '-'}", f"Trial: {'yes (Trial toggle ON)' if trial else 'no (feed)'}",
        *([f"Note: {r['note']}"] if r.get("note") else []),
        "Post only from the fallback pack (caption.txt unchanged, AI label ON, no cross-posting).",
        "More than 30 min late: skip and mark 'skipped' in posted_log.csv. Never post late.",
        "Then: paste the permalink into posted_log.csv.",
    ])
    uid = re.sub(r"[^A-Za-z0-9._-]", "-", f"{r['date']}-{r['page']}-{r['platform']}-{r['slot_et']}-{r.get('file_id') or ''}")
    return [
        "BEGIN:VEVENT", f"UID:{uid}@strongyears-slots", f"DTSTAMP:{stamp}",
        f"DTSTART;TZID=America/New_York:{start:%Y%m%dT%H%M00}",
        f"DTEND;TZID=America/New_York:{start + timedelta(minutes=15):%Y%m%dT%H%M00}",
        _fold("SUMMARY:" + _esc(" · ".join(x for x in (plat, r["page"], r.get("cta_keyword") or "") if x))),
        _fold(f"DESCRIPTION:{_esc(desc)}"),
        "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-PT10M", _fold(f"DESCRIPTION:{_esc(plat + ' ' + r['page'])}"), "END:VALARM",
        "END:VEVENT",
    ]


def calendar(rows: list[dict], name: str, stamp: str) -> str:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Strong Years//posting slots//EN", "CALSCALE:GREGORIAN",
             _fold(f"X-WR-CALNAME:{_esc(name)}"), "X-WR-TIMEZONE:America/New_York", *VTIMEZONE.splitlines()]
    for r in sorted(rows, key=lambda r: (r["date"], r["slot_et"], r["platform"])):
        lines += event(r, stamp)
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def export(day: date, out: Path, rows: list[dict] | None = None, tomorrow_platforms: set[str] | None = None,
           week_platforms: set[str] | None = None) -> dict:
    if rows is None:
        with PLAN.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(ZoneInfo("UTC")).strftime("%Y%m%dT%H%M%SZ")
    week = {(day + timedelta(days=i)).isoformat() for i in range(7)}
    written: dict[str, dict] = {}
    for page in sorted({r["page"] for r in rows}):
        slug = page.lstrip("@").replace(".", "_")
        t = [r for r in rows if r["page"] == page and r["date"] == day.isoformat()
             and (not tomorrow_platforms or r["platform"] in tomorrow_platforms)]
        w = [r for r in rows if r["page"] == page and r["date"] in week and (not week_platforms or r["platform"] in week_platforms)]
        if not (t or w):
            continue
        (out / f"{slug}_tomorrow.ics").write_text(calendar(t, f"{page} · {day}", stamp), encoding="utf-8")
        (out / f"{slug}_week.ics").write_text(calendar(w, f"{page} · week of {day}", stamp), encoding="utf-8")
        written[page] = {"tomorrow": len(t), "week": len(w)}
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="launch day YYYY-MM-DD (default: the next 08:00 ET)")
    ap.add_argument("--out", default=str(ROOT / "production" / "launch_day" / "out" / "calendar"))
    ap.add_argument("--tomorrow-platforms", default="ig_reels,fb_reels", help="launch day is IG + FB Reels by hand; 'all' for every row")
    ap.add_argument("--week-platforms", default="all")
    ap.add_argument("--canon6", action="store_true", help="CANON 6 topology: one .ics per account (tools/topology.py), all lanes incl. Stories")
    a = ap.parse_args([x for x in (argv if argv is not None else sys.argv[1:]) if x != "--ics"])
    day = date.fromisoformat(a.date) if a.date else next_launch_date()
    sel = lambda s: None if s == "all" else set(s.split(","))  # noqa: E731
    if a.canon6:
        import topology  # noqa: PLC0415
        w = export(day, Path(a.out), rows=topology.week(day))
    else:
        w = export(day, Path(a.out), tomorrow_platforms=sel(a.tomorrow_platforms), week_platforms=sel(a.week_platforms))
    print(f"calendar: {day} → {os.path.relpath(a.out)}; " + "; ".join(f"{p} {v['tomorrow']}/{v['week']}" for p, v in w.items()))
    return 0 if w else 1


if __name__ == "__main__":
    sys.exit(main())
