"""First 150 render jobs from the recipe (VIDEO_RE §9.2–9.3 routing) over products/VIDEO_PRODUCTION_QUEUE.json, in
priority order (P0 first, queue order, shot order). One job per (shot, variant) for motion shots, one per shot
otherwise. Each job names the model chain, the locked reference images (production/refs/manifest.json) and, for
exercises, the performer driving clip. Writes render_jobs_first150.json and .csv. Renders nothing.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIMIT = 150
PRIO = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def ref_index() -> dict:
    man = json.loads((ROOT / "production/refs/manifest.json").read_text(encoding="utf-8"))
    idx: dict[tuple[str, str], list[str]] = {}
    for it in man["items"]:
        if it["character"] in ("chang", "sun"):
            idx.setdefault((it["character"], it["wardrobe_code"]), []).append(it["id"])
    return idx


def refs_for(speakers: list[str], wardrobe: str, idx: dict) -> list[str]:
    out = []
    for sp in speakers or ["CHANG"]:
        who = "sun" if sp.upper().startswith("SUN") else "chang"
        face = ["S01", "S02"] if who == "sun" else ["C01", "C02"]
        body = [r for r in idx.get((who, wardrobe), []) if r not in face][:1]
        out += face + body
    return out[:5]


def chain(mode: str) -> list[str]:
    if mode == "performer_driving_video":
        return ["keyframe: Nano Banana 2, pose-matched to driving-clip frame 1 + face/wardrobe refs + set plate",
                "motion: Kling 3.0 Motion Control (Std) with the performer driving clip",
                "form QA: pose-angle check vs the driving clip (<=12 deg, rep count equal)",
                "assembly: loop to segment, rep counter, VO by Chang to the real rep timing"]
    if mode.startswith("talking_head"):
        return ["keyframe: Nano Banana 2 reference-locked (never text-to-video a face)",
                "voice: ElevenLabs v3, locked voice_id",
                "lip-sync: InfiniteTalk audio-driven from the final VO"]
    if mode.startswith("gen_scene"):
        return ["keyframe: Nano Banana 2 food/scene keyframe", "motion: Veo 3.1 image-to-video 4-8 s (liquids, steam)",
                "talking insert: InfiniteTalk on a locked keyframe"]
    return ["assembler graphics"]


def build() -> list[dict]:
    q = json.loads((ROOT / "products/VIDEO_PRODUCTION_QUEUE.json").read_text(encoding="utf-8"))
    idx = ref_index()
    videos = sorted(enumerate(q["queue"]), key=lambda t: (PRIO.get(t[1].get("priority"), 9), t[0]))
    jobs = []
    for _, v in videos:
        for s in v["shots"]:
            variants = s.get("variants") or [None]
            for var in variants:
                if len(jobs) >= LIMIT:
                    return jobs
                wardrobe = (var or {}).get("wardrobe_code") or s.get("wardrobe_code") or v.get("wardrobe_code")
                setc = (var or {}).get("set_code") or s.get("set_code") or v.get("set_code")
                jid = f"{s['shot_id']}" + (f"-{var['exercise']}-{var['version']}" if var else "")
                jobs.append({
                    "job_id": jid, "video_id": v["video_id"], "video_title": v["title"], "priority": v["priority"],
                    "due": v.get("due"), "shot_id": s["shot_id"], "segment": s.get("segment"), "render_mode": s["render_mode"],
                    "duration_s": s.get("duration_s"), "set_code": setc, "wardrobe_code": wardrobe,
                    "speakers": s.get("speakers"), "refs": refs_for(s.get("speakers") or [], wardrobe, idx),
                    "set_plate": f"PLATE-{setc}", "driving_clip_id": (var or {}).get("driving_clip_id"),
                    "generated_loop_s": (var or {}).get("generated_loop_s"), "chain": chain(s["render_mode"]),
                    "vo_text": s.get("vo_text", ""), "on_screen": s.get("on_screen", []),
                    "ai_tag": v.get("corner_tag", "AI character"), "c2pa": True, "status": "queued (not rendered)"})
    return jobs


if __name__ == "__main__":
    jobs = build()
    (HERE / "render_jobs_first150.json").write_text(json.dumps({"count": len(jobs), "jobs": jobs}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (HERE / "render_jobs_first150.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["job_id", "priority", "video_id", "shot_id", "render_mode", "duration_s", "set_code", "wardrobe_code", "refs", "driving_clip_id", "due"])
        for j in jobs:
            w.writerow([j["job_id"], j["priority"], j["video_id"], j["shot_id"], j["render_mode"], j["duration_s"], j["set_code"],
                        j["wardrobe_code"], " ".join(j["refs"]), j["driving_clip_id"] or "", j["due"]])
    print(len(jobs), "jobs")
