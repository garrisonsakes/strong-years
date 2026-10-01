# Day-1 profile copy: @changyin and @sunyoon.kitchen (Instagram + Facebook)

Copy everything between the backticks exactly. Replace `{{DOMAIN}}` with the live site domain (one value, everywhere). Bios are the SAFETY_RULES §7 FALLBACK strings from ACCOUNT_SETUP.md §0.1: don't reword them.

## Chang Yin

| Field | Paste this |
|---|---|
| Display name (IG + FB Page name) | `Chang Yin · AI character` |
| Handle | `changyin` |
| Instagram bio | `Chang Yin, 74 (AI character) · Strength after 60, done safely · Real research, sources linked · 👇 Free 7-day plan` |
| Facebook intro (about 100-character limit; the full bio doesn't fit) | `Chang Yin, 74 · AI character · Strength after 60 · Sources linked` (the approved short variant: log it as a SAFETY §7 platform variant before use) |
| Facebook "About" (long description) | `Chang Yin, 74 (AI character) · Strength after 60, done safely · Real research, sources linked · 👇 Free 7-day plan` then a new line, then `Characters are AI. Content is built on published research (sources on our site).` then a new line, then `Made by the Strong Years team. Not medical advice; check with your doctor before starting new exercise.` |
| Link (IG "Add external link" + FB website) | `https://{{DOMAIN}}/go?p=cy` |
| Link title (IG) | `Free Day 1` |
| Profile picture | `production/launch_day/pfp/chang_profile_1080.png` |

## Sun Yoon

| Field | Paste this |
|---|---|
| Display name (IG + FB Page name) | `Sun Yoon · AI character` |
| Handle | `sunyoon.kitchen` |
| Instagram bio | `Sun Yoon, 76 (AI character) · His wife. Blunter than him. · Real recipes, real research · 👇 Free soup book` |
| Facebook intro (about 100-character limit; the full bio doesn't fit) | `Sun Yoon, 76 · AI character · Real recipes, real research` (same short-variant rule) |
| Facebook "About" (long description) | `Sun Yoon, 76 (AI character) · His wife. Blunter than him. · Real recipes, real research · 👇 Free soup book` then a new line, then `Characters are AI. Content is built on published research (sources on our site).` then a new line, then `Made by the Strong Years team. Not medical advice; check with your doctor before starting new exercise.` |
| Link (IG "Add external link" + FB website) | `https://{{DOMAIN}}/go?p=sk` |
| Link title (IG) | `Free Day 1` |
| Profile picture | `production/launch_day/pfp/sun_profile_1080.png` |

The `/go` hub is in runway (waitlist) mode until checkout opens: the free waitlist shows first, then switches itself on D0. Put tracking (UTMs) only inside the `/go` tiles, never in the bio URL.

## Profile-picture crop (from the seed images approved today)

| | Source | Crop box (x0, y0, x1, y1), px | Output |
|---|---|---|---|
| Chang | `production/refs/out/concepts/chang_a.png` (1536×2048) | `210, 0, 1360, 1150` (1150 px square, face centred) | 1080×1080 PNG |
| Sun | `production/refs/out/concepts/sun_a.png` (1536×2048) | `130, 0, 1280, 1150` | 1080×1080 PNG |

- Both platforms show the picture as a circle. Keep the face inside the middle 70% and keep the top of the hair inside the frame.
- The **"AI" corner mark** is baked in: white "AI" on a near-black (#111111) rounded pill, bottom-right at 700–850 × 800–900 px. Its farthest corner sits 475 px from the centre, so the 540 px circle never clips it.
- Rebuild the files with `python3 production/launch_day/render_day1.py --stage pfp` (local only, no API).
- **Swap later:** chang_a still shows the long beard and the sleeveless shirt (the crop already cuts off the gold cuff). Once the lock pack is approved, re-crop the locked `C01` / `S01` the same way: same face centring, same AI mark.
- Cover/banner (FB): the home-world set with `AI characters · Real research` in full-contrast text (ACCOUNT_SETUP §0.1). Not made tonight.

## Story highlights (create each one when it has its first Story; covers are a solid colour with the name in full-contrast type)

| Chang | Sun |
|---|---|
| `Start here` (the AI disclosure + how the pages work) | `Start here` |
| `Day 1 free` (waitlist link sticker → `/waitlist`) | `Day 1 free` |
| `Sources` (one study card per Story) | `Sources` |
| `How we're made` | `How we're made` |
| `Chair test` | `Soups` |

## Pinned posts (ORGANIC_ENGINE §3.5, runway window)

| Pin | Chang | Sun | When |
|---|---|---|---|
| 1 | "Hi, we're AI" (duo, CHARACTERS §9.2) | same video | When rendered (needs the duo shot; not in tonight's set) |
| 2 | "How we choose studies" (FALLBACK wording, no review claim) | same | When rendered |
| 3 | **D1-CY-1 = S158 "Not a doctor, not a real person"** | **D1-SK-1 = S167 "Are you even real?"** | **Tonight, right after it posts** |

- Instagram: open the post → ⋯ → **Pin to your profile** (up to 3 pins).
- Facebook Page: open the post → ⋯ → **Pin post** (pins one post at a time) **[verify on device]**.

## AI-label toggles (do these before the first post)

**Instagram, once per account:** Edit profile → **AI-generated profile** → On (introduced Aug 31 2026; may sit under Settings → Account type and tools **[verify on device]**). Screenshot the profile showing the label and save it in 1Password.

**Instagram, every post:** Share screen → **Advanced settings** → **AI info / Add AI label** → On.

**Facebook, every post:** Reel composer → **AI info** (may read "Made with AI") → On **[verify on device]**. The caption keeps the AI-character footer as written; the intro and About text already say "AI character".

The burned-in `AI character` corner tag is in every video file. Never crop it out and never cover it with a sticker.
