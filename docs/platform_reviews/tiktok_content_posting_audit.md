# TikTok Content Posting API: audit submission (Direct Post)

Copy-paste answers for TikTok for Developers → your app → **Content Posting API → Direct Post → Apply for audit**. Nothing has been submitted. Products to add to the app: **Login Kit**, **Content Posting API** (Direct Post on), and **Display API** (for `video.list`, our own performance numbers).

**App name:** Strong Years Publisher · **Category:** Education / Health & fitness · **Platform:** Web · **Website:** `https://strongyears.com` · **Privacy policy:** `https://strongyears.com/privacy` · **Terms:** `https://strongyears.com/terms`

## Read this before submitting (the gaps)

1. **Who the app is for.** TikTok's Content Sharing Guidelines list "a utility tool to help upload contents to the account(s) you or your team manages" as an example of an unacceptable use. Our honest use case is exactly that (our own three accounts). Expect a rejection on that ground. Plan for it: until an approval lands, post by hand from the TikTok app (or the upload-post fallback in PIPELINE §5.3), with the same AI label and caption. Do not reword the use case to imply third-party creators use the app; they don't.
2. **The n8n node does not meet the UX rules yet** (`n8n_core_workflow.json`, "TikTok: Direct Post (PULL_FROM_URL)"): it hardcodes `privacy_level: PUBLIC_TO_EVERYONE`, never calls `creator_info/query`, and has no per-post confirmation screen. Before an audit, the publish step has to become a person-approved screen (an `/admin/exceptions` item works) that shows the items in "UX compliance" below, and the node must use the privacy level the person picked. Until then the node stays disabled (`deploy/scripts/n8n_import.py`, `LAUNCH_MODE` gate).
3. **Unaudited clients** can only post `SELF_ONLY` (private) and only for a handful of users per day: the node as written would error. Test with `SELF_ONLY` on the sandbox/test accounts and record the screencast from that.
4. **`brand_organic_toggle: true`** ("Your brand") is right for Strong Years promoting its own membership; the screen must show it as a choice the person can change, with TikTok's label text.

## Scopes requested

| Scope | Why (paste) |
|---|---|
| `user.info.basic` | "Show the connected account's display name and avatar on the confirmation screen, so the person posting can see which of our accounts the video goes to." |
| `video.publish` | "Post an approved, compliance-checked educational video to our connected account after a person confirms the privacy level, interaction settings and content disclosure on our confirmation screen." |
| `video.list` | "Read view, like, comment and share counts for videos our account has posted, to decide which topics to make more of. Shown only to our team." |

Not requested: `video.upload` (inbox/draft flow), any ads or business-API scope, any scope for other users' data.

## Audit form answers

**Describe your app and how it uses the Content Posting API.**
> Strong Years makes short educational exercise and cooking videos for adults 60+. The two hosts, Chang Yin and Sun Yoon, are AI characters, and every video says so: a burned-in "AI character" tag on every frame, a disclosure line at the end of every caption, the account bio, and TikTok's AI-generated content label (`is_aigc: true`) on every post. Our team writes and produces each video; before it can be posted it passes an automated claims-and-disclosure scanner, an automated reviewer, and a person for anything flagged. A team member then opens our confirmation screen, sees the account, the video preview and the caption, chooses the privacy level and interaction settings, confirms the content disclosure, and presses Post. The app uses `creator_info/query` before every post and `post/publish/video/init` with `PULL_FROM_URL` from our verified domain, then polls `post/publish/status/fetch`.

**Who are your users?**
> Our own content team (2–3 people), posting to TikTok accounts our company owns. No members of the public log in to this app.

**How do you get the user's consent before posting?**
> Nothing posts automatically. Each post requires a person to press Post on the confirmation screen after reviewing the preview, caption, privacy level, interaction settings and disclosure toggles. The screen states "By posting, you agree to TikTok's Music Usage Confirmation" (and the Branded Content Policy when "Branded content" is on).

**Do you add watermarks, logos or promotional content to the user's video?**
> No. The app posts the video file exactly as our team produced it. The only on-screen marks are the ones the creator authored for disclosure: the "AI character" tag and on-screen safety text, which are part of the video, not added by the API client.

**Content restrictions.**
> Health-education content for older adults: no medical claims, no diagnosis or treatment language, a safety line on every movement video, and an AI disclosure everywhere (SAFETY_RULES.md D-02, D-04, D-05, §7). Our compliance gate blocks any post that fails those checks before it can reach the confirmation screen.

**Expected volume.**
> Up to 3 posts per account per day across 3 accounts (≤ 9/day total), with minimum spacing between posts on the same account.

**Data handling.**
> We store the TikTok `publish_id`, the resulting video id and the public counts from `video.list` against our own post record. Tokens are encrypted at rest and refreshed with the refresh token; disconnecting the account in our admin revokes and deletes them. We don't collect data about viewers or other users.

## UX compliance (what the confirmation screen shows; record this in the screencast)

| TikTok requirement | Our screen |
|---|---|
| Creator info from `creator_info/query` before posting | Account nickname + avatar at the top; if `max_video_post_duration_sec` is shorter than the video, Post is disabled with the reason |
| Privacy level: options from `privacy_level_options`, **no default** | Dropdown with only the returned options, empty until chosen; Post disabled until chosen |
| Interaction toggles (Comment, Duet, Stitch) | Three toggles, off by default; any the creator has disabled in TikTok are shown switched off and locked, with the reason in full-contrast text (stitch/duet not shown for photo posts) |
| Commercial content disclosure | "Disclose video content" switch, off by default; when on: "Your brand" / "Branded content" checkboxes; Post disabled until one is ticked; the matching label text is shown; "Branded content" cannot be private |
| Legal declaration | "By posting, you agree to TikTok's Music Usage Confirmation" (+ Branded Content Policy when applicable), with links |
| Preview | The video plays on the screen; caption is editable |
| AI-generated content | "AI-generated" shown as on and locked (`is_aigc: true` for every Strong Years video) |
| After posting | Status polled from `post/publish/status/fetch`; the person sees "processing / posted / failed" and is told it can take a few minutes to appear |

## Screencast script (≤ 3 min, test account, English UI)

1. Log in to our admin; open the post queue; show one post with "scanner: pass · judge: pass · human: approved" and one blocked post with its reason.
2. Open the approved post → Connect TikTok (Login Kit consent screen showing the three scopes) → back on the confirmation screen.
3. Show the account name/avatar, the video preview, the caption ending with the AI disclosure, the AI-generated label locked on.
4. Show the privacy dropdown empty and Post disabled; pick an option. Toggle comments on. Turn on "Disclose video content", tick "Your brand", show the label text and the Music Usage Confirmation line.
5. Press Post; show the status changing to posted; open the TikTok app and show the video with the AI-generated label and the burned-in "AI character" tag.
6. Show the performance row filling from `video.list` the next day (or the request in the log).
