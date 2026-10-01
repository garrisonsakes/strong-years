# STACK_DECISION — Chang Yin & Sun Yoon video stack (verified Oct 1, 2026)

Scope: 4 IG pages, 25 unique 30–50 s vertical videos/day (planning number: **40 s avg → 1,000 s/day → 30,000 s/month, 750 videos/month**), reposted to TikTok/YT Shorts, n8n-driven, budget ≤ $1,000/mo (stretch ~$2,000).
Method: 20 web searches/fetches, no generation calls, no accounts, no spend. Prices are list prices from the cited pages; vendor and aggregator pages can be stale or biased, so the bake-off below re-checks them.

**Budget math to keep in mind:** $1,000/mo ÷ 30,000 s = **$0.033 per rendered second, all-in**. No talking-avatar model verified here hits that on 100% of runtime at a usable resolution. The rest of this doc is about how to deal with that.

---

## 1. Comparison table

Per-video cost = 40 s × list price, generation only (no retries, TTS or stills).

| Option | Type | Driven by | Max length / call | $/s (list) | $/40 s video | Realism notes (evidence) | Fit |
|---|---|---|---|---|---|---|---|
| **Kling AI Avatar v2 Standard** (`fal-ai/kling-video/ai-avatar/v2/standard`) | still + audio → talking video | Audio | Not stated on fal page (unverified) | $0.0562 [1][2] | **$2.25** | Beat OmniHuman 1.5 head-to-head on lip-sync, expressions and speech-aligned hand motion [6] | **Primary** |
| Kling AI Avatar v2 Pro (`…/v2/pro`) | same | Audio | unverified | $0.115 [2] | $4.60 | Same family, higher tier [2][6] | Quality ceiling |
| Hedra Character-3 (Hedra API) | portrait + audio | Audio | **up to 10 min** [7] | $0.025 (540p) / $0.05 (720p) / $0.0625 (1080p) [7] | $1.00 / $2.00 / $2.50 | Called the "budget option, with trade-offs in lip-sync accuracy and natural movement" (VEED, a competitor) [8] | **Backup / budget lever** |
| HeyGen Photo Avatar IV (API) | photo + script/audio | Audio or text | Long-form | $0.05 [9] (VEED cites $0.10 + $100/mo API minimum [8]; **sources conflict**) | $2.00–4.00 | Mature API with built-in voices | Alternative backup |
| OmniHuman 1.5 (`fal-ai/bytedance/omnihuman/v1.5`) | image + audio | Audio | 30 s @1080p, 60 s @720p [3] | $0.16 [3] | $6.40 | Stable identity, but less natural sync and head tilt than Kling [6] | Too expensive |
| InfiniteTalk (`fal-ai/infinitalk`) | image/video + audio | Audio | Long-form | $0.20 @480p, ×2 @720p [10] | $8.00+ | Built for long takes; poor price on fal | No (fal price) |
| Veo 3.1 Lite / Fast / Standard (`veo-3.1-lite-generate-preview`, `veo-3.1-fast-generate-preview`, `veo-3.1-generate-preview`) | ref image + prompt → video **with native voice** | Text | Short clips plus an "extension" feature [11]; clip length not confirmed on Google's page | Lite $0.05 (720p) / Fast $0.10 / Std $0.40 [4] | $2.00 / $4.00 / $16.00 | Native audio. Voice is regenerated on every call, with no locked voice ID found (risk) | Single-call option |
| Gemini Omni 1.1 Flash (`gemini-omni-1.1-flash-preview`, released Aug 27 2026) | prompt + 3 s video reference → video + audio | Text | **40 s total** through 10 s scene extensions [12] | ~$0.10 (720p) [12] | ~$4.00 | ~15% stutter rate in one ad-production test [5] | **Best single-call candidate** |
| Seedance 2.0 / 2.5 (fal `bytedance/seedance-2.0/…`, `…/2.5/reference-to-video`) | refs + quoted dialogue → video + audio | Text | 15 s (2.0) / 30 s (2.5) [13] | $0.30 / ~$0.47 @720p [13] | $12 / $19 | Rated "indistinguishable from filmed UGC," but words get corrupted [5] | Too expensive |
| Kling 3.0 Pro (text/i2v + audio) | prompt → video + audio | Text | — | mid-tier [5] | — | Lip-sync drifts after about 8 s [5] | No for 40 s takes |
| Sora 2 API | — | — | — | — | — | **API shut down Sept 24, 2026** [14] | Dead |
| Captions Mirage | full-frame generated actor | Script | not disclosed | Plans $9.99–$279.99/mo [15] | n/a | Generates the whole frame, so it looks "more filmed than puppeted" [15]. No public API or custom fictional character confirmed | Not automatable (unverified) |
| Higgsfield, Arcads, Argil, Creatify, Topview, Synthesia, D-ID | all-in-one actor/UGC platforms | Script | — | Arcads/Argil/Higgsfield pricing pages broken or unclear as of Jul 17 2026 [16]. Creatify Aurora $0.14/s [8] | — | No independent realism data. A Playcut benchmark with measured metrics is still "upcoming" [16] | Not shortlisted |

**TTS** (cost per video at ~650 characters):

| Service | Price | Per video | Notes |
|---|---|---|---|
| ElevenLabs v3 | $0.10 per 1K characters [17] | ~$0.07 | Most expressive; voice design gives a fixed `voice_id` |
| Cartesia Sonic 3.6 | — | — | #1 on the Artificial Analysis blind arena [17] |
| Fish Audio S2.1 Pro | ~$0.014/min [17] | ~$0.01 | Cheapest |

MiniMax was not verified.

**Stills:** Nano Banana 2 (`gemini-3.1-flash-image`) costs **$0.045–$0.151 per image** depending on resolution [18].

---

## 2. Scoring the three architectures

Scores run 1–5 (5 = best). Monthly cost assumes 750 videos and a 20% retry allowance.

| | (a) Single call: Gemini Omni 1.1 Flash or Veo 3.1 (ref + script → finished video with voice) | (b) Still + TTS + lip-sync, 3 calls (Nano Banana 2 → ElevenLabs v3 → Kling Avatar v2 Std) | (c) All-in-one platform API (HeyGen Photo Avatar IV / Hedra) |
|---|---|---|---|
| **Realism** | 4: full scene, natural camera and motion | 4: best verified sync and hands among audio-driven models [6] | 3: talking-portrait look [8] |
| **Character consistency** (face) | 3: re-derived every call. Omni needs a 3 s video ref [12]. Drift over hundreds of videos not measured | **5**: every clip is anchored to an approved still | 4: one saved avatar |
| **Voice consistency** | **2**: voice is generated per call, with no voice-ID lock found | **5**: one fixed ElevenLabs `voice_id` per character | 4–5: saved voice |
| **Cost** at 25/day | Omni ~$3,600/mo. Veo Lite ~$1,800/mo, but 8 s clips must be stitched | ~$2,150/mo at 100% avatar runtime; ~$1,100 with the hybrid edit (§3) | Hedra 540p ~$900. Hedra 720p / HeyGen ~$1,800 |
| **Automation friction** | **5**: 1 call (plus extensions) | 3: 3 calls + ffmpeg | 4: 1–2 calls |
| **Platform/policy risk** | Same labeling duty everywhere (§5). Google embeds SynthID/C2PA, so expect auto-labeling | Same. Separate vendors mean one outage can be swapped out | Single-vendor lock-in. Health-content ToS not verified for any vendor |
| **Total** | 21 | **25** | 22 |

---

## 3. Recommendation

### Primary stack: (b) Nano Banana 2 → ElevenLabs v3 → Kling AI Avatar v2 Standard on fal

**Confidence: MEDIUM.** The price and API facts are verified. The realism ranking rests on one head-to-head [6] plus one ad-production test [5]. Nothing tested older faces specifically.

**Pipeline per video, run from n8n:**

1. **Still.** Call `gemini-3.1-flash-image` with the locked character reference sheet plus a scene prompt to make one 9:16 still per scene. Reuse a library of about 30 approved stills per character instead of generating new ones every time; that is cheaper and holds consistency better.
2. **Voice.** Call ElevenLabs v3 TTS with the character's fixed `voice_id` → MP3.
3. **Animation.** POST `fal-ai/kling-video/ai-avatar/v2/standard` with `{image_url, audio_url, prompt}`, using the queue API with a webhook back to n8n.
4. **Assembly.** ffmpeg adds captions, b-roll cutaways and music → publish.

**Cost per 40 s video:**

| Item | Cost |
|---|---|
| Kling Standard ($0.0562 × 40 s) | $2.25 |
| ElevenLabs v3 | $0.07 |
| Still (amortized) | ~$0.05 |
| **Base total** | **≈ $2.37** |
| **With 20% retries** | **≈ $2.85** |

- **Full on-camera runtime:** ≈ **$2,140/mo** at 25/day, which is over the stretch cap. At 20/day it is about $1,700/mo.
- **Hybrid edit (Yang Mun-style, recommended):** the avatar talks for about 50% of runtime (hook, key lines, CTA). The rest is the same voice track over Ken-Burns stills and kitchen b-roll, done with ffmpeg and no AI call. That comes to **≈ $1.45/video, ≈ $1,090/mo**. This is the only verified way to land near $1k without dropping to 540p.

### Backup stack: same still and voice → Hedra Character-3 API

**Confidence: MEDIUM-LOW.**

- One call, up to 10 min, audio-driven, so the voice stays locked [7].
- 720p costs $2.00/video (≈ $1,800/mo at full runtime). 540p costs $1.00/video (≈ $900/mo at full runtime, ≈ $500 hybrid) — the only full-runtime option under $1k.
- The quality trade-off is per VEED, a competitor [8]. Swapping to it only changes the step-3 endpoint.
- HeyGen Photo Avatar IV ($0.05/s, if that is correct [9]) is the alternate. The price conflict needs settling first [8].

### Fewest moving pieces: Gemini Omni 1.1 Flash, single call (prompt + 3 s character video ref → 40 s video with voice)

**Confidence: LOW.** The model is 5 weeks old and the evidence comes mostly from secondary sources [5][12].

What it gives up:

1. **Voice identity.** No locked voice was found, so the "same grandma" can sound different between videos. This is the main reason it is not the primary.
2. **Cost.** About $4 per video, ≈ $3,600/mo with retries — over budget.
3. **Reliability.** About a 15% stutter rate [5].
4. **Weaker face anchoring** than a fixed still.

Veo 3.1 Lite is cheaper (≈ $2/video) but uses short clips that have to be stitched, and voice drift across clips is likely. Sora 2 is unavailable [14].

---

## 4. 48-hour bake-off protocol (no spend until approved; est. ≤ $120 total)

**Scripts.** Write these to match the actual CHARACTERS.md / SCRIPTS.md voice:

- **S1:** 30 s, Chang Yin, kitchen tip, close-up, fast hook.
- **S2:** 45 s, Sun Yoon, strength cue with hand gestures, medium shot.
- **S3:** 50 s, two-character exchange (stresses identity and voice switching).

**Contenders:** 3 options × 3 scripts, 2 takes each = 18 renders.

| Option | Setup | Est. cost |
|---|---|---|
| **A** (primary) | Identical NB2 still + ElevenLabs v3 audio → Kling Avatar v2 Standard. Add 1 Pro take per script as the ceiling | ~$15 + ~$15 |
| **B** (backup) | The **same** still + audio → Hedra Character-3 at 720p and 540p. Isolates the animator as the only variable | ~$15 |
| **C** (single call) | Gemini Omni 1.1 Flash with a 3 s character reference clip. Plus 1 take on Veo 3.1 Fast with reference images | ~$40 |

**What to measure** (enter in a sheet per render):

1. **Blind realism:** 5+ raters aged 55+, mixed into 5 real UGC clips; "real or AI?" and 1–5 naturalness. This is the deciding metric.
2. **Lip-sync:** SyncNet LSE-C/LSE-D (open source), plus a manual check of plosives (p/b/m) and teeth.
3. **Face consistency:** ArcFace cosine similarity of 10 frames per render vs the master reference. Pass if ≥ 0.6 average and no frame < 0.5.
4. **Voice consistency:** speaker-embedding similarity (e.g., Resemblyzer) across all of a character's renders. Matters most for option C.
5. **Older-face artifacts:** wrinkle "swimming," teeth/dentures, neck skin, glasses, and hand count/shape in S2.
6. **Operations:** failure/retry rate, wall-clock latency per 40 s, API errors or content-filter refusals on health words (e.g., "blood pressure," "joint pain"), and vendor ToS on health claims and synthetic personas.
7. **Unit economics:** actual $ per *usable* video (cost ÷ pass rate) × 750/mo.

**Decision rule:** pick the cheapest option within 0.3 naturalness points of the best that also passes consistency. If no option under $0.067/s passes, run the hybrid edit on A.

---

## 5. Platform rules (Oct 2026) that affect tool choice

- **Instagram (announced Aug 31, 2026):** a profile whose featured person is AI-generated must use the **"AI-generated profile" label**. Undisclosed accounts get reach suppressed; labeled ones are "not penalized simply for having an AI-generated person" [19]. → Label all 4 pages from day one. Tool choice does not change this.
- **TikTok:** realistic AI people and cloned voices must be labeled. TikTok **auto-labels from C2PA metadata** and escalates from reduced reach to removal or suspension [20]. → Don't strip C2PA/metadata (stripping looks like evasion). Toggle the AIGC label in the posting API.
- **YouTube:** tick the "altered or synthetic content" disclosure. Under the **inauthentic-content policy**, templated, low-variation, high-volume AI uploads lose monetization. One January 2026 enforcement wave terminated 16 AI channels [21]. → **The biggest risk to the repost plan is YouTube, not tool choice.** Vary formats, keep the human editorial layer real, and don't push all 25 videos a day to one YT channel.
- **Health content:** none of the vendor ToS on health topics were verified. Check them in the bake-off (step 6), and route claims through the existing SAFETY_RULES.md.

**Where evidence is thin:**

- No benchmark of lip-sync on **older faces** was found.
- No independent test of **identity drift over hundreds of videos** for any tool.
- All-in-one platforms (Arcads, Argil, Higgsfield, Captions) have no measured head-to-heads; Playcut's lab metrics are not yet released [16].
- The Kling Avatar max clip length isn't on fal's page.
- HeyGen API pricing conflicts between sources.

---

## Sources
1. fal — Kling AI Avatar v2 Standard: https://fal.ai/models/fal-ai/kling-video/ai-avatar/v2/standard
2. fal — Kling AI Avatar v2 Pro / API ref: https://fal.ai/models/fal-ai/kling-video/ai-avatar/v2/pro ; https://fal.ai/docs/model-api-reference/video-generation-api/kling-video-ai-avatar-v2
3. fal — OmniHuman 1.5: https://fal.ai/models/fal-ai/bytedance/omnihuman/v1.5/llms.txt
4. VidCost — Gemini API Veo per-second prices and model IDs: https://vidcost.com/api/gemini-api/ (also https://costgoat.com/pricing/google-veo, https://www.aifreeapi.com/en/posts/veo-3-1-pricing)
5. MaxFusion — lip-sync test across video models, Jul 2026: https://maxfusion.ai/blog/ai-video-models-lip-sync-2026
6. PiAPI — OmniHuman 1.5 vs Kling AI Avatar: https://piapi.ai/blogs/omnihuman-1-5-vs-kling-ai-avatar
7. Magic Hour — Hedra Character-3 guide and API pricing: https://magichour.ai/blog/guide-to-hedra-ai
8. VEED — Best lip-sync API 2026 (vendor-authored): https://www.veed.io/learn/best-lipsync-api
9. RealtimeAvatar — HeyGen API pricing explained: https://realtimeavatar.ai/blog/heygen-api-pricing-explained
10. fal — InfiniteTalk: https://fal.ai/models/fal-ai/infinitalk
11. Google — Gemini API video docs: https://ai.google.dev/gemini-api/docs/video
12. eesel — Gemini Omni 1.1 Flash pricing: https://www.eesel.ai/blog/gemini-omni-1-1-flash-pricing
13. fal — Seedance 2.5 vs 2.0: https://fal.ai/learn/devs/seedance-2-5-vs-seedance-2-0
14. Sora 2 API shutdown: https://pasqualepillitteri.it/en/news/18764/openai-sora2-api-dismessa-en ; https://help.apiyi.com/en/sora-2-api-shutdown-alternatives-2026-en.html
15. Prizmad — Captions AI review (competitor-authored), Jul 2026: https://prizmad.com/review/captions-ai
16. Playcut — AI Actor Benchmark v0.9, Jul 17 2026 (vendor-authored): https://playcut.ai/benchmarks/ai-actors/
17. TeamDay — Best AI voice models, Sep 2026: https://www.teamday.ai/blog/best-ai-voice-models-2026
18. Google — Gemini API pricing (Nano Banana 2): https://ai.google.dev/gemini-api/docs/pricing
19. TechCrunch — Instagram limits undisclosed AI profiles, Aug 31 2026: https://techcrunch.com/2026/08/31/instagram-puts-new-limits-on-undisclosed-ai-profiles/
20. Hypelive — TikTok AI content rules 2026: https://www.hypelive.io/en/blog/tiktok-ai-content-rules-2026
21. Lenspov — YouTube inauthentic-content policy 2026: https://lenspov.com/articles/youtube-ai-content-demonetization-2026
