# Chang & Sun workers

Python 3.11 + FastAPI services that `n8n_core_workflow.json` calls. One image serves every endpoint. Deploy it as the render worker (`RENDER_WORKER_URL`) and the QA worker (`QA_WORKER_URL`), or run a single instance for both.

```
make install-dev   # pip deps (system deps: ffmpeg with libflite + chromaprint, tesseract-ocr)
make test          # full suite: renders synthetic audio/video, ~4–5 min
make test-fast     # compliance, packaging, workflow contract, growth (no rendering)
make test-growth   # growth engine only (adapters, scoring, actions, allocator, governor property tests, API, workflow)
make test-sql      # schema.sql + schema_growth.sql on local Postgres 16 (or PGTEST_DSN)
make sample        # end-to-end sample video -> out/sample/
make serve         # uvicorn app:app on :8080
make docker        # image built from the rebuild/ root so the spec files ship with it
```

## Endpoints

| Path | n8n node | What it does |
|---|---|---|
| `POST /voice/stitch` | Worker: Stitch & Segment Voice | Joins the per-line ElevenLabs files with gaps and turns the character alignment into word timings (`[tags]` dropped). Cuts per-shot WAVs for InfiniteTalk, with separate Chang and Sun tracks for `speaker: both`. |
| `POST /assemble` | Worker: Assemble Master | Takes the manifest from *Build Assembly Manifest* and renders a 1080×1920, 30 fps, H.264 High master with AAC 48 kHz audio, loudness-normalised to −14 LUFS (−1.5 dBTP). Burned-in word-by-word captions use Figtree ExtraBold at 52–64 px, white text with a yellow active word on a near-black pill, inside the safe zones. The "AI character" tag sits top-left (D-02). Also handles hook/emphasis text, PiP insets (top-right), study cards (lower-left, citation looked up in EVIDENCE.md), and a music bed ducked under the voice with sidechain compression. Signs C2PA (`trainedAlgorithmicMedia`) and returns the pHash sequence, audio fingerprint, 12 QA frames, the transcript and every burned-in string. It also writes a `_clean` mezzanine without the script hook, which the variants are rendered from. |
| `POST /variants` | Worker: Render Platform Variants | Burns the platform hook into that platform's safe zone, trims to `max_s`, makes a cover with the cover text and re-signs C2PA. |
| `POST /qa`, `POST /qa/score` | Worker: Deterministic QA | Checks spec (ffprobe), EBU R128 loudness and true peak, black and freeze frames (freezes inside `graphic` shots are ignored), duration bounds, and C2PA presence. Runs tesseract OCR on the captions (character error rate against the script, plus a number check) and on the AI tag. ArcFace and SyncNet hooks skip when their models are absent. Returns metrics, a decision and a route (`auto` / `approval` / `regen` / `human`), using the same bands as prompts/07 and the *Decide QA Route* node. |
| `POST /compliance/scan` | Worker: Compliance Scan (new) | Deterministic checker for pass 1 (script JSON) and pass 2 (packaging, transcript and burned-in text). Covers blocked_claims.json, the SAFETY_RULES §3.1 regexes, identity/credential/clergy rules, testimonials and scarcity, movement safety (M-01…M-07, §4.2 tags), food cautions (§5), red flags (§4.3), evidence (C-01/C-04/C-07), the reviewer gate (§7), and disclosure: footer, movement add-on, AI tag, `is_aigc`, `containsSyntheticMedia`, no links on X. Myth-bust exception candidates are passed to the LLM judge. Paid-ad JSON (`ad_scripts.json`: hooks, body VO/on-screen, primary text, headline, end cards, offer lines) is scanned field by field. "Guarantee" passes only as the refund-policy phrase "14-day money-back guarantee" / "money-back guarantee" (SAFETY_RULES CX-GUAR, BC14/BC23); next to a health outcome it blocks. `judge: true` also calls prompts/03 via the Anthropic API. |
| `POST /compliance/judge`, `GET /compliance/selftest` | – | LLM judge only (skipped with `status: skipped` when there's no `ANTHROPIC_API_KEY`), and the §10–11 self-test. |
| `POST /uniqueness/check`, `POST /uniqueness/fingerprint` | Worker: Uniqueness Guard (new) | Allow or deny against sibling pages (PIPELINE §2.3). Checks TF-IDF cosine (0.86 same page, 0.80 network), MinHash Jaccard, more than 6 shared consecutive words (safety and CTA lines excepted), pHash (more than 40% of seconds within Hamming distance 10), Chromaprint audio (spectral-hash fallback), and the 48 h / different-slot-hour stagger. Fetches siblings from Supabase when `siblings` is omitted. |
| `POST /package` | Worker: Package + Pass 2 (new) | Normalises the LLM packaging: appends the exact footer (reviewer-gated) with the movement add-on before it, forces AI flags, applies length and hashtag limits, removes banned tags, strips links from X, and rewrites the CTA where no DM automation exists (TikTok US, YouTube). Builds UTM + `pid` links for bio and DM, then runs compliance pass 2. |
| `POST /growth/metrics/normalize`, `POST /growth/metrics/fetch` | Growth: Normalize Metrics | Raw platform insight payloads (IG/FB Graph, TikTok, YouTube Analytics, Threads, X) or already-canonical captures → `post_metrics` snapshots at 1 h / 3 h / 6 h / 24 h / 72 h, with DB rollups (keyword comments, opt-ins, ebook buyers, members). `/fetch` pulls live insights only with `GROWTH_LIVE_METRICS=1`, under the same SSRF policy as media fetches (`METRICS_ALLOWED_HOSTS`). |
| `POST /growth/baselines`, `POST /growth/score` | Growth: Baselines, Growth: Score | Rolling per-page × platform × horizon baselines (median/MAD, empirical-Bayes shrinkage toward the network or cold-start prior) and the composite velocity score with class WINNER / PROMISING / NORMAL / LOSER and the bandit reward. PIPELINE §7.5. |
| `POST /growth/actions` | Growth: Winner Actions | Queued jobs only: remix requests for other pages (uniqueness thresholds attached, YouTube July-2026 limits), boost candidates re-checked under the stricter ad policy + mandatory judge (pass → awaiting a human; flagged or unjudged → human), pin suggestions, LOSER down-weights. |
| `POST /growth/allocate` | Growth: Allocate Slots | Thompson sampling over pillar × grammar × format × speaker × length per page/platform → tomorrow's slot plan for `tools/build_content.py`. 20% exploration floor (hard), 14-day decay, cadence ≤ 9, pillar and grammar constraints, running bits. |
| `POST /growth/governor/plan`, `POST /growth/governor/execute`, `GET /growth/governor/audit`, `GET /growth/config` | Growth: Governor Plan (dry run) | The spend governor: a deterministic plan (boosts → retargeting → cold) inside the approved daily / monthly / cash-floor envelope, BLITZ §9 lines (price-aware) and the §11 graduation gate, with an append-only hash-chained audit log. `execute` is a stub that refuses unless `SPEND_ENABLED=1`, `GROWTH_DRY_RUN=0` and a human approval is bound to the plan's `state_hash`, and even then calls no ad API. |
| `GET /health`, `GET /health/details`, `GET /files/*` | – | `/health` is an unauthenticated liveness probe (`{"ok": true}` only). `/health/details` (authenticated) is the capability report. `/files` serves local outputs when R2 isn't configured; it's authenticated unless `PUBLIC_FILES=1` and confined to `OUTPUT_DIR`. |

`n8n_growth_workflow.json` (44 nodes: hourly metrics → score → winner actions; nightly allocator → governor dry run → Slack approval) calls the `/growth/*` endpoints through `QA_WORKER_URL`; `tests/test_growth_workflow.py` checks the same contract for it.

`python -m tools.patch_workflow` idempotently wires the three new nodes into `../n8n_core_workflow.json` and updates *Parse Verdict*, *Build QA Vision Request*, *Decide QA Route* and *Build Variant & Post Rows* to read them. `tests/test_workflow.py` checks that every worker URL in the workflow is served, that the connections resolve, and that the patched Code nodes parse and behave correctly on mock data under node.

## CLI

```
python -m compliance selftest
python -m compliance scan ../data/content/scripts.json ../data/content/ad_scripts.json [--judge] [--json out/report.json] [--strict]
python -m compliance text "Detox tea melts belly fat"
python -m compliance templates ../app/content/lifecycle/sequences.json dm/flows/*.json   # every customer-facing string must pass
```

Ops round: `dm/` (Instagram/Messenger keyword → DM bot, Meta-signature webhook at `/dm/webhook`, `APP_REVIEW.md`), `packager/fallback.py` (`POST /package/fallback`, manual post pack), `growth/approvals.py` (`POST /growth/approvals/boost`, `GET /growth/summary`) and `common/exceptions.py` (posts to the members app's `/api/exceptions` when `APP_URL` + `EXCEPTIONS_API_TOKEN` are set; used by the compliance human route, the uniqueness guard and the governor).

## Environment

| Var | Purpose |
|---|---|
| `SPEC_DIR` | Folder holding SAFETY_RULES.md, EVIDENCE.md, prompts/ and n8n_core_workflow.json. Defaults to the parent of `workers/`. |
| `OUTPUT_DIR`, `WORK_DIR`, `PUBLIC_BASE_URL` | Local outputs, served under `/files` |
| `R2_ENDPOINT`, `R2_BUCKET`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_PUBLIC_BASE` | Upload outputs to R2 instead |
| `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` | Register master and variant rows in `assets` (FK targets for `videos` and `variants`), resolve library `asset_id`s, fetch sibling fingerprints |
| `WORKER_TOKEN` | **Required.** Callers send `X-Worker-Token` (the n8n credential) or an HMAC signature (`X-Worker-Timestamp`, `X-Worker-Signature: sha256=HMAC(token, ts + "." + body)`). Without it every endpoint answers 503. `DEV_NO_AUTH=1` disables auth for local development only. |
| `FETCH_ALLOWED_HOSTS`, `MAX_FETCH_BYTES`, `FETCH_TIMEOUT_S`, `LOCAL_MEDIA_ROOTS` | Media fetch policy: https only, allow-listed hosts (a leading `.` matches subdomains; the R2 and `PUBLIC_BASE_URL` hosts are always added), public IPs only, redirects re-checked, byte and time caps, and media containers only (no playlists). Local paths are accepted only under `OUTPUT_DIR`, `WORK_DIR` or `LOCAL_MEDIA_ROOTS`. |
| `REQUIRE_JUDGE`, `JUDGE_TIMEOUT_S` | The LLM judge is mandatory (`REQUIRE_JUDGE=1`, the default). Without `ANTHROPIC_API_KEY`, or on error, timeout (default 60 s) or unparsable output, the final verdict is `human`. Set it to `0` only for offline reports. |
| `SPEND_ENABLED`, `GROWTH_DRY_RUN` | Growth spend switches, env-only (a request can't change them). Defaults `0` / `1`: governor plans are advisory and the executor refuses. There is no ad API client in this codebase, so even `1` / `0` plus a human approval only records the plan. |
| `GROWTH_LIVE_METRICS`, `METRICS_ALLOWED_HOSTS` | `0` by default: the metrics adapters parse fixtures or payloads n8n pushes. With `1`, `/growth/metrics/fetch` may call the platform analytics APIs, https only, exact-host allow-list (Graph, Threads, TikTok, YouTube Analytics, X), public IPs, no redirects, 2 MB cap, bearer token in the header only. |
| `GROWTH_CONFIG_PATH`, `GROWTH_AUDIT_PATH` | JSON deep-merged over `growth/config.DEFAULTS` (thresholds, caps, weights; validated: the 20% exploration floor can't go lower). The governor's audit JSONL (default `OUTPUT_DIR/growth/governor_audit.jsonl`). |
| `REVIEWER_SIGNED` | `1` only once a credentialed reviewer has signed (SAFETY §7). This is the **only** switch for "reviewed by…" wording; request fields are ignored. |
| `ANTHROPIC_API_KEY`, `MODEL_JUDGE` | LLM compliance judge (defaults to claude-opus-5-5) |
| `C2PA_SIGN_CERT`, `C2PA_PRIVATE_KEY`, `C2PA_TSA_URL`, `C2PA_ALLOW_DEV_CERT` | Production C2PA signer. `C2PA_ALLOW_DEV_CERT` defaults to `0`: without a certificate, masters ship unsigned and QA holds them at `review`. With `1` (dev and tests), a throwaway dev CA signs, and QA marks the result `c2pa_trusted: false`. Neither case can auto-publish. |
| `X264_PRESET`, `CAPTION_FONT`, `SITE_BASE_URL`, `INSIGHTFACE_HOME` | Tuning |

## What still needs real keys or models

- **C2PA:** a signing certificate from a CA on the C2PA trust list. Until then the dev certificate produces a valid but untrusted manifest.
- **LLM judge:** needs `ANTHROPIC_API_KEY`. Without it, any myth-bust exception candidate goes to a human.
- **ArcFace:** needs `pip install -r requirements-optional.txt`, the buffalo_l model and the character reference images.
- **SyncNet:** a GPU QA worker still needs to be built; this worker only reports it as skipped.
- **R2 and Supabase:** credentials are needed for public URLs and asset rows. The sibling query's embedding names are **[A]**.
- **Transcript:** currently taken from the TTS alignment, which is the exact voiced text. A true ASR pass (Scribe/Whisper) is a TODO for pass 2 on third-party audio.
- **Font:** Figtree (OFL), from google/fonts on GitHub. `fonts/Figtree-ExtraBold.ttf` is the wght=800 instance of `Figtree[wght].ttf`.
- **Naming:** the packaging module lives in `packager/`, because a local `packaging/` package would shadow PyPI `packaging`, which pytest itself imports.

## Growth engine: what it will never do

`workers/growth/` scores, queues, plans and logs. It does not publish, spend, create accounts, contact anyone or fake engagement, and its tests prove the caps: `tests/test_growth_governor.py` runs 3,000 random states (hostile and well-formed) plus an exhaustive envelope grid through `governor.decide` and checks the invariants (planned spend ≤ every cap, boosts only for WINNER + compliance pass + judge + named human approval, cold only after the §11 gate and never more than +20%/day, bad input → zero plan, identical input → identical plan). `schema_growth.sql` backs the same rules in Postgres: `boost_queue` can't hold an `approved` row without a passing judge and a named human, `spend_ledger` refuses a day above the approved daily cap and is append-only together with `governor_decisions`, for every role.

Thresholds the client should confirm (all in `growth/config.py`, marked `[A]` or `[C]`): winner score 1.5 at 6 h / 1,000 views, loser −1.0 at 24 h, breakout 500K views; 3 remixes per winner, 1 for YouTube; boost request $50/day, per-boost ceiling $250/day, retargeting ceiling $1,000/day, cold ceiling $8K/day, first cold day $50; `pre_gate_cold_daily_usd` 0 (set 3000 to run the R7 pre-gate line); exploration floor 20%, 14-day decay.

## Security notes (AUDIT_CODE.md)

- **Auth (H9):** the workers fail closed. See `WORKER_TOKEN` above.
- **Fetch policy (H9):** see the Environment table. IDs used in paths are validated (`[A-Za-z0-9_-]{1,64}`), and every write is confined to its base directory. ffmpeg is always called with argument lists, never a shell.
- **Errors (L12):** error responses are sanitised (422/502/500 plus an `error_id`). ffmpeg stderr and paths stay in the server log.
- **Scanner evasion (H10):** text is NFKC-normalised, zero-width characters are stripped and confusables are mapped. Spaced-out, dotted, hyphenated and leetspeak variants are also scanned. Mixed-script words block. The n8n regex pre-scan and pass 2 run the same normalisation in JS.
- **Database:** `schema.sql` §11 and `schema_growth.sql` enable RLS on every table with deny-by-default policies. EXECUTE is granted to `service_role` only, and every function has a fixed `search_path`. Tokens live only in Supabase Vault. Reviewers get read-only access through the `app_role = reviewer` JWT claim. SQL tests: `tests/test_schema_sql.py` and `tests/test_growth_schema_sql.py`, run on local Postgres 16 or against `PGTEST_DSN`.
- **Table names (H11):** the pipeline's `orders` table (DM/UTM attribution) is **not** the Strong Years app's orders table, which is named `sy_orders`. Run the pipeline in its own Supabase project if you can. If they share one, the names don't collide.

## Compliance: two layers, then a human

Every script, and again every final caption set, goes through:

1. **Deterministic scan** (`compliance/scanner.py`, and the same normalisation in the n8n regex nodes and `tools/build_content.py`). It covers blocked_claims.json, the SAFETY_RULES rules and anti-evasion normalisation: NFKC and NFKD fold, confusables, any-punctuation separators, masks, joins, repeated letters, textspeak, leetspeak, and fuzzy stems at edit distance ≤ 1 (Damerau, real words excluded via `fuzzy_exclude`). It is fast and catches the obvious. A deterministic **block can never be cleared** by the judge.
2. **LLM judge, mandatory** (`compliance/judge.py`, prompts/03). Untrusted text is tagged as data, temperature is 0 and there is a confidence floor of 0.8. It runs in n8n for pass 1 (*LLM: Compliance Judge*, `onError: continueRegularOutput`, 120 s timeout) and in the worker for pass 2 (`/package`). **No key, API error, timeout or bad JSON means the item goes to human review. It never passes.**
3. **Human** (review app / `v_human_queue`) for anything either layer flags or can't decide: `revise` after two attempts, `human`, `block`, a judge that was unavailable, MB-EX candidates, and sensitive topics.

Where it's enforced:

- `/compliance/scan`: `final.verdict` is `pass` only with `judge_passed: true`. The judge runs even if the request sends `judge: false`.
- `/package`: `pass2_ok` requires a passing judge on the packaged text. Otherwise it reports an `LLM-JUDGE` issue, and n8n routes to *Brief → human_review (pass 2)*.
- `/qa/score` and `/qa`: without `judge_passed: true` the route is always `human`, never `auto` or `approval`.
- n8n: *Parse Verdict* sets `judge.judge_ok` and turns any would-be pass into `human` without it. *Decide QA Route* re-checks `judge_ok` before `auto` or `approval`.

The CLI (`python -m compliance scan`) stays deterministic-only for offline reports. Its output is not a publish decision.
