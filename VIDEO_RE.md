# VIDEO_RE: How the Yang Mun videos are made, and a better production recipe for Chang Yin and Sun Yoon

Frame-level forensic teardown of 26 Yang Mun videos (15 YouTube, 11 Instagram), followed by an upgraded production system for Chang Yin (a visibly strong 74-year-old retired welder who trains) and Sun Yoon (his wife).
Analysis date: 30 Sep 2026. Everything cited here can be reproduced from `/home/claude/rebuild/video/`.

---

## 0. Summary

**How Yang Mun is made.** The 2026 remedy reels on @yangmunus bring in almost all of the views. They are built like this:
1. **Nano Banana** (Gemini image) stills of "the monk + a prop" in a temple set.
2. Those stills go through **image-to-video in about 8-second units** (most likely Veo 3.x, possibly Kling). Recipe steps are shot as **faceless hands-only inserts**.
3. **One continuous ElevenLabs voice-over** is laid over the top. It is clean TTS with no room tone, no music and no SFX.
4. The clips are cut to that voice-over. **CapCut auto-captions** are added: small, white, lowercase, no punctuation.
5. The reel is exported at 720×1280 / 30 fps / about −17 LUFS and posted with a "comment HEAL" call to action.

The 2025 YouTube era used a different, simpler process: **one still image lip-synced for 60–105 s in a single take** (HeyGen Avatar IV, Hedra or InfiniteTalk class tools), at 25 fps, with no captions.

**What they do badly, and where we can beat them:**
- **No identity lock.** At least six different faces appear across the sample (key frame 12).
- **Wardrobe and religion changes.** Grey, navy, maroon, orange and Tibetan robes.
- **Five different synthetic voices.**
- **Loose lip-sync.** The mouth keeps moving through pauses in long talking shots.
- **Physics cheats.** Water turns wine-red; "gummies" that cannot set; an impossible transparent intestine prop.
- **Exercise demos are ripped footage of a real person.** In Dde36RZKQ‑V (15–44 s) a clinician in green scrubs is shown with his head cropped off, and a leftover video-player progress bar is still visible.
- **Unsupported medical claims and invented backstory.**

**Confidence levels:**

| Pipeline element | Confidence | Main evidence |
|---|---|---|
| ElevenLabs-class TTS voice | **High** | Same-voice speaker-embedding similarity of 0.97–0.99 across videos shot in different rooms; digital-silence floor between words (−70 to −180 dBFS); speech starts at exactly 0.00 s in 26/26 files |
| Nano Banana stills | **High** | Creator's own claim; SynthID reports; single-still single-take formats |
| CapCut-style auto-captions | **High** | Captions copy ASR errors, e.g. "walk A." for "walk away" in Dde6GjRBEVl at 30 s |
| Veo 3.x for the action shots | **Medium** | Longest shots ≤ about 9 s; a native 24 fps clip in xhu4iu8vVuY; legible brand text ("VapoRub") on a prop; SynthID reports. Kling 2.x/3.0 is the alternative |
| Audio-driven lip-sync tool for the 2025 single-take and 8.5‑min formats | **Medium** | Single 33–511 s takes with a static body |

---

## 1. Data acquisition and method (what was done, and what failed)

**Getting the videos.**
- **YouTube via yt-dlp failed.** Every googlevideo media URL returned HTTP 403, even with the nightly build and a bgutil PO-token server. The media URLs are bound to a single IP, and the egress pool here rotates IPs.
- **YouTube workaround:** a public cobalt instance (`api.cobalt.liubquanti.click`) was used for the MP4s. This is a remux of YouTube's own renditions, so the metadata is YouTube's rather than the creator's. One file, yt_V1t8IcG9dio, had corrupt data after 150 s on the first pull and was downloaded again cleanly at 720p.
- **Instagram:** yt-dlp got HTTP 429, so reels were pulled through `kkinstagram.com`, which 302-redirects to the original fbcdn MP4. Two reels returned thumbnails and one returned a connection reset; those three were fetched through cobalt instead.
- **Substitution:** the low performer Tla_hxhxWuk returned empty from every route, so 3daKowdg2Ig (415 views) was used in its place.

**What was measured, per video:**
- ffprobe and exiftool metadata, a raw `strings` scan, and an MP4 top-level box walk (looking for C2PA/JUMBF).
- Cut detection two ways: ffmpeg `select=gt(scene,0.3)` with `showinfo`, and a frame-difference detector. The scene 0.3 filter misses same-set cuts, so the frame-difference detector is the main one.
- Frames every 1 s (every 5 s for the long videos) plus hi-res frames at the timestamps of interest. About 1,400 frames were extracted. I viewed contact sheets for all 26 videos and full-resolution frames for 15.
- faster-whisper `small` transcripts with word timestamps.
- Resemblyzer speaker embeddings.
- Praat F0 (pitch).
- pyloudnorm LUFS.
- HPSS harmonic ratio inside speech gaps (a music-bed detector).
- MediaPipe FaceLandmarker mouth aperture in pauses vs speech (a lip-sync test).
- Tesseract OCR of the caption band at 4 fps.

**Files:**
- `video/raw/`: 26 MP4s
- `video/meta/`: ffprobe JSON, cuts, `audio_metrics.json`, `caption_ocr.json`
- `video/transcripts/`: JSON and TXT for every video
- `video/frames/<id>/`: all extracted frames
- `video/sheets*/`: contact sheets
- `video/hires/`: hi-res frames
- `video/key_frames/`: the 12 picks

---

## 2. Per-video forensics table

Column notes:
- **Voice cluster**: see §5.
- **Face**: see §4.1.
- **Shots**: counted with the frame-difference detector. For the itsyangmuns reels, the 2025 YouTube videos and the long videos, the single shot was confirmed by eye. The j8WR count is corrected, because its white caption boxes caused false positives.
- **WPM**: words across the span of speech.
- **Gap music**: the harmonic energy ratio in inter-word gaps. Above about 0.5 means a music bed is present.

| # | ID (platform) | Views | Era / order | Res / fps | Video bitrate | Dur (s) | Shots / avg shot length (s) | Format | Voice cluster | Words / WPM | F0 median (Hz) | Pauses ≥300 ms (mean s) | Gap music | LUFS | Caption style |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | DdmojIyKCTg (IG main) | 1M | Sep 2026 | 720×1280 / 30 | 987k | 29.0 | 6 / 4.8 | Prop demo, standing, courtyard | V2 | 73 / 153 | 157 | 8 (0.69) | 0.00 | −17.1 | lowercase white, ~70% height |
| 2 | Dde36RZKQ‑V (IG main) | 474K | 2026 | 720×1280 / 30 | 961k | 53.8 | 5 / 10.7 | Plate hook, then seated talking head with ripped exercise inset | V2 | 155 / 175 | 151 | 17 (0.37) | 0.00 | −17.1 | lowercase white |
| 3 | Ddzghllq1z0 (IG main) | 411K | 2026 | 720×1280 / 30 | 813k | 34.2 | 8 / 4.3 | Lime-on-blueberries, blender demo | V2 | 90 / 160 | 150 | 9 (0.53) | 0.02 | −17.2 | lowercase white |
| 4 | DdkLMjXK8sm (IG main) | 409K | 2026 | 720×1280 / 30 | 911k | 43.8 | about 12 real (19 detected) / 2.3 | "Natural ibuprofen" gummies; hands-only inserts | V2 | 115 / 158 | 152 | 13 (0.52) | 0.01 | −17.1 | lowercase white |
| 5 | Ddhjjc8qauR (IG main) | 305K | 2026 | 720×1280 / 30 | 765k | 43.0 | 9 / 4.8 | Honey-tomato blender demo | V2 | 115 / 161 | 149 | 11 (0.43) | 0.00 | −17.2 | lowercase white |
| 6 | Dd4w89RKBmd (IG main) | 196K | 2026 | 720×1280 / 30 | 892k | 48.2 | 10 / 4.8 | Transparent-gut prop, then lemon brew | V2 | 121 / 152 | 147 | 16 (0.54) | 0.00 | −17.2 | lowercase white, plus a stray bold "chicken." (5 s) |
| 7 | Ddbt6FgKACc (IG main) | 53.8K (low) | 2026 | 720×1280 / 30 | 797k | 46.6 | 11 / 4.2 | Herb bouquet talk with static AI-infographic insets | V2 | 108 / 140 | 149 | 17 (0.49) | 0.14 | −17.1 | lowercase white |
| 8 | Dd4qFQ‑lQLU (IG main) | 22K (low) | 2026 | 720×1280 / 30 | 937k | 38.1 | 6 / 6.3 | Salt-under-tongue, seated at stone table | V2 | 94 / 150 | 145 | 5 (0.64) | 0.00 | −17.1 | lowercase white |
| 9 | Dde6GjRBEVl (IG itsyangmuns) | 133K | 2026 | 720×1280 / 25 | 1094k | 50.2 | 1 / 50 | Floor-seated, hand on chest, single take | V3 | 153 / 184 | 142 | 20 (0.47) | **0.69** | −17.2 | Condensed title-case, 1 line |
| 10 | DdbshGColTp (IG itsyangmuns) | 92.7K | 2026 | 720×1280 / 25, **48 kHz** | 869k | 33.2 | 1 / 33 | Chair-seated with candle; black title box | V4 | 96 / 176 | 143 | 15 (0.53) | 0.03 | −17.1 | Bold white multi-line, plus black title box |
| 11 | DdueaoKBHf6 (IG itsyangmuns) | 27K (low) | 2026 | 720×1280 / 25 | 969k | 45.5 | 1 / 45 | Standing, hand on chest; a background extra walks through | V3 | 135 / 179 | 147 | 17 (0.52) | **0.67** | −17.2 | Condensed, plus black title box |
| 12 | j8WRhcQvzRM (YT short) | **12.56M** (363K likes, 22K comments) | 10 Nov 2025 | 720×1280 / 25 | 1180k (Main profile) | 95.8 | 1 / 95.8 | Floor-seated, low table, open book, candle, high angle | V1 | 218 / 138 | 137 | 38 (0.49) | 0.09 | −17.1 | **Black bold on white rounded box**, mid-frame |
| 13 | Qdv6S7HonSM (YT) | 1.1M | 25 Nov 2025 | 1080×1920 / 25 | 2191k | 78.2 | 1 / 78 | Book and candles, golden hall, **no captions** | V1 | 188 / 145 | 132 | 23 (0.57) | 0.11 | −17.1 | none |
| 14 | 2qD_vrrcq3k (YT) | 953K | Nov–Dec 2025 | 1080×1920 / 25 | 2084k | 105.8 | 1 / 106 | Same template outdoors, navy robe, gestures | V1 | 236 / 135 | 141 | 36 (0.55) | 0.30 | −17.1 | none |
| 15 | Er2Ig4GM7z0 (YT) | 521K | late 2025 | 1080×1920 / 25 | 2126k | 65.2 | 1 / 65 | Book and candles, blue robe | V1 | 157 / 146 | 135 | 19 (0.53) | 0.10 | −17.1 | none |
| 16 | xkFzhFj0TkU (YT) | 372K | late 2025 | 1080×1920 / 25 | 1981k | 97.4 | 1 / 97 | Book, grey robe, golden Buddha | V1 | 241 / 150 | 139 | 28 (0.52) | 0.04 | −17.1 | none |
| 17 | CnzjV3QrO70 (YT) | 330K | late 2025 | 1080×1920 / 25 | 2120k | 83.2 | 1 / 83 | Book, grey robe, candle bottom | V1 | 189 / 137 | 138 | 33 (0.58) | 0.00 | −19.5 | none |
| 18 | FvoEDuYwEys (YT, "podcast" tag) | 259K | late 2025 | 1080×1920 / 25 | 2378k | 94.2 | 1 / 94 | Cross-legged on floor, blue work shirt | V1 | 220 / 141 | 130 | 32 (0.58) | 0.01 | −19.8 | none |
| 19 | b-m8-2M7M_4 (YT) | 188K | late 2025 | 1080×1920 / 25 | 1965k | 84.3 | 1 / 84 | Book, ochre-over-grey robe | V1 | 181 / 130 | 136 | 29 (0.51) | 0.03 | −19.8 | none |
| 20 | 6AP7bDlni0w (YT) | 188K | late 2025 | 1080×1920 / 25 | 2217k | 64.5 | 1 / 64 | Relationship/silence wisdom | V1 | 149 / 140 | 142 | 21 (0.53) | 0.03 | −17.1 | none |
| 21 | eFJbWl36_uk (YT) | 178K | late 2025 | 1080×1920 / 25 | 2157k | 80.8 | 1 / 81 | "5 things I will never do" | V1 | 193 / 145 | 134 | 23 (0.51) | 0.03 | −19.7 | none |
| 22 | ‑G_q4QpTskQ (YT) | 120 (low) | Sep 2026 (2nd newest) | 720×1280 / 30 | 1055k | 38.0 | 3 / 12.6 | Selfie-POV plate hook | V2 | 103 / 167 | 155 | 14 (0.41) | 0.01 | −17.1 | lowercase white |
| 23 | xhu4iu8vVuY (YT) | 259 (low) | 2026 | 720×1280 / **24** | 1440k | 33.7 | 8 / 4.2 | Patient treatment (VapoRub), Tibetan robe | V2 | 93 / 170 | 147 | 9 (0.42) | 0.01 | −17.1 | Bold white, black stroke, 4 lines |
| 24 | 3daKowdg2Ig (YT, substitute low) | 415 | 2026 | 720×1280 / 30 | 905k | 29.3 | 4 / 7.3 | Patient behind-ear sesame oil; book mock-up pops in | V2 | 78 / 162 | 156 | 6 (0.49) | 0.00 | lowercase, plus black title box |
| 25 | V1t8IcG9dio (YT long) | 302 | newest long | 1280×720 (orig. 1080p) / **24** | 1003k | 511.5 | 1 / 511 | 16:9 "podcast": boom mic, orange robe, hand on cheek the whole time | V5 | 1340 / 158 | 136 | 178 (0.71) | 0.23 | **−23.4** | NLE white with shadow, bottom |
| 26 | H‑Qbw7MnLQk (YT long) | 2,100 | long | 1920×1080 / **24** | 4294k | 414.1 | 1 / 414 | 16:9 guided meditation, eyes down, stool | V5 | 676 / 99 | 136 | 117 (1.77) | **0.85** | **−23.4** | NLE white, bottom |

The IG view counts come from the brief; the YouTube counts come from the channel scrape.

---

## 3. Container and provenance forensics

**No C2PA or JUMBF on any file.**
- Top-level boxes are `ftyp, moov, free, mdat` on Instagram and fragmented `ftyp, moov, (moof, mdat)…, mfra` on YouTube.
- There are no `uuid` or `jumb` boxes. A case-sensitive byte search for `c2pa`, `jumb`, `jumd` and `urn:c2pa` returns 0 hits.
- The single "C2pA" hit in b‑m8‑2M7M_4 is random mixed-case bytes inside `mdat`.
- Both platforms re-encode uploads and strip any Content Credentials that were there.
- SynthID is a pixel-level watermark and cannot be checked without Google's SynthID Detector, so we cannot confirm or rule it out here. It was reported externally (see the brief).

**Encoder and handler strings:**
- IG: video `encoder=AVC Coding`, handlers `VideoHandler` / `SoundHandler`, and zero dates (0000:00:00). This is Meta's transcoder; every creation-tool tag is gone.
- YT: handler "ISO Media file produced by Google Inc.", udta `artist=Yang Mun`, title set, and `encoder Lavf61.1.100` (added by the remux).
- **9 of the 10 2025 YouTube uploads still carry x264 SEI strings** in the H.264 stream, repeated 14–18 times: `x264 - core 155 r2901 7d0ff22` (j8WR, 2qD, 6AP7, Cnzj, Er2Ig, xkFz, b-m8, eFJb) and `x264 - core 165` (Qdv6, 25 Nov 2025). None of the 2026 uploads do.
  - This is weak evidence. It is consistent with a server-side renderer built on ffmpeg 4.x (x264 core 155 ships with those builds), such as a cloud avatar-render service, but YouTube renditions are not normally where creator SEI survives. We do not rely on it.

**Frame-rate signatures (strong, because platforms keep the source frame rate at or below 30):**
- **25 fps** for the 2025 YouTube single-takes and all itsyangmuns reels. 25 fps is the default output of HeyGen, InfiniteTalk and most talking-head lip-sync tools.
- **30 fps** for the yangmunus reels and the 2026 YouTube shorts. That is the CapCut mobile default export, so the action clips are re-timed to 30p in the editor.
- **24 fps** for xhu4iu8vVuY and both long-forms. 24 fps is Veo's native output (and a 24p NLE timeline). xhu4 is probably a Veo timeline exported without conforming.

**Loudness:**
- **22 of 26 files sit at −17.1 or −17.2 LUFS integrated.** Shorts on both platforms share a fixed loudness step in the export chain.
- The 2025 "podcast" batch sits at −19.5 to −19.8.
- The **long-forms sit at −23.4**, which is the EBU R128 broadcast target. That points to a desktop NLE loudness preset (Premiere, Resolve or Descript), so the long-forms were assembled on a different workstation than the shorts.

**Audio sample rate:** 44.1 kHz everywhere except DdbshGColTp at 48 kHz. That one is a different export path, and it is also the one with a different voice (V4).

---

## 4. Visual forensics

### 4.1 Identity: there is no identity lock

See key frame 12, which puts six face crops side by side.
- **Nov 2025 j8WR (12.56M views):** heavier face, visible ears, black-navy jacket, and something that looks like a thin lav cable.
- **2025 book series (Qdv6 / Er2Ig / xkFz / Cnzj / b-m8):** smaller, thinner faces that differ from video to video. Robes switch between grey, blue, navy and ochre.
- **2026 yangmunus (Dde36, Ddmoj, Ddzg, Ddhj, DdkL, Dd4w, Ddbt, Dd4q):** the **most stable** face (narrow skull, tall forehead, deep nasolabial folds) in a consistent maroon cross-collar robe. This is the one place they clearly used reference images.
- **xhu4iu8vVuY (2026 YT):** a different man again, dressed in Tibetan maroon and saffron with thangkas and a vajra bell. That is a religious-costume change.
- **itsyangmuns:** each video has a different older face in saffron robes. DdbshGColTp has fuller jowls; Dde6GjRBEVl is thinner.
- **Long-forms:** yet another face, in orange robe.

**What this means for us:** the audience does not seem to punish drift; the 12.56M-view video uses a face that never appears again. But drift is the first thing journalists point to as proof of fakery. For a character presented as openly AI with credentialed human reviewers, consistency is **brand equity**, not a way to dodge detection.

### 4.2 Shot grammar of the high performers (yangmunus, 2026)

The same four-part pattern repeats across the reels.

**A. Frame-0 action hook: the prop is moving at t=0.**
- DdmojIyKCTg 0–4.5 s: the monk tips a basket of sliced red onion into a clear glass pot, and the onions are mid-fall at 1–3 s (key frame 01).
- Ddzghllq1z0 0–8.1 s: a lime is squeezed over a mountain of blueberries at lens-level.
- Ddhjjc8qauR 0–2.8 s: a honey dipper drips onto a platter of tomato slices.
- Dde36RZKQ‑V 0–7.1 s: a rice plate is pushed toward a wide lens, open-mouthed smile, teeth visible (key frame 03).
- DdkLMjXK8sm 0–1.9 s: cupped hands of heart "gummies", faceless.
- Dd4w89RKBmd 0–13 s: food poured into a **transparent plastic intestine** (key frame 06). This prop is physically impossible and could only be made with AI.

**B. Recipe beats as 2–3 s inserts, often faceless.**
- DdkLMjXK8sm 11–34 s is shot at chest height with the face cropped out: turmeric into a jar, a dropper into a heart mold (key frame 05), unmolding.
- Dd4w89 28–30 s is hands-only straining.
- Dropping the face is a **consistency hack**: a face that is not in frame cannot drift.

**C. Payoff: holding up the "result" glass.** Onion 13–28 s; blueberry 20–34 s; tomato 20–43 s.

**D. CTA while still holding the prop.**

**Average shot length is 2.3–6.3 s. No shot is longer than about 9–10 s** unless a PiP inset is covering it (Dde36's 21.7 s shot is one continuous talking head under the inset). This is consistent with **8-second generation units**. Veo 3.x takes 4, 6 or 8 s per call; Kling takes 5 or 10 s.

**Continuity cheats (they cut through physics):**
- **DdmojIyKCTg 4.5 s:** in shot A the pot holds clear water; in shot B it is deep wine-red with onions, and the glass holds "wine" (key frame 02). Boiled red onion gives a pale mauve liquid, not this.
- **Dd4qFQ‑lQLU:** the water glass jumps from the left of the salt bowl (0–6 s) to the right (14–38 s).
- **DdkLMjXK8sm:** a heart mould produces irregular blobs rather than hearts. Turmeric plus coconut oil with no gelling agent produces fat drops, not "gummies".
- **Ddhjjc8qauR 8 s:** the blender jar goes from empty to holding tomato halves across a cut.

### 4.3 PiP and inset compositing

- **Dde36RZKQ‑V 15.3–44.5 s:** a real-human exercise clip (claps, calf raises, squats, twists, "rib flapping") is laid over the seated monk.
  - The inset is about 520×400 px on 720 wide (**72% width**), centred at x, spanning 48–79% of frame height, with hard edges and no border or shadow.
  - The performer wears green surgical scrubs with a clip-on lav, and his **head is cropped off** by the top edge.
  - A **video-player progress bar** is burned in at the bottom-left of the inset (key frame 04). The clip was screen-recorded or downloaded from a short-video app (very likely a Douyin/Chinese clinician exercise video).
  - The caption sits *over* the inset.
  - Legal and ethical exposure: copyright, right of publicity, and a misleading claim that the monk is demonstrating.
- **Ddbt6FgKACc 12–30 s (low performer):** the insets are **static AI images** (a stomach with mint leaves, a glowing brain, a woman sleeping in lavender, a ✗/✓ boiling comparison) in a square at about 60% width. **No motion inside the inset and no physical transformation**, and it is the lowest-performing main reel in the sample (53.8K).
- **3daKowdg2Ig 22–28 s:** a flat PNG mock-up of the "TIME TO HEAL" book slides in at lower-left.

### 4.4 Other formats (visual)

- **Floor-seated wisdom, single take** (all 2025 YouTube, all itsyangmuns):
  - One still image; the body is locked except for gentle head nods and hand gestures.
  - Candles, lanterns and book never change.
  - DdueaoKBHf6 has **background drift**: at 4 s a cluster of lanterns "grows" on the right, and at 16–20 s a man in a black suit walks through the background. This is a streaming or long-context video model hallucinating the world, not a static-photo avatar.
- **High-angle "phone on the table" framing** (j8WR, 2qD, Cnzj):
  - The camera looks down about 25–30°, with the table corner and book in the lower-left and a **blown candle flare at the bottom centre**.
  - It reads as someone filming the monk on their own phone. This is authenticity cosplay, and the most-viewed video uses it.
- **Selfie POV (‑G_q4QpTskQ, the newest):** arm-extended selfie framing and a moving background, typical of Veo's 2026 "selfie video" prompt pattern.
- **Patient-treatment (xhu4, 3daK):** an over-the-shoulder second person. The patient's face is never shown in 3daK, which reduces a second identity burden. In xhu4 the **VapoRub jar has a sharp, legible label**: trademark use, and a sign of a model with strong text rendering (Veo 3.x or Nano Banana Pro).
- **Long-form 16:9 "podcast"** (V1t8IcG9dio, key frame 11):
  - A boom-arm microphone in a temple hall, orange robe, hand on cheek, **the same pose for 511 s**.
  - Mean frame-to-frame difference is 0.64 per 0.25 s (tiny); frames 60 s apart differ by 3.15.
  - There is no exact loop, so this is an audio-driven long-video model (InfiniteTalk class) running on one still.
  - Views: 302. The format failed.

### 4.5 Hands, teeth and mouth artifacts

- **Hands:** the fingers are generally good (5 fingers, plausible knuckles). Failures happen at contact: the dropper tip passes behind the mould edge (DdkLMjXK8sm 24–29 s), the basket rim merges with the fingers (DdmojIyKCTg 0–2 s), and the lime is held in a claw that would not squeeze (Ddzghllq1z0 0–7 s).
- **Teeth:** the front teeth show as an **even white band** in open-mouth hook frames (Dde36 2 s). Real 80-year-old dentition shows wear, gaps and yellowing. This is a telltale sign.
- **Lip-sync test:** mean mouth aperture during pauses of ≥ 350 ms divided by aperture during speech (1.0 means the mouth moves regardless of audio).
  - Short action shots close the mouth in pauses: ratios **0.01–0.09** in DdmojIyKCTg 4.5–7.6 s and 10.1–13.1 s, and Ddzghllq1z0 12.7–17.5 s.
  - Long talking shots **keep moving through pauses**: ratios **0.96–1.36** in DdmojIyKCTg 13.1–28.7 s, Ddzghllq1z0 20.2–34 s, Dde36 15–44 s and 2qD (1.10).
  - Interpretation, **medium confidence**: talking clips were generated *speaking their own line* (Veo native speech, or a generic talking animation), then the native audio was discarded and the ElevenLabs master voice-over laid on top. Sync is good only where the pacing happens to match.
  - On a phone, with 2–3 s captions pulling the eye, viewers do not notice. **Our upgrade drives every talking shot from the final voice-over audio** (details in §9.4).

---

## 5. Audio forensics

**Five synthetic voices (Resemblyzer cosine similarity):**

| Cluster | Videos | Within-cluster similarity | F0 median | Pace | Character |
|---|---|---|---|---|---|
| V1, "2025 elder" | j8WR, Qdv6, 2qD, Er2Ig, xkFz, Cnzj, Fvo, b‑m8, 6AP7, eFJb | 0.95–0.99 | 130–142 Hz | 130–150 wpm | Low, slow, "my friend" register, light East Asian accent |
| V2, "2026 remedy" | All 8 yangmunus reels, ‑G_q4, 3daK, xhu4 | 0.95–0.99 | 145–157 Hz | 140–175 wpm | Brighter, faster, recipe-reading cadence |
| V3 | itsyangmuns Dde6G, Dduea | 0.97 | 142–147 Hz | **179–184 wpm** | Fast for "wisdom", with music bed |
| V4 | itsyangmuns DdbshG | 0.85–0.88 to everything | 143 Hz | 176 wpm | Separate voice / 48 kHz export |
| V5 | Long-forms V1t8, H‑Qbw | 0.97 | 136 Hz | 158 wpm (podcast) / 99 wpm (meditation) | Narrator |

- Similarity between clusters is 0.74–0.93.
- **0.98–0.99 between different videos is a synthetic-voice fingerprint.** Real people recorded in different rooms and on different mics typically score about 0.80–0.92.
- **Clean TTS with no room tone.** Inter-word noise floors are −63 to −91 dBFS, and several shots contain **true digital zero** (−180 dB): DdmojIyKCTg 10.1–13.1 s and xhu4iu8vVuY 16.4–20.4 s. Native Veo audio would carry ambience, which rules out Veo native audio in the final mix.
- **No music, no SFX on yangmunus.** The harmonic ratio in speech gaps is 0.00–0.02 on 7 of 8 main reels (Ddbt6 is 0.14), and there is no pour, blender or knife sound even over a running blender (Ddhjjc8qauR 17–19 s). IG shows the audio as "Original audio".
- **itsyangmuns uses a music bed** (harmonic ratio 0.67–0.69, gap level −25 to −28 dBFS), which fits the "Buddha Code • Moment of Peace" library track.
- **Timing.**
  - The first word lands at **0.00 s in 26 of 26 videos**.
  - The last word ends 0.1–0.9 s before the file ends.
  - Pause means are 0.37–0.69 s and pause maxima under 1.7 s on shorts. That is ElevenLabs sentence pacing with no added breaths.
  - Meditation is the only video with long silences (mean 1.77 s, max 8.96 s).

---

## 6. Script forensics

**Length and pace:** main-account reels are **73–155 words in 29–54 s**. The 2025 YouTube wisdom videos are 149–241 words in 64–106 s.

**Hooks, in the first 3 s:**
- **"X on Y and (just) watch what happens"**: Ddzghllq1z0 0.0–3.3 s ("Put lime on blueberries and just watch what happens", 411K); Ddhjjc8qauR 0–2.8 s ("Put honey on the tomato and see what happens", 305K).
- **"Did you know that…"**: DdmojIyKCTg 0–6.5 s (1M), and also Dd4qFQ‑lQLU 0–6.1 s (22K). The same words produced a 45× difference in views, so **the visual transformation matters more than the hook wording.**
- **Question plus outcome**: Dde36 0–2.5 s, "After dinner, want to burn sugar fast?"
- **Enemy / pattern interrupt**: DdkLMjXK8sm 0–5 s ("Natural ibuprofen. Stop taking that ibuprofen."), and the repeated line **"Pharmacies don't like / hate this because half their customers would disappear overnight"** (Ddzghllq1z0 3.6–7.9 s; Ddhjjc8qauR 2.8–7.8 s).
- **2025 wisdom**: "You drink water the WRONG way, my friend…" (j8WR 0–6.5 s); "It took me 40 years to learn this, but I'll give it to you in 50 seconds" (CnzjV3QrO70 0–4.2 s).

**Body:** imperative recipe steps of 3–8 words each, one per shot. Then 2–5 benefit claims stacked quickly ("calms inflammation, detoxes your liver, keeps your blood pressure in check", Ddzghllq1z0 24.7–29.0 s).

**CTA** starts at **76–90% of runtime**.
- Onion: 22.0 of 28.9 s.
- Blueberry: 29.0 of 34.2 s.
- Dde36: 44.7 of 53.8 s.
- Fixed wording: "Comment HEAL (and I'll send you) Time to Heal."
- itsyangmuns uses "Comment JOURNEY / S‑O‑U‑L… check out my 30-day healing journey / Healing the Modern Soul".
- 2025 YouTube uses "comment yes" (j8WR 89.5 s) or "comment young moon" (6AP7 58.8 s).

**Claims we must never copy:**
- "Stop taking that ibuprofen, it has too many chemicals" (DdkLMjXK8sm 0–5 s).
- Salt under the tongue makes a headache disappear "in under 5 minutes because… reduces swelling in the brain's blood vessels" (Dd4qFQ‑lQLU 14–29 s).
- "Calf raises 100 times → your kidneys will become stronger; twists → spleen and stomach" (Dde36 20–37 s).
- Lemon-turmeric water leaves your "gut cleared right out" (Dd4w89 33 s).
- "Lowers your blood pressure" (Ddhjjc8qauR 28–30 s).

**Invented backstory presented as real:**
- "My teacher, Dr. Li Zhongsheng, he lived to be 102" (j8WR 7.2 s).
- "In my 70 years I've never needed a medical prescription for this" (Ddhjjc8qauR 24–27 s).
- "My mother used this remedy" (xhu4iu8vVuY 0 s).

**Caption and script mismatch:** the captions reproduce ASR errors, for example "walk A." for "walk away" (Dde6GjRBEVl 30 s) and "Lee Jong Sheng" (j8WR captions) vs "Li Zhongsheng" (audio). The captions are auto-generated and not proofread.

---

## 7. Caption and edit forensics (OCR-verified)

| Account / era | Font look | Case / punctuation | Size | Position | Chunking |
|---|---|---|---|---|---|
| yangmunus 2026 | Geometric sans, medium weight, white with soft black shadow (CapCut default-like) | lowercase, no punctuation except "?" | Glyph height about 34 px on 1280 (**2.7% of height**, small) | Centre at **68–71% height** | 3–9 words, **1.5–3.3 s each**, 1–2 lines, max about 440 px wide (61%) |
| itsyangmuns | Condensed grotesk (Barlow Condensed / Oswald-like) | Title case with punctuation, sentence fragments that cut across sentence boundaries | about 3% of height | 55–65% height | 4–6 words |
| itsyangmuns titles | White on black rounded rectangle (CapCut text "background" style) | "Remember this before sleeping tonight" | about 2.5% of height | Top 8–10% | Persistent |
| YT Nov 2025 (j8WR) | Black extra-bold on white rounded boxes | Sentence case with punctuation | about 3.5% | **Mid-frame (40–60%)**, over the chest | 1 sentence, up to 4 lines |
| YT 2026 xhu4 | Bold white with black stroke | Sentence case | about 3.5% | 62–78% height | Up to 4 lines, overlong |
| Long-form | NLE subtitle, white with shadow | Sentence case | about 4% on 16:9 | Bottom 12% | Full sentences |

**Edit:** no punch-ins, no zooms, no transitions except hard cuts, no SFX, no music (main account), and no progress bar or retention graphics. The 2025 YouTube videos are raw single takes. They skip standard retention craft entirely, which is a large, cheap gap for us to fill.

---

## 8. Inferred production pipeline per format

| Format | Evidence | Most likely pipeline (tool per step) | Confidence | Est. cost / video | Est. time |
|---|---|---|---|---|---|
| **F1 Prop/food demo remedy** (Ddmoj, Ddzg, Ddhj, DdkL, Dd4w, Dd4q) | Shots ≤ 9 s; hands-only inserts; face stable across reels (reference used); clean TTS V2; CapCut captions; 30 fps; −17 LUFS | 1) ChatGPT script from a "remedy + enemy" template. 2) ElevenLabs TTS (V2 voice) as the master track. 3) Nano Banana/Pro: 4–7 stills from a face reference plus prop per beat (faceless stills for steps). 4) Image-to-video per still: **Veo 3/3.1 Fast** (8 s) via Gemini/Flow, or Kling 2.x. 5) CapCut: lay clips to the voice-over, trim, auto-captions, export 720p30. 6) Manual IG post, "comment HEAL" plus ManyChat | Tools: medium-high. Veo vs Kling: medium (Veo favoured by 24 fps native in xhu4, text rendering, SynthID reports) | $6–17 at API prices (5–7 clips × 8 s × $0.15/s, ×1.5–2 rerolls), plus about $0.10 TTS and $0.20 stills. Close to flat on a Google AI Ultra / Flow plan | 30–60 min |
| **F2 Seated talking head plus PiP B-roll** (Dde36, Ddbt6) | Continuous 22–37 s talking head under the inset; inset is ripped real footage or static NB images | Talking clip from one still (Veo clips stitched, or a lip-sync avatar), plus CapCut picture-in-picture of downloaded Douyin/TikTok exercise clips (headless crop) or Nano Banana infographic stills | Medium | $2–8 | 20–30 min |
| **F3 Patient-treatment scene** (xhu4, 3daK; brief: cabbage on back, salt/bay leaves under feet) | Two-person still; patient face hidden; brand text legible; 24 fps native in xhu4 | NB Pro two-person still, then Veo 3.x 8 s clips (3–4), ElevenLabs voice-over, CapCut plus PNG book mock-up | Medium | $5–12 | 30–45 min |
| **F4 Selfie POV** (‑G_q4) | Arm-extended framing; walking background | Veo 3.1 "selfie" image-to-video from an NB still (2–3 clips) plus voice-over | Medium | $3–6 | 15–25 min |
| **F5 Floor-seated wisdom single take** (itsyangmuns; 2025 YT) | One shot of 33–106 s; body static; 25 fps; different face per video; music bed on itsyangmuns | NB still (one per video, no reference), then **HeyGen Avatar IV / Photo Avatar** (matches the HeyGen case study, "about 20 min/video") or InfiniteTalk, then CapCut captions, title box and library music | Tool class: high. Exact vendor: medium (HeyGen favoured) | $0–10 on a HeyGen plan; $2–6 via InfiniteTalk API | 15–25 min |
| **F6 "1 minute of wisdom"** (Qdv6 1.1M, Er2Ig, xkFz, 6AP7, Cnzj) | *Not* a compilation: a single 65–97 s static-still lip-sync with no captions | As F5 with the "open book + candles" template; V1 voice | High | $2–8 | 15 min |
| **F7 Long-form 8.5-min "podcast" / meditation** (V1t8, H‑Qbw) | 16:9, 24 fps, one pose for 414–511 s, no loop; −23.4 LUFS (NLE); V5 voice | Long script (ChatGPT), ElevenLabs long-form, **InfiniteTalk** (up to about 10 min) or HeyGen long render on one NB still, then NLE (Premiere/Resolve) subtitles and loudness normalisation | Medium | $15–35 | 45–90 min |

**Why they grew fast:** they did not win on craft. The package is **one visible physical transformation in frame 0**, plus a folk-remedy promise, plus an anti-pharma enemy line, plus an elder-sage character, plus a single-word comment CTA. Comment counts drive distribution: j8WR has 22K comments on 12.56M views, and the onion reel has 10.3K on 1M.

**Why they are decaying:**
- The low performers are the static ones: herbs, salt, and still insets.
- The newest YouTube shorts get 120–415 views; the YouTube long-forms get 302–2,100.
- The itsyangmuns median is decaying.
- Their costume and religion drift created press exposure.

---

## 9. Upgraded recipe: Chang Yin and Sun Yoon

> **Canonical source:** `/home/claude/rebuild/CHARACTERS.md` (the bible) wins on every character, heritage, set, wardrobe, voice and caption fact. `/home/claude/rebuild/PIPELINE.md` wins on routing and costs. This section only adds the **production craft** the forensics (§0–§8) justify, expressed in the bible's codes: set codes `SET-*`, wardrobe codes `C-*` / `S-*`, and the §13 reference pack.

### 9.0 What we do differently (design principles drawn from the forensics)

1. **Make the physical transformation in frame 0 real, and let it be strength.** Yang Mun's winners all open on moving matter (onions falling, DdmojIyKCTg 1 s). Ours open on **Chang's body doing something visibly hard**: a kettlebell off the garage floor, a floor rise with no hands, a farmer's carry. Food demos open on real food physics, with real foley sound.
2. **Lock identity, voice and wardrobe.** They have six faces and five voices (§4.1, §5). We have one face, one designed voice and fixed wardrobe codes per character (CHARACTERS §4.4–4.5, §5.4–5.5), checked automatically on every render (§9.7).
3. **Drive every talking shot from the final voice-over audio.** Their mouth keeps moving through pauses (ratio about 0.96–1.36). Ours must close in pauses (ratio ≤ 0.35).
4. **Shoot our own demos with our own human performers, never ripped footage** (their Dde36RZKQ‑V 15–44 s scrubs clip). Motion-transfer them onto Chang (§9.3; PIPELINE §3 driving-video library).
5. **Keep claims honest.** Each claim needs evidence IDs plus [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: reviewer sign-off] FALLBACK: "a team check against EVIDENCE.md" (EVIDENCE.md, SAFETY_RULES.md). Sun Yoon's public myth-busting (pillar P15) turns their claims into our content.
6. **Apply retention craft they skip:** readable captions, punch-ins, foley, a soft music bed, and loop endings.
7. **Treat provenance and labelling as a feature:** the bible's disclosure system (§9 of CHARACTERS), a burned-in "AI character" tag, and a C2PA-signed master (PIPELINE §1.4).

### 9.1 Heritage and world (canonical: CHARACTERS §3, §6)

- **Chang Yin**, 74 (born 1952, fictional). **Hwagyo**: born in Incheon's Chinatown, with his grandfather from Shandong. A **retired welder** who never stopped training. He is **not a master, monk, doctor or coach by credential**. Fans call him "Chang" or "Coach Chang", never "Master".
- **Sun Yoon**, 76 (born 1950 in Incheon). Korean. Retired lunch-counter owner. She kept her family name, Yoon, which is why she is "Sun Yoon". Two years older than Chang, which she uses "as a legal argument".
- **Married 1976** (the 50th anniversary in 2026 is a content event). **Emigrated to Northern California in 1983.** They live in a **small 1960s house near the coast**, with neighbour Frank Delgado (79) and Mandu the cat.
- **Every backstory beat is fiction and stated as fiction** ("in our story"). It is flavour, **never an authority claim**. This directly answers Yang Mun's "my teacher lived to 102" (j8WR 7.2 s) and "in my 70 years" (Ddhjjc8qauR 24 s).
- **On screen they speak English.** At most one foreign word per video (*aigo*, *yeobo*, *hǎo*, *mandu* / *jiaozi*). No accent comedy.
- **Visual world:** garage gym, kitchen with onggi crocks, walnut study table, backyard with a persimmon tree, seaside promenade, living room, bedroom, front stoop, plus the occasional market, bathroom and Frank's porch.
- **Never:** robes, temples, altars, misty mountains, bamboo, pentatonic music or chop-suey fonts (CHARACTERS §14).

### 9.2 Identity lock

#### 9.2.1 Master prompts (verbatim from CHARACTERS §13.1; do not paraphrase)

**Chang (append the wardrobe-code text):**
`Photorealistic portrait of a 74-year-old East Asian man, retired welder who strength-trains, 170 cm, lean muscular build of a fit older tradesman, broad shoulders, thick forearms with visible veins, slightly loose skin at elbows and neck, age spots, deep crow's feet, short white crew-cut hair receding at temples, short neatly trimmed 1 cm white beard and mustache, bushy white eyebrows, small scar through outer left eyebrow, warm dark brown eyes, gold wedding band, natural skin texture with pores, shot on iPhone at eye level, soft natural light, candid, documentary realism`

Visual-spec details from §4.4 to keep in every prompt family:
- Burn scar on the back of the right hand.
- Palm calluses.
- Sparse white chest hair.
- Slight upper-back rounding.
- About 15–18% body-fat look: "a fit retired tradesman who has lifted for 14 years", not "a bodybuilder with an old face".

**Chang negative prompt (always):**
`bodybuilder, steroid physique, 8-pack abs, oiled skin, smooth plastic skin, young skin, long wispy beard, Fu Manchu mustache, topknot, robe, monk, temple, prayer beads, kung fu costume, bamboo, misty mountains, conical hat, extra fingers, distorted hands, text artifacts`

**Sun Yoon (append the wardrobe-code text):**
`Photorealistic portrait of a 76-year-old Korean woman, 155 cm, petite and upright, silver-white chin-length bob with side part and a tortoiseshell hair clip on the left, reading glasses on a jade-green beaded cord around her neck, small pearl stud earrings, jade bangle on left wrist, gold wedding band, neatly drawn soft brown eyebrows, deep laugh lines, mischievous bright dark eyes, coral-rose lipstick, small mole beside left nostril, natural skin texture, shot on iPhone at eye level, soft window light, candid, documentary realism`

**Sun negative prompt (always):**
`geisha, hanbok (except holiday episodes), exaggerated makeup, young skin, plastic skin, caricature, dragon-lady, bowl haircut, conical hat, fan, extra fingers, distorted hands`

**House negative additions** (from the forensics; append to both):
`perfect white teeth band, readable fake text, garbled labels, floating objects, liquid changing colour, duplicated fingers on props, wide-angle face distortion`

**Wardrobe codes (CHARACTERS §4.5 / §5.5):** paste the table's item text verbatim after the master prompt.
- **Chang:** C-TRAIN-A (the faded navy tank, default garage), C-TRAIN-B (outdoor / tai chi), C-KITCHEN (Sun's pink floral apron), C-CASUAL (flannel or cardigan), C-FORMAL, C-BED.
- **Sun:** S-KITCHEN (blue-and-white striped linen apron), S-CARDI-JADE (thumbnail look), S-CARDI-MUSTARD, S-WALK (visor), S-TRAIN, S-FORMAL (hanbok on holidays only), S-BED.

#### 9.2.2 Reference pack (CHARACTERS §13.1: 24 images generated on day 0, human-selected, then locked)

- **Chang, 10 images:** front, 3/4 smile, profile, C-TRAIN-A front and back, hands close-up, C-KITCHEN, C-CASUAL, C-FORMAL, C-TRAIN-B outdoors.
- **Sun, 8 images:** front, 3/4 smirk with glasses, profile, S-KITCHEN full body, S-CARDI-JADE seated, S-WALK with visor, hands (bangle and ring), S-FORMAL.
- **Duo, 3 images:** sofa, garage (Chang lifting, Sun in the doorway), kitchen side by side.
- **Others:** Frank, Mandu, and one empty set plate per set code.

How each model uses the pack:

| Model | Which refs from the pack | Our rule |
|---|---|---|
| **Nano Banana 2 / Pro** (keyframes; PIPELINE §1.3: NB2 primary, NB Pro fallback) | Face (front + 3/4) + the full body in the matching wardrobe code + the set plate (≤ 5 refs per scene) | Every video's first frame is a reference-locked keyframe. **Never text-to-video a face shot.** Prompt ends with: "Same person as the reference images; keep facial structure, hairline, beard, eyebrow scar and body proportions identical." |
| **Veo 3.1** (liquids and physics fallback) | Image-to-video from the approved keyframe. "Ingredients" ≤ 3 refs (face, wardrobe body, set) | 4 / 6 / 8 s clips. Describe only motion and camera, never re-describe the face. Audio off unless we keep the ambience. |
| **Kling 3.0** (Std i2v for non-speaking scenes; **Motion Control for every exercise**) | Pose-matched keyframe + performer driving video | ≤ 10 s in image-orientation mode, ≤ 30 s in video-orientation mode. Std for the standard tier, Pro for premium. |
| **Seedance 2.0** (premium, multi-ref duo scenes) | @Image1 Chang face, @Image2 Sun face, @Image3 the duo ref (19/20/21), @Image4 the set plate, @Audio1 the dialogue stem (≤ 9 images total) | R4 duo dialogue in the premium tier |
| **InfiniteTalk** (standard) / **OmniHuman 1.5** (premium) | One keyframe + the final voice-over | All talking shots, **audio-driven from the final voice-over**. Talking-head shots are ≤ 30% of a video (≤ 40% hard cap, CHARACTERS §13.2 / PIPELINE §1.4). |
| **Higgsfield Soul** (API fallback) | Train on the 10 approved Chang images and the 8 Sun images | Lifestyle-still variety when NB drifts |

#### 9.2.3 Sets (canonical: CHARACTERS §6; generate one empty plate per code and reuse it as a background reference)

| Code | Use in this recipe | Light |
|---|---|---|
| **SET-GARAGE** | Strength demos. Kettlebells 8/12/20 kg, squat rack and barbell, **chair against the wall**, bands on the pegboard, clipboard log, "NO MIRROR FLEXING — S.Y." sign and the convex mirror | 6:30–8:00 warm sidelight through the open door |
| **SET-KITCHEN** | Sun's cooking. Onggi crocks, gas stove, digital scale, fridge whiteboard "SUN'S BALANCE: 28 s / CHANG: 24 s" | Midday window light |
| **SET-TABLE** | Honest prop format (Yang Mun's table, done honestly). Study card, barley tea, fruit bowl | Late morning |
| **SET-YARD** | Balance at the fence rail, farmer carries, persimmon tree | Morning / golden hour |
| **SET-PROM** | Tai chi / qigong, walks, steel railing | 7:00 fog, soft |
| **SET-LIVING** | Mobility on the floor, Q&A, couple scenes, Mandu on the armrest | Evening lamp or afternoon |
| **SET-BED** | Wind-down, bedside balance | Night, warm lamp |
| **SET-STOOP** | 5 steps and a handrail: step tests, step-ups, Frank passes by | Morning / afternoon |
| **SET-MARKET** *(occasional)* | Asian supermarket produce aisle or farmers-market stall | Daytime |
| **SET-BATH** *(occasional)* | Habit-stacked balance at the sink with the grab bar | Morning / evening |
| **SET-FRANK** *(occasional)* | Frank's porch | Afternoon |

**Camera language** (CHARACTERS §13.2, plus forensic additions):
- 70% of Chang's shots are full body or medium-full *while moving*. A support object is always visible in movement shots.
- iPhone look at eye level, handheld micro-shake, 24–30 fps, natural light.
- Duo framing: Sun enters from the left, and her reactions are close-ups.
- Insets sit **top-right, never over the face**. The study card is lower-third left for 2 s. Yang Mun's floating chest-box inset is banned (§4.3).
- Exercise capture uses a tripod-locked 1× lens from 3–3.5 m at hip height.
- Continuity (seasonal persimmons, whiteboard scores, Mandu's position) is tracked in `/world/continuity.json`.

### 9.3 Movement realism: biomechanically correct demos

**Why pure text-to-video or image-to-video fails at exercise:**
- Video models have no skeleton or joint limits.
- Rep counts are not controllable (ask for 5, get 3.5).
- Tempo drifts.
- Load doesn't change posture: a 20 kg kettlebell floats.
- Hand-object contact slips.
- Knees cave, the lumbar spine rounds under load, the left and right sides swap, feet slide.
- Clips cap at 8–10 s.

For a 60+ audience, a single wrong-form demo is a credibility and injury liability. Policy (PIPELINE §1.4): **exercises only via `motion_transfer`; we never let a generative model invent an exercise.**

**The pipeline:**

1. **Programme and review.** [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: The PT/DPT on the review team writes the cues, regression, progression and contraindications.] FALLBACK: "Our team writes the cues, regression, progression and contraindications from published exercise guidance (no review claim)." Loads stay modest and believable, per Chang's proof library (CHARACTERS §4.7), and every demo beyond a beginner level is labelled **"Chang's level"**.
2. **Driving-video library** (PIPELINE §3: one 4-hour shoot yields 150–250 clips).
   - A real 60+ performer with a signed release covering motion transfer, about 170 cm and lean.
   - Filmed on an iPhone at 4K 30p, **tripod-locked 9:16**, 1× lens from 3–3.5 m at hip height (1.0–1.1 m), full body with 8–10% margin.
   - Fitted clothes with the **C-TRAIN-A silhouette** (a tank and knee-length shorts expose the joints; baggy clothes hide them).
   - Real props identical to SET-GARAGE (8/12/20 kg bells, the same wooden chair, 5-step stoop).
   - Front, 45° and side angles; 2-1-2 tempo; reps counted aloud; a 1–2 s A-pose at the start of each take.
3. **Pose-matched keyframe.** NB2 or NB Pro. Inputs: Chang face and C-TRAIN-A refs, **frame 1 of the driving clip** as the pose reference, and the SET-GARAGE plate. Use the same framing and scale.
4. **Motion transfer.**
   - **Kling 3.0 Motion Control**: Std about $0.13/s for the standard tier, Pro $0.168/s for premium. Use video-orientation mode (≤ 30 s) for turns and image-orientation mode (≤ 10 s) when he faces the camera throughout.
   - Fallbacks: Kling 2.6 Std MC (lean), or Wan 2.2 Animate self-hosted.
   - Generate 2 variants on standard, 3–4 on premium.
5. **Automated form QA.**
   - Run MediaPipe Pose or RTMPose on the driving clip and on the output. Reject if a tracked joint angle deviates > 12° for more than 5 frames, or if the rep count differs (rep bottoms are local minima of hip height).
   - Reject if the kettlebell detaches from the hand (gap > 3% of frame width).
   - Check the wedding band is on the left hand and the burn scar is on the right hand.
6. **Graphics from real pose data.**
   - A rep counter (top-right safe zone).
   - Foley thuds timed to the real contact frames.
   - A **0.5× RIFE slow-motion form check** of the best rep, with a skeleton-angle line (knee-over-toe or neutral spine) drawn from the performer's pose data.
7. **Voice.** Chang counts to the *real* rep timing ("One… two… breathe out… three", CHARACTERS §4.6). Talking cutaways sit **between** sets, so we never lip-sync during exertion.

**Props checklist:**
- Load shows on the body (forearm tendons, packed shoulders, gripping feet).
- Chalk on the hands in C-TRAIN-A.
- Plates are unmarked or show correct numbers.
- A bell never passes through a thigh.
- A real set-down thud is timed to contact.

### 9.4 Voice (canonical: CHARACTERS §4.6, §5.6, §13.3)

**Designed voices only. Never cloned from a real person.** Use ElevenLabs Voice Design with the bible's prompts:
- **Chang:** "Warm, low baritone male voice in his mid-70s with a light East Asian (Mandarin/Korean-influenced) accent. Calm, unhurried, clear articulation, slight gravel, smiles audibly on jokes. Studio-clean but intimate, as if speaking to one person in a garage." Stability 0.55, similarity 0.8, style 0.2. About **140 wpm**.
- **Sun:** "Bright, crisp female voice in her mid-70s with a light Korean accent. Quick comic timing, dry, warm underneath, slightly raspy on laughs, precise consonants." Stability 0.45, style 0.35. About **155 wpm**.

Generate 6–10 candidates, have a human (plus the cultural consultant) pick one, lock the voice_id, and never regenerate. Model is **Eleven v3** (PIPELINE §1.3), with Flash v2.5 as fallback.

**v3 tags we use:** `[warmly]`, `[chuckles]`, `[laughs]`, `[sighs]`, `[curious]`, `[sarcastic]`, `[deadpan]`, `[exhales]`, `[breathing heavily]` (after a set). Use 1–2 per 10 s. Pauses come from punctuation (`…`, `—`). The accent guardrail applies: light and consistent, and the QC reviewer rejects any take that reads as caricature.

**Script-language locks** (CHARACTERS §4.6 / §5.6):
- Chang uses 4–9 word sentences and at most one signature phrase per video.
- Banned words: "my friend" (Yang Mun's verbal tic, V1 cluster in §5), "detox", "cure", "cleanse", "ancient secret", "Master", "anti-aging", "trust me".
- Sun delivers her verdict first, then the reason, then the kindness.

**Pronunciation dictionary** (alias rules applied to every request):

| Term | Say it as |
|---|---|
| Chang Yin | Chahng Yin |
| Sun Yoon | SUN (as in "sun") YOON (rhymes with "moon"); both names, always |
| yeobo | YUH-bo |
| aigo | EYE-go |
| jajangmyeon | jah-jahng-myun |
| miyeok-guk | mee-yuk-gook |
| doenjang | dwen-jahng |
| onggi | ong-gee |
| songpyeon | song-pyun |
| mandu | mahn-doo |
| jiaozi | jyow-dzuh |
| hǎo | how |
| qigong | chee-gong |
| tai chi | tie chee |
| Baduanjin | bah-dwahn-jin |
| Mandu (the cat) | MAHN-doo |
| sarcopenia | sar-koh-PEE-nee-uh |

**Consistency QA:**
- Resemblyzer similarity to the locked master take must be **≥ 0.95**. Their within-cluster range is 0.95–0.99, which gives the benchmark.
- The master is **−14 LUFS, AAC 48 kHz** (PIPELINE master spec). Theirs is −17 LUFS at 44.1 kHz.
- Add room tone at about −62 dBFS so gaps are never digital zero (their tell, §5).

### 9.5 Lip-sync vs native audio: decision tree

```
Is the shot a close/medium talking shot (mouth > 3% of frame height)?
├─ NO (full-body demo, hands insert, B-roll, back of head, wide)
│     → Kling 3.0 Std i2v / Veo 3.1 Fast (liquids) with audio OFF; VO + foley in edit.
│       Exercises: Kling Motion Control only (§9.3).
└─ YES
   ├─ One speaker, talking-only line (≤ 30% of runtime)
   │     → InfiniteTalk (Standard) / OmniHuman 1.5 (Premium), audio-driven from final VO.
   │       Add a punch-in every 3–5 s; cut to action/B-roll every 6–10 s.
   ├─ One speaker, line delivered while handling a prop/gesturing
   │     → Kling/Veo i2v motion clip, then video-to-video lip-sync pass to the final VO
   │       (fallback). QA pause/speech mouth ratio ≤ 0.35.
   ├─ Duo in one frame (R4)
   │     → Premium: Seedance 2.0 reference-to-video with @Audio1 dialogue stem, ≤ 10–15 s per gen.
   │       Standard/Lean: shot/reverse-shot singles, each InfiniteTalk-driven; Sun's reactions as close-ups.
   └─ Hero laugh/overlap moment (Premium, top 5%)
         → Veo 3.1 native dialogue take → ElevenLabs Voice Changer onto the locked voice_id
           (keeps timing, restores timbre).
```

**Stitching 8-second clips:**
- Every beat is **≤ 7.5 s** of voice-over; split the voice-over before generating.
- Clip N+1 starts from the last frame of clip N, or from the same locked keyframe.
- Cut on action (a lift, a pour).
- Script prop-state changes so liquids never jump colour or level (Yang Mun's clear→red pot, DdmojIyKCTg 4.5 s).
- One LUT per set code, with 3–5% grain.
- For a loop ending, the last frame equals the first frame.

### 9.6 Edit template

| Time | Beat | Picture | Audio | On-screen |
|---|---|---|---|---|
| 0.0–1.5 s | **Hook: visible effort or transformation** | The hardest frame first (bell leaving the floor, floor rise, pot at the boil) | First word at **0.00 s** (Yang Mun does this in 26/26), foley hit at 0.1 s | Hook text ≤ 6 words |
| 1.5–5 s | Stakes | Talking cutaway, 1.08× punch-in | Voice-over plus room tone | Captions |
| 5–25 s | Demo / recipe beats | 2–4 s shots; rep counter; 0.5× form check | Foley on every contact | Cue captions plus rep numbers |
| 25–35 s | Proof | **Study card lower-third left, 2 s** (CHARACTERS §13.2) | Music ducks | Source line |
| 35–42 s | CTA plus loop | CTA mid-action; last frame = first frame | Keyword CTA | CTA card |

**Captions** (canonical: CHARACTERS §13.2; supersedes the style detail in §10 trick 10):
- Warm rounded humanist sans, **Nunito or Figtree Bold at 52–64 px** on 1080×1920.
- High contrast only: **white or cream on a dark pill, or near-black on cream**. Never grey, no "//" decorations, no brush-stroke or "Asian" fonts.
- Text comes from the script, force-aligned to the voice-over (word timings from ElevenLabs), so none of their ASR errors ("walk A.").
- 2–5 words per chunk, ≤ 2 lines, ≤ 26 characters per line.
- Caption centre at about 63% of height.
- Safe zone: x 90–930, y 220–1480.
- The **burned-in "AI character" tag** appears on every video.

**Sound:**
- Voice-over at −14 LUFS; foley at −18 to −24; music bed at −30 to −34.
- Music comes from the ElevenLabs Music library (PIPELINE §1.3), with no pentatonic "oriental" riffs.
- SFX by set: kettlebell thud, garage-door roll, pot lid, knife on board, gulls on SET-PROM, Mandu's meow.

**Length:** IG 20–40 s, TikTok 25–55 s, Shorts 30–58 s, FB 30–60 s.

**CTA:** the page's keyword (ManyChat on IG/FB); on TikTok US, link in bio plus a pinned comment. Closers come from the bible ("Same time tomorrow." / "Tell me your number." / "Now go eat.").

### 9.7 Realism QA checklist (the gate before publish; automated where possible, human spot-check per PIPELINE §2.1)

**Identity:**
- ArcFace cosine vs the locked front ref ≥ 0.60 on 6 sampled frames (worst ≥ 0.50).
- Chang: eyebrow scar, 1 cm white beard (never a long goatee), wedding band left, burn scar right.
- Sun: tortoiseshell clip on the left, jade cord, jade bangle on the left wrist, mole beside the left nostril, silver bob.

**Wardrobe and set:**
- The wardrobe code matches the brief.
- Set props match the plate (the same chair, the same kettlebells).
- `continuity.json` state respected (whiteboard scores, season, Mandu).

**Hands:**
- 5 fingers, grip wraps the object, no fused knuckles, calluses and rings consistent.

**Teeth and mouth:**
- No perfect white bar.
- Mouth closes in pauses (ratio ≤ 0.35).
- No lip-teeth merging.

**Eyes:**
- Blinks every 2–6 s.
- Consistent catch-lights.
- No iris-colour change.

**Text on props:**
- Only our branded study card and the "NO MIRROR FLEXING — S.Y." sign may be readable.
- Everything else is blurred or blank, with no brand logos (their VapoRub label, §4.4).

**Physics:**
- Liquids keep level and colour.
- Steam only from hot things.
- Food volume is conserved.
- Weights load the body.
- No foot slide.
- Shadows match the key light.

**Exercise:**
- Pose-angle check passed.
- Rep count matches the voice-over.
- Regression shown.
- "Chang's level" label where needed.
- [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: PT sign-off.] FALLBACK: "Team check against published exercise guidance (no review claim)."

**Food:**
- Cooked once for real.
- Allergen, sodium and "who should skip this" line present (CHARACTERS §2).

**Claims:**
- Every claim maps to an evidence ID.
- Compliance judge passes (PIPELINE §1.4, two gates).
- No banned phrases.

**Audio:**
- Voice similarity ≥ 0.95.
- Room tone present.
- −14 LUFS, −1 dBTP.

**Provenance:**
- C2PA-signed master.
- `is_aigc` / `containsSyntheticMedia` true.
- Platform AI labels on.
- Burned-in "AI character" tag.
- SynthID left intact.
- Prompts, seeds and model versions logged.

### 9.8 Twenty-five production prompts, ready to copy and paste

**Tokens.**
- `[CHANG]` / `[SUN]` = the §9.2.1 master prompt.
- `[C-TRAIN-A]` etc. = that wardrobe code's item text from CHARACTERS §4.5 / §5.5.
- `[SET-GARAGE]` etc. = that set's description from CHARACTERS §6.
- `[NEG-C]` / `[NEG-S]` = the negative prompts from §9.2.1.

**Refs to attach:** the matching subset of the §13.1 pack (face + wardrobe body + set plate; the duo refs for two-person scenes).

**Append to every keyframe:** "Same person as reference images, identical facial structure, hairline, beard and scars. Real iPhone photo, 9:16, eye level, natural light, visible skin texture, no text except the study card, no logos, no watermark."

**Append to every i2v prompt:** "Keep face and wardrobe exactly as in the first frame. Realistic weight and physics. Handheld micro-movement. No on-screen text. No music."

**Tier** follows PIPELINE §4.1 routing: a new idea renders Lean, a proven hook renders Standard, and the top 5% render Premium. Exercise shots always come from the Motion Control driving library.

---

**P01. Kettlebell deadlift ("pick it up like this")**. R3, 32 s, Lean → Standard.
- **Keyframe:** [CHANG] [C-TRAIN-A] in [SET-GARAGE], hinged over a chipped 20 kg kettlebell between his feet, flat back, chalked hands, garage door open behind, morning sidelight, full body at 3 m, hip-height camera. [NEG-C]
- **Motion:** driving clip `kb_deadlift_front_20kg` (5 reps, 2-1-2) through Kling 3.0 MC, image orientation, 10 s × 2.
- **Hook (0–1.5 s):** Kling Std i2v. "the bell leaves the floor as he stands tall and exhales, then sets it down with a thud."
- **Voice (Chang):**
  > [exhales] I'm 74. Watch. Hips back… flat back… stand up tall. Breathe out when it's hard. Five slow reps. [warmly] New to this? Eight kilos. Or a bag of rice. Legs first. Same time tomorrow.
- **Edit:** rep counter; 0.5× form check on rep 3 with a neutral-spine line; a "Chang's level: 20 kg" tag.
- **Evidence:** resistance training in older adults (EVIDENCE E01/E03 family).

**P02. Goblet squat to a deep-squat hold, with the chair as coach**. R3, 30 s.
- **Keyframe:** [CHANG] [C-TRAIN-A] [SET-GARAGE], holding a 12 kg kettlebell at his chest in front of the wooden chair against the wall.
- **Motion:** `goblet_squat_to_chair` (5 reps touching the chair), then `deep_squat_hold_10s` (Chang's level).
- **Voice:**
  > The chair is not your enemy. The chair is your coach. Sit back… touch… stand. [curious] Can you hold the bottom for ten? …eight, nine, ten. Can't yet? Hold the counter and go halfway.
- **Edit:** countdown ring; knee-over-toe line; "Chang's level" on the deep hold.

**P03. Hip mobility (90/90 switches) with the Sun interruption**. R1, 32 s.
- **Keyframe:** [CHANG] [C-CASUAL] seated on the floor rug in [SET-LIVING] in a 90/90 hip position, Mandu on the sofa armrest, the K-drama paused on the TV.
- **Motion:** `hip_9090_switch` × 6 via Kling MC.
- **Cutaway (Kling i2v):** [SUN] [S-CARDI-JADE] in the doorway, arms crossed, eyebrow raised.
- **Voice (Chang):**
  > I'd rather lift than stretch. [sighs] She catches me every time. Knees swing… slow… sixty seconds a day.

  **Voice (Sun):**
  > [deadpan] Hip replacement? Ask your surgeon first. Then do it anyway. Every day.

**P04. Balance: the fridge whiteboard rematch**. R1, 30 s.
- **Keyframes:**
  - [SUN] [S-TRAIN] in [SET-KITCHEN] standing on one leg, fingertips hovering over the counter, the whiteboard behind reading "SUN'S BALANCE: 28 s / CHANG: 24 s".
  - [CHANG] [C-CASUAL] attempting the same, wobbling.
- **Motion:** `single_leg_counter_hover` (both performers' clips mapped to each character).
- **Voice (Sun):**
  > Ten seconds on one leg. [pause] In a big study of people over fifty, those who couldn't do it had higher risk later. [warmly] Near the counter. Every day. [smirk] Twenty-eight. Beat that, old man.

  **Voice (Chang):**
  > [laughs] Twenty-four… tomorrow twenty-five.
- **Edit:** on-screen timer; study card "Araújo et al., BJSM 2022, association" (lower-third left, 2 s). Update the whiteboard state in `continuity.json`.

**P05. Breathwork: six breaths a minute, at bedtime**. R1, 40 s, Lean.
- **Keyframe:** [CHANG] [C-BED] sitting on the edge of the bed in [SET-BED], one hand on his belly, reading glasses on his forehead, warm lamp.
- **Talk:** InfiniteTalk from the voice-over.
- **Insert (Kling i2v):** "hand rises and falls slowly on the belly."
- **Voice:**
  > [calm] Six breaths a minute. In through the nose… two, three, four, five. [exhales] Out slow… two, three, four, five. A few minutes of this can bring blood pressure down for a while. It's a tool, not a medicine.
- **Edit:** a breathing pacer circle; no captions during the counting.

**P06. Morning tai chi / qigong on the promenade**. R3, 35 s.
- **Keyframe:** [CHANG] [C-TRAIN-B] at [SET-PROM], 7:00 fog, the steel railing on the left, gulls, distant walkers, feet shoulder-width.
- **Motion:** `baduanjin_lift_sky` × 4 (a qualified teacher is the performer) via Kling MC, video orientation, 25 s.
- **Voice:**
  > Every morning since I retired. [softly] Palms up… lift… rise on your toes if your balance allows… and lower. It's exercise from China, and the studies on balance in older adults are good. Slow is the point.
- **Edit:** gull foley; no music for the first 5 s.
- **Evidence:** tai chi and qigong for balance (E14–E17).

**P07. Bird-dog with Sun's spoon**. R3, 32 s. **Needs a movement check** ([ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: PT review] FALLBACK: "team check against published exercise guidance; hold if unsure").
- **Keyframe:** [CHANG] [C-TRAIN-A] on all fours on a mat in [SET-LIVING], a wooden spoon balanced on his lower back.
- **Motion:** `bird_dog_alt_8s` via Kling MC.
- **Cutaway (Kling i2v):** [SUN] [S-KITCHEN] placing the spoon.
- **Voice:**
  > **Chang:** Back complains when you bend? Don't only stretch it. Build it. Opposite arm, opposite leg… don't drop the spoon.
  > **Sun:** [deadpan] That's my good spoon.
  > **Chang:** [chuckles] Sharp pain, numbness or leg weakness? See a clinician first.

**P08. Grip: farmer's carry across the yard (plus Chang's-level hang)**. R3, 35 s, Standard.
- **Keyframes:**
  - [CHANG] [C-TRAIN-A] in [SET-YARD] walking tall with two 20 kg kettlebells past the persimmon tree.
  - [CHANG] [C-TRAIN-A] hanging from the squat-rack bar in [SET-GARAGE].
- **Motion:** `farmer_carry_2x20_15m` (Kling MC, video orientation, 20 s) and `bar_hang_30s` (10 s excerpt, labelled "Chang's level, not for beginners").
- **Voice:**
  > Grip strength is one of the simplest signals of how we're aging. Carry heavy things. Groceries count. Two bags, walk tall, twice a week. [chuckles] The hang? That's my level. Start with the carry.
- **Evidence:** grip strength and mortality (PURE), stated as an association.

**P09. The stoop step test, with Frank**. R3, 38 s.
- **Keyframe:** [CHANG] [C-TRAIN-B] at the bottom of the 5 concrete steps of [SET-STOOP], hand near the black rail, checking a watch. Frank [plaid short-sleeve shirt, suspenders, cap, compression sleeve on right knee] on the sidewalk holding a newspaper.
- **Motion:** `stoop_up_down_12_trips` (60 steps, brisk, rail available) via Kling MC, video orientation, 30 s.
- **Voice:**
  > **Chang:** Twelve trips up my stoop. Sixty steps, about four flights. [breathing lightly] Fifty-four seconds. One study linked doing that under a minute with better heart-test results. It's a check, not a diagnosis.
  > **Frank:** [dry] I'll time you. From the chair.
- **Edit:** stopwatch; footsteps foley.
- **Evidence:** ESC 2020 (Peteiro et al.), observational.

**P10. The 30-second chair stand**. R3, 30 s, Lean.
- **Keyframe:** [CHANG] [C-TRAIN-A] seated on the wooden chair against the wall in [SET-GARAGE], arms crossed, feet flat.
- **Motion:** `chair_stand_30s` (22 reps, which matches Chang's proof library) via Kling MC, video orientation.
- **Voice:**
  > Thirty seconds. Arms crossed. All the way up, all the way down. [counting] …twenty-two. That's my number. Tell me your number. Low? This is your exercise.
- **Evidence:** CDC STEADI chair-stand norms.

**P11. Sun's doenjang-jjigae with cabbage (fiber and fermented)**. R2, 40 s.
- **Keyframes (x4):**
  - [SUN] [S-KITCHEN] at the gas stove in [SET-KITCHEN] tearing napa cabbage into a pot.
  - Hands-only: a spoon of doenjang from an onggi crock pressed through a sieve.
  - Tofu cubed on a board beside the digital scale.
  - A steaming bowl pushed toward the camera.
- **Scenes:** Veo 3.1 Fast i2v for the liquids (dissolving doenjang, simmer); Kling Std for the rest.
- **Voice (Sun):**
  > Your stomach doesn't need a special tea. It needs fiber and time. Cabbage, lots. Doenjang, one spoon. Salty, so weigh it. Grams, not vibes. Tofu for protein. Ten minutes. [deadpan] He eats fourteen dumplings in five minutes.

  **Voice (Chang, off-screen):**
  > [laughs] Efficient.

  **Voice (Sun):**
  > Now go eat.
- **Edit:** real foley; a sodium / "who should skip" line.

**P12. Protein at the study table**. R4, 30 s.
- **Keyframe:** duo ref #19/21 adapted to [SET-TABLE]. [CHANG] [C-CASUAL] and [SUN] [S-CARDI-JADE] at the walnut table, barley tea, a bowl with eggs and tofu, the printed study card, her glasses on the cord.
- **Talk:** Seedance 2.0 (Premium) or shot/reverse-shot InfiniteTalk (Standard).
- **Dialogue:**
  > **Sun:** [teasing] Seventy-four and he eats three eggs.
  > **Chang:** Older muscle needs more protein, not less.
  > **Sun:** [glasses on her nose] Show me the study.
  > **Chang:** [slides the card] One to one-point-two grams per kilo, for healthy people our age.
  > **Sun:** [deadpan] Fine. Then you do the dishes.
- **Evidence:** PROT-AGE; kidney-disease caveat in the caption.

**P13. Sun roasts the mirror flexing**. R4, 22 s, loop.
- **Keyframe:** duo ref #20. [SUN] [S-CARDI-MUSTARD] in the garage doorway of [SET-GARAGE], arms crossed. [CHANG] [C-TRAIN-A] flexing in the small convex mirror under the "NO MIRROR FLEXING — S.Y." sign.
- **Scene:** Kling i2v. "he slowly flexes, notices her, pretends to adjust the mirror."
- **Voice:**
  > **Sun:** [deadpan] Mr. Tank Top. Every morning. Swing, swing, flex.
  > **Chang:** [chuckles] Quality control.
  > **Sun:** Seven out of ten. Because I love you.
- **Edit:** final frame = first frame.

**P14. Myth-bust: "onion water clears your lungs"**. R1, 35 s, Sun's pillar (P15).
- **Keyframe:** [SUN] [S-CARDI-JADE] at [SET-TABLE] holding a glass of *pale mauve* onion water at arm's length, a jar of honey and a mug of warm water on the table, the study card face-down.
- **Scenes:** Veo 3.1 Fast i2v.
  1. "she tilts the glass, unimpressed, sets it down."
  2. "she stirs honey into warm water."
- **Voice (Sun):**
  > No. [pause] Nothing you drink reaches your lungs. Put the onion in the soup. [warmly] For a cough, honey in warm water has real evidence. Not for babies under one. Cough longer than three weeks, or blood? Doctor. Today.
- **Edit:** "MYTH" stamp at 0.5 s, then "WHAT HELPS"; study card "Honey for acute cough, Cochrane".
- **Rule:** name the myth, never the competitor.

**P15. Q&A reply: "My knees hurt going downstairs"**. R1, 35 s.
- **Keyframe:** [CHANG] [C-CASUAL] on the sofa in [SET-LIVING], leaning forward, the lamp on, Mandu beside him.
- **Talk:** InfiniteTalk, ≤ 30% of runtime.
- **Motion inserts:** `step_down_eccentric_stoop` at [SET-STOOP] (handrail) and `wall_sit_20s` at [SET-GARAGE].
- **Question card top-right:** a permissioned real question, or labelled "a question we get a lot".
- **Voice:**
  > Going down, the thigh works while it lengthens. So train exactly that. Slow step-downs. Three seconds. Hold the rail. Pride is not a safety rail. Wall sit, twenty seconds. Swelling, locking, giving way? Get it checked.

**P16. Market run (Sun's cheap, honest basket)**. R2, 35 s.
- **Keyframes:** [SUN] [S-WALK] and [CHANG] [C-CASUAL] in the produce aisle of [SET-MARKET]. She inspects a napa cabbage; he carries a full basket in one hand like a farmer carry. Prices are out of focus, with no store branding.
- **Scenes:** Kling Std i2v × 4.
  1. Cabbage into the basket.
  2. Hands pick kiwis.
  3. A frozen-berry bag held up.
  4. Chang grinning with the heavy basket.
- **Voice:**
  > **Sun:** Cabbage, cheap. Beans. Kiwis. Frozen berries, same nutrients, half the price. [sarcastic] And a strong husband to carry.
  > **Chang:** [laughs] Loaded carry. I'm training.

**P17. Morning habit stack (sink balance, then garage)**. R3, 40 s.
- **Keyframes:**
  - [CHANG] [C-BED] at the pedestal sink in [SET-BATH], one hand near the grab bar, brushing his teeth while standing on one leg.
  - [CHANG] [C-TRAIN-A] rolling up the garage door in [SET-GARAGE].
- **Motion:** `sink_single_leg_brush` (2 × 10 s) and `wall_pushup_10` via Kling MC.
- **Scene (Kling i2v):** "garage door rolls up, morning light floods in."
- **Voice:**
  > Two minutes brushing. One minute each leg. Grab bar right there. [chuckles] Then coffee, then the garage. Ten wall push-ups before the phone. Every day, a little.

**P18. After-dinner walk (the real version of "burn sugar fast")**. R2, 30 s.
- **Keyframe:** [CHANG] [C-CASUAL] and [SUN] [S-WALK] stepping down the [SET-STOOP] steps onto the sidewalk at golden hour, her visor on.
- **Scenes:** Kling Std i2v × 3 (walking, her gesturing, Frank waving from [SET-FRANK]).
- **Voice:**
  > **Chang:** Ten, fifteen minutes of walking after dinner helps with the blood-sugar rise. Muscles use it.
  > **Sun:** [teasing] And it's the only time he listens to me.
- **Evidence:** post-meal walking and postprandial glucose (Buffey 2022).

**P19. Neck reset for phone necks**. R3, 28 s, Lean.
- **Keyframe:** [CHANG] [C-CASUAL] with his back to the wall beside the photo wall in [SET-LIVING], chin tuck.
- **Motion:** `chin_tuck_wall_8` and `wall_angel_6` via Kling MC.
- **Voice:**
  > Head in front of your shoulders? Back of the head to the wall. Small double chin. Hold. Slow wall angels. Twice a day. Hands going numb? See someone.

**P20. Two kiwis a day (constipation, a real trial food)**. R2, 28 s.
- **Keyframe:** [SUN] [S-CARDI-JADE] at [SET-TABLE] halving kiwis on a small board, the fruit bowl behind.
- **Scenes:** Kling i2v × 2 (cutting; spooning).
- **Voice (Sun):**
  > Somebody asked me about constipation. Short version: two green kiwis a day. There are real trials. Prunes work too. Water, walk. [deadpan] Not a tea that costs forty dollars.
- **Evidence:** kiwifruit RCTs; allergy caveat.

**P21. "Strong is a habit" identity montage**. R3/R1, 20 s, Premium, loop.
- **Keyframes:** from the proof library (CHARACTERS §4.7), labelled "Chang's level":
  - Floor sit-to-stand with no hands.
  - Farmer's carry.
  - Deep squat hold.
  - Single-leg balance at the fence rail in [SET-YARD].
  - 40 cm box step-up with a vest.
  - A laugh at [SET-TABLE] with Sun.
- **Motion:** reuse approved MC outputs, plus a Veo 3.1 (premium) opener: "slow push-in as he looks up from the bar, breath visible in the cool garage."
- **Voice:**
  > People ask what I take. [pause] I lift. I walk. I eat her cooking. I sleep. Strong is a habit. Start today.
- **Edit:** hard cuts on the beat; loop.

**P22. Wind-down duo**. R4, 40 s.
- **Keyframe:** [CHANG] [C-BED] and [SUN] [S-BED] in [SET-BED], the bojagi-coloured quilt, lamp, glasses of water, alarm clock.
- **Talk:** singles via InfiniteTalk, plus a Kling i2v two-shot: "she turns off her lamp, he stretches his neck."
- **Voice:**
  > **Chang:** Same bedtime, same wake time. Weekends too.
  > **Sun:** [sarcastic] And no phone in bed, Mr. "one more video".
  > **Chang:** [laughs] Coffee after two? That's your 3 a.m. problem.

**P23. Myth-bust #2: "100 claps make your lungs younger"**. R1 + R3, 35 s.
- **Keyframe:** [SUN] [S-CARDI-JADE] at [SET-TABLE], glasses on her nose, reading the claim off a phone. Then [CHANG] [C-TRAIN-A] in [SET-GARAGE].
- **Motion:** `step_ups_40cm_box` and `march_intervals` via Kling MC.
- **Voice:**
  > **Sun:** "Clap one hundred times, your lungs get younger." [pause] No.
  > **Chang:** What helps your breathing fitness is getting a little out of breath on purpose. Step-ups. Brisk walks. Three times a week.
  > **Sun:** Nobody is coming to save your knees. You are.

**P24. Label reading in the kimchi fridge (sodium)**. R2, 30 s.
- **Keyframe:** [SUN] [S-WALK] at the cold case in [SET-MARKET] comparing two unbranded kimchi jars, glasses on her nose, one eyebrow up.
- **Scene:** Kling i2v. "she compares the jars, puts one back." A clean composited graphic: "Sodium: per serving".
- **Voice (Sun):**
  > Kimchi, good. Kimchi with the salt of the whole ocean, not every day. Look at sodium per serving. Pick the lower one. Blood pressure? Ask your doctor about your number. [laughs] I'm fun at the market.

**P25. Weekly "study table" Q&A**. R4, 55–90 s, Shorts / FB.
- **Keyframe:** [CHANG] [C-CASUAL] and [SUN] [S-CARDI-JADE] at [SET-TABLE], barley tea, the printed study card, a phone on a stand showing a blurred comment feed.
- **Talk:** Seedance 2.0 (Premium) or alternating InfiniteTalk singles (Standard). Punch-ins every 4 s; motion inserts from the library.
- **Structure:**
  - 3 permissioned audience questions (movement, food, sleep).
  - Chang answers in ≤ 45 words with one action step.
  - Sun gets the last word ("Short version:").
  - Closer: "Tell me in the comments. I read them. Well, the team reads them to me." (the bible's AI wink).

---

### 9.9 Production economics: reconciled with PIPELINE.md §4

**The reconciled recommendation:** use **PIPELINE §4.1 routing**.
- Tiers are Lean $0.89 / Standard $4.04 / Premium $13.67 (blended across R1–R4 at 3:2:1:1).
- The recommended mix is **60 / 35 / 5**, giving **$2.63 generation cost per base video**.
- Generation cost is about $2.2K/month at 4 pages (840 base videos), $5.5K at 10 pages and $11.1K at 20 pages.
- **All-in** (tools, VAs, credentialed reviewer, performer refreshes) is **about $7.2K / $14.8K / $24.7K per month**, which is **about $8.60 / $7.00 / $5.90 per base video**.

**Why my earlier $10–14 per video was higher.** It was a generation-only estimate with four assumptions PIPELINE doesn't make:
1. **Premium motion transfer on more videos.** I routed 15% to a "hero" tier ($25–60) and put Kling Pro MC or Veo 3.1 Standard on every exercise video. PIPELINE sends exercises through the motion library at Standard (R3 is $5.25) or Lean ($1.11), and uses Premium only for the top 5%.
2. **Fresh generations every time.** I assumed new keyframes and scenes for every video. PIPELINE pre-renders about 300 action clips, 150 macros and 80 graphic templates, so 25–45% of each video is free library footage.
3. **Performer shoots as a per-video cost.** I amortised them at $8–15 per move. PIPELINE treats the shoot as a one-time $1.5–3K plus $500/month refreshes.
4. **Higher prices and rerolls.** I used reseller and list prices with 1.5–2× rerolls, versus PIPELINE's verified routing: NB2 batch, Kling v3 Std at $0.084/s, and InfiniteTalk self-hosted on the Lean tier.

My figure is close to PIPELINE's **all-in** cost per video at small scale ($7–9), not its generation cost.

**What this recipe adds without changing that budget:**
- The quality gates in §9.3 and §9.7 (pose QA, pause-mouth ratio, identity cosine, voice similarity) run in the QA worker, already costed in PIPELINE §4.3.
- **Non-negotiables at every tier:** exercises only from the driving-video library through Motion Control; talking shots audio-driven from the final voice-over. On Lean, both run on the Kling 2.6 MC / Wan 2.2 self-host and self-hosted InfiniteTalk routes.
- The 0.5× form-check, rep counter and foley are assembler features (about $0 marginal).

**Tier mapping for the 25 prompts:**
- **Lean by default:** new ideas, P05, P10, P19.
- **Standard once proven:** most R1, R2 and R3.
- **Premium (top 5% only):** P12, P21 and P25 when they break out, Seedance duo scenes, Veo 3.1 native-dialogue hero laughs, and each page's pinned "Hi, we're AI" post.

**Throughput:** follow PIPELINE §2 and §4.5 (p50 about 18 min end-to-end, 20–30 concurrent provider jobs, 7 base videos per page per day, uniqueness levels L0–L4). This section changes none of that.

---

## 10. Top craft tricks to steal or upgrade (ranked)

1. **Motion at frame 0.** Onions mid-fall at 1 s (DdmojIyKCTg, 1M) vs a static herb bouquet (Ddbt6FgKACc, 53.8K). Our upgrade: an elder mid-lift.
2. **The first word at 0.00 s** (26/26 videos). No silent intro, ever.
3. **Faceless hands-only inserts for process steps** (DdkLMjXK8sm 11–34 s). They hide identity drift and are cheap. Keep them for recipe steps even with a locked identity.
4. **"Put X on Y and watch what happens"** is a curiosity-gap hook tied to a visible prop (411K, 305K). Honest version: "Try this on one leg and watch what happens to your balance."
5. **A single-word comment CTA at 76–90% of runtime, while still holding the prop.** It drives the comment velocity that fed their reach (j8WR: 22K comments).
6. **The "phone on the table" high-angle framing, plus a candle flare** (j8WR, 12.56M). It reads as a relative filming grandpa. Our version: Sun Yoon "films" him with the phone (a POV).
7. **Beat-per-shot editing at 2–4 s** (average shot length 2.3–4.8 s on winners vs 6.3 s on the 22K salt reel).
8. **Real prop transformation beats abstract insets.** A blender, a pour or a steaming pot outperforms still AI infographics (Ddbt6). Use motion B-roll only.
9. **Drive talking shots from the final voice-over** (fixing their pause-mouth mismatch, ratios 0.96–1.36), and add room tone so there is never digital-zero silence.
10. **Readable, proofread captions at 63% height, 64–72 px, white with a black stroke** (theirs are small, ASR-errored, lowercase), plus foley and a ducked music bed, neither of which they have.

## 11. Limitations of this analysis

- **SynthID** could not be tested locally. **C2PA absence** is expected after platform transcode and says nothing about the source files.
- The **Veo vs Kling attribution** for Yang Mun's action clips is inference from frame rate, clip length, text rendering and external SynthID reports. It is not a metadata proof.
- The **x264 SEI** finding on the 2025 YouTube files is anomalous and treated as weak evidence.
- The **lip-sync pause metric** uses MediaPipe on 720p faces; treat the per-shot ratios as indicative. It could not track the smallest faces (Qdv6, Dde6G).
- **Sample coverage:** YouTube upload dates were available only for j8WR (10 Nov 2025) and Qdv6 (25 Nov 2025); the others are ordered by playlist index. The low performer Tla_hxhxWuk was unavailable and replaced by 3daKowdg2Ig.
- **Tool prices** are list or reseller prices seen in Sep 2026 and change often. Kling Motion Control per-second pricing is not published uniformly, so verify it on your own account.

**Sources for tool specs:**
- [Kling 3.0 Motion Control (Replicate)](https://replicate.com/kwaivgi/kling-v3-motion-control)
- [Kling Motion Control user guide](https://kling.ai/quickstart/motion-control-user-guide)
- [Seedance 2.0 reference-to-video (fal)](https://fal.ai/models/bytedance/seedance-2.0/reference-to-video)
- [Veo 3.1 developer guide (DEV, Jun 2026)](https://dev.to/akaranjkar08/veo-31-developer-guide-timestamp-prompting-multi-shot-video-and-full-api-june-2026-3l5i)
- [Veo 3.1, Google DeepMind](https://deepmind.google/models/veo/)
- [ElevenLabs v3 audio tags](https://elevenlabs.io/blog/v3-audiotags)
- [ElevenLabs pronunciation dictionaries](https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/pronunciation-dictionaries)
- [ElevenLabs best practices](https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices)
