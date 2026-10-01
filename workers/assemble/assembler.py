"""POST /assemble: timeline + voice + word timings -> 1080x1920 30 fps H.264 High master, AAC 48 kHz, −14 LUFS,
burned-in word-by-word captions, AI corner tag, optional PiP insets and study cards, ducked music, C2PA signed.

Accepts the manifest built by the n8n node 'Build Assembly Manifest' unchanged, plus optional keys:
  locale, platform (safe-zone preset), ai_tag, pip:[{src,start_s,end_s,position}], study_cards:[{title,evidence_id,
  citation?,start_s,end_s}], music.url
Returns what 'Save Video + QA' / 'Worker: Deterministic QA' / 'Build QA Vision Request' read:
  asset_id, master_url, duration_s, transcript, words, phash_seq, audio_fp, c2pa, frames, burned_in_text, ...
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from assemble import c2pa_sign, graphics
from assemble import captions as C
from assemble.layout import FPS, H, W, safe_zone
from assemble.overlay import CaptionStyle, OverlayPlan, burned_in_strings, render_track
from common import config, disclosure, evidence, media, storage, supabase
from uniqueness import audiofp, phash

FULL_LAYOUTS = {None, "", "full", "split"}
PIP_LAYOUTS = {"pip_top", "pip_bottom", "pip"}
COVER = "scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h},setsar=1"


class AssemblyError(ValueError):
    pass


def _resolve(src, jobdir: Path, tag: str) -> Path:
    if isinstance(src, str):
        return storage.fetch(src, jobdir)
    if not isinstance(src, dict):
        raise AssemblyError(f"bad media source for {tag}: {src!r}")
    if src.get("url"):
        return storage.fetch(src["url"], jobdir)
    if src.get("graphic"):
        return graphics.render_graphic(src["graphic"], jobdir / f"{tag}_graphic.png")
    if src.get("color"):
        return graphics.colour_card(src["color"], src.get("label", ""), jobdir / f"{tag}_card.png")
    if src.get("asset_id"):
        url = supabase.asset_url(src["asset_id"]) if supabase.enabled() else None
        if not url:
            raise AssemblyError(f"library asset {src['asset_id']} cannot be resolved (set SUPABASE_URL/SUPABASE_SERVICE_KEY)")
        return storage.fetch(url, jobdir)
    raise AssemblyError(f"unsupported media source for {tag}: {src!r}")


def _motion_filter(camera: str, dur: float, still: bool) -> str:
    frames = max(1, int(round(dur * FPS)))
    if still and camera != "static":
        if camera in ("handheld_micro", "handheld"):
            return (COVER.format(w=W + 60, h=H + 106) +
                    f",crop={W}:{H}:x='30+22*sin(2*PI*t/3.1)':y='53+30*sin(2*PI*t/4.3)'")
        # slow push (default for stills so graphics never read as frozen frames)
        return (COVER.format(w=W * 2, h=H * 2) +
                f",zoompan=z='1+0.07*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}")
    if camera in ("handheld_micro", "handheld"):
        return COVER.format(w=W + 40, h=H + 70) + f",crop={W}:{H}:x='20+14*sin(2*PI*t/3.1)':y='35+20*sin(2*PI*t/4.3)'"
    if camera == "slow_push":
        return COVER.format(w=W, h=H) + f",scale=w='trunc({W}*(1+0.05*t/{max(dur, 0.1):.3f})/2)*2':h=-2:eval=frame,crop={W}:{H}"
    return COVER.format(w=W, h=H)


def encode_segment(src: Path, dur: float, camera: str, out: Path) -> Path:
    still = media.is_image(src)
    inp = ["-loop", "1", "-framerate", str(FPS), "-t", f"{dur:.3f}", "-i", str(src)] if still else \
          ["-stream_loop", "-1", "-t", f"{dur:.3f}", "-i", str(src)]
    vf = _motion_filter(camera, dur, still) + f",fps={FPS},format=yuv420p"
    media.ffmpeg([*inp, "-vf", vf, "-an", "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                  "-pix_fmt", "yuv420p", "-r", str(FPS), str(out)])
    return out


def plan_timeline(timeline: list[dict], total: float) -> tuple[list[dict], list[dict], list[str]]:
    """Split shots into contiguous base segments and PiP overlays. Returns (base, pips, warnings)."""
    warns: list[str] = []
    shots = sorted(timeline, key=lambda s: float(s.get("start_s", 0)))
    full = [s for s in shots if (s.get("layout") or "full") not in PIP_LAYOUTS]
    pips = [s for s in shots if (s.get("layout") or "full") in PIP_LAYOUTS]
    if not full:
        raise AssemblyError("timeline has no full-frame shot")
    base = []
    for k, s in enumerate(full):
        a = 0.0 if k == 0 else float(s.get("start_s", 0))
        b = float(full[k + 1].get("start_s", 0)) if k + 1 < len(full) else total
        if b - a < 1 / FPS:
            warns.append(f"shot {s.get('n')} has no screen time; skipped")
            continue
        if s.get("layout") == "split":
            warns.append(f"shot {s.get('n')}: 'split' layout rendered full-frame (split not implemented)")
        base.append({**s, "_a": a, "_b": b})
    overlays = []
    for s in pips:
        a = float(s.get("start_s", 0))
        overlays.append({"n": s.get("n"), "src": s.get("src"), "start_s": a,
                         "end_s": min(total, a + float(s.get("duration_s", 0))),
                         "position": "top_right" if s.get("layout") in ("pip_top", "pip") else "bottom_left",
                         "graphic": (s.get("src") or {}).get("graphic") if isinstance(s.get("src"), dict) else None})
    return base, overlays, warns


def mix_audio(voice: Path | None, music: Path | None, total: float, gain_db: float, jobdir: Path) -> Path:
    """voice + music ducked under voice (sidechain) -> loudnorm two-pass to −14 LUFS / −1.5 dBTP, 48 kHz stereo."""
    mix = jobdir / "mix.wav"
    fmt = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
    if voice is None and music is None:
        media.ffmpeg(["-f", "lavfi", "-t", f"{total:.3f}", "-i", "anullsrc=r=48000:cl=stereo", str(mix)])
        return mix
    args, fc = [], []
    if voice is not None:
        args += ["-i", str(voice)]
    if music is not None:
        args += ["-stream_loop", "-1", "-i", str(music)]
    if voice is not None and music is not None:
        fade_out = max(0.0, total - 1.2)
        fc = [f"[0:a]{fmt},apad=whole_dur={total:.3f},asplit=2[v1][v2]",
              f"[1:a]{fmt},atrim=0:{total:.3f},volume={gain_db}dB,afade=t=in:d=0.8,afade=t=out:st={fade_out:.3f}:d=1.2[m]",
              "[m][v2]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=350[md]",
              "[v1][md]amix=inputs=2:duration=first:normalize=0[out]"]
    elif voice is not None:
        fc = [f"[0:a]{fmt},apad=whole_dur={total:.3f}[out]"]
    else:
        fc = [f"[0:a]{fmt},atrim=0:{total:.3f},volume={gain_db}dB[out]"]
    media.ffmpeg([*args, "-filter_complex", ";".join(fc), "-map", "[out]", "-t", f"{total:.3f}", "-c:a", "pcm_f32le", str(mix)])
    return loudnorm(mix, jobdir / "mix_norm.wav")


def loudnorm(src: Path, out: Path, target: float = -14.0, tp: float = -1.5, lra: float = 11.0) -> Path:
    p = media.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(src), "-af",
                   f"loudnorm=I={target}:TP={tp}:LRA={lra}:print_format=json", "-f", "null", "-"])
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr, re.S)
    if not m:
        raise AssemblyError("loudnorm measurement failed")
    j = json.loads(m.group(0))
    if j["input_i"] in ("-inf", "inf"):
        media.ffmpeg(["-i", str(src), "-ar", "48000", "-c:a", "pcm_s16le", str(out)])
        return out
    af = (f"loudnorm=I={target}:TP={tp}:LRA={lra}:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,"
          "aresample=48000")
    media.ffmpeg(["-i", str(src), "-af", af, "-ar", "48000", "-c:a", "pcm_s16le", str(out)])
    return out


def frame_times(total: float, n: int = 12) -> list[float]:
    """First 0.5 s, the last frame, and evenly spaced (~every 3 s) in between (prompts/07)."""
    if n <= 2:
        return [0.5, max(0.0, total - 0.1)][:n]
    inner = [round(0.5 + (total - 0.6) * k / (n - 1), 2) for k in range(1, n - 1)]
    return [0.5, *inner, round(max(0.0, total - 0.1), 2)]


def assemble(manifest: dict, workdir: Path | None = None) -> dict:
    t0 = time.time()
    config.ensure_dirs()
    asset_id = storage.new_id()
    brief = storage.safe_id(manifest.get("brief_id") or "adhoc", "brief_id")   # AUDIT H9: no traversal
    jobdir = Path(workdir or config.WORK_DIR) / f"asm_{asset_id}"
    jobdir.mkdir(parents=True, exist_ok=True)
    locale = manifest.get("locale") or "en-US"
    warns: list[str] = []

    ai_tag = manifest.get("ai_tag", disclosure.ai_tag(locale))
    if not ai_tag:
        raise AssemblyError("SAFETY_RULES D-02: the burned-in AI corner tag is required on every video")

    voice = storage.fetch(manifest["voice_track"], jobdir) if manifest.get("voice_track") else None
    voice_dur = media.duration(voice) if voice else 0.0
    timeline = manifest.get("timeline") or []
    tl_end = max((float(s.get("start_s", 0)) + float(s.get("duration_s", 0)) for s in timeline), default=0.0)
    total = round(max(tl_end, voice_dur + 0.4), 3)
    if total <= 0:
        raise AssemblyError("empty timeline and no voice")

    # 1) base video
    base, pips, w = plan_timeline(timeline, total)
    warns += w
    segs = []
    for k, s in enumerate(base):
        src = _resolve(s["src"], jobdir, f"shot{s.get('n', k)}")
        segs.append(encode_segment(src, s["_b"] - s["_a"], s.get("camera") or "static", jobdir / f"seg_{k:02d}.mp4"))
    concat = jobdir / "segments.txt"
    concat.write_text("".join(f"file '{p.name}'\n" for p in segs))
    base_mp4 = jobdir / "base.mp4"
    media.ffmpeg(["-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(base_mp4)])

    # 2) overlays (captions, text, study cards, AI tag): full + clean (no hook) tracks
    cap = manifest.get("captions") or {}
    style = CaptionStyle.from_manifest(cap)
    zone = safe_zone(manifest.get("platform", "master"),
                     {k: v for k, v in (("top_pct", cap.get("safe_top_pct")), ("bottom_pct", cap.get("safe_bottom_pct")))
                      if v is not None})
    cards = []
    for sc in manifest.get("study_cards") or []:
        cit = evidence.citation(sc.get("evidence_id")) or sc.get("citation") or ""
        if sc.get("evidence_id") and not evidence.citation(sc.get("evidence_id")):
            warns.append(f"study card {sc.get('evidence_id')}: not in EVIDENCE.md, citation not verified (V-03)")
        cards.append({**sc, "citation": cit, "end_s": sc.get("end_s", float(sc.get("start_s", 0)) + 2.0)})
    for p in list(pips):
        g = p.get("graphic")
        if g and (g.get("type") == "study_card"):
            cards.append({"title": g.get("text", ""), "evidence_id": g.get("source_evidence_id"),
                          "citation": evidence.citation(g.get("source_evidence_id")) or "",
                          "start_s": p["start_s"], "end_s": p["end_s"]})
            pips.remove(p)
    words = C.clean_words(manifest.get("words") or [])
    plan = OverlayPlan(duration=total, zone=zone, style=style, words=words, texts=manifest.get("on_screen") or [],
                       study_cards=cards, ai_tag=ai_tag, include_hook=True)
    ov_full = render_track(plan, jobdir / "ov_full")
    clean_plan = OverlayPlan(duration=total, zone=zone, style=style, words=words, texts=manifest.get("on_screen") or [],
                             study_cards=cards, ai_tag=ai_tag, include_hook=False)
    ov_clean = render_track(clean_plan, jobdir / "ov_clean")

    # 3) audio
    mus = manifest.get("music") or {}
    music = None
    if mus.get("url") or mus.get("src"):
        music = storage.fetch(mus.get("url") or mus.get("src"), jobdir)
    elif mus.get("mood") not in (None, "none"):
        warns.append("music.mood set but no music.url: rendered without a music bed")
    audio = mix_audio(voice, music, total, float(mus.get("gain_db", -20)), jobdir)

    # 4) final composite: base + PiP + overlay track -> master and clean mezzanine
    args = ["-i", str(base_mp4), "-f", "concat", "-safe", "0", "-i", str(ov_full),
            "-f", "concat", "-safe", "0", "-i", str(ov_clean)]
    fc, last = [], "[0:v]"
    for k, p in enumerate(pips):
        src = _resolve(p["src"], jobdir, f"pip{k}")
        args += (["-loop", "1", "-framerate", str(FPS), "-i", str(src)] if media.is_image(src)
                 else ["-stream_loop", "-1", "-i", str(src)])
        idx = 3 + k
        pw, ph = 420, 420
        x = W - pw - 12 - 40 if p["position"] == "top_right" else zone.left
        y = zone.top + 110 if p["position"] == "top_right" else int(H * 0.50)
        dur = p["end_s"] - p["start_s"]
        fc.append(f"[{idx}:v]trim=duration={dur:.3f},setpts=PTS-STARTPTS+{p['start_s']:.3f}/TB,"
                  f"{COVER.format(w=pw, h=ph)},pad={pw + 12}:{ph + 12}:6:6:color=white,fps={FPS}[p{k}]")
        fc.append(f"{last}[p{k}]overlay={x}:{y}:eof_action=pass:enable='between(t,{p['start_s']:.3f},{p['end_s']:.3f})'[b{k}]")
        last = f"[b{k}]"
    fc.append(f"{last}split=2[bm][bc]")
    fc.append(f"[1:v]fps={FPS},format=rgba[ovf]")
    fc.append(f"[2:v]fps={FPS},format=rgba[ovc]")
    fc.append("[bm][ovf]overlay=0:0:format=auto:shortest=0:eof_action=repeat,format=yuv420p[vm]")
    fc.append("[bc][ovc]overlay=0:0:format=auto:shortest=0:eof_action=repeat,format=yuv420p[vc]")
    aidx = 3 + len(pips)
    args += ["-i", str(audio)]
    out = manifest.get("output") or {}
    master_raw = jobdir / "master_unsigned.mp4"
    clean_mp4 = jobdir / "master_clean.mp4"
    preset = "superfast" if config.X264_PRESET == "ultrafast" else config.X264_PRESET   # ultrafast can't emit High
    enc = ["-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", str(FPS * 2),
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", "-t", f"{total:.3f}"]
    media.ffmpeg([*args, "-filter_complex", ";".join(fc),
                  "-map", "[vm]", "-map", f"{aidx}:a", "-preset", preset, "-crf", str(out.get("crf", 18)),
                  *enc, str(master_raw),
                  "-map", "[vc]", "-map", f"{aidx}:a", "-preset", "veryfast", "-crf", "16", *enc, str(clean_mp4)],
                 timeout=3600)

    # 5) provenance, fingerprints, QA frames
    master = jobdir / "master.mp4"
    c2pa_info = c2pa_sign.sign(master_raw, master, title=f"{manifest.get('page_slug', 'page')}-{brief}.mp4") \
        if (manifest.get("c2pa") or {}).get("sign", True) else {"signed": False, "reason": "c2pa.sign=false"}
    if not master.exists():
        master = master_raw
    probe = media.ffprobe(master)
    vs = next(s for s in probe["streams"] if s["codec_type"] == "video")
    dur = float(probe["format"]["duration"])
    qa_opts = manifest.get("qa") or {}
    phash_seq = phash.video_phash_seq(master) if qa_opts.get("phash", True) else []
    audio_fp = audiofp.fingerprint(master) if qa_opts.get("chromaprint", True) else None
    slug = re.sub(r"[^a-z0-9_-]+", "-", str(manifest.get("page_slug") or "page").lower()).strip("-")[:64] or "page"
    key = f"masters/{slug}/{brief}/{asset_id}.mp4"
    pub = storage.publish(master, key, "video/mp4")
    pub_clean = storage.publish(clean_mp4, key.replace(".mp4", "_clean.mp4"), "video/mp4")
    frames = []
    for k, t in enumerate(frame_times(dur, int(qa_opts.get("export_frames", 12)))):
        fp = media.extract_frame(master, t, jobdir / f"frame_{k:02d}.jpg")
        frames.append({"t": t, "url": storage.publish(fp, f"qa/{asset_id}/frame_{k:02d}.jpg", "image/jpeg")["url"]})
    transcript = " ".join(w.text for w in words)
    burned = burned_in_strings(plan)
    row = {"id": asset_id, "kind": "master", "storage_key": pub["storage_key"], "public_url": pub["url"],
           "mime": "video/mp4", "duration_s": round(dur, 3), "width": vs["width"], "height": vs["height"],
           "fps": round(media.parse_rate(vs.get("r_frame_rate")), 2), "bytes": pub["bytes"], "sha256": pub["sha256"],
           "phash_seq": phash_seq, "audio_fp": audio_fp, "page_id": manifest.get("page_id"), "source": "generated",
           "c2pa": c2pa_info, "tags": ["master"]}
    registered = False
    if supabase.enabled():  # pragma: no cover
        try:
            supabase.insert("assets", row)
            registered = True
        except Exception as e:
            warns.append(f"asset registration failed: {e}")
    return {
        "asset_id": asset_id, "asset_registered": registered, "master_url": pub["url"], "clean_url": pub_clean["url"],
        "storage_key": pub["storage_key"], "local_path": pub.get("local_path"), "duration_s": round(dur, 3),
        "width": vs["width"], "height": vs["height"], "fps": row["fps"], "codec": vs.get("codec_name"),
        "profile": vs.get("profile"), "bytes": pub["bytes"], "sha256": pub["sha256"],
        "transcript": transcript, "transcript_source": "tts_alignment",
        "words": [{"word": w.text, "start_s": w.start, "end_s": w.end} for w in words],
        "burned_in_text": burned, "expected_on_screen": [t["text"] for t in (manifest.get("on_screen") or [])],
        "phash_seq": phash_seq, "audio_fp": audio_fp, "c2pa": c2pa_info, "frames": frames,
        "loudness": media.loudness(master), "warnings": warns, "render_s": round(time.time() - t0, 1),
    }
