/**
 * Strong Years: the single source of truth for everything provision.ts creates.
 *
 * Canon: BRIEF.md CANON UPDATE 2 (binding), OFFER.md §0/§0.1, FUNNEL.md §5.
 * Every price here is a canon price. Change a price here, re-run `npm run provision`,
 * and the plan is re-applied idempotently (create-or-update by handle / code / title).
 *
 * Money is in USD dollars as strings (Shopify `Money` scalar).
 */

import WEBHOOK_TOPIC_FIXTURE from "./webhook-topics.json" with { type: "json" };

export type ProductRole =
  | "ebook"            // front-end Starter Books (one-time, digital)
  | "founding"         // Founding Membership (subscription, capped by inventory)
  | "standard"         // Standard membership after the founding cohort closes
  | "annual"           // Founding annual, offered after renewal 1
  | "essentials"       // $12 save offer
  | "gift"             // prepaid gift, no auto-renew
  | "bump_wallplan"    // $9 digital bump
  | "bump_kit"         // $29 physical bump
  | "coached"          // R3: 12-week coached group program (ASCENSION.md), $147/mo default, $97/$197 test cells
  | "prepaid"          // MONETIZATION_ENGINE.md §3: 12 months paid once, no auto-renew (Shop Pay Installments eligible). DRAFT: client decision
  | "gift_bundle";     // MONETIZATION_ENGINE.md §3: caregiver bundle (3-month gift + Starter Books for the buyer). DRAFT: client decision

export interface VariantSpec {
  /** Value for the single option (Shopify always needs one option). */
  option: string;
  price: string;
  sku: string;
  requiresShipping: boolean;
  tracked: boolean;
  /** Only applied when the product/variant is first created. Never re-applied (no silent resets). */
  initialQuantity?: number;
  inventoryPolicy: "DENY" | "CONTINUE";
  weightLb?: number;
  taxable: boolean;
}

export interface ProductSpec {
  handle: string;
  role: ProductRole;
  title: string;
  /** ACTIVE = listed; UNLISTED = reachable only by direct link (cells, save offers); DRAFT = not sellable yet. */
  status: "ACTIVE" | "UNLISTED" | "DRAFT";
  /** Online Store 2.0 template suffix (theme/templates/product.<suffix>.json). */
  templateSuffix: "ebook" | "membership" | "gift" | "bump" | "coached" | "";
  productType: string;
  tags: string[];
  optionName: string;
  variants: VariantSpec[];
  collections: string[];
  /** Subscription-only product (set in the verify phase, after the selling plan exists). */
  subscriptionOnly: boolean;
  /** Which selling-plan key(s) must be attached (see SELLING_PLANS). */
  sellingPlans?: string[];
  /** Pricing cell this product represents, if any. */
  cell?: string;
  seoTitle: string;
  seoDescription: string;
  descriptionHtml: string;
  /**
   * PDFs delivered for this product. INTEGRATION.md decision: the members app serves every PDF (watermarked with the
   * buyer's name, email and order; pdf-lib) after the orders/paid webhook grants access; Shopify's Digital Downloads
   * app cannot watermark, so it is NOT used for delivery. Kept here so the welcome email and the members app know
   * which books an order unlocks; never attached in Digital Downloads.
   */
  digitalFiles?: string[];
  publishToOnlineStore: boolean;
}

/** No founding seat cap (Garrison, Oct 2 2026): founding is open to everyone until the close date, then standard.
 *  null = unlimited. The founding variant is not inventory-tracked, so nothing can sell out or show a count. */
export const FOUNDING_CAP: number | null = null;
/** FUNNEL.md canonical: default L90 = Sat Jan 9 2027 (client decision). Override with FOUNDING_CLOSE_DATE. */
export const FOUNDING_CLOSE_DATE_DEFAULT = "2027-01-09";
export const FOUNDING_PRICE = "25.00";
export const STANDARD_PRICE = "35.00";
export const ANNUAL_PRICE = "249.00";
export const ESSENTIALS_PRICE = "12.00";
/** Cell B: $12 today = books + first founding month, then $25/mo. */
export const CELL_B_FIRST_CYCLE_PRICE = "12.00";

const DISCLOSURE_P =
  "<p><strong>Chang Yin and Sun Yoon are AI characters.</strong> Their life story is made up. The exercises and recipes are real, built from published guidelines for older adults. General fitness and nutrition education, not medical advice. Check with your doctor before starting new exercise.</p>";

const BOOKS_DESC = `<p>Two books to keep forever: <strong>Chang Yin's 7-Day Strength Reset</strong> (seven follow-along sessions of 8 to 12 minutes, most of them next to a chair and a kitchen counter, with an Easier and a Harder version of every move) and <strong>Sun Yoon's Strong Kitchen</strong> (protein at every meal, cheap food, and honest evidence grades on kitchen remedies).</p>
<p>Instant download. Large print. Yours to keep. Refund on request within 14 days.</p>
${DISCLOSURE_P}`;

function ebookCell(cell: string, price: string, handleSuffix: string, status: "ACTIVE" | "UNLISTED"): ProductSpec {
  return {
    handle: `strong-years-starter-books${handleSuffix}`,
    role: "ebook",
    title: "The Strong Years Starter Books",
    status,
    templateSuffix: "ebook",
    productType: "Digital book",
    tags: ["sy-ebook", `sy-cell-${cell}`, "digital"],
    optionName: "Format",
    variants: [{ option: "PDF download", price, sku: `SY-BOOKS-${cell.toUpperCase()}`, requiresShipping: false, tracked: false, inventoryPolicy: "CONTINUE", taxable: true }],
    collections: ["books"],
    subscriptionOnly: false,
    cell,
    seoTitle: "7-Day Strength Reset + Strong Kitchen | Strong Years",
    seoDescription: "Two large-print books to keep: a 7-day strength plan built for a chair and a kitchen counter, and a protein-first kitchen book with honest evidence grades.",
    descriptionHtml: BOOKS_DESC,
    digitalFiles: ["products/strength_reset.pdf", "products/strong_kitchen.pdf"],
    publishToOnlineStore: true,
  };
}

/**
 * Cell design (justified in RUNBOOK.md §Design decisions):
 * one product per price cell, not one product with three price variants.
 *  - A variant selector would expose all three prices on one page and in /products/<handle>.js,
 *    and a buyer could pick the cheapest variant; one product per cell shows each visitor exactly
 *    one real price that is the price charged.
 *  - Digital Downloads attaches per product/variant either way; reporting by product is cleaner.
 *  - The $12 cell is the canonical, listed, indexable page; $7 and $15 are UNLISTED with
 *    rel=canonical to the $12 page, so search sees one page.
 */
export const EBOOK_CELLS = [
  { id: "e12", price: "12.00", handle: "strong-years-starter-books", weight: 0.34, default: true },
  { id: "e7", price: "7.00", handle: "strong-years-starter-books-c7", weight: 0.33, default: false },
  { id: "e15", price: "15.00", handle: "strong-years-starter-books-c15", weight: 0.33, default: false },
] as const;

/**
 * Funnel arms (sticky per visitor, theme assigns, order carries `sy_arm`). CANON UPDATE 3 (BRIEF.md):
 *  B = LAUNCH DEFAULT: "$12 today = books + first month, then $25/mo" as ONE subscription purchase
 *      (founding plan + STARTER12 first-payment discount; no second card entry, no post-purchase page needed).
 *  A = TEST CELL: Starter Books one-time, founding offer on the thank-you page + 3 emails (the post-purchase
 *      app stays scaffolded but off by default: beta, needs access approval, never shows on digital-only orders
 *      or wallet/PayPal payments). Weights are the launch split; `default: true` marks what a visitor sees when the
 *      arm test is off (ARM_TEST_ON=false in the theme config).
 */
export const FUNNEL_ARMS = [
  // CANON UPDATE 6 (Oct 2 2026): T = "$12 today = Starter Books + a 7-day trial of the founding membership; first $25
  // on day 7, then monthly" is THE launch offer. It needs a selling plan with a 7-day trial period, which the free
  // Shopify Subscriptions app cannot make (INTEGRATION.md §9: trial-capable app, e.g. Appstle "Trial periods", or the
  // app engine). Until `npm run verify` finds that plan (name contains "7-day trial"), the theme and the members app
  // fall back to B automatically, so the store is never without an offer.
  { id: "T", weight: 1, cell: "t12", default: true },
  { id: "B", weight: 0, cell: "m12", default: false },
  { id: "A", weight: 0, default: false },
] as const;
/** The trial length of arm T (days). The plan must bill the first $25 exactly this many days after checkout. */
export const TRIAL_DAYS = 7;
/** Cell ids match the members app catalog (app/src/lib/billing/shopify.ts: e7, e12, e15, m12, t12). */

/**
 * R3 (BRIEF.md CANON UPDATE 4, ASCENSION.md): the 12-week coached group program, delivered by a certified
 * older-adult trainer (a real person), weekly video call, Chang's curriculum. Sold ONLY from inside the members app
 * (in-app triggers, never cold ads), on the Subscriptions app's monthly plan. One product per price cell, like the
 * ebook cells: each member sees exactly one real price. The honest cohort cap is real inventory: 0 until a coach is
 * hired and a cohort opens (RUNBOOK: set it to the cohort cap, 30–50), DENY when out, so nobody can buy a seat that
 * does not exist. The members app mirrors the count from its own enrollments table.
 */
export const COACHED_PRICE = "147.00";
export const COACHED_CELLS = [
  { id: "c147", price: "147.00", handle: "coached-12-week", sku: "SY-COACHED-147", default: true },
  { id: "c97", price: "97.00", handle: "coached-12-week-c97", sku: "SY-COACHED-97", default: false },
  { id: "c197", price: "197.00", handle: "coached-12-week-c197", sku: "SY-COACHED-197", default: false },
] as const;

function coachedCell(c: (typeof COACHED_CELLS)[number]): ProductSpec {
  const dollars = c.price.replace(/\.00$/, "");
  return {
    handle: c.handle,
    role: "coached",
    title: "Strong Years Coached: 12 weeks with a real coach",
    status: "UNLISTED",
    templateSuffix: "coached",
    productType: "Coached program",
    tags: ["sy-coached", `sy-cell-${c.id}`, "subscription"],
    optionName: "Plan",
    variants: [{ option: "Monthly", price: c.price, sku: c.sku, requiresShipping: false, tracked: true, initialQuantity: 0, inventoryPolicy: "DENY", taxable: true }],
    collections: ["membership"],
    subscriptionOnly: true,
    sellingPlans: ["monthly"],
    cell: c.id,
    seoTitle: "Strong Years Coached | 12 weeks with a certified coach",
    seoDescription: `A 12-week small-group program with a certified older-adult trainer: one live video call a week and a weekly check-in. $${dollars} a month, cancel online anytime.`,
    descriptionHtml: `<p>Twelve weeks in a small group with a <strong>certified older-adult fitness trainer, a real person</strong>. One live video call a week, a weekly check-in your coach reads, and Chang Yin's session plan in between.</p>
<p><strong>$${dollars} today, then $${dollars} a month until you cancel.</strong> The program is 12 weeks (three monthly payments). We email you before a fourth payment; cancel online anytime in your account. 14-day money-back guarantee on your first coached payment.</p>
<p>Groups are capped so your coach knows your name. When a group is full, the page says so.</p>
<p><strong>Chang Yin is an AI character; your coach is a real person.</strong> Coaching is general fitness instruction, not medical care or physical therapy. Check with your doctor before starting new exercise.</p>`,
    publishToOnlineStore: false,
  };
}

export const PRODUCTS: ProductSpec[] = [
  ebookCell("e12", "12.00", "", "ACTIVE"),
  ebookCell("e7", "7.00", "-c7", "UNLISTED"),
  ebookCell("e15", "15.00", "-c15", "UNLISTED"),
  {
    handle: "founding-membership",
    role: "founding",
    title: "Strong Years Founding Membership",
    status: "ACTIVE",
    templateSuffix: "membership",
    productType: "Membership",
    tags: ["sy-membership", "sy-founding", "subscription"],
    optionName: "Plan",
    variants: [{
      option: "Founding monthly",
      price: FOUNDING_PRICE,
      sku: "SY-FOUNDING-25",
      requiresShipping: false,
      tracked: false,
      inventoryPolicy: "CONTINUE",
      taxable: true,
    }],
    collections: ["membership"],
    subscriptionOnly: true,
    sellingPlans: ["monthly", "trial_7", "starter_b"],
    seoTitle: "Founding Membership | Strong Years",
    seoDescription: "Daily 8 to 12 minute strength sessions with Chang Yin (AI character), Sun Yoon's Sunday recipes and a monthly Strength Age retest. $25 a month, cancel online anytime.",
    descriptionHtml: `<p>Your Daily Practice with Chang Yin, 8 to 12 minutes a day at your level, with a chair-based version of everything. Sun Yoon's recipes every Sunday. A Strength Age you retest every month.</p>
<p><strong>$25 today for your first month, then $25 a month until you cancel.</strong> Founding price locked for as long as you stay subscribed. 14-day money-back guarantee on your membership charge, once per person. Cancel online anytime in your account.</p>
<p>The founding price is open to everyone who joins before the founding close date. There is no limit on founding memberships.</p>
${DISCLOSURE_P}`,
    publishToOnlineStore: true,
  },
  {
    handle: "strong-years-membership",
    role: "standard",
    title: "Strong Years Membership",
    status: "DRAFT", // goes ACTIVE in --phase=close-founding
    templateSuffix: "membership",
    productType: "Membership",
    tags: ["sy-membership", "sy-standard", "subscription"],
    optionName: "Plan",
    variants: [{ option: "Monthly", price: STANDARD_PRICE, sku: "SY-STANDARD-35", requiresShipping: false, tracked: false, inventoryPolicy: "CONTINUE", taxable: true }],
    collections: ["membership"],
    subscriptionOnly: true,
    sellingPlans: ["monthly"],
    seoTitle: "Strong Years Membership",
    seoDescription: "Daily strength sessions, Sunday recipes and a monthly Strength Age retest. $35 a month, cancel online anytime.",
    descriptionHtml: `<p>Your Daily Practice with Chang Yin, Sun Yoon's Sunday recipes and a monthly Strength Age retest.</p><p><strong>$35 today for your first month, then $35 a month until you cancel.</strong> 14-day money-back guarantee on your membership charge, once per person. Cancel online anytime.</p>${DISCLOSURE_P}`,
    publishToOnlineStore: false,
  },
  {
    handle: "founding-annual",
    role: "annual",
    title: "Strong Years Founding Annual",
    status: "UNLISTED",
    templateSuffix: "membership",
    productType: "Membership",
    tags: ["sy-membership", "sy-annual", "subscription"],
    optionName: "Plan",
    variants: [{ option: "Yearly", price: ANNUAL_PRICE, sku: "SY-ANNUAL-249", requiresShipping: false, tracked: false, inventoryPolicy: "CONTINUE", taxable: true }],
    collections: ["membership"],
    subscriptionOnly: true,
    sellingPlans: ["yearly"],
    seoTitle: "Founding Annual | Strong Years",
    seoDescription: "For founding members after their first renewal: $249 a year.",
    descriptionHtml: `<p>For founding members after their first renewal. <strong>$249 today, then $249 every year until you cancel.</strong> We email you 30 days before every yearly renewal. Cancel online anytime.</p>${DISCLOSURE_P}`,
    publishToOnlineStore: true,
  },
  {
    handle: "essentials-membership",
    role: "essentials",
    title: "Strong Years Essentials",
    status: "UNLISTED",
    templateSuffix: "membership",
    productType: "Membership",
    tags: ["sy-membership", "sy-essentials", "subscription"],
    optionName: "Plan",
    variants: [{ option: "Monthly", price: ESSENTIALS_PRICE, sku: "SY-ESSENTIALS-12", requiresShipping: false, tracked: false, inventoryPolicy: "CONTINUE", taxable: true }],
    collections: ["membership"],
    subscriptionOnly: true,
    sellingPlans: ["monthly"],
    seoTitle: "Strong Years Essentials",
    seoDescription: "The Daily Practice and the monthly retest for $12 a month.",
    descriptionHtml: `<p>The Daily Practice and the monthly Strength Age retest, without the extras. <strong>$12 a month until you cancel.</strong> Cancel online anytime.</p>${DISCLOSURE_P}`,
    publishToOnlineStore: true,
  },
  {
    handle: "gift-strong-years",
    role: "gift",
    title: "Give Strong Years (prepaid gift)",
    status: "ACTIVE",
    templateSuffix: "gift",
    productType: "Gift membership",
    tags: ["sy-gift", "no-auto-renew"],
    optionName: "Length",
    variants: [
      { option: "3 months", price: "49.00", sku: "SY-GIFT-3M", requiresShipping: false, tracked: false, inventoryPolicy: "CONTINUE", taxable: true },
      { option: "12 months", price: "119.00", sku: "SY-GIFT-12M", requiresShipping: false, tracked: false, inventoryPolicy: "CONTINUE", taxable: true },
    ],
    collections: ["gifts"],
    subscriptionOnly: false,
    seoTitle: "Give Mom or Dad Strong Years | Prepaid gift",
    seoDescription: "A prepaid gift membership: 3 months for $49 or 12 months for $119. One payment. It does not renew.",
    descriptionHtml: `<p>A prepaid gift membership. <strong>One payment. It does not renew.</strong> You choose the start date; the gift ends on the end date shown at checkout. Near the end, the person you gave it to can choose to continue on their own card. Nobody is charged automatically.</p>${DISCLOSURE_P}`,
    publishToOnlineStore: true,
  },
  {
    handle: "the-wall-plan",
    role: "bump_wallplan",
    title: "The Wall Plan + 12 grocery lists",
    status: "ACTIVE",
    templateSuffix: "bump",
    productType: "Printable",
    tags: ["sy-bump", "digital"],
    optionName: "Format",
    variants: [{ option: "PDF download", price: "9.00", sku: "SY-WALLPLAN-9", requiresShipping: false, tracked: false, inventoryPolicy: "CONTINUE", taxable: true }],
    collections: ["books"],
    subscriptionOnly: false,
    seoTitle: "The Wall Plan | Strong Years",
    seoDescription: "A large-print 12-week calendar for your fridge plus 12 weekly grocery lists.",
    descriptionHtml: `<p>A printable 12-week calendar for your fridge plus 12 weekly grocery lists from Sun Yoon. Large print, one page a week. Yours to keep, even if you cancel. Refund on request within 14 days.</p>${DISCLOSURE_P}`,
    digitalFiles: ["products/twelve_week_printable.pdf"],
    publishToOnlineStore: true,
  },
  {
    handle: "strong-years-kit",
    role: "bump_kit",
    title: "The Strong Years Kit",
    status: "ACTIVE",
    templateSuffix: "bump",
    productType: "Equipment",
    tags: ["sy-bump", "physical"],
    optionName: "Kit",
    variants: [{
      option: "Loops + door anchor + grip trainer",
      price: "29.00",
      sku: "SY-KIT-29",
      requiresShipping: true,
      tracked: true,
      initialQuantity: 0, // real stock only; set it when the kits arrive (RUNBOOK step 14)
      inventoryPolicy: "DENY",
      weightLb: 0.9,
      taxable: true,
    }],
    collections: ["gear"],
    subscriptionOnly: false,
    seoTitle: "The Strong Years Kit",
    seoDescription: "3 resistance loops, a door anchor and a grip trainer, with a large-print card.",
    descriptionHtml: `<p>You don't need equipment to start. Inside: 3 resistance loops (light, medium, heavy), a door anchor and a grip trainer, with a large-print card showing how Chang Yin uses each one. One payment, shipped to you. 30-day refund, no return needed.</p>${DISCLOSURE_P}`,
    publishToOnlineStore: true,
  },
  ...COACHED_CELLS.map(coachedCell),

  // ---------------------------------------------------------------- MONETIZATION_ENGINE.md §3 (proposals, DRAFT)
  // Both are DRAFT: provisioned so the client can review them in Shopify Admin, NOT sellable, NOT in the members
  // catalog (verify phase emits no row for them) until the client decides the price and flips the status. Activation
  // steps are in MONETIZATION_ENGINE.md §3.
  {
    handle: "strong-years-12-months-prepaid",
    role: "prepaid",
    title: "Strong Years, 12 months prepaid (does not renew)",
    status: "DRAFT",
    templateSuffix: "gift",
    productType: "Prepaid membership",
    tags: ["sy-prepaid", "no-auto-renew"],
    optionName: "Length",
    // Shop Pay Installments can't buy subscription products (help.shopify.com/en/manual/payments/shop-pay-installments/faq),
    // so the founding annual ($249/yr, a subscription) can never be split. This ONE-TIME product at the same $249 can:
    // US orders $35–$30,000 qualify. Same price as the annual, so nobody is shown two prices for a year.
    variants: [{ option: "12 months", price: ANNUAL_PRICE, sku: "SY-PREPAID-12M", requiresShipping: false, tracked: false, inventoryPolicy: "CONTINUE", taxable: true }],
    collections: ["membership"],
    subscriptionOnly: false,
    seoTitle: "Strong Years, 12 months prepaid",
    seoDescription: "Twelve months of Strong Years, paid once. It does not renew. Pay in installments with Shop Pay where eligible.",
    descriptionHtml: `<p>Twelve months of Strong Years for <strong>$249, paid once. It does not renew.</strong> Near the end we email you; continuing is your choice. Where Shop Pay Installments is offered at checkout, the lender shows its terms before you agree.</p>${DISCLOSURE_P}`,
    publishToOnlineStore: false,
  },
  {
    handle: "family-bundle",
    role: "gift_bundle",
    title: "Family bundle: a 3-month gift + the Starter Books for you",
    status: "DRAFT",
    templateSuffix: "gift",
    productType: "Gift membership",
    tags: ["sy-gift", "sy-bundle", "no-auto-renew"],
    optionName: "Bundle",
    variants: [{ option: "3-month gift + books", price: "55.00", sku: "SY-FAMILY-55", requiresShipping: false, tracked: false, inventoryPolicy: "CONTINUE", taxable: true }],
    collections: ["gifts"],
    subscriptionOnly: false,
    seoTitle: "Family bundle | Strong Years",
    seoDescription: "Give a parent 3 months of Strong Years and get the Starter Books yourself. One payment. Nothing renews.",
    descriptionHtml: `<p>A 3-month prepaid gift for someone you love, and the Starter Books for you, so you can do Day 1 together on a call. <strong>One payment. Nothing renews.</strong></p>${DISCLOSURE_P}`,
    publishToOnlineStore: false,
  },
];

export interface CollectionSpec { handle: string; title: string; descriptionHtml: string; }
export const COLLECTIONS: CollectionSpec[] = [
  { handle: "books", title: "Books and printables", descriptionHtml: "<p>Large-print books and printables to keep.</p>" },
  { handle: "membership", title: "Membership", descriptionHtml: "<p>Strong Years membership plans. Every plan renews until you cancel and can be cancelled online.</p>" },
  { handle: "gifts", title: "Gifts", descriptionHtml: "<p>Prepaid gift memberships. They do not renew.</p>" },
  { handle: "gear", title: "Gear", descriptionHtml: "<p>Simple equipment Chang Yin uses.</p>" },
];

/**
 * Selling plans. Two engines (RUNBOOK §Design decisions):
 *  - "shopify_subscriptions" (DEFAULT, canon): plans are created by the client inside the free
 *    Shopify Subscriptions app (it only bills plans it owns). provision.ts verifies them.
 *    Cell B's "$12 first month" is the native subscription discount limited to the first payment.
 *  - "app": provision.ts creates SellingPlanGroups owned by the Strong Years custom app, including a
 *    fixed first-cycle pricing policy for cell B. The app must then run billing itself.
 */
export interface SellingPlanSpec {
  key: string;
  /** Name customers see (Shopify Subscriptions "Title"). */
  name: string;
  interval: "MONTH" | "YEAR";
  intervalCount: number;
  /** Trial length in days (canon 6): the first charge is this many days after checkout, $0 at checkout. */
  trialDays?: number;
  /** For the app engine only: first-cycle price then recurring price. */
  firstCyclePrice?: string;
  recurringPrice?: string;
  description: string;
}
export const SELLING_PLANS: SellingPlanSpec[] = [
  { key: "monthly", name: "Monthly, renews until you cancel", interval: "MONTH", intervalCount: 1, description: "Billed every month on the same date until you cancel. Cancel online anytime." },
  // CANON UPDATE 6. Created by hand in the trial-capable subscription app (Appstle: plan → "Trial period" 7 days) or by
  // provision.ts in the app engine (pricing policy: first cycle 100% off + the app sets nextBillingDate = checkout + 7
  // days and runs the day-7 billing attempt). verifyPhase keys on the name containing "7-day trial".
  { key: "trial_7", name: "7-day trial, then $25 a month", interval: "MONTH", intervalCount: 1, trialDays: TRIAL_DAYS, firstCyclePrice: "0.00", recurringPrice: FOUNDING_PRICE, description: "$0 today. Your first $25 is charged 7 days after checkout, then $25 every month on the same date until you cancel. Cancel online anytime; cancel in the first 7 days and the membership costs nothing." },
  { key: "yearly", name: "Yearly, renews until you cancel", interval: "YEAR", intervalCount: 1, description: "Billed every year until you cancel. We email you 30 days before each renewal." },
  {
    key: "starter_b",
    name: "$12 first month with the Starter Books, then $25 a month",
    interval: "MONTH",
    intervalCount: 1,
    firstCyclePrice: CELL_B_FIRST_CYCLE_PRICE,
    recurringPrice: FOUNDING_PRICE,
    description: "$12 today for the Starter Books and your first founding month, then $25 every month until you cancel.",
  },
];

export interface DiscountSpec {
  code: string;
  title: string;
  kind: "books_fixed" | "starter_first_payment" | "winback_first_payment" | "group_quantity";
  amount: string;
  oncePerCustomer: boolean;
  /** Who it's for: tracking for affiliates and page shoutouts (commission is paid by the members app). */
  owner: string;
  /** starter_first_payment / winback_first_payment: the single membership product the code applies to; group_quantity: the gift product. */
  product?: string;
  /** group_quantity only: minimum quantity of the product in the cart. */
  minQuantity?: number;
  /** group_quantity only: percentage off as a fraction (0.2 = 20%). */
  percent?: number;
}

/**
 * Discounts.
 *  - STARTER12 is cell B in the shopify_subscriptions engine: $13 off the founding membership's FIRST
 *    payment only (recurringCycleLimit 1), subscription purchases only → $12 today, then $25/mo.
 *  - Page/affiliate codes take $2 off the Starter Books (one-time purchases only, never the membership,
 *    so MRR is never discounted). Attribution, not price cutting. Add affiliates in config/affiliates.json.
 */
export const DISCOUNTS: DiscountSpec[] = [
  // Cell B = LAUNCH DEFAULT (BRIEF.md CANON UPDATE 3). STARTER12: $13 off the founding membership's first payment only
  // ($25 → $12 today, then $25/mo). STARTER12S: $23 off the standard membership's first payment once the founding group is
  // closed ($35 → $12 today, then $35/mo). appliesOncePerCustomer: a returning customer who already used the code sees the
  // plain membership price at checkout, never a second $12 month. Auto-applied by the /discount/<CODE> share link the
  // members app's /b and /join redirect through, and re-applied by the theme's offer form (data-sy-discount).
  { code: "STARTER12", title: "Cell B: Starter Books + first founding month for $12", kind: "starter_first_payment", amount: "13.00", oncePerCustomer: true, owner: "cell-B", product: "founding-membership" },
  { code: "STARTER12S", title: "Cell B after the founding close: Starter Books + first month for $12", kind: "starter_first_payment", amount: "23.00", oncePerCustomer: true, owner: "cell-B", product: "strong-years-membership" },
  { code: "CHANG", title: "Page code: Chang Yin page", kind: "books_fixed", amount: "2.00", oncePerCustomer: true, owner: "page:chang" },
  { code: "SUNYOON", title: "Page code: Sun Yoon kitchen page", kind: "books_fixed", amount: "2.00", oncePerCustomer: true, owner: "page:sun" },
  { code: "CHANGANDSUN", title: "Page code: duo page", kind: "books_fixed", amount: "2.00", oncePerCustomer: true, owner: "page:duo" },
  // MONETIZATION_ENGINE.md §3. Win-back by lapse length (routing table "winback"): first payment only, once per customer,
  // the membership product only. Sent only to lapsed members by the members app (/b?t=WINBACK applies the code through
  // the /discount/<CODE> share link); the page shows the code price and the plan price, so the consent record matches.
  // ≤30 days lapsed: no code (rejoin at the public price). 31–90: $12 first month back. 90+: $9 first month back.
  { code: "WINBACK12", title: "Win-back 31-90 days: first month back $12 (founding)", kind: "winback_first_payment", amount: "13.00", oncePerCustomer: true, owner: "winback", product: "founding-membership" },
  { code: "WINBACK12S", title: "Win-back 31-90 days: first month back $12 (standard)", kind: "winback_first_payment", amount: "23.00", oncePerCustomer: true, owner: "winback", product: "strong-years-membership" },
  { code: "WINBACK9", title: "Win-back 90+ days: first month back $9 (founding)", kind: "winback_first_payment", amount: "16.00", oncePerCustomer: true, owner: "winback", product: "founding-membership" },
  { code: "WINBACK9S", title: "Win-back 90+ days: first month back $9 (standard)", kind: "winback_first_payment", amount: "26.00", oncePerCustomer: true, owner: "winback", product: "strong-years-membership" },
  // Group rate: 20% off 5 or more gift seats in one order. Given by a person after the /ask/group quote form; never
  // advertised as a public code. (Shopify B2B quantity price breaks need Plus; a quantity-minimum code works on Basic.)
  { code: "GROUP5", title: "Group rate: 20% off 5+ gift seats (quote)", kind: "group_quantity", amount: "0", percent: 0.2, minQuantity: 5, oncePerCustomer: false, owner: "group-quote", product: "gift-strong-years" },
];

/** Codes the system issues (never affiliate/page codes): excluded from affiliate crediting. */
export const SYSTEM_CODES = ["STARTER12", "STARTER12S", "WINBACK12", "WINBACK12S", "WINBACK9", "WINBACK9S", "GROUP5"] as const;

/**
 * Hardship / "pay what you can" (MONETIZATION_ENGINE.md §3). Never a shared public code. The /ask/price form files an
 * exception; a person reads it and, if they agree, issues a SINGLE-USE code for that one customer (Discounts → Create
 * → Amount off products → limit to 1 use, the membership product, recurring for the cycles below). The copy promises a
 * person reads it, nothing more. Budget cap keeps it sustainable and is reviewed monthly.
 */
export const HARDSHIP_POLICY = {
  method: "human_issued_single_use_code",
  codePrefix: "SYHELP",
  options: [
    { label: "Essentials price on the full membership", firstCyclesPrice: "12.00", cycles: 6 },
    { label: "Half price", percentOff: 50, cycles: 6 },
  ],
  monthlyBudgetSeats: 50,
  reviewSla: "2 business days",
} as const;

/**
 * Regional pricing via Shopify Markets (MONETIZATION_ENGINE.md §3). Launch sells in the US only (USD store). Other
 * markets stay CLOSED until two things are verified on the live store: (1) the free Shopify Subscriptions app bills
 * the membership correctly in the market's currency, (2) tax/VAT registration. Price adjustments apply via the market's
 * price list (percentage) to ONE-TIME products only; membership prices stay the catalog prices. The routing table's
 * open_countries mirrors the "open" markets; closed countries get the free waitlist.
 */
export const MARKETS = [
  { handle: "us", name: "United States", countries: ["US"], currency: "USD", open: true, priceAdjustmentPercent: 0 },
  { handle: "ca", name: "Canada", countries: ["CA"], currency: "CAD", open: false, priceAdjustmentPercent: 0 },
  { handle: "uk-ie", name: "UK and Ireland", countries: ["GB", "IE"], currency: "GBP", open: false, priceAdjustmentPercent: 0 },
  { handle: "anz", name: "Australia and New Zealand", countries: ["AU", "NZ"], currency: "AUD", open: false, priceAdjustmentPercent: 0 },
  { handle: "ppp", name: "Lower purchasing-power markets", countries: ["PH", "IN", "MX", "BR", "ZA"], currency: "USD", open: false, priceAdjustmentPercent: -40 },
] as const;

/** Members app (Next.js, members.<domain>) receives every webhook here; topic is in X-Shopify-Topic. Matches the route the members app already has. */
export const WEBHOOK_PATH = "/api/webhooks/shopify"; // app/src/app/api/webhooks/shopify/route.ts

/**
 * Webhook contract, shared with the members app through config/webhook-topics.json (the app's contract test reads
 * the same file). CORE topics fire store-wide for any app holding the scope (orders/*, refunds/create, customers/*,
 * inventory_levels/update, app/uninstalled): the members app provisions and revokes access from these alone.
 * orders/paid fires for every Shopify Subscriptions renewal order (source_name "subscription_contract"), which is how
 * renewals extend access. ENRICHMENT topics (subscription_contracts/*, subscription_billing_attempts/*) require
 * read_own_subscription_contracts and fire only for contracts owned by the subscribing app
 * (https://shopify.dev/docs/api/admin-graphql/latest/enums/WebhookSubscriptionTopic); Shopify Subscriptions owns these
 * contracts, so they are registered only in the app engine and are never the source of truth.
 * There is no "orders/refunded" topic in the Admin API; refunds/create is the refund event.
 */
const toEnum = (t: string) => t.toUpperCase().replace("/", "_");
export const WEBHOOK_TOPICS_CORE = WEBHOOK_TOPIC_FIXTURE.core.map(toEnum) as readonly string[];
export const WEBHOOK_TOPICS_APP_ENGINE = WEBHOOK_TOPIC_FIXTURE.enrichment.map(toEnum) as readonly string[];

export interface MetafieldDefSpec {
  ownerType: "SHOP" | "PRODUCT" | "ORDER" | "CUSTOMER";
  key: string;
  name: string;
  type: "json" | "single_line_text_field" | "boolean" | "number_integer" | "date_time";
  description: string;
  storefront: "PUBLIC_READ" | "NONE";
}
export const METAFIELD_NAMESPACE = "strong_years";
export const METAFIELD_DEFINITIONS: MetafieldDefSpec[] = [
  { ownerType: "SHOP", key: "cells", name: "Pricing cells", type: "json", description: "Ebook price cells and funnel arms with weights. The theme assigns one per visitor (sticky).", storefront: "PUBLIC_READ" },
  { ownerType: "SHOP", key: "founding", name: "Founding cohort", type: "json", description: "Close date, standard price, closed flag (cap is null: no seat limit since Oct 2 2026). Formerly the seat count was the founding variant's real inventory.", storefront: "PUBLIC_READ" },
  { ownerType: "SHOP", key: "links", name: "Links and company", type: "json", description: "Members app URL, support email, billing phone, company legal name and mailing address.", storefront: "PUBLIC_READ" },
  { ownerType: "PRODUCT", key: "role", name: "Strong Years role", type: "single_line_text_field", description: "ebook | founding | standard | annual | essentials | gift | bump_wallplan | bump_kit | coached", storefront: "PUBLIC_READ" },
  { ownerType: "PRODUCT", key: "cell", name: "Price cell", type: "single_line_text_field", description: "Price cell this product sells (e7, e12, e15, c147, c97, c197).", storefront: "PUBLIC_READ" },
  { ownerType: "ORDER", key: "cell", name: "Cell and arm", type: "single_line_text_field", description: "Written by the members app from note attributes (_sy_cell, _sy_arm).", storefront: "NONE" },
  { ownerType: "ORDER", key: "attribution", name: "Attribution", type: "json", description: "First and last touch: utm_*, post_id, page, keyword, character. Written by the members app from note attributes.", storefront: "NONE" },
  { ownerType: "ORDER", key: "consent", name: "Auto-renewal consent record", type: "json", description: "Exact terms text hash, timestamp, price, cell. Kept 3+ years (California ARL).", storefront: "NONE" },
  { ownerType: "CUSTOMER", key: "first_touch", name: "First touch", type: "json", description: "First recorded attribution for this customer.", storefront: "NONE" },
  { ownerType: "CUSTOMER", key: "cell", name: "Cell and arm", type: "single_line_text_field", description: "Sticky cell/arm at first purchase.", storefront: "NONE" },
  { ownerType: "CUSTOMER", key: "guarantee_used", name: "14-day money-back guarantee used", type: "boolean", description: "Once per person. Set by the members app when a membership refund is issued.", storefront: "NONE" },
];

/** URL redirects (Online Store → Navigation → URL redirects). */
export const REDIRECTS = [
  { path: "/join", target: "/products/founding-membership" },
  { path: "/start", target: "/" },
  { path: "/books", target: "/products/strong-years-starter-books" },
  { path: "/gift", target: "/products/gift-strong-years" },
  { path: "/terms", target: "/pages/membership-and-cancellation" },
  { path: "/safety", target: "/pages/safety" },
  { path: "/how-we-make-this", target: "/pages/how-we-make-this" },
];
