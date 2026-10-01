"""Day-1 end-to-end renderer: locked refs -> voices -> per post (keyframe, TTS, lip-sync, 2 no-face inserts) ->
workers/assemble (captions, opening text, loudness, AI tag, IG/FB variants) -> QA -> out/day1/<page>/<post>/ +
the manual post pack (workers/packager/fallback).

DRY_RUN=1 is the DEFAULT. In DRY_RUN every HTTP call goes to an in-process mock (httpx.MockTransport): nothing
leaves the machine, no key is read, no money is spent; outputs land in out/dryrun/day1/. Live needs ALL of:
    DRY_RUN=0  GEMINI_API_KEY=...  ELEVENLABS_API_KEY=...  FAL_KEY=...
and writes out/day1/. Optional: GEMINI_IMAGE_MODEL (default gemini-2.5-flash-image), FAL_LIPSYNC_TIER
(standard|pro, default standard), FAL_INSERT_MODEL (veo|seedance, default veo), REF_CANDIDATES (default 2),
ELEVEN_TTS_MODEL (default eleven_v3).

  python3 production/launch_day/render_day1.py                       # dry run, all stages, all 6 posts
  python3 production/launch_day/render_day1.py --only D1-CY-1        # one post
  DRY_RUN=0 ... render_day1.py --stage refs                          # live: lock-pack candidates, then STOP for review
  DRY_RUN=0 ... render_day1.py --approve refs --reviewer "Name"      # sign off the auto-picked pack (or --pick C02=1)
  DRY_RUN=0 ... render_day1.py --stage voices                        # 3 previews per voice, then STOP for review
  DRY_RUN=0 ... render_day1.py --approve voices --reviewer "Name" --pick chang=0,sun=2
  DRY_RUN=0 ... render_day1.py                                       # resumes: everything already done is skipped

Idempotent + resumable: every step writes its outputs and a record in <out>/state.json; a re-run skips steps whose
outputs exist. Every step appends its cost estimate (USD, list prices as of Oct 2026, verify before trusting) to
<out>/costs.jsonl; <out>/costs_summary.json totals them. Network policy (live): https only, exact host
allow-list, every resolved IP must be public, no redirects, byte + time caps, keys in headers only.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REFS = ROOT / "production" / "refs"
SEEDS = {"chang": [REFS / "out/concepts/chang_a.png", REFS / "out/concepts/chang_b.png"],
         "sun": [REFS / "out/concepts/sun_a.png"]}
DAY = "2026-10-01"


def dry_run() -> bool:
    return os.environ.get("DRY_RUN", "1") != "0"


def out_root() -> Path:
    if os.environ.get("DAY1_OUT"):
        return Path(os.environ["DAY1_OUT"]).resolve()
    return HERE / ("out/dryrun/day1" if dry_run() else "out/day1")


def _bootstrap_workers(out: Path) -> None:
    """workers/common/config reads env at import: confine worker output + fetch roots to our out dir."""
    os.environ.setdefault("OUTPUT_DIR", str(out / "_worker"))
    os.environ.setdefault("WORK_DIR", str(out / "_work"))
    roots = [p for p in os.environ.get("LOCAL_MEDIA_ROOTS", "").split(os.pathsep) if p]
    for r in (str(HERE), str(REFS), str(out)):
        if r not in roots:
            roots.append(r)
    os.environ["LOCAL_MEDIA_ROOTS"] = os.pathsep.join(roots)
    os.environ.setdefault("X264_PRESET", "veryfast")
    cfg = sys.modules.get("common.config")
    if cfg is not None:   # already imported (e.g. by build_day1_plan): extend its fetch roots in place
        for r in roots:
            if r not in cfg.LOCAL_MEDIA_ROOTS:
                cfg.LOCAL_MEDIA_ROOTS.append(r)
    for p in (str(ROOT / "workers"), str(REFS)):
        if p not in sys.path:
            sys.path.insert(0, p)


import httpx  # noqa: E402

# ---------------------------------------------------------------- endpoints, docs, prices --------------------------
# Gemini image ("Nano Banana") generateContent with inline reference images:
#   https://ai.google.dev/gemini-api/docs/image-generation
GEMINI_HOST = "generativelanguage.googleapis.com"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
# ElevenLabs Voice Design (previews) + create-from-preview + TTS with character timestamps:
#   https://elevenlabs.io/docs/api-reference/text-to-voice/design
#   https://elevenlabs.io/docs/api-reference/text-to-voice/create
#   https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps
ELEVEN_HOST = "api.elevenlabs.io"
ELEVEN = "https://api.elevenlabs.io"
# fal queue API (submit -> status_url -> response_url): https://fal.ai/docs/documentation/model-apis/inference/queue
# Lip-sync talking head from a still + audio: Kling AI Avatar v2 (duration follows the audio):
#   https://fal.ai/docs/model-api-reference/video-generation-api/kling-video-ai-avatar-v2
#   (fal-ai/kling-video/ai-avatar/v2/standard | /pro). Kling "lipsync/audio-to-video" needs a source VIDEO, which we
#   don't have today (no performer footage), so the avatar endpoint is the right Kling route.
# No-face inserts: Veo 3.1 Fast image-to-video https://fal.ai/models/fal-ai/veo3.1/fast/image-to-video/api
#   (durations 4s/6s/8s, aspect 9:16, generate_audio false); Seedance fallback:
#   https://fal.ai/models/fal-ai/bytedance/seedance/v1/pro/image-to-video/api
FAL_QUEUE_HOST = "queue.fal.run"
FAL_QUEUE = "https://queue.fal.run"
FAL_CDN_SUFFIXES = (".fal.media",)          # result files (v3.fal.media, ...)
LIPSYNC_MODEL = {"standard": "fal-ai/kling-video/ai-avatar/v2/standard", "pro": "fal-ai/kling-video/ai-avatar/v2/pro"}
INSERT_MODEL = {"veo": "fal-ai/veo3.1/fast/image-to-video", "seedance": "fal-ai/bytedance/seedance/v1/pro/image-to-video"}
ALLOWED_HOSTS = {GEMINI_HOST, ELEVEN_HOST, FAL_QUEUE_HOST}

PRICE = {  # USD estimates (list prices Oct 2026; confirm on each provider's pricing page before a big run)
    "gemini_image": 0.039,                 # per output image (gemini-2.5-flash-image)
    "eleven_design_call": 0.10,            # per design call (3 previews), credits-based estimate
    "eleven_tts_per_1k_chars": 0.22,       # eleven_v3 on a Creator-tier credit price
    "kling_avatar_standard_per_s": 0.0562, # fal docs
    "kling_avatar_pro_per_s": 0.115,       # fal docs
    "veo31_fast_per_s": 0.10,              # video only, no audio (estimate; fal pricing page)
    "seedance_pro_per_s": 0.12,            # estimate
}

# ---------------------------------------------------------------- spec fixes for the lock pack -------------------
PACK = {"chang": ["C01", "C02", "C03", "C04", "C05", "C06", "C24", "C22"],     # all C-CASUAL: the approved look
        "sun": ["S01", "S02", "S03", "S06", "S19", "S11", "S07", "S08"]}       # identity + table + kitchen sets
FIXES = {
    "chang": ("EDIT FIXES (apply all, keep the face from the reference images identical): short white crew cut "
              "receding at the temples; trimmed white beard and mustache exactly 1 cm long, neat edges (not long, "
              "not wispy); an OPEN olive-green flannel shirt worn over a plain white crew-neck tee; one plain smooth "
              "gold wedding band on the LEFT ring finger and no other jewellery (no bracelet, no cuff, no watch); a "
              "small healed scar crossing the OUTER end of his LEFT eyebrow. No text anywhere."),
    "sun": ("EDIT FIXES (apply all, keep the face from the reference image identical): wherever the kitchen shows "
            "cans, tins or labelled containers, replace them with real glass jars of napa-cabbage kimchi (red chili "
            "and cabbage visible through clear glass, plain metal or glass lids, NO labels, NO printed text). Keep the "
            "jade bangle on the LEFT wrist, plain gold band, pearl studs, tortoiseshell clip on the LEFT, reading "
            "glasses on the jade-green beaded cord. No text anywhere."),
}
KEYFRAME = ("Photorealistic vertical 9:16 iPhone frame for a talking-to-camera video. {who} {framing}. Set: {set}. "
            "Eye level, natural light, looking straight into the lens, mouth closed in a relaxed neutral expression "
            "(ready to speak), both hands low and relaxed, face fully inside the middle of the frame (top 12% and "
            "bottom 22% free of the face). Same person as the reference images: identical face, hairline, "
            "{marks}. {fix} No text, letters, logos or watermarks.")
WHO = {"chang": ("Chang Yin, 74-year-old East Asian retired welder", "beard length, eyebrow scar"),
       "sun": ("Sun Yoon, 76-year-old Korean grandmother, petite, silver-white chin-length bob",
               "mole beside the left nostril, coral-rose lipstick")}
SET_TEXT = {"SET-GARAGE": "his home garage gym, pegboard with tools, rubber mat, open garage door light",
            "SET-PROM": "a foggy seaside promenade, steel railing, weathered wooden bench",
            "SET-TABLE": "a walnut dining table in a warm home, window light",
            "SET-KITCHEN": "her warm home kitchen, gas stove, glass kimchi jars on an open shelf"}
INSERT_SUFFIX = " Photorealistic, vertical 9:16, natural light, documentary realism. Absolutely no faces, no text."


# ---------------------------------------------------------------- SSRF-safe HTTP ----------------------------------
class NetPolicyError(ValueError):
    pass


def _public_ip(ip: str) -> bool:
    import ipaddress
    a = ipaddress.ip_address(ip)
    return not (a.is_private or a.is_loopback or a.is_link_local or a.is_reserved or a.is_multicast or a.is_unspecified)


def host_allowed(host: str) -> bool:
    host = (host or "").lower().rstrip(".")
    return host in ALLOWED_HOSTS or any(host.endswith(s) and len(host) > len(s) for s in FAL_CDN_SUFFIXES)


class SafeHttp:
    """All outbound calls go through here. Live: real DNS + public-IP check + no redirects + caps. DRY_RUN: the
    caller passes a MockTransport and a fake resolver; the allow-list still applies, so a mock can't hide a bad URL."""
    MAX_BYTES = 600 * 1024 * 1024

    def __init__(self, transport: httpx.BaseTransport | None = None, resolver=None, timeout: float = 300.0):
        self.resolver = resolver or (lambda h, p: [i[4][0] for i in socket.getaddrinfo(h, p, proto=socket.IPPROTO_TCP)])
        self.client = httpx.Client(transport=transport, timeout=timeout, follow_redirects=False)

    def check(self, url: str) -> None:
        u = urlparse(url)
        if u.scheme != "https":
            raise NetPolicyError(f"only https is allowed: {u.scheme}")
        if u.username or u.password:
            raise NetPolicyError("credentials in URLs are not allowed")
        if not host_allowed(u.hostname or ""):
            raise NetPolicyError(f"host not on the allow-list: {u.hostname}")
        try:
            ips = self.resolver(u.hostname, u.port or 443)
        except OSError as e:
            raise NetPolicyError("host does not resolve") from e
        if not ips or not all(_public_ip(i) for i in ips):
            raise NetPolicyError("host resolves to a non-public address")

    def request(self, method: str, url: str, *, headers: dict | None = None, json_body=None, params=None) -> httpx.Response:
        self.check(url)
        with self.client.stream(method, url, headers=headers, json=json_body, params=params) as r:
            if 300 <= r.status_code < 400:
                raise NetPolicyError("redirect refused")
            buf = bytearray()
            for chunk in r.iter_bytes(1 << 16):
                buf += chunk
                if len(buf) > self.MAX_BYTES:
                    raise NetPolicyError("response exceeds byte cap")
            if r.status_code >= 400:
                raise RuntimeError(f"{method} {urlparse(url).hostname}{urlparse(url).path}: HTTP {r.status_code} {bytes(buf[:300])!r}")
            return httpx.Response(r.status_code, headers=r.headers, content=bytes(buf), request=r.request)

    def json(self, method: str, url: str, **kw) -> dict:
        return self.request(method, url, **kw).json()


# ---------------------------------------------------------------- providers --------------------------------------
def b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def mime_of(b: bytes) -> str:
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if b[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if b[:4] == b"RIFF":
        return "audio/wav"
    if b[4:8] == b"ftyp":
        return "video/mp4"
    return "audio/mpeg"


def data_uri(b: bytes) -> str:
    return f"data:{mime_of(b)};base64,{b64(b)}"


class Gemini:
    def __init__(self, http: SafeHttp, key: str):
        self.http, self.key = http, key
        self.model = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")

    def image(self, text: str, refs: list[bytes], aspect: str = "9:16") -> list[bytes]:
        parts = [{"text": text}] + [{"inline_data": {"mime_type": mime_of(b), "data": b64(b)}} for b in refs[:5]]
        body = {"contents": [{"role": "user", "parts": parts}],
                "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}}}
        j = self.http.json("POST", GEMINI_URL.format(model=self.model), json_body=body,
                           headers={"x-goog-api-key": self.key, "Content-Type": "application/json"})
        out = [base64.b64decode(p["inlineData"]["data"]) for c in j.get("candidates", [])
               for p in (c.get("content") or {}).get("parts", []) if "inlineData" in p]
        if not out:
            raise RuntimeError("Gemini returned no image (safety block or empty candidate)")
        return out


class Eleven:
    def __init__(self, http: SafeHttp, key: str):
        self.http, self.h = http, {"xi-api-key": key, "Content-Type": "application/json"}

    def design(self, description: str, text: str, seed: int) -> list[dict]:
        j = self.http.json("POST", f"{ELEVEN}/v1/text-to-voice/design", headers=self.h,
                           json_body={"voice_description": description, "text": text, "seed": seed,
                                      "model_id": os.environ.get("ELEVEN_TTV_MODEL", "eleven_ttv_v3")})
        return [{"generated_voice_id": p["generated_voice_id"], "audio": base64.b64decode(p["audio_base_64"])}
                for p in j.get("previews", [])]

    def create(self, name: str, description: str, generated_voice_id: str) -> str:
        j = self.http.json("POST", f"{ELEVEN}/v1/text-to-voice", headers=self.h,
                           json_body={"voice_name": name, "voice_description": description,
                                      "generated_voice_id": generated_voice_id})
        return j["voice_id"]

    def tts(self, voice_id: str, text: str, settings: dict) -> tuple[bytes, dict]:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", voice_id):
            raise NetPolicyError("bad voice_id")
        j = self.http.json("POST", f"{ELEVEN}/v1/text-to-speech/{voice_id}/with-timestamps", headers=self.h,
                           params={"output_format": "mp3_44100_128"},
                           json_body={"text": text, "model_id": os.environ.get("ELEVEN_TTS_MODEL", "eleven_v3"),
                                      "voice_settings": settings})
        return base64.b64decode(j["audio_base64"]), j.get("alignment") or j.get("normalized_alignment") or {}


class Fal:
    def __init__(self, http: SafeHttp, key: str, poll_s: float = 4.0, max_wait_s: float = 1800.0):
        self.http, self.h, self.poll_s, self.max_wait_s = http, {"Authorization": f"Key {key}"}, poll_s, max_wait_s

    def run(self, model: str, payload: dict) -> dict:
        if not re.fullmatch(r"[a-z0-9-]+(/[a-z0-9._-]+)+", model):
            raise NetPolicyError("bad model id")
        sub = self.http.json("POST", f"{FAL_QUEUE}/{model}", headers=self.h, json_body=payload)
        status_url, response_url = sub["status_url"], sub["response_url"]
        t0 = time.time()
        while True:
            st = self.http.json("GET", status_url, headers=self.h)
            if st.get("status") == "COMPLETED":
                break
            if st.get("status") not in ("IN_QUEUE", "IN_PROGRESS"):
                raise RuntimeError(f"fal {model}: status {st.get('status')}")
            if time.time() - t0 > self.max_wait_s:
                raise TimeoutError(f"fal {model}: still {st.get('status')} after {self.max_wait_s}s (request {sub.get('request_id')})")
            time.sleep(self.poll_s)
        return self.http.json("GET", response_url, headers=self.h)

    def download(self, url: str) -> bytes:
        return self.http.request("GET", url).content      # CDN files are public; no key sent


# ---------------------------------------------------------------- state, ledger, gates ---------------------------
class Ledger:
    """Step records live in state.json (refs, voices) and state_<post_id>.json (one per post), so several
    `--only <post>` processes can run in parallel once refs + voices are approved without clobbering each other."""

    def __init__(self, out: Path):
        self.out = out
        self.state = {}
        for p in sorted(out.glob("state*.json")):
            self.state.update(json.loads(p.read_text()))

    def _file(self, key: str) -> Path:
        parts = key.split(":")
        return self.out / (f"state_{parts[1]}.json" if parts[0] == "post" else "state.json")

    def done(self, key: str) -> dict | None:
        rec = self.state.get(key)
        if rec and all((self.out / p).exists() for p in rec.get("outputs", [])):
            return rec
        return None

    def record(self, key: str, outputs: list[Path], cost: float, detail: str, extra: dict | None = None) -> dict:
        rec = {"outputs": [str(Path(p).relative_to(self.out)) for p in outputs], "cost_usd": round(cost, 4),
               "detail": detail, "dry_run": dry_run(), "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               **(extra or {})}
        self.state[key] = rec
        f = self._file(key)
        mine = json.loads(f.read_text()) if f.exists() else {}
        mine[key] = rec
        tmp = f.with_suffix(f".tmp{os.getpid()}")
        tmp.write_text(json.dumps(mine, indent=1))
        tmp.replace(f)
        with (self.out / "costs.jsonl").open("a") as fh:
            fh.write(json.dumps({"step": key, "usd_estimate": rec["cost_usd"], "detail": detail, "dry_run": dry_run()}) + "\n")
        print(f"  [{'dry' if dry_run() else 'live'}] {key}: ~${cost:.3f} ({detail})")
        return rec

    def summary(self) -> dict:
        self.state = {}
        for p in sorted(self.out.glob("state*.json")):
            self.state.update(json.loads(p.read_text()))
        tot, by = 0.0, {}
        for k, r in self.state.items():
            tot += r.get("cost_usd", 0)
            by[k.split(":")[0]] = round(by.get(k.split(":")[0], 0) + r.get("cost_usd", 0), 4)
        s = {"dry_run": dry_run(), "total_usd_estimate": round(tot, 2), "by_stage": by,
             "note": "estimates from PRICE in render_day1.py; a DRY_RUN total is what the live run would cost"}
        (self.out / "costs_summary.json").write_text(json.dumps(s, indent=1))
        return s


class AwaitingApproval(Exception):
    pass


def approvals(out: Path) -> dict:
    p = out / "approvals.json"
    return json.loads(p.read_text()) if p.exists() else {}


def approve(out: Path, what: str, reviewer: str, picks: dict) -> dict:
    a = approvals(out)
    a[what] = {"reviewer": reviewer, "at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "picks": picks}
    (out / "approvals.json").write_text(json.dumps(a, indent=1))
    return a


def need_approval(out: Path, what: str, msg: str) -> dict:
    a = approvals(out).get(what)
    if a:
        return a
    if dry_run():
        return approve(out, what, "DRY_RUN (auto)", {})[what]
    raise AwaitingApproval(msg)


# ---------------------------------------------------------------- context ----------------------------------------
class Ctx:
    def __init__(self, out: Path, http: SafeHttp, keys: dict):
        self.out, self.http = out, http
        self.ledger = Ledger(out)
        self.gemini = Gemini(http, keys.get("GEMINI_API_KEY", ""))
        self.eleven = Eleven(http, keys.get("ELEVENLABS_API_KEY", ""))
        self.fal = Fal(http, keys.get("FAL_KEY", ""), poll_s=0.0 if dry_run() else 4.0)
        self.plan = json.loads((HERE / "day1_plan.json").read_text(encoding="utf-8"))
        self.voice_design = json.loads((ROOT / "production/voices/voice_design.json").read_text(encoding="utf-8"))
        self.samples = json.loads((HERE / "voice_samples/voice_samples.json").read_text(encoding="utf-8"))


def ffmpeg(*args: str) -> None:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error", "-y", *args], capture_output=True, timeout=1800)
    if p.returncode:
        raise RuntimeError(p.stderr.decode()[-600:])


def duration(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, timeout=60)
    return float(r.stdout.strip() or 0)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def h8(*parts) -> str:
    """Short content hash for step keys: a changed prompt, line or upstream file gets a new key (re-render),
    unchanged inputs keep their key (skip)."""
    m = hashlib.sha256()
    for x in parts:
        m.update(x.read_bytes() if isinstance(x, Path) else str(x).encode())
        m.update(b"\0")
    return m.hexdigest()[:8]


# ---------------------------------------------------------------- stage: lock pack --------------------------------
def stage_refs(cx: Ctx) -> dict:
    import render_refs
    man = {it["id"]: it for it in render_refs.load_manifest()["items"]}   # sha256-verified locked prompts
    n_cand = int(os.environ.get("REF_CANDIDATES", "2"))
    picks = (approvals(cx.out).get("refs") or {}).get("picks") or {}
    pack = {}
    for ch, ids in PACK.items():
        seeds = [p.read_bytes() for p in SEEDS[ch]]
        locked: list[bytes] = []
        for rid in ids:
            it = man[rid]
            d = cx.out / "refs" / ch
            d.mkdir(parents=True, exist_ok=True)
            key = f"refs:{rid}"
            if not cx.ledger.done(key):
                text = (f"{it['prompt']}\n\nAvoid: {it['negative_prompt']}\n\n{FIXES[ch]}\n\nReference images: the first "
                        f"{len(seeds)} are the approved seed face; any others are already-locked shots of the same person.")
                outs = []
                for n in range(n_cand):
                    img = cx.gemini.image(text, seeds + locked[:5 - len(seeds)], it["aspect_ratio"])[0]
                    p = d / f"{rid}_cand{n}.png"
                    p.write_bytes(img)
                    outs.append(p)
                cx.ledger.record(key, outs, n_cand * PRICE["gemini_image"], f"{n_cand} Nano Banana edits from seed",
                                 {"manifest_sha256": it["sha256"]})
            pick = int(picks.get(rid, 0))
            chosen = d / f"{rid}_cand{pick}.png"
            locked.append(chosen.read_bytes())
            pack[rid] = {"character": ch, "file": str(chosen.relative_to(cx.out)), "sha256": sha(chosen), "candidate": pick}
    (cx.out / "refs" / "pack.json").write_text(json.dumps(pack, indent=1))
    a = need_approval(cx.out, "refs", "Lock pack candidates written to refs/<character>/. Check each against "
                      "production/refs/ACCEPTANCE.md, then: --approve refs --reviewer NAME [--pick C02=1,S07=0]")
    if not dry_run() and not (cx.out / "refs" / "locked.json").exists():
        dest = REFS / "locked"
        dest.mkdir(exist_ok=True)
        for rid, r in pack.items():
            shutil.copyfile(cx.out / r["file"], dest / f"{rid}.png")
        (cx.out / "refs" / "locked.json").write_text(json.dumps({"reviewer": a["reviewer"], "at": a["at"], "pack": pack}, indent=1))
    return pack


def pack_paths(cx: Ctx, ch: str, pack: dict) -> list[Path]:
    return [cx.out / r["file"] for rid, r in pack.items() if r["character"] == ch]


# ---------------------------------------------------------------- stage: voices -----------------------------------
def stage_voices(cx: Ctx) -> dict:
    vd = cx.voice_design["voices"]
    d = cx.out / "voices"
    d.mkdir(parents=True, exist_ok=True)
    previews = {}
    for ch, v in vd.items():
        key = f"voices:design:{ch}"
        rec = cx.ledger.done(key)
        if not rec:
            pv = cx.eleven.design(v["description"], v["preview_text"], seed=1000)
            outs = []
            for i, p in enumerate(pv[:3]):
                f = d / f"{ch}_preview{i}.mp3"
                f.write_bytes(p["audio"])
                outs.append(f)
            rec = cx.ledger.record(key, outs, PRICE["eleven_design_call"], "ElevenLabs voice design, 3 previews",
                                   {"generated_voice_ids": [p["generated_voice_id"] for p in pv[:3]]})
        previews[ch] = rec["generated_voice_ids"]
    a = need_approval(cx.out, "voices", "Voice previews written to voices/<character>_preview{0,1,2}.mp3. Listen with "
                      "production/voices/calibration_lines.json in mind, then: --approve voices --reviewer NAME --pick chang=N,sun=N")
    ids = {}
    for ch, v in vd.items():
        key = f"voices:create:{ch}"
        rec = cx.ledger.done(key)
        if not rec:
            gen = previews[ch][int(a.get("picks", {}).get(ch, 0))]
            vid = cx.eleven.create(f"{ch.title()} (Strong Years, designed)", v["description"], gen)
            f = d / f"{ch}_voice_id.txt"
            f.write_text(vid)
            rec = cx.ledger.record(key, [f], 0.0, "create voice from the approved preview", {"voice_id": vid})
        ids[ch] = rec["voice_id"]
        for i, line in enumerate(cx.samples["characters"][ch]["approval_lines"]):
            k2 = f"voices:sample:{ch}:{i}"
            if not cx.ledger.done(k2):
                audio, _ = cx.eleven.tts(ids[ch], line, v["settings"])
                f = d / f"{ch}_approval_line{i + 1}.{ 'wav' if mime_of(audio) == 'audio/wav' else 'mp3'}"
                f.write_bytes(audio)
                cx.ledger.record(k2, [f], len(line) / 1000 * PRICE["eleven_tts_per_1k_chars"], "approval line TTS")
    (d / "voices.json").write_text(json.dumps(ids, indent=1))
    return ids


# ---------------------------------------------------------------- stage: one post ---------------------------------
def char_of(post: dict) -> str:
    return "chang" if post["speaker"] == "CHANG" else "sun"


def stage_post(cx: Ctx, post: dict, pack: dict, voice_ids: dict) -> dict:
    from assemble import assembler, variants, voice as V
    from packager import fallback
    from qa import face, qa as QA
    from uniqueness import guard

    ch, pid = char_of(post), post["post_id"]
    pdir = cx.out / post["page"] / pid
    pdir.mkdir(parents=True, exist_ok=True)
    work = pdir / "_src"
    work.mkdir(exist_ok=True)
    refs = pack_paths(cx, ch, pack)
    L = cx.ledger

    # (a) keyframe still from the locked pack
    who, marks = WHO[ch]
    text = KEYFRAME.format(who=who, framing=post["render"]["keyframe"]["framing"],
                           set=SET_TEXT[post["render"]["keyframe"]["set"]], marks=marks, fix=FIXES[ch])
    k_kf = f"post:{pid}:keyframe:{h8(text, *refs[:5])}"
    kf = work / f"keyframe_{k_kf[-8:]}.png"
    if not L.done(k_kf):
        kf.write_bytes(cx.gemini.image(text, [p.read_bytes() for p in refs[:5]])[0])
        L.record(k_kf, [kf], PRICE["gemini_image"], "Nano Banana keyframe from locked refs")

    # (b) TTS per beat -> stitched track + word timings (workers/assemble/voice)
    lines = []
    for k, b in enumerate(post["beats"]):
        key = f"post:{pid}:tts:{k}:{h8(voice_ids[ch], b['vo'])}"
        rec = L.done(key)
        if not rec:
            audio, align = cx.eleven.tts(voice_ids[ch], b["vo"], cx.voice_design["voices"][ch]["settings"])
            stem = f"line{k:02d}_{key[-8:]}"
            f = work / f"{stem}.{'wav' if mime_of(audio) == 'audio/wav' else 'mp3'}"
            f.write_bytes(audio)
            (work / f"{stem}.align.json").write_text(json.dumps(align))
            rec = L.record(key, [f, work / f"{stem}.align.json"], len(b["vo"]) / 1000 * PRICE["eleven_tts_per_1k_chars"], "TTS beat")
        f = cx.out / rec["outputs"][0]
        lines.append({"i": k, "speaker": ch, "url": str(f), "text": b["vo"],
                      "alignment": json.loads((cx.out / rec["outputs"][1]).read_text()) or None})
    st = V.stitch({"brief_id": pid, "gap_ms": 160, "lines": lines})
    track = work / "voice_track.wav"
    shutil.copyfile(urlparse(st["track_url"]).path if st["track_url"].startswith("file:") else st["track_url"], track)
    total = round(st["duration_s"] + 0.4, 3)
    starts = [ln["start_s"] for ln in st["lines"]]

    # (c) lip-synced talking head for the whole track (Kling AI Avatar v2), trimmed per talk window below
    k_ls = f"post:{pid}:lipsync:{h8(track, kf, os.environ.get('FAL_LIPSYNC_TIER', 'standard'))}"
    talk = work / f"talk_{k_ls[-8:]}.mp4"
    if not L.done(k_ls):
        mp3 = work / "voice_track.mp3"
        ffmpeg("-i", str(track), "-ac", "1", "-b:a", "128k", str(mp3))
        tier = os.environ.get("FAL_LIPSYNC_TIER", "standard")
        res = cx.fal.run(LIPSYNC_MODEL[tier], {"image_url": data_uri(kf.read_bytes()), "audio_url": data_uri(mp3.read_bytes()),
                                               "prompt": "Natural, warm talking to camera; small natural head movements; hands still; no text."})
        talk.write_bytes(cx.fal.download(res["video"]["url"]))
        L.record(k_ls, [talk], st["duration_s"] * PRICE[f"kling_avatar_{tier}_per_s"],
                 f"Kling AI Avatar v2 {tier}, {st['duration_s']:.1f}s")

    # (d) two no-face inserts: Nano Banana still -> Veo 3.1 Fast i2v (no audio)
    ins_files = {}
    imodel = os.environ.get("FAL_INSERT_MODEL", "veo")
    for j, ins in enumerate(post["render"]["inserts"]):
        k_st = f"post:{pid}:insert{j}:still:{h8(ins['still'])}"
        k_cl = f"post:{pid}:insert{j}:video:{h8(ins['still'], ins['motion'], imodel)}"
        still, clip = work / f"insert{j}_{k_st[-8:]}.png", work / f"insert{j}_{k_cl[-8:]}.mp4"
        if not L.done(k_st):
            still.write_bytes(cx.gemini.image(ins["still"] + INSERT_SUFFIX, [])[0])
            L.record(k_st, [still], PRICE["gemini_image"], "Nano Banana insert still (no face)")
        if not L.done(k_cl):
            payload = ({"prompt": ins["motion"] + " No faces, no text.", "image_url": data_uri(still.read_bytes()),
                        "duration": "8s", "aspect_ratio": "9:16", "resolution": "1080p", "generate_audio": False,
                        "negative_prompt": "face, person's head, text, letters, logo, watermark"}
                       if imodel == "veo" else
                       {"prompt": ins["motion"] + " No faces, no text.", "image_url": data_uri(still.read_bytes()),
                        "duration": "8", "aspect_ratio": "9:16", "resolution": "1080p"})
            res = cx.fal.run(INSERT_MODEL[imodel], payload)
            clip.write_bytes(cx.fal.download(res["video"]["url"]))
            L.record(k_cl, [clip], 8 * PRICE["veo31_fast_per_s" if imodel == "veo" else "seedance_pro_per_s"],
                     f"{INSERT_MODEL[imodel]} 8s")
        ins_files[ins["beat"]] = clip

    # (e) timeline: insert beats show the insert (max 7.5 s, then back to the face); talk windows are cut from talk.mp4
    talk_len = duration(talk)
    shots, n = [], 0

    def talk_seg(a: float, b: float) -> str:
        nonlocal n
        n += 1
        f = work / f"talk_{n:02d}.mp4"
        a2 = min(a, max(0.0, talk_len - 0.5))
        ffmpeg("-ss", f"{a2:.3f}", "-i", str(talk), "-t", f"{max(0.2, b - a):.3f}", "-an", "-c:v", "libx264",
               "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", str(f))
        return str(f)

    for k in range(len(post["beats"])):
        a = 0.0 if k == 0 else starts[k]
        b = starts[k + 1] if k + 1 < len(starts) else total
        if k in ins_files:
            e = min(b, a + 7.5)
            shots.append({"n": len(shots) + 1, "route": "broll", "start_s": a, "duration_s": e - a,
                          "src": str(ins_files[k]), "layout": "full", "camera": "static"})
            if b - e > 0.3:
                shots.append({"n": len(shots) + 1, "route": "lipsync_talk", "start_s": e, "duration_s": b - e,
                              "src": talk_seg(e, b), "layout": "full", "camera": "static"})
        else:
            shots.append({"n": len(shots) + 1, "route": "lipsync_talk", "start_s": a, "duration_s": b - a,
                          "src": talk_seg(a, b), "layout": "full", "camera": "handheld_micro" if k == 0 else "static"})
    on_screen = [{"text": b["ost"], "start_s": (0.0 if k == 0 else starts[k]),
                  "end_s": (min(2.6, starts[1]) if k == 0 else (starts[k + 1] if k + 1 < len(starts) else total)),
                  "style": "hook" if k == 0 else "emphasis"} for k, b in enumerate(post["beats"])]
    cards = [{"title": c["title"], "evidence_id": c["evidence_id"], "start_s": starts[c["beat"]] + 0.3,
              "end_s": starts[c["beat"]] + 3.3} for c in post["render"]["study_cards"]]
    manifest = {"brief_id": pid, "page_slug": post["page"].lstrip("@"), "locale": "en-US", "timeline": shots,
                "voice_track": str(track), "words": st["words"],
                "captions": {"size_px": 60, "fill": "#FFFFFF", "pill": "#111111", "highlight": "#FFD84D",
                             "safe_bottom_pct": 22, "safe_top_pct": 12, "max_words_per_chunk": 4},
                "on_screen": on_screen, "study_cards": cards, "music": {"mood": "none"}, "c2pa": {"sign": True},
                "qa": {"export_frames": 12, "phash": True, "chromaprint": True}}
    (work / "assembly_manifest.json").write_text(json.dumps(manifest, indent=1))

    # (f) assemble master + IG/FB variants (workers/assemble)
    master = pdir / "master.mp4"
    k_as = f"post:{pid}:assemble:{h8(json.dumps(manifest, sort_keys=True), track, talk, *ins_files.values())}"
    if not L.done(k_as):
        res = assembler.assemble(manifest)
        shutil.copyfile(res["local_path"], master)
        shutil.copyfile(Path(res["local_path"]).with_name(Path(res["local_path"]).stem + "_clean.mp4"), work / "master_clean.mp4")
        (work / "assemble_result.json").write_text(json.dumps({k: v for k, v in res.items() if k != "words"}, indent=1, default=str))
        L.record(k_as, [master, work / "assemble_result.json"], 0.0, "assemble (local ffmpeg)",
                 {"master_url": res["master_url"]})
    ar = json.loads((work / "assemble_result.json").read_text())
    k_va = f"post:{pid}:variants:{h8(master, json.dumps(post['variants'], sort_keys=True))}"
    if not L.done(k_va):
        vr = variants.render_variants({"video_id": pid, "master_url": ar["master_url"], "variants": [
            {"platform": "instagram", "on_screen_hook": post["variants"]["ig"]["on_screen_hook"], "cover_text": post["variants"]["ig"]["cover_text"]},
            {"platform": "facebook", "on_screen_hook": post["variants"]["fb"]["on_screen_hook"], "cover_text": post["variants"]["fb"]["cover_text"]}]})
        outs = []
        for v in vr["variants"]:
            short = {"instagram": "ig", "facebook": "fb"}[v["platform"]]
            for src_url, name in ((v["url"], f"{short}.mp4"), (v["cover_url"], f"{short}_cover.jpg")):
                shutil.copyfile(urlparse(src_url).path, pdir / name)
                outs.append(pdir / name)
        L.record(k_va, outs, 0.0, "IG + FB variants (local ffmpeg)")

    # (g) QA: probes, loudness, caption OCR, AI tag, C2PA, face consistency vs the locked pack (if installed)
    qa_p = pdir / "qa.json"
    k_qa = f"post:{pid}:qa:{h8(master, json.dumps(cx.plan['posts'], sort_keys=True))}"
    if not L.done(k_qa):
        script_text = " ".join(b["vo"] for b in post["beats"])
        q = QA.run({"video_url": ar["master_url"], "asset_id": pid.replace("-", "_"),
                    "reference_urls": [str(p) for p in refs[:5]], "expected_on_screen": [b["ost"] for b in post["beats"]],
                    "script_text": script_text, "shot_map": shots, "frames": 12,
                    "checks": ["ffprobe", "ebur128", "blackdetect", "freezedetect", "ocr_captions", "ai_tag", "duration", "c2pa", "face_arcface"],
                    "context": {"judge_passed": None}})
        siblings = [{"id": o["post_id"], "page_id": o["page"], "platform": "instagram",
                     "script_text": " ".join(b["vo"] for b in o["beats"]), "scheduled_at": o["variants"]["ig"]["scheduled_at"]}
                    for o in cx.plan["posts"] if o["post_id"] != pid]
        uq = guard.check({"id": pid, "page_id": post["page"], "platform": "instagram", "script_text": script_text,
                          "scheduled_at": post["variants"]["ig"]["scheduled_at"]}, siblings)
        face_ok, face_why = face.available()
        q["uniqueness"] = {"allow": uq.get("allow"), "reasons": uq.get("reasons", [])}
        q["face_module"] = {"installed": face_ok, "reason": face_why}
        m = q["metrics"]
        blockers = [r for r in (
            None if m.get("ai_tag_present") in (True, None) else "AI tag not detected by OCR",
            None if (m.get("caption_cer") is None or m["caption_cer"] <= 0.25) else f"caption OCR CER {m['caption_cer']}",
            None if (m.get("face_sim_median") is None or m["face_sim_median"] >= 0.6) else f"face similarity {m['face_sim_median']} < 0.6",
            None if uq.get("allow") else "uniqueness guard denied",
            None if (m.get("lufs_integrated") is None or -16.0 <= m["lufs_integrated"] <= -12.0) else f"loudness {m['lufs_integrated']} LUFS",
            None if m.get("spec_ok", True) else f"spec: {m.get('spec_problems')}") if r]
        q["day1_warnings"] = [w for w in (
            None if m.get("c2pa_present") else "C2PA not signed (set C2PA_SIGN_CERT/C2PA_PRIVATE_KEY); the manual AI-label toggle is then the only platform label",
            None if face_ok else f"face consistency not measured ({face_why}); compare the face to refs/ by eye",
            "LLM judge not run here: a human reviews caption + video before posting") if w]
        q["day1_status"] = "HOLD" if blockers else "READY_FOR_HUMAN_REVIEW"
        q["day1_blockers"] = blockers
        qa_p.write_text(json.dumps(q, indent=1, default=str))
        L.record(k_qa, [qa_p], 0.0, f"QA {q['decision']} / {q['day1_status']}")
    q = json.loads(qa_p.read_text())

    # (h) post files + manual post pack (workers/packager/fallback)
    for pl in ("ig", "fb"):
        (pdir / f"caption_{pl}.txt").write_text(post["variants"][pl]["caption"], encoding="utf-8")
    (pdir / "first_comment.txt").write_text(post["first_comment"], encoding="utf-8")
    items = [{"post_id": pid, "page": post["page"], "platform": pl, "variant_id": f"{pid}-{pl}", "is_aigc": True,
              "uniqueness": q["uniqueness"], "caption": post["variants"][pl]["caption"], "hashtags": post["variants"][pl]["hashtags"],
              "first_comment": post["first_comment"], "video": str(pdir / f"{pl}.mp4"),
              "scheduled_at": post["variants"][pl]["scheduled_at"]} for pl in ("ig", "fb")]
    pk = fallback.build_pack(DAY, items, pdir / "pack")
    post_json = {"post_id": pid, "page": post["page"], "status": q["day1_status"], "blockers": q["day1_blockers"],
                 "warnings": q.get("day1_warnings", []),
                 "qa_decision": q["decision"], "qa_route": q.get("route_label"), "llm_judge": "pending (human review before posting)",
                 "files": {"ig": "ig.mp4", "fb": "fb.mp4", "ig_cover": "ig_cover.jpg", "fb_cover": "fb_cover.jpg",
                           "master": "master.mp4", "caption_ig": "caption_ig.txt", "caption_fb": "caption_fb.txt",
                           "first_comment": "first_comment.txt", "qa": "qa.json"},
                 "schedule": {pl: post["variants"][pl]["scheduled_at"] for pl in ("ig", "fb")},
                 "ai_label": {pl: post["variants"][pl]["ai_label"] for pl in ("ig", "fb")},
                 "pack": pk, "dry_run": dry_run()}
    (pdir / "post.json").write_text(json.dumps(post_json, indent=1))
    return post_json


def write_index(cx: Ctx, _results: list[dict] | None = None) -> list[dict]:
    """Index every post rendered so far (reads post.json from disk, so parallel --only runs all show up)."""
    import csv
    order = [p["post_id"] for p in cx.plan["posts"]]
    results = sorted((json.loads(p.read_text()) for p in cx.out.glob("*/D1-*/post.json")),
                     key=lambda r: order.index(r["post_id"]))
    with (cx.out / "meta_business_suite_day1.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Platform", "Page", "Scheduled time", "Text", "Video", "First comment", "Variant ID", "Status"])
        for r in results:
            post = next(p for p in cx.plan["posts"] if p["post_id"] == r["post_id"])
            for pl, name in (("ig", "Instagram"), ("fb", "Facebook")):
                w.writerow([name, r["page"], r["schedule"][pl], post["variants"][pl]["caption"],
                            f"{r['page']}/{r['post_id']}/{pl}.mp4", post["first_comment"], f"{r['post_id']}-{pl}", r["status"]])
    (cx.out / "day1_summary.json").write_text(json.dumps({"day": DAY, "dry_run": dry_run(), "posts": [
        {k: r[k] for k in ("post_id", "page", "status", "blockers", "qa_decision", "schedule")} for r in results],
        "costs": cx.ledger.summary()}, indent=1))
    return results


# ---------------------------------------------------------------- profile pictures (local, no API) --------------
PFP = {"chang": {"seed": "chang_a.png", "box": (210, 0, 1360, 1150)},     # 1150 px square, face centred
       "sun": {"seed": "sun_a.png", "box": (130, 0, 1280, 1150)}}


def make_pfp(dest: Path) -> list[Path]:
    from PIL import Image, ImageDraw, ImageFont
    dest.mkdir(parents=True, exist_ok=True)
    out = []
    font_p = ROOT / "workers/fonts"
    fonts = sorted(font_p.glob("*Bold*.ttf")) + sorted(font_p.glob("*.ttf"))
    for ch, spec in PFP.items():
        im = Image.open(REFS / "out/concepts" / spec["seed"]).convert("RGB").crop(spec["box"]).resize((1080, 1080), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        f = ImageFont.truetype(str(fonts[0]), 64) if fonts else ImageFont.load_default()
        # "AI" corner mark: white on near-black pill, bottom-right, inside the circle-crop safe area
        x0, y0, x1, y1 = 700, 800, 850, 900     # farthest corner 475 px from centre: inside the 540 px circle crop
        d.rounded_rectangle((x0, y0, x1, y1), radius=24, fill=(17, 17, 17))
        tw = d.textlength("AI", font=f)
        d.text(((x0 + x1 - tw) / 2, y0 + 14), "AI", fill=(255, 255, 255), font=f)
        p = dest / f"{ch}_profile_1080.png"
        im.save(p)
        out.append(p)
    return out


# ---------------------------------------------------------------- dry-run mock backend ----------------------------
class MockBackend:
    """Stands in for Gemini, ElevenLabs and fal in DRY_RUN. Produces real, small media so the downstream pipeline
    (stitch, assemble, variants, QA, pack) runs for real. Speech pace: DRY_SEC_PER_WORD (default 0.4 s/word)."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        tmp.mkdir(parents=True, exist_ok=True)
        self.jobs: dict[str, dict] = {}
        self.calls: list[str] = []
        self.spw = float(os.environ.get("DRY_SEC_PER_WORD", "0.4"))

    def _png(self, w=540, h=960) -> bytes:
        from PIL import Image, ImageDraw
        import random
        im = Image.new("RGB", (w, h), (random.randint(40, 200), random.randint(40, 200), random.randint(40, 200)))
        ImageDraw.Draw(im).ellipse((w * 0.3, h * 0.25, w * 0.7, h * 0.5), fill=(225, 190, 160))
        p = self.tmp / f"{uuid.uuid4().hex}.png"
        im.save(p)
        return p.read_bytes()

    def _wav(self, secs: float) -> bytes:
        p = self.tmp / f"{uuid.uuid4().hex}.wav"
        ffmpeg("-f", "lavfi", "-i", f"sine=frequency=180:duration={secs:.2f}", "-af", "volume=0.3", "-ar", "44100", "-ac", "1", str(p))
        return p.read_bytes()

    def _mp4(self, secs: float) -> bytes:
        p = self.tmp / f"{uuid.uuid4().hex}.mp4"
        ffmpeg("-f", "lavfi", "-i", f"testsrc2=s=540x960:r=30:d={secs:.2f}", "-c:v", "libx264", "-preset", "ultrafast",
               "-pix_fmt", "yuv420p", str(p))
        return p.read_bytes()

    def handler(self, req: httpx.Request) -> httpx.Response:
        u, host = req.url, req.url.host
        self.calls.append(f"{req.method} {host}{u.path}")
        body = json.loads(req.content or b"{}") if req.method == "POST" else {}
        if host == GEMINI_HOST:
            assert req.headers.get("x-goog-api-key") is not None
            return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"inlineData": {"mimeType": "image/png", "data": b64(self._png())}}]}}]})
        if host == ELEVEN_HOST and u.path == "/v1/text-to-voice/design":
            return httpx.Response(200, json={"previews": [{"generated_voice_id": f"gen_{i}_{uuid.uuid4().hex[:8]}",
                                                           "audio_base_64": b64(self._wav(1.5))} for i in range(3)]})
        if host == ELEVEN_HOST and u.path == "/v1/text-to-voice":
            return httpx.Response(200, json={"voice_id": "dryvoice_" + re.sub(r"\W", "", body["voice_name"].split()[0]).lower()})
        if host == ELEVEN_HOST and u.path.endswith("/with-timestamps"):
            text = body["text"]
            secs = max(0.6, len(text.split()) * self.spw)
            chars = list(text)
            step = secs / max(1, len(chars))
            return httpx.Response(200, json={"audio_base64": b64(self._wav(secs)), "alignment": {
                "characters": chars, "character_start_times_seconds": [round(i * step, 3) for i in range(len(chars))],
                "character_end_times_seconds": [round((i + 1) * step, 3) for i in range(len(chars))]}})
        if host == FAL_QUEUE_HOST and req.method == "POST":
            rid = uuid.uuid4().hex
            model = u.path.strip("/")
            if "audio_url" in body:
                a = self.tmp / f"{rid}.audio"
                a.write_bytes(base64.b64decode(body["audio_url"].split(",", 1)[1]))
                secs = duration(a)
            else:
                secs = float(str(body.get("duration", "8")).rstrip("s"))
            self.jobs[rid] = {"model": model, "secs": secs}
            base = f"https://queue.fal.run/{'/'.join(model.split('/')[:2])}/requests/{rid}"
            return httpx.Response(200, json={"request_id": rid, "status_url": base + "/status", "response_url": base})
        if host == FAL_QUEUE_HOST and req.method == "GET":
            rid = u.path.rstrip("/").split("/")[-2 if u.path.endswith("/status") else -1]
            if u.path.endswith("/status"):
                return httpx.Response(200, json={"status": "COMPLETED"})
            return httpx.Response(200, json={"video": {"url": f"https://v3.fal.media/files/dry/{rid}.mp4"}})
        if host.endswith(".fal.media"):
            rid = u.path.rsplit("/", 1)[-1].split(".")[0]
            return httpx.Response(200, content=self._mp4(self.jobs[rid]["secs"]))
        return httpx.Response(404, json={"error": f"mock: unknown {host}{u.path}"})


# ---------------------------------------------------------------- main ---------------------------------------------
def build_ctx(out: Path, transport=None, resolver=None) -> tuple[Ctx, MockBackend | None]:
    mock = None
    if dry_run():
        mock = MockBackend(out / "_mock")
        http = SafeHttp(transport=transport or httpx.MockTransport(mock.handler), resolver=lambda h, p: ["93.184.216.34"])
        keys = {"GEMINI_API_KEY": "dry", "ELEVENLABS_API_KEY": "dry", "FAL_KEY": "dry"}
    else:
        keys = {k: os.environ.get(k, "") for k in ("GEMINI_API_KEY", "ELEVENLABS_API_KEY", "FAL_KEY")}
        missing = [k for k, v in keys.items() if not v]
        if missing:
            raise SystemExit(f"DRY_RUN=0 needs {', '.join(missing)}; refusing")
        http = SafeHttp(transport=transport, resolver=resolver)
    return Ctx(out, http, keys), mock


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--stage", default="all", choices=["all", "refs", "voices", "posts", "pfp"])
    ap.add_argument("--only", default="", help="comma list of post_ids")
    ap.add_argument("--approve", default="", help="refs and/or voices")
    ap.add_argument("--reviewer", default="")
    ap.add_argument("--pick", default="", help="e.g. chang=0,sun=2 (voices) or C02=1,S07=0 (refs)")
    a = ap.parse_args(argv)
    out = out_root()
    out.mkdir(parents=True, exist_ok=True)
    _bootstrap_workers(out)
    if a.stage == "pfp":
        for p in make_pfp(HERE / "pfp"):
            print("wrote", p.relative_to(HERE))
        return 0
    if a.approve:
        if not a.reviewer:
            print("--approve needs --reviewer NAME", file=sys.stderr)
            return 2
        picks = dict(kv.split("=") for kv in a.pick.split(",") if "=" in kv)
        for what in a.approve.split(","):
            approve(out, what.strip(), a.reviewer, {k: int(v) for k, v in picks.items()})
            print(f"approved {what} by {a.reviewer}")
        return 0
    cx, mock = build_ctx(out)
    print(f"{'DRY RUN (mock HTTP, no spend)' if dry_run() else 'LIVE'} -> {out}")
    only = {x.strip() for x in a.only.split(",") if x.strip()}
    try:
        pack = stage_refs(cx)
        if a.stage == "refs":
            return 0
        voice_ids = stage_voices(cx)
        if a.stage == "voices":
            return 0
        results = []
        for post in cx.plan["posts"]:
            if only and post["post_id"] not in only:
                continue
            print(f"post {post['post_id']} ({post['page']} {post['script_id']})")
            results.append(stage_post(cx, post, pack, voice_ids))
        results = write_index(cx)
    except AwaitingApproval as e:
        print(f"STOPPED for review: {e}")
        cx.ledger.summary()
        return 10
    s = cx.ledger.summary()
    for r in results:
        print(f"  {r['post_id']:<8} {r['status']:<24} {', '.join(r['blockers']) or ''}")
    print(f"estimated cost: ${s['total_usd_estimate']} ({'would spend' if dry_run() else 'spent'})")
    if mock:
        print(f"mock HTTP calls: {len(mock.calls)} (no network)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
