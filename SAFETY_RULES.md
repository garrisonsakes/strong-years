# SAFETY_RULES.md: compliance checker specification

This file is written for **both** the automated compliance checker (an LLM plus regex pass that runs on every script JSON before rendering, and again on the rendered caption and on-screen text) and the human reviewer who spot-checks.

**Severity levels**
- `BLOCK`: the post can't render or publish until it's fixed. The checker returns the rule ID and the offending span.
- `REWRITE`: the checker auto-rewrites with the listed safe alternative, then re-checks.
- `FLAG`: the post publishes, but a human sees it in the daily review queue within 24 h.
- `REQUIRE`: the field or string must be present, or the post is treated as BLOCK.

**Pipeline position:** Script LLM → **Checker pass 1 (script JSON)** → voice/video render → **Visual QC (movement form)** → **Checker pass 2 (final caption + burned-in text + transcript via ASR)** → scheduler. A post published without passing both checker passes is a P0 incident.

---

## 0. Why these rules exist (context for the checker LLM)
Yang Mun was attacked for four things (E44): (1) posing as a real 87-year-old monk, (2) borrowing religious clergy trust, (3) remedies with no evidence ("lower blood pressure instantly", onion water), and (4) AI-generated "customer" photos and fake testimonials. Platforms also changed in 2026. Instagram requires the AI-generated profile label or the account loses reach. TikTok excludes unlabeled realistic AI from For You. YouTube's July 2026 policy targets "AI personas as credentialed experts" in health. The FTC bans fake reviews and testimonials and requires competent and reliable scientific evidence for health claims. **Our moat is the opposite of Yang Mun: openly AI, human-reviewed, evidence-cited, safe.** A single violation undoes that moat.

---

## 1. Identity & disclosure rules

| ID | Rule | Severity |
|---|---|---|
| D-01 | Every profile bio contains the disclosure string (per platform, §7). The IG profile has the "AI-generated profile" label switched on. TikTok has the AI-generated content toggle on for **every** post. YouTube has "altered or synthetic content" = Yes on every upload. | REQUIRE |
| D-02 | Every video carries a persistent burned-in corner tag. EN: `AI character`. ES: `Personaje IA`. Minimum 28 px at 1080 w, top-left, 70% opacity, white on a dark pill (no gray text, per brand rules). | REQUIRE |
| D-03 | Every caption ends with the disclosure footer (§7). | REQUIRE |
| D-04 | Characters never claim to be human, real or alive. Block: `I am real`, `I'm a real person`, `not AI`, `this is really me`, `born in 19xx` stated as fact outside a clearly fictional frame, `my real name`. | BLOCK |
| D-05 | Characters never claim professional credentials: doctor, Dr., physician, nurse, physical therapist, PT, physiotherapist, dietitian, nutritionist, pharmacist, TCM practitioner, acupuncturist, licensed, certified, "master" as a professional healing title, monk, priest, lama, shifu, sifu, guru, clergy. Block these when used about Chang or Sun. The word "coach" is allowed. | BLOCK |
| D-06 | The fictional backstory may color a story but may **never be evidence**. Block any pattern where a character's own experience proves a health outcome: `I cured my`, `this fixed my`, `my arthritis went away`, `I haven't been sick since`, `I never went to the hospital because`, `my doctor was shocked`. | BLOCK |
| D-07 | No religious framing. Block: `monastery`, `temple secret`, `sacred`, `ancient Chinese secret`, `ancient wisdom` (as a health authority), `qi will heal`, `Buddha`, `dharma`, `meridian cleansing`. Tai chi and qigong are allowed as **exercise** with evidence (E14–E17). Terms like "qi" may appear only as cultural vocabulary, never as a mechanism ("in tai chi we call this 'sinking the qi' — really it's lowering your center of mass"). | BLOCK / REWRITE |
| D-08 | A winking AI reference appears in at least 1 in 20 posts per page (e.g., Sun: "He's AI and he still won't do his stretches"). The scheduler tracks this. | FLAG if <1/20 over a trailing 7 days |
| D-09 | Never impersonate or name a real person, brand, doctor or creator (including Yang Mun) in a negative or comparative way. Generic "internet trends" is fine. | BLOCK |

## 2. Endorsements, testimonials, reviews (FTC)

| ID | Rule | Severity |
|---|---|---|
| T-01 | No fabricated testimonials, reviews, "member results", before/after photos or quotes. AI-generated "customer" faces are banned everywhere: posts, sales pages, ads, email. | BLOCK |
| T-02 | Real member comments may be shown only with (a) written permission logged by comment ID, (b) the real handle or first name + initial, (c) no editing of meaning, and (d) if the post makes a result claim, the typical-results disclosure: "Results vary. Most people who follow the plan 3×/week notice easier chair stands within weeks." | REQUIRE when a comment is shown |
| T-03 | Side characters (Frank, the kids) are **fictional** and may not report product results. Block: `Frank lost`, `Frank's knee is healed`, `since joining the club Frank…`. Frank may show effort, regressions and humor. | BLOCK |
| T-04 | No fake scarcity or fake pricing anchors in content: `only 3 spots left`, `price goes up at midnight` (unless literally true and logged), `was $99` (unless actually sold at that price). | BLOCK |
| T-05 | Any paid relationship (a brand, affiliate or supplement partner) needs `#ad` or "Paid partnership" at the start of the caption plus the platform tool. | REQUIRE |

## 3. Health-claim language

### 3.1 Blocked words and phrases (regex, case-insensitive, word-boundary). BLOCK unless listed as REWRITE.
```
cure[sd]?|curing|heal(s|ed|ing)? (your|the|my) (arthritis|diabetes|blood pressure|cancer|heart|liver|kidney|thyroid|dementia|alzheimer'?s|neuropathy|osteoporosis)
reverse[sd]? (diabetes|arthritis|osteoporosis|aging|dementia|alzheimer'?s|heart disease)
(treats?|treatment for) (diabetes|hypertension|cancer|arthritis|depression|anxiety disorder|insomnia|ibs|gerd)
prevent[s]? (cancer|dementia|alzheimer'?s|stroke|heart attack)            → REWRITE: "is linked with lower risk of" + evidence ID required
detox|cleanse (your )?(liver|colon|kidneys|blood)|flush (out )?toxins
lower(s)? (your )?blood pressure (instantly|in minutes|fast|immediately)
burn (sugar|belly fat|fat) (fast|instantly|overnight)
melt(s)? (belly )?fat|target(ed)? fat loss|spot reduc
boost(s)? (your )?immune system                                          → REWRITE: "supports normal immune function" only with nutrient evidence, else delete
anti-?aging (secret|miracle)|fountain of youth|add (\d+ )?years to your life|live to 100
miracle|secret (doctors|big pharma)|doctors (hate|don't want)|big pharma|they don't want you to know
(?<!money.back )guarantee\b|guarantee[ds]\b|money.back guarantee (that|you|you'?ll|your|it|it'?ll|this)\b|money.back guarantee\b[^.!?\n]{0,120}\b(stronger|sleep\w*|pain\w*|lose|lost|losing|weight|fat|balance|falls?|results?|feel better|younger|fix\w*|heal\w*|improve\w*|works? for you|see a difference|notice)|(stronger|sleep\w*|pain\w*|lose|lost|losing|weight|fat|balance|falls?|results?|feel better|younger|fix\w*|heal\w*|improve\w*|works? for you|see a difference|notice)\b[^.!?\n]{0,120}\bmoney.back guarantee|100% (safe|effective|natural)|no side effects|works for everyone
clinically proven                                                         → REWRITE: "studied in [n] people" + evidence ID
instead of (your )?(medication|medicine|pills|surgery|doctor)
(stop|quit|reduce|replace) (taking )?(your )?(medication|medicine|pills|insulin|blood thinner|statin)
natural (alternative|replacement) (to|for) (medication|statins|metformin|antidepressants)
never (get sick|go to the (doctor|hospital))
(this|it) (will|can) fix (your )?(knee|back|hip|shoulder) (forever|for good|permanently)
pain[- ]free (forever|guaranteed)
```

**Myth-bust exception (MB-EX).** A blocked term may appear **only** when all of these are true: (a) the script has `pillar: P15` or `myth_bust: true`; (b) the sentence containing the term negates or debunks it (e.g. "Detox tea? No.", "If a video says 'instantly', close the video"); (c) any on-screen text containing the term carries a "MYTH" label or ✗ marker; (d) the script states what the evidence *does* support, with an evidence ID. The checker LLM confirms (b) semantically. Regex alone can't pass it. The exception never covers disease-cure claims (`cure`, `reverse [disease]`) or medication phrases. Those stay BLOCK even inside a debunk.

**Commerce-guarantee exception (CX-GUAR, BLITZ canon, Sep 30 2026).** "Guarantee" is allowed **only** in the exact refund-policy phrases "14-day money-back guarantee" and "money-back guarantee" (hyphen or space). It stays BLOCK everywhere else: "guaranteed results", "guarantee you'll sleep", "guarantees", "money-back guarantee that/you'll…", and any sentence that puts a money-back guarantee next to a health outcome ("stronger in 14 days, money-back guarantee"). The regex line above encodes this with a lookbehind, and `prompts/blocked_claims.json` BC14/BC23 mirror it. The MB-EX never covers the outcome case.

### 3.2 Flagged (FLAG, and an evidence ID is required in the script JSON)
`inflammation|anti-inflammatory|hormones?|testosterone|estrogen|metabolism|blood sugar|insulin|cholesterol|blood pressure|gut health|microbiome|immune|memory|brain|dementia|cortisol|vagus|HRV|bone density|osteoporosis|arthritis|sciatica|neuropathy|prostate|menopause|constipation|IBS|reflux|sleep apnea|longevity|lifespan|mortality`

### 3.3 Allowed claim frames (the checker prefers these)
- "In a study of [n] people aged [x]…" (evidence ID required)
- "linked with", "associated with", "people who… tend to…" (required for C-grade evidence)
- "improved", "reduced", "helped" (only for A/B-grade RCT evidence)
- "may help", "can support", "for many people", "for most healthy adults"
- "a sign worth checking with your doctor", "a screening test, not a diagnosis"
- "average change over [x] weeks of practice" (required when citing BP, glucose or BMD)

### 3.4 Numbers rules
| ID | Rule | Severity |
|---|---|---|
| C-01 | Every statistic must match the EVIDENCE.md entry exactly (number, population, direction). The checker compares the numbers against the cited ID. | BLOCK on mismatch |
| C-02 | Observational (C-grade) findings may never be phrased causally. "Grip strength predicts mortality" is fine. "Squeezing a ball adds years" is BLOCK. | BLOCK |
| C-03 | Relative risk needs context. If you say "84% higher risk", on-screen text must also show the population ("adults 51–75, 7-yr study"). | REQUIRE |
| C-04 | No invented numbers ("90% of people over 60…") unless there's an evidence ID. | BLOCK |
| C-05 | Protein advice stays inside E28 (1.0–1.2 g/kg; 1.2–1.5 if active). Always add "kidney disease → ask your doctor" whenever grams/kg are given. | REQUIRE |
| C-06 | Food and remedy content must include one "who should skip or ask first" line when a known caution exists (see §5 table). | REQUIRE |
| C-07 | A script that makes a health claim without an `evidence` field is BLOCK. | BLOCK |

## 4. Movement safety

### 4.1 Required elements for any script with movement (`has_movement: true`)
| ID | Requirement | Severity |
|---|---|---|
| M-01 | **Support cue** within the first 10 s of the movement: "Hold a counter/chair" or "chair behind you" or "wall next to you". Balance drills always start with support. | REQUIRE |
| M-02 | **Regression** offered, spoken or on screen: an easier version (higher seat, hands on thighs, partial range, wall support). | REQUIRE |
| M-03 | **Stop rule** on screen or in the caption: "Stop if you feel chest pain, dizziness or sharp pain." | REQUIRE |
| M-04 | **Breathing cue** for any strength move: "breathe out as you stand/push". Never "hold your breath" (E42). | REQUIRE |
| M-05 | Pain rule for rehab content: "Mild discomfort up to 3 out of 10 is okay if it settles by tomorrow. Sharper, or worse the next day → back off and ask your doctor or PT" (E41). | REQUIRE for pillar P06 |
| M-06 | Rep and duration defaults for general-audience posts: 5–12 reps, 1–3 sets, holds 10–30 s, balance holds ≤30 s. Anything beyond must be labeled "advanced" and shown with a regression. | FLAG |
| M-07 | Chang may *demonstrate* advanced feats (deep squat, pistol to box, floor-to-stand without hands, heavy carries) **only** with the on-screen label "Chang's level — not your starting point" and a shown beginner version. | REQUIRE |
| M-08 | Generated motion QC: every movement clip passes human form review before publishing. Check that knees track over toes (no inward collapse), neutral spine on hinges, no hyperextended locked knees in balance, the chair doesn't slide (against a wall), and nothing anatomically impossible (extra joints, hands through objects). Any fail means re-render. **Never publish AI motion with incorrect form, even as B-roll.** | BLOCK |
| M-09 | Chairs are shown against a wall or counter in every chair drill. Balance drills are shown next to a counter or in a corner. | REQUIRE (visual QC) |
| M-10 | No barefoot drills on slippery floors, no socks on hard floors, no rugs under the feet. Visual QC checks. | BLOCK |

### 4.2 Contraindication table (the checker inserts the note when the movement tag matches)
| Movement tag | Who must skip or modify (spoken or in caption) | Rule |
|---|---|---|
| `spinal_flexion_loaded` (sit-ups, crunches, weighted toe-touches, deep rounded stretches with load) | Osteoporosis/osteopenia or past vertebral fracture | **Not used in general content at all** (E40). Use hinge, bird-dog, wall-slide alternatives. |
| `spinal_twist_end_range` (forceful seated twists, golf-swing twists with load) | Osteoporosis | Gentle, unloaded rotation only, with the cue "only as far as comfortable". |
| `floor_transfer` (sit-rise test, floor get-ups) | Recent hip/knee replacement (follow surgeon precautions), severe knee OA, dizziness, anyone who can't get up alone | Show the chair version first. Cue: "Only try the floor with a sturdy chair or sofa next to you and someone home." |
| `deep_hip_flexion` (>90° with adduction or internal rotation) | Hip replacement within the surgeon's precaution period | Cue: "New hip? Follow your surgeon's precautions first." |
| `isometric_hold` (wall sit, plank >20 s, heavy grip) | Uncontrolled/very high blood pressure, recent heart event | Cue: "Breathe through it. High blood pressure or heart condition? Ask your doctor before long holds." (E20, E42) |
| `inversion_head_below_heart` (downward dog, forward folds held long) | Glaucoma, uncontrolled BP, retinal issues, dizziness | Avoid in general content. If used: "Skip if you have glaucoma or blood-pressure dizziness." |
| `neck_circles_full` | Cervical arthritis, dizziness, vertebral artery concerns | Replace with nods and half-turns. Never full circles. |
| `jumping_impact` | Osteoporosis without training history, pelvic floor issues, joint replacement | General content uses heel drops (standing heel raise → drop) only, labeled "gentle impact". LIFTMOR-style loading only as "supervised" (E29). |
| `breath_retention` (holds >5 s, hyperventilation styles like Wim Hof) | Pregnancy (N/A mostly), heart conditions, epilepsy, fainting history | **Not used.** Allowed: slow breathing, cyclic sighing, extended exhale (E18–E19). No breath holds over 4 s. |
| `standing_up_fast` (after floor or bed work) | Orthostatic hypotension, BP medication | Cue: "Sit a moment before you stand, then stand slowly." Required in all bed/floor routines. |
| `overhead_press_loaded` | Shoulder pain or impingement, rotator cuff tear | Offer landmine/incline alternative or reduce range: "only to comfortable height". |
| `pelvic_floor` | Pelvic pain, post-surgery | "If you have pelvic pain or leaking that isn't improving, a pelvic-floor physio can check you." (E31) |

### 4.3 Red-flag symptoms: required "see your doctor" triggers
If the script topic or a comment being replied to mentions any of the following, the script must include the **Red-flag line** and may not offer an exercise or remedy as the solution:
`chest pain | pressure in chest | shortness of breath at rest | fainting | sudden weakness or numbness (face/arm/leg) | trouble speaking | sudden severe headache | new confusion | calf swelling/redness (clot) | blood in stool or black stool | vomiting blood | unexplained weight loss | fever with back pain | loss of bladder/bowel control or numbness in the saddle area | night pain that wakes you and doesn't change with position | a fall with head strike (especially on blood thinners) | hot swollen joint | severe new back pain after a fall`

- **Red-flag line (EN):** "That one isn't for exercise. That's for your doctor, today." (Chang) or "No soup for this. Call your doctor. Today." (Sun)
- **Emergency line (EN):** "Chest pain, face drooping, can't speak? Call 911 now." (Adapt the number per market: ES-US 911, MX 911, ES 112, UK 999, EU 112, BR 192, IN 112, JP 119.)

### 4.4 Crisis protocol (comments, DMs, replies)
- Any comment or DM mentioning suicide, self-harm, wanting to die, or abuse → **no character reply in public**. The automation sends a DM (or pins a reply when DMs are closed): "I'm an AI character, but you matter to real people. In the US call or text 988 (Suicide & Crisis Lifeline). Outside the US: findahelpline.com." It also escalates to a human moderator within 1 h.
- Grief, loneliness, estrangement (very common in this audience): a warm, non-clinical character reply is allowed, and it must not promise to be a companion or friend replacement. Allowed: "Call one person today. Sun Yoon says so." Blocked: "I'll always be here for you", "you don't need anyone else".
- The characters never give individualized medical advice in comments or DMs. The default deflection is "Good question for your doctor. Here's what the research says in general…" plus a link to a general post.
- DM automations (ManyChat) must state in the first message: "This is an automated message from the Chang & Sun team (AI characters). Reply STOP anytime."

## 5. Food, remedy & supplement cautions (auto-insert table)
| Topic tag | Required caution line |
|---|---|
| `honey` | "Never for babies under 1." Plus, for diabetes: "counts as sugar." |
| `ginger_supplement` / `turmeric_supplement` / `garlic_supplement` / `fish_oil` | "On blood thinners? Ask your doctor first." |
| `grapefruit` | "Grapefruit interacts with many medicines. Check your labels." |
| `potassium_salt` / `salt_substitute` / `bananas_large_amounts` | "Kidney disease or on blood-pressure pills like ACE inhibitors? Ask your doctor first." (E35) |
| `high_protein` | "Kidney disease? Ask your doctor for your number." (E28) |
| `fiber_increase` | "Go up slowly and drink water, or you'll feel it." (E24) |
| `fermented_foods` / `kimchi` | "Kimchi is salty. Watching sodium? Small portions or rinse." |
| `leafy_greens_vitamin_K` | "On warfarin? Keep greens steady, don't suddenly change. Ask your doctor." |
| `peppermint_oil` | "Can make reflux worse." (E34) |
| `fasting` / `meal_skipping` | **Not used** for this audience (medication/hypoglycemia risk). BLOCK. |
| `raw_eggs` / `raw_sprouts` / `unpasteurized` | BLOCK (older adults are at higher foodborne-illness risk). |
| `alcohol_as_health` (e.g. "red wine for your heart") | BLOCK. |
| `supplement_any` | Allowed only in "Later" phase content with the line "Supplements don't replace food or medicine. Ask your doctor or pharmacist, especially if you take prescriptions." No dosing beyond label-standard, no disease claims (DSHEA structure/function only), and the FDA disclaimer on sales pages. |
| `herbs_tcm` | Herbs may be discussed as **culinary** (ginger, scallion, jujube, goji in soup). Medicinal herb dosing is blocked. |

## 6. Visual & set rules (checked at visual QC)
| ID | Rule | Severity |
|---|---|---|
| V-01 | No robes, prayer beads, temples, altars, incense ceremonies, monks, meditation-hall imagery or misty-mountain Orientalist sets. Sets come only from the approved home world (CHARACTERS.md §5). | BLOCK |
| V-02 | No fake medical settings (white coats, clinic backgrounds, stethoscopes on characters). | BLOCK |
| V-03 | "Study cards" shown on screen must reproduce the real citation (journal, year, first author) exactly as in EVIDENCE.md. Never fake a journal page or PDF. Use our own branded card design. | BLOCK |
| V-04 | Text colors: white or cream on dark, or near-black on cream/white. **No gray text anywhere** (brand rule). Minimum 52 px caption size at 1080×1920, max 2 lines, safe zone: 250 px from the bottom, 180 px from the top. | REQUIRE |
| V-05 | Characters stay consistent with CHARACTERS.md visual specs (reference-image lock). Hands have 5 fingers. The wedding rings are present. | BLOCK on major drift |
| V-06 | Other people in the frame are AI-generated extras (not real people's likenesses), never minors in health demos, and never presented as "patients". | BLOCK |
| V-07 | Food safety visuals: no raw meat near ready-to-eat food, and no knife used toward the hand. | FLAG |

## 7. Required disclosure strings (exact text)

Reviewer gate (same convention as FUNNEL.md): every string that claims or implies review by licensed professionals is written as `[ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: <claim>] FALLBACK: "<line with no review claim>"`. Until a credentialed reviewer has signed (PAGE DNA `reviewer_signed` = true), publish the FALLBACK string exactly.

**Instagram bio (Chang page):**
[ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: `Chang Yin, 74 (AI character) · Strength after 60, done safely · Science-checked by licensed humans · 👇 Free 7-day plan`] FALLBACK: "`Chang Yin, 74 (AI character) · Strength after 60, done safely · Real research, sources linked · 👇 Free 7-day plan`"

**Instagram bio (Sun Yoon kitchen):**
`Sun Yoon, 76 (AI character) · His wife. Blunter than him. · Real recipes, real research · 👇 Free soup book`

**Duo page bio:**
[ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: `Chang & Sun · AI characters, real advice, 50 years of fictional marriage · Reviewed by licensed PT + dietitian`] FALLBACK: "`Chang & Sun · AI characters, real advice, 50 years of fictional marriage · Sources on our site`"

**TikTok / YouTube bio:** same, plus [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: "Characters are AI. Content is reviewed by licensed professionals (names on our site)."] FALLBACK: "Characters are AI. Content is built on published research (sources on our site)."

**Caption footer (EN, required, always last):**
[ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: `Chang & Sun are AI characters. Content is educational, reviewed by licensed professionals, and not medical advice. Check with your doctor before starting new exercise.`] FALLBACK: "`Chang & Sun are AI characters. Content is educational, built on published research, and not medical advice. Check with your doctor before starting new exercise.`"

**Caption footer (ES):**
[ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: `Chang y Sun son personajes de IA. Contenido educativo revisado por profesionales con licencia; no es consejo médico. Consulta a tu médico antes de empezar un ejercicio nuevo.`] FALLBACK: "`Chang y Sun son personajes de IA. Contenido educativo basado en investigación publicada; no es consejo médico. Consulta a tu médico antes de empezar un ejercicio nuevo.`" (Spanish-market reviewer must be credentialed for that market, EXPANSION.md.)

**Movement add-on (appended before the footer):**
`Go at your own pace. Hold a counter or chair. Stop if you feel chest pain, dizziness, or sharp pain.`

**Pinned post #1 (every page):** "Hi, we're AI." Script lives in CHARACTERS.md §8.

**Website "Who makes this" page (required before any paid ad runs):** [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: real names, licenses and photos of the human reviewers (PT/DPT, RD, MD advisor),] FALLBACK: "the real team (no credential claims)," the editorial process, and how evidence is chosen. *These must be real people under contract. If there's no reviewer yet, remove "reviewed by licensed professionals" from every string until there is.* (BLOCK: the claim can't be made without a signed reviewer.)

## 8. Commerce & subscription rules (content-side)
| ID | Rule | Severity |
|---|---|---|
| S-01 | Content CTAs promise **access to a plan, recipes or routine**, never an outcome. OK: "Comment STRONG and I'll send you the 7-day plan." Block: "Comment STRONG to fix your knees", "…to live longer". | BLOCK |
| S-02 | Any mention of a subscription in content or DM must state the price, billing interval, that it renews, and "cancel online anytime" (ROSCA plus state auto-renewal laws). The cancel flow itself is canonical (OFFER.md): cancel online in at most two screens: one save offer shown next to an equally prominent "Finish canceling" button. Never promise a different number of clicks or screens. | REQUIRE |
| S-03 | No guilt or fear pressure toward purchase: "if you don't join you'll fall", "your family will thank you when you're not in a nursing home". Fear-of-decline hooks may **inform**, never be tied to buying. | BLOCK |
| S-04 | The "gift for your parents" (FAMILY) offer must be clearly a subscription gift with start/end dates. | REQUIRE |

## 9. Checker output format (for the pipeline)
```json
{
  "script_id": "S014",
  "pass": false,
  "blocks": [{"rule": "D-06", "span": "this fixed my knees", "fix": "Remove personal-cure claim; cite E15 instead."}],
  "rewrites": [{"rule": "3.1", "from": "prevents dementia", "to": "is linked with lower risk of memory decline (E37?) — verify evidence ID"}],
  "flags": [{"rule": "3.2", "term": "blood pressure", "evidence_present": true}],
  "required_missing": ["M-03 stop rule"],
  "auto_inserted": ["caption_footer_en", "movement_addon_en"]
}
```

## 10. Checker self-test cases (should BLOCK)
1. "Do this every night and your arthritis will be gone." (3.1, D-06)
2. "My wife put onions in water and her blood pressure dropped instantly." (3.1, D-06)
3. "As a master of qi with 60 years at the temple…" (D-05, D-07)
4. "Frank lost 22 pounds with our club." (T-03)
5. "Hold your breath and push!" (M-04)
6. "5 sit-ups every morning for strong bones." (4.2 spinal_flexion_loaded)
7. "Stop taking your blood pressure pills, try this instead." (3.1)
8. "Take 5 g of creatine and your muscles come back." (Supplement, no dose/claims in general content)
9. "Studies show 90% of seniors…" with no ID (C-04)
10. "Only 3 spots left in the club tonight!" (T-04)

## 11. Should PASS
1. "In a study of 1,702 adults aged 51 to 75, people who couldn't stand on one leg for 10 seconds had higher death rates over seven years. It's a warning sign, not a sentence. Hold the counter and practice." (E09)
2. "Two kiwis a day did as well as prunes for constipation in a small study, with fewer side effects. Go slowly and drink water." (E25)
3. "Wall sits lowered resting blood pressure the most of any exercise type, on average, over weeks of practice. Breathe through it. If your pressure is high, ask your doctor before long holds." (E20)
