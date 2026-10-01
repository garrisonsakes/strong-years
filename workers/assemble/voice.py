"""POST /voice/stitch: join per-line TTS files into one voice track, derive word timings from ElevenLabs
character alignment, and cut per-shot audio segments for lip-sync (InfiniteTalk single or multi-speaker).

Input  (n8n 'Aggregate Voice Lines'): {brief_id, gap_ms, lines:[{i,speaker,url,duration_s,alignment}], shots:[...]}
Output (consumed by 'Build Lip-sync Jobs' and 'Build Assembly Manifest'):
       {track_url, duration_s, words:[{word,start_s,end_s,line_i,speaker}], lines:[{i,speaker,start_s,end_s}],
        segments:[{shot_n,url,start_s,end_s,speakers:{chang,sun}}]}
"""
from __future__ import annotations

import re
import subprocess
import wave
from pathlib import Path

import numpy as np

from common import config, storage

SR = 48000


def decode_pcm(path: Path, sr: int = SR) -> np.ndarray:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-f", "s16le", "-ac", "1", "-ar", str(sr),
                        "-"], capture_output=True, timeout=300)
    if p.returncode != 0:
        raise RuntimeError(f"decode failed for {path}: {p.stderr.decode()[-400:]}")
    return np.frombuffer(p.stdout, dtype=np.int16)


def write_wav(path: Path, pcm: np.ndarray, sr: int = SR) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.astype(np.int16).tobytes())
    return path


def words_from_alignment(alignment: dict | None, text_fallback: str, duration: float) -> list[dict]:
    """ElevenLabs alignment {characters, character_start_times_seconds, character_end_times_seconds} -> words.
    Bracketed performance tags ([warmly]) are dropped. Falls back to length-proportional timing."""
    chars = (alignment or {}).get("characters") or []
    starts = (alignment or {}).get("character_start_times_seconds") or []
    ends = (alignment or {}).get("character_end_times_seconds") or []
    words: list[dict] = []
    if chars and len(chars) == len(starts) == len(ends):
        in_tag, cur, cs, ce = False, "", None, None
        for ch, s, e in zip(chars, starts, ends):
            if ch == "[":
                in_tag = True
            if in_tag:
                if ch == "]":
                    in_tag = False
                continue
            if ch.isspace():
                if cur:
                    words.append({"word": cur, "start_s": cs, "end_s": ce})
                cur, cs, ce = "", None, None
                continue
            cur += ch
            cs = s if cs is None else cs
            ce = e
        if cur:
            words.append({"word": cur, "start_s": cs, "end_s": ce})
        return words
    toks = re.sub(r"\[[^\]]*\]", " ", text_fallback or "").split()
    total = sum(len(t) + 1 for t in toks) or 1
    t = 0.0
    for tok in toks:
        d = duration * (len(tok) + 1) / total
        words.append({"word": tok, "start_s": round(t, 3), "end_s": round(t + d * 0.92, 3)})
        t += d
    return words


def stitch(req: dict, workdir: Path | None = None) -> dict:
    brief = storage.safe_id(req.get("brief_id") or storage.new_id(), "brief_id")      # AUDIT H9: no traversal
    workdir = storage.confine(Path(workdir or config.WORK_DIR), f"voice_{brief}")
    workdir.mkdir(parents=True, exist_ok=True)
    gap = int(SR * float(req.get("gap_ms", 180)) / 1000)
    lines = sorted(req.get("lines") or [], key=lambda l: l.get("i", 0))
    if not lines:
        raise ValueError("no voice lines")
    pcs, meta, words = [], [], []
    t = 0
    for k, ln in enumerate(lines):
        pcm = decode_pcm(storage.fetch(ln["url"], workdir))
        dur = len(pcm) / SR
        start = t / SR
        for w in words_from_alignment(ln.get("alignment"), ln.get("text", ""), dur):
            words.append({**w, "start_s": round(start + float(w["start_s"]), 3), "end_s": round(start + float(w["end_s"]), 3),
                          "line_i": ln.get("i"), "speaker": ln.get("speaker")})
        meta.append({"i": ln.get("i"), "speaker": ln.get("speaker"), "start_s": round(start, 3),
                     "end_s": round(start + dur, 3), "_a": t, "_b": t + len(pcm)})
        pcs.append(pcm)
        t += len(pcm)
        if k < len(lines) - 1:
            pcs.append(np.zeros(gap, dtype=np.int16))
            t += gap
    track = np.concatenate(pcs)
    track_path = write_wav(workdir / "voice_track.wav", track)
    pub = storage.publish(track_path, f"voice/{brief}/voice_track.wav", "audio/wav")

    segments = []
    for sh in req.get("shots") or []:
        if sh.get("route") != "lipsync_talk":
            continue
        storage.safe_id(sh.get("n"), "shot n")
        sel = [m for m in meta if m["i"] in (sh.get("voice_lines") or [])]
        if not sel:   # infer by time overlap with the planned shot window
            a, b = float(sh.get("start_s", 0)), float(sh.get("start_s", 0)) + float(sh.get("duration_s", 0))
            sel = [m for m in meta if m["start_s"] < b and m["end_s"] > a]
        if not sel:
            continue
        a = max(0, min(m["_a"] for m in sel) - int(0.1 * SR))
        b = min(len(track), max(m["_b"] for m in sel) + int(0.1 * SR))
        seg = {"shot_n": sh.get("n"), "start_s": round(a / SR, 3), "end_s": round(b / SR, 3), "speakers": {}}
        p = write_wav(workdir / f"shot_{sh.get('n')}.wav", track[a:b])
        seg["url"] = storage.publish(p, f"voice/{brief}/shot_{sh.get('n')}.wav", "audio/wav")["url"]
        if sh.get("speaker") == "both":
            for spk in ("chang", "sun"):
                mask = np.zeros(len(track), dtype=bool)
                for m in meta:
                    if m["speaker"] == spk:
                        mask[m["_a"]:m["_b"]] = True
                part = np.where(mask[a:b], track[a:b], 0).astype(np.int16)
                pp = write_wav(workdir / f"shot_{sh.get('n')}_{spk}.wav", part)
                seg["speakers"][spk] = storage.publish(pp, f"voice/{brief}/shot_{sh.get('n')}_{spk}.wav", "audio/wav")["url"]
        segments.append(seg)
    return {"track_url": pub["url"], "duration_s": round(len(track) / SR, 3), "words": words,
            "lines": [{k: v for k, v in m.items() if not k.startswith("_")} for m in meta], "segments": segments}
