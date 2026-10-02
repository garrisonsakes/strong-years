"""Daily posting plan D-7 .. D+90 (tonight 2026-10-01 = D-7, D0 = 2026-10-08) -> data/content/posting_plan_90d.csv
and the generated tables in POSTING_PLAN.md (between the PLAN_TABLES markers).

One row = one published post (page x platform x slot). One source script = one uniqueness group per page per slot:
IG / FB / TT get their own packaged variant of the master (native caption + CTA mechanics), YouTube gets a distinct
cut, Threads and X get a text/carousel post written from the same script. Every row has its own file_id (never
the same file twice). Library scripts (data/content/scripts.json; runway_scripts.json is the S151-S190 subset with
extra fields) are used once network-wide, in data/content/runway_calendar_R7.csv order first; empty slots are
"GEN-needed" and get pillar/format from the CONTENT_SYSTEM §3 share-of-feed targets under the allocator caps
(workers/growth/config.py). Deterministic; no network, no spend.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "data/content"
OUT_CSV = CONTENT / "posting_plan_90d.csv"
VAR_CSV = CONTENT / "posting_plan_variants_90d.csv"   # Trial Reels (TEST) + Facebook text/photo slots
sys.path.insert(0, str(Path(__file__).resolve().parent))
import posting_rules as PR  # noqa: E402  (also puts workers/ on sys.path)
from growth import variants as GV  # noqa: E402

D0 = date(2026, 10, 8)            # tonight 2026-10-01 is D-7 (7-day runway)
D_FIRST, D_LAST = -7, 90
SHOOT_D = -3                       # performer shoot day; movement renders from D-3, first movement post D-2
MOVEMENT_FIRST_POST_D = SHOOT_D + 1
PLATFORMS = ["ig_reels", "fb_reels", "tiktok", "yt_shorts", "threads", "x"]
VIDEO_PLATFORMS = PLATFORMS[:4]

PAGES = {  # handle: (start D, code, lead character, max cadence override). CANON UPDATE 4: 4 IG pages, all from D-7
    "@changyin": (-7, "CY", "CHANG", None),
    "@sunyoon.kitchen": (-7, "SK", "SUN", None),
    "@changandsun": (-7, "CS", "DUO", None),
    "@changyin.strength": (-7, "CYS", "CHANG", None),
}
# Library scripts written for pages that are no longer in the canon roster post on the nearest canon page.
PAGE_REMAP = {"@changyin.mobility": "@changyin.strength", "@sunyoon": "@sunyoon.kitchen", "@changyin.espanol": "@changyin"}
FULL_CADENCE = 6                  # CANON UPDATE 4: 6 videos/day per page from D0 (ramp 3/day D-7..D-5, 5/day D-4..D-1)
MAX_MOVEMENT_PER_PAGE_DAY = 1     # movement only where the script has an exercise demo, ~1 in 6
BROLL_SHARE = 0.25                # B-roll ("insert" lane) <= 25% of masters; 1 Nano Banana still + push-in, Veo only if flagged
MAX_PER_PILLAR_PER_DAY = 2        # workers/growth/config.py allocator.max_per_pillar_per_day

# 55+ windows (ORGANIC_ENGINE §1.4 canon slots first, then added in-window slots up to 9; all ET)
SLOTS = {
    "fb_reels": ["06:30", "08:00", "10:00", "12:00", "15:00", "18:30", "20:00", "09:00", "13:30"],
    "ig_reels": ["07:00", "08:30", "11:00", "12:45", "16:00", "19:00", "21:00", "14:00", "17:30"],
    "tiktok": ["08:00", "12:00", "17:00", "19:30", "21:00", "07:15", "10:30", "14:30", "15:45"],
    "yt_shorts": ["09:00", "14:00", "18:00", "20:00", "07:45", "11:30", "16:30", "12:30", "21:15"],
    "threads": ["07:30", "12:30", "18:00", "09:30", "15:30", "20:30", "11:00", "17:00", "21:30"],
    "x": ["08:00", "13:00", "19:00", "09:45", "11:45", "15:15", "17:45", "20:45", "07:00"],
}

SHARE = {  # CONTENT_SYSTEM §3 (%), pillar -> per page
    "@changyin": dict(P01=12, P02=9, P03=12, P04=6, P05=5, P06=5, P07=4, P08=5, P09=4, P10=2, P13=3, P14=7, P15=8, P16=4, P17=2, P18=4, P19=6, P20=2),
    "@sunyoon.kitchen": dict(P10=15, P11=22, P12=13, P13=15, P14=2, P15=12, P16=8, P17=3, P18=5, P19=5),
    "@changandsun": dict(P01=6, P03=8, P07=5, P09=2, P13=6, P15=6, P16=15, P17=35, P18=8, P19=6, P20=3),
    "@changyin.strength": dict(P01=20, P02=22, P04=15, P06=8, P13=4, P14=10, P15=8, P18=5, P19=8),
}
PILLAR_FORMATS = {  # CONTENT_SYSTEM §1 primary formats
    "P01": ["F02", "F16", "F23"], "P02": ["F01", "F17", "F15"], "P03": ["F02", "F15", "F32"], "P04": ["F15", "F02"],
    "P05": ["F20", "F05", "F01"], "P06": ["F14", "F03"], "P07": ["F21"], "P08": ["F22"], "P09": ["F05"],
    "P10": ["F06", "F31"], "P11": ["F31", "F12"], "P12": ["F06"], "P13": ["F18", "F12"], "P14": ["F13", "F30"],
    "P15": ["F04", "F28"], "P16": ["F07", "F35"], "P17": ["F08", "F34", "F35"], "P18": ["F09", "F10", "F26"],
    "P19": ["F11"], "P20": ["F08", "F28"],
}
PILLAR_CTA = {"P01": "STRONG", "P02": "STRONG", "P03": "BALANCE", "P04": "STRONG", "P05": "BACK", "P06": "BACK",
              "P07": "BREATH", "P08": "BALANCE", "P09": "SLEEP", "P10": "GUT", "P11": "SOUP", "P12": "GUT",
              "P13": "SOUP", "P14": "STRONG", "P15": "TEST", "P16": "BEGIN", "P17": "BEGIN", "P18": "BEGIN",
              "P19": "STRONG", "P20": "BEGIN"}
ES_KEYWORD = {"STRONG": "FUERTE", "BALANCE": "EQUILIBRIO", "BACK": "ESPALDA", "KNEES": "RODILLAS", "SLEEP": "SUEÑO",
              "BREATH": "RESPIRA", "SOUP": "SOPA", "BEGIN": "EMPEZAR", "TEST": "PRUEBA", "FAMILY": "FAMILIA",
              "GUT": "SOPA", "BOOK": "LIBRO", "JOIN": "UNIRME", "WAITLIST": "LISTA"}   # FUNNEL.md §4.20–4.22
# ---- Spanish rows (CHARACTERS_ES.md; BRIEF.md CANON UPDATE 5) ----------------------------------------------------------
# The Spanish page opens at the $30K retained-MRR rung of the scale-on-MRR ladder (workers/growth/config.py
# governor.scale_rules), not on a calendar date. ES_START_D = the plan day the governor flipped that rung: None (default)
# = not in this plan (output unchanged); set it here, or with the env var ES_START_D, once the rung is hit. The page then
# runs its own runway (ES_RUNWAY_DAYS: LISTA waitlist, no offers), then a launch week (LIBRO/UNIRME rows under the same
# offer caps), then steady state; GEN rows use the Spanish keyword map and the ES library (data/content/scripts_es.json).
ES_OPEN_RUNG_MRR = 30_000
ES_START_D: int | None = None
ES_RUNWAY_DAYS = 7
ES_PAGES = {  # handle: (code, lead, CONTENT_SYSTEM §3-style pillar share for the duo page)
    "@donchuyylupe": ("DCL", "DUO_ES", dict(P01=10, P02=10, P03=10, P04=8, P05=4, P07=3, P09=3, P10=7, P11=8, P12=5, P13=8,
                                            P15=8, P16=6, P17=6, P19=2, P20=2)),
}
if re.fullmatch(r"[+-]?\d+", os.environ.get("ES_START_D", "").strip()):
    ES_START_D = int(os.environ["ES_START_D"])
if ES_START_D is not None:
    for _h, (_code, _lead, _share) in ES_PAGES.items():
        PAGES[_h] = (ES_START_D, _code, _lead, None)
        SHARE[_h] = _share


def local_d(page: str, d: int) -> int:
    """Offer/runway clock for a page: the global D for the US pages; for a Spanish page, days since its own checkout
    opened (negative during its ES_RUNWAY_DAYS runway)."""
    if page in ES_PAGES and ES_START_D is not None:
        return d - (ES_START_D + ES_RUNWAY_DAYS)
    return d


def load_es_library() -> list[dict]:
    path = CONTENT / "scripts_es.json"
    if ES_START_D is None or not path.exists():
        return []
    out = []
    for s in json.loads(path.read_text(encoding="utf-8")):
        g = s.get("hook_grammar") or ["CUR"]
        out.append({**s, "hook_grammar": "+".join(g) if isinstance(g, list) else g})
    return out


MOTION_FORMATS = {"F01", "F11", "F14", "F17", "F20", "F21", "F22", "F23", "F25", "F34"}   # config render_format.motion
INSERT_FORMATS = {"F06", "F12", "F16", "F18", "F19", "F28", "F30", "F31"}                # no-face prop/kitchen/stat cuts
GEN_GRAMMARS = ["OBJ3", "IF_EVERY", "MYTH_NOT", "WATCH", "TEST_NOW", "SHARE", "DEMO"]   # POSTDB §8 grammars
GEN_SECONDS = 42                                                                         # allocator bucket M target


def cadence(page: str, d: int) -> int:
    start, _, _, cap = PAGES[page]
    age = d - start
    if age < 0:
        return 0
    n = 3 if age <= 2 else 5 if age <= 6 else FULL_CADENCE
    return min(n, cap) if cap else n


def broll_caps(page: str, d: int) -> tuple[int, int]:
    """(per page-day cap, network-day cap) for B-roll masters: network <= floor(25% of the day's masters)."""
    n = cadence(page, d)
    return -(-n // 4), int(BROLL_SHARE * sum(cadence(p, d) for p in PAGES))


def stage(d: int) -> str:
    return "RUNWAY" if d < 0 else "LAUNCH_WEEK" if d <= 6 else "SCALE"


def offer_target(page: str, d: int) -> int:
    """Book/join masters per page per day (ORGANIC_ENGINE §1.3/§5.2: <=2 in launch week; plan rule after: 1/day)."""
    if d < 0:
        return 0
    if d <= 6:
        return {5: 0, 6: 1}.get(d, 2)
    return 1


def offer_cap(d: int) -> int:
    return 0 if d < 0 else 2 if d <= 6 else 1


def waitlist_target(n: int) -> int:
    """Runway: ~1 in 3 masters asks for WAITLIST (8 of 25 runway scripts, ORGANIC_ENGINE §3.2)."""
    return round(n / 3)


def load_library() -> tuple[dict, list[tuple[str, str]], dict]:
    lib = {s["id"]: s for s in json.loads((CONTENT / "scripts.json").read_text(encoding="utf-8"))}
    for s in json.loads((CONTENT / "runway_scripts.json").read_text(encoding="utf-8")):
        lib[s["id"]] = {**lib.get(s["id"], {}), **s}
    for s in lib.values():
        s["page"] = PAGE_REMAP.get(s["page"], s["page"])
    order = []
    with (CONTENT / "runway_calendar_R7.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            order += [(PAGE_REMAP.get(r["page"], r["page"]), m) for m in re.findall(r"\b(S\d+)\b", r["posts"])]
    hooks = {}
    with (CONTENT / "hooks.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            hooks[r["id"]] = r["category"]
    return lib, order, hooks


def load_wave2() -> list[dict]:
    """Wave-2 scripts (data/content/scripts_wave2.py, written by the wave2 agent) normalised to library keys.
    Each carries `group` (the plan group it was written for) and its own lane; missing/broken file -> []."""
    path = CONTENT / "scripts_wave2.py"
    if not path.exists():
        return []
    try:
        import runpy
        raw = runpy.run_path(str(path)).get("SCRIPTS", [])
    except Exception as e:  # file is being edited concurrently: plan without it, say so
        print(f"WARN wave2 not loaded: {e}")
        return []
    out = []
    for s in raw:
        g = s.get("grammar") or ["CUR"]
        out.append({"id": s["id"], "page": PAGE_REMAP.get(s["page"], s["page"]), "pillar": s["pillar"], "format": s["format"],
                    "speaker": s["speaker"], "hook_grammar": g[0] if isinstance(g, list) else g, "cta_keyword": s.get("cta"),
                    "target_seconds": GEN_SECONDS, "has_movement": s.get("lane") == "movement",
                    "w2_lane": s.get("lane"), "group": s.get("group"), "veo": bool(s.get("veo")), "wave2": True})
    return out


def load_all() -> dict:
    lib, _, _ = load_library()
    return {**lib, **{s["id"]: s for s in load_wave2()}, **{s["id"]: s for s in load_es_library()}}


def cta_type_of(kw: str) -> str:
    return {"WAITLIST": "waitlist", "BOOK": "book", "JOIN": "join",
            "LISTA": "waitlist", "LIBRO": "book", "UNIRME": "join"}.get((kw or "").upper(), "none")


def previous_assignments() -> dict[str, dict]:
    """group -> row for script ids already written into the plan that are neither library nor GEN-needed
    (e.g. tools/assign_scripts.py output), so a rebuild keeps them."""
    if not OUT_CSV.exists():
        return {}
    keep = {}
    with OUT_CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["script_id"] not in ("GEN-needed", "") and not re.fullmatch(r"S\d+", r["script_id"]):
                keep.setdefault(r["uniqueness_group"], r)
    return keep


def build() -> list[dict]:
    lib, r7, hooks = load_library()
    w2 = load_wave2()
    queues: dict[str, list[str]] = defaultdict(list)
    seen = set()
    for page, sid in r7:
        if sid in lib and lib[sid]["page"] == page and sid not in seen:
            queues[page].append(sid); seen.add(sid)
    for sid in sorted(lib, key=lambda x: int(x[1:])):
        if sid not in seen:
            queues[lib[sid]["page"]].append(sid); seen.add(sid)
    for s in load_es_library():                       # Spanish library, only when ES_START_D is set
        lib[s["id"]] = s
        queues[s["page"]].append(s["id"])
    pins: dict[str, str] = {}
    for s in w2:
        lib[s["id"]] = s
        queues[s["page"]].append(s["id"])
        if s.get("group"):
            pins[s["group"]] = s["id"]
    for g, r in previous_assignments().items():
        sid = r["script_id"]
        if sid not in lib:
            lib[sid] = {"id": sid, "page": r["page"], "pillar": r["pillar"], "format": r["format"], "speaker": r["character"],
                        "hook_grammar": r["hook_grammar"], "cta_keyword": r["cta_keyword"], "target_seconds": int(r["seconds"] or GEN_SECONDS),
                        "has_movement": r["render_lane"] == "movement", "w2_lane": r["render_lane"]}
            queues[r["page"]].append(sid)
        pins[g] = sid
    pin_day = {sid: int(re.match(r"UG-\w+-([+-]\d+)-", g).group(1)) for g, sid in pins.items()
               if re.match(r"UG-\w+-([+-]\d+)-", g)}
    used: set[str] = set()
    pillar_count: dict[str, Counter] = defaultdict(Counter)
    gen_n: Counter = Counter()
    rows: list[dict] = []
    alt_offer: Counter = Counter()
    placed_group: dict[str, str] = {}
    for d in range(D_FIRST, D_LAST + 1):
        day = D0 + timedelta(days=d)
        net_broll = 0
        for page, (start, code, lead, _) in PAGES.items():
            n = cadence(page, d)
            if not n:
                continue
            slots: list[dict | None] = [None] * n
            st = {"pill": Counter(), "offers": 0, "mv": 0, "br": 0}
            ld = local_d(page, d)
            o_target, o_cap = offer_target(page, ld), offer_cap(ld)
            br_page, br_net = broll_caps(page, d)

            def broll_ok() -> bool:
                return st["br"] < br_page and net_broll + st["br"] < br_net

            def lane_of(s: dict) -> str | None:
                """Canon lane for a script today, or None if it can't post today (defer)."""
                w2l = s.get("w2_lane")
                if s.get("has_movement") or w2l == "movement":
                    return "movement" if d >= MOVEMENT_FIRST_POST_D and st["mv"] < MAX_MOVEMENT_PER_PAGE_DAY else None
                if w2l == "insert":                      # voice-over only, no face: must be a B-roll master
                    return "insert" if broll_ok() else None
                if w2l is None and s["format"] in INSERT_FORMATS and broll_ok():
                    return "insert"
                return "talking_head"

            def take(sid: str, i: int) -> bool:
                s = lib[sid]
                ct = cta_type_of(s.get("cta_keyword"))
                if ct == "waitlist" and ld >= 0:
                    return False
                if ct in ("book", "join") and (ld < 0 or st["offers"] >= min(o_target, o_cap)):
                    return False
                if st["pill"][s["pillar"]] >= MAX_PER_PILLAR_PER_DAY:
                    return False
                lane = lane_of(s)
                if lane is None:
                    return False
                used.add(sid)
                st["pill"][s["pillar"]] += 1
                st["offers"] += ct in ("book", "join")
                st["mv"] += lane == "movement"
                st["br"] += lane == "insert"
                hg = s.get("hook_grammar")
                hg = "+".join(hg) if isinstance(hg, list) else hg or hooks.get(s.get("hook_id") or "", "CUR")
                slots[i] = {"script_id": sid, "pillar": s["pillar"], "format": s["format"], "character": s["speaker"],
                            "hook_grammar": hg, "cta_keyword": s["cta_keyword"], "cta_type": ct, "cta_source": "script",
                            "seconds": int(s.get("target_seconds") or GEN_SECONDS), "lane": lane,
                            "demo": "y" if lane == "movement" else "n", "veo": "y" if s.get("veo") else "n"}
                return True

            # 0) pinned scripts (wave2 groups / earlier assignments) where the canon caps allow them
            for i in range(n):
                sid = pins.get(f"UG-{code}-{d:+03d}-{i + 1}")
                if sid and sid not in used and lib[sid]["page"] == page:
                    take(sid, i)
            # 1) library + wave2 queue, in order, that are legal today
            for sid in queues[page]:
                free = [i for i in range(n) if slots[i] is None]
                if not free:
                    break
                if sid not in used and pin_day.get(sid, D_FIRST - 1) <= d:   # pinned scripts wait for their own day
                    take(sid, free[0])
            # 2) GEN-needed slots
            for i in range(n):
                if slots[i] is not None:
                    continue
                share = SHARE[page]
                tot = sum(pillar_count[page].values()) + 1
                cands = [p for p in share if st["pill"][p] < MAX_PER_PILLAR_PER_DAY]
                p = max(cands, key=lambda q: (share[q] / 100 - pillar_count[page][q] / tot, share[q]))
                fmts = PILLAR_FORMATS[p]
                fmt = fmts[gen_n[(page, p)] % len(fmts)]
                lane = "talking_head"
                if fmt in MOTION_FORMATS:
                    if d >= MOVEMENT_FIRST_POST_D and st["mv"] < MAX_MOVEMENT_PER_PAGE_DAY:
                        lane = "movement"
                    else:
                        fmt = next((f for f in fmts if f not in MOTION_FORMATS), fmt)
                if lane == "talking_head" and fmt in INSERT_FORMATS and broll_ok():
                    lane = "insert"
                gen_n[(page, p)] += 1
                st["pill"][p] += 1
                st["mv"] += lane == "movement"
                st["br"] += lane == "insert"
                kw = PILLAR_CTA[p]
                ct = "none"
                if st["offers"] < o_target:
                    ct = "book" if alt_offer[page] % 2 == 0 else "join"
                    alt_offer[page] += 1
                    st["offers"] += 1
                    kw = ct.upper()
                if page in ES_PAGES:
                    kw = ES_KEYWORD.get(kw, kw)
                k = gen_n[(page, "all")]; gen_n[(page, "all")] += 1
                slots[i] = {"script_id": "GEN-needed", "pillar": p, "format": fmt, "character": lead,
                            "hook_grammar": GEN_GRAMMARS[k % len(GEN_GRAMMARS)], "cta_keyword": kw, "cta_type": ct,
                            "cta_source": "generated", "seconds": GEN_SECONDS, "lane": lane,
                            "demo": "y" if lane == "movement" else "n", "veo": "n"}
            net_broll += st["br"]
            masters = slots
            # 3) runway waitlist ratio: swap the last line of value masters to WAITLIST until ~1 in 3
            if ld < 0:
                need = waitlist_target(n) - sum(m["cta_type"] == "waitlist" for m in masters)
                for m in reversed(masters):
                    if need <= 0:
                        break
                    if m["cta_type"] == "none":
                        m.update(cta_type="waitlist", cta_keyword=ES_KEYWORD["WAITLIST"] if page in ES_PAGES else "WAITLIST",
                                 cta_source="swap" if m["script_id"] != "GEN-needed" else "generated")
                        need -= 1
            for m in masters:
                pillar_count[page][m["pillar"]] += 1
            # 4) rows: one group = one render (render_id) -> 4 packaged video files + Threads/X text variants.
            # Facebook is a native upload with its own caption and close; fb_long_target(n) of the day's masters
            # (movement first, then the longest) get their Facebook placement as a 60-180 s long cut instead.
            fb_long_i = set(sorted(range(n), key=lambda i: (masters[i]["lane"] != "movement", -masters[i]["seconds"], i))
                            [:PR.fb_long_target(n)])
            for i, m in enumerate(masters):
                grp = f"UG-{code}-{d:+03d}-{i + 1}"
                placed_group[m["script_id"]] = grp
                for plat in PLATFORMS:
                    slot = sorted(SLOTS[plat][:n])[i]
                    is_text = plat in ("threads", "x")
                    surface = PR.PLAT_SURFACE[plat]
                    variant = "yt_distinct_cut" if plat == "yt_shorts" else ("text_post" if is_text else "platform_package")
                    secs = 0 if is_text else m["seconds"]
                    if plat == "fb_reels":
                        variant = "fb_long" if i in fb_long_i else "fb_native"
                        if variant == "fb_long":
                            secs = int(min(PR.FB_LONG_S[1], max(PR.FB_LONG_S[0], 2 * m["seconds"] + 10)))
                    trial_feed = plat == "ig_reels" and PR.ig_trial_reel(page, d)
                    rows.append({
                        "date": day.isoformat(), "day_index": d, "stage": stage(ld), "page": page, "platform": plat,
                        "slot_et": slot, "render_lane": "carousel_text" if is_text else m["lane"],
                        "pillar": m["pillar"], "format": "F37" if is_text and plat == "threads" else ("F37/F36" if is_text else m["format"]),
                        "character": m["character"], "hook_grammar": m["hook_grammar"], "cta_type": m["cta_type"],
                        "cta_keyword": m["cta_keyword"], "cta_source": m["cta_source"], "uniqueness_group": grp,
                        "file_id": f"{grp}-{plat}", "variant": variant,
                        "script_id": m["script_id"], "seconds": secs,
                        "cadence_target": n, "render_id": "" if is_text else f"R-{grp}",
                        "demo": m["demo"], "veo_flag": m["veo"] if not is_text else "n",
                        "variant_role": "PLACEMENT", "body_id": f"B-{grp}", "hook_id": f"H-{grp}",
                        "close_id": f"C-{grp}-{surface}",
                        "caption_source": "fb_native" if plat == "fb_reels" else "platform_native",
                        "close_line": GV.CLOSE_BY_PLATFORM.get(surface, ""),
                        "graduation_strategy": "SS_PERFORMANCE" if trial_feed else "",
                        "feed_rule": "graduation" if plat == "ig_reels" else "",
                    })
    build.wave2_map = [(s["id"], s.get("group") or "", placed_group.get(s["id"], "")) for s in w2]  # type: ignore[attr-defined]
    return rows


FIELDS = ["date", "day_index", "stage", "page", "platform", "slot_et", "render_lane", "pillar", "format", "character",
          "hook_grammar", "cta_type", "cta_keyword", "cta_source", "uniqueness_group", "file_id", "variant",
          "script_id", "seconds", "cadence_target", "render_id", "demo", "veo_flag",
          "variant_role", "body_id", "hook_id", "close_id", "caption_source", "close_line", "graduation_strategy",
          "feed_rule"]
VFIELDS = ["date", "day_index", "stage", "page", "platform", "slot_et", "variant_role", "target_group", "body_id",
           "hook_id", "variant_id", "file_id", "ops", "dims_changed", "signature", "graduation_strategy", "seconds",
           "cost_usd", "script_id", "pillar", "hook_grammar", "cta_keyword"]
TRIAL_SLOTS = [f"{(375 + 45 * k) // 60:02d}:{(375 + 45 * k) % 60:02d}" for k in range(20)]   # 06:15 ... 20:30 ET
FB_TEXT_PHOTO_SLOTS = {"fb_text": "11:30", "fb_photo": "16:30"}
ALT_HOOKS_PER_MASTER = 3          # the writer drafts 3 alternative hooks per master (same claim, new opening)


def build_variants(rows: list[dict]) -> list[dict]:
    """TEST rows (IG Trial Reels) and Facebook text/photo slots from the placement plan.
    Trial Reels published on day d test the hooks of day d+1's masters (>= 10 h before their feed slot, so the 6 h
    read decides graduation). Per page-day count = posting_rules.trial_cap (3 / 6 / configured cap), spread over the
    next day's masters (<= max_trials_per_body each); variants come from workers/growth/variants.generate."""
    ig = [r for r in rows if r["platform"] == "ig_reels"]
    by_day: dict[tuple, list[dict]] = defaultdict(list)
    for r in ig:
        by_day[(r["page"], int(r["day_index"]))].append(r)
    out: list[dict] = []
    for page, (start, code, _, _) in PAGES.items():
        for d in range(D_FIRST, D_LAST + 1):
            today, nxt = by_day.get((page, d)), by_day.get((page, d + 1))
            if not today:
                continue
            day = today[0]["date"]
            for p, slot in FB_TEXT_PHOTO_SLOTS.items():
                out.append({"date": day, "day_index": d, "stage": stage(d), "page": page, "platform": p, "slot_et": slot,
                            "variant_role": "PLACEMENT", "target_group": "", "body_id": "", "hook_id": "",
                            "variant_id": f"FB-{code}-{d:+03d}-{p}", "file_id": f"FB-{code}-{d:+03d}-{p}", "ops": p,
                            "dims_changed": "", "signature": "", "graduation_strategy": "", "seconds": 0,
                            "cost_usd": GV._vcfg(None)["op_cost_usd"][p], "script_id": "GEN-needed", "pillar": "",
                            "hook_grammar": "", "cta_keyword": ""})
            if not nxt:
                continue
            cap = PR.trial_cap(page, d)
            per_body = min(int(PR.VCFG["max_trials_per_body"]), -(-cap // len(nxt)))
            pools = []
            for r in nxt:
                m = {"master_id": r["uniqueness_group"], "page": page, "duration_s": int(r["seconds"]), "pillar": r["pillar"],
                     "format": r["format"], "hook_grammar": r["hook_grammar"], "character": r["character"],
                     "hook_id": r["hook_id"], "body_id": r["body_id"], "close_id": f"C-{r['uniqueness_group']}",
                     "hook_pool": [{"id": f"{r['hook_id']}-alt{k + 1}", "text": ""} for k in range(ALT_HOOKS_PER_MASTER)]}
                auto = {(page, r["body_id"])} if r.get("graduation_strategy") == "SS_PERFORMANCE" else set()
                pools.append((r, GV.assign_trial_params(GV.generate(m, per_body), auto)))
            picked = []
            for j in range(per_body):                   # round-robin: every master gets its first test first
                for r, vs in pools:
                    if j < len(vs) and len(picked) < cap:
                        picked.append((r, vs[j]))
            for k, (r, v) in enumerate(picked):
                out.append({"date": day, "day_index": d, "stage": stage(d), "page": page, "platform": "ig_trial",
                            "slot_et": TRIAL_SLOTS[k], "variant_role": "TEST", "target_group": r["uniqueness_group"],
                            "body_id": v["body_id"], "hook_id": v["hook_id"], "variant_id": v["variant_id"],
                            "file_id": f"{v['variant_id']}-ig_trial", "ops": "|".join(v["ops"]),
                            "dims_changed": "|".join(v["dims_changed"]),
                            "signature": json.dumps(v["signature"], sort_keys=True, separators=(",", ":")),
                            "graduation_strategy": v["trial_params"]["graduation_strategy"], "seconds": v["length_s"],
                            "cost_usd": v["cost_usd"], "script_id": r["script_id"], "pillar": r["pillar"],
                            "hook_grammar": r["hook_grammar"], "cta_keyword": r["cta_keyword"]})
    return out


def write_csv(rows: list[dict], path: Path = OUT_CSV, fields: list[str] = FIELDS) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    import account_topology as AT
    rows = build()
    write_csv(rows)
    vrows = build_variants(rows)
    # CANON UPDATE 6 topology: one FB page (text/photo once per page), 3 Stories per IG page per day, and the account
    # plan (1 YouTube channel at 4/day until the quota raise, FB 12 + 2 long, TikTok accounts separate from IG pages).
    vrows = AT.fb_text_photo_rows(vrows) + AT.stories_rows(rows, stage)
    write_csv(vrows, VAR_CSV, VFIELDS)
    acc = AT.apply(rows)
    AT.write(acc, FIELDS)
    held = Counter((r["platform"], r["hold_reason"]) for r in acc if r["publish"] != "y")
    print(f"account plan: {sum(r['publish'] == 'y' for r in acc)} scheduled + {sum(r['publish'] != 'y' for r in acc)} held "
          f"-> {AT.ACCOUNTS_CSV.relative_to(ROOT)}; held by reason: {dict(held)}")
    print(f"day 1 per account: {AT.summary(acc, vrows, 1)}")
    print(f"{len(vrows)} variant rows ({sum(r['platform'] == 'ig_trial' for r in vrows)} Trial Reels, "
          f"{sum(r['platform'] != 'ig_trial' for r in vrows)} FB text/photo) -> {VAR_CSV.relative_to(ROOT)}")
    wm = build.wave2_map  # type: ignore[attr-defined]
    if wm:
        with (CONTENT / "wave2_group_map.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["script_id", "written_for_group", "plan_group", "moved"])
            w.writerows([(a, b, c, "y" if b != c else "n") for a, b, c in wm])
        print(f"wave2: {len(wm)} scripts, {sum(b != c for _, b, c in wm)} moved to another group (canon lane caps) -> data/content/wave2_group_map.csv")
    print(f"{len(rows)} posts -> {OUT_CSV.relative_to(ROOT)}")
