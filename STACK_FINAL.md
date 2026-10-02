# STACK_FINAL: the no-waste video stack for Chang Yin & Sun Yoon (verified Oct 2, 2026)

Supersedes the cost sections of STACK_DECISION.md and STACK_AUDIT_SUB1K.md. Planning numbers are unchanged: **25 unique masters/day, 750/month, 40 s average**, two locked characters, n8n end to end.

**Client rule applied to every line:** keep a dollar only if it changes what the viewer sees or hears, or what content is possible.

**Method.** I re-read STACK_DECISION, STACK_AUDIT_SUB1K, COSTS, PIPELINE and CONTENT_SYSTEM, then ran 28 web searches and fetches. That is 3 over the 25 budget, spent on Kling vendor pricing pages that would not render. I made no spending, no accounts and no generation calls. Anything marked [A] is an assumption that the bake-off (section 7) has to measure.

---

## 0. Answer

**Recommended: Tier B "no-waste ≤ $1K."** It costs **≈ $1.28 per video**, which is **≈ $960/month in generation** at 25 per day. Fixed costs add about $480/month on top, plus a one-time performer shoot.

Two upgrades from Tier A are wired in as switches. Each one turns on only if the bake-off shows viewers can see the difference:

- **Kling Avatar Pro on medium-shot hooks:** about +$180/month.
- **Motion Control v3 for exercise demos:** about +$60/month.

With both on, Tier B is about $1,200/month. **Confidence: MEDIUM.** The prices are verified. The quality boundaries come from one Std-vs-Pro comparison and from house rules, not viewer data.

The biggest finding is that **most of the spend in the current models is invisible**:

- **The talking-head lane runs lip-sync over the whole audio track and then trims it.** COSTS.md §6 lever 1 says render_day1.py does this, so about half of the avatar seconds are bought and then thrown away.
- **Full-runtime avatar (the $2,140/month "full" stack) pays for frames the content system bans.** CONTENT_SYSTEM.md's house rules are "show-not-tell (≤30% talking head for Chang)" and "frame 1 = motion or prop." So the hybrid edit is the house format, not a compromise.
- **Veo inserts are about 40% of COSTS.md's per-day bill, and they are generated fresh for every master on fal at $0.15/s.** Most of that B-roll has no character in it and could be reused.

---

## 1. Waste audit: money that doesn't reach the screen

Savings are at 750 videos/month.

| # | Waste line | Evidence | Fix | Saving / month | Viewer impact |
|---|---|---|---|---|---|
| W1 | **Lip-syncing the whole track and then trimming it.** render_day1.py renders about 50 s of lip-sync per master | COSTS.md §1 lane recipe and §6 lever 1 | Slice the ElevenLabs audio first. Send only the on-camera windows (hook, mid beat, close, and any 4 s platform CTA swap) to `fal-ai/kling-video/ai-avatar/v2/standard` | **≈ $1,000+** against the coded pipeline (avatar seconds per master drop from ~50 to 10–14) | None. The trimmed frames never aired |
| W2 | **Fresh Veo inserts for every master, through fal at $0.15/s** | COSTS.md: Veo is ~40% of production. Gemini API direct is $0.10/s for Fast, and Lite is cheaper [COSTS §1; STACK_DECISION 4] | (a) Build a **reusable B-roll library** of about 300 character-free 6 s clips per month: hands, food, steam, tea, chairs, parks. (b) Generate per-video inserts only when the script names a specific action, and call **Gemini direct** for them | **≈ $1,500+** against the COSTS lane recipe (3 × 8 s Veo per master) | None if the library rotates. **Rule:** no clip is reused on the same page within 30 days |
| W3 | **Re-rendering 40 s when one beat fails** | fal does not bill server errors (HTTP ≥ 500) or queue time [fal-pricing]. Content/QA rejects are billed | Animate in **slices**, so a reject reruns 6 s instead of 40 s. Gate the inputs before the expensive step (W4) | Retry factor drops from 1.2 to ~1.15 [A]. About $30–60/month | None |
| W4 | **Bad inputs reaching the animator** | Retry sources are a bad still or bad audio. ElevenLabs v4 pronunciation accuracy is 91.7% vs 85.6% for v3 [decoder] | 1. Keep a **pre-validated still library**: each still passes the ArcFace check once and is then reused. 2. Run an **ASR check of the TTS output against the script** before animating (Scribe v2 is $0.22 per hour of audio, about $0.002 per video) [EL-api]. 3. Test `eleven_v4` (same $0.08/1K list price as v3) to cut audio retakes | Included in W3 | Fewer mispronounced words on screen |
| W5 | **"Prompt caching" and seed locking of the identity reference** | Nano Banana 2 has no context caching listed. A reference image costs input tokens at $0.50/M (≈ $0.0006 per image, assuming ~1,290 tokens) [gemini-pricing] | **Drop it.** It isn't a lever. The approved still is what locks identity, not a seed | $0 | n/a |
| W6 | **Stills at standard price** | Nano Banana 2 Batch API is 50% off: 2K costs $0.050 vs $0.101 [gemini-pricing] | Make every library still through Batch. They are not latency-critical | ≈ $20–40 | None. Same model and same output |
| W7 | **4K anything** | Instagram targets 1080×1920 and has no 4K playback. It re-encodes uploads, and 1080p at 5–8 Mbps looks sharper after compression than oversized uploads [mallary]. Kling official 4K is $0.42/s vs $0.084–0.14/s [aireiter]. Nano Banana 2 at 4K is $0.151 vs $0.101 at 2K | Kling Avatar already outputs 1080p at 48 fps [piapi-avatar]. **Never upscale.** Export 1080×1920 at 30 fps, 5–8 Mbps. Cap stills at 2K | Avoided cost | None. The platform discards it |
| W8 | **Frame rate** | Kling avatar, lip-sync and Motion Control are priced per second, not per frame [fal pages] | Not a cost lever. Convert 48 fps to 30 fps in ffmpeg (a 30 fps default is recommended [mallary]) | $0 | None |
| W9 | **Paying for rounding** | Kling LipSync bills in 5 s increments [STACK_AUDIT A]. Avatar rounding is not published | Cut LipSync slices to multiples of 5 s. Measure avatar billing granularity in the bake-off | Up to 20% on LipSync seconds | None |
| W10 | **Oversized fixed lines** | Assembly is ~100 files/day × 1.5 CPU-min = 150 CPU-min/day, about 3% of one 8-vCPU box. COSTS.md budgets **2 boxes** | **One** box (≈ $90 → $0). One Vercel seat, not two (−$20). **ElevenLabs on pay-as-you-go** at $0.08/1K: ~0.5–0.6M characters/month comes to $40–50 with no plan tier. Keep Creator ($22) only if voice design or cloning requires a plan. Hold the $500 quarterly performer refresh until the library actually has gaps | ≈ $110–280 | None |
| W11 | **Vendor markups that buy nothing** | See section 4 | Veo goes direct through the Google key you already hold. Kling stays on fal | ≈ $0–60 | None |

**What I did not cut:** ElevenLabs voice (about 3% of the bill and audible 100% of the time), human compliance review, ManyChat (it carries the CTA keyword funnel), and the performer shoot (section 3).

---

## 2. Where paying more is the right call

| Item | Delta | Viewer-visible evidence | Verdict |
|---|---|---|---|
| **Kling Avatar v2 Pro on the hook, medium/wide shots only** (6 s) | +$0.41 per affected video (6 s × $0.059 × 1.15). At ~60% of hooks that is ≈ **+$180/month** | In PiAPI's Std-vs-Pro test, Standard was "very stiff, with arms fixed at the sides" and "flatter." Pro showed "natural hand gestures," "subtle eye movement" and posture shifts. Lip-sync was "reasonably solid" in both [piapi-guide] | **Pay, but only when hands or torso are in frame.** On close-ups the difference is out of frame, so that would be waste. Medium confidence; confirm in bake-off B1 |
| **Motion Control v3 Std ($0.126/s) instead of v2.6 Std ($0.07/s) for exercise demos** | ≈ +$0.55 per exercise video, ≈ **+$60/month** | Exercise form is the product and the safety moat (PIPELINE.md: "we never let a generative model invent an exercise"). v3 is the newer tier [fal-mc3; fal-mc26]. I found no head-to-head | **Switch, conditional on bake-off B3.** A form error on screen costs more than $60/month |
| **One performer shoot** (COSTS: $1.5–3K, assumed) | One-time cost | This is the only route to correct exercise motion: Kling Motion Control maps a real performer's movement onto the character. Without it the exercise lane (about 1 master in 7) can't be made honestly | **Pay.** Skip the crew: a 60+ performer, a tripod, three angles. The quarterly refresh happens only when the library has gaps |
| **2K source stills for the avatar** (vs 1K) | +$0.016 per still through Batch, about $2/month | Kling outputs 1080p, and older faces read as "AI" first through skin texture (STACK_AUDIT §3) | **Pay.** The cost is trivial and the face detail is on screen |
| **ElevenLabs v3/v4 instead of Fish S2-pro** | ≈ +$40/month | Fish actually scores higher on speaker similarity (4.03 vs 3.68) [STACK_AUDIT P]. Expressiveness for older voices is unmeasured. v4 adds laughter and whisper cues and better long-form consistency [decoder] | **Keep ElevenLabs in Tier B.** Switch only if Fish wins blind test B5 |
| Veo 3.1 **Fast** instead of **Lite** for per-video inserts | +$0.30 per 6 s insert | Lite has "lower-resolution output... less fine-grained detail and slightly weaker temporal consistency" [mindstudio] | **Tier A only.** Inserts run 1–3 s on screen behind captions. Re-test in B2 |

---

## 3. Flexibility check: every CONTENT_SYSTEM concept, cheapest lane that keeps it

| Concept (formats) | Cheapest lane that keeps the concept | Tier B cost/video | Needs the expensive lane? |
|---|---|---|---|
| **Talking head** (F07, F10, F26, F27, F35, F24, F33) | Avatar Std slices (~13 s: hook, mid beat, close), with voice over library B-roll and prop stills for the rest. That matches "≤30% talking head" | ≈ $1.26 | No |
| **Kitchen demo** (F06, F12, F18, F31) | Avatar Std 10 s, plus **one** fresh recipe-specific insert (Veo 3.1 Lite direct, 6 s), plus library hands/steam/plating clips | ≈ $1.24 | No. The fresh insert is the concept, though: removing it (Tier C on talk/duo) turns a recipe into stock footage |
| **Exercise demo** (F01–F03, F14, F15, F17, F20, F22, F25, F34) | **Kling Motion Control from the performer's driving clips.** Each render is cached and may be reused once on a different page or wardrobe, never the same page within 30 days. Avatar Std for the spoken cue | ≈ $1.44 | **Yes: the shoot is mandatory.** v2.6 vs v3 is the price toggle |
| **Duo scene** (F08, F23, F34, R4) | **Shot/reverse-shot**: two single-face avatar renders cut together, plus one silent two-shot (Lite i2v from a Nano Banana 2 two-shot still) | ≈ $1.26 | No. **A true two-shot with both people talking in one frame is not covered** by any single-person avatar model. Keep it out of scripts, or use the exception budget below |
| **Story bits / walk & talk** (F19 Market Walk, F29 Walk & Talk) | i2v walking base clip (Veo Fast direct, 10 s) → **Kling LipSync** `fal-ai/kling-video/lipsync/audio-to-video` at $0.014/s (2–10 s video per call) | ≈ $1.26 + **$1.35** | **Yes: exception lane.** A still-anchored avatar can't walk |
| **B-roll / anatomy / stat / study cards** (F13, F16, F28, F30) | Library clips plus Remotion/ffmpeg graphics | ≈ $0.10 | No |
| **Static** (F36–F39 carousels, text posts) | Nano Banana 2 Batch stills plus graphics | ≈ $0.05 | No |

**Exception budget (included in the Tier B monthly):** **$100/month**, which covers:

- **About 40 walk-and-talk videos** (~$54).
- **Up to 10 test renders of a true two-shot dialogue** (~$30). Try Kling LipSync on a two-person i2v clip; multi-face support is **unverified**, LOW confidence.
- **About $16 of slack.**

n8n draws this budget down and refuses exception-lane briefs once it is spent.

---

## 4. Vendor-direct vs aggregator

| Component | Direct | Aggregator | Delta | Decision |
|---|---|---|---|---|
| Kling AI Avatar v2 | Official Kling API: prepaid packages only, **$700 minimum for 5,000 units, valid 180 days** [aireiter]. The avatar unit price would not render on kling.ai [kling-dev] | fal Std **$0.0562/s**, Pro $0.115/s [fal-avatar]. PiAPI Std **$0.052/s** [piapi-avatar] | PiAPI is ~7% cheaper: ≈ $45/month on ~11K avatar s/month | **Stay on fal.** One key covers Avatar, LipSync and Motion Control. fal does not bill 5xx errors or queue time [fal-pricing]. 7% does not pay for a fourth vendor or a 180-day prepaid lock. Ask fal for enterprise pricing ("custom per-endpoint pricing and volume discounts" [fal-pricing]) once spend passes ~$1.5K/month |
| Veo 3.1 inserts and library | Gemini API: Fast $0.10/s, Lite ≈ $0.05/s [STACK_DECISION 4; teamday] | fal $0.15/s [COSTS] | **−33% to −67%** | **Go direct.** The Google key already exists for Nano Banana 2, so this adds no moving piece |
| Stills | Gemini API, Batch at −50% [gemini-pricing] | — | — | Direct, through Batch |
| Voice | ElevenLabs direct: PAYG v3 $0.08/1K, v4 $0.08/1K list ($0.022 promo until Oct 12) [EL-api] | — | — | Direct. The voice_id lives there |
| Hedra Character-3 | Hedra API $0.05/s at 720p [STACK_DECISION 7] | — | — | Backup only. Same still and audio, swap the endpoint |

**Result: 3 keys (fal, Google, ElevenLabs).** That is the fewest moving pieces that still avoids paying markup on the second-largest line.

---

## 5. Tiered budget model (750 videos/month, generation only)

Lane mix follows PIPELINE.md's 3:2:1:1 ratio: talk 43%, kitchen 29%, exercise 14%, duo 14%. Retry factors [A]: avatar ×1.15 (sliced and gated), Motion Control ×1.3, Veo ×1.2. TTS is ~650 characters per video.

| | **Tier A: no-waste best** | **Tier B: no-waste ≤ $1K (recommended)** | **Tier C: floor** |
|---|---|---|---|
| Stills | `gemini-3.1-flash-image` 2K **Batch**, 2 new per video | Same, 1 new per video plus the rotated library | Library only, 1K Batch |
| Voice | `eleven_v4` (or `eleven_v3`), fixed voice_id | Same | Fish Audio S2-pro (only if it passes B5) |
| On camera | `fal-ai/kling-video/ai-avatar/v2/standard`, 12–16 s. **`…/v2/pro` for the 6 s hook on medium shots** | `…/ai-avatar/v2/standard`, 10–14 s | `…/ai-avatar/v2/standard`, 6–10 s (hook and close only) |
| Exercise motion | `fal-ai/kling-video/v3/standard/motion-control`, fresh per video | `fal-ai/kling-video/v2.6/standard/motion-control`, cached and reused 2× | v2.6 Std, reused 3× |
| Inserts | `veo-3.1-fast-generate-preview` direct, 1–2 fresh per video | `veo-3.1-lite-generate-preview` direct. Kitchen gets 1 fresh; talk and duo only when the script names an action (~50%) | Lite, kitchen only |
| B-roll library | ~300 clips/month on Veo Fast | ~300 clips/month on Veo Lite | Lite library plus ffmpeg Ken Burns |
| Walk & talk | Veo Fast base → `fal-ai/kling-video/lipsync/audio-to-video` | Same, inside the $100 exception cap | Not offered |
| **Per video** | **≈ $2.73** | **≈ $1.28** | **≈ $0.88** |
| **Month at 25/day** | **≈ $2,050** | **≈ $960** (+$180 / +$60 if the switches flip) | **≈ $660** |

**Fixed costs, every tier (from COSTS.md, after the W10 cuts):**

| Line | Monthly |
|---|---|
| Claude generation + judge | ≈ $100 |
| Human review | ≈ $85 |
| 1 VPS [A] | $90 |
| Supabase | $40 |
| Vercel (1 seat) | $20 |
| Resend | $20 |
| ManyChat (4 pages) | $116 |
| R2 | ≈ $5 |
| **Total** | **≈ $480/month** |
| Performer shoot | one-time, $1.5–3K [A] |

**What the viewer gains or loses between tiers:**

- **C → B:** the recipe or prop the script talks about actually appears on screen instead of generic footage. The on-camera face gets about 40% more time, the voice stays the tested ElevenLabs voice, and exercise footage repeats half as often. Without that, repeated exercise footage risks YouTube's "low-variation" flag.
- **B → A:** gestures and posture on medium-shot hooks; somewhat crisper, steadier inserts; exercise renders that never repeat. **Close-up talking frames are identical between A and B.**

**Why B:** every Tier A dollar that isn't in B is either invisible on close-ups or not yet proven visible. The two A items that plausibly are visible are wired as bake-off switches, not dropped. Tier C cuts things the concept needs: kitchen inserts, voice quality, and on-camera time that is already at the ≤30% house rule. Headroom under $1K is thin (~$40), so n8n keeps the month-to-date guardrail from STACK_AUDIT §6: above $900 it drops the mid beat.

---

## 6. Things I could not verify

- Kling official avatar unit prices (the page would not render).
- Avatar billing rounding.
- Kling LipSync quality on older faces, and whether it handles multiple faces.
- Any viewer study comparing Veo Lite and Fast inserts.
- Whether ElevenLabs voice design requires a paid plan.
- Hetzner box pricing [A].
- Retry rates. Every ×1.15 / ×1.3 factor above is an assumption.

---

## 7. 48-hour bake-off: updated to test the exact tier boundaries

This builds on STACK_DECISION §4 and STACK_AUDIT §7 (same S1–S3 scripts, same stills, same audio, 55+ blind raters). It adds about $60, for a total of ≈ $225, and nothing runs until it is approved.

| ID | Boundary | Test | Pass rule |
|---|---|---|---|
| **B1** | A/B: Pro hook | 6 s hook, Std vs Pro, close-up and medium shot (S1, S2) | Pro flips on **only for shot types** where raters prefer it ≥60% and naturalness is +0.3 |
| **B2** | A/B: inserts | Same 6 s insert from Veo Fast vs Lite, shown in the cut behind captions | Lite stays unless raters spot it at more than chance |
| **B3** | A/B: Motion Control | One driving clip (sit-to-stand, 45° angle) through v2.6 Std vs v3 Std. A PT checks form, plus hand/foot artifact counts | v3 if v2.6 fails form or artifacts on ≥1 in 5 |
| **B4** | B/C: on-camera time | Same S1 at 14 s vs 10 s on camera | Keep 14 s if "keep watching" preference ≥55% |
| **B5** | B/C: voice | `eleven_v4` vs `eleven_v3` vs Fish S2-pro on the same lines: blind naturalness, Resemblyzer consistency, ASR word-error rate | The cheapest voice within 0.2 naturalness of the best |
| **B6** | B/C: kitchen insert | S1 with a fresh recipe insert vs library-only | Fresh stays if recall of "what she made" is +20% |
| **B7** | Waste check | Log every render's billed seconds against output seconds, and the rejects per slice with gated stills and ASR-checked audio | Replace the [A] retry factors with measured ones and confirm avatar billing rounding |
| **B8** | Vendor | Same input on fal Std vs PiAPI Std: diff the frames, latency and errors | Switch only if PiAPI is identical **and** fal declines volume pricing |
| **B9** | Exception lane | 2 walk-and-talk renders, plus 2 attempts at a two-person LipSync | Exception lane approved or struck |
| **B10** | Stills | 1K vs 2K source still, ArcFace score plus phone viewing of skin texture | 2K stays unless no rater can tell |

**Decision rule:**

- **Ship Tier B.** Flip each switch (B1, B3) only on a pass.
- **Re-cost from the measured B7 numbers.** If B7 measures retries above ×1.3, fix the inputs before spending more on models.

---

## Sources

The bracketed tags above map to these sources. Other citations point to the repo files (COSTS.md, PIPELINE.md, CONTENT_SYSTEM.md), and numbered tags like [STACK_DECISION 4] or [STACK_AUDIT P] point to those files' own source lists.

- [fal-avatar] https://fal.ai/models/fal-ai/kling-video/ai-avatar/v2/standard
- [fal-pricing] https://fal.ai/docs/documentation/model-apis/pricing (5xx errors and queue time not billed; enterprise volume pricing)
- [fal-mc3] https://fal.ai/models/fal-ai/kling-video/v3/standard/motion-control ($0.126/s)
- [fal-mc26] https://fal.ai/models/fal-ai/kling-video/v2.6/standard/motion-control ($0.07/s)
- [piapi-avatar] https://piapi.ai/kling-ai-avatar (Std $0.052/s; 1080p at 48 fps; up to 1 min)
- [piapi-guide] https://piapi.ai/blogs/kling-ai-avatar-guide-standard-vs-pro
- https://replicate.com/kwaivgi/kling-avatar-v2 (Pro: "better facial detail and smoother motion"; 1080p at 48 fps)
- [aireiter] https://aireiter.com/blog/kling-api-pricing (official Kling $0.084–0.42/s; $700 / 5,000-unit prepaid packages, 180-day validity)
- [kling-dev] https://kling.ai/dev/pricing (did not render)
- [gemini-pricing] https://ai.google.dev/gemini-api/docs/pricing (Nano Banana 2 standard and Batch per-image prices; no context caching listed)
- [EL-api] https://elevenlabs.io/pricing/api (v3 / v4 $0.08/1K; v4 promo $0.022 until Oct 12; pay-as-you-go)
- [decoder] https://the-decoder.com/elevenlabs-new-v4-speech-model-makes-ai-voices-more-expressive-and-consistent/ (v4 released Sep 29, 2026; pronunciation 91.7% vs 85.6%)
- [mindstudio] https://www.mindstudio.ai/blog/veo-3-1-vs-fast-vs-light-comparison
- [teamday] https://www.teamday.ai/blog/ai-api-pricing-comparison-2026 (Veo 3.1 Lite in the $0.03–0.05/s range at 720p)
- [mallary] https://mallary.ai/blog/instagram-reel-resolution (1080×1920 target, no 4K playback, 30 fps, 5–8 Mbps)
- https://z.tools/blog/ai-lipsync-models-comparison (lip-sync artifact patterns: teeth, cheeks)
