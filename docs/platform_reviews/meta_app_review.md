# Meta App Review: Strong Years publisher + insights (+ DM bot)

**App name:** Strong Years Publisher · **Type:** Business · **Use case:** "Manage messaging and content on Instagram" + "Manage everything on your Page" · **Category:** Health & fitness (education)
**Accounts it touches:** only Strong Years' own Instagram professional accounts (@changyin, @sunyoon.kitchen, @changandsun) and their linked Facebook Pages, all owned by the client's Business Portfolio. No third-party users log in. Privacy policy: `https://strongyears.com/privacy` · Data deletion: `https://strongyears.com/privacy#delete` (callback in `workers/dm`) · Terms: `https://strongyears.com/terms`

## App description (paste into "Tell us how you'll use this app")

> Strong Years publishes short educational exercise and cooking videos for adults 60+ to its own Instagram professional accounts, reads the performance of those posts, and answers comments and DMs that people send to those accounts. The two hosts, Chang Yin and Sun Yoon, are AI characters, and every post says so: the account bio, a pinned "Hi, we're AI" post, a burned-in "AI character" tag on every video frame, a disclosure line at the end of every caption, and Instagram's AI label. Before anything is published it passes an automated compliance check (blocked health claims, required safety and AI-disclosure lines), a second automated review, and a human review for anything flagged. The app only acts on accounts our business owns. It never posts on behalf of other people, never runs ads, and never messages anyone who has not written to us first.

## Permissions and per-permission use case (paste each block into its permission's field)

| Permission | Access | Paste this |
|---|---|---|
| `instagram_basic` | Advanced | "We read our own Instagram professional accounts' ids and media ids so each published Reel, its comments and its insights are matched to the post record in our content system." |
| `instagram_content_publish` | Advanced | "We publish Reels to our own three Instagram professional accounts: create a REELS media container with a hosted video URL and the approved caption, then publish it. Every caption ends with our AI-character disclosure and every video carries a burned-in 'AI character' tag. A post can only be published after it passes our compliance gate (automated claim scanner, automated reviewer, human review for anything flagged). At most a few posts per account per day, spaced apart. We use trial Reels for our own accounts only." |
| `instagram_manage_insights` | Advanced | "We read views, reach, likes, comments, shares, saves, follows and average watch time for our own Reels to decide which topics to make more of. The numbers are stored per post in our own database and shown only to our team." |
| `instagram_manage_comments` | Advanced | "When someone comments a keyword (e.g. STRONG) on one of our Reels, we post one public reply without links or prices and send one private reply. The first message states that it is an automated assistant and that Chang Yin and Sun Yoon are AI characters." |
| `instagram_manage_messages` | Advanced | "We answer DMs people send our accounts, inside the 24-hour standard messaging window, with the lesson or waitlist link they asked for. STOP ends messages; 'human' hands the conversation to a person; crisis language pauses automation and shows 988 / 911." |
| `pages_show_list` | Standard | "During setup our admin picks which of their Pages are linked to our Instagram accounts." |
| `pages_read_engagement` | Advanced | "We read our own Page posts, comments and video insights to match comments to posts and measure our videos." |
| `read_insights` | Advanced | "We read video insights for our own Facebook Pages' videos (views, average watch time) for the same per-post performance table." |
| `pages_manage_metadata` | Advanced | "We subscribe our Pages to webhook fields (messages, messaging_postbacks, feed) so comments and messages reach our assistant." |
| `pages_messaging` | Advanced | "Messenger version of the DM flow above, same rules." |
| `pages_manage_engagement` | Advanced | "One public reply under a comment on our own Page posts." |
| `business_management` | Advanced (only if asset access is through the Business Portfolio) | "Our Pages and Instagram accounts live in our Business Portfolio; the app reads which assets it has been granted." |

**Not requested:** `pages_manage_posts` (Facebook videos are posted by hand), any `ads_*` permission, any `user_*` permission, message tags beyond the standard window, Human Agent.

## Screencast scripts (record on the test accounts, English UI, captions on, ≤ 3 min each)

**1. Publish (instagram_content_publish, instagram_basic)**
1. Show the internal post queue: one approved post, its compliance status ("scanner: pass · judge: pass · human: approved") and the caption ending with the AI disclosure.
2. Show a second post in the queue with status "blocked" and the reason (e.g. a blocked health claim) and that the publisher skips it.
3. Trigger the publisher. Show the Graph API calls in the log: `POST /{ig-user-id}/media` (media_type REELS, video_url, caption) then `POST /{ig-user-id}/media_publish`.
4. Open the Instagram app: the Reel is live, the "AI character" tag is visible on the video, the caption ends with the disclosure, the AI label is on.

**2. Insights (instagram_manage_insights, read_insights, pages_read_engagement)**
1. Show the per-post table in `/admin/today` empty for the new Reel.
2. Run the snapshot job; show the `GET /{media-id}/insights` request and the filled row (views, reach, saves, avg watch time). Explain that only our own posts are read.

**3. Comments and DMs (instagram_manage_comments, instagram_manage_messages, pages_*)** — follow `workers/dm/APP_REVIEW.md` "Reviewer test account script" (comment STRONG → public reply + DM 1 with the AI disclosure → button → link → `STOP` → silence → `START` → "talk to someone" → handoff).

## Data handling answers

- **Data stored:** post ids, our own captions, per-post metrics; for DMs the page-scoped sender id, keyword tags and timestamps, and an email only if the person types it (sent with the exact consent text). No message bodies beyond the dedup id.
- **Shared with:** nobody. No data is sold or used for ads targeting.
- **Retention / deletion:** metrics kept while the post exists; contact rows deleted on request or via the data-deletion callback.
- **Security:** tokens in the server vault (`deploy/secrets.env`, never in the repo); webhooks verified with `X-Hub-Signature-256` (fail closed); admin behind basic auth + lockout + optional TOTP.

## Before submitting

- Business verification complete; 2FA on every admin; app icon; privacy and data-deletion URLs live.
- Test users added to all three IG accounts; the screencasts above recorded with no real customer data.
- `GRAPH_API_VERSION` set to the version the reviewer will see (the workflow defaults to v24.0).
