# YouTube API Services: quota extension + compliance audit

Copy-paste answers for the **YouTube API Services – Audit and Quota Extension Form** (Google Cloud project → YouTube Data API v3 → Quotas → "Apply for higher quota"). Nothing has been submitted. One Google Cloud project, OAuth consent screen **verified** (sensitive scopes need it), three Strong Years channels authorized by the client's own Google accounts.

**API client name:** Strong Years Publisher · **Website:** `https://strongyears.com` · **Privacy policy:** `https://strongyears.com/privacy` · **Terms:** `https://strongyears.com/terms` · **Contact:** the client's ops email

## Read this before submitting

1. **Private-only until audited.** Videos uploaded through `videos.insert` from an unverified API project (created after July 28 2020) are locked private. Until the audit passes, upload by hand in YouTube Studio with the same settings ("Altered or synthetic content: Yes"). The n8n node "YT: Init Resumable Upload" stays disabled until then.
2. **Privacy policy must** link to the YouTube Terms of Service (`https://www.youtube.com/t/terms`) and the Google Privacy Policy (`https://policies.google.com/privacy`), say what YouTube data we store and for how long, and tell people how to revoke access (`https://myaccount.google.com/permissions`). Confirm `/privacy` has those three lines before submitting.
3. **Quota math.** Check the current per-method costs in Google's quota calculator on the day you submit. ORGANIC_ENGINE.md §2.5 records the newer uploads bucket (`videos.insert` = 1 unit, 100 calls/day per project); if the project still shows the classic 10,000 units/day with `videos.insert` = 1,600, use the request in the "Quota" answer below.
4. **Monetization is a separate question.** YouTube's July 2026 clarification makes AI personas discussing health ineligible for YPP; Strong Years does not depend on YouTube ad revenue (ORGANIC_ENGINE.md §2.5). Don't mention monetization on this form.

## OAuth scopes

| Scope | Why (paste) |
|---|---|
| `https://www.googleapis.com/auth/youtube.upload` | "Upload approved educational Shorts to our own channels with the title, description, tags, category and the altered/synthetic content flag set." |
| `https://www.googleapis.com/auth/youtube.readonly` | "Read our own channels' video ids and public statistics to match each upload to our post record." |
| `https://www.googleapis.com/auth/yt-analytics.readonly` | "Read views, watch time and average view duration for our own videos, shown only to our team, to decide which topics to make more of." |

Not requested: `youtube` (full manage), `youtube.force-ssl`, comment-writing scopes, any scope for other channels.

## Form answers

**Describe your API client and its use of YouTube API Services.**
> Strong Years publishes short educational exercise and cooking videos for adults 60+ to its own three YouTube channels and reads those videos' performance. The hosts, Chang Yin and Sun Yoon, are AI characters, and every video discloses it: a burned-in "AI character" tag on every frame, a disclosure line in every description, the channel About section and a pinned introduction Short, and YouTube's altered or synthetic content setting (`status.containsSyntheticMedia: true`) on every upload. Before any upload, the video and its text pass an automated health-claims and disclosure scanner, an automated reviewer, and a person for anything flagged. The client is internal: only our team uses it, and it only acts on channels our company owns.

**Which API methods do you call?**
> `videos.insert` (resumable upload; `snippet` title/description/tags/categoryId 26, `status` privacyStatus, selfDeclaredMadeForKids=false, containsSyntheticMedia=true), `videos.list` (part=statistics for our own video ids), `channels.list` (mine=true), YouTube Analytics `reports.query` (ids=channel==MINE; views, estimatedMinutesWatched, averageViewDuration by video).

**How many users / channels?**
> 2–3 team members; 3 channels, all owned by our company.

**Do you display YouTube data to anyone outside your organization?**
> No. Numbers appear only in our internal admin screen.

**How do you store YouTube API data, and for how long?**
> We store our own video ids and their statistics against our post records. Statistics are refreshed daily and anything older than 30 days is either refreshed or deleted, per the Developer Policies. OAuth refresh tokens are encrypted at rest; disconnecting a channel in our admin revokes the token with Google and deletes it. We store no data about viewers, commenters or other channels.

**Do you use YouTube data for advertising or sell it?**
> No.

**Do you combine YouTube data with data from other platforms?**
> We show YouTube numbers next to our own Instagram and TikTok numbers in one internal table so the team can compare topics. Metrics from each platform are labelled with their source and are not merged into a derived cross-platform metric shown as YouTube data.

**Quota requested and calculation.**
> At full cadence: 3 channels × up to 4 Shorts/day = 12 uploads/day. Classic costs: 12 × `videos.insert` 1,600 = 19,200; `videos.list` / `channels.list` ≈ 50 calls × 1 = 50; Analytics is billed separately. Requested: **25,000 units/day** (≈ 30% headroom for retries of failed resumable uploads). Under the uploads bucket model: 12 of 100 `videos.insert` calls/day, no extension needed for uploads; we would request only what the calculator shows for the read calls.

**How does your client meet the "Required Minimum Functionality"?**
> Users authorize with Google OAuth and can see which channel is connected; every upload shows the person the title, description, privacy status and the synthetic-content flag before it is queued; the person can disconnect a channel at any time.

## Compliance audit checklist (answers)

| Requirement | Strong Years |
|---|---|
| Accurate, non-misleading metadata | Titles ≤ 60 chars from the packager (`workers/packager/packager.py`); no clickbait or health claims (scanner) |
| Altered/synthetic disclosure | `containsSyntheticMedia: true` on every upload; the packager refuses a package without it (`workers/packager/fallback.py`) |
| Made for kids | `selfDeclaredMadeForKids: false` (audience: adults 60+) |
| No spam / repetitive content | One channel per editorial page, no cross-channel duplicates, remix cap 1 per source with a text-similarity limit (`workers/growth/config.py`), max 4/day per channel |
| Medical misinformation policy | General fitness and nutrition education only; no diagnosis/treatment/cure language; safety line on every movement video (SAFETY_RULES.md) |
| Branding | We don't use YouTube logos or imply endorsement |
| Data deletion | Statistics refreshed or deleted within 30 days; tokens revoked and deleted on disconnect |

## Screencast script (≤ 3 min)

1. Our admin: the post queue with one approved post ("scanner: pass · judge: pass · human: approved") and one blocked post with its reason.
2. Connect a channel: Google consent screen with the three scopes; back in admin the channel name shows as connected.
3. Open the approved Short: title, description ending with the AI disclosure, privacy status, "Altered or synthetic content: Yes" locked on. Queue it; show the `videos.insert` resumable upload in the log.
4. YouTube Studio: the Short with the altered/synthetic label and the burned-in "AI character" tag.
5. The statistics row filling from `videos.list` / Analytics; then Disconnect → token revoked.
