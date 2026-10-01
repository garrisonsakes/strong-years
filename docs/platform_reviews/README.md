# Platform API review submissions (copy-paste ready)

Nothing here has been submitted. The client submits from their own developer accounts (Meta Business Portfolio with business verification, TikTok for Developers organization, Google Cloud project with OAuth consent verified). Until each approval lands, the matching n8n publisher nodes stay disabled (`deploy/scripts/n8n_import.py` keeps every publish/spend node off unless `LAUNCH_MODE=live`) and posts go out by hand from the native apps with the same AI labels.

| File | Platform | What it covers |
|---|---|---|
| `meta_app_review.md` | Instagram Graph API + Facebook Pages | Permissions, per-permission use-case text, screencast scripts, data handling. DM-bot details: `workers/dm/APP_REVIEW.md` (same app) |
| `tiktok_content_posting_audit.md` | TikTok Content Posting API (Direct Post) | Audit form answers, UX-guideline compliance, the gaps to close before submitting |
| `youtube_api_compliance.md` | YouTube Data API v3 + YouTube Analytics API | Quota extension form answers, compliance audit answers, OAuth scopes |

## The two facts every reviewer asks about (same wording in all three)

**AI disclosure.** Chang Yin and Sun Yoon are AI characters, and every surface says so: the profile bio and pinned "Hi, we're AI" post on every account; a burned-in "AI character" tag on every frame of every video (SAFETY_RULES.md D-02); the caption footer on every post ("Chang & Sun are AI characters. Content is educational, built on published research, and not medical advice. Check with your doctor before starting new exercise.", SAFETY_RULES.md §7); and the platform's own AI flag on every upload: Instagram "AI info" label, TikTok `is_aigc: true`, YouTube `status.containsSyntheticMedia: true`. The packager (`workers/packager/packager.py`) sets the flags and refuses a package without them (`workers/packager/fallback.py`). Characters never claim to be human or credentialed (D-04, D-05).

**Compliance gate.** Nothing is published unless it has passed, in order: (1) the deterministic scanner (`workers/compliance/scanner.py`: blocked health claims, required disclosures, movement-safety lines, credential claims; self-test `python -m compliance selftest`), (2) a mandatory model judge (`workers/compliance/judge.py`), and (3) a human for anything the scanner or judge flags or finds ambiguous (`/admin/exceptions`, append-only audit trail). Visual QC (`workers/qa`) checks the burned-in AI tag and on-screen text before packaging. The publisher (`n8n_core_workflow.json`, node group "P. Publisher") only claims posts whose status is approved, one at a time, with minimum spacing per platform. No ad spend runs through these apps.
