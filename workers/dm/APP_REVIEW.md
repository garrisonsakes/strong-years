# Meta App Review: Strong Years DM bot (workers/dm)

What the in-house bot needs from Meta before it can answer comments and DMs on the Strong Years Instagram accounts and Facebook Pages. Nothing here has been submitted; the client's Meta Business Portfolio (business verification done) submits it. Until approval, `DM_SEND_ENABLED=0` (the default) keeps every reply in the outbox, and the manual fallback (ManyChat or a person in the inbox) handles DMs.

## Permissions to request (Advanced Access unless noted)

| Permission | Why the bot needs it | Screencast shows |
|---|---|---|
| `instagram_basic` | Read the IG professional account id and media ids to attribute comments to posts | Account connected in the app's settings page |
| `instagram_manage_messages` | Receive IG DMs (webhook `messages`, `messaging_postbacks`) and reply inside the 24-hour window | Commenting "STRONG", receiving DM 1 with the AI disclosure, tapping "Yes, send it" |
| `instagram_manage_comments` | Receive `comments` webhooks, post the public reply ("Sent it to your messages"), and send the one private reply to that comment | A comment on a Reel, the public reply, the private reply in the inbox |
| `pages_messaging` | Messenger: receive and reply to messages and postbacks on the Facebook Pages | Same flow on Messenger |
| `pages_manage_metadata` | Subscribe the Pages to the webhook fields (`messages`, `messaging_postbacks`, `feed`) | Webhook subscription screen |
| `pages_read_engagement` | Read Page posts/comments to match a comment to its post id | Comment on a Page post → reply |
| `pages_show_list` (standard) | List the Pages the admin manages during setup | Setup screen |
| `pages_manage_engagement` | Post the public comment reply on Facebook Pages | Public reply under a Page post |
| `business_management` (only if the Pages live in the client's Business Portfolio and the app needs to list them) | Asset access through the portfolio | Setup screen |

**Not requested:** `instagram_content_publish`, `pages_manage_posts`, ads permissions, `user_*` permissions, any "Human Agent" feature. The bot never publishes posts, never spends, never messages anyone who hasn't written or commented first, and never uses message tags (automation stays inside the standard 24-hour window; a person replying from the inbox may use the HUMAN_AGENT tag within 7 days under Meta's policy, outside this bot).

## Webhook fields

- Instagram: `messages`, `messaging_postbacks`, `comments`.
- Page: `messages`, `messaging_postbacks`, `feed` (comments only; `item = comment`, `verb = add`).
- Callback: `https://<workers-host>/dm/webhook`. Verify token: `DM_VERIFY_TOKEN`. Every POST is checked against `X-Hub-Signature-256` with the app secret (`META_APP_SECRET`); a missing secret answers 503 (fail closed), a bad signature 401.

## Policy points the reviewer will look for (and where the code enforces them)

| Policy | Enforcement |
|---|---|
| 24-hour standard messaging window | `Bot._in_window` gates every follow-up; follow-ups (nudge +20 min, check-in +22 h) only exist for a conversation the person started |
| Private replies: one message per comment, within 7 days | One DM 1 per comment event (`private_reply_to_comment`), sent immediately; dedup by event id |
| No unsolicited messages | Every action carries `in_reply_to` an inbound event; tests assert it (`tests/test_dm_bot.py`) |
| Opt-out | STOP / UNSUBSCRIBE (exact word) → opt-out in the consent log, one confirmation, silence; START → opt-in |
| Automated experience disclosure | The first message to every contact states it is an automated assistant and that Chang Yin and Sun Yoon are AI characters |
| Human handoff | "human", "person", "agent" → handoff (automation paused 7 days), a person replies from the inbox |
| Safety | Self-harm, medical-emergency, abuse and grief language → automation paused, the 988 / 911 line (FUNNEL.md §4.14), an item in /admin/exceptions for a person |
| Data use | The bot stores the Meta-scoped sender id, tags (keywords), timestamps and, only when the person types it, their email (sent to our own `/api/leads` with the exact consent text shown). No message bodies are stored beyond the event dedup id; exceptions carry a hashed contact key and the category, never the text. Deletion: the data-deletion callback removes the contact row and consent rows on request (to build with the privacy policy URL before submission). |

## Reviewer test account script

1. Comment `STRONG` on the test Reel → public reply appears, DM 1 arrives with the AI disclosure and a "Yes, send it" button.
2. Tap it → DM 2 with the lesson link (`/s/l1?mc_id=…`) and the email quick replies.
3. Type `price` → the price answer (runway: no price, the free waitlist link).
4. Type `STOP` → confirmation; comment `STRONG` again → public reply only, no DM.
5. Type `START`, then `talk to someone` → handoff message; the bot stays quiet.

## Before submitting

- Privacy policy URL and data-deletion instructions URL live on strongyears.com.
- App icon, category "Messaging", business verification complete, 2FA on every admin.
- The screencasts above recorded on the test accounts (no real customers).
