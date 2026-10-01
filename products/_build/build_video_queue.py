"""VIDEO_PRODUCTION_QUEUE.json: every member video (Daily Practice DP01–30, the guided retest RT01, 30 program sessions,
12 Gut Reset kitchen lessons) broken into render shots for the PIPELINE.md stack, plus the performer driving-video shot list
and a cost summary at the three PIPELINE.md §4.1 tiers."""
import os, sys, json, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import PRODUCTS
from library import EX


BREATH = {"cyclic_sigh", "breath_46"}
BED = {"bed_bridge", "pelvic_tilt_bed", "clam_bed", "knee_rock_bed"}
TABLE = {"finger_spread", "fist_flat", "thumb_touch", "wrist_curl", "jar_twist", "hand_stretch", "ball_squeeze", "book_pinch"}
STAIRS = {"stair_climb", "step_up"}
SUN_WARDROBE = {"SET-KITCHEN": "S-KITCHEN", "SET-LIVING": "S-CARDI-JADE", "SET-PROM": "S-WALK", "SET-YARD": "S-WALK", "SET-GARAGE": "S-CARDI-MUSTARD",
                "SET-TABLE": "S-CARDI-JADE", "SET-STOOP": "S-WALK", "SET-BED": "S-BED"}
LOOP_MAX = 20  # seconds of generated motion per variant; the assembler loops it under the VO + rep counter (Kling MC accepts 3–30 s driving clips)

# PIPELINE.md §1.3 / §4.1 unit prices and overgeneration factors
TIERS = {
    "lean": dict(motion=0.07, lipsync=0.008, scene=0.03, voice_per_1k=0.04, keyframe=0.034, per_video=0.10, over=1.3, takes=2,
                 note="Kling 2.6 Std MC; InfiniteTalk self-hosted [A]; Wan/Kling blended scenes [A]"),
    "standard": dict(motion=0.13, lipsync=0.06, scene=0.095, voice_per_1k=0.08, keyframe=0.101, per_video=0.25, over=1.5, takes=3,
                     note="Kling v3 Std MC; InfiniteTalk 720p; Kling v3 Std / Veo 3.1 Fast scenes; NB2 2K keyframes"),
    "premium": dict(motion=0.168, lipsync=0.16, scene=0.35, voice_per_1k=0.08, keyframe=0.134, per_video=0.56, over=2.0, takes=4,
                    note="Kling v3 Pro MC; OmniHuman 1.5; Seedance 2.0 / Veo 3.1; NB Pro keyframes"),
}


def secs(t):
    m, s = t.split(":")
    return int(m) * 60 + int(s)


def shot_set(eid, default):
    if eid in BED:
        return "SET-BED"
    if eid in TABLE:
        return "SET-TABLE"
    if eid in STAIRS:
        return "SET-STOOP"
    return default


DRIVING = {}


def driving_id(eid, version):
    did = f"DRV-{eid}-{version}"
    if did not in DRIVING:
        e = EX[eid]
        how = e["easier"] if version == "easier" else e["harder"] if version == "harder" else " ".join(e["steps"])
        DRIVING[did] = dict(id=did, exercise=eid, name=e["name"], version=version, performer="Performer A (Chang motion double, 60+ strong male)",
                            clip_seconds="10–20", what_to_perform=how, setup=e["setup"], equipment=e["equip"],
                            set_for_blocking=shot_set(eid, "SET-GARAGE"), form_check="M-08: knees over toes, neutral spine on hinges, chair against wall, shoes on, no rugs",
                            used_by=[])
    return did


def priority(vid, program=None, phase=None, week=None):
    if vid.startswith("DP") or vid == "RT01":
        return "P0", "D−10 to D−1 (before go-live)"
    if program == "GUT":
        return ("P1", "launch week 1") if week <= 4 else ("P2", "by launch week 4") if week <= 8 else ("P3", "by launch week 8")
    if phase == 1:
        return ("P0", "D−10 to D−1 (before go-live)") if program in ("S70", "BAL") else ("P1", "launch week 1")
    return ("P2", "by launch week 4") if phase == 2 else ("P3", "by launch week 8")


def queue_item(sess, source, program=None, phase=None):
    vid = sess["id"]
    pr, due = priority(vid, program, phase, sess.get("week"))
    shots, chars = [], 0
    talk = motion = scene = 0
    variants_total = 0
    for g in sess["segments"]:
        a, b = secs(g["start"]), secs(g["end"])
        dur = b - a
        vo_text = " ".join(x["vo"] for x in g["beats"])
        chars += len(vo_text)
        speakers = sorted({x["speaker"] for x in g["beats"]})
        tracks = g.get("tracks")
        base = dict(shot_id=f"{g['id']}", segment=g["name"], t_start=g["start"], t_end=g["end"], duration_s=dur,
                    set_code=sess["set"], wardrobe_code=sess["wardrobe"], speakers=speakers, vo_text=vo_text,
                    on_screen=[x["ost"] for x in g["beats"] if x["ost"]], caption_burn_in=True)
        if "SUN" in speakers:
            base["sun_wardrobe_code"] = SUN_WARDROBE.get(sess["set"], "S-CARDI-JADE")
        if tracks and not all(tracks[t]["exercise"] in BREATH for t in tracks):
            variants = {}
            for tr, x in tracks.items():
                key = (x["exercise"], x["version"])
                variants.setdefault(key, []).append(tr)
            loop = min(LOOP_MAX, dur)
            var_out = []
            for (eid, ver), trs in variants.items():
                did = driving_id(eid, ver)
                DRIVING[did]["used_by"].append(g["id"])
                var_out.append(dict(tracks=trs, exercise=eid, version=ver, driving_clip_id=did, generated_loop_s=loop,
                                    set_code=shot_set(eid, sess["set"]), wardrobe_code=("C-BED" if eid in BED else sess["wardrobe"]),
                                    doses={t: tracks[t]["dose"] for t in trs}, advanced_label=any(tracks[t]["advanced"] for t in trs)))
            motion += loop * len(variants)
            variants_total += len(variants)
            base.update(render_mode="performer_driving_video", provider="Kling 3.0 Motion Control + performer driving clip (PIPELINE §1.3)",
                        voice="voice-over (no lip-sync) + 2–3 s talking-head insert if the character addresses camera", variants=var_out,
                        assembly="loop generated clip to segment length; overlay rep counter, track panel, 'Easier:' card; audio = VO + library music bed",
                        qa="M-08 human form review on every variant before publish")
            talk += min(3, dur)
        elif g["kind"] == "kitchen_demo":
            base.update(render_mode="gen_scene_food_plus_talking_head", provider="Kling v3 Std / Veo 3.1 Fast i2v food shots + InfiniteTalk inserts",
                        food_shots=[dict(step=i + 1, text=x["vo"], seconds=6) for i, x in enumerate(g["beats"][1:-1])])
            scene += min(dur, 6 * max(1, len(g["beats"]) - 2))
            talk += max(0, dur - 6 * max(1, len(g["beats"]) - 2))
        else:
            mode = "talking_head_seated_breath" if tracks else "talking_head"
            base.update(render_mode=mode, provider="ElevenLabs v3 + InfiniteTalk lip-sync on a reference-locked keyframe (PIPELINE §1.3)")
            talk += dur
        shots.append(base)
    item = dict(video_id=vid, source=source, program=program, title=sess["title"], type=sess["type"], priority=pr, due=due,
                duration_s=sess["duration_s"], duration=sess["duration"], set_code=sess["set"], wardrobe_code=sess["wardrobe"],
                speakers=sess["speakers"], track_outputs=(["rebuild", "steady", "strong", "iron"] if sess.get("has_movement", True) else ["all"]),
                corner_tag="AI character", c2pa=True, captions=True, caption_footer=sess.get("caption_footer"),
                movement_addon=sess.get("caption_movement_addon"), evidence=sess.get("evidence", []),
                seconds=dict(talking_head_lipsync=talk, generated_motion=motion, generated_scene=scene, voice_chars=chars,
                             keyframes=len(shots) + variants_total), shots=shots)
    return item


def cost(item, tier):
    T = TIERS[tier]
    s = item["seconds"]
    return (s["generated_motion"] * T["motion"] * T["over"] + s["talking_head_lipsync"] * T["lipsync"] * T["over"]
            + s["generated_scene"] * T["scene"] * T["over"] + s["voice_chars"] / 1000 * T["voice_per_1k"] * T["takes"]
            + s["keyframes"] * T["keyframe"] * T["over"] + T["per_video"])


def build():
    global S, PG
    S = json.load(open(os.path.join(PRODUCTS, "sessions.json")))
    PG = json.load(open(os.path.join(PRODUCTS, "programs.json")))
    DRIVING.clear()
    items = [queue_item(x, "sessions.json") for x in S["sessions"]]
    items += [queue_item(x, "sessions.json") for x in S.get("guided_tests", [])]
    for p in PG["programs"]:
        for x in p["sessions"]:
            items.append(queue_item(x, "programs.json", program=p["id"], phase=x.get("phase")))
    for it in items:
        it["est_cost_usd"] = {t: round(cost(it, t), 2) for t in TIERS}
    tot = lambda k: sum(i["seconds"][k] for i in items)
    by_pr = {}
    for it in items:
        d = by_pr.setdefault(it["priority"], dict(videos=0, minutes=0.0, standard_usd=0.0))
        d["videos"] += 1
        d["minutes"] += it["duration_s"] / 60
        d["standard_usd"] += it["est_cost_usd"]["standard"]
    for d in by_pr.values():
        d["minutes"] = round(d["minutes"], 1)
        d["standard_usd"] = round(d["standard_usd"], 2)
    runtime = sum(i["duration_s"] for i in items) / 60
    outputs = sum(i["duration_s"] * len(i["track_outputs"]) for i in items) / 60
    summary = dict(
        videos=len(items), by_source=dict(daily_practice=sum(1 for i in items if i["video_id"].startswith("DP")), guided_retest=1,
                                          program_sessions=sum(1 for i in items if i["program"] and i["program"] != "GUT"),
                                          gut_kitchen_lessons=sum(1 for i in items if i["program"] == "GUT")),
        base_runtime_minutes=round(runtime, 1), published_output_minutes_all_tracks=round(outputs, 1),
        generated_motion_seconds=tot("generated_motion"), talking_head_lipsync_seconds=tot("talking_head_lipsync"),
        generated_scene_seconds=tot("generated_scene"), voice_characters=tot("voice_chars"),
        unique_driving_clips=len(DRIVING),
        est_cost_usd={t: round(sum(i["est_cost_usd"][t] for i in items), 2) for t in TIERS},
        recommended_tier="standard for all member videos (product quality is retention); premium only for DP01 and the welcome video",
        by_priority=dict(sorted(by_pr.items())),
        performer_shoot=f"{len(DRIVING)} driving clips of 10–20 s each. At PIPELINE.md D6 pace (4 h → 150–250 clips) this is one shoot day with a 60+ strong performer; add a form reviewer on set.",
        assumptions=[
            "Unit prices and overgeneration factors are PIPELINE.md §1.3/§4.1 (Sept 2026). [A] items there remain assumptions.",
            f"Each distinct exercise variant is generated once as a ≤{LOOP_MAX} s loop from a performer driving clip; the Remotion/ffmpeg assembler loops it to segment length under the VO, rep counter and track panel. Continuous 2–4 minute walking segments reuse one loop plus library B-roll.",
            "Talk segments and breath segments are lip-synced full-length; movement segments are voice-over with a ~3 s talking insert.",
            "Four track outputs per session are assembled from the same shots (no extra generation); cost of assembly compute is inside the per-video LLM+QA+assembly line.",
            "Voice = ElevenLabs v3 at API rates × takes; keyframes = one per shot and one per motion variant.",
            "Excludes the one-time performer shoot ($1.5–3K, PIPELINE §4), cultural review, and human form review labour (M-08).",
        ])
    # reuse: one generated loop per (exercise, version, set, wardrobe) across all videos
    uniq = {}
    for it in items:
        for sh in it["shots"]:
            for v in sh.get("variants", []):
                k = (v["exercise"], v["version"], v["set_code"], v["wardrobe_code"])
                uniq[k] = max(uniq.get(k, 0), v["generated_loop_s"])
    reuse_motion = sum(uniq.values())
    saved = tot("generated_motion") - reuse_motion
    summary["with_loop_reuse"] = dict(unique_motion_loops=len(uniq), generated_motion_seconds=reuse_motion,
                                      est_cost_usd={t: round(summary["est_cost_usd"][t] - saved * TIERS[t]["motion"] * TIERS[t]["over"], 2) for t in TIERS},
                                      note="Loops keyed by exercise × version × set × wardrobe are rendered once and reused by every session that uses them (the queue marks them via driving_clip_id).")
    q = dict(version="2026-09-30", consumer="n8n W4/W5 render workers (PIPELINE.md): one job per video_id; shots → keyframes → motion_transfer | lipsync_talk | gen_scene → assemble per track → QA (ArcFace, SyncNet, EBU R128, OCR, vision-LLM, M-08 human form review) → upload to member library (not social publish).",
             summary=summary, tiers=TIERS, driving_clip_shotlist=sorted(DRIVING.values(), key=lambda d: d["id"]), queue=items)
    out = os.path.join(PRODUCTS, "VIDEO_PRODUCTION_QUEUE.json")
    json.dump(q, open(out, "w"), indent=1, ensure_ascii=False)
    return out, summary


if __name__ == "__main__":
    out, s = build()
    print(out)
    print(json.dumps(s, indent=1)[:2500])
