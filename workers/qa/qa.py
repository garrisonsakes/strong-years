"""POST /qa: deterministic QA of a rendered master (n8n 'Worker: Deterministic QA').

Request (as sent by n8n): {video_url, asset_id, reference_urls, expected_on_screen, script_text, shot_map, checks,
frames} plus optional platform, duration_bounds, ai_tag, context{trusted, risk_tier, attempts, vision_decision}.
Response: {metrics, frames:[{t,url}], decision, reasons, route, checks:{name: ok|skipped|error}, skipped:{...}}
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from assemble import c2pa_sign
from assemble.assembler import frame_times
from common import config, media, storage
from qa import face, ocr, probes, scoring

ALL_CHECKS = ["ffprobe", "ebur128", "blackdetect", "freezedetect", "ocr_captions", "ai_tag", "duration", "c2pa",
              "face_arcface", "syncnet"]


def run(req: dict, workdir: Path | None = None) -> dict:
    config.ensure_dirs()
    aid = storage.safe_id(req.get("asset_id") or storage.new_id(), "asset_id")   # AUDIT H9: no traversal
    req = {**req, "asset_id": aid}
    job = storage.confine(Path(workdir or config.WORK_DIR), f"qa_{aid}")
    job.mkdir(parents=True, exist_ok=True)
    video = storage.fetch(req["video_url"], job)
    checks = set(req.get("checks") or ALL_CHECKS) | {"ffprobe", "duration", "ai_tag"}
    platform = req.get("platform", "master")
    status, skipped, m = {}, {}, {}

    m.update(probes.spec(video))
    status["ffprobe"] = "ok"
    m.update(probes.duration_check(m["duration_s"], platform, req.get("duration_bounds")))
    status["duration"] = "ok"
    if "ebur128" in checks:
        m.update(probes.loudness(video))
        status["ebur128"] = "ok"
    if checks & {"blackdetect", "freezedetect"}:
        bf = probes.black_freeze(video)
        # 'graphic' shots are intentionally still (cards, timers): freezes fully inside them are expected.
        still = [(float(s.get("start_s", 0)), float(s.get("start_s", 0)) + float(s.get("duration_s", 0)))
                 for s in (req.get("shot_map") or []) if s.get("route") == "graphic"]
        if still:
            inside = [f for f in bf["freeze_segments"]
                      if any(a - 0.1 <= f["start"] and f["start"] + f["dur"] <= b + 0.1 for a, b in still)]
            bf["freeze_segments"] = [f for f in bf["freeze_segments"] if f not in inside]
            bf["freeze_in_graphics"] = inside
            bf["freeze_max_s"] = round(max([f["dur"] for f in bf["freeze_segments"]], default=0.0), 3)
        m.update({k: v for k, v in bf.items() if not k.startswith("_")})
        status["blackdetect"] = status["freezedetect"] = "ok"

    # frames for vision QA (12 by default) + dense OCR samples (every 1 s)
    dur = m["duration_s"]
    frame_list = []
    for k, t in enumerate(frame_times(dur, int(req.get("frames", 12)))):
        p = media.extract_frame(video, t, job / f"vqa_{k:02d}.jpg")
        frame_list.append({"t": t, "path": p,
                           "url": storage.publish(p, f"qa/{req.get('asset_id') or job.name}/vqa_{k:02d}.jpg", "image/jpeg")["url"]})
    if ocr.available() and checks & {"ocr_captions", "ai_tag"}:
        ocr_frames = []
        t = 0.6
        while t < dur - 0.2:
            p = media.extract_frame(video, t, job / f"ocr_{int(t * 10):05d}.png")
            ocr_frames.append((round(t, 2), Image.open(p).convert("RGB")))
            t += float(req.get("ocr_step_s", 1.0))
        if "ocr_captions" in checks:
            m.update(ocr.caption_check(ocr_frames, req.get("script_text") or "", req.get("expected_on_screen"), platform))
            status["ocr_captions"] = "ok"
        tag = req.get("ai_tag", "AI character")
        picks = [ocr_frames[i] for i in sorted({0, len(ocr_frames) // 2, len(ocr_frames) - 1})] if ocr_frames else []
        hits = [ocr.ai_tag_present(ocr.ai_tag_text(im, platform), tag) for _, im in picks]
        m["ai_tag_present"] = bool(hits) and all(hits)
        m["ai_tag_frames_checked"] = len(hits)
        status["ai_tag"] = "ok"
    else:
        skipped["ocr_captions"] = skipped["ai_tag"] = "tesseract not installed"
        m["caption_cer"] = None

    if "c2pa" in checks:
        info = c2pa_sign.read(video)
        m["c2pa_present"] = info.get("present")
        m["c2pa_ai_generated"] = info.get("ai_generated")
        m["c2pa_trusted"] = info.get("trusted")
        status["c2pa"] = "ok" if info.get("present") is not None else "skipped"

    if "face_arcface" in checks:
        refs = [storage.fetch(u, job) for u in (req.get("reference_urls") or [])]
        fr = face.face_similarity([f["path"] for f in frame_list], refs)
        m.update({k: v for k, v in fr.items() if k.startswith("face_sim")})
        if fr.get("face_status") != "ok":
            skipped["face_arcface"] = fr.get("face_reason") or fr.get("face_status")
        status["face_arcface"] = fr.get("face_status")
    if "syncnet" in checks:
        sn = face.syncnet(video)
        m.update({k: v for k, v in sn.items() if k in ("syncnet_conf", "syncnet_dist")})
        skipped["syncnet"] = sn["syncnet_reason"]
        status["syncnet"] = sn["syncnet_status"]

    ctx = req.get("context") or {}
    sc = scoring.score(m, vision_decision=ctx.get("vision_decision"), trusted=bool(ctx.get("trusted")),
                       risk_tier=ctx.get("risk_tier", "green"), attempts=int(ctx.get("attempts", 1)),
                       uniqueness_allow=ctx.get("uniqueness_allow", True), judge_passed=ctx.get("judge_passed"),
                       require_judge=config.REQUIRE_JUDGE)
    return {"asset_id": req.get("asset_id"), "metrics": m,
            "frames": [{"t": f["t"], "url": f["url"]} for f in frame_list],
            "decision": sc["decision"], "deterministic_decision": sc["deterministic"], "reasons": sc["reasons"],
            "route": sc["route"], "route_label": sc["route_label"], "checks": status, "skipped": skipped}
