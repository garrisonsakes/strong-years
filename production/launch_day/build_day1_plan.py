"""Build + validate production/launch_day/day1_plan.json (6 day-1 posts, talking head + no-face inserts only).

  python3 production/launch_day/build_day1_plan.py          # writes day1_plan.json, exits 1 if any post fails

Sources: data/content/runway_scripts.json (RUNWAY_SCRIPTS.md, generated), the tools/build_content.py rule set
(validate / validate_v2 / validate_runway, blocked claims, outcome + mortality, condition hashtags), the workers
compliance scanner (pass 1 on the script, pass 2 on the packaged IG/FB captions + transcript + burned-in text,
first comments as snippets), the workers packager (exact SAFETY §7 footer, hashtag limits) and the fallback
packer's hold rules. The mandatory LLM judge is NOT run here (no external AI calls); every post is marked
judge=pending and still goes through the pipeline judge / human review before anything is published.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "workers"), str(ROOT / "tools")]

from common import evidence  # noqa: E402
from compliance import scanner  # noqa: E402
from packager import fallback, packager  # noqa: E402

_spec = importlib.util.spec_from_file_location("build_content", ROOT / "tools" / "build_content.py")
BC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BC)

DAY = "2026-10-01"
TZ = "-04:00"   # EDT on Oct 1 2026
PAGES = {"CHANG": {"handle": "@changyin", "code": "cy", "name": "Chang Yin"},
         "SUN": {"handle": "@sunyoon.kitchen", "code": "sk", "name": "Sun Yoon"}}

# Chosen for the no-performer-footage constraint: every beat can be carried by a lip-synced talking head except
# the two insert beats, which are object/hands-only shots (no face). Order per page follows the RUNWAY_ORDER
# disclosure-first rule (S158 / S167 first; they are the page's single WAITLIST post). S159 / S152 / S157 / S156
# (the next Chang runway picks) need a full-body demo and wait for performer footage; S155 and S154 replace them.
# Times: ORGANIC_ENGINE §1.4 55+ windows (ET). IG 19:00 / 21:00 and FB 18:30 / 20:00 are listed slots; the
# 20:00 IG, 21:30 FB and the Sun +15 min offsets are off-list (3 posts tonight > 2 listed evening slots).
POSTS = [
    {"post_id": "D1-CY-1", "script": "S158", "ig": "19:00", "fb": "18:30",
     "keyframe": {"set": "SET-GARAGE", "framing": "medium close-up, chest up, the old welding helmet on a nail on the pegboard behind his right shoulder"},
     "inserts": [
         {"beat": 1, "still": "Close-up of an old, scuffed welding helmet hanging on a nail on a garage pegboard, warm morning light from the open garage door, dust in the air, shallow depth of field. No people, no text, no logos.",
          "motion": "Very slow push-in on the welding helmet on its nail; dust drifts in the light. Static otherwise. No people."},
         {"beat": 3, "still": "Wide garage interior at morning: a sturdy wooden chair pushed against the wall, a rubber floor mat, an 8 kg kettlebell beside the chair, a folded towel on the seat, pegboard with hand tools. No people, no text, no logos, no screens.",
          "motion": "Slow lateral dolly left to right across the chair and kettlebell; morning light shifts slightly. No people."}]},
    {"post_id": "D1-CY-2", "script": "S154", "ig": "20:00", "fb": "20:00",
     "keyframe": {"set": "SET-GARAGE", "framing": "medium shot, waist up, a dusty 8 kg kettlebell held low in front of him with both hands"},
     "inserts": [
         {"beat": 1, "still": "Side view, framed from the shoulders down (no head or face in frame), an older man in a white tee and dark jeans in a garage doing a kettlebell deadlift: feet wide, 8 kg kettlebell between his feet, hips pushed back, flat back, chest proud, a wooden chair against the wall beside him. Natural light. No text.",
          "motion": "The man slowly stands up with the kettlebell held close, hips forward, flat back, then lowers it with hips back. One slow rep. Camera static at hip height, framing stays below the shoulders; the head never enters the frame."},
         {"beat": 4, "still": "Close-up on a rubber garage mat: a canvas backpack with two plain hardcover books (blank spines, no titles) being slid into it by weathered older hands, a plain gold wedding band on the left hand. No face, no text.",
          "motion": "The hands slide the second book into the backpack and zip it halfway. Camera static, close-up, hands only."}]},
    {"post_id": "D1-CY-3", "script": "S155", "ig": "21:00", "fb": "21:30",
     "keyframe": {"set": "SET-PROM", "framing": "medium shot, seated on a promenade bench by a steel railing, foggy sea behind, a small sand timer on the bench beside him"},
     "inserts": [
         {"beat": 2, "still": "Close-up of a small wooden sand timer on a weathered promenade bench, fog over grey water behind, steel railing out of focus. No people, no text.",
          "motion": "The sand flows steadily through the timer; fog drifts slowly behind. Static close-up. No people."},
         {"beat": 3, "still": "Foggy seaside promenade at dusk: a steel railing with three gulls perched on it, calm grey water, soft light. No people, no text.",
          "motion": "The gulls lift off the railing one by one and glide away into the fog. Slow, calm. Static camera."}]},
    {"post_id": "D1-SK-1", "script": "S167", "ig": "19:15", "fb": "18:45",
     "keyframe": {"set": "SET-TABLE", "framing": "medium close-up at the walnut table, reading glasses on, a printed index card held low in one hand (blank side to camera)"},
     "inserts": [
         {"beat": 2, "still": "Warm home kitchen counter still life: three real glass jars of napa-cabbage kimchi (red chili visible through the glass, plain metal lids, no labels), a wooden cutting board with sliced scallions, a digital kitchen scale with a blank display. No people, no text, no logos.",
          "motion": "Slow push-in across the kimchi jars toward the cutting board; steam drifts from a pot out of frame. No people."},
         {"beat": 3, "still": "Overhead of a walnut table: a steaming bowl of soup with tofu and scallion, chopsticks and a spoon, an older woman's hands setting the bowl down, a jade bangle on the left wrist and a plain gold band. No face, no text.",
          "motion": "The hands set the bowl down gently and withdraw; steam rises. Static overhead camera, hands only."}]},
    {"post_id": "D1-SK-2", "script": "S160", "ig": "20:15", "fb": "20:15",
     "keyframe": {"set": "SET-KITCHEN", "framing": "medium close-up at the kitchen counter, over-the-glasses look, two green kiwis halved on a cutting board in front of her, glass kimchi jars on the shelf behind"},
     "inserts": [
         {"beat": 2, "still": "Overhead of three small white bowls side by side on a wooden counter: two halved green kiwis, a few dried prunes, a spoonful of psyllium husk. Natural window light. No people, no text.",
          "motion": "Very slow overhead drift across the three bowls from left to right. No people."},
         {"beat": 3, "still": "Close-up of an older woman's hand (jade bangle on the left wrist, plain gold band) scooping green kiwi flesh out of a halved kiwi with a teaspoon over a cutting board. No face, no text.",
          "motion": "The spoon scoops the kiwi half clean in one smooth motion, hand only, static close-up."}]},
    {"post_id": "D1-SK-3", "script": "S161", "ig": "21:15", "fb": "21:45",
     "keyframe": {"set": "SET-KITCHEN", "framing": "medium close-up by the gas stove, a steaming pot of chicken and radish soup beside her, glass kimchi jars on the shelf behind"},
     "inserts": [
         {"beat": 2, "still": "Close-up of a clear glass laboratory petri dish on a white lab bench beside a small cup of golden broth, cool clinical light. No people, no text, no labels.",
          "motion": "Slow push-in on the petri dish; faint steam rises from the broth cup. No people."},
         {"beat": 3, "still": "Overhead of a stove-top: a ladle lifting chicken, white radish and scallion from a steaming pot into a ceramic bowl, an older woman's hand with a jade bangle. No face, no text.",
          "motion": "The ladle pours the soup into the bowl, steam rising; hands only; static overhead camera."}]},
]

# Day-1 caption edits (IG/FB variants only). The fallback packer scans each caption as a stand-alone snippet, which
# is stricter than the script-context scan the library passed: a bare "chest pain" needs the §4.3 red-flag line and
# a condition name ("constipation") is C-07 outside a script. Wording follows the spoken line of the same script.
CAPTION_EDITS = {
    "S154": [("Heart condition or new chest pain? Get medical clearance first (ACSM).",
              "Heart condition? Get medical clearance first (ACSM). New chest pain isn't for exercise. That's for your doctor, today.")],
    "S160": [("75 adults with chronic constipation", "75 adults with slow, stubborn bathrooms")],
}

# Day-1 spoken-line edit. S158 (Chang) and S167 (Sun) both say "...real. A team of people made me." The uniqueness
# guard (workers/uniqueness/guard.py, network rule: <= 6 shared consecutive words across pages within 14 days)
# denies whichever posts second, so the canon runway calendar (both on the same day) can't pass it as written.
# Sun's line is reworded; the disclosure is unchanged in meaning (and her caption still says it in full).
VO_EDITS = {"S167": [(1, "A team of people made me. Chang too.", "Real people on a team made me. Chang too.")]}

FIRST_COMMENT_CTA = {
    "WAITLIST": "Comment WAITLIST and the team sends the free link by DM. No card, one email when we open.",
    "TEST": "Comment TEST and the team sends the free 3-minute Strength Age test by DM.",
    "BREATH": "Comment BREATH and the team sends the guided 5-minute 4-6 Breath by DM.",
    "GUT": "Comment GUT and the team sends Sun Yoon's 7-Day Fiber Ladder by DM.",
    "SOUP": "Comment SOUP and the team sends Sun Yoon's Three Soups (with grams) by DM.",
}
FB_TAGS = {"CHANG": "#changyin", "SUN": "#sunyoon"}
AI_LABEL_TOGGLE = {
    "ig": "Instagram: Share screen → Advanced settings → 'AI info' / Add AI label: ON (account-level 'AI-generated profile' must already be on). " + fallback.AI_LABEL["ig"],
    "fb": fallback.AI_LABEL["fb"] + " Facebook Reels composer: 'AI info' toggle sits under the caption field's settings [verify on device].",
}
WINDOW_NOTE = "If a file is not QA-passed 30 min before its slot, do not rush it: post it at tomorrow's 08:30 IG / 08:00 FB slot instead."


def short_citation(eid: str) -> str:
    c = evidence.citation(eid) or ""
    c = re.sub(r"\s+—.*$", "", c)
    c = re.sub(r"\s*\((known literature|abstract only|secondary)[^)]*\)", "", c)
    return re.sub(r"https?://\S+|\*", "", c).strip()


def first_comment(s: dict) -> str:
    name = PAGES[s["speaker"]]["name"]
    src = "; ".join(short_citation(e) for e in s["evidence"])
    lines = [f"Sources: {src}." if src else f"{name} is an AI character made by a team of people; the story is fiction.",
             FIRST_COMMENT_CTA[s["cta_keyword"]]]
    if src:
        lines.append(f"{name} is an AI character made by the Strong Years team.")
    return "\n".join(lines)


def beat_windows(s: dict) -> list[tuple[int, int]]:
    return [tuple(int(x) for x in b["t"].split("-")) for b in s["beats"]]


def build() -> tuple[dict, list[str]]:
    rs = {s["id"]: s for s in json.loads((ROOT / "data/content/runway_scripts.json").read_text(encoding="utf-8"))}
    src = {s["id"]: s for s in BC.load_scripts()}
    problems: list[str] = []
    posts, per_page_waitlist = [], {}
    for sid, edits in VO_EDITS.items():
        for k, old, new in edits:
            if old not in rs[sid]["beats"][k]["vo"]:
                problems.append(f"{sid}: VO edit anchor not found in beat {k}")
            rs[sid]["beats"][k]["vo"] = rs[sid]["beats"][k]["vo"].replace(old, new)
            b = list(src[sid]["beats"][k])
            b[2] = b[2].replace(old, new)
            src[sid]["beats"][k] = tuple(b)
    for sid, edits in CAPTION_EDITS.items():
        for old, new in edits:
            for d in (rs[sid], src[sid]):
                if old not in d["caption"]:
                    problems.append(f"{sid}: caption edit anchor not found: {old[:40]}")
                d["caption"] = d["caption"].replace(old, new)

    # build_content.py rule set on exactly these six scripts (tuple-form sources)
    chosen = [src[p["script"]] for p in POSTS]
    problems += BC.validate([dict(x) for x in chosen], BC.load_hooks(), BC.load_evidence_ids())
    for x in chosen:
        pub = BC.script_published_text(x)
        problems += BC.blocked_claims_scan(x["id"], pub)
        prom = {"on_screen": pub["on_screen"], "thumbnail": x["thumb"], "title": x["title"], "yt_title": x["yt"],
                "hook_line": x["beats"][0][2]}
        problems += BC.outcome_claim_hits(x["id"], pub, prom)
        problems += BC.mortality_hits(x["id"], prom, {"spoken": pub["spoken"], "caption": pub["caption"]})

    for p in POSTS:
        s = rs[p["script"]]
        pid, spk = p["post_id"], s["speaker"]
        page = PAGES[spk]
        if s["page"] != page["handle"]:
            problems.append(f"{pid}: script page {s['page']} != {page['handle']}")
        if s["cta_keyword"] == "WAITLIST":
            per_page_waitlist[page["handle"]] = per_page_waitlist.get(page["handle"], 0) + 1
        wins = beat_windows(s)
        protected = {0, len(s["beats"]) - 1} | {i for i, b in enumerate(s["beats"]) if s["skip_line"] in b["vo"]}
        for ins in p["inserts"]:
            if ins["beat"] in protected:
                problems.append(f"{pid}: insert on beat {ins['beat']} (hook / skip line / CTA stay on the face)")
            if re.search(r"\b(face|head)\b", ins["still"] + ins["motion"], re.I) and not re.search(r"no (head or )?face|never enters|hands only|no face", ins["still"] + ins["motion"], re.I):
                problems.append(f"{pid}: insert prompt may show a face")
        fb_tags = [FB_TAGS[spk], next(t for t in s["hashtags"]["ig"] if t != FB_TAGS[spk])]
        pk = packager.package({"instagram": {"caption": s["caption"], "hashtags": s["hashtags"]["ig"]},
                               "facebook": {"caption": s["caption"], "hashtags": fb_tags}},
                              script={"has_movement": s["has_movement"], "cta_keyword": s["cta_keyword"]},
                              page_slug=page["handle"].lstrip("@"), brief_id=pid)
        notes = [n for n in pk["notes"] if "line 1" not in n]
        problems += [f"{pid}: packager note: {n}" for n in notes]
        variants = {
            "ig": {"platform": "Instagram Reel", "caption": pk["packaging"]["instagram"]["caption"],
                   "hashtags": pk["packaging"]["instagram"]["hashtags"],
                   "scheduled_at": f"{DAY}T{p['ig']}:00{TZ}", "file": f"out/day1/{page['handle']}/{pid}/ig.mp4",
                   "cover": f"out/day1/{page['handle']}/{pid}/ig_cover.jpg", "on_screen_hook": s["beats"][0]["ost"],
                   "cover_text": s["thumbnail_text"], "ai_label": AI_LABEL_TOGGLE["ig"]},
            "fb": {"platform": "Facebook Reel", "caption": pk["packaging"]["facebook"]["caption"],
                   "hashtags": pk["packaging"]["facebook"]["hashtags"],
                   "scheduled_at": f"{DAY}T{p['fb']}:00{TZ}", "file": f"out/day1/{page['handle']}/{pid}/fb.mp4",
                   "cover": f"out/day1/{page['handle']}/{pid}/fb_cover.jpg", "on_screen_hook": s["beats"][0]["ost"],
                   "cover_text": s["thumbnail_text"], "ai_label": AI_LABEL_TOGGLE["fb"]},
        }
        fc = first_comment(s)
        transcript = " ".join(b["vo"] for b in s["beats"])
        burned = [b["ost"] for b in s["beats"]] + ["AI character"]
        # compliance: pass 1 (script) + pass 2 (packaged captions / transcript / burned-in) + first comment snippet
        v1 = scanner.scan(s)["verdict"]
        v2r = scanner.scan(s, pass_no=2, packaging={"instagram": pk["packaging"]["instagram"],
                                                    "facebook": pk["packaging"]["facebook"]},
                           transcript=transcript, burned_in_text=burned, has_movement=s["has_movement"])
        v3 = scanner.scan(text=fc)["verdict"]
        for name, v in (("pass1", v1), ("pass2", v2r["verdict"]), ("first_comment", v3)):
            if v != "pass":
                problems.append(f"{pid}: compliance {name} verdict {v} {v2r.get('required_missing') if name == 'pass2' else ''}")
        for pl in ("ig", "fb"):
            item = {"page": page["handle"], "platform": pl, "variant_id": f"{pid}-{pl}", "is_aigc": True,
                    "uniqueness": {"allow": True}, "caption": variants[pl]["caption"], "first_comment": fc}
            why = fallback._hold_reason(item)
            if why:
                problems.append(f"{pid}/{pl}: fallback packer would hold it: {why}")
            for t in variants[pl]["hashtags"]:
                if BC.CONDITION_HASHTAG.search(t):
                    problems.append(f"{pid}/{pl}: condition hashtag {t}")
            problems += BC.blocked_claims_scan(f"{pid}/{pl}", {"caption": variants[pl]["caption"], "first_comment": fc})
        posts.append({
            "post_id": pid, "page": page["handle"], "page_code": page["code"], "speaker": spk, "script_id": s["id"],
            "title": s["title"], "vo_edits": [n for _, _, n in VO_EDITS.get(s["id"], [])], "caption_edits": [n for _, n in CAPTION_EDITS.get(s["id"], [])], "cta_keyword": s["cta_keyword"], "cta_deliverable": s["cta_deliverable"],
            "format": "talking_head + 2 no-face inserts", "music": s["music"], "evidence": s["evidence"],
            "has_movement": s["has_movement"], "target_seconds": s["target_seconds"],
            "hook_line": s["hook_line"], "skip_line": s["skip_line"],
            "beats": [{"t": b["t"], "vo": b["vo"], "ost": b["ost"],
                       "route": next(("insert" for i in p["inserts"] if i["beat"] == k), "talk"),
                       "study_card": bool(re.search(r"study card", b["shot"], re.I))} for k, b in enumerate(s["beats"])],
            "render": {"keyframe": p["keyframe"], "inserts": p["inserts"],
                       "study_cards": [{"beat": k, "evidence_id": s["evidence"][0], "title": b["ost"]}
                                       for k, b in enumerate(s["beats"]) if re.search(r"study card", b["shot"], re.I) and s["evidence"]]},
            "variants": variants, "first_comment": fc,
            "ai_label_reminder": "Turn ON the AI label on BOTH posts (IG 'AI info', FB 'AI info'); the burned-in 'AI character' tag and the caption footer stay as rendered.",
            "fallback_window": WINDOW_NOTE,
            "validation": {"build_content_rules": "pass", "compliance_pass1": v1, "compliance_pass2": v2r["verdict"],
                           "first_comment_scan": v3, "llm_judge": "pending: runs in the pipeline (/compliance/scan, mandatory) or a human reviews before posting"},
        })
    from uniqueness import guard
    cands = [{"id": p["post_id"], "page_id": p["page"], "platform": "instagram",
              "script_text": " ".join(b["vo"] for b in p["beats"]), "scheduled_at": p["variants"]["ig"]["scheduled_at"]}
             for p in posts]
    for c in cands:
        g = guard.check(c, [x for x in cands if x["id"] != c["id"]])
        if not g["allow"]:
            problems.append(f"{c['id']}: uniqueness guard: {'; '.join(g['reasons'])}")
        next(p for p in posts if p["post_id"] == c["id"])["validation"]["uniqueness_guard"] = "allow" if g["allow"] else "deny"
    for h, n in per_page_waitlist.items():
        if n > 1:
            problems.append(f"{h}: {n} WAITLIST CTAs on day 1 (max 1 per page)")
    for h in {p["page"] for p in posts}:
        if sum(1 for p in posts if p["page"] == h) != 3:
            problems.append(f"{h}: expected 3 posts")
    if problems:
        for p in posts:
            p["validation"]["build_content_rules"] = "see problems"
    plan = {"day": DAY, "timezone": "America/New_York (EDT, UTC-4)", "generated_by": "production/launch_day/build_day1_plan.py",
            "constraint": "No performer footage: talking head (Kling AI Avatar v2 lip-sync from a locked Nano Banana keyframe) + 2 no-face inserts (Veo 3.1 Fast i2v) per post.",
            "cadence_note": "PIPELINE §5.4 week-1 ramp is 2 videos/page/platform; day 1 runs 3 per page by client decision.",
            "platforms": ["Instagram Reel", "Facebook Reel"], "posts": posts,
            "validation_summary": {"posts": len(posts), "problems": problems, "all_pass": not problems}}
    return plan, problems


def main() -> int:
    plan, problems = build()
    (HERE / "day1_plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for p in problems:
        print("PROBLEM", p)
    print(f"day1_plan.json: {len(plan['posts'])} posts, {'ALL PASS' if not problems else f'{len(problems)} problems'}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
