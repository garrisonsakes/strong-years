# EVIDENCE APPENDIX: Chang Yin & Sun Yoon content system

Every health statement in HOOKS.md, SCRIPTS.md and the LLM prompts has to trace back to an ID below (E01–E48). The compliance checker (SAFETY_RULES.md, rule C-07) rejects any script that makes a numeric or mechanistic claim without an `evidence:` field pointing to one of these IDs.

How to use this in scripts:
- Say the number the way the study reported it. Put the ID in the evidence note, never on screen. On screen, write the short form, e.g. "Study: 142,861 adults, 17 countries".
- For observational data (cohorts), say "linked with", "people who… tend to…". Never say it "causes" or "adds years". For RCT or Cochrane data, "improved", "reduced" and "helped" are fine.
- Grade codes: **A** = Cochrane review, large meta-analysis of RCTs, or a guideline body. **B** = single good RCT or small meta-analysis. **C** = observational cohort (association only). **D** = mechanistic/physiology or expert consensus. Say C- and D-grade findings with hedges.

Verified via web on 2026-09-30 unless marked "(known literature)".

---

## Strength, muscle, aging

| ID | Finding (what we may say) | Grade | Source |
|---|---|---|---|
| E01 | Progressive resistance training in older adults: 121 RCTs, 6,700 people, 2–3×/week. Large effect on strength (SMD 0.84), moderate-to-large effect on getting out of a chair (SMD −0.94), gait speed +0.08 m/s, less osteoarthritis pain. Most side effects were minor soreness or joint pain. | A | Liu & Latham, Cochrane 2009 — https://www.cochrane.org/evidence/CD002759_progressive-resistance-strength-training-improving-physical-function-older-adults |
| E02 | NSCA position statement: resistance training is safe and effective for older adults, including frail people. Progress gradually. Train 2–3×/week, 1–3 sets of 6–12 reps at 70–85% 1RM once adapted. Include power (fast lifting intent) and balance. | A | Fragala et al., J Strength Cond Res 2019 — https://journals.lww.com/nsca-jscr/fulltext/2019/08000/resistance_training_for_older_adults__position.1.aspx |
| E03 | Ten frail nursing-home residents aged ~90, 8 weeks of high-intensity leg training: strength +174%, thigh muscle area up about 9%, walking speed improved. Muscle still adapts in the 90s. | B (small) | Fiatarone et al., JAMA 1990 — https://pubmed.ncbi.nlm.nih.gov/2342214/ |
| E04 | Around age 75, muscle mass falls about 0.6–1% per year while strength falls 2.5–4% per year. Strength drops 2–5× faster than mass, and losing strength predicts disability and death better than losing mass. | A (review) | Mitchell et al., Frontiers in Physiology 2012 — https://www.frontiersin.org/journals/physiology/articles/10.3389/fphys.2012.00260/full |
| E05 | 10 days of bed rest in healthy adults (mean age 67) cost about 0.95 kg of leg lean mass, with muscle protein synthesis down about 30%. Younger adults lost under 0.4 kg over 28 days. | B | Kortebein et al., JAMA 2007 — https://news.uams.edu/2007/04/25/extended-bed-rest-accelerates-muscle-deterioration-in-older-adults-uams-researchers-report-in-jama/ |
| E06 | Sarcopenia screening cut-offs (EWGSOP2): grip under 27 kg for men or under 16 kg for women, or 5 chair rises taking more than 15 s, signals "probable sarcopenia". | A (consensus) | Cruz-Jentoft et al., Age Ageing 2019 — https://www.esceo.org/sites/esceo/files/pdf/2019%20Age%20Ageing%20EWGSOP2.pdf |
| E21 | Doing 30–60 min/week of muscle-strengthening activity is linked with 10–20% lower all-cause, CVD and cancer mortality (J-shaped curve, no clear benefit above about 1 h). Combined with aerobic activity: about 40% lower all-cause mortality. | C (cohort meta) | Momma et al., BJSM 2022 — https://www.news-medical.net/news/20220301/30-60-minutesweek-of-muscle-strengthening-activities-may-lower-mortality-risk.aspx |
| E29 | LIFTMOR: postmenopausal women with low bone mass did supervised high-intensity resistance plus impact training (2×/week, 8 months). BMD at spine and hip improved and physical function improved. It was supervised and progressed. | B | Watson et al., JBMR 2018 — https://pubmed.ncbi.nlm.nih.gov/28975661/ |
| E38 | Creatine taken during resistance training in older adults gave greater gains in lean mass and some strength measures than training alone. Future upsell topic only. Say "ask your doctor first", especially with kidney disease. | A− (meta) | Chilibeck et al., OAJSM 2017 — https://pubmed.ncbi.nlm.nih.gov/29138605/ |
| E39 | High-velocity "power" training (lift with fast intent, lower slowly) gives functional gains similar to or slightly better than traditional training in older adults, and it is safe when supervised and progressed. | A− | J Physiotherapy 2023 systematic review — https://www.sciencedirect.com/science/article/pii/S183695532300053X ; Eur Rev Aging Phys Act 2022 — https://link.springer.com/article/10.1186/s11556-022-00297-x |
| E42 | AHA scientific statement (2023): resistance training is recommended for adults with and without cardiovascular disease. It lowers blood pressure and improves glucose control and function. Avoid breath-holding (Valsalva). People with CVD should get individualized clearance. | A (statement) | Paluch et al., Circulation 2024 — https://www.ahajournals.org/doi/10.1161/CIR.0000000000001189 |

## Functional tests (the "Can you do this?" engine)

| ID | Finding | Grade | Source |
|---|---|---|---|
| E07 | PURE study: 142,861 adults in 17 countries. Every 5 kg lower grip strength was linked with 16% higher all-cause mortality and 17% higher CV mortality. Grip predicted mortality better than systolic blood pressure. | C | Leong et al., Lancet 2015 — https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(14)62000-6/abstract ; summary https://www.consultant360.com/exclusives/could-grip-strength-predict-all-cause-mortality-risk |
| E08 | Sitting-rising test (sit to the floor and stand up without support; score 0–10, lose 1 point per hand/knee support). 2,002 adults aged 51–80. The lowest scorers (0–2) had 5–6× the death risk of the highest (8–10). Each +1 point was linked with 21% lower mortality. | C | Brito, Araújo et al., Eur J Prev Cardiol 2012/2014 — https://www.sciencedaily.com/releases/2012/12/121213085202.htm |
| E09 | 10-second one-leg stance (free foot resting on the back of the other calf, arms at sides, 3 tries). 1,702 people aged 51–75. Failing it was linked with 84% higher all-cause mortality over about 7 years. Failure rates: about 18% at 61–65, about 37% at 66–70, over 50% at 71–75. | C | Araújo et al., BJSM 2022 — https://www.bristol.ac.uk/news/2022/june/tne-second-one-legged-stance.html |
| E10 | Gait speed and survival: 34,485 adults 65+. 0.8 m/s is around median life expectancy. ≥1.0 m/s was linked with longer-than-expected survival. Under 0.6 m/s means higher risk. | C | Studenski et al., JAMA 2011 — https://www.sciencedaily.com/releases/2011/01/110104161621.htm |
| E11 | CDC STEADI 30-second chair stand (17-inch chair, arms crossed). Below-average scores that signal fall risk: men 60–64 <14, 65–69 <12, 70–74 <12, 75–79 <11, 80–84 <10, 85–89 <8, 90–94 <7. Women 60–64 <12, 65–69 <11, 70–74 <10, 75–79 <10, 80–84 <9, 85–89 <8, 90–94 <4. If they use their arms to stand, the score is 0. | A (tool) | CDC STEADI — https://www.cdc.gov/steadi/media/pdfs/STEADI-Assessment-30Sec-508.pdf |

## Balance & falls

| ID | Finding | Grade | Source |
|---|---|---|---|
| E12 | Exercise and falls: 108 RCTs, 23,407 people. Exercise cut the rate of falls by about 23%. Balance and functional exercise alone: about 24%. Multiple types (balance + resistance): about 34%. Tai chi: about 19% (lower certainty). | A | Sherrington et al., Cochrane 2019 — https://www.cochrane.org/evidence/CD012424_exercise-preventing-falls-older-people-living-community |
| E13 | Otago Exercise Programme (home-based leg strength, balance, walking): 7 trials, 1,503 people, mean age 81.6. Falls down about 32% (RR 0.68). Deaths down in the trial period (RR 0.45, interpret with caution). | A− | Thomas et al., Age Ageing 2010 — https://www.ncbi.nlm.nih.gov/books/NBK78898/ |
| E14 | Tai Ji Quan: Moving for Better Balance. 670 adults 70+ (mean 77.7) at high fall risk, 24 weeks, 2×60 min/week. Falls were 58% lower than stretching (IRR 0.42) and 31% lower than multimodal exercise (IRR 0.69). | B+ | Li et al., JAMA Intern Med 2018 — https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/2701631 |
| E36 | USPSTF: exercise interventions are recommended for community-dwelling adults 65+ at increased fall risk (Grade B, 2024). Vitamin D supplementation is **not** recommended to prevent falls in community-dwelling older adults (2024–25). | A (guideline) | USPSTF — https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/falls-prevention-community-dwelling-older-adults-interventions ; https://www.healio.com/news/primary-care/20241217/uspstf-advises-against-vitamin-d-supplementation-to-prevent-falls-in-older-adults |
| E45 | Getting-up-from-the-floor strategies can be taught to older adults. Practice it before you ever need it (backward chaining: kneel → half-kneel → stand, using sturdy furniture). | B (known literature) | Hofmeyer et al., J Am Geriatr Soc 2002 (floor-rise strategy training) |

## Mobility, pain, tai chi, qigong, yoga

| ID | Finding | Grade | Source |
|---|---|---|---|
| E15 | Tai chi vs physical therapy for knee osteoarthritis: 204 adults. Similar improvements in pain and function at 12 weeks, sustained to 52 weeks. Tai chi group had more improvement in depression and quality of life. | B+ | Wang et al., Ann Intern Med 2016 — https://www.nccih.nih.gov/research/research-results/study-shows-tai-chi-and-physical-therapy-were-equally-helpful-for-knee-osteoarthritis |
| E30 | Exercise for chronic low back pain: 249 trials, 24,486 people. Pain about 15 points better (0–100 scale) at 3 months vs no treatment or usual care. Function improved modestly. | A | Hayden et al., Cochrane 2021 — https://www.cochrane.org/evidence/CD009790_exercise-treatment-chronic-low-back-pain |
| E30b | Yoga for chronic non-specific low back pain gives small-to-moderate improvements in function vs no exercise. | A | Wieland et al., Cochrane 2022 — https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD010671.pub3 |
| E17 | Baduanjin/qigong in older adults: meta-analyses report better sleep quality and fewer depressive symptoms (moderate certainty, heterogeneous trials). | A− | Frontiers Public Health 2026 meta-analysis — https://pmc.ncbi.nlm.nih.gov/articles/PMC13501274/ ; qigong & sleep meta — https://pmc.ncbi.nlm.nih.gov/articles/PMC12757222/ |
| E41 | Pain-monitoring model: during and after exercise, pain up to about 3/10 (we use a conservative threshold) is acceptable if it settles by the next morning and isn't trending up week to week. | B (known literature) | Thomeé, Phys Ther 1997; Silbernagel et al., Am J Sports Med 2007 |
| E40 | Osteoporosis exercise guidance: do resistance and balance training. Avoid rapid, repeated or loaded spinal flexion (sit-ups, toe-touches with weight) and forceful twisting. Flexion-exercise programs were linked with more vertebral fractures. | A (consensus) | Giangregorio et al., "Too Fit To Fracture", Osteoporos Int 2014 — https://link.springer.com/10.1007/s00198-014-2881-4 ; Sinaki & Mikkelsen, Arch Phys Med Rehabil 1984 |
| E31 | Pelvic floor muscle training for urinary incontinence in women: PFMT groups were far more likely to report cure or improvement. For stress incontinence, about 8× more likely to report cure than controls. | A | Dumoulin et al., Cochrane 2018 — https://www.cochrane.org/evidence/CD005654_pelvic-floor-muscle-training-urinary-incontinence-women |

## Breath, nervous system, sleep

| ID | Finding | Grade | Source |
|---|---|---|---|
| E18 | 111 adults, 5 min/day for 1 month. Cyclic sighing (two inhales through the nose, long slow exhale through the mouth) produced the largest daily improvement in positive mood, more than mindfulness meditation. All breathing groups improved. | B | Balban et al., Cell Reports Medicine 2023 — https://stanmed.stanford.edu/cyclic-sighing-stress-relief/ |
| E19 | Voluntary slow breathing (around 6 breaths/min) increases vagally-mediated heart-rate variability during and after practice. | A− (meta) | Laborde et al., Neurosci Biobehav Rev 2022 — https://www.sciencedirect.com/science/article/abs/pii/S0149763422002007 |
| E16 | Older adults with insomnia: tai chi chih improved sleep. CBT-I (the first-line treatment) was stronger. Both reduced inflammatory markers. | B | Irwin et al., SLEEP 2014 — https://academic.oup.com/sleep/article-abstract/37/9/1543/2416985 |

## Blood pressure, glucose, walking

| ID | Finding | Grade | Source |
|---|---|---|---|
| E20 | Exercise and resting BP: 270 RCTs, 15,827 people. Isometric training lowered BP the most (−8.24/−4.00 mmHg). Wall squat ranked top for systolic. Aerobic −4.49/−2.53, dynamic resistance −4.55/−3.04. These are average changes over weeks of training, **not instant**. | A | Edwards et al., BJSM 2023 — https://bmjgroup.com/static-isometric-exercise-such-as-wall-sits-best-for-lowering-blood-pressure/ |
| E22 | Daily steps: in adults 60+, mortality benefit plateaued at about 6,000–8,000 steps/day. The top quartiles had 40–53% lower risk than the lowest (about 3,500/day). | C | Paluch et al., Lancet Public Health 2022 — https://www.sciencedaily.com/releases/2022/03/220303112207.htm |
| E23 | Light walking after meals (even 2–5 minutes) lowers the post-meal glucose rise compared with sitting. | A− (meta) | Buffey et al., Sports Med 2022 — https://pubmed.ncbi.nlm.nih.gov/35147898/ |
| E35 | Salt substitute (25% potassium chloride) in 20,995 older adults at high risk: stroke, major CV events and death were all reduced. **Caution:** potassium salt isn't for people with kidney disease or on potassium-raising medicines. Always say "ask your doctor first". | B+ | Neal et al., NEJM 2021 (SSaSS) — https://www.nejm.org/doi/full/10.1056/NEJMoa2105675 |

## Digestion, kitchen, protein

| ID | Finding | Grade | Source |
|---|---|---|---|
| E24 | Fiber: 25–29 g/day was linked with 15–30% lower all-cause and CV mortality, type 2 diabetes and colorectal cancer. More fiber was linked with more benefit. | A (meta of cohorts + RCTs) | Reynolds et al., Lancet 2019 — https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(18)31809-9/fulltext |
| E25 | Chronic constipation: 2 green kiwifruit/day vs 100 g prunes vs 12 g psyllium, 4 weeks, 75 patients. All three improved bowel movements similarly. Kiwi had the fewest side effects and highest satisfaction, and improved bloating. | B (exploratory) | Chey et al., Am J Gastroenterol 2021 — https://www.healio.com/news/gastroenterology/20210608/kiwi-fruit-effectively-relieves-symptoms-in-chronic-constipation |
| E26 | 36 adults, 10 weeks. A high-fermented-food diet (yogurt, kefir, kimchi, sauerkraut, kombucha; intake rose to about 6 servings/day by the end) increased microbiome diversity and lowered 19 inflammatory proteins (including IL-6). The high-fiber arm didn't show those changes over 10 weeks. | B (small) | Wastyk et al., Cell 2021 — https://med.stanford.edu/news/all-news/2021/07/fermented-food-diet-increases-microbiome-diversity-lowers-inflammation.html |
| E27 | Prune Study: postmenopausal women eating 50 g prunes/day (about 5–6) preserved total hip BMD over 12 months vs controls. | B | De Souza et al., Am J Clin Nutr 2022 — https://pmc.ncbi.nlm.nih.gov/articles/PMC9193411/ |
| E28 | PROT-AGE: adults over 65 should get 1.0–1.2 g protein/kg/day, and 1.2–1.5 g/kg if active or ill (unless there is severe kidney disease). Aim for 25–30 g per meal with about 2.5–2.8 g leucine. | A (consensus) | Bauer et al., JAMDA 2013 — https://pubmed.ncbi.nlm.nih.gov/23867520/ |
| E32 | Honey improved upper-respiratory-infection symptoms, especially cough frequency and severity, compared with usual care. **Never give honey to infants under 12 months.** | A− | Abuelgasim et al., BMJ Evid Based Med 2021 — https://www.phc.ox.ac.uk/news/honey-better-than-usual-care-for-easing-respiratory-symptoms-especially-cough |
| E33 | Ginger for osteoarthritis pain: small effect vs placebo, with more GI complaints. Say it "may help a little". Ginger for nausea has reasonable support. It can interact with blood thinners at supplement doses. | A− | Bartels et al., Osteoarthritis Cartilage 2015 — https://www.oarsijournal.com/article/S1063-4584(14)00641-4/fulltext ; ginger umbrella review AJCN 2022 — https://ajcn.nutrition.org/article/S0002-9165(22)00277-5/fulltext |
| E34 | Enteric-coated peppermint oil improved global IBS symptoms and abdominal pain vs placebo. It can worsen reflux. | A− | Alammar et al., BMC Complement Altern Med 2019 — https://link.springer.com/article/10.1186/s12906-018-2409-0 |

## Social connection & mindset

| ID | Finding | Grade | Source |
|---|---|---|---|
| E37 | 148 studies, 308,849 people. Stronger social relationships were linked with a 50% higher likelihood of survival (OR 1.50), comparable to well-known risk factors like smoking. | C (meta of cohorts) | Holt-Lunstad et al., PLoS Med 2010 — https://journals.plos.org/plosmedicine/article?id=10.1371%2Fjournal.pmed.1000316 |
| E43 | Pre-exercise screening (ACSM 2015): anyone with symptoms of cardiovascular, metabolic or renal disease (chest pain, unusual breathlessness, fainting) should get medical clearance before starting. Otherwise, light-to-moderate exercise can begin and progress. | A (guideline) | Riebe et al., Med Sci Sports Exerc 2015 (known literature) |
| E44 | Yang Mun criticism record: deception about being real ("My number one concern is that this is a lie"), religious appropriation of clergy trust, Orientalist "misty mountain" imagery, AI-generated reviewer photos, monetizing sacred practice. | Press | Columbia News Service 2026 — https://columbianewsservice.com/2026/03/24/millions-found-comfort-in-a-buddhist-monk-but-he-was-never-real/ ; EBU Spotlight — https://spotlight.ebu.ch/p/yang-mun-ai-influencer-scam ; America Magazine Aug 2026 — https://www.americamagazine.org/news/2026/08/31/ai-chatbots-religious-teachers/ |


## Safety physiology (added for scripts)

| ID | Finding | Grade | Source |
|---|---|---|---|
| E46 | Orthostatic hypotension (a blood-pressure drop on standing) is common in older adults. A meta-analysis found it in about 22% of community-dwelling older people. The risk is higher with some blood-pressure and other medicines. Practical rule: sit, pump your ankles, then stand slowly while holding something. | A− (meta, known literature) | Saedon et al., J Gerontol A Biol Sci Med Sci 2020 (prevalence of orthostatic hypotension, systematic review & meta-analysis) |
| E47 | The calf muscle pump: calf contraction compresses the deep veins and, with the venous valves, pushes blood back toward the heart. It's standard physiology. Walking and heel raises activate it. A red flag is one swollen, red, painful calf (possible clot), which needs a doctor, not exercise. | D (physiology) | Standard physiology texts; e.g. Recek, Int J Angiol 2013 "Calf pump activity influencing venous hemodynamics in the lower extremity" (known literature) |
| E48 | Adults with loud snoring plus witnessed pauses in breathing, gasping or daytime sleepiness should get a clinical evaluation for obstructive sleep apnea. Breathing exercises aren't a substitute. | A (guideline, known literature) | Kapur et al., AASM Clinical Practice Guideline, J Clin Sleep Med 2017 |

---

## Things we deliberately DO NOT claim (common viral remedies with no competent evidence)
Use these as **myth-bust ammunition** (pillar P15). Never present them as remedies.
- Onion in water, salt under feet, bay leaves under feet, cabbage leaves on the back "for any pain", potato in socks. There's no evidence of systemic benefit. At best cabbage leaves are a folk compress used for breast engorgement, with mixed evidence.
- "Lower blood pressure instantly" tricks. Slow breathing can transiently reduce BP (E19), but resting BP changes come from weeks of training (E20) and from diet and medication managed by a doctor.
- Liver/colon "cleanses" and "detox" drinks. The liver and kidneys do this job. There's no competent evidence for products that claim to help.
- "Burn sugar after dinner" drinks. The post-meal walk has evidence (E23); drinks don't.
- Vitamin D to prevent falls in healthy community-dwelling adults (E36 says no). Exercise has the evidence (E12–E14).
- "Coconut water + olive oil + lime for back pain" (a Yang Mun example). No evidence. Exercise has it (E30).

## Evidence refresh protocol
- Monthly: [ONLY PUBLISH ONCE A SIGNED, CREDENTIALED REVIEWER EXISTS: the reviewer (licensed PT and RD on retainer)] FALLBACK: "our team (no credential claim until a reviewer signs)" re-checks the top 20 claims in use and adds new ones as E46+.
- Each new ID needs the grade, exact numbers, a URL, and a "how to say it" line.
- A claim with grade C or D may never be the *only* support for a CTA promise (e.g. "join to live longer" is banned; "join to follow the 7-day strength plan" is fine).

## Paid products additions (E49–E58, added 2026-09-30 for /products)

Status key: **opened** = the source page or file was fetched and read on 2026-09-30. **Unverified** = cited from known literature, not opened in this pass.

| ID | Finding (what we may say) | Grade | Source |
|---|---|---|---|
| E49 | Senior Fitness Test (Rikli & Jones): 7,183 US community-dwelling adults aged 60–94 from 267 sites in 21 states. "Normal range" = the middle 50% (25th–75th percentile) for each 5-year age band and sex. 30-s chair stand, 30-s arm curl (5 lb women / 8 lb men), 2-minute step test (right-knee lifts to midway between kneecap and hip bone), chair sit-and-reach (inches, + past the toes / − short of them). Example normal ranges, women 70–74: chair stand 10–15, arm curl 12–17, step test 68–101, sit-and-reach −1.0 to +4.0 in; men 70–74: 12–17, 14–21, 80–110, −3.5 to +2.5 in. Full tables in products/strength_reset.md. It's a fitness comparison, not a diagnosis. | A (tool/norms) | Rikli & Jones, Senior Fitness Test Manual, 2nd ed. 2013 (primary not opened). **Opened:** normative tables — https://integrativephysicaltherapyservices.com/wp-content/uploads/2023/08/Fitness-Testing-for-Seniors-PDF.pdf ; protocol + sample size — https://fitnessnorms.com/functional/chair-sit-and-reach/ , https://fitnessnorms.com/functional/step-test/ , https://fitnessnorms.com/functional/arm-curl/ . Note: the PDF's women 60–64 sit-and-reach cell reads "−0.5 to +0.5" (typo); we use the fitnessnorms 25th–75th percentiles (−0.6 to +4.8 in). |
| E50 | CDC STEADI 4-Stage Balance Test: feet side by side, semi-tandem (instep beside big toe), tandem (heel to toe), one leg; up to 10 s each, stop at the first stage not held. "An older adult who cannot hold the tandem stand for at least 10 seconds is at increased risk of falling." | A (tool) | CDC STEADI — **opened** https://www.cdc.gov/steadi/media/pdfs/STEADI-Assessment-4Stage-508.pdf |
| E51 | CDC STEADI Timed Up and Go: stand from a chair, walk 10 feet (3 m) at normal pace, turn, walk back, sit. "An older adult who takes ≥12 seconds to complete the TUG is at risk for falling." Always have someone stand by. | A (tool) | CDC STEADI — **opened** https://www.cdc.gov/steadi/media/pdfs/STEADI-Assessment-TUG-508.pdf |
| E52 | USDA FoodData Central, SR Legacy (April 2018 release): per-100 g energy, protein, total dietary fiber, sodium and leucine used for every recipe calculation in Sun Yoon's Strong Kitchen (FDC IDs listed per ingredient in the book's method appendix). | A (reference database) | **Opened/downloaded** https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip |
| E53 | Label values for two Korean pastes not in SR Legacy, per 100 g: Sempio gochujang (barcode 8801005000178) 233 kcal, 5.0 g protein, 2.7 g fiber, 2,640 mg sodium; Obok chunjang (8801126032447) 200 kcal, 20 g protein, 0 g fiber, 3,200 mg sodium (single crowd-sourced label; protein looks high, so treat as approximate). | D (label data) | Open Food Facts API — **opened** https://world.openfoodfacts.org/product/8801005000178 , https://world.openfoodfacts.org/product/8801126032447 |
| E54 | Safe minimum internal temperatures: ground meat 160°F; beef/pork steaks, chops, roasts 145°F + 3-minute rest; all poultry 165°F; fish 145°F or until opaque and flaking; shrimp until pearly/opaque; clams until shells open; eggs until yolk and white are firm; egg dishes 160°F; leftovers 165°F. | A (federal guidance) | FoodSafety.gov — **opened** https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures |
| E55 | Adults 65+ are at higher risk of foodborne illness (weaker immune response, slower gut transit, less stomach acid, reduced liver and kidney clearance). | A (federal guidance) | FoodSafety.gov — **opened** https://www.foodsafety.gov/people-at-risk/older-adults |
| E56 | Water gargling RCT (Japan): 387 healthy volunteers aged 18–65, 60 days. Gargling plain water daily was linked with 36% fewer upper-respiratory infections vs usual care; povidone-iodine gargle showed no significant difference. No sham/placebo arm (critics note possible bias). Not studied in adults over 65. | B− (single RCT, unblinded) | Satomura et al., Am J Prev Med 2005 (primary abstract page returned 403: **primary not opened, unverified**). **Opened** secondary report: https://www.infectioncontroltoday.com/view/gargling-may-prevent-colds-expert-finds-results-hard-swallow |
| E57 | Chicken soup slowed white-blood-cell (neutrophil) movement in a lab dish. The authors state clinical benefit "remains untested". Lab evidence only: tradition, enjoy it as food. | D (in vitro) | Rennard et al., Chest 2000 — **opened** https://www.unmc.edu/strategic-communications/for-the-media/press-kits/files/chickensouppublishedstudy2000.pdf |
| E58 | Seaweed iodine varies enormously: commercially available seaweeds measured 16 to 2,984 mcg iodine per gram. Adult upper limit 1,100 mcg/day from all sources. People with autoimmune thyroid disease may have adverse effects at intakes considered safe for others. | A (NIH fact sheet) | NIH Office of Dietary Supplements — **opened** https://ods.od.nih.gov/factsheets/Iodine-HealthProfessional/ , https://ods.od.nih.gov/factsheets/Iodine-Consumer/ |
| E59 | Exercise for hand osteoarthritis (Cochrane): 7 trials, 534 people, mostly women. After a hand-exercise programme, pain was 0.5 points lower (0–10), function 2.2 points better (0–36) and finger stiffness 0.7 points lower (0–10). Small effects, low or very low certainty, not sustained at medium- and long-term follow-up. The few adverse events were more finger-joint inflammation and hand pain. Say "may help a little with stiffness and hand use", never "fixes arthritis". | A (Cochrane, low certainty) | Østerås et al., Cochrane 2017 — **opened** https://www.cochrane.org/CD010388/MUSKEL_exercise-hand-osteoarthritis |
| E60 | WalkBack RCT: 701 adults who had recently recovered from an episode of low back pain. An individualised, progressive walking program plus six physiotherapist-guided education sessions over 6 months: median 208 days before a recurrence vs 112 days in the no-intervention group; healthcare visits and work absence roughly halved. Say "people who walked… went longer before their back pain came back", never "walking prevents back pain". Not an older-adult-only sample. | B+ (single large RCT) | Pocovi et al., Lancet 2024 — **opened** summary https://www.sciencedaily.com/releases/2024/06/240620152321.htm (primary: https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(24)00755-4/fulltext, not opened) |
