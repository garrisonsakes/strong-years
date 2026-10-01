# ACCOUNT_SETUP.md: creating and configuring every Strong Years account (client only)

> **Order of operations across the whole launch now lives in [`LAUNCH_RUNBOOK.md`](LAUNCH_RUNBOOK.md)** (Oct 1 2026). This file remains the click-by-click account guide; bios link to `/go?p=…` / `/tt`, which switch from waitlist mode to launch mode by themselves when checkout opens.


**Who does this:** the client (Garrison) personally, or a person he employs, on his own devices and logins. We never create, log into or operate accounts; our pipeline only receives access the client grants through official OAuth screens or system-user tokens the client generates. Nothing here spends money (ad accounts are created with no payment method and no campaigns).

**When:** D−28 → D−22 for the three day-1 pages (ORGANIC_ENGINE.md §1.1, R = 21). Later pages (`@changyin.strength`, `@changyin.mobility`, `@sunyoon`, `@changyin.espanol`) follow the same steps 3–4 days before their start date (ORGANIC_ENGINE §1.2).

**Menu labels change often.** Every path below was written for the October 2026 apps; where a label is not confirmed from a primary source it's marked **[verify on device]**. If a label differs, use the platform's search box in Settings with the quoted word.

---

## 0. Ground rules (read once)

1. **One legal entity, one Meta business portfolio, openly one studio.** Every account names Strong Years in its About/description. No proxies, VPN hopping, anti-detect browsers or device farms (PIPELINE.md §5.1): they are the signal "coordinated inauthentic behavior" enforcement looks for.
2. **Logins:** one company email alias per account (e.g. `ig.changyin@{{COMPANY_DOMAIN}}`), a unique generated password in the 1Password vault "Strong Years / Accounts", **authenticator-app 2FA** (not SMS) with recovery codes saved in the same 1Password item. Two human admins per platform (the client + one named backup person).
3. **Devices:** create Instagram and TikTok accounts on a real phone, one new account per platform per day (space them out across D−28 → D−26). Instagram allows up to 5 accounts logged in per device.
4. **VAs work through roles** (Business Suite, YouTube channel permissions, ManyChat team seats), never through shared passwords.
5. **AI disclosure is set before the first post** on every account (SAFETY_RULES.md D-01). The bio strings below are the SAFETY §7 FALLBACK strings (no reviewer is signed); do not edit them except where a platform limit forces the short version marked for approval.
6. **Bios link to waitlist mode** until the client flips launch mode on D0 (ORGANIC_ENGINE §3.2).
7. **Don't post anything yet** except the native pinned posts in week 0 (ORGANIC_ENGINE §1.1).

### 0.1 Names, handles and bios (the source of truth for every step below)

| Page | Display name | Handle (IG / Threads / TikTok / YouTube / FB) | X handle (no periods, ≤15 chars) |
|---|---|---|---|
| Chang flagship | Chang Yin · AI character | `changyin` | `changyin` |
| Sun's kitchen | Sun Yoon · AI character | `sunyoon.kitchen` (TikTok/YouTube: `sunyoon.kitchen` if allowed, else `sunyoonkitchen`) | `sunyoon_kitchen` |
| Duo | Chang & Sun · AI characters | `changandsun` | `changandsun` |
| Later: strength | Chang Yin Strength · AI | `changyin.strength` | `changyinstrong` |
| Later: mobility | Chang Yin Mobility · AI | `changyin.mobility` | `changyinmobile` |
| Later: Sun | Sun Yoon · AI character | `sunyoon` | `sunyoon` |
| Later: Spanish | Chang Yin en español · IA | `changyin.espanol` | `changyin_es` |

If a handle is taken, use the first free option in this order and record it in BRIEF.md: `{handle}.strongyears`, `{handle}.official`, `strongyears.{handle}`. Never use a name that could be mistaken for a real person or another brand.

**Bios (exact; SAFETY_RULES.md §7 FALLBACK strings):**

| Where | Chang flagship | Sun's kitchen | Duo |
|---|---|---|---|
| Instagram, Threads, Facebook intro, X | `Chang Yin, 74 (AI character) · Strength after 60, done safely · Real research, sources linked · 👇 Free 7-day plan` | `Sun Yoon, 76 (AI character) · His wife. Blunter than him. · Real recipes, real research · 👇 Free soup book` | `Chang & Sun · AI characters, real advice, 50 years of fictional marriage · Sources on our site` |
| YouTube description (first lines) | The Instagram string + new line + `Characters are AI. Content is built on published research (sources on our site).` + new line + `Made by the Strong Years team. Not medical advice; check with your doctor before starting new exercise.` | same pattern | same pattern |
| TikTok (80-character limit **[verify on device]**) | **Short version, needs compliance sign-off:** `Chang Yin, 74 · AI character · Strength after 60 · Sources linked` | `Sun Yoon, 76 · AI character · Real recipes, real research` | `Chang & Sun · AI characters · Real advice · Sources linked` |

The full TikTok disclosure sentence ("Characters are AI. Content is built on published research (sources on our site).") doesn't fit 80 characters, so it goes in the pinned "Hi, we're AI" video's caption and on the `/tt` page header. Log the short bio as an approved SAFETY §7 platform variant before use.

**Links (waitlist mode until D0):** Chang `{{DOMAIN}}/go?p=cy`, Sun `{{DOMAIN}}/go?p=sk`, Duo `{{DOMAIN}}/go?p=cs`, TikTok (all) `{{DOMAIN}}/tt?p={code}`, YouTube `{{DOMAIN}}/go?p=yt-{code}`. Add UTMs only in the `/go` page's tiles, not in the bio URL.

**Profile images:** the locked reference portraits (CHARACTERS §13.1), each with the small "AI" corner mark baked in. Banner/cover (Facebook, YouTube, X): the home-world set with "AI characters · Real research" in full-contrast text.

---

## 1. Prerequisites (D−30 → D−29)

1. **Company domain + email:** in Google Workspace (or the existing provider) create the aliases: `meta@`, `ig.changyin@`, `ig.sunyoonkitchen@`, `ig.changandsun@`, `tt.changyin@`, `tt.sunyoonkitchen@`, `tt.changandsun@`, `yt@`, `x.changyin@`, `x.sunyoonkitchen@`, `x.changandsun@`, `manychat@`, `dev@`. All deliver to one monitored inbox with filters.
2. **1Password:** vault "Strong Years / Accounts"; share it with the backup admin only.
3. **Authenticator app** on the client's phone and on the backup admin's phone (both enrolled for every account, or recovery codes stored).
4. **Two phones** for account creation and native posting (the client's + one company phone).
5. **Site pages live (DEV):** `{{DOMAIN}}/privacy`, `/terms`, `/safety`, `/how-we-make-this`, `/go`, `/tt`, `/waitlist`. Meta, TikTok and Google app reviews require the privacy policy and a data-deletion URL.
6. **Legal documents ready** for business verification: articles of organization / EIN letter, a utility bill or bank statement with the business address, and the business phone.

---

## 2. Meta business portfolio (Business Manager) (D−28)

1. On a computer, go to **business.facebook.com** → log in with the client's personal Facebook profile (it must be a real, long-standing profile with 2FA on) → **Create an account** → business portfolio name **Strong Years** (legal name in verification), your name, business email `meta@{{COMPANY_DOMAIN}}` → **Submit** → confirm the email.
2. **Settings** (gear) → **Business info** → fill the legal name, address, phone, website `{{DOMAIN}}`.
3. **Security Center** → **Start verification** → choose the legal entity → upload the documents → verify by email or phone. (Approval can take days; start it first.)
4. **Brand safety → Domains → Add** → `{{DOMAIN}}` → **DNS TXT verification** → add the TXT record at the DNS host → **Verify**.
5. **Security Center → Two-factor authentication → Required for everyone**.
6. **Users → People → Add** → the backup admin (full control) and, later, each VA (partial access: Content, Messages, Community activity, Insights; no Settings, no Payments).
7. **Ad account (created empty, no payment method):** **Accounts → Ad accounts → Add → Create a new ad account** → name `Strong Years – Organic Boosts` → time zone America/New_York, currency USD → **do not add a payment method** (the spend governor and the client's approval come first; BLITZ.md §11).

---

## 3. Facebook Pages (D−28, three Pages)

For each of the three day-1 pages:
1. In **Business Suite** (business.facebook.com) → **Accounts → Pages → Add → Create a new Facebook Page**.
2. **Page name:** the display name from §0.1 (e.g. `Chang Yin · AI character`). **Category:** `Digital creator` (add `Health & wellness website` as the second category). **Bio:** the bio string from §0.1 (Facebook's intro limit is ~100 characters **[verify on device]**; if it cuts, use the TikTok short version and put the full string in the About section).
3. **Create Page** → add the profile picture and cover.
4. **Page settings → Page setup → Username** → the handle from §0.1.
5. **Edit details:** website `{{DOMAIN}}/go?p={code}`, email `meta@{{COMPANY_DOMAIN}}`, "About" long description: the YouTube description text from §0.1.
6. **Action button → Edit → Send message** (comment → Messenger flows run through ManyChat).
7. **Settings → Privacy / Messaging**: messaging on; **Settings → Page setup → Page access**: confirm the client and the backup admin both have full control (task access through Business Suite).
8. **Professional dashboard → Page transparency**: confirm the organization (Strong Years) shows once business verification completes.
9. Do not boost, do not create ads, do not invite friends to like the Page.

---

## 4. Instagram professional accounts (D−28 → D−26, one per day)

On the phone, for each page:
1. Instagram app → profile → username at the top → **Add account → Create new account** → **Sign up with email** → `ig.{page}@{{COMPANY_DOMAIN}}` → confirmation code → password from 1Password → birthday (the account owner's real date; this is the human owner of a business account) → username from §0.1.
2. Skip contact syncing; skip "find friends".
3. **Edit profile:** Name (display name from §0.1), Username, **Bio** (exact string), **Links → Add external link** → the waitlist-mode link, title "Free Day 1".
4. **Edit profile → AI-generated profile → turn on** (the label Instagram introduced Aug 31 2026 for accounts built around an AI person; it shows on the profile and alongside content) **[verify on device: the toggle may sit under "Edit profile" or "Account type and tools"]**. Screenshot the profile showing the label and save it in 1Password (the pipeline won't mark the account active without `ai_label_verified_at`, PIPELINE §5.2).
5. **Settings and activity → Account type and tools → Switch to professional account → Creator** → category **Digital creator** → choose whether to display the category (on).
   - Creator (not Business) because broadcast channels are a creator tool and Trial Reels are offered to professional accounts. Both types work with the content-publishing API and ManyChat.
6. **Connect the Facebook Page:** Edit profile → **Page → Connect** → select the matching Page from §3 (or Accounts Center → Accounts → Add accounts → the client's Facebook profile, then connect the Page).
7. **Accounts Center → Password and security → Two-factor authentication** → this account → **Authentication app** → scan with the authenticator → enter the code → **save the recovery codes** in 1Password.
8. **Settings → Messages and story replies → Message controls → Connected tools → Allow access to messages: ON** (required for ManyChat).
9. **Settings → Hidden words:** turn on "Hide comments" and "Advanced comment filtering"; add custom words: `crypto, whatsapp me, DM me for, investment, forex, telegram` (impersonation and scam patterns, CONTENT_SYSTEM §6.5).
10. **Settings → Creator tools and controls → Branded content:** turn on (needed for the "Paid partnership" label on real partner collabs, ORGANIC_ENGINE §4.5). **[verify on device]**
11. **Settings → Sharing and reuse (Remix):** allow remixes of Reels (partners can do side-by-sides).
12. **Week 0 only:** post the 3 pinned posts natively from this phone (files from the shared drive), pin them, and follow 10–20 real, relevant accounts by hand. No automation until runway day 1.

---

## 5. Threads (D−26, after each Instagram account exists)

1. Install **Threads** → **Log in with Instagram** → choose the page's Instagram account.
2. **Import from Instagram** (name, picture, bio, link) → check the bio is the exact string; set the profile **Public**.
3. **Settings → Account → Fediverse sharing: off** for now (keeps moderation inside Threads; client may revisit).
4. 2FA is the Instagram account's 2FA (Threads uses the same login).
5. **Communities:** join 3–5 relevant communities (fitness over 60, cooking, retirement) as the page. Post nothing yet.

---

## 6. TikTok (D−28 → D−26, one per day) + TikTok Business Center + TikTok for Developers

### 6.1 Accounts (phone)
1. TikTok app → **Sign up → Use phone or email → Email** → `tt.{page}@{{COMPANY_DOMAIN}}` → birthday (owner's real date) → password → code.
2. **Profile → Edit profile:** Name (≤30 characters: `Chang Yin · AI character`), Username from §0.1, Bio (the TikTok short version from §0.1), photo.
3. **Profile → ☰ → Settings and privacy → Account → Switch to Business Account** → category **Education** or **Fitness** **[verify on device]**. Business accounts get the business suite and analytics, and use the commercial music library (we use original audio only). Then add the **Website** link if the field is available (TikTok may require a follower minimum for bio links **[verify on device]**; until then the link lives in the pinned video caption and the `/tt` page).
4. **Settings and privacy → Security → 2-step verification** → turn on with the **authenticator app** if offered, otherwise email + SMS **[verify on device]**; save backup codes.
5. **Settings and privacy → Privacy:** account **Public**; Duet/Stitch on (partner side-by-sides); Downloads off.
6. **AI label on every manual post:** before posting, **More options → AI-generated content → on**. Posts sent by our pipeline carry `is_aigc: true`, which adds "Creator labeled as AI-generated" ([TikTok Direct Post reference](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post)).
7. **Business suite → Automated messages / Keyword replies** **[verify on device]**: add the keywords WAITLIST, STRONG, SOUP, TEST, BOOK (from D0) with the first line of the matching FUNNEL §4 DM 1 and the `/tt` link (US comment triggers aren't available; DM keyword replies are).

### 6.2 TikTok Business Center (computer)
1. **business.tiktok.com → Create** → business name Strong Years, legal info, time zone America/New_York.
2. **Assets → TikTok accounts → Add → Request access** → approve the request inside each TikTok app (the account owner approves).
3. **Assets → Ad accounts → Create** (name `Strong Years – Spark Boosts`, **no payment method**). Spark Ads stay off until the governor and the client approve a boost of a proven winner (ORGANIC_ENGINE §2.4).
4. **Members → Invite** the backup admin (Admin) and VAs (Operator, no finance).

### 6.3 TikTok for Developers (for the publishing pipeline)
1. **developers.tiktok.com** → log in with `dev@` → **Manage apps → Connect an app** → organization Strong Years.
2. App details: name `Strong Years Publisher`, icon, category Entertainment/Lifestyle, description, **Terms** `{{DOMAIN}}/terms`, **Privacy** `{{DOMAIN}}/privacy`.
3. **Add products:** **Login Kit** and **Content Posting API** (enable **Direct Post**).
4. **Scopes:** `user.info.basic`, `video.upload`, `video.publish`.
5. **Redirect URI:** `{{APP_DOMAIN}}/api/oauth/tiktok/callback` (DEV gives the exact URL).
6. **URL properties → Verify** the media host prefix used for `PULL_FROM_URL` (the R2 public domain DEV names) by the DNS or file method.
7. **Submit for review**, then submit the **Content Posting API audit** (until it passes, API posts are private-only; the pipeline publishes TikTok through upload-post meanwhile, PIPELINE §5.3).
8. **Authorize:** when DEV asks, open the app's TikTok connect link, log in as each page's TikTok account, approve the scopes. Tokens go straight to our server; no password leaves the client.

---

## 7. YouTube channels (D−28) + Google Cloud project (D−28)

### 7.1 Channels (computer, signed in as `yt@{{COMPANY_DOMAIN}}`, a Google account with 2-Step Verification via authenticator + backup codes)
1. **youtube.com → profile picture → Settings → Add or manage your channel(s) → Create a channel** (this creates a Brand Account, so several people can manage it without sharing the login) → name = display name from §0.1 → **Create**.
2. **YouTube Studio → Customization → Profile:** handle from §0.1, picture, banner, **description** (the YouTube description from §0.1), **links**: "Free Day 1" → `{{DOMAIN}}/go?p=yt-{code}`, contact email `yt@`.
3. **Studio → Settings → Channel → Advanced settings → Audience:** "No, set this channel as not made for kids".
4. **Studio → Settings → Channel → Feature eligibility → Intermediate features → Verify phone number**.
5. **Studio → Settings → Upload defaults:** title template blank; description first line `{{DOMAIN}}/go?p=yt-{code}`; visibility **Private** (the pipeline sets Public when approved); comments "Hold potentially inappropriate comments for review". The **"Altered or synthetic content" = Yes** answer is set per upload in the upload flow and by our API (`status.containsSyntheticMedia: true`); if Upload defaults offers the field, set it to Yes there too **[verify on device]**.
6. **Studio → Settings → Permissions → Invite**: backup admin = Manager; VA = Editor (limited) (can upload and edit, can't delete the channel or change permissions).
7. Repeat for the other two channels (each is its own Brand Account under the same Google login).
8. Week 0: upload the pinned "Hi, we're AI" Short manually, mark altered/synthetic = Yes, and pin its comment with the waitlist link.

### 7.2 Google Cloud project for uploads (computer, `dev@`)
1. **console.cloud.google.com → New project** → `strongyears-publisher`.
2. **APIs & Services → Library →** enable **YouTube Data API v3** and **YouTube Analytics API**.
3. **OAuth consent screen:** User type **External** → app name `Strong Years Publisher`, support email, logo, app domain `{{DOMAIN}}`, privacy `{{DOMAIN}}/privacy`, terms `{{DOMAIN}}/terms`, authorized domain `{{DOMAIN}}` → **scopes:** `.../auth/youtube.upload`, `.../auth/youtube.readonly`, `.../auth/yt-analytics.readonly` → **Publishing status: In production** (in Testing, refresh tokens expire after 7 days) → submit for **Google verification** (upload is a sensitive scope).
4. **Credentials → Create credentials → OAuth client ID → Web application** → redirect URI from DEV (`{{APP_DOMAIN}}/api/oauth/youtube/callback`). Save the client ID/secret in 1Password and put them in the app's secret store (DEV tells you where), never in chat or email.
5. **YouTube API Services audit:** submit the "YouTube API Services – Audit and Quota Extension" form for the project. Until it passes, `videos.insert` uploads are private-only (projects created after 28 July 2020); the upload quota is 100 `videos.insert` calls per day per project ([videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert)). The pipeline uses upload-post until then.
6. **Authorize:** open DEV's connect link once per channel, sign in as `yt@`, pick the right Brand Account channel, approve.

---

## 8. X accounts + X developer app (D−27)

1. **x.com → Create account** → email `x.{page}@` → name from §0.1 → handle from §0.1 (X: letters, numbers, underscores, ≤15 characters).
2. **Edit profile:** bio (exact string), website `{{DOMAIN}}/go?p={code}`, picture, header.
3. **Settings and privacy → Security and account access → Security → Two-factor authentication → Authentication app**; save the backup code.
4. **Automation label [C, optional]:** **Settings → Your account → Account information → Automation** lets an account show "Automated by @{managing account}". Our posts are human-approved scheduled posts, so the label isn't required; the client decides. **[verify on device]**
5. **developer.x.com** (as `dev@`) → sign up for the pay-per-use tier → **Project + App** `Strong Years Publisher` → **User authentication settings:** OAuth 2.0, Web App, callback URL from DEV, website `{{DOMAIN}}`, scopes `tweet.read tweet.write users.read media.write offline.access` → save the Client ID/Secret in 1Password + the app secret store → prepaid credits only when the client approves (a few dollars covers launch volume, PIPELINE §5.3).
6. **Authorize** each X account through DEV's connect link.

---

## 9. ManyChat, upload-post, and pipeline access

### 9.1 ManyChat (D−24)
1. **manychat.com → Sign up** with `manychat@` (Google) → **create one workspace per page** (Chang, Sun kitchen, Duo).
2. In each workspace: **Settings → Channels → Instagram → Connect** (log in with the client's Facebook profile, pick the page's IG account; "Allow access to messages" must already be on, §4.8) and **Facebook → Connect** the matching Page.
3. Upgrade each workspace to **Pro** (keyword triggers on comments, email collection, external requests). Client pays; we never hold the card.
4. **Settings → Team:** invite the backup admin (Admin) and the operator (Live Chat agent).
5. **Settings → General → Bot name / About:** "Strong Years team assistant (automated). Chang Yin and Sun Yoon are AI characters." (FUNNEL §4.1).
6. Build the flows from FUNNEL.md §4.1–4.19 (runway mode: §4.18 + the runway link rule; from D0: §4.19). Test each keyword from a separate test IG account before D−21.
7. **External request** step to the n8n webhook (DEV supplies URL + secret) for email capture → `/api/leads`.

### 9.2 upload-post (fallback publisher; D−24)
1. **upload-post.com** → sign up with `dev@` → connect TikTok, YouTube, Facebook and Threads for each page through their OAuth screens → create the API key → store it in the app secret store. (Used until the TikTok and YouTube audits pass; PIPELINE §5.3.)

### 9.3 Meta access for the pipeline (D−24)
1. **developers.facebook.com** (as the client's profile, within the Strong Years business portfolio) → **My Apps → Create app** → use cases **"Manage messaging & content on Instagram"** and **"Manage everything on your Page"**, plus a **Threads** use case (Threads API) → connect the business portfolio.
2. App settings: privacy policy `{{DOMAIN}}/privacy`, terms, data-deletion URL `{{DOMAIN}}/privacy#delete`, icon, category. **Standard Access is enough for accounts the business owns** (no App Review needed for our own Pages and IG accounts; PIPELINE §5.3).
3. **Business Suite → Settings → Users → System users → Add** → `strongyears-publisher` (Admin role is not needed; Employee) → **Assign assets:** each Page (Content + Messages + Insights) and each Instagram account (Content + Insights + Comments) → **Generate new token** for the app with: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `pages_read_user_content`, `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments`, `instagram_manage_insights`, `business_management`, `read_insights`; token expiry **Never**. For Threads, authorize through the Threads OAuth flow DEV provides (`threads_basic`, `threads_content_publish`, `threads_manage_replies`, `threads_read_replies`, `threads_manage_insights`).
4. Paste the token **only** into the app's secret store (or a 1Password item shared with DEV). Never in chat, email or a doc.

### 9.4 Backup handles (planned, NOT created)
Write these into BRIEF.md's decision log; create one only if its main account is permanently lost:
`@changyin.strongyears`, `@sunyoon.kitchen.sy`, `@changandsun.strongyears` (IG/Threads/TikTok/YouTube); X `changyin_sy`, `sunyoonkitchen2`, `changandsun_sy`. When used: AI label on first, same bios, a "We moved here" post from the surviving pages, and week 1 of the ramp. Idle duplicate accounts are not created in advance because they look like a network and can't be warmed honestly.

---

## 10. Verification checklist (per page; all ✓ before runway day 1)

| Check | IG | FB | Threads | TikTok | YouTube | X |
|---|---|---|---|---|---|---|
| Created by the client, company alias email, password in 1Password | ☐ | n/a (admins' profiles) | n/a (IG login) | ☐ | ☐ | ☐ |
| Authenticator 2FA on, recovery codes saved; 2 admins | ☐ | ☐ (both admin profiles) | ☐ (via IG) | ☐ | ☐ | ☐ |
| Display name + handle per §0.1, recorded in BRIEF.md | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Bio = exact SAFETY §7 string (or approved short variant) | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| AI disclosure setting on (IG AI-generated profile label; TikTok AI toggle habit + `is_aigc`; YT altered/synthetic = Yes) with screenshot | ☐ | About text ☐ | bio ☐ | ☐ | ☐ | bio ☐ |
| Professional/business mode (IG Creator; TikTok Business; FB Page in business portfolio) | ☐ | ☐ | — | ☐ | — | — |
| Link = waitlist-mode `/go` or `/tt` and it loads | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Messages access for ManyChat; keyword test passes | ☐ | ☐ | — | DM keyword reply ☐ | — | — |
| Pipeline access granted via OAuth / system user (token in secret store) | ☐ | ☐ | ☐ | ☐ (audit submitted) | ☐ (audit submitted) | ☐ |
| Week-0 pinned posts live (native) | ☐ | ☐ | intro post ☐ | ☐ | pinned Short ☐ | intro post ☐ |
| Hidden words / comment filters on | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| No ads, no payment methods, no boosts | ☐ | ☐ | — | ☐ | — | ☐ |

Send DEV a note "accounts ready" with the list of handles (no passwords, no tokens) when every box is ticked.
