# COSTS.md: what the content engine costs per day and per month

Model: `tools/build_costs.py` produces `data/costs_model.csv` (54 scenarios, plain numbers) and the **`Costs` sheet in `economics.xlsx`**, which has a yellow inputs block and a scenario grid that is all formulas. No other sheet was touched (cell-by-cell compare: 0 changes). I recalculated the sheet in LibreOffice and it matches the CSV within 0.08%, the gap being CSV rounding. Prices are public list prices checked **Oct 1 2026** ([A] = assumption or estimate). Nothing was bought, called or posted.

Unit: **1 master = 1 source script = 4 video files (IG, FB, TT, YT distinct cut) + 2 text/carousel posts (Threads, X)**, as in POSTING_PLAN.md. So posts/day = pages × posts/day/platform × 6, and masters/day = pages × posts/day/platform.

## 1. Prices used

| Line | Price | Source |
|---|---|---|
| Nano Banana stills | **$0.067/image** (Nano Banana 2, 1K; batch $0.034; Lite $0.0336) | [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing). render_day1.py still carries $0.039 for gemini-2.5-flash-image, which no longer appears on the pricing page |
| Kling lip-sync (still + audio) | **$0.0562/s** (AI Avatar v2 Standard; Pro $0.115/s) | [fal: Kling AI Avatar v2 Standard](https://fal.ai/models/fal-ai/kling-video/ai-avatar/v2/standard) |
| Kling Motion Control | **$0.07/s** (v2.6 Standard; PIPELINE lists v3 Std ~$0.13/s, Pro $0.168/s) | [fal: Kling 2.6 Std Motion Control](https://fal.ai/models/fal-ai/kling-video/v2.6/standard/motion-control) |
| Veo inserts | **$0.15/s** (Veo 3.1 Fast i2v on fal, no audio; Gemini API direct $0.10/s). Seedance 1 Pro fallback ≈ $0.148/s ($0.74 per 1080p 5 s) | [costgoat Veo, Oct 2026](https://costgoat.com/pricing/google-veo), [fal Seedance 1 Pro](https://fal.ai/models/fal-ai/bytedance/seedance/v1/pro/image-to-video) |
| ElevenLabs | Creator $22 / 121K credits · Pro $99 / 600K · Scale $299 / 1.8M · Business $990 / 6M (1 credit ≈ 1 char); overage $0.10/1K; API pay-as-you-go v3 $0.08/1K. The model picks the cheapest tier each month | [flexprice ElevenLabs breakdown](https://flexprice.io/blog/elevenlabs-pricing-breakdown), [ElevenLabs API pricing](https://elevenlabs.io/pricing/api) |
| Claude (script gen + mandatory judge) | Sonnet 5.5 $2 / $10 per MTok in/out · Haiku 4.5 $1 / $5 (batch −50%) | [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing) |
| Human compliance review | **$20/h [A]** × 20 s per post | brief (20 s); rate [A] |
| Performer shoot | $2,250 one-off [A, midpoint of PIPELINE $1.5–3K] + $500/quarter refresh, over 90 days = **$30.56/day** (full only) | PIPELINE.md |
| Assembly VPS | **$90/mo per 8-vCPU dedicated box [A]**; 1 orchestration box + ceil(files × 1.5 CPU-min ÷ 5,760) assembly boxes = 2 boxes in every scenario | [Hetzner Jun 2026 price adjustment](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/), [Northflank on the increases](https://northflank.com/blog/hetzner-cloud-server-price-increases) |
| Storage / CDN | R2 $0.015/GB-month, **egress free**; 25 MB per file + 50 MB intermediates per master, 90-day retention [A] | [Cloudflare R2 pricing](https://developers.cloudflare.com/r2/pricing/) |
| n8n / Supabase / Vercel / email | n8n self-hosted $0 · Supabase Pro $25 (+$15 compute [A]) · Vercel Pro $20 × 2 seats [A] · Resend Pro $20 (50K emails) = **$100/mo** | [n8n pricing](https://www.nocode.mba/articles/n8n-pricing), [Supabase](https://supabase.com/pricing), [Vercel](https://vercel.com/pricing), [Resend](https://resend.com/docs/knowledge-base/what-is-resend-pricing) |
| Posting tools | Direct platform APIs from n8n ($0) + ManyChat Pro **$29/mo per page** (2,500 active contacts, then $0.05 each) | [ManyChat pricing](https://manychat.com/pricing) |
| Payment fees (breakeven only) | 2.9% + 30¢ per charge [verify the store's plan]; 12% refunds (BLITZ §13.1) | [Shopify card-fee guide](https://www.shopify.com/blog/credit-card-processing-fees) |

### Lane recipes per master (42 s mean; retakes: images ×1.5, lip-sync ×1.15, motion ×1.3, inserts ×1.25, TTS ×1.3 [A])

| Lane | Generated per master | Cost |
|---|---|---|
| talking_head (render_day1.py as coded: the **whole track** is lip-synced, then trimmed) | 3 stills, 50 s lip-sync (incl. 2 × 4 s TikTok/YouTube CTA swaps), 2 × 8 s Veo | **$6.53** |
| movement | 3 stills, 25 s motion control, 25 s lip-sync, 1 × 8 s Veo | **$5.70** |
| insert (no face) | 7 stills, 3 × 8 s Veo | **$5.20** |
| Every master adds | ~940 TTS chars; Sonnet gen + judge, 6 × Haiku caption + judge = $0.134; 2 Threads/X posts (30% carousels, 2 AI images each) | |

The plan's lane mix from D+7 on is talking-head 48%, movement 26%, insert 26% (`posting_plan_90d.csv`). Lean moves the movement share into talking-head.

## 2. Totals (no paid amplification)

| Config | Pages | Posts/day/platform | Posts/day | Masters/day | $/day | $/month | $/post | $/1K views, page age 15 d · 75 d | Breakeven MRR (members) |
|---|---|---|---|---|---|---|---|---|---|
| full | 3 | 3 | 54 | 9 | $106 | $3,208 | $1.95 | $0.56 · $0.22 | $3,801 (152) |
| full | 3 | 6 | 108 | 18 | $168 | $5,110 | $1.56 | $0.44 · $0.17 | $6,055 (242) |
| full | 3 | 9 | 162 | 27 | $231 | $7,012 | $1.42 | $0.41 · $0.16 | $8,308 (332) |
| full | 5 | 3 | 90 | 15 | $149 | $4,534 | $1.66 | $0.47 · $0.18 | $5,372 (215) |
| full | 5 | 6 | 180 | 30 | $253 | $7,704 | $1.41 | $0.40 · $0.16 | $9,128 (365) |
| full | 5 | 9 | 270 | 45 | $358 | $10,874 | $1.32 | $0.38 · $0.15 | $12,885 (515) |
| full | 7 | 3 | 126 | 21 | $193 | $5,860 | $1.53 | $0.44 · $0.17 | $6,943 (278) |
| full | 7 | 6 | 252 | 42 | $339 | $10,298 | $1.34 | $0.38 · $0.15 | $12,202 (488) |
| full | 7 | 9 | 378 | 63 | $485 | $14,735 | $1.28 | $0.37 · $0.14 | $17,461 (698) |
| lean | 3 | 3 | 54 | 9 | $77 | $2,338 | $1.42 | $0.41 · $0.16 | $2,771 (111) |
| lean | 3 | 6 | 108 | 18 | $141 | $4,300 | $1.31 | $0.37 · $0.15 | $5,095 (204) |
| lean | 3 | 9 | 162 | 27 | $206 | $6,261 | $1.27 | $0.36 · $0.14 | $7,419 (297) |
| lean | 5 | 3 | 90 | 15 | $122 | $3,704 | $1.35 | $0.39 · $0.15 | $4,389 (176) |
| lean | 5 | 6 | 180 | 30 | $229 | $6,973 | $1.27 | $0.36 · $0.14 | $8,262 (330) |
| lean | 5 | 9 | 270 | 45 | $337 | $10,242 | $1.25 | $0.36 · $0.14 | $12,136 (485) |
| lean | 7 | 3 | 126 | 21 | $167 | $5,069 | $1.32 | $0.38 · $0.15 | $6,007 (240) |
| lean | 7 | 6 | 252 | 42 | $317 | $9,646 | $1.26 | $0.36 · $0.14 | $11,430 (457) |
| lean | 7 | 9 | 378 | 63 | $468 | $14,223 | $1.24 | $0.35 · $0.14 | $16,853 (674) |

$/month = $/day × 30.4. $/post = production cost ÷ all posts, text posts included; per video file it's about 1.5× that.

How the reach and breakeven columns are worked out:
- **$/1K views** uses the central reach in BLITZ §13.2: 6,000 mean views per video post at page age 15 d, growing ×1.6 every 30 d (×2.56 by age 75 d, under the 40K cap). Platform multipliers are IG 1.3 / FB 1.0 / TT 0.7 / YT 0.5, and Threads/X count as 0. At conservative reach (×0.35) the figures roughly triple.
- **Breakeven MRR** is the total monthly cost ÷ $25 × (1 − 2.9%) − 30¢, × (1 − 12% refunds) = $21.11 net per member-month.

### Component breakdown, full config, $/day

| Line | 3p×3 | 3p×6 | 3p×9 | 5p×3 | 5p×6 | 5p×9 | 7p×3 | 7p×6 | 7p×9 |
|---|---|---|---|---|---|---|---|---|---|
| Nano Banana stills | 4.38 | 8.76 | 13.13 | 7.30 | 14.59 | 21.89 | 10.21 | 20.43 | 30.64 |
| Kling lip-sync | 17.71 | 35.42 | 53.13 | 29.52 | 59.04 | 88.55 | 41.32 | 82.65 | 123.97 |
| Kling motion control | 5.37 | 10.73 | 16.10 | 8.94 | 17.89 | 26.83 | 12.52 | 25.04 | 37.56 |
| Veo inserts | 27.00 | 54.00 | 81.00 | 45.00 | 90.00 | 135.00 | 63.00 | 126.00 | 189.00 |
| ElevenLabs (tier) | 1.17 | 2.01 | 2.86 | 1.73 | 3.14 | 4.54 | 2.29 | 4.26 | 6.23 |
| Claude gen + judge | 1.21 | 2.41 | 3.62 | 2.01 | 4.02 | 6.03 | 2.81 | 5.63 | 8.44 |
| Human review | 6.00 | 12.00 | 18.00 | 10.00 | 20.00 | 30.00 | 14.00 | 28.00 | 42.00 |
| Performer shoot | 30.56 | 30.56 | 30.56 | 30.56 | 30.56 | 30.56 | 30.56 | 30.56 | 30.56 |
| VPS assembly | 5.92 | 5.92 | 5.92 | 5.92 | 5.92 | 5.92 | 5.92 | 5.92 | 5.92 |
| Storage / CDN | 0.06 | 0.12 | 0.18 | 0.10 | 0.20 | 0.30 | 0.14 | 0.28 | 0.42 |
| n8n/Supabase/Vercel/email | 3.29 | 3.29 | 3.29 | 3.29 | 3.29 | 3.29 | 3.29 | 3.29 | 3.29 |
| Posting tools | 2.86 | 2.86 | 2.86 | 4.77 | 4.77 | 4.77 | 6.68 | 6.68 | 6.68 |
| **Production** | **105.52** | **168.08** | **230.65** | **149.14** | **253.41** | **357.68** | **192.75** | **338.74** | **484.72** |

**Veo inserts (~40%) and lip-sync (~25%) make up two-thirds of the cost.** Claude, voice, storage and SaaS together come to under 10%.

### Optional paid amplification (full config): $/month · breakeven MRR

| Amp $/day | 3p×3 | 3p×6 | 3p×9 | 5p×3 | 5p×6 | 5p×9 | 7p×3 | 7p×6 | 7p×9 |
|---|---|---|---|---|---|---|---|---|---|
| $0 | $3.2K · $3.8K | $5.1K · $6.1K | $7.0K · $8.3K | $4.5K · $5.4K | $7.7K · $9.1K | $10.9K · $12.9K | $5.9K · $6.9K | $10.3K · $12.2K | $14.7K · $17.5K |
| $500 | $18.4K · $21.8K | $20.3K · $24.1K | $22.2K · $26.3K | $19.7K · $23.4K | $22.9K · $27.1K | $26.1K · $30.9K | $21.1K · $25.0K | $25.5K · $30.2K | $29.9K · $35.5K |
| $1,500 | $48.8K · $57.8K | $50.7K · $60.1K | $52.6K · $62.3K | $50.1K · $59.4K | $53.3K · $63.2K | $56.5K · $66.9K | $51.5K · $61.0K | $55.9K · $66.2K | $60.3K · $71.5K |

Paid spend stays under the spend governor's caps (BLITZ §9/§11) and boosts only WINNER posts. At $500/day or more, amplification costs more than the whole production engine.

## 3. Breakeven: the cadence each MRR level pays for (no amp; posts/day/platform/page, max 9)

| MRR | full 3 pages | full 5 | full 7 | lean 3 | lean 5 | lean 7 |
|---|---|---|---|---|---|---|
| $5K | 4.5 | 2.7 | 1.8 | 5.8 | 3.4 | 2.4 |
| $10K | 9 (cap) | 6.6 | 4.7 | 9 (cap) | 7.3 | 5.2 |
| $15K | 9 | 9 (cap) | 7.5 | 9 | 9 (cap) | 7.9 |
| $20K | 9 | 9 | 9 (cap) | 9 | 9 | 9 (cap) |

The full 7-page × 7/day plan needs about **$14.0K MRR (~560 retained members)** ($387/day) to pay for its own production.

## 4. Lean vs full

- **Lean** is talking-head plus inserts only: no movement lane and no performer shoot.
- **Full** adds Kling Motion Control from the performer clips.
- A movement master is *cheaper* than a talking-head master ($5.70 vs $6.53), because render_day1.py lip-syncs the whole track. So lean saves only the shoot amortization: **about $17–30/day, $500–870/month**.
- Lean also loses the exercise demos, which are the safety moat (PIPELINE §driving-video library) and 26% of the plan's masters. The case for lean is speed (no shoot on the critical path), not cost.

## 5. This plan (POSTING_PLAN.md, D−7…D+90, no amp)

**≈ $29.7K over 98 days** (≈ $24.9K generation, review and Claude; $4.4K fixed plus the shoot; ElevenLabs ≈ $0.4K), or **$1.37 per post**. By month: Oct ≈ $4.5K variable, Nov ≈ $8.9K, Dec ≈ $9.6K.

## 6. Levers (not applied in the central numbers)

1. **Lip-sync only the talk windows** instead of the whole track. render_day1 trims after lip-syncing the full audio, so talking-head lip-sync drops ~50%: about −$49/day at 7p×9.
2. **Veo through the Gemini API directly** ($0.10/s vs fal's $0.15/s): −33% on inserts, about −$63/day at 7p×9. This needs a key outside the current fal allow-list.
3. **Batch Nano Banana** ($0.034): −50% on stills.
4. Batch API for the Claude judge passes: −50% on a small line.

Together, levers 1–3 cut full 7p×9 from ~$485/day to ~$357/day (−26%).

## 7. Caveats

- Retake factors, seconds per lane, the reviewer rate, the VPS price and the token counts are all [A]. Re-run `python3 tools/build_costs.py` (or edit the yellow cells) once `costs.jsonl` from a real `render_day1.py` run exists. Use its per-step actuals.
- ManyChat contact overage isn't modelled: $0.05 per active contact beyond 2,500 per page per month.
- `economics.xlsx` was saved with openpyxl, so its formula cells recalculate when the file is next opened in Excel or LibreOffice.
