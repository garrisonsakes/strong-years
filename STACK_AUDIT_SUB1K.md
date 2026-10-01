# STACK_AUDIT_SUB1K: can we hit ≤ $1,000/mo without dropping quality? (verified Oct 1, 2026)

Companion to STACK_DECISION.md. Same planning numbers: 750 videos/mo, 40 s average, 30,000 s/mo. Hard cap ≤ $1,000/mo means **≤ $1.33/video all-in**, or $1.30 with headroom.
Method: 25 web searches/fetches. No accounts, no spend, no generation calls. All prices are list prices from the cited pages. Aggregator and vendor pages can be stale, so the bake-off (§6) re-checks them.

**Bottom line.** No audio-driven avatar model verified at ≥720p comes in under $0.033/s for 100% of runtime. There are only two ways to get under $1K:

1. **Put less runtime through the expensive model.** Keep Kling AI Avatar v2 on camera for about 40% of runtime and run the voice over animated stills for the rest.
2. **Change the kind of lip-sync.** Generate a reusable library of "performance" base clips once, then lip-sync each new audio track onto them with **Kling LipSync at $0.014/s**, about 4× cheaper than Avatar v2. The trade-off is that gestures are no longer driven by the audio.

Self-hosting does not beat the API price once ops time is counted.

---

## 1. Verified per-second prices (new findings marked ★)

| Model / endpoint | Type | $/s (list) | Max length / call | Source |
|---|---|---|---|---|
| Kling AI Avatar v2 Std `fal-ai/kling-video/ai-avatar/v2/standard` | still + audio | $0.0562 | not stated | STACK_DECISION [1] |
| ★ **Kling LipSync** `fal-ai/kling-video/lipsync/audio-to-video` | **video + audio (v2v)** | **$0.014**, rounded up to 5 s | **Video 2–10 s, 720–1920 px; audio 2–60 s**. ~12 min per job | [A][B] |
| ★ LatentSync (1.x) `fal-ai/latentsync` | video + audio (v2v) | **$0.20 flat per video ≤ 40 s**, then $0.005/s | — | [C] |
| ★ Sync lipsync-2 `fal-ai/sync-lipsync/v2` | v2v | $0.05 ($3/min) | — | [D] |
| ★ Sync direct (sync.so): lipsync-2 / 2-pro / 1.9 | v2v | Scale plan ($249/mo): $0.04 / $0.067 / $0.02. Creator plan: $0.05 / $0.083 / $0.025 | 30 min (Scale) | [E] |
| ★ InfiniteTalk on WaveSpeed `wavespeed-ai/infinitetalk` | image + audio | **$0.03 @480p / $0.06 @720p** | 10 min. 10–30 s compute per output second | [F] |
| InfiniteTalk on fal | image + audio | $0.20 @480p | long | STACK_DECISION [10] |
| ★ Wan 2.2 S2V `fal-ai/wan/v2.2-14b/speech-to-video` | image + audio | $0.10 @480p / $0.15 @580p / $0.20 @720p (16 fps) | — | [G] |
| OmniHuman 1.5: fal / ★ WaveSpeed | image + audio | $0.16 / $0.25 | 30 s @1080p, 60 s @720p | [3] / [H] |
| Hedra Character-3 API | image + audio | $0.025 @540p / $0.05 @720p / $0.0625 @1080p | 10 min | STACK_DECISION [7] |
| ★ Hedra subscription credits | image + audio | 6 credits/s. Pro is $75 for 14,400 credits, ≈ **$0.031/s** (resolution unstated). Credits don't roll over | — | [I] (May 30, 2026; "planning inputs, not permanent quotes") |
| ★ HeyGen Photo Avatar IV API | image + audio/text | **$0.05/s at 720p/1080p**, plus $1 per avatar creation, prepaid wallet | long | [J] (this settles STACK_DECISION's price conflict in favor of $0.05; still MEDIUM confidence) |
| MuseTalk 1.5 | v2v | — | — | Documented "out-of-sync" problems; "preview or fallback" only [K] |

Not verified this pass: Kling 2.6 avatar tiers beyond v2; official Kling API unit prices (the page didn't render); Tavus; Hallo3; MultiTalk hosted prices; Novita, Segmind and Runware listings; RunPod H100 hourly rate.

---

## 2. Ranked routes (cost includes 20% retries on the animation step, TTS at ~650 characters, and amortized stills)

| # | Route | $/video | $/mo @25/day | Quality vs the $2K stack | Automation friction | Main risk | Confidence |
|---|---|---|---|---|---|---|---|
| **1** | **Hybrid-40 (recommended).** Kling Avatar v2 Std on camera for 16 s (hook 8 s + mid beat 4 s + close 4 s). The other 24 s are the same voice over animated stills/b-roll (ffmpeg Ken Burns) | **≈ $1.25** (1.08 avatar + 0.065 TTS + 0.10 stills) | **≈ $935** | **Same per frame**, with less face time (40% vs 100%) | Low: same 3 calls plus a split/assemble step | Retention if the face is off screen too long. Fix with the hook and the cut rhythm | Cost HIGH, perception MED-LOW |
| **2** | **Hybrid-60 with lip-sync body.** Avatar v2 for hook + close (12 s, $0.67). A 12 s mid on-camera beat via **Kling LipSync** over a library base clip ($0.21). VO over stills for the remaining 16 s | ≈ $1.20 | ≈ $900 | **Same on hook/close; slightly lower in the mid beat** (gesture not audio-driven) | Medium: needs a base-clip library plus 10 s chunking | Repeated gestures across videos and seams at 10 s | MED-LOW |
| 3 | **Full lip-sync library.** About 40 base "performance" clips of 10 s per character, made once with any i2v model (~$0.84 per clip at ~$0.084/s [L] → ~$70 per refresh). Every video is 100% on camera via Kling LipSync in 4×10 s chunks | ≈ $0.85 | ≈ $640 | **Slightly lower**: mouth is good, but body motion is generic and repeats | Medium | YouTube "low-variation" policy if base clips repeat; Kling LipSync quality on older faces untested | MED-LOW |
| 4 | Hedra Character-3, 540p full runtime (API) or Pro credits | $1.00–1.50 (+20%) | $900–1,350 | **Noticeably lower**: 540p plus weaker sync per VEED (a competitor) | Low: 1 call | Single vendor; 540p softness on 1080×1920 | MED-LOW |
| 5 | InfiniteTalk on WaveSpeed, 480p full runtime | $1.44 + 0.12 | ≈ $1,170 | **Noticeably lower** (480p upscaled). 720p is $2.88, more than Kling | Low | Slow (10–30× realtime); over cap anyway | MED |
| 6 | Sync lipsync-1.9 on the base library (Scale plan) | ≈ $1.10 | ≈ $830 + $249 plan = **$1,080** | Slightly lower | Medium | Over cap. lipsync-2 is $1.60+/video | MED |
| 7 | LatentSync on fal over the base library | ≈ $0.35 | ≈ $265 | **Noticeably lower**: "visible mouth boxes, black mouth artifacts, jitter, unnatural teeth," identity drift [K] | Medium | Dentures and wrinkles on older faces are a likely failure point | MED |
| 8 | Self-host InfiniteTalk (RunPod 4090 community, $0.34/hr [M]) | ≈ $0.35 GPU at 480p; ≈ $0.80 at 720p (est.) | $255–600 GPU **+ 10–20 h/mo ops** | Same as #5 (480p) or slightly lower (720p) | **High**: ~15 min of 4090 compute per 10 s clip even with FusionX/TeaCache [N]. Needs ~1–2.5 GPUs running 24/7. Spot preemption | Reliability, queue babysitting, model updates | MED-LOW |
| 9 | HeyGen Photo Avatar IV API | $2.40 | $1,800 | Slightly lower (talking-portrait look) | Low | Over cap | MED |
| 10 | OmniHuman 1.5, Wan 2.2 S2V 720p, Veo 3.1 Lite, Gemini Omni | $2.40–$9.60 | $1,800+ | — | — | Over cap | HIGH (price) |
| ✗ | Flat all-in-one plans (Argil, Captions, Creatify, Hedra Pro) | — | — | — | — | No verified plan covers ~500 min/mo with API access and persistent custom characters for under $1K. Hedra Pro covers ~2,400 s/mo (60 videos). Argil and Captions plan limits were not verified this pass; earlier evidence shows minute caps far below 500 min | LOW |

**Self-hosting verdict.** At 25/day the GPU bill comes out about the same as WaveSpeed's API price for the same model. You also take on preemptions, ComfyUI drift and on-call time. It only wins at more than 3× this volume, or if InfiniteTalk at 480p is acceptable, and in that case WaveSpeed already sells it with no ops. **Not recommended.**

---

## 3. Format levers (what keeps quality)

- **Avatar time is the cost driver; everything else is pennies.** Each 1 s of Avatar v2 costs $0.067 including retries. Going from 100% to 40% on camera saves about $1.60/video.
- **Hook + close on the best model.** The first 3 s decide retention and the last 3 s carry the CTA. Keep those on Kling Avatar v2 every time. The middle can be VO over animated stills, or cheap v2v lip-sync.
- **Two-character videos.** Use shot/reverse-shot: two single-face renders cut together. That avoids MultiTalk-style multi-person models (unpriced) and is cheaper per second.
- **Resolution.** IG, TikTok and Shorts re-encode to 1080×1920 at a low bitrate. 720p sources upscale without obvious loss on phones. 540p and 480p soften wrinkle and skin texture, and older faces read as "AI" first through skin. **No viewer study found**, so this is a bake-off item (LOW confidence).
- **Frame rate.** Kling prices don't vary with fps. Wan S2V is 16 fps (looks choppy for talking). Not a useful lever.
- **Batch discounts.** No batch or queue discount found on fal or WaveSpeed. Gemini Batch takes **50% off** Nano Banana 2 stills [O]. Free tiers don't matter at this volume.
- **Library reuse.** Approved stills (and, for routes 2/3, base clips) are generated once per month, which cuts cost and drift. Rotate 30–40 per character to stay clear of YouTube's "low-variation" flag.

## 4. Voice (fixed cloned voice per character)

| Service | Price | Per video (~650 characters) | Consistency |
|---|---|---|---|
| ElevenLabs v3 | $100 per 1M characters | $0.065 | Fixed `voice_id`. Multilingual v2 similarity score 3.68 |
| ★ Fish Audio S2-pro | $15 per 1M UTF-8 bytes | ~$0.01 | **Highest speaker similarity, 4.03** (Hume leaderboard, Sep 2026) |
| ★ Cartesia Sonic 3.5 | — | — | Similarity 3.70 |
| ★ Inworld TTS-2 Flash | from $7 per 1M | ~$0.005 | Not ranked |
| ★ Gemini 3.8 Flash TTS | $9 per 1M audio tokens | low | No cloned-voice lock verified |

Source for all rows: [P][O].

**Verdict:** voice is only ~5% of cost. Switching ElevenLabs to Fish S2-pro saves about $40/mo, and Fish may actually be *more* consistent. Only switch if older-voice expressiveness (warmth, pacing, laughs) passes a blind test. MED confidence.

## 5. Stills

| Model | Price | Notes |
|---|---|---|
| Nano Banana 2 (`gemini-3.1-flash-image`) | $0.045 (512 px) / $0.067 (1K) / $0.101 (2K); **50% off via Batch** | Current identity-edit pick [O] |
| ★ Seedream 4 edit (`fal-ai/bytedance/seedream/v4/edit`) | **$0.03/image**, multi-reference | [Q] |
| Flux Kontext; a "Nano Banana 2 Lite" | — | Not verified. No Lite image SKU appeared on Google's pricing page |

**Verdict:** stills are ≤ $0.10/video either way. Keep NB2 on Batch for the master library, and A/B Seedream 4 for bulk scene stills. Cost is not the reason to choose; identity score in the bake-off decides it.

---

## 6. Recommended ≤ $1K configuration

**Route 1, "Hybrid-40"** (with Route 2 as an upgrade if its mid-beat passes the bake-off)

| Step | Model ID | Amount / video | Cost |
|---|---|---|---|
| Stills | `gemini-3.1-flash-image` via Batch (library), plus `fal-ai/bytedance/seedream/v4/edit` for scene stills | 3 scene stills | ~$0.10 |
| Voice | ElevenLabs `eleven_v3`, fixed `voice_id` per character (Fish S2-pro if it wins the blind test) | full 40 s | $0.065 (or $0.01) |
| On-camera | `fal-ai/kling-video/ai-avatar/v2/standard` on audio slices: hook 0–8 s, mid 4 s, close last 4 s | 16 s × $0.0562 × 1.2 retries | $1.08 |
| B-roll | ffmpeg Ken Burns / parallax over the scene stills, same audio, captions, music | 24 s | $0 |
| **Total** | | | **≈ $1.25/video → ≈ $935/mo** at 25/day ($1.19 → $895 with Fish) |

**What it gives up vs the $2K full-runtime stack:**

- About 60% of runtime is VO over animated stills instead of the character talking on camera.
- Per-frame quality is unchanged: same model, same face, same voice. The cost is *presence*, not fidelity.
- Retention impact is unmeasured. The format is Yang Mun-style, which the source page already uses.

**Headroom:** only ~$65/mo. A spike in the retry rate above 20% breaks the cap. Guardrail: n8n tracks the month-to-date spend, and above $900 it drops the mid beat (12 s on camera, ≈ $0.93/video).

## 7. Bake-off amendments (add ~$45 to the ≤ $120 plan)

Add these contenders, using the same S1–S3 scripts, the same stills and the same audio:

| ID | Setup | Est. cost |
|---|---|---|
| **D** | Kling LipSync (`fal-ai/kling-video/lipsync/audio-to-video`) over 3 base clips per character. Measure seams at the 10 s joins, teeth/dentures and gesture mismatch | ~$5 + ~$10 base clips |
| **E** | InfiniteTalk on WaveSpeed at 480p and 720p (S1 only) | ~$5 |
| **F** | LatentSync on fal (S1, S2) as the floor | ~$1 |
| **G** | Sync lipsync-2 on fal (S1) as the v2v ceiling | ~$5 |
| **H** | Hybrid-40 vs full-runtime A in a blind A/B with 55+ raters. Ask "which would you keep watching?" plus a 3 s-hold proxy. **This is the deciding test for the ≤$1K plan** | $0 extra (re-edits A) |
| **I** | Voice: ElevenLabs v3 vs Fish S2-pro on the same lines. Blind naturalness rating plus Resemblyzer consistency | <$1 |
| **J** | Resolution: Avatar output at native vs 720p downscale-then-upscale, viewed on phones by raters | $0 |
| **K** | Stills: NB2 vs Seedream 4 edit, ArcFace identity score against the master | ~$2 |

**Decision rule addition:** choose the cheapest route whose blind naturalness is within 0.3 points of full-runtime A **and** whose "keep watching" preference is ≥ 45% against A. If Hybrid-40 fails H, the honest answer is that ≤ $1K costs some perceived quality. In that case go to Route 2 or 3 if D passes; otherwise budget about $1.1K (Hybrid-50).

## 8. Confidence

- **Prices: HIGH** for fal and WaveSpeed pages fetched today. **MED** for HeyGen, Hedra credits, sync.so and the TTS aggregators.
- **Quality verdicts: MED-LOW.** Nothing found tests older faces specifically. Kling LipSync and InfiniteTalk realism is unbenchmarked head-to-head against Avatar v2.
- **Self-host numbers: MED-LOW.** These are one user report on a 4090 [N] plus a single price snapshot [M]. The H100 RunPod rate was not verified.

## Sources

- [A] fal: Kling LipSync audio-to-video pricing. https://fal.ai/models/fal-ai/kling-video/lipsync/audio-to-video
- [B] fal: Kling LipSync API constraints. https://fal.ai/models/fal-ai/kling-video/lipsync/audio-to-video/api
- [C] fal: LatentSync. https://fal.ai/models/fal-ai/latentsync
- [D] fal: Sync lipsync-2. https://fal.ai/models/fal-ai/sync-lipsync/v2
- [E] Sync.so pricing. https://sync.so/pricing
- [F] WaveSpeed: InfiniteTalk. https://wavespeed.ai/models/wavespeed-ai/infinitetalk
- [G] fal: Wan 2.2 S2V. https://fal.ai/models/fal-ai/wan/v2.2-14b/speech-to-video
- [H] WaveSpeed: OmniHuman 1.5. https://wavespeed.ai/models/bytedance/avatar-omni-human-1.5
- [I] MakeFun: Hedra cost matrix (May 30, 2026). https://makefun.ai/hedra-character-omnia-avatar-video-cost-matrix/
- [J] RealtimeAvatar: HeyGen API pricing 2026. https://realtimeavatar.ai/blog/heygen-api-pricing-explained
- [K] Instavar: open-source lip-sync models compared 2026. https://instavar.com/research/ai-video/open-source-lip-sync-models
- [L] Costbench: Kling API $0.084–0.168/s. https://costbench.com/software/ai-media-apis/kling-api/ (search-result title only; MED-LOW)
- [M] SynpixCloud: cloud GPU pricing snapshot, Sep 12, 2026. https://www.synpixcloud.com/blog/cloud-gpu-pricing-comparison-2026
- [N] InfiniteTalk GitHub issue #210 (speed reports). https://github.com/MeiGen-AI/InfiniteTalk/issues/210
- [O] Google: Gemini API pricing. https://ai.google.dev/gemini-api/docs/pricing
- [P] MarkTechPost: voice cloning APIs, Sep 21, 2026. https://www.marktechpost.com/2026/09/21/best-voice-cloning-apis-in-2026-speaker-similarity-consent-checks-and-price-per-1m-characters/
- [Q] fal: Seedream 4 edit. https://fal.ai/models/fal-ai/bytedance/seedream/v4/edit
- [1], [3], [7], [10]: see STACK_DECISION.md sources.
