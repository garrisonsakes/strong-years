"""POST /variants: per-platform renders from the master (L1 packaging variants, PIPELINE §2.3).

Each variant: platform-native on-screen hook burned in for the first 2.4 s inside that platform's safe zone,
trimmed to the platform's max length, a cover image with the cover text, then re-signed with C2PA.
Renders from the assembler's clean mezzanine (<master>_clean.mp4: captions + AI tag, no script hook) when it exists,
so the platform hook never stacks on top of the script hook.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from assemble import c2pa_sign
from assemble.layout import H, W, safe_zone
from assemble.overlay import draw_ai_tag, draw_text_block
from common import config, media, storage, supabase


PLATFORMS = {"instagram", "tiktok", "youtube", "facebook", "threads", "x"}


def _clean_source(master_url: str, jobdir: Path) -> tuple[Path, bool]:
    if master_url.endswith(".mp4"):
        try:
            return storage.fetch(master_url[:-4] + "_clean.mp4", jobdir), True
        except Exception:
            pass
    return storage.fetch(master_url, jobdir), False


def hook_png(text: str, platform: str, safe: dict | None, out: Path) -> Path:
    z = safe_zone(platform, safe)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_text_block(img, text.split(), size=78, fill="#FFF6E5", pill="#111111", pill_alpha=0.9, center_x=z.center_x,
                    max_w=z.width, anchor_y=z.top + 90, anchor="top", max_lines=3, min_size=60)
    img.save(out)
    return out


def cover(video: Path, text: str | None, platform: str, safe: dict | None, out: Path, t: float = 1.0) -> Path:
    fr = media.extract_frame(video, t, out.with_suffix(".src.jpg"))
    img = Image.open(fr).convert("RGBA").resize((W, H))
    if text:
        z = safe_zone(platform, safe)
        draw_text_block(img, text.split(), size=110, fill="#FFFFFF", pill="#111111", pill_alpha=0.92,
                        center_x=z.center_x, max_w=z.width, anchor_y=int(H * 0.38), anchor="top", max_lines=3,
                        min_size=72)
    draw_ai_tag(img, "AI character", safe_zone(platform, safe))
    img.convert("RGB").save(out, quality=92)
    return out


def render_variants(req: dict, workdir: Path | None = None) -> dict:
    config.ensure_dirs()
    vid = storage.safe_id(req.get("video_id") or storage.new_id(), "video_id")   # AUDIT H9
    jobdir = Path(workdir or config.WORK_DIR) / f"var_{vid}"
    jobdir.mkdir(parents=True, exist_ok=True)
    src, used_clean = _clean_source(req["master_url"], jobdir)
    master_dur = media.duration(src)
    results = []
    for v in req.get("variants") or []:
        pl = v["platform"]
        if pl not in PLATFORMS:
            raise ValueError(f"unknown platform {pl!r}")
        if not v.get("render", True):
            results.append({"platform": pl, "rendered": False, "asset_id": None, "reason": "text-only post"})
            continue
        safe = v.get("safe_zone") or None
        dur = min(master_dur, float(v.get("max_s") or master_dur))
        out_raw = jobdir / f"{pl}_raw.mp4"
        args = ["-i", str(src)]
        hook = v.get("on_screen_hook")
        if hook and used_clean:
            hp = hook_png(hook, pl, safe, jobdir / f"{pl}_hook.png")
            args += ["-loop", "1", "-framerate", "30", "-t", "2.4", "-i", str(hp)]
            fc = "[0:v][1:v]overlay=0:0:eof_action=pass:enable='lte(t,2.4)',format=yuv420p[v]"
            vmap = ["-filter_complex", fc, "-map", "[v]", "-map", "0:a?"]
        else:
            vmap = ["-map", "0:v", "-map", "0:a?"]
        media.ffmpeg([*args, *vmap, "-t", f"{dur:.3f}", "-c:v", "libx264", "-profile:v", "high", "-preset",
                      "superfast" if config.X264_PRESET == "ultrafast" else config.X264_PRESET, "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k",
                      "-ar", "48000", "-movflags", "+faststart", str(out_raw)])
        signed = jobdir / f"{pl}.mp4"
        c2 = c2pa_sign.sign(out_raw, signed, title=f"{vid}-{pl}.mp4")
        final = signed if signed.exists() else out_raw
        asset_id = storage.new_id()
        pub = storage.publish(final, f"variants/{vid}/{pl}_{asset_id}.mp4", "video/mp4")
        cv = cover(final, v.get("cover_text"), pl, safe, jobdir / f"{pl}_cover.jpg")
        cpub = storage.publish(cv, f"variants/{vid}/{pl}_{asset_id}_cover.jpg", "image/jpeg")
        registered = False
        if supabase.enabled():  # pragma: no cover - variants.asset_id is an FK to assets(id)
            try:
                supabase.insert("assets", {"id": asset_id, "kind": "variant", "storage_key": pub["storage_key"],
                                           "public_url": pub["url"], "mime": "video/mp4", "bytes": pub["bytes"],
                                           "sha256": pub["sha256"], "c2pa": c2, "tags": ["variant", pl]})
                registered = True
            except Exception:
                registered = False
        results.append({"platform": pl, "rendered": True, "asset_id": asset_id, "asset_registered": registered,
                        "url": pub["url"],
                        "storage_key": pub["storage_key"], "duration_s": round(media.duration(final), 3),
                        "cover_url": cpub["url"], "hook_burned": bool(hook and used_clean),
                        "trimmed": dur < master_dur - 0.05, "c2pa": c2, "sha256": pub["sha256"]})
    return {"video_id": vid, "source": "clean_mezzanine" if used_clean else "master", "variants": results}
