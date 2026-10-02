# Strong Years on Shopify: RUNBOOK

> **Superseded for order of operations, env vars, webhook topics and prices by [`../LAUNCH_RUNBOOK.md`](../LAUNCH_RUNBOOK.md) (Oct 1 2026 integration round; decisions in `../INTEGRATION.md`).** This file keeps the click-by-click detail. Where they differ: Digital Downloads is NOT used (the members app serves watermarked PDFs), the post-purchase app is OFF at launch, arm B ("$12 today = books + first month") is the default and A the test, `/join` and `/b` land on the product page (never a cart permalink), the webhook list is `config/webhook-topics.json`, and the API version is 2026-07 on both sides.

One command builds the store: `npm run provision` (Admin GraphQL **2026-07**, the latest stable version on 2026-10-01; 2026-10 is still the release candidate). It runs as a **dry run by default** and prints every GraphQL operation it would send. Nothing here has touched any live store. The K9SUPPS store is on a hard deny list in `src/client.ts`, so the script refuses it by domain and by name.

**Client clicks: about 175 in total**, in 18 steps (counted per step below). About 40 of the clicks are the test orders in step 17, and 24 are Digital Downloads uploads.

---

## 0. What exists (shopify/)

| Path | What it is |
|---|---|
| `config/catalog.ts` | Single source of truth: 10 products, 4 collections, selling-plan specs, discount codes, metafield definitions, webhook topics, redirects. Every price is a canon price. |
| `src/provision.ts` → `src/plan.ts` | Idempotent create-or-update. Keys: products/collections by handle, discounts by code, webhooks by topic+URI, pages by handle, redirects by path, metafield definitions by namespace+key. Phases: `core`, `verify`, `close-founding`. |
| `src/operations.ts` | All 29 GraphQL documents. Every one is validated against the Admin schema with Shopify's `validate_graphql_codeblocks`, and the input shapes are validated with inlined variables (`test/fixtures/schema-validation.json`). |
| `src/legal.ts` | Refund, subscription, terms, privacy, shipping and contact policies, plus the content pages (membership and cancellation, about the characters, FAQ, how we make this, safety, welcome). They are generated from OFFER.md and FUNNEL.md. |
| `src/webhooks.ts`, `src/seatLedger.ts` | The webhook contract and helpers for the members app: HMAC check, attribution parsing, order classification, and the founding seat ledger. |
| `theme/` | Online Store 2.0 theme ported from the approved prototype: landing (the /join equivalent, arm-aware), Starter Books page (cell-aware), membership page (FUNNEL §5.6), cell B page (`?view=starter`), gift, cart, account hub, FAQ, characters, legal, welcome. Self-hosted fonts. **Shopify Theme Check: 0 offenses.** |
| `app-postpurchase/` | The "Strong Years Offers" app: a post-purchase extension (one-click founding membership with BuyerConsent), a Thank you/Order status block, and the offer and changeset-signing server (`server/postPurchase.ts`) that the members app mounts. |
| `emails/` | The 3-email onboarding for Starter Books buyers. The **members app** sends them (Resend/Postmark via `app/src/lib/notify.ts`), not Shopify Email, because the emails branch on behavior (sessions done, became a member) that only the members app knows. |
| `test/` | 128 tests: DRY_RUN snapshots of every operation (both engines, all phases), plan invariants, SAFETY_RULES §3.1 regexes run over every published string, theme design and checkout-integrity rules, webhook, seat-ledger and post-purchase server tests. |

Run everything: `npm install && npm run check` (typecheck + tests + Theme Check).

---

## 1. Design decisions (and why)

**1.1 Price cells: one product per cell, not one product with 3 variants.** A variant selector exposes $7/$12/$15 on one page and in `/products/<handle>.js`, and a buyer can pick the cheapest. With separate products, each visitor sees exactly one real price, and that price is the one charged. The $12 product is the listed, indexable page. The $7 and $15 products are `UNLISTED` with `rel=canonical` to the $12 page and `noindex`. The layout assigns a sticky cell before first paint and routes the visitor to their cell's product, so there is no price flicker and no bait-and-switch.

**1.2 Subscription engine: Shopify Subscriptions (default, per canon).** The free Shopify Subscriptions app bills **only plans it owns**, and plans it owns can only be created in its UI. So `provision` creates the products, and the client creates 2 plans (step 10). `npm run verify` then checks them, makes the products subscription-only and writes the members-app catalog.
- **Cell B ("$12 today = books + first month, then $25/mo")** uses the native subscription discount `STARTER12`: $13 off the founding membership, **first payment only** (`recurringCycleLimit: 1`, `appliesOnSubscription: true`). The founding variant and the 5,000 cap are shared.
- The selling-plan **fixed first-cycle pricing policy** asked for in the brief is fully implemented in the alternative engine, `SUBSCRIPTION_ENGINE=app`. There, the Strong Years app owns the plans (fixed PRICE 12.00, then recurring after cycle 1 at PRICE 25.00, validated against the schema). That engine also needs a billing scheduler, which is not built here, plus `write_own_subscription_contracts` access. It stays off until someone builds that scheduler.

**1.3 Founding cap = real inventory (5,000) on the founding variant**, with policy DENY. It is set **only when the variant is first created**, so re-running never resets the count. Shopify Subscriptions renewal orders also decrement inventory and fail when stock is 0. `src/seatLedger.ts` handles this: each renewal gives its seat back (+1), a 14-day refund of the first charge gives the seat back, and a cancellation does not. At 0, the variant flips to CONTINUE so that existing members' renewals never fail. Then `npm run close-founding -- --yes-close-founding` unpublishes the founding product, activates the $35 standard product and sets `founding.closed`. The storefront counter reads inventory and follows the FUNNEL.md COUNT_LINE rule. It has no timer.

**1.4 Post-purchase one-click offer: our own app, two surfaces.** References: [About product offers](https://shopify.dev/docs/apps/build/checkout/product-offers), [Create a post-purchase subscription](https://shopify.dev/docs/apps/build/checkout/product-offers/create-a-post-purchase-subscription), [Thank you page extensions](https://shopify.dev/docs/apps/build/checkout/thank-you-order-status).
- Post-purchase extensions run on non-Plus plans. They are beta: a dev store works freely, but a **live store needs Shopify's access approval**.
- **Shopify cannot add a subscription post-purchase to an order without a shipping address.** A digital-only Starter Books order has no shipping address.
- The post-purchase page is also skipped for Apple Pay, Google Pay, PayPal, installments, and orders that already contain a subscription.
- So the one-click founding offer (`add_subscription` + `<BuyerConsent policy="subscriptions">` + full terms) shows only on book orders that include the $29 kit. Digital-only orders get a one-click $9 Wall Plan offer on that page instead.
- **Every** order also gets the **Thank you / Order status block** (Polaris web components). It links to the membership page, where the terms and the unticked consent checkbox are, and Shop Pay makes that checkout one tap for returning buyers. Those orders also get the 3 emails.
- The true "no second card entry" path for everyone is **cell B**: one checkout, one subscription.
- A third-party post-purchase app (e.g. AfterSell) would have the same Shopify limits. Its only advantage is that it is already approved, so it is the fallback if the access request stalls.

**1.5 Consent without Shopify Plus.** Checkout checkboxes need Plus. So the unticked, required auto-renewal checkbox sits on the membership page and in the cart, directly under the terms box.
- The theme records the consent on the order as `sy_consent_sha`, `sy_consent_at` and `sy_consent_price`: a SHA-256 of the exact terms and label text shown.
- The theme renders **no express or "Buy it now" buttons**, because they would bypass the consent and attribution. Shop Pay, Apple Pay and Google Pay are still offered inside checkout.
- Links in emails and on the thank-you page go to the product page, never to a cart permalink.

**1.6 Attribution.** The landing page captures `utm_*`, `post_id` (alias `pid`), `page`, `keyword`, `character`, `platform` and `mc_id` as first touch and last touch, and writes them as cart attributes. Shopify turns these into order `note_attributes`, which reach the members app in `orders/paid`.
- Names and limits match the members app reader exactly (`app/src/lib/billing/shopify.ts` `cartContextFromAttributes`): flat `sy_ft_<field>`, `sy_lt_<field>`, `sy_cell` (e7/e12/e15/m12), `sy_vid`, `sy_sku`, each value at most 100 characters.

---

## 2. Client steps (exact clicks)

> Do these in order. "→" is one click. Typing isn't counted.

**Step 1: Create the store (≈8 clicks).** shopify.com → Start free trial → name **Strong Years** → country **United States** → currency **USD** (it can't change after the first sale) → choose the **Basic** plan → Pick plan → Confirm. Use a new login or the Strong Years organization. Never the K9SUPPS one.

**Step 2: Domain (≈6).** Settings → Domains → Connect existing domain → `strongyears.com` → Next → Verify, after the DNS records are set.

**Step 3: Shopify Payments (≈14).**
- Settings → Payments → Activate Shopify Payments → complete the business and bank form → Submit.
- Shop Pay, Apple Pay and Google Pay are on by default: open Manage → confirm all three are ticked → Save.
- PayPal: Activate PayPal → log in → Connect.
- Statement descriptor: Shopify Payments → Manage → Statement descriptor **STRONGYEARS MEMBER** → Save.

**Step 4: Customer accounts (≈4).** Settings → Customer accounts → choose **Customer accounts** (the new, code-based ones; Shopify Subscriptions' cancel and pause screens live here) → Save.

**Step 5: Install the 2 free apps (≈6).** App Store → **Shopify Subscriptions** → Install → Install. App Store → **Digital Downloads** → Install → Install.

**Step 6: Create the Strong Years app (≈12).** New admin-created custom apps are disabled since Jan 1 2026, so this uses the Dev Dashboard.
1. dev.shopify.com → pick the organization that owns the store → Create app → name **Strong Years Offers** → Create.
2. Versions → New version → Access scopes → paste:
   `read_products,write_products,read_inventory,write_inventory,read_locations,read_publications,write_publications,read_discounts,write_discounts,read_content,write_content,read_online_store_pages,write_online_store_pages,read_legal_policies,write_legal_policies,read_online_store_navigation,write_online_store_navigation,read_orders,write_orders,read_customers,write_customers,read_markets_home,read_purchase_options`
3. → Release → Home → Install app → choose the Strong Years store → Install.
4. Settings → copy **Client ID** and **Client secret**.

**Step 7: Paste the credentials (0 clicks).**
1. Copy `shopify/.env.example` to `.env`.
2. Set `SHOPIFY_STORE`, `CONFIRM_STORE` (the same domain), `SHOPIFY_CLIENT_ID`, `SHOPIFY_CLIENT_SECRET`, `MEMBERS_APP_URL`, `COMPANY_LEGAL_NAME`, `MAILING_ADDRESS`, `SUPPORT_EMAIL`, `BILLING_PHONE`, `GOVERNING_STATE`.
3. Members app env:
   - `SHOPIFY_WEBHOOK_SECRET` = the **Client secret**. Shopify signs every webhook with the app secret; it can't be set per subscription.
   - `SHOPIFY_STORE_DOMAIN`.
   - `SHOPIFY_API_VERSION=2026-07`.

**Step 8: Provision (0 clicks).**
```
cd shopify && npm install
set -a; . ./.env; set +a
npm run provision                      # dry run: read the plan
DRY_RUN=false npm run provision        # live: ~110 operations, about a minute
```
Live mode refuses to run without `CONFIRM_STORE`, with any `{{PLACEHOLDER}}` left in the legal facts, without an https members URL, or against any store matching the deny list.

**Step 9: Theme (≈5).** `npx shopify theme push --path theme --unpublished --store <store>.myshopify.com`. Or zip `theme/` and use Online Store → Themes → Add theme → Upload zip file → choose file. Then → Publish → Publish.

**Step 10: Subscription plans (≈18).**
1. Apps → Subscriptions → Plans → + Plan → Title **Monthly, renews until you cancel** → leave "Offer discount" off → Delivery frequency **1 Month** → Add products → tick **Strong Years Founding Membership**, **Strong Years Membership**, **Strong Years Essentials** → Add → Save.
2. + Plan → Title **Yearly, renews until you cancel** → frequency **1 Year** → Add products → tick **Strong Years Founding Annual** → Add → Save.
3. Settings (in the Subscriptions app): set payment retries to **3 attempts, 3 days apart, then cancel**.
4. Then run `npm run verify`. It checks the plans, makes the 4 products subscription-only and writes `out/members-catalog.<store>.json`. Load that file into the members app `shopify_products` table.

**Step 11: Digital Downloads (≈24, 6 per product).** Apps → Digital Downloads → Create digital product (or "Add attachment") → pick the product → Upload file → Save, for each of:
- `strong-years-starter-books` ($12), `-c7` ($7) and `-c15` ($15): `products/strength_reset.pdf` + `products/strong_kitchen.pdf`. **Regenerate `strength_reset.pdf` first; see risk R6.**
- `the-wall-plan`: `products/twelve_week_printable.pdf`.

There is no public Admin API for Digital Downloads attachments, so this step can't be scripted. The founding product gets **no** attachment: the members app delivers its books (immediately for cell B, on day 15 for the keep-forever bonus).

**Step 12: Post-purchase app (≈12).**
1. `cd shopify/app-postpurchase && npm install && npx shopify app deploy`. Set `client_id` in `shopify.app.toml` first.
2. Dev Dashboard → app → API access → **Post-purchase extensions → Request access** → Submit.
3. Once Shopify approves: Settings → Checkout → Post-purchase page → select **Strong Years Offers** → Save.
4. Members app: mount `server/postPurchase.ts` at `/api/shopify/post-purchase/offer` and `/sign-changeset`. Env: `SHOPIFY_API_KEY`, `SHOPIFY_API_SECRET`, `SY_FOUNDING_VARIANT_ID`, `SY_FOUNDING_SELLING_PLAN_ID`, `SY_WALLPLAN_VARIANT_ID` and `SY_EBOOK_PRODUCT_IDS`, all from the verify output.

**Step 13: Thank-you block (≈7).** Settings → Checkout → Customize → page selector **Thank you** → Add app block → **Founding offer** → set URL `https://strongyears.com/products/founding-membership` and price `$25` → Save. Repeat on **Order status** (≈5 more).

**Step 14: Notifications (≈6).**
- Settings → Notifications → Order confirmation → Edit → paste the FUNNEL.md §5.5 B2 terms block inside `{% if subscription %}` → Save.
- Apps → Subscriptions → Settings → Notifications: confirm that the 3-day reminder is on.

**Step 15: Kit stock (≈4, when the kits arrive).** Products → The Strong Years Kit → Inventory → set quantity → Save. It is 0 until then, so the bump stays hidden. Real stock only.

**Step 16: Counsel review (0 clicks).** Have counsel review the generated policies at Settings → Policies and `/pages/membership-and-cancellation`: the 50-state auto-renewal matrix, CA, NY, MN, VA, the AI-character disclosure and privacy (WA MHMDA). Edit `src/legal.ts` and re-run provision, which overwrites the policies idempotently.

**Step 17: Test orders in test mode (≈40).**
1. Settings → Payments → Shopify Payments → Manage → **Enable test mode** → Save.
2. Place these, with card `4242 4242 4242 4242`:
   - (a) $12 books only. Expect the Wall Plan post-purchase offer (once approved), the thank-you block and email 1.
   - (b) Books + kit. Expect the founding post-purchase offer → accept with the box ticked → a contract appears under Apps → Subscriptions.
   - (c) `/join`: tick consent → founding $25. Check the order note attributes for `sy_consent_sha` and `sy_cell`, and that founding inventory went 5000 → 4999.
   - (d) Landing in arm B (`/?arm=B`): $12 at checkout with STARTER12, and the contract's next charge shows $25.
   - (e) Gift 3 months, with recipient properties.
   - (f) Refund order (c) from the members app and check the seat goes back.
   - (g) In Apps → Subscriptions → the contract → **Bill now**: the renewal order arrives, and the ledger gives the seat back.
3. Cancel one contract from the customer account and confirm it takes 2 screens.

**Step 18: Go live (≈7).** Disable test mode (Manage → untick → Save). Online Store → Preferences → Password protection → untick → Save.

---

## 3. After launch

- **Close the founding group** (cap reached or the close date passes): `npm run close-founding -- --yes-close-founding`. It is one-way.
- **Add an affiliate code:** add a row to `DISCOUNTS` in `config/catalog.ts` → `DRY_RUN=false npm run provision`. Codes take $2 off the books only and never touch the membership. Commission (30% recurring for 12 months) is computed by the members app from `discount_codes`.
- **Change a price:** edit `config/catalog.ts` → provision. Existing contracts keep their price, which is what makes "founding price locked" true. A price change for existing members needs the 30-day notice (FUNNEL §5.5 E).
- **Webhook self-heal:** Shopify deletes a webhook subscription after 19 consecutive failed deliveries (about 48 hours of retries), so a members-app outage can silently cut access events. Run `DRY_RUN=false SHOPIFY_STORE=… CONFIRM_STORE=… MEMBERS_APP_URL=https://… npm run webhooks:heal` every 15 minutes from the deploy host's cron. It re-creates missing topics and repoints wrong URIs from `config/webhook-topics.json`, writes nothing when all is well, and never deletes. Exit code 2 means it healed something: deliveries were lost, so reconcile orders since the last webhook the members app received. Shopify's own retries cover shorter outages.
- **Rollback:** every object has a stable handle or code. Re-running provision restores the configured state. The script never deletes anything.

---

## 4. Open risks (decide or verify) — R1, R4, R5, R6 and R7 were resolved in the Oct 1 integration round (INTEGRATION.md); the text below is kept as the record of what was open

- **R1. The members app expects `subscription_contracts/*` webhooks.** Those topics only fire for contracts **owned by the subscribing app**, and Shopify Subscriptions owns these. The webhook docs list them as requiring `read_own_subscription_contracts`.
  - In the default engine, membership state must come from `orders/paid` (every renewal is an order), `refunds/create` and `orders/cancelled`. Cancellation or pause then shows up as the absence of the next renewal order, and access lapses at period end plus `SHOPIFY_GRACE_DAYS`.
  - The members app's `cancelContract()` cannot cancel a Shopify Subscriptions contract. Its 14-day refund has to send the member to Shopify's cancel screen, or support cancels in the admin.
  - There is also no Admin webhook topic named "orders/refunded"; `refunds/create` is the refund event.
- **R2. Our own 7-day and 2-day renewal reminders** can't know about a cancellation made in Shopify's portal. Word them conditionally ("if your membership is still active…") or rely on Shopify Subscriptions' built-in 3-day reminder plus the yearly summary.
- **R3. Post-purchase access approval** for a live store is outside our control. Until it lands, the thank-you block, cell B and the emails carry the founding offer.
- **R4. The Essentials $12 save offer is not self-serve** with Shopify Subscriptions: customers can pause or cancel but not swap product. Support edits the contract in the admin, or the member re-subscribes.
- **R5. Cell B and STARTER12 are once per customer.** A returning customer who already used it sees $25 at checkout, not $12; checkout always shows the real total before payment. In the members catalog, cell B shares (variant, plan) with `founding_monthly`. The members app must tell them apart by the `STARTER12` code or `sy_sku=bundle_m12`, so the verify export omits a separate `bundle_m12` row in this engine.
- **R6. `products/strength_reset.pdf` still mentions the $1 7-day trial** (line 1875 of the .md source). CANON UPDATE 2 forbids it. Regenerate the PDF before uploading it in step 11.
- **R7. Digital Downloads delivers unwatermarked PDFs** (canon: watermarked downloads). The members app's watermarked copies can be the primary link in email 1, with Digital Downloads as the receipt fallback.
- **R8. Subscription-only digital products:** confirm with test (b) or (c) that Shopify Subscriptions bills a non-shipping product as expected.
- **R9. Founding renewals after the cap:** the ledger flips the variant to CONTINUE the moment stock reaches 0. If a renewal is billed in the seconds before that, Shopify Subscriptions retries it the next day. Confirm in test (g).
- **R10. Legal copy is a draft of our practices.** It is not legal advice. Step 16 is required.
