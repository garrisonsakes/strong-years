# EXPANSION.md: cloning the Chang Yin / Sun Yoon system into new languages and markets

**Scope.** This file covers the market scoring and rollout order, the two localization modes, the "market pack" that makes a new market config instead of a rebuild, the operating model (QA, support, payments, tax, time zones), a 90-day expansion calendar with go/no-go gates, and a full launch kit for the #1 non-English market (Spanish, led by US Hispanic and Mexico).

**Companion files.** SAFETY_RULES.md (disclosure strings, blocked claims, emergency numbers per market), EVIDENCE.md (E-IDs cited below), prompts/08_localization_adapter.md (transcreation stage), economics.xlsx and mrr_scenarios.csv (US model).

**Citation convention.** `[S#]` refers to the source list at the end. `[E#]` refers to EVIDENCE.md. "EST" marks our own estimate, with the method stated. FX placeholders are marked "FX" and must be refreshed from a live rate API at config time.

---

## 0A. CANON UPDATE (Oct 2 2026): ES → PT → DE on the scale-on-MRR ladder (supersedes conflicting lines below)

**What changed.** BRIEF.md CANON UPDATE 5 replaced calendar triggers with the governor's MRR ladder, and the Spanish build now exists (CHARACTERS_ES.md, OFFER_ES.md, SCRIPTS_ES.md). Where §0–§5 below differ, this section wins:
- **Spanish opens at the $30K retained-MRR rung** (config row in workers/growth/config.py `governor.scale_rules`; plan rows via `ES_START_D` in tools/build_posting_plan.py), not at "US month 4–5" or the §4 day-0 trigger list.
- **Native first, no Mode A pilot.** The Spanish page is **Don Chuy & Doña Lupe (@donchuyylupe)** from day one; @changyin.espanol is retired (its scripts post on @changyin). Doña Carmen is staged for the $50K rung or the day-30 switch rule (CHARACTERS_ES.md §0).
- **US Hispanic first, in USD, on the US Shopify market with Spanish enabled** (same prices and cells as the US, OFFER_ES.md §2). MXN / EUR / LATAM price books in §5.7 become later config rows (after the Spanish Gate 2), each needing its own currency/payment decision. **No $1 trial anywhere** (CANON UPDATE 2): every "7 days for $1" cell in §5.7 is void.
- **PT-BR and DE open at the $100K rung** ("open PT/DE clones", CANON UPDATE 5), PT first, DE when PT has passed its Gate 1 (§4.2 KPIs, measured from each page's own start). Italy, France and the rest keep the §1.6 order behind them.

### 0A.1 Sequence

| Step | Rung (retained MRR) | Language / market | Show | Why this order |
|---|---|---|---|---|
| 1 | $30K | **es-US** (Mexican-American first; MX/ES/LATAM by later price-book rows) | Don Chuy & Doña Lupe (duo); Doña Carmen staged | Full US ARPU in USD, no new entity or tax regime, same Shopify store; largest 55+ language cluster (§0) |
| 2 | $100K | **pt-BR** | Vô Tonico & Dona Graça (ARCHETYPES.md #4; run the same duo-vs-single test as CHARACTERS_ES.md §0) | Largest single-country 55+ audience, WhatsApp-forward culture like the Spanish one, Pix Automático rails (§3.3); lower ARPU, so it waits for the rung where cost is immaterial |
| 3 | $100K + PT Gate 1 | **de-DE** (DACH) | Oma Ingrid Brandt (#7), single | Highest EU ARPU but the heaviest compliance (HWG, Kündigungsbutton, Widerruf); 50–69s prefer articles, so pair video with carousels/text posts (§1.6) |

### 0A.2 The clone checklist (the Spanish build is the template; one PR per language)

| # | Step | Spanish artifact (template) | Done when |
|---|---|---|---|
| 1 | **Gate.** The ladder row for the language is reached; the governor flips it. No generation, handle or translator spend before. | workers/growth/config.py ladder; BRIEF CANON 5 | The rung is logged in the governor's decision log |
| 2 | **Research brief** (≤12 searches, cited): platform use for 55+ in that language, health priorities vs the local health-advertising law, the top local 55+ health creators, cultural review needs | CHARACTERS_ES.md §1, §16 | Every number has a source line |
| 3 | **Duo vs single decision** with a scored table and a day-30 switch rule | CHARACTERS_ES.md §0 | Decision + switch thresholds written |
| 4 | **Bible in CHARACTERS.md format**: ages, openly fictional AI-disclosed origin, house/kitchen/patio sets, wardrobe codes, voice cards with regional choices and catchphrases, 24 running bits, family cast (no minors on camera), never-say list, the "I'm AI" line, writer system prompts | CHARACTERS_ES.md §2–§12 | The native cultural reviewer signs the bible |
| 5 | **Reference pack**: 24 prompts per character + duo, same schema and sha256 lock; staged characters marked STAGED | production/refs_es/ (build_manifest.py, manifest.json, ACCEPTANCE.md, render_refs_es.py) | 54 locked images (duo case) with both reviewers' names |
| 6 | **Voices**: ElevenLabs design prompts (designed, never cloned), 10 calibration lines each, pronunciation lexicon + aliases, number/price reading rules | production/voices/es/ | One voice_id locked per character |
| 7 | **Claims layer**: the language's patterns added to prompts/blocked_claims.json (new BC ids, `"lang"`, accent-tolerant, not MB-EX eligible: myth-busts never quote "remedy + condition"); a language validator hooked into tools/build_content.py; tests | BC26–BC37; tools/build_content_es.py; tools/test_build_content_es.py | English corpus still 0 hits; workers tests green |
| 8 | **Content**: 40 scripts (25 runway, 15 launch) + 40 hooks on the proven grammars with language-specific detectors (IF_EVERY / NOT_X / MYTH / WATCH ≥45%) | data/content/hooks_es.psv, scripts_es.py → SCRIPTS_ES.md | Validator PASS + reviewer sign-off on all 40 |
| 9 | **Offer**: handles, storefront (Shopify Markets language; same price where the market is the US, a currency decision elsewhere), offer copy, legal copy flagged ⚖ for attorney + certified translator, 3 onboarding emails | OFFER_ES.md | Both legal sign-offs logged |
| 10 | **Funnel**: the waitlist / book / join DM flows in the language | FUNNEL.md §4.20–4.22 | ManyChat flows built with `lang` tags |
| 11 | **Posting plan**: page rows with a configurable start and the page's own runway → launch clock, keyword map | tools/build_posting_plan.py (`ES_PAGES`, `ES_START_D`, `local_d`), tools/validate_plan.py | Plan validates with the start set |
| 12 | **People**: two paid cultural reviewers (community + language/health-comms), an in-language human inbox, first 50 scripts reviewed in full, then 10 random per 2 weeks | CHARACTERS_ES.md §14 | Contracts signed |
| 13 | **Gates**: §4.2 KPIs measured from the page's own start; kill/hold rules unchanged | §4.2 | Gate 1 read at day 14 |

### 0A.3 Per-language deltas for PT and DE (fill steps 2–13 with these)

| Item | pt-BR | de-DE |
|---|---|---|
| Keywords (STRONG/BALANCE/SOUP/BEGIN/TEST/FAMILY · WAITLIST/BOOK/JOIN) | FORTE / EQUILÍBRIO / SOPA / COMEÇAR / TESTE / FAMÍLIA · LISTA / LIVRO / ENTRAR | STARK / BALANCE / SUPPE / START / TEST / FAMILIE · LISTE / BUCH / MITMACHEN |
| Register | *você*, warm; Graça teases, Tonico demonstrates | *Sie* to viewers (test *du* only after reviewer advice); Oma precise and dry |
| Claims words to add (BC, lang tag) | cura/curar, milagre, desintoxica/limpa o fígado, "baixa a pressão/o açúcar", "controla o diabetes", "pare o remédio", "segredo", garantia outside "garantia de reembolso de 14 dias" (BR statutory withdrawal is 7 days: legal confirms the wording), "vitalício" | heilt/Heilung, Wunder, entgiften/Entschlackung, "senkt Blutzucker/Blutdruck", "gegen Diabetes", "Medikamente absetzen", Geheimnis, Garantie outside "14-Tage-Geld-zurück-Garantie", "lebenslang"; HWG counsel reviews the list |
| Myth-bust rule | Quote the remedy, never "remedy + condition" (the ARCHETYPES #4 onion-water hook becomes "Água de cebola em jejum? Não."); same for every market | same |
| Legal copy ⚖ | CONAR/ANVISA, CDC Art. 49 withdrawal, LGPD; attorney + sworn translator | HWG/HCVO, Kündigungsbutton, Widerrufsbelehrung, Impressum, AI Act Art. 50; Abmahnung-proof review before any post |
| Price / rails | R$ price book (§1.3) + Pix Automático; a currency/MoR decision (Shopify Markets local currency only where its payments support it; verify before build) | EUR via the EU stack (§3.3–3.4), SEPA + PayPal; 14-day Widerruf flow |
| Format note | WhatsApp Channel for top-of-funnel (free); Kwai labeling if used | Carousels and text posts alongside video (§1.6) |

## 0. Decision summary

| Question | Answer |
|---|---|
| Rollout order | **0) English Commonwealth** (UK/CA/AU/IE/NZ): a pricing and tax switch, no new content. → **1) Spanish cluster**: US Hispanic + Mexico first, then Spain and the rest of LATAM through geo-pricing on the same pages. → **2) Brazil (pt-BR).** → **3) Italy.** → **4) DACH**, then **France.** → Opportunistic: **Philippines** (English content already reaches it; low ARPU). → Later, native-archetype only: **Poland/CEE, Japan, Korea.** → **India** only as a YouTube/ad-revenue play. → **MENA Arabic: hold.** |
| #1 non-English market | **Spanish, led from US Hispanic + Mexico.** One language pack reaches about 63M Facebook accounts aged 55+ across US-Hisp/MX/ES/LATAM (EST, NapoleonCat Aug 2026 [S3]), 2.3× Brazil. The US Hispanic slice pays full US prices in USD, under the same legal entity, the same FTC/ROSCA regime and the same processor as the US launch. Mexico adds cheap reach (FB CPM about $2–4 vs about $16 in the US [S1][S2]). The demand is proven: Yang Mun already sells in ES, and there are 50 Spanish-language AI "health" profiles with 12.6M followers, most selling $11–35 guides [S16]. The supply is low-trust misinformation. That gap is the whole opportunity for an openly-AI, [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: human-reviewed] FALLBACK: "evidence-cited" brand. |
| Mode | Launch every market in **Mode A** first (Chang & Sun re-voiced natively in the language: 7 days, about $3–6K). Build a **Mode B native archetype** only after a market passes Gate 1. For Spanish, Mode B = "Don Chuy & Doña Lupe" (§5). **Spanish timing (canonical):** Mode A pilot page @changyin.espanol from US day 30 at 3 posts/day (organic); full Spanish market launch (paid, localized pricing, checkout, the *Años Fuertes* membership) in month 4–5 of the US business, after the US day-10 gate passes and the US reaches its first milestones (§4); Don Chuy & Doña Lupe (@donchuyfuerte) about 3–4 weeks after that launch; Doña Carmen Ruiz (women-led) after Gate 2. |
| Cost to launch a new market | **Mode A: about $4–7K in the first 30 days** (incl. about $2.5K paid test), then about $3.5–6K/month run-rate. **Mode B: about $10–16K over the first 60 days**, then about $5–9K/month. Break-even is about 200–330 paying members in US-Hisp, 260–450 in Spain, 380–650 in Mexico and 420–720 in Brazil (Mode A; ×1.4–1.5 for Mode B) (§3.6). |
| What changes per market | Only the **market pack** (§2.5): character bible, voice IDs, sets, localized recipe DB, glossary, claims linter, CTA keywords, price book, checkout methods, support language, compliance rules, posting schedule. The pipeline code, evidence library and safety engine stay global. |

---

## 1. Market scoring

### 1.1 Raw inputs (15 markets)

"55+ FB accounts" = Meta advertising-audience accounts aged 55–64 plus 65+, from NapoleonCat (Aug 2026 unless noted). These are audience estimates, not unique people. They overstate reach in some countries (Japan especially), but they are consistent across countries. CPM = Facebook feed CPM from 2026 benchmark sets ([S1] Adligator, Mar 2026 ranges; [S2] Lebesgue 2026 point values). "Price level" = World Bank 2024 nominal GDP per capita ÷ PPP GDP per capita [S4]. "Spotify ratio" = local Spotify Premium price in USD ÷ US $11.99 [S5], used as a real-world proxy for how global digital subscriptions actually price locally.

| Market | 55+ FB accts (M) | 55+ IG accts (M) | 65+ pop (M) [S4] | Older-adult internet signal | FB CPM USD | Price level | Spotify ratio | Recurring-payment reality | Notes |
|---|---|---|---|---|---|---|---|---|---|
| EN-Commonwealth (UK/CA/AU/IE/NZ) | ≈25 (CA 9.3, AU 5.9, UK ≈10 EST) [S3] | n/a | UK 13.5, CA 8.2, AU 4.8 | Mature | UK 11.8 / CA 11.5 / AU 11.6 [S2] | 0.84–0.90 | 0.92–1.08 | Cards, Apple/Google Pay, PayPal | English content already reaches these viewers organically from the US pages |
| US Spanish (Hispanic 55+) | ≈7 EST (≈12M Hispanic 55+ × 82% Spanish-primary or bilingual [S11] × ≈70% on FB) | n/a | ≈4.6 Hispanic 65+ (2019) [S12] | 23% of Hispanic 50+ are primarily Spanish-speaking, 59% bilingual [S11] | ≈13–16 (US) [S1][S2] | 1.00 | 1.00 | Cards; higher un/under-banked share → offer PayPal/Cash App Pay | Faith is the #2 value (6 in 10) and family #1 [S11]; 68% of Latinos speak Spanish at home [S10] |
| Mexico | 16.5 [S3] | 4.6 [S3] | 10.8 | 71% of 55+ online (2024) [S7]; 99.5% of adults 18+ on FB (ad-reach basis) [S8] | 2.0–3.9 [S1][S2] | 0.54 | 0.46 | Debit cards; OXXO is cash and **not recurring** [S22]; SPEI; Mercado Pago | Subscription reform in force 13 Dec 2025: 5-day pre-renewal notice, immediate cancel [S32]; 16% IVA from first sale [S26] |
| Brazil (pt-BR) | 31.9 [S3] | 22.3 [S3] | 23.4 | 74.5% of 60+ online in 2025 (IBGE) [S6] | 2.5–4.0 [S1]; 2.63 [S2] | 0.46 | 0.375 | **Pix Automático** recurring, supported by Stripe since Apr 2026 [S19][S20]; cards with installments | 7-day withdrawal (CDC art. 49) [S33]; IOF 3.5% on cross-border since May 2025 [S27]; LGPD |
| Spain | 9.6 [S3] | 5.9 [S3] | 10.3 | High | 5.5–8.0 [S1]; 6.65 [S2] | 0.61 | 1.00 | Cards, SEPA DD, PayPal | 15-day pre-renewal notice (Ley 10/2025) [S31]; EU AI Act Art. 50 [S30]; withdrawal button [S28] |
| LATAM ex-MX (CO/AR/CL/PE/EC…) | ≈30 EST (CO 7.5, AR 7.8 [S3] + others) | n/a | CO 5.2, AR 5.7, CL 2.8, PE 3.2 | High on FB | CO 1.8–3.0, AR 1.5–3.0, CL 3.0–4.5 [S1] | 0.35–0.46 | 0.17–0.46 | Fragmented; FX controls (AR); cards via MoR | 0% registration thresholds for non-residents (CO, CL) [S25] |
| Italy | 13.1 (Jun 2026) [S3] | n/a | 14.5 | 55+ = 28.6% of IT FB audience, the highest share in the set [S3] | 5.0–7.5 [S1]; 6.06 [S2] | 0.65 | 1.00 | Cards, PayPal, SEPA | National AI law 132/2025 on top of the EU AI Act [S37] |
| DACH (DE/AT/CH) | 11.1 (DE 9.3 [S3] + AT/CH ≈1.8 EST) | DE 5.4 [S3] | DE 19.4 | High, but 50–69s prefer articles over video on social (ARD/ZDF 2025) [S62] | DE 8–11 [S1]; 9.05 [S2] | 0.76 | 1.00 | PayPal, SEPA DD, cards, Klarna | **Kündigungsbutton** (§312k BGB, since 2022) + **Widerrufsbutton** (from 19 Jun 2026) [S28]; HWG health-ad law [S60]; Abmahnung culture |
| France | 12.0 [S3] | n/a | 15.2 | High | 7–10 [S1]; 6.95 [S2] | 0.74 | 1.00 | CB cards, PayPal, SEPA | Loi influenceurs 2023: mandatory **"Image virtuelle"** label; ban on promoting therapeutic abstention [S35]; cancellation "en 3 clics" [S59] |
| Poland / CEE | 4.5 [S3] | n/a | 7.4 | Medium | 3.5–5.5 [S1]; 5.55 [S2] | 0.49 | 0.54 | BLIK, P24 (one-time), cards | UOKiK dark-pattern fines ≈PLN 40M [S29] |
| Philippines | 11.9 [S3] | n/a | 6.4 | FB-dominant | 1.5–3.5 [S1]; 3.40 [S2] | 0.34 | ≈0.40 EST | GCash/Maya, cards | English/Taglish; VAT threshold PHP 3M [S25] |
| India (EN/Hindi) | 38.7 [S3] | n/a | 103.7 | Growing | 1.0–1.8 [S1]; 1.36 [S2] | 0.24 | 0.15 | UPI Autopay (e-mandate) | ASCI 2025: health influencers must show **qualifications** [S36]; GST 18% from first sale [S25] |
| Japan | 14.0 (inflated audience est.) [S3] | n/a | 36.9 | SNS use: 60s ≈90%, 70s ≈70%, mostly LINE [S14] | 6.73 [S2] | 0.62 | 0.63 | Cards; konbini (one-time); PayPay | JCT threshold ¥10M [S25]; strict pharma-ad law (PMD Act); LINE-centric |
| South Korea | n/a (FB weak) | n/a | 10.0 | 76.9% of elderly online (2024); YouTube-centric [S15] | 5.80 [S2] | 0.59 | 0.71 | Kakao/Naver Pay, cards | Sun Yoon's Korean heritage could anchor a spin-off (heritage-sensitive, see §2.4) |
| MENA Arabic (KSA/UAE/EG) | KSA 1.55 [S3] + EG/UAE EST | n/a | KSA 1.0, EG 6.0 | Young demographics | KSA 12.01, UAE 10.0, EG 1.81 [S2] | 0.45 avg | ≈0.55 | mada, cards, BNPL | Religious/gender-norm sensitivity; influencer licensing regimes; small 55+ online base |

### 1.2 Cross-cutting 2026 rules that hit every market

| Rule | Where | What it forces in the market pack |
|---|---|---|
| Instagram "AI-generated profile" label; unlabeled AI-person accounts lose reach [S39] | Global | `ai_label: true` on every IG account. Bio string localized (SAFETY_RULES §7). |
| EU AI Act Art. 50: deployers must disclose deepfake-type synthetic content from **2 Aug 2026**. Applies to non-EU deployers whose output is used in the EU. Machine-readable marking deadline for legacy systems 2 Dec 2026 [S30] | ES, IT, DE, FR, PL | Burned-in `Personaje IA` / `KI-Figur` / `Personaggio IA` / `Personnage IA` corner tag + C2PA metadata kept intact (never strip on export) + chatbot "you are talking to an AI" at first DM message. |
| France: "Image virtuelle" mention on content showing an AI face/silhouette; ban on promoting therapeutic abstention [S35] | FR | Extra on-screen tag + linter rule `FR-ABST` (block any "instead of your medication" framing; already blocked globally by SAFETY_RULES 3.1). |
| EU withdrawal button from 19 Jun 2026 (Directive 2023/2673) + German Kündigungsbutton (§312k BGB) [S28][S29] | EU (withdrawal), DE (both) | Checkout config `withdrawal_button: true` (EU), `cancel_button: true` (DE). Digital-content waiver checkbox + durable-medium confirmation email. |
| Spain: pre-renewal notice ≥15 days before charging [S31] | ES | `renewal_notice_days: 15` → mid-cycle reminder on monthly plans (counsel to confirm scope for monthly contracts). |
| Mexico: express informed consent for recurring charges, notice ≥5 days before renewal, immediate cancel [S32] | MX | `renewal_notice_days: 5`. 7-day trials must send the notice on day 2. |
| Brazil: 7-day right of regret for remote contracts, full immediate refund [S33]; AI-labelling bill PL 2338/2023 passed Senate, pending in the Chamber [S38] | BR | `refund_window_days: 7` (no-questions). Label everything now (future-proof). |
| UK DMCC Act subscription regime delayed to **spring 2027** [S34] | UK | Build the reminder + easy-exit flows now anyway (same as ROSCA flows). |
| India ASCI (Apr 2025): health/nutrition claims require qualified influencers with credentials displayed [S36] | IN | Only viable if a credentialed Indian human reviewer/presenter is shown; AI character cannot "be" the expert. |
| ManyChat TikTok automations: available everywhere **except EU and UK**; DM keyword triggers, no hyperlink buttons [S40] | EU/UK | TikTok CTA in EU/UK = "link in bio" only; comment→DM stays on IG/FB. |
| WhatsApp Business per-message rates (Jul 2026): marketing BR $0.0625, MX $0.0436, ES $0.0615, DE $0.1365, IN $0.0118; utility BR $0.0070, MX $0.0080 [S48][S49] | All | WhatsApp is for reminders and utility, not daily broadcast content (see §5.7 unit cost). |

### 1.3 Price localization (PPP) for the $12 / $15 / $20 / $25 / $30 test ladder

Method: price factor = mean(price level, Spotify ratio), capped at 1.0. Local price = USD tier × factor × FX, rounded to a local charm point. In the EU, UK, AU and MX, consumer prices must be shown **tax-inclusive**, so the net column deducts VAT/IVA. FX placeholders (Sep 2026): MXN 18.5, BRL 5.4, EUR 0.86, GBP 0.75, CAD 1.37, AUD 1.52, PLN 3.65, PHP 57, INR 85, JPY 147, KRW 1,390, SAR 3.75. **Refresh at config time.**

| Market | Factor | $12 tier | $15 tier | $20 tier | $25 tier | $30 tier | Net of VAT at $20 tier (USD) | Min-price floor note |
|---|---|---|---|---|---|---|---|---|
| US / US-Hisp | 1.00 | $12 | $15 | $20 | $25 | $30 | $20.00 (sales tax on top where applicable) | none. **The US-Hispanic price is same as the US in every mode: the blitz cells (F25/F30 or T25 → $25) while the founding cohort is open, then `{{STANDARD_PRICE}}` ($35 default); $20 only if the whole US funnel returns to `OFFER_MODE=standard`. One US price across languages (AUDIT F34).** The tier columns are the post-blitz test ladder, not a language-specific price. |
| UK | 0.94 | £8.99 | £10.99 | £13.99 | £17.99 | £20.99 | ≈$15.5 (20% VAT) | none |
| Canada | 0.92 | C$14.99 | C$18.99 | C$24.99 | C$31.99 | C$37.99 | ≈$18.2 (+GST/HST over C$30K) | none |
| Australia | 0.90 | A$16.99 | A$21.99 | A$27.99 | A$34.99 | A$41.99 | ≈$16.7 (10% GST) | none |
| Mexico | 0.50 | MX$119 | MX$149 | MX$199 | MX$249 | MX$279 | ≈$9.3 (16% IVA) | Keep ≥MX$119: fixed fees (MoR ≈5% + $0.50) eat 11%+ below it |
| Brazil | 0.42 | R$27,90 | R$34,90 | R$44,90 | R$54,90 | R$67,90 | ≈$8.3 before local taxes | Pix at 2% [S21] keeps the fee drag low |
| Spain | 0.80 | €8.99 | €9.99 | €13.99 | €16.99 | €19.99 | ≈$13.4 (21% VAT) | none |
| Italy | 0.82 | €8.99 | €10.99 | €13.99 | €16.99 | €19.99 | ≈$13.3 (22% VAT) | none |
| DACH | 0.88 | €9.99 / CHF 12.90 | €11.99 / CHF 14.90 | €14.99 / CHF 19.90 | €18.99 / CHF 24.90 | €22.99 / CHF 29.90 | ≈$14.7 (DE 19% VAT) | none |
| France | 0.87 | €9.99 | €11.99 | €14.99 | €17.99 | €21.99 | ≈$14.5 (20% VAT) | none |
| Poland | 0.52 | 22.99 zł | 27.99 zł | 37.99 zł | 46.99 zł | 56.99 zł | ≈$8.5 (23% VAT) | Push quarterly plans (BLIK is one-time) |
| LATAM ex-MX | 0.36 | $4.99 | $5.99 | $7.99 | $8.99 | $10.99 (local currency via MoR) | ≈$6.7 after IVA | **Floor $4.99**; default to quarterly |
| Philippines | 0.37 | ₱249 | ₱299 | ₱399 | ₱499 | ₱599 | ≈$6.3 (12% VAT over threshold) | Floor ₱249 |
| India | 0.20 | ₹199 | ₹249 | ₹349 | ₹449 | ₹499 | ≈$3.5 (18% GST) | MoR fixed fee = 15–27% of price → annual-only, or a local processor |
| Japan | 0.62 | ¥1,100 | ¥1,380 | ¥1,800 | ¥2,300 | ¥2,800 | ≈$11.1 (10% JCT) | none |
| Korea | 0.65 | ₩10,900 | ₩13,900 | ₩17,900 | ₩22,900 | ₩26,900 | ≈$11.7 (10% VAT) | none |
| KSA | 0.50 | SAR 22.99 | SAR 27.99 | SAR 37.99 | SAR 46.99 | SAR 55.99 | ≈$8.8 (15% VAT) | none |

**Anti-arbitrage rule:** price by **billing country** (card BIN / Pix / local method), not IP. The **gift** plan is priced in the **payer's** currency (critical for US Hispanic children paying for parents in Mexico, see §5.6).

### 1.4 Scoring model

Weights (sum to 100): **A** reachable 55+ audience (log-scaled) 20 · **B** ARPU/willingness to pay (price factor) 15 · **C** paid efficiency = localized price ÷ CPM × payment-conversion factor (log-scaled) 15 · **D** organic platform fit for 55+ (IG/FB/YT/TikTok + automation availability) 10 · **E** recurring-payment friction 10 · **F** localization effort / pack reuse 10 · **G** competition quality gap 5 · **H** regulatory burden (inverse) 15. A, B and C are computed from the §1.1 inputs and scaled to 1–5. D–H are judged 1–5 from the evidence in §1.1–1.2.

| Rank | Market | A reach | B ARPU | C paid eff. | D organic | E pay | F loc. | G comp. | H reg. | **Score /100** | Localized $20-tier price | Conv-adj. impressions per $ of month-1 ARPU |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **EN-Commonwealth** | 4.2 | 4.7 | 2.2 | 4 | 5 | 5 | 2 | 4 | **79.3** | $18.70 | 1,612 |
| 2 | **Brazil** | 4.6 | 2.1 | 5.0 | 5 | 4 | 2 | 3 | 3 | **73.9** | $8.35 | 2,699 |
| 3 | **Mexico** | 3.4 | 2.5 | 4.2 | 5 | 3 | 4 | 2 | 3 | **68.8** | $10.00 | 2,333 |
| 4 | **US Spanish** | 1.8 | 5.0 | 1.9 | 4 | 5 | 4 | 2 | 4 | **68.1** | $20.00 | 1,538 |
| 5 | Spain | 2.4 | 4.0 | 4.4 | 4 | 5 | 3 | 2 | 2 | 66.9 | $16.10 | 2,421 |
| 6 | Italy | 3.0 | 4.1 | 4.2 | 4 | 4 | 2 | 4 | 2 | 66.8 | $16.50 | 2,314 |
| 7 | LATAM ex-MX | 4.5 | 1.8 | 2.6 | 5 | 2 | 4 | 3 | 3 | 65.5 | $7.30 | 1,746 |
| 8 | France | 2.8 | 4.4 | 4.6 | 3 | 5 | 2 | 3 | 1 | 64.1 | $17.40 | 2,504 |
| 9 | Philippines | 2.8 | 1.9 | 1.9 | 5 | 3 | 4 | 3 | 4 | 61.4 | $7.40 | 1,524 |
| 10 | India | 5.0 | 1.0 | 3.4 | 4 | 3 | 3 | 1 | 2 | 60.1 | $3.90 | 2,007 |
| 11 | DACH | 2.7 | 4.4 | 3.2 | 3 | 5 | 2 | 3 | 1 | 59.6 | $17.60 | 1,956 |
| 12 | Poland/CEE | 1.0 | 2.6 | 2.1 | 4 | 4 | 2 | 4 | 2 | 47.9 | $10.30 | 1,577 |
| 13 | South Korea | 1.5 | 3.3 | 2.0 | 2 | 3 | 1 | 3 | 3 | 46.0 | $13.00 | 1,569 |
| 14 | Japan | 3.1 | 3.1 | 1.0 | 2 | 3 | 1 | 3 | 2 | 45.8 | $12.50 | 1,300 |
| 15 | MENA Arabic | 1.5 | 2.5 | 1.4 | 3 | 3 | 1 | 3 | 1 | 37.9 | $10.00 | 1,400 |

**Sensitivity (same inputs, different weights).** The top block (Commonwealth, Spanish markets, Brazil) and the bottom block (Japan, Korea, Poland, MENA) are stable under every weighting. Only the middle reorders.

| Weighting | Order |
|---|---|
| Cash-first (B 25, C 20, A 10) | Commonwealth 78 › US-Spanish 72 › Spain 71 › Italy 69 › Brazil 69 › France 69 › Mexico 66 › DACH 63 › LATAM 58 › PH 56 › IN 52 › KR 49 › PL 49 › JP 45 › MENA 38 |
| Scale-first (A 30) | Commonwealth 78 › Brazil 77 › LATAM 71 › Mexico 70 › India 66 › Italy 65 › Spain 63 › PH 62 › US-Spanish 62 › France 60 › DACH 56 › JP 46 › PL 43 › KR 43 › MENA 35 |
| Compliance-averse (H 25) | Commonwealth 78 › Brazil 73 › US-Spanish 70 › Mexico 67 › Italy 66 › Spain 66 › LATAM 63 › PH 63 › France 61 › DACH 57 › IN 56 › KR 49 › PL 49 › JP 46 › MENA 37 |

### 1.5 Why we rank by **language cluster**, not by country

Organic reach follows **language**, not borders. A Spanish reel from a Spanish-language page is served to Spanish speakers in the US, MX, CO, AR, ES and the rest of LATAM at once. One content pack, one set of pages and one ManyChat build serve the whole cluster, and checkout geo-pricing captures each country's willingness to pay.

| Language cluster | 55+ FB accts (M) | Σ revenue index* | Pages needed at launch | Checkout configs | Legal frames |
|---|---|---|---|---|---|
| **Spanish** (US-Hisp + MX + ES + LATAM) | **≈63** | **5.3** | 3 IG + 1 FB + 1 TT + 1 YT (shared) | USD, MXN, EUR, local-via-MoR | US (existing), MX, EU/ES |
| Portuguese (BR) | 31.9 | 2.3 | same set | BRL (Pix Automático + cards) | BR |
| Italian | 13.1 | 1.8 | same set | EUR | EU/IT |
| German (DE/AT/CH) | 11.1 | 1.9 | same set | EUR/CHF | EU/DE + CH |
| French (FR + BE/CH/CA-QC spill) | 12.0+ | 2.1+ | same set | EUR/CAD | EU/FR |

*Revenue index = 55+ accounts × localized $20-tier price × payment factor × 1% (illustrative only, not a forecast). Spanish cluster = US-Hisp 1.40 + MX 1.15 + ES 1.55 + LATAM 1.20.

### 1.6 Recommended rollout order and reasoning

| Order | Market | Mode | Why now | What we already beat Yang Mun on |
|---|---|---|---|---|
| 0 (config switch; any time after the US launch, live by calendar W1 at the latest) | **UK/CA/AU/IE/NZ** | Config only | Already seeing the English content. Needs geo-pricing (§1.3), VAT/GST via MoR, UK/AU/CA legal pages, emergency-number swaps (999/112/000) in the safety pack. Top score in every weighting. | Yang Mun sells in USD only on its Shopify store; we price locally. |
| 1 | **Spanish: US Hispanic + Mexico** (Spain + LATAM monetized via geo-pricing from day 1) | Mode A pilot (@changyin.espanol, 3/day) from US day 30 → full market launch = calendar day 0 (US month 4–5) → Mode B (Don Chuy & Doña Lupe, @donchuyfuerte) about day 21–28 → Doña Carmen Ruiz after Gate 2 | Biggest language cluster. The US slice has full ARPU and no new legal entity, tax regime or processor. MX adds low CPMs. Demand is proven [S16][S17]. | Yang Mun's ES is a **store translation**; the content is English. The Spanish AI-health field is dominated by misinformation profiles now under press and platform scrutiny [S16][S18]. We are native, labeled, and [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: reviewed] FALLBACK: "evidence-cited". |
| 2 | **Brazil** | Mode A about day 35 → Mode B about day 75 | Largest single-country 55+ audience (31.9M FB + 22.3M IG), lowest CPMs with real payment rails (Pix Automático recurring on Stripe [S20]), 74.5% of 60+ online and rising fastest [S6]. Scores #2 overall and #1–2 under scale weighting. | Brazil has AI-doctor health scams under CFM scrutiny [S18]. A transparent brand is differentiated. |
| 3 | **Italy** | Mode A about day 60 | Highest 55+ share of FB audience (28.6%) [S3], second-cheapest EU CPM. "Nonna" kitchen culture fits the food and recipe pillar. Reuses the **EU compliance stack** built for Spain (AI Act, GDPR Art. 27 rep, OSS, withdrawal button). | No Italian store at Yang Mun. |
| 4 | **DACH**, then **France** | Mode A about day 90+ | Highest EU ARPU, but the heaviest compliance (HWG, Abmahnung risk, Kündigungs- + Widerrufsbutton; FR "Image virtuelle" + influencer law). ARD/ZDF 2025 shows 50–69s prefer articles to video on social [S62], so pair them with a carousel/text-post format. | Yang Mun already sells DE, so demand is validated. Enter with better compliance, not first. |
| 5 (opportunistic) | **Philippines** | English pages + ₱ pricing | Already reached by English content. Cheap. Low ARPU. Just turn on PHP pricing and GCash via MoR. | n/a |
| 6 | **Poland/CEE, Japan, Korea** | Mode B only, with a local partner | Low scores. Japan/Korea need native archetypes and platform-native distribution (LINE, Kakao, YouTube). Korea could reuse Sun Yoon's heritage in a Korean-language kitchen spin-off, pending cultural review. | n/a |
| 7 | **India** | YouTube ad-rev + annual plan only | Huge reach, very low ARPU (≈$3.90 at the $20 tier), ASCI qualification rule [S36]. Only with a credentialed Indian human co-presenter. | n/a |
| Hold | **MENA Arabic** | n/a | Small 55+ online base, high Gulf CPMs, religious and gender-norm constraints on a shirtless-strength elder, influencer licensing regimes. Revisit in 2027. | n/a |

---

## 2. Localization modes

### 2.1 The architecture fact that makes cloning cheap

Our pipeline is **script → voice → lip-sync → assemble** (prompts 02–07). A new language is therefore **not a dub of a finished video**. It is a **re-render from a transcreated script** (prompts/08). Non-speaking shots (B-roll, motion clips, food inserts) are reused unchanged because text is never baked into them. Only the talking-head segments are re-lip-synced. Cost scales with *lip-synced seconds*, not video length.

"Dubbing" tools (ElevenLabs Dubbing, HeyGen Video Translate) are used only for **long-form backlog** (8–20 min YouTube videos) where re-scripting isn't worth it.

### 2.2 Mode A (same characters, native-voiced) vs Mode B (native local archetype)

| Dimension | **Mode A: Chang & Sun speak the language** | **Mode B: native archetype** (e.g., Don Chuy & Doña Lupe) |
|---|---|---|
| What it is | Same characters, same sets. Script transcreated (prompts/08), voice = the same ElevenLabs cloned timbre speaking the target language (multilingual models keep the timbre), lip-sync re-rendered, captions localized. | New character bible, faces, voices, sets and recipe context, built natively for the culture. Same pipeline, evidence library, safety engine and offer skeleton. |
| Time to first post | 5–7 days (glossary + linter + reviewer onboarding) | 3–5 weeks (character sheets, consistency tests, voice design, sets, 60-post buffer) |
| One-time cost | $1.5–3K | $6–10K |
| Wins when | (1) Testing a market fast. (2) The US character has proven equity (a clip went viral in the region; comments already arrive in that language). (3) "Foreign teacher" novelty is an asset (the Asian-elder archetype travels well; Yang Mun's global following proves it). (4) The market is small relative to effort. | (1) The market passes Gate 1 and needs to **scale past 250K followers/page**. (2) Cultural intimacy drives shares: family jokes, local foods, idioms, telenovela-style banter. (3) Native accent matters (older viewers notice non-native prosody). (4) Portfolio risk: a separate archetype diversifies away from one character's reach. |
| Loses when | Heavy idioms and humor. Food content anchored in Chinese/Korean pantry (fine as character, weak as utility). Prosody uncanny in the target language. | Before product-market fit (you pay the build cost blind). |
| Risk | Cultural-distance ceiling; "why does he speak Spanish?" (answer it openly: "Soy un personaje de IA, hoy le hablo en español"). | Stereotype risk (sombreros, "abuelita" caricature). Mitigated by native reviewer sign-off on the bible. |
| Our default | **Every market starts here.** | **Build after Gate 1 passes.** In Spanish, run both permanently: Chang & Sun (ES, @changyin.espanol) as page 1, Don Chuy & Doña Lupe as page 2, Doña Carmen Ruiz as page 3. |

### 2.3 Cost per video (45-second reel, about 20 s of lip-synced talking head, 25 s reused B-roll)

| Component | Unit price (source) | Mode A per reel | Mode B per reel | Dub-only (long-form) |
|---|---|---|---|---|
| Transcreation LLM + back-translation | ≈$0.01–0.03 | $0.02 | $0.02 | n/a |
| TTS (≈700 Spanish chars) | ElevenLabs API $0.08/1K chars on v2/v3; v4 promo $0.022 [S41] | $0.02–0.06 | $0.02–0.06 | n/a |
| Lip-sync (20 s) | InfiniteTalk $0.03–0.06/s; HeyGen API ≈$0.10/s (BRIEF) | $0.60–2.00 | $0.60–2.00 | n/a |
| New scene/character stills | Nano Banana ≈$0.07/img (BRIEF) | $0 (reuse) | $0.14–0.28 | n/a |
| New motion B-roll (only when no reusable clip) | Kling/Seedance/Veo ≈$0.03–0.40/s (BRIEF) | $0 (reuse) | $0–2.00 amortized | n/a |
| Captions/burn-in | self-hosted ffmpeg / Submagic plan | ≈$0.01 | ≈$0.01 | n/a |
| Native QA (100% for first 30 days, then 20% sample + 100% of flagged) | $15–25/hr, ≈1.5 min/reel | $0.40–0.60 → $0.10–0.15 | $0.40–0.60 → $0.10–0.15 | n/a |
| **Total per reel** | | **≈$0.75–2.70** | **≈$0.90–4.90** | n/a |
| Long-form 10-min dub | ElevenLabs Dubbing v1 $0.50/min (no lip-sync) [S41]; HeyGen translate 5 credits/min, ≈$2/min via API with lip-sync [S43]; Perso $1/min with lip-sync [S42] | n/a | n/a | **$5 (audio) to $20 (lip-synced)** per 10-min video |

**Monthly production at target volume:** 3 pages × 8 posts/day × 30 = 720 reels ≈ **$540–1,950/month (Mode A)** or **$650–3,500/month (Mode B)** before QA sampling savings.

### 2.4 Heritage handling when Chang & Sun travel

- Chang Yin (Chinese heritage) and Sun Yoon (Korean heritage) stay who they are in every language. In Spanish they are "Chang y Sun". **Never "el chino"** (a common LATAM nickname for East Asians that the linter must block in captions and replies), never "maestro" (SAFETY_RULES D-05 blocks "master" as a healing title), and never "sabio oriental" or exoticized "Oriente" framing.
- Their own heritage foods stay as character (congee, kimchi) with a one-line explanation. **Utility** recipes get local equivalents (§2.5 recipe DB).
- Korea spin-off (later): Sun Yoon leading in Korean is plausible, but it needs Korean cultural review of *her* bible first. A Korean-heritage woman married to a Chinese man is fine as fiction, but Korean audiences will judge the details (food, speech level, family terms).

### 2.5 Cultural adaptation checklist (fill per market pack; examples shown)

| Dimension | es-MX / es-US | es-ES | pt-BR | it-IT | de-DE |
|---|---|---|---|---|---|
| **Address** | Chang/Don Chuy → viewer: *usted* (default; A/B *tú*). Sun/Doña Lupe → viewer: *tú* (comadre register). Plural *ustedes*. Support/DM/checkout: *usted*. | *usted* for elders; plural *vosotros*. Castilian voice variant later. | *você*; *o senhor / a senhora* in support. | *Lei* in support; *tu* in content is acceptable for warmth. | ***Sie*** everywhere (content, DM, support). |
| **Family dynamics** | Multigenerational homes (>25% of Hispanic 50+ [S11]); grandparent childcare (26%); adult children as buyers → **gift plan**. Remittance-style "pay from US, use in MX". | Nuclear + strong *abuelos* role; *nietos*. | *Netos*, *vó/vô*; big WhatsApp family groups → "send to your mother" shares. | *Nonna/nonno*, Sunday lunch. | Independence valued; less "family guilt" framing, more autonomy/"selbstständig bleiben". |
| **Religion** | Catholic/evangelical majority; faith is #2 value [S11]. Allowed: *"Dios mediante"*, *"bendiciones"* in human-written comment replies only, sparingly. **Never** Virgin of Guadalupe imagery, prayer-as-remedy, or clergy framing. | More secular; skip religious phrases. | Catholic + evangelical; same rules as MX. | Catholic culture; neutral. | Secular; none. |
| **Humor** | Marital banter (Lupe roasting Chuy), *dichos* ("más vale paso que dure"), telenovela reactions. **No** *chancla* jokes (corporal-punishment association). | Dry irony; *refranes*. | Warm teasing, *novela* energy. | Theatrical exasperation. | Understated, self-ironic; less slapstick. |
| **Foods (utility swap)** | Blueberries → guava, papaya, jamaica (unsweetened). Salmon → canned sardines/tuna. Greek yogurt → plain yogurt/jocoque. Quinoa → **amaranto**, oats. Kale → quelites/espinaca. Beans (*frijoles de la olla*), nopal, eggs, queso fresco, corn tortilla. | Legumbres, sardinas, aceite de oliva, gazpacho, huevos. | Feijão, ovo, couve, mandioca, sardinha, banana, açaí (unsweetened). | Legumi, ricotta, sardine, olio EVO, minestrone. | Quark, Haferflocken, Linsen, Sauerkraut, Hering. |
| **Folk remedies: myth-bust list (never recommend)** | **CDS/MMS (chlorine dioxide)**, *"insulina vegetal"*, garlic-in-the-morning for BP, *bicarbonato con limón*, Vaporub-on-feet, *sábila* for diabetes, *té de guanábana* cure claims. | Same + homeopathy claims. | Chlorine dioxide, *"chá que cura"*, *"garrafada"*, *suco de batata* for gastritis [S18]. | Homeopathy/"depurativi" detox. | Schüßler-Salze and homeopathy efficacy claims, *Entgiftung* (HWG + UWG exposure). |
| **Units / formats** | kg, cm, °C, 24h in MX; US-Hisp uses lb/°F (dual-display). | metric, 24h, decimal comma. | metric, decimal comma. | metric, decimal comma. | metric, decimal comma, date DD.MM. |
| **Emergency number** (SAFETY_RULES 4.3) | 911 (US & MX) | 112 | 192 (SAMU) | 112 | 112 |
| **Text expansion vs EN** (rule of thumb) | +15–25%; ≤7 words on screen (adapter rule 7) | +15–25% | +15–30% | +10–20% | +20–35% (compound nouns: keep ≤28 chars/line) |
| **Must-avoid visual tropes** | Sombrero/charro costume, cactus-and-desert clichés, "Mexican filter" yellow tint. | Flamenco/bullfighting. | Carnival/favela clichés. | Mafia/pizza clichés. | Lederhosen as default. |

### 2.6 The market pack: new market = config, not rebuild

**Directory (one folder per locale-market; everything else is global):**

```
markets/
  _global/
    evidence/EVIDENCE.md             # E-IDs, never forked per market
    safety/SAFETY_RULES.md           # global rules; markets can only ADD rules
    pillars.yaml                     # content pillars P01–P15
    pipeline/                        # prompts 01–08, render graph, scheduler code
  es-419/                            # language pack (shared by US-Hisp, MX, LATAM)
    glossary.csv                     # term → approved translation (exercise/test names)
    claims_linter.yaml               # regex BLOCK/REWRITE in Spanish (see 5.8)
    disclosures.yaml                 # corner tag, bio, caption footer, DM opener
    hooks_bank.csv                   # 30+ tested hooks with EN gloss
    recipes.jsonl                    # localized recipe DB, reviewer + E-ID per recipe
    characters/
      chang-es/  bible.md  voice.json  refs/  sets/     # Mode A
      don-chuy/  bible.md  voice.json  refs/  sets/     # Mode B
      dona-lupe/ bible.md  voice.json  refs/  sets/
    funnels/manychat_es.json         # keyword → flow map
    support/macros_es.yaml, faq_es.md
  es-419/markets/
    us-hisp.yaml  mx.yaml  co.yaml  ar.yaml  ...   # price book, checkout, tax, legal, schedule
  es-ES/  (inherits es-419, overrides voice, glossary deltas, disclosures, legal)
  pt-BR/  it-IT/  de-DE/ ...
```

**market.yaml (example: `es-419/markets/mx.yaml`)**

```yaml
market: MX
locale: es-MX
language_pack: es-419
characters: [chang-es, sun-es, don-chuy, dona-lupe]
pages:
  - {platform: instagram, handle: "@donchuyfuerte", characters: [don-chuy, dona-lupe], ai_label: true, posts_per_day: 8}
  - {platform: instagram, handle: "@changyin.espanol", characters: [chang-es, sun-es], ai_label: true, posts_per_day: 3}   # Mode A pilot since US day 30
  - {platform: facebook,  handle: "Don Chuy y Doña Lupe", posts_per_day: 6}
  - {platform: tiktok,    handle: "@donchuyfuerte", ai_toggle: every_post, dm_keywords: true, comment_triggers: false}
  - {platform: youtube,   handle: "@DonChuyFuerte", synthetic_flag: true, shorts_per_day: 3}
register: {viewer_default: usted, lupe_to_viewer: tu, support: usted}
disclosures: {corner_tag: "Personaje IA", caption_footer: es_footer_v1, dm_opener: es_dm_ai_v1}
emergency_number: "911"
cta_keywords: [FUERZA, SILLA, CAMINA, DESAYUNO, EQUILIBRIO, RODILLA, CALMA, AGUA, SAL, MEMBRESIA, MAMA]
pricing:
  currency: MXN
  tiers: [119, 149, 199, 249, 279]      # split-test arms mirror USD 12/15/20/25/30
  default_arm: 149
  quarterly_prepaid: 449                 # OXXO-eligible (one-time)
  annual: 1490
  trial: {days: 7, price: 19}
  gift_plan: {payer_currency: auto, months: [3, 6, 12]}
checkout:
  processor: stripe_managed_payments     # MoR; switch to direct Stripe MX entity > MX$550K MRR
  methods_recurring: [card, apple_pay, google_pay]
  methods_one_time: [oxxo, spei]
tax: {regime: MX_IVA_digital, rate: 0.16, handled_by: mor}
legal:
  renewal_notice_days: 5
  cancel: {online: true, max_screens: 2, save_offers: 1, finish_button_equal_prominence: true, immediate: true}
  withdrawal_button: false
  refund_policy_days: 14                 # voluntary, > legal minimum
  privacy: MX_LFPDPPP_2025
support: {language: es, hours_local: "08:00-20:00", sla_first_response_h: 4, ai_first: true}
schedule:
  tz: America/Mexico_City
  slots_local: ["06:45","08:30","11:00","13:30","16:00","19:15","20:45","22:00"]
qa:
  linguistic_reviewer: {pool: upwork_mx, sample_rate_after_d30: 0.2}
  clinical_reviewer: {role: "Nutrióloga (cédula) + Fisioterapeuta (cédula)", sla_h: 24}
kpis_profile: spanish_v1                 # gates in §4.2
```

**Module parameterization:** what stays global, what the pack sets, and what automated check enforces it.

| Module | Global (never forked) | Market-pack parameters | Automated check before render/publish |
|---|---|---|---|
| Ideation (01) | Pillars, evidence IDs, winner library | Local trend feed (comments in the language), holiday calendar (e.g., Día de las Madres 10 May MX, Día do Avô BR 26 Jul) | Idea must map to an E-ID |
| Script (02) + Transcreation (08) | Schema, claim frames | Register, glossary, idiom list, local foods, humor notes | Syllable delta ≤ ±12% per line; back-translation diff reviewed |
| Compliance judge (03) | SAFETY_RULES global | `claims_linter.yaml` (language regex), market legal add-ons (FR "Image virtuelle", DE HWG phrases) | BLOCK on any match; REQUIRE footer/tag |
| Shot plan / render (04–07) | Motion library, B-roll bank | Character refs, sets, voice IDs, corner-tag text | Face-consistency score ≥ threshold; form QC (M-08) |
| Captions (06) | Style (high contrast, no gray) | Line length, hashtags (#saludables #adultosmayores #fuerza), emergency number | ≤7 words on screen; hashtag denylist |
| Distribution | Scheduler, dedupe across pages | TZ + slots, page handles, platform toggles (AI label) | Uniqueness hash per page; label on |
| Funnel | ManyChat flow templates | Keywords (ASCII only), DM copy, lead magnet file | Keyword collision check across pages |
| Offer | Offer architecture (tripwire → trial → MRR, gift) | Price book, trial terms, value-stack names | Price displayed = tax-inclusive where required |
| Checkout | Stripe Billing / MoR integration | Methods, currency, renewal notice days, cancel/withdrawal buttons | Legal-config unit tests (notice timers fire; cancel ≤2 screens: one save offer next to an equally prominent "Finish canceling" button) |
| Support | Help-desk + AI agent | Language, macros, hours, escalation contacts, crisis lines | Crisis keyword routing test |
| Analytics | Event schema | Market tag, currency normalization | Daily KPI job per market vs gates |

**"New market in a week" checklist (Mode A):**

| Day | Task | Owner | Time |
|---|---|---|---|
| 1 | Copy pack from nearest language; set `market.yaml`; FX + price book; legal config | Ops | 3 h |
| 1 | Hire linguistic reviewer + clinical reviewer (contracts, NDA, credentials verified) | Ops | 4 h |
| 2 | Build glossary (first 300 terms) with Opus + reviewer; translate disclosures; claims linter regex | Reviewer + LLM | 6 h |
| 2–3 | Transcreate the top-60 US winners (08 adapter); reviewer approves | Pipeline + reviewer | 8 h |
| 3 | Voice: test the multilingual clone on 10 lines; set stability/style; check prosody with a native speaker | Ops + reviewer | 2 h |
| 4 | Render 60-post buffer; form QC; caption QC | Pipeline | automated |
| 4 | ManyChat flows localized; lead magnet translated and designed (large type, no gray text) | Ops | 4 h |
| 5 | Checkout live (MoR); privacy policy, terms, cancel flow, renewal notices in language; support macros | Ops + counsel | 6 h |
| 6 | Accounts created and warmed; IG AI label on; bios with disclosures | Ops | 2 h |
| 7 | Go live on the warm-up ramp (PIPELINE.md §5.4: 1–2 posts/day week 1, 3 week 2, 5–6 week 3, then 6–9; a pilot page stays at 3/day); paid test $80–100/day only from the market launch | Media buyer | n/a |

---

## 3. Operating model

### 3.1 People per market

| Role | Mode A load | Mode B load | Where to hire | Rate (2026) | Monthly cost |
|---|---|---|---|---|---|
| Native linguistic + cultural reviewer | 10–15 h/wk (drops after day 30 with 20% sampling) | 15–20 h/wk | Upwork, Workana (LATAM), ProZ; prefer 50+ native speakers (they catch prosody an older viewer hears) | $10–32/h on Upwork for Spanish proofreaders [S44] | $600–1,800 |
| Credentialed clinical reviewer (RD/nutritionist + PT) in the language | 4–6 h/wk | 6–8 h/wk | MX: *nutrióloga/fisioterapeuta con cédula profesional* (verify on the SEP registry); US-Hisp: bilingual RD; BR: CRN/CREFITO registrants; EU: registered dietitian/physio | $20–60/h (Upwork dietitians [S45]) | $500–1,900 |
| Community + support agent (human escalations) | 15–20 h/wk | 20–30 h/wk | Colombia/Mexico BPO or freelancers | Bilingual EN/ES agents $10–16/h CO, $10–15/h MX vs $35–48 onshore [S46] | $650–1,900 |
| AI support agent | 24/7 first line | same | Intercom Fin or equivalent | "from $0.99 per Fin outcome" + $29–85/seat [S47] | $100–400 |
| Local counsel (one-time + retainer) | set-up | set-up | MX consumer/data; ES/EU consumer + AI Act; BR CDC/LGPD; DE HWG/UWG specialist | one-time $1–5K per jurisdiction cluster | $0–300 retainer |

**Rule:** the "reviewed by licensed professionals" line in the target language may run only once a named, credentialed reviewer **for that market** is under contract (SAFETY_RULES §7). US reviewers do not cover MX or BR claims.

### 3.2 In-language customer support

| Layer | Spec |
|---|---|
| Channels | Email + web chat (primary), IG/FB DM (ManyChat hands off to human on keywords `CANCELAR`, `REEMBOLSO`, `COBRO`, `AYUDA`, `HUMANO`), WhatsApp for utility only (receipts, renewal notices, password links) |
| AI first line | Trained on FAQ, cancel, refund and billing policies, and access issues. Must say it is an AI at first message (EU AI Act Art. 50 chatbots [S30]). **Never** gives health advice beyond linking the evidence-reviewed library and "consulte a su médico". |
| Human escalation | All billing disputes, refund exceptions, crisis keywords (SAFETY_RULES 4.4, localized lines: MX Línea de la Vida 800 911 2000; ES 024; BR CVV 188; US 988), and anything the AI isn't confident on. |
| SLA | First response ≤4 h in local business hours; cancellations processed instantly and self-serve (never gated behind chat). |
| Target | ≤8 tickets per 100 members per month; AI resolution ≥60% by day 60. |

### 3.3 Payment processing

| Stage | Setup | Why |
|---|---|---|
| Launch (every non-US market) | **Merchant of Record**: Stripe Managed Payments (MoR for digital products, handles VAT/GST in 80+ countries; subscriptions through Checkout/Payment Links only; no Connect) [S23]. Alternatives: Paddle / Lemon Squeezy 5% + $0.50, Creem 3.9% + $0.40, Whop 3% + processing [S24]. | Zero tax registrations on day 1. The MoR registers and remits. |
| Local methods | BR: **Pix** (2% [S21]) incl. **Pix Automático** mandates for subscriptions (3-day pre-debit notice by the bank; default mandate cap 400 BRL; IOF handling configurable) [S19][S20]. MX: cards recurring; **OXXO one-time only** (no recurring, no refunds) [S22] → sell OXXO-eligible **prepaid quarterly/annual**. EU: SEPA DD 0.8% + 30¢ capped $6; PL: BLIK 1.9% + 30¢; IN: UPI 2% [S21]. | Recurring-capable methods decide churn. Card-only in LATAM loses buyers. |
| Scale (a market > ≈$30K MRR) | Direct Stripe account + Stripe Tax, or a local entity for MX/BR if payment acceptance or MoR fees justify it | Recover the 2–4 pt MoR premium |
| Fixed-fee floor | At MoR 5% + $0.50: a $5 price loses 15%, a $2.30 price 27% | Hence the price floors in §1.3 and annual-only in India |

**Verify before launch:** which local methods Stripe Managed Payments supports per country. If Pix/OXXO aren't available under MoR, run BR/MX on direct Stripe + Stripe Tax and register for BR/MX indirect tax (both require registration from the first B2C sale [S25][S26]).

### 3.4 Tax (B2C digital services)

| Jurisdiction | Rule for a non-resident seller | Handling |
|---|---|---|
| EU (ES, IT, DE, FR, PL…) | VAT from the **first** sale; one registration via **non-Union OSS** covers all 27 states [S25] | MoR at launch; OSS registration if going direct. Also appoint a GDPR Art. 27 EU representative. |
| UK | VAT from the first sale [S25] | MoR |
| Mexico | 16% IVA, register within 30 days of first supply; SAT real-time data access from 1 Apr 2026 [S26] | MoR |
| Brazil | Registration from the first B2C sale [S25]; customers pay IOF 3.5% on cross-border payments since May 2025 [S27] | MoR; show IOF note at checkout for Pix/card |
| Canada | GST/HST above CAD 30K; QST separately [S25] | MoR |
| Australia | GST above AUD 75K [S25] | MoR |
| India | GST 18% from first sale [S25] | MoR or skip |
| Japan / Korea | JCT above ¥10M; KR from first sale [S25] | MoR |

### 3.5 Posting time zones (older audiences skew early morning, lunch and 7–10 pm local)

| Market | TZ | 8 local slots | Same slots in UTC |
|---|---|---|---|
| US-Hisp (anchor Central) | America/Chicago (UTC−5 CDT / −6 CST) | 06:45, 08:30, 11:00, 13:30, 16:00, 19:15, 20:45, 22:00 | 11:45…03:00 (+1) CDT |
| Mexico | America/Mexico_City (UTC−6, no DST since 2022) | same | 12:45, 14:30, 17:00, 19:30, 22:00, 01:15, 02:45, 04:00 |
| Colombia/Peru | UTC−5 | same | 11:45…03:00 |
| Argentina/Brazil | UTC−3 | same | 09:45…01:00 |
| Spain/Italy/DE/FR | Europe/Madrid etc. (UTC+2 summer / +1 winter) | same | 04:45…20:00 (summer) |
| Philippines | UTC+8 | same | 22:45 (−1)…14:00 |

A single Spanish page serves US + MX + LATAM, so **alternate slots between CT-anchored and ART/BRT-anchored**. For the Spain page (when split), post on Madrid time. The scheduler reads `schedule.tz` from the pack and handles DST.

### 3.6 Unit economics per market (EST; the US model lives in economics.xlsx)

| Line | Mode A market (monthly) | Mode B market (monthly) |
|---|---|---|
| Production (720 reels) | $540–1,950 | $650–3,500 |
| Linguistic + clinical QA | $1,100–3,700 | $1,500–3,700 |
| Support (human + AI) | $750–2,300 | $900–2,500 |
| Tools delta (ManyChat seats, help desk) | $150–300 | $150–300 |
| **Run-rate (ex paid ads)** | **≈$3.5–6K** | **≈$5–9K** |
| Break-even paying members at net ARPU | US-Hisp ($18 net) ≈200–330 · MX ($9.3) ≈380–650 · BR ($8.3) ≈420–720 · ES ($13.4) ≈260–450 | ×1.4–1.5 of Mode A |

---

## 4. 90-day expansion calendar (day 0 = the Spanish market launch date, month 4–5 of the US business)

**Day 0 is not parallel with the US launch.** It is the Spanish market launch date (paid, localized pricing, checkout), in month 4–5 of the US business. Every "dN" below counts from it.

**Before day 0:** the Mode A Spanish pilot page @changyin.espanol has run since US day 30 at 3 posts/day (organic only; no Spanish paid media or Spanish checkout). ES Gate 1 (§4.2, organic metrics) is read on the pilot 14 days after it goes live. While the pilot runs: pack es-419 v0 (glossary, linter, disclosures, hooks bank), hire the MX linguistic reviewer + nutrióloga/fisio, transcreate the top-60 US winners, and (once Gate 1 passes) start the Don Chuy & Doña Lupe build (3–5 weeks) so Mode B can go live about 3–4 weeks after day 0.

**Day-0 trigger (all must be true):** the US day-10 gate (trial→paid) has passed; US ≥$25K MRR; one page ≥250K followers; pipeline sustaining ≥6 posts/day/page with ≤2% QA reject; month-1 renewal ≥55%; cancel/renewal compliance flows audited; zero open P0 safety incidents.

### 4.1 Calendar

| Week | Commonwealth | Spanish (US-Hisp + MX → ES/LATAM) | Brazil | Italy / DACH / FR | Gate |
|---|---|---|---|---|---|
| W1 (d1–7) | Geo-pricing GBP/CAD/AUD/NZD/EUR-IE live via MoR; UK/AU/CA legal pages; emergency numbers | **Spanish market launch (d0):** *Años Fuertes* live with localized pricing and checkout (USD/MXN/EUR); ManyChat ES; @changyin.espanol adds FB page, TikTok, YT Shorts; $100/day US-Hisp + $80/day MX paid test; pack es-419 v1 from pilot learnings | n/a | n/a | n/a |
| W2 (d8–14) | Monitor conversion by country | Monitor paid conversion (US-Hisp vs MX); Don Chuy & Doña Lupe: consistency tests, voice design, sets (build started before d0) | Pack pt-BR v0 start | n/a | n/a |
| W3 (d15–21) | n/a | ES Gate 1 re-read on paid traffic (d14). Don Chuy & Doña Lupe: 60-post buffer rendered and QA'd; recipe DB localization (first 150) | Hire BR reviewer + nutricionista (CRN) + fisio (CREFITO) | n/a | n/a |
| W4 (d22–28) | n/a | **Mode B live (about 3–4 weeks after d0):** @donchuyfuerte (IG/TT/YT) on the warm-up ramp (PIPELINE.md §5.4) up to 8/day; gift plan "Regálale fuerza a tu mamá" | Transcreate top-60; Pix Automático test | n/a | n/a |
| W5–6 (d29–42) | n/a | Spain geo-pricing + EU compliance stack (Art. 27 rep, withdrawal button, 15-day notice, AI Act tags); LATAM floor prices | **Mode A live** (Chang & Sun em português); R$ price test | EU stack reused → Italy pack v0 | **ES Gate 2 (d30)** |
| W7–8 (d43–56) | n/a | Scale winners; second Mode B page (Option 2 "Doña Carmen Ruiz", women 50+, ARCHETYPES.md #1) if Gate 2 passes | **BR Gate 1 (d49)**. Native archetype design (bible + native reviewer sign-off) | Italy reviewer hired; transcreation | n/a |
| W9–10 (d57–70) | Evaluate splitting a UK page (British voice) | ES-ES voice variant if Spain ≥20% of ES revenue | **BR Gate 2 (d65)**. Scale paid if CAC gate passes | **Italy Mode A live (d60)** | **ES Gate 3 (d60)** |
| W11–12 (d71–84) | n/a | Long-form YT in Spanish (dub-only backlog) | **Mode B live** | DACH: HWG counsel review of the claims linter, cancel + withdrawal buttons, PayPal/SEPA | **IT Gate 1 (d74)** |
| W13 (d85–90) | n/a | Quarterly review: scale / hold / kill per page | n/a | Go/no-go on DACH Mode A launch (d91–97) and France (d120+) | Portfolio review |

### 4.2 Go / no-go KPIs per market

Baselines are relative to the US pages **at the same age since launch** (normalizes for account warm-up).

| Gate | Metric | **GO** (scale) | **ITERATE** (fix, re-test 14 days) | **KILL / HOLD** |
|---|---|---|---|---|
| **Gate 1 (d14 after live)** | Median views/reel vs US at same age | ≥50% | 25–50% | <25% after 60 posts and 3 hook iterations |
| | Keyword comments per 1K views | ≥5 | 2–5 | <2 |
| | DM → lead-magnet opt-in | ≥35% | 20–35% | <20% |
| | Reviewer QA pass rate | ≥95% | 90–95% | <90% (pause pipeline) |
| **Gate 2 (d30 after live)** | Lead → trial/tripwire | ≥8% | 4–8% | <4% |
| | Trial → paid | ≥35% (benchmark H&F ≈42%, BRIEF) | 25–35% | <25% |
| | Paying members | US-Hisp ≥250 · MX ≥400 · BR ≥400 · IT ≥200 | 50–99% of target | <50% |
| | Paid CAC vs 3-month gross profit per member | ≤1.0× | 1.0–1.5× | >1.5× (organic-only) |
| | Payment failure rate (first charge) | ≤12% | 12–25% | >25% (fix methods before scaling) |
| **Gate 3 (d60 after live)** | Market MRR (USD) | Spanish cluster ≥$15K · BR ≥$6K · IT ≥$5K | 50–99% | <50% → hold at Mode A maintenance (≤3 posts/day) |
| | Month-1 renewal | ≥55% | 45–55% | <45% |
| | Refunds / chargebacks | ≤5% / ≤0.6% | ≤8% / ≤0.9% | above → stop paid, audit disclosures |
| | Support tickets per 100 members/mo | ≤8 | 8–12 | >12 |
| | Compliance incidents (platform strikes, regulator/press complaints upheld) | 0 | 1 minor, fixed within 48 h | any P0 → pause market |
| **Gate 4 (d90 after live)** | Contribution margin after run-rate + ads | ≥25% | 0–25% | negative two months running |

---

## 5. Launch kit: Spanish (US Hispanic + Mexico core)

### 5.1 Positioning in one line
**"Fuerza después de los 60, explicada con cariño y sin mentiras."** (Strength after 60, explained with warmth and without lies.) Openly AI characters, recipes from your own kitchen, a routine you can do with a chair, and [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: a team of real professionals checking every word.] FALLBACK: "every word built on published research and guidelines for older adults."

**Why this beats the Spanish field:** the 50 AI health profiles documented in July 2026 sell "what your grandmother knew but the pharmacy won't tell you" and "70 years of natural remedies" [S16]. Paco del Campo reached 1M+ followers in two weeks selling €5–13 remedy books, with his AI nature buried in site fine print [S17]. We invert every trust signal: labeled, [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: reviewed,] FALLBACK: "(no review claim)" evidence-cited, and no cures.

### 5.2 Launch sequencing
1. **Page 1 (pilot from US day 30, before the market launch): "Chang y Sun"** in Spanish on **@changyin.espanol** (Mode A, 3 posts/day, organic). Tests demand using proven characters; it gets paid media, localized pricing and checkout at the Spanish market launch (d0, US month 4–5).
2. **Page 2 (d21–28, about 3–4 weeks after the Spanish market launch): Option 1, Don Chuy & Doña Lupe** (@donchuyfuerte; primary native archetype, mirrors the US duo's dynamic).
3. **Page 3 (d45+ if Gate 2 passes): Option 2, Doña Carmen Ruiz** (female-led; women 50–75 are the core buyers; bible = ARCHETYPES.md #1).

### 5.3 Archetype Option 1: **Don Chuy y Doña Lupe** (primary)

| Field | Don Chuy (Jesús Arriaga, 74, AI character) | Doña Lupe (Guadalupe Arriaga, 72, AI character) |
|---|---|---|
| Role | The living proof that strength is trainable at any age. Demonstrates; explains mechanisms simply. | The blunt truth-teller. Asks the audience's questions, roasts his excuses, protects safety ("¡junto a la pared!"). |
| Look (image-gen spec) | Mexican man, 74. Broad shoulders, visibly strong forearms and deltoids, lean but muscular, not bodybuilder-shiny. Weathered tan skin, deep smile lines, thick white mustache, short white hair. Plain cotton t-shirts (white, olive, navy), a work shirt on cool days, jeans or work pants, leather huaraches or sneakers. Reading glasses in the shirt pocket. **No sombrero, no charro costume.** | Mexican woman, 72. Soft build, straight posture, silver hair in a low bun, small gold earrings, reading glasses on a beaded chain, floral apron over a solid blouse, cardigan. Expressive eyebrows (the eye-roll is a signature beat). |
| Sets | (1) Patio with bougainvillea, terracotta floor, a sturdy wooden chair against a wall. (2) Homemade gym corner: sandbag (*costal*), two buckets with handles, a door-frame pull-up bar, a towel. (3) Neighborhood walk: sidewalk, *tiendita*, plaza with kiosk (evening). (4) *Tianguis* produce stall (B-roll). | (1) Kitchen: talavera tiles, *comal*, *olla de barro*, wooden spoons, plants on the windowsill. (2) Dining table with plastic floral tablecloth, *cafecito*, notebook of recipes. |
| Voice (ElevenLabs Voice Design prompt) | "Mexican man, 74, warm deep baritone with slight gravel, unhurried northern-Mexico cadence but neutral enough for all Latin America, laughs from the chest, speaks slowly and clearly for older listeners." Target 135–145 wpm. | "Mexican woman, 72, bright mid-pitch, quick central-Mexico cadence, dry sarcasm, affectionate scolding, clicks her tongue before a punchline." Target 150–160 wpm. |
| Register | *usted* to viewers (A/B *tú*); calls Lupe "mi reina", "vieja" (affectionate, test it) | *tú* to viewers (comadre voice); calls him "Jesús" when scolding, "Chuy" when sweet |
| Catchphrases | "Despacio, pero diario." · "La fuerza se entrena, no se hereda." · "Con la pared cerca, siempre." | "Eso dice él. Ahora te digo yo." · "No presumas, Jesús." · "Pregúntale a tu doctor, que no muerde." |
| Niche / pillars | Chair strength, carries (*las bolsas del mandado*), balance, walking after meals, knees and back (exercise-first), breath for nerves, sleep | Protein-smart Mexican cooking on a budget, low-salt seasoning, hydration, myth-busting *remedios de la comadre*, family and loneliness (Q&A sticker format) |
| Fictional lore (colors stories, **never evidence**, D-06) | Former bricklayer, likes *danzón*, grows chiles | Ran the family *fonda*, keeps a recipe notebook, watches *novelas* |
| Disclosure moments | Pinned post #1: "Somos personajes de IA." Winking lines ≥1 in 20 posts (D-08): Lupe: "Es de inteligencia artificial y aun así no se estira." | same |

### 5.4 Archetype Option 2: **Doña Carmen Ruiz** (female-led, women 50–75; bible = ARCHETYPES.md #1)

| Field | Doña Carmen (Carmen Ruiz, 72, AI character) |
|---|---|
| Strategic role | Speaks directly to the buyer: women 55–75 worried about bones, weight after menopause, knees, loneliness, and caring for everyone except themselves. Bridges to a future women's track (synergy with the Unignorable perimenopause funnel) without making hormone claims. |
| Fictional lore (colors stories, **never evidence**, D-06) | Retired elementary-school teacher from Puebla, living in San Antonio for 35 years. A widow who remarried at 65 (running storyline with Don Álvaro, 75, a retired mariachi trumpeter who "only trains his lungs"). Five grandkids (off camera). Frank Delgado is her cousin (network crossover with the Chang & Sun world). |
| Look | Mexican woman, 72, 158 cm, sturdy and strong: visibly strong arms and shoulders (defined, not extreme). Silver hair in a low bun with a tortoiseshell comb, brown skin with natural texture and laugh lines, small gold hoops, reading glasses on her head. Cardigans in terracotta and teal; sneakers for training; an apron with embroidered flowers in the kitchen. Carries a bucket of sand (*cubeta con arena*) as her "kettlebell". **No rebozo-as-costume, no sombreros, no "spicy abuela" caricature.** |
| Sets | Backyard with a lemon tree and a concrete patio (her gym). Kitchen with a *comal* and a clay bean pot. Front porch steps. The neighborhood park walking track (evening walks with neighbors: non-speaking extras, never presented as members). Living room with a photo wall. |
| Voice | "Mexican woman, 72, low-mid warm alto, warm-authoritative retired-schoolteacher tone, confident and funny, fast when joking, slow when teaching, a grandmother who lifts." 140 wpm. |
| Register | *usted*, with "mija/mijo" said affectionately |
| Catchphrases | "Las piernas no se jubilan." · "Con permiso, pero no." · "Primero la proteína, luego el pan dulce." · "Aquí nadie se sienta después de comer." · "Primero usted, luego el mundo." · "Sus huesos escuchan lo que carga." · "Aquí nadie se rinde, se descansa." |
| Pillars | Strength for bones (resistance + balance, E29 framed as "supervised" for impact), chair and floor-rise practice (E45), protein at every meal (E28), fiber (E24), post-meal walks (E23), pelvic-floor basics (E31), social connection (E37), sleep. Mexican home cooking re-balanced for protein and fiber (frijoles de olla, huevos a la mexicana, caldo de pollo, nopales). |
| Guardrails | No menopause/hormone claims (blocked terms need an E-ID); no weight-loss promises; osteoporosis contraindications (4.2) auto-inserted; no diabetes "reversal" language; immigration topics are never content |
| When to launch | After Gate 2 on the Spanish cluster (about d45+ after the Spanish market launch), as page 3 following Don Chuy & Doña Lupe. Or as page 2 if Don Chuy tests poorly with women 55–75 in the first 30 days. |

### 5.5 Thirty hooks (Spanish, with English gloss)
Speaker: C = Don Chuy, L = Doña Lupe, DC = Doña Carmen, CS = Chang/Sun (Mode A). Keywords are ASCII-only for automation.

| # | Hook (ES) | English gloss | Speaker | Pillar | CTA keyword | E-ID |
|---|---|---|---|---|---|---|
| 1 | "Si no se puede levantar de esta silla sin usar las manos, quédese." | If you can't get up from this chair without your hands, stay. | C | Chair test | SILLA | E11 |
| 2 | "La prueba de la silla: 30 segundos. ¿Cuántas hace usted?" | The chair test: 30 seconds. How many can you do? | C | Chair test | SILLA | E11 |
| 3 | "Terminaste de comer y te vas directo al sillón. Por eso." | You finish eating and go straight to the couch. That's why. | L | Post-meal walk | CAMINA | E23 |
| 4 | "Haga esto mientras se lava los dientes y sus piernas se lo agradecen." | Do this while brushing your teeth; your legs will thank you. | C | Balance | EQUILIBRIO | E09 |
| 5 | "Mire cómo cargo el mandado. Esto también es ejercicio." | Look how I carry the groceries. This is exercise too. | C | Grip/carries | FUERZA | E07 |
| 6 | "¿Pan dulce y café de desayuno? Su músculo se queda con hambre." | Sweet bread and coffee for breakfast? Your muscle stays hungry. | C | Protein | DESAYUNO | E28 |
| 7 | "Jesús, me duelen las rodillas en la escalera. ¿Mejor ya no subo?" | Jesús, my knees hurt on the stairs. Should I stop climbing? | L→C | Knees | RODILLA | E15 + OARSI [S55] |
| 8 | "Cuando me entran los nervios, él me dice que respire así. Y funciona." | When I get nervous, he tells me to breathe like this. And it works. | L | Breath | CALMA | E19 |
| 9 | "¿Sabía que después de los 60 la sed avisa tarde?" | Did you know that after 60, thirst warns you late? | C | Hydration | AGUA | new E-ID [S57] |
| 10 | "Mi comadre dice que el ajo en ayunas le baja la presión. Jesús, dile la verdad." | My friend says garlic on an empty stomach lowers her blood pressure. Jesús, tell her the truth. | L | Myth-bust | SAL | E20, E35 |
| 11 | "No soy doctor. Ni siquiera soy una persona de verdad." | I'm not a doctor. I'm not even a real person. | C | Transparency | MEMBRESIA | n/a |
| 12 | "Doña Lupe tiene algo que decirte y no te va a gustar." | Doña Lupe has something to tell you and you won't like it. | L | Varies | varies | varies |
| 13 | "¿A tu mamá ya no le gusta salir a caminar? Mándale este video." | Your mom doesn't want to go walking anymore? Send her this video. | L | Gift/share | MAMA | E22 |
| 14 | "Con la edad, la fuerza se va más rápido que el músculo. Mire." | With age, strength leaves faster than muscle. Watch. | C | Why strength | FUERZA | E04 |
| 15 | "Tres ejercicios con una silla. Ni gimnasio, ni pesas." | Three exercises with a chair. No gym, no weights. | C | Chair routine | SILLA | E01 |
| 16 | "¿Es tarde para empezar a los 70? Le contesto con datos." | Is 70 too late to start? I'll answer with data. | C | Never too late | FUERZA | E03 |
| 17 | "Lo que desayuno en un día normal (y no es caro)." | What I eat for breakfast on a normal day (and it's not expensive). | C/L | Protein | DESAYUNO | E28 |
| 18 | "Frijoles de la olla: barato, con fibra y con proteína. Así los hace Lupe." | Pot beans: cheap, with fiber and protein. This is how Lupe makes them. | L | Fiber | RECETA | E24 |
| 19 | "Guarde este video para cuando le duela la espalda de estar sentado." | Save this video for when your back hurts from sitting. | C | Back | ESPALDA | E30 |
| 20 | "Si le da miedo caerse, empiece por aquí." | If you're afraid of falling, start here. | C | Falls | EQUILIBRIO | E12, E13 |
| 21 | "¿Se puede levantar del piso sin ayuda? Practíquelo antes de necesitarlo." | Can you get up from the floor unaided? Practice before you need it. | C | Floor rise | PISO | E45 |
| 22 | "El consomé en polvo es la sal escondida de tu cocina." | Bouillon powder is the hidden salt in your kitchen. | L | Low-salt cooking | SAL | E35 (+ caution) |
| 23 | "¿Quieres regalarle a tu mamá algo que sí va a usar? Veinte minutos de fuerza al día." | Want to give your mom something she'll actually use? Twenty minutes of strength a day. | L | Gift | MAMA | n/a (S-03/S-04: no guilt; gift terms shown) |
| 24 | "Chuy presume que carga el garrafón. Yo presumo que no se ha lastimado." | Chuy brags that he carries the water jug. I brag that he hasn't hurt himself. | L | Safe progression | FUERZA | E02 |
| 25 | "Sus huesos escuchan lo que carga." | Your bones listen to what you carry. | DC | Bones | HUESOS | E29 (supervised) |
| 26 | "Mija, primero usted. Cinco minutos, aquí en el patio." | Honey, you first. Five minutes, here on the patio. | DC | Self-care strength | FUERZA | E01 |
| 27 | "Esto le pasa a sus piernas después de 10 días en cama." | This is what happens to your legs after 10 days in bed. | C | Disuse | FUERZA | E05 |
| 28 | "La fuerza de sus manos dice mucho de su salud." | The strength of your hands says a lot about your health. | C | Grip | FUERZA | E07 |
| 29 | "Doña Lupe responde: '¿Por qué me canso tanto?'" | Doña Lupe answers: "Why am I so tired?" | L | Q&A sticker | CANSANCIO | E43 (screening), E22 |
| 30 | "Chang y Sun ahora hablan español. Y siguen sin venderte milagros." | Chang and Sun now speak Spanish. And they still don't sell you miracles. | CS | Mode A launch | MEMBRESIA | n/a |

### 5.6 Ten short scripts (Spanish; about 35–45 s each)

Every script ends with the ES caption footer from SAFETY_RULES §7 and the movement add-on where relevant. Every movement shows a wall/chair setup (M-08). Corner tag `Personaje IA` is always on screen. Timings are approximate.

**Script 1: "La prueba de la silla"** (E11) · Keyword SILLA
- [0–3s | Patio, silla contra la pared] **DON CHUY:** Si no se puede levantar de esta silla sin usar las manos… quédese.
- [3–12s] **DON CHUY:** Siéntese derechito, brazos cruzados en el pecho. Párese completo y vuelva a sentarse. Cuente cuántas hace en 30 segundos. · TEXTO: *Prueba de 30 segundos*
- [12–22s | Inserto tabla] **DON CHUY:** Hombres de 70 a 74: menos de 12 es señal de que las piernas necesitan trabajo. Mujeres de esa edad: menos de 10. · TEXTO: *Referencia: CDC (EE. UU.)*
- [22–28s | Inserto cocina] **DOÑA LUPE:** Y con la silla pegada a la pared, que no quiero verte en el piso.
- [28–36s] **DON CHUY:** La buena noticia: la fuerza de piernas se entrena a cualquier edad. Despacio, pero diario.
- [36–42s] **DON CHUY:** Comente SILLA y le mando la rutina de 7 días para subir su número.
- *EN gloss:* Chair-stand test with CDC below-average cut-offs; strength is trainable; CTA for 7-day routine.

**Script 2: "Diez minutos después de comer"** (E23) · Keyword CAMINA
- [0–3s | Mesa, platos vacíos] **DOÑA LUPE:** Terminaste de comer y te vas directo al sillón. Por eso.
- [3–5s] **DON CHUY:** ¿Por eso qué, Lupe?
- [5–15s] **DOÑA LUPE:** Después de comer, el azúcar en la sangre sube. Es normal. Pero caminar un ratito ayuda a que tus músculos usen parte de esa azúcar.
- [15–25s | Caminando en la cuadra] **DON CHUY:** Aunque sean unos minutos. A paso de plática. En el patio, en el pasillo, alrededor de la cuadra. · TEXTO: *Camina después de comer*
- [25–33s] **DOÑA LUPE:** Y si tomas medicina para la diabetes, no la cambies por esto. Esto se suma, no la sustituye.
- [33–40s] **DON CHUY:** Comente CAMINA y le mando el plan de caminatas de 7 días.
- *EN gloss:* Post-meal glucose rises normally; light walking after meals lowers the rise (meta-analysis); never replaces medication.

**Script 3: "El desayuno que cuida su músculo"** (E28) · Keyword DESAYUNO
- [0–3s | Pan dulce en la mesa] **DON CHUY:** ¿Pan dulce y café de desayuno? Su músculo se queda con hambre.
- [3–13s] **DON CHUY:** Después de los 65, los expertos recomiendan más proteína que a los jóvenes: más o menos un gramo por cada kilo de su peso, al día. · TEXTO: *1 a 1.2 g por kilo al día*
- [13–24s | Inserto plato] **DON CHUY:** Mi desayuno: dos huevos, frijoles de la olla, un pedazo de queso fresco y tortilla de maíz.
- [24–30s] **DOÑA LUPE:** Y el pan dulce, los domingos. No todos los días, Jesús.
- [30–36s] **DON CHUY:** Si tiene enfermedad de los riñones, pregúntele a su médico cuánta proteína le toca.
- [36–42s] **DON CHUY:** Comente DESAYUNO y le mando siete desayunos con proteína, baratos y mexicanos.
- *EN gloss:* PROT-AGE 1.0–1.2 g/kg/day for adults over 65; a Mexican breakfast example; kidney caveat.

**Script 4: "Mientras se lava los dientes"** (E09) · Keyword EQUILIBRIO
- [0–3s | Baño, lavabo] **DON CHUY:** Haga esto mientras se lava los dientes y sus piernas se lo agradecen.
- [3–13s] **DON CHUY:** Una mano en el lavabo. Levante un pie apenas del piso. Aguante diez segundos. Cambie de pie. · TEXTO: *Una mano en el lavabo*
- [13–25s] **DON CHUY:** En un estudio con 1,702 personas de 51 a 75 años, quienes no podían sostenerse diez segundos en un pie tuvieron más mortalidad en los siguientes siete años. Es una señal de aviso, no una sentencia.
- [25–31s] **DOÑA LUPE:** Siempre agarrado del lavabo, ¿eh? Sin presumir.
- [31–36s] **DON CHUY:** Dos minutos, dos veces al día. Despacio, pero diario.
- [36–41s] **DON CHUY:** Comente EQUILIBRIO y le mando la rutina completa.
- *EN gloss:* Matches the SAFETY_RULES §11 pass example (E09); support always on.

**Script 5: "Las bolsas del mandado"** (E07) · Keyword FUERZA
- [0–3s | Entrando con bolsas] **DON CHUY:** Mire cómo cargo el mandado. Esto también es ejercicio.
- [3–13s] **DON CHUY:** En un estudio con más de 140 mil adultos de 17 países, cada 5 kilos menos de fuerza de agarre se asoció con 16% más mortalidad. · TEXTO: *Fuerza de agarre = señal de salud*
- [13–24s | Demostración] **DON CHUY:** Una bolsa en cada mano, espalda derecha, hombros atrás. Camine 20 pasos. Descanse. Tres veces.
- [24–30s] **DON CHUY:** Empiece ligerito: una botella de agua de litro en cada bolsa.
- [30–35s] **DOÑA LUPE:** Y el garrafón no lo cargas tú solo, que ya te vi.
- [35–40s] **DON CHUY:** Comente FUERZA y le mando la rutina de fuerza para manos y brazos.
- *EN gloss:* PURE grip-mortality association (E07, exact numbers); farmer's-carry progression.

**Script 6: "Rodillas y escaleras"** (E15, OARSI [S55]) · Keyword RODILLA
- [0–4s | Escalera] **DOÑA LUPE:** Jesús, me duelen las rodillas en la escalera. ¿Mejor ya no subo?
- [4–13s] **DON CHUY:** Al contrario, mi reina. Para la artrosis de rodilla, el ejercicio es de lo primero que recomiendan las guías médicas. · TEXTO: *Ejercicio: tratamiento de primera línea*
- [13–24s | Sentada en silla] **DON CHUY:** Sentada, estire la pierna, aguante cinco segundos y bájela despacio. Diez veces cada pierna.
- [24–31s] **DON CHUY:** Un poquito de molestia está bien si al día siguiente ya se le quitó. Si duele más, se baja la dosis.
- [31–36s] **DOÑA LUPE:** Y si la rodilla está hinchada y caliente, primero al médico.
- [36–41s] **DON CHUY:** Comente RODILLA y le mando la rutina para rodillas.
- *EN gloss:* Exercise is core first-line OA care; pain-monitoring rule M-05/E41; red-flag referral.

**Script 7: "Respire: cuatro y seis"** (E19) · Keyword CALMA
- [0–4s | Mesa, té] **DOÑA LUPE:** Cuando me entran los nervios, él me dice que respire así. Y funciona.
- [4–14s] **DON CHUY:** Aire por la nariz contando cuatro. Suéltelo despacito por la boca contando seis. Cinco minutos. · TEXTO: *4 adentro · 6 afuera*
- [14–24s] **DON CHUY:** Respirar lento, unas seis veces por minuto, ayuda a su cuerpo a pasar al modo calma.
- [24–33s] **DON CHUY:** No sustituye su tratamiento si tiene ansiedad. Es una herramienta más. Y si siente dolor en el pecho, no son nervios hasta que un médico lo diga: llame al 911.
- [33–39s] **DON CHUY:** Comente CALMA y le mando el audio guiado de cinco minutos.
- *EN gloss:* Slow breathing ≈6/min raises vagal HRV (E19); no breath holds over 4 s (4.2); chest-pain emergency line.

**Script 8: "La sed avisa tarde"** (hydration, new E-ID from [S57]) · Keyword AGUA
- [0–3s | Vaso de agua] **DON CHUY:** ¿Sabía que después de los 60 la sed avisa tarde?
- [3–13s] **DON CHUY:** Con los años, el cuerpo siente menos sed aunque le falte agua. Por eso muchos adultos mayores se deshidratan sin darse cuenta.
- [13–23s | Jarra de agua de jamaica sin azúcar] **DON CHUY:** Mi costumbre: un vaso de agua con cada comida y uno a media mañana. Agua de pepino o de jamaica sin azúcar también cuenta.
- [23–31s] **DOÑA LUPE:** Y si el doctor te limitó los líquidos por el corazón o los riñones, hazle caso al doctor, no a este señor.
- [31–37s] **DON CHUY:** Comente AGUA y le mando la tabla para no olvidarse.
- *EN gloss:* Age-related decline in thirst perception is documented; fluid-restriction caveat. **Add an E-ID before publishing.**

**Script 9: "Mito: el ajo en ayunas"** (E20, E35) · Keyword SAL
- [0–4s | Cocina, ajo] **DOÑA LUPE:** Mi comadre dice que el ajo en ayunas le baja la presión. Jesús, dile la verdad.
- [4–10s] **DON CHUY:** El ajo es buena comida. Pero no reemplaza su pastilla de la presión.
- [10–21s] **DON CHUY:** Lo que sí tiene respaldo: moverse casi todos los días, menos sal, y tomar su medicina como se la recetaron. · TEXTO: *Movimiento + menos sal + tu medicina*
- [21–30s | Consomé en polvo] **DOÑA LUPE:** Y el consomé en polvo trae muchísima sal. Sazona con limón, ajo, chile y hierbas.
- [30–35s] **DON CHUY:** Y mídase la presión, comadre.
- [35–41s] **DOÑA LUPE:** Comenta SAL y te mando diez recetas bajas en sal.
- *EN gloss:* Myth-bust (SAFETY_RULES "do not claim" list). Never suggest potassium salt substitutes here without the kidney/medication caution from E35.

**Script 10: "No soy doctor"** (transparency; pinned-post candidate) · Keyword MEMBRESIA
- [0–3s | Patio] **DON CHUY:** No soy doctor. Ni siquiera soy una persona de verdad.
- [3–6s] **DOÑA LUPE:** Yo tampoco. Somos personajes hechos con inteligencia artificial.
- [6–15s] [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: **DON CHUY:** Pero lo que le enseñamos lo revisa un equipo real: una nutrióloga y un fisioterapeuta con cédula profesional. Sus nombres están en nuestra página. · TEXTO: *Revisado por profesionales reales*] FALLBACK: "**DON CHUY:** Pero lo que le enseñamos viene de estudios publicados y de guías para adultos mayores. Las fuentes están en nuestra página. · TEXTO: *Basado en estudios reales*"
- [15–24s] **DON CHUY:** Nada de curas milagrosas. Nada de "deje su medicina". Solo lo que la ciencia respalda y que usted puede hacer en su casa.
- [24–30s] **DOÑA LUPE:** Y si algo no te queda claro, pregúntale a tu médico. Nosotros no nos ofendemos.
- [30–38s] **DON CHUY:** Comente MEMBRESIA y le cuento cómo funciona Años Fuertes: el precio, cómo se cancela, todo.
- *EN gloss:* Brand-defining trust post. **Publish the FALLBACK line until named, credentialed reviewers for this market are under contract** (SAFETY_RULES §7).

### 5.7 Localized offer and pricing

**Membership name:** **Años Fuertes** (the Spanish clone of Strong Years) on every Spanish page: @changyin.espanol (Mode A), Don Chuy & Doña Lupe, and Doña Carmen Ruiz. One product, one name.

**Value stack (ES):**

| Component | ES name | Delivery | Cost to serve |
|---|---|---|---|
| Daily 8–12-min routine (3 levels: silla / de pie / piso) | *Rutina del día* | App/web video + audio, large type | ≈$0 marginal |
| Monthly progress tests (chair stand, one-leg, grip-with-towel) | *Pruebas del mes* | Guided video + logbook | ≈$0 |
| Weekly live-style class (pre-rendered, "premiere" time) | *Clase del domingo* | Video | ≈$0 |
| Mexican recipe library (150 at launch → 300), protein + fiber + low-salt tags | *Recetario Fuerte* | Web + printable PDF, large type | ≈$0 |
| "Pregúntale a Doña Lupe" monthly Q&A (AI character, human-reviewed answers) | *Doña Lupe responde* | Video | ≈$0.20/member |
| Utility WhatsApp: renewal notice, weekly plan reminder (≤4 msgs/mo) | *Recordatorios* | WhatsApp utility templates (MX $0.0080/msg [S49]) | ≈$0.03/member/mo |
| Family plan (+1 profile for a parent) | *Plan familiar* | Same account | ≈$0 |

**Do not** deliver daily content by WhatsApp marketing templates: 30 × $0.0436 = **$1.31/member/month in MX** (14% of net ARPU) and $1.88 in Brazil [S49]. Use the WhatsApp **Channel** (free, public) for top-of-funnel and the member area for paid content.

**Price book (split-test arms mirror the US $12/$15/$20/$25/$30 ladder):**

| Market | Monthly arms | Default | Annual | Prepaid (one-time methods) | Trial | Front-end options |
|---|---|---|---|---|---|---|
| US Hispanic | Full US prices (same arms as the US, OFFER.md): same as the US in every mode: the blitz cells (F25/F30 or T25 → $25) while the founding cohort is open, then `{{STANDARD_PRICE}}` ($35 default); $20 only if the whole US funnel returns to `OFFER_MODE=standard`. One US price across languages (AUDIT F34) | **Same as the US** (blitz: F25/F30/T25 → $25; after the cap: $35) | Same as the US (blitz founding annual $249 from L35; standard-mode $119) | n/a | 7 days for $1 | Free: *Prueba de la silla + rutina de 7 días*. Tripwire A: *Reto 7 días "Fuerza después de los 60"* $7 (US $7 Reset price; includes 7 days of membership). Tripwire B: *Recetario Fuerte* $17 (US Strong Kitchen price). |
| Mexico | MX$119 / 149 / 199 / 249 / 279 | **MX$149** | MX$1,490 | 3 months MX$449 · 12 months MX$1,490 (OXXO/SPEI) | 7 days MX$19 | Tripwire A MX$49 · Tripwire B MX$99 |
| Spain | €8.99 / 9.99 / 13.99 / 16.99 / 19.99 | **€9.99** | €99 | n/a | 7 days €1 (with EU waiver flow) | Tripwire A €3.99 |
| LATAM ex-MX | $4.99–$10.99 (local currency via MoR) | **$5.99** | $59 | quarterly default | 7 days $1 | Tripwire A $2.99 |
| **Gift plan** (all) | 3 / 6 / 12 months, priced in **payer's** currency | 6 months | n/a | n/a | n/a | *"Regálale fuerza a tu mamá"*: payer in the US, recipient anywhere; recipient onboarding by WhatsApp link (utility) |

**Legal copy required at every price display (S-02, MX reform, ES law):** price, interval, auto-renewal, renewal date, "cancele en línea en cualquier momento, en máximo dos pantallas: una oferta para quedarse junto a un botón igual de visible, 'Terminar cancelación'", notice timing (MX: aviso 5 días antes; ES: aviso 15 días antes), refund policy (14 days voluntary; BR 7 days statutory).

### 5.8 Funnel notes (Spanish)

**Keyword map (ManyChat; IG + FB comment→DM; TikTok DM keywords in US/MX [S40]).**

| Keyword | Lead magnet | Next step |
|---|---|---|
| SILLA / FUERZA / EQUILIBRIO / RODILLA / ESPALDA / PISO / HUESOS | 7-day routine for that pillar (video + printable) | Day-0 offer: trial or Tripwire A |
| CAMINA / DESAYUNO / RECETA / SAL / AGUA | Mini-recetario or plan (PDF, large type) | Day-0 offer: Tripwire B |
| CALMA | 5-min guided audio | Trial |
| MAMA | Gift explainer | Gift checkout |
| MEMBRESIA | Años Fuertes membership explainer with full terms | Checkout |

**DM opener (Art. 50-compliant, first message):**
> "¡Hola! Soy el asistente automático de Don Chuy y Doña Lupe (personajes creados con IA). Aquí está su rutina de 7 días 👉 [enlace]. ¿Es para usted o para alguien que quiere? (Responda 1: para mí · 2: para mi mamá/papá)"

Branch 2 → gift flow; branch 1 → pillar-specific follow-up at +24 h and +72 h (inside the 24-h window where possible), then email.

**Landing page (ES), top to bottom:** hero with the real product (routine on a phone + printable plan) · [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: "Personajes de IA · Contenido revisado por [Nombre], nutrióloga (Céd. Prof. ####) y [Nombre], fisioterapeuta (Céd. Prof. ####)"] FALLBACK: "Personajes de IA · Contenido basado en estudios publicados (fuentes en nuestra página)" · 3 benefits framed as *access*, not outcomes (S-01) · what's inside (stack) · price box with all legal copy · "Cómo cancelar" block with a screenshot of the two-screen cancel · FAQ (¿Es real Don Chuy? No. ¿Sirve si tengo 75? Sí, hay nivel silla. ¿Puedo pagar en OXXO? Sí, plan de 3 o 12 meses) · Minimum 18–20 px body, **pure black-on-white or white-on-deep-color, no gray text anywhere, especially buttons**. No fake reviews (T-01). Real member quotes only with logged permission (T-02).

**Claims linter additions (es-419), BLOCK unless an E-ID and an allowed frame apply:**
`cura(r|n)?|sana(r)? (la|el|tu|su)|elimina (la|el)|adiós a (la|el)|desintoxica|limpia (el|tu) (hígado|colón|sangre)|sin medicamentos|deje (su|tu) (medicina|pastilla)|revierte|milagro(so)?|insulina vegetal|dióxido de cloro|CDS|MMS|lo que la farmacia no (te|le) dice|baja la presión (al instante|en minutos)|el chino|maestro|monje|templo`

**Paid media (test from the d0 market launch; scale from Gate 2):** Advantage+ with Spanish-language creative, age 50–75, US-Hisp (language: Spanish) and MX campaigns separate. Winners = organic top 5% by keyword-comments/1K views. Start $100/day US-Hisp + $80/day MX. Scale 20%/day while CAC ≤ 3-month gross profit.

---

## 6. Sources

- [S1] Adligator, Meta Ads CPM by Country 2026 (data 31 Mar 2026): https://adligator.com/blog/meta-ads-cpm-by-country-benchmarks
- [S2] Lebesgue, Facebook Ads CPM by Country: 2026 Ecommerce Benchmarks: https://lebesgue.io/facebook-ads/facebook-cpm-by-country
- [S3] NapoleonCat, Facebook/Instagram users by country and age (Aug 2026; Italy and Japan Jun 2026), e.g. https://stats.napoleoncat.com/facebook-users-in-mexico/ · https://stats.napoleoncat.com/facebook-users-in-brazil/ · https://stats.napoleoncat.com/facebook-users-in-spain/ · https://stats.napoleoncat.com/facebook-users-in-germany/ · https://stats.napoleoncat.com/facebook-users-in-italy/ · https://stats.napoleoncat.com/facebook-users-in-france/ · https://stats.napoleoncat.com/facebook-users-in-colombia/ · https://stats.napoleoncat.com/facebook-users-in-argentina/ · https://stats.napoleoncat.com/facebook-users-in-poland/ · https://stats.napoleoncat.com/facebook-users-in-india/ · https://stats.napoleoncat.com/facebook-users-in-philippines/ · https://stats.napoleoncat.com/facebook-users-in-japan/ · https://stats.napoleoncat.com/facebook-users-in-saudi_arabia/ · https://stats.napoleoncat.com/facebook-users-in-canada/ · https://stats.napoleoncat.com/facebook-users-in-australia/ · https://stats.napoleoncat.com/facebook-users-in-united_states_of_america/ · https://stats.napoleoncat.com/instagram-users-in-brazil/ · https://stats.napoleoncat.com/instagram-users-in-mexico/ · https://stats.napoleoncat.com/instagram-users-in-spain/ · https://stats.napoleoncat.com/instagram-users-in-germany/ · https://stats.napoleoncat.com/instagram-users-in-united_states_of_america/
- [S4] World Bank API (2024): NY.GDP.PCAP.CD, NY.GDP.PCAP.PP.CD, SP.POP.65UP.TO, SP.POP.TOTL: https://api.worldbank.org/v2/country/MEX;BRA;ESP;DEU/indicator/NY.GDP.PCAP.PP.CD?format=json&date=2024
- [S5] Net Life Value, Spotify Premium prices by country 2026: https://www.netlifevalue.com/prices/spotify
- [S6] IBGE via NC News (1 Aug 2026), 74.5% of 60+ used the internet in 2025: https://ncnews.com.br/2026/08/01/quase-75-dos-idosos-usam-internet-no-brasil-aponta-pesquisa-do-ibge/
- [S7] INEGI ENDUTIH 2024 via Forbes México, 55+ internet use 71%: https://forbes.com.mx/los-usuarios-de-internet-en-mexico-ascendieron-a-100-2-millones-en-2024-el-83-1-de-la-poblacion/
- [S8] DataReportal, Digital 2026: Mexico: https://datareportal.com/reports/digital-2026-mexico
- [S9] DataReportal, Digital 2026: Brazil: https://datareportal.com/reports/digital-2026-brazil
- [S10] Pew Research, Key facts about U.S. Latinos (Oct 2025): https://www.pewresearch.org/short-reads/2025/10/22/key-facts-about-us-latinos/
- [S11] AARP, Heritage & Heart: Hispanic Adults 50+ (2024): https://www.aarp.org/pri/topics/aging-experience/demographics/heritage-heart-perspectives-values-hispanic-adults/
- [S12] ACL, 2020 Profile of Hispanic Americans 65+: https://acl.gov/sites/default/files/Profile%20of%20OA/HispanicProfileReport2021.pdf
- [S13] Pew Research, Americans' Social Media Use 2025: https://www.pewresearch.org/internet/2025/11/20/americans-social-media-use-2025/
- [S14] Mobile Society Research Institute (moba-ken), Japan seniors' SNS use 2025: https://www.moba-ken.jp/project/seniors/seniors20250418.html
- [S15] Kyunghyang Shinmun / Statistics Korea 2025 Elderly Statistics: https://www.khan.co.kr/article/202509291723001
- [S16] Maldita.es / Factchequeado, 50 Spanish-language AI health profiles (Jul 2026): https://factchequeado.com/teexplicamos/20260729/doctors-quacks-healers-ai-spanish-false-health-advice-instagram/ · https://maldita.es/investigaciones/20260727/perfiles-instagram-salud-espa%C3%B1ol/
- [S17] Xataka, AI elderly influencers (Paco del Campo): https://www.xataka.com/robotica-e-ia/se-acabaron-bellezas-espectaculares-ahora-influencers-creados-ia-optan-dar-pena-resultar-entranables
- [S18] Diário da Manhã, AI fake doctors in Brazil; CFM monitoring: https://www.dm.com.br/economia/medicos-falsos-criados-por-ia-lucram-com-curas-milagrosas-nas-redes-sociais/
- [S19] Stripe Docs, Pix Automático: https://docs.stripe.com/payments/pix/pix-automatico
- [S20] Stripe Changelog, Pix recurring payments support (2026-04-22): https://docs.stripe.com/changelog/dahlia/2026-04-22/pix-recurring-payments-support
- [S21] Stripe, Local payment methods pricing: https://stripe.com/pricing/local-payment-methods
- [S22] Stripe, OXXO: https://stripe.com/payment-method/oxxo
- [S23] Stripe Docs, Managed Payments (merchant of record): https://docs.stripe.com/payments/managed-payments
- [S24] Dodo Payments, Cheapest MoR 2026: https://dodopayments.com/blogs/cheapest-merchant-of-record
- [S25] Dodo Payments, VAT/GST registration thresholds for digital sellers: https://dodopayments.com/blogs/vat-gst-registration-thresholds
- [S26] Kintsugi, Mexico VAT (IVA) guide 2026: https://trykintsugi.com/sales-tax-guides/latam/mexico
- [S27] Barbosa Legal, IOF increase since May 2025: https://barbosalegal.com/chronicles/increase-of-iof-in-brazil-what-has-changed-in-international-transactions-since-may-2025
- [S28] ADVANT Beiten, Withdrawal button from 19 June 2026: https://www.advant-beiten.com/en/news/der-widerrufs-button-kommt-neue-pflicht-fuer-den-online-handel-ab-19-juni-2026
- [S29] Churnkey, EU Consumer Rights Directive subscription guide: https://churnkey.co/guides/eu-consumer-rights-directive
- [S30] EU AI Act Art. 50 practical guide: https://artificialintelligenceact.eu/transparency-rules-article-50/
- [S31] Spain Ministerio de Derechos Sociales, Consumo y Agenda 2030, subscriptions under Ley de Servicios de Atención a la Clientela: https://www.dsca.gob.es/en/consumo/nota-informativa-nueva-regulacion-suscripciones-ley-servicios-atencion-clientela
- [S32] Greenberg Traurig, Mexico LFPC reform on subscriptions (Dec 2025): https://www.gtlaw.com/en/insights/2025/12/reformas-a-la-ley-federal-de-proteccion-al-consumidor
- [S33] Conjur, Direito de arrependimento em serviços digitais (May 2025): https://conjur.com.br/2025-mai-25/direito-de-arrependimento-em-servicos-digitais-posso-cancelar-streaming-curso-online-ou-app/
- [S34] Lewis Silkin, UK DMCC subscriptions regime delayed to spring 2027: https://www.lewissilkin.com/en/insights/2026/04/02/consumer-law-update-subscriptions-regime-delayed-again-to-spring-2027-102mops
- [S35] Distique Avocats, Loi influenceurs du 9 juin 2023 ("Image virtuelle"): https://distique-avocats.com/loi-influenceurs/
- [S36] LexOrbis, ASCI health/finance influencer qualification update (Apr 2025): https://www.lexorbis.com/asci-updates-influencer-guidelines-for-health-and-finance-sectors-strikes-balance-between-expertise-and-expression/
- [S37] Norton Rose Fulbright, Italy Law No. 132/2025 on AI: https://www.nortonrosefulbright.com/en/knowledge/publications/9bfedfea/italy-enacts-law-no-132-2025-on-artificial-intelligence-sector-rules-and-next-steps
- [S38] Barbieri Advogados, AI content labelling in Brazil 2026: https://www.barbieriadvogados.com/conteudo-gerado-por-ia-marcacao-e-rotulagem/
- [S39] TechCrunch, Instagram limits undisclosed AI profiles (31 Aug 2026): https://techcrunch.com/2026/08/31/instagram-puts-new-limits-on-undisclosed-ai-profiles/
- [S40] ManyChat Community, TikTok automations available in the U.S. (not EU/UK): https://community.manychat.com/product-updates/tiktok-automations-are-now-available-in-the-u-s-7729
- [S41] ElevenLabs API pricing: https://elevenlabs.io/pricing/api
- [S42] Perso, AI dubbing pricing 2026: https://perso.ai/blog/ai-dubbing-pricing-2026-cost-breakdown-for-every-major-tool
- [S43] Fluxnote, HeyGen video translation guide 2026: https://fluxnote.io/guides/heygen-video-translation-guide
- [S44] Upwork, Spanish proofreaders: https://www.upwork.com/hire/spanish-proofreading-freelancers/
- [S45] Upwork, Dietitians: https://www.upwork.com/hire/dietitians/
- [S46] CallForce, Bilingual customer support outsourcing rates 2026: https://callforce.global/blog/bilingual-customer-support-outsourcing/
- [S47] Intercom pricing (Fin): https://www.intercom.com/pricing
- [S48] FormBeep, WhatsApp API pricing by country (1 Jul 2026): https://formbeep.com/whatsapp-api-pricing/
- [S49] Setsmart, WhatsApp Business API per-message rates 2026: https://setsmart.io/blog/whatsapp-business-api-pricing
- [S50] CDC STEADI 30-Second Chair Stand: https://www.cdc.gov/steadi/media/pdfs/STEADI-Assessment-30Sec-508.pdf
- [S51] Sports Medicine 2022, post-meal exercise meta-analysis: https://link.springer.com/article/10.1007/s40279-022-01808-7
- [S52] BJSM 2022, 10-second one-legged stance: https://pubmed.ncbi.nlm.nih.gov/35728834/
- [S53] PURE grip strength, Lancet 2015: https://pubmed.ncbi.nlm.nih.gov/25982160/
- [S54] PROT-AGE 2013: https://pubmed.ncbi.nlm.nih.gov/23867520/
- [S55] OARSI 2019 guidelines: https://pubmed.ncbi.nlm.nih.gov/31278997/
- [S56] Zaccaro 2018, slow breathing review: https://pmc.ncbi.nlm.nih.gov/articles/PMC6137615/
- [S57] Disturbances of thirst and fluid balance with aging: https://pubmed.ncbi.nlm.nih.gov/28267585/
- [S58] DKFZ, AI influencers for cancer prevention (Jan 2025): https://www.dkfz.de/en/news/press-releases/detail/krebspraevention-zum-niedrigpreis-ki-generierte-influencer-erreichen-risikogruppen-auf-social-media
- [S59] francenum.gouv.fr, Résiliation "en 3 clics": https://www.francenum.gouv.fr/guides-et-conseils/developpement-commercial/gestion-de-la-relation-client/resiliation-en-3-clics
- [S60] Heilmittelwerbegesetz (HWG): https://www.gesetze-im-internet.de/heilmwerbg/BJNR006049965.html
- [S61] Freshfields, Digital Fairness Act Part 7, subscriptions: https://www.freshfields.com/en/our-thinking/blogs/technology-quotient/digital-fitness-check-and-digital-fairness-act-part-7-contract-cancellations-and-102krzt
- [S62] ARD/ZDF-Medienstudie 2025, social media usage (via Radioszene): https://www.radioszene.de/208344/social-media-wachstum.html
- Internal: BRIEF.md (tool unit costs, Yang Mun store EN/DE/ES), SAFETY_RULES.md, EVIDENCE.md, prompts/08_localization_adapter.md.

**Known data gaps (verify before spending):** UK 55+ FB count (EST); Korea 55+ platform split; exact Stripe Managed Payments support for Pix/OXXO; Spain's 15-day notice applied to monthly plans (counsel); MX reviewer cédula verification process; live FX.
