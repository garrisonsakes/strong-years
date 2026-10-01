# LAUNCH_CHECKLIST.md: items the audit found missing or partial

> **Superseded as the launch sequence by [`LAUNCH_RUNBOOK.md`](LAUNCH_RUNBOOK.md)** (Oct 1 2026). This file remains the audit-derived item list with owners and costs. Items that changed: #8 sales tax is Shopify Tax, not Stripe Tax; #9 the descriptor is set in Shopify Payments; #21 watermarking is done by the members app (Digital Downloads is not used); #26 processor 2 is moot on Shopify Payments at launch; #31 the open decisions are listed in LAUNCH_RUNBOOK.md §10.


Source: AUDIT_BUSINESS.md §8 ("Missing entirely") plus the audit findings that need a build, a document or a decision. Owners follow BLITZ_OPS.md: **G** Garrison · **CL** content lead · **DEV** developer · **VA1** content QA / ad ops · **VA2** community / DMs · **SUP** support · **ATT** consumer-protection attorney · **REV** credentialed reviewer · **PERF** movement performer. Deadlines are relative to launch: **D−10 … D−1** are build days, **L1** is launch day (example calendar: D−10 = Fri Oct 2 2026, L1 = Mon Oct 12 2026).

Status key: **Missing** (nothing exists) · **Partial** (exists but incomplete or contradicted) · **Drafted** (a draft exists and needs review or signature) · **Exists** (built; only verify) · **In progress, verify** (being built now; confirm before launch) · **Open** (not started).

Costs are estimates marked [A] where unbenchmarked. One-time costs are shown first; monthly costs after "/mo".

---

## 1. Blockers: nothing launches without these

| # | Item | What "done" means | Owner | Deadline | Cost | Status |
|---|---|---|---|---|---|---|
| 1 | **Member session production** (AUDIT F01, critical) | Sessions 1–30 rendered for all 4 tracks (Rebuild, Steady, Strong, Iron), and weeks 1–4 of at least 2 of the six 12-week programs, with release dates for the rest shown on the programs page. After launch: 1 session a day plus 4 program sessions a week, with a named owner. The $27 keep-forever upsell is sold only for completed programs, or as a dated pre-order. | CL (REV reviews once signed) | Sessions 1–30 + 2 program starts by **D−1**; cadence from L1 | $6K/mo member-content budget (Assumptions!E115) [A] | **Partial**: sessions 1–30 and all six 12-week programs are written (`products/daily_practice_sessions_1-30`, `products/programs/`); `VIDEO_PRODUCTION_QUEUE.json` lists 73 videos (~$6.3K). **No member video is rendered yet** (needs the client's generation keys and cash) |
| 2 | **Terms of service** | A full ToS: exercise risk acknowledgment (clickwrap at checkout and before the first session), limitation of liability, arbitration and class waiver, governing law, 18+ eligibility, AI-chat terms, community rules, IP licence, DMCA agent. Links from `/join`, the footer and the app. | ATT | Draft **D−6**, final **D−3** | $3–6K [A] | **Missing** (`/terms` is a policy summary) |
| 3 | **Refund, cancellation and add-on policy page** | `/refunds` states the canonical policy (FUNNEL.md top): 14-day money-back guarantee on the membership charge, one per person; add-ons refunded on request within 14 days; kit 30 days; bonus download vests on day 15; how to cancel. Matches the terms box on `/join` word for word. | DEV (copy: G, ATT review) | **D−4** | — | **Partial** (route exists; copy must match the canonical policy) |
| 4 | **Privacy policy, consumer health data policy, Your Privacy Choices** | Full privacy policy (entity, categories, purposes, subprocessors, retention, CPRA "sharing" disclosure, GPC honoured); a separate Washington MHMDA consumer health data policy; a "Your Privacy Choices" link on every page; opt-in consent for health data (quiz answers, chat memory). No false statements about what goes to ad platforms. | ATT + DEV | **D−4** | $2–4K [A] (with #2) | **Partial** (`/privacy`, `/health-data`, `/privacy-choices` routes exist; counsel review of content pending) |
| 5 | **Data processing inventory** | Record of processing, subprocessor list (Stripe, Supabase, Anthropic, ElevenLabs, Twilio, ManyChat, Mux, Meta, the ESP, the help desk), DPAs signed, retention schedule, zero-retention settings for chat where offered. | DEV + ATT | **D−5** | $0–2K | **Missing** |
| 6 | **Entity setup** | Decision D2 made; formation or selection, EIN, bank account, registered agent; written note on the relationship with Unignorable and K9SUPPS (decides whether "made by the same team" may be said). | G (+ accountant) | **D−10** (processor applications depend on it) | $500–1.5K | **Partial** (decision only) |
| 7 | **Insurance** | Bound: general liability, professional liability for fitness instruction, media/IP liability, cyber, product liability for the kit. Certificates on file. | G + broker | Quotes **D−8**, bound **D−2** | $8–15K/yr [A] | **Missing** |
| 8 | **Sales tax** | Stripe Tax on for digital subscriptions and the physical kit; nexus monitoring (e.g. WA, PA, TX tax digital goods); registration where required. | G + accountant | **D−7** | Stripe Tax ~0.5% of taxed volume; CPA $1–2K | **Missing** |
| 9 | **Merchant descriptor** | `STRONGYEARS MEMBER` + support URL and billing phone on the processor; the same name on receipts, welcome and renewal emails; verified on a real bank statement (BLITZ_OPS §1.6 row 12). | DEV | Configure **D−7**, verify **D−1** | — | **Exists** (verify) |
| 10 | **Auto-renewal compliance jobs** | Reminder email before every renewal charge (7 and 2 days before the first, 3 days before each later one; 30 days before annual); California annual reminder every 12 months for all auto-renewing members; price-change notice exactly 30 days ahead; `{{IF_SMS}}` rendering so "text CANCEL" never shows while SMS is off. | DEV | **D−4** | — | **Exists, verify**: reminders before every charge and the yearly California notice are in the app (`clock.ts`); `{{IF_SMS}}` gating on every surface (AUDIT_FINAL F09/F10/F11 PASS) |
| 11 | **50-state auto-renewal matrix** | Counsel's matrix (CA, NY GBL §527-a acknowledgment contents, MN, VA, CO at minimum) wired into `legal_pack`; confirmation email B/B2 (FUNNEL §5.5) checked against it. | ATT | **D−4** | incl. in launch legal $10–25K | **Missing** |
| 12 | **Published crisis protocol + incident log** | `/safety` shows the crisis protocol exactly as FUNNEL §4.14 and §6.3a (SB 243); an incident log table with timestamps, channel, category, response time; the NY 3-hour re-disclosure timer live in the chat. | DEV (copy CL) | **D−3** | — | **Exists, verify**: `/safety` published, 3-hour re-disclosure live (`chat.ts`); incident log to verify |
| 13 | **Moderation and crisis roster** | Named people and phone numbers for 07:00–23:00 ET, 7 days (BLITZ_OPS §1.3, §8.1); crisis tabletop done (§8.3). **Decision:** buy overnight coverage (BPO or paid rotation) or keep the honest "a person reads it at 7am" wording (the canonical copy already assumes no 24/7 human). | G | Roster **D−3**; coverage decision **D−5** | Overnight BPO $3–8K/mo [A] | **Partial** (07:00–23:00 only) |
| 14 | **Reviewer contract** | `TEMPLATES/reviewer_contract.md` reviewed by counsel, signed by REV, credential verified, naming consent captured. Only then flip `REVIEWER_SIGNED=true` and publish the gated copy. | ATT → G → REV | Counsel **D−6**, signature any time (launch runs on FALLBACK copy until then) | Counsel $500–1K; reviewer $2.5–6K/mo (Assumptions!E113 says $6K, PIPELINE.md $2.5–3.5K: reconcile) | **Drafted** |
| 15 | **Performer likeness / motion-capture release** | `TEMPLATES/performer_release.md` reviewed by counsel; signed by every performer and demonstrator (including the real "Frank" demonstrator) **before** any capture used to drive AI renders. | ATT → CL → PERF | Counsel **D−8**, signed before first capture | Counsel $500–1K | **Drafted** |

## 2. Needed at launch (launch can proceed, but not without a named owner and date)

| # | Item | What "done" means | Owner | Deadline | Cost | Status |
|---|---|---|---|---|---|---|
| 16 | **Customer support tool** | Help Scout or Gorgias with BLITZ_OPS §8 macros, the `help@` inbox, the billing phone line, refund macros matching the canonical policy. | SUP + DEV | **D−9** | ~$25–75 per user/mo [A] | **Exists** (specified in BLITZ_OPS §1.2; set up and test) |
| 17 | **Character reference-pack generation job** | CHARACTERS.md §13.1 job run; approved reference pack locked and versioned before any launch render. | CL | **D−10** | ~$50–150 of image credits [A] | **Exists** (run it) |
| 18 | **Creative testing matrix** | Spec below (§3) loaded into the ad-ops sheet; each launch ad named by cell. | VA1 + G | **D−3** | — | **Partial** (ADS.md §5, BLITZ_OPS §6.2/§6.6) |
| 19 | **Dashboard: cohort and renewal views** | Add to the KPI dashboard: MRR net of open refund windows; renewal-adjusted MRR (members × expected renewal-1 survival); renewal 1 by channel and price cell; refund rate by channel; founding count vs processors. Milestones are reported on both MRR lines. | DEV | KPI views **D−2**; cohort views by **L25** (first renewal reminders) | — | **Partial** (BLITZ_OPS §7.2, `/admin`) |
| 20 | **Pages the plan links to** | `/live` and `/live/replay` built (or the YouTube Premiere fallback wired from `/start?ev=live`); warm variants `/start?v=w` and `/start?v=walk`; partner/shoutout `?via=` tracking; FUNNEL lesson pages (`/s/l0`–`/s/l8` and variants), `/go`, `/tt`, `/yt` either built or pointed at existing routes. Link check in the D−1 rehearsal. | DEV | **D−8** (`/live`), **D−2** (the rest) | — | **Missing** |
| 21 | **Refund-abuse controls** | PDFs watermarked with the buyer's email; bonus download vests on day 15; self-serve refund limited to the membership, one per person; repeat refunders flagged by card fingerprint. | DEV | **D−4** | — | **Partial**: day-15 vesting and one guarantee per person are built; **PDF watermarking is in progress, verify** (customer copy no longer promises it until verified) |
| 22 | **Warm-list sign-off** | Counsel's written sign-off on using the Unignorable list for Strong Years (BLITZ_OPS §3.1 consent gaps); WA/NV/CT suppression; per-number SMS consent records or no SMS. | ATT + G | **D−4** | incl. in launch legal | **Missing** |
| 23 | **Email domain warm-up** | Warm-up schedule per BLITZ_OPS §3.1 item 5; DMARC to quarantine after 14 clean days. | G | Start **D−10** | — | **Missing** |
| 24 | **SMS registration** | 10DLC brand + campaign **and** toll-free verification submitted in parallel (whichever clears first). | DEV | Submitted **D−10** | ~$50 one-time + monthly fees [A] | **Partial** (3–6 week lead time) |
| 25 | **Web push (PWA)** | Android and iOS home-screen web push live, so first cohorts have a daily trigger before SMS clears (AUDIT F17). | DEV | **D−2** | — | **In progress, verify** (being built now; AUDIT_FINAL found no service worker or manifest at its check) |
| 26 | **Processor 2 or pre-approval** | Braintree `payments` abstraction built, or written Stripe volume pre-approval for the planned month-1 volume. | DEV / G | Pre-approval **D−5**; Braintree target **L21** | — | **Missing** |
| 27 | **Ad-account capacity** | The chosen account's spending limit ≥ $15K/day confirmed, or a fresh Strong Years account seeded now with a spend ramp in the model (AUDIT F16). | G | **D−10** (seed a fresh account ~D−30 if needed) | — | **Partial** |
| 28 | **Organic amplification gate** | Any organic post flagged for Spark/Partnership ads passes the ADS validator; condition hashtags replaced with activity tags; S09's "58% FEWER FALLS" thumbnail reworded (AUDIT F15). | CL + VA1 | **D−2** | — | **Missing** |
| 29 | **Affiliate onboarding** | Affiliate agreement template (counsel), W-9/W-8 collection before first payout, 1099 filing at the $2,000 threshold. | G + ATT | Before affiliates go live (**L10**) | incl. in launch legal | **Partial** (terms described, no template) |
| 30 | **Accessibility audit** | WCAG 2.2 AA check on `/join`, `/q/a`, `/q/b` and the account/cancel screens at the largest iPhone text size. | DEV | **D−3** | $0–2K [A] | **Partial** (palette only) |
| 31 | **Client decisions still open** | D4 standard price (default $35); `FOUNDING_CLOSE_DATE` (default L90); founding annual $249 from L35; launch spend strategy (auditor: $3K/day L1–L3 → L4 gate); 24/7 coverage (#13). | G | **D−5** | — | **Open** |

## 2a. Engineering blockers from AUDIT_FINAL.md (owned by the app agent; tracked here so launch can't miss them)

| # | Item | What "done" means | Owner | Deadline | Cost | Status |
|---|---|---|---|---|---|---|
| 32 | **NEW-1: account takeover through checkout** (critical) | Checkout with an existing member's email never mints a session (magic link instead) and never overwrites an existing Stripe customer or payment method; regression test re-runs checkout with an existing email. | DEV | Before any paid traffic | — | **Open** |
| 33 | **Crisis detector v2** (C2) | LLM classifier required in production (boot assertion, fail closed); lexicon widened with the 11 misses in AUDIT_FINAL §2a; a held-out corpus the lexicon was never tuned on; benign false positives re-checked. | DEV | Before any paid traffic | `ANTHROPIC_API_KEY` usage | **In progress, verify** |
| 34 | **Scanner hardening** (H10) | Diacritic folding for match-only en-US rules, em/en dashes as separators, `*` inside a word as a wildcard for banned stems; mirrored in the n8n JS pre-scan; AUDIT_FINAL's 10 bypass strings all blocked. | DEV | Before content goes live | — | **In progress, verify** |

## 3. Creative testing matrix (spec for item 18)

**Cells:** concept (ADS_SCRIPTS.md concept ID) × hook (3 per concept) × format (UGC, follow-along, quiz static, test demo) × audience (W 55–70, M 60–75, AC 35–55, CG). Not every combination runs: each week tests **4 concepts × 3 hooks** in one format per concept, on the audience the concept was written for.

**Budget per cell:** $60–120/day per ad set (one concept, 3 hook ads), 3–5 days, or until 1.5× the target cost per member is spent.

**Naming:** `{camp}_{aud}_{concept}_{hook}_{format}_{yyyymmdd}` (ADS.md §4.1).

**Decision rule:** a hook wins inside its concept when its cost per paid opt-in is ≥ 20% better than the concept median on ≥ 150 opt-ins per arm (or 2× target spend without a result = loss). A concept graduates to the scaling campaign on ≥ 10 purchases at or under the blended band in BLITZ_OPS §6.4. Kill on hook rate < 20% after 3,000 impressions. The L1–L5 price test ($25 vs $30) and the bump test (one bump vs three) run on-site, never by duplicating ads.

**Log:** one row per ad (cell, spend, hook rate, CTR, cost per opt-in, arm-B purchase rate, refund rate by ad at day 14); VA1 updates at 09:30 daily.

## 4. Launch legal budget (reconciled)

Checkout and terms review, ToS, privacy and consumer health data policies, the reviewer, performer and affiliate contracts, cross-brand sends and the 50-state matrix: **$10–25K one-time** (FUNNEL.md §0.5 now says the same; the old $2–5K line was too low per AUDIT F29).
