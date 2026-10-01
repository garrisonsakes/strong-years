import { isDeployed } from "./deployEnv";
/**
 * Central runtime configuration. Everything that differs between demo (mock) mode and
 * production is read here, so the rest of the code never touches process.env directly.
 *
 * Mock mode = any integration whose env vars are absent runs as a local stub:
 *  - no SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY  -> in-memory data store (seeded)
 *  - no STRIPE_SECRET_KEY                          -> built-in checkout simulator
 *  - no ANTHROPIC_API_KEY                          -> scripted character replies
 *  - no RESEND/POSTMARK/TWILIO keys                -> messages written to the outbox table
 */

function num(name: string, fallback: number): number {
  const raw = process.env[name];
  if (raw === undefined || raw === "") return fallback;
  const n = Number(raw);
  return Number.isFinite(n) ? n : fallback;
}

function str(name: string, fallback = ""): string {
  const raw = process.env[name];
  return raw === undefined || raw === "" ? fallback : raw;
}

export const env = {
  get siteUrl() {
    return str("NEXT_PUBLIC_SITE_URL", "http://localhost:3000").replace(/\/$/, "");
  },
  /**
   * Round 7 (C2): the coach chat needs the model-based crisis classifier on every
   * deploy that isn't explicitly local. Only `next dev` / vitest, or an in-memory
   * demo build that sets LOCAL_DEMO_BUILD=true (the e2e/screenshot servers),
   * may answer with rules and scripted replies. Never with real data, never on
   * Vercel production.
   */
  get chatRequiresModel() {
    return isDeployed();
  },
  get isProduction() {
    return process.env.NODE_ENV === "production" && process.env.VERCEL_ENV === "production";
  },
  get supabaseUrl() {
    return str("SUPABASE_URL", str("NEXT_PUBLIC_SUPABASE_URL"));
  },
  get supabaseServiceKey() {
    return str("SUPABASE_SERVICE_ROLE_KEY");
  },
  get stripeSecretKey() {
    return str("STRIPE_SECRET_KEY");
  },
  get stripeWebhookSecret() {
    return str("STRIPE_WEBHOOK_SECRET");
  },
  get allowLiveStripe() {
    return str("ALLOW_LIVE_STRIPE") === "true";
  },
  /** H5: local development only. Never honoured in a production deployment. */
  get devAllowUnsigned() {
    return str("DEV_ALLOW_UNSIGNED") === "true" && process.env.VERCEL_ENV !== "production" && !str("STRIPE_SECRET_KEY").includes("_live");
  },
  get anthropicKey() {
    return str("ANTHROPIC_API_KEY");
  },
  get anthropicModel() {
    return str("ANTHROPIC_MODEL", "claude-haiku-4-5");
  },
  /** Dev defaults exist ONLY while running on demo data; with real data they are required. */
  get sessionSecret() {
    const v = str("SESSION_SECRET");
    if (v) return v;
    if (!mode.mockDb) throw new Error("SESSION_SECRET is required when Supabase is configured.");
    return "dev-only-session-secret-change-me-0123456789";
  },
  get cronSecret() {
    const v = str("CRON_SECRET");
    if (v) return v;
    // With real data and no secret, cron is locked (random value nobody knows).
    return mode.mockDb ? "dev-cron-secret" : crypto.randomUUID();
  },
  get adminUser() {
    return str("ADMIN_USER", "admin");
  },
  get adminPassword() {
    return str("ADMIN_PASSWORD", "strongyears-demo");
  },
  get reviewerSigned() {
    // Reviewer gate (FUNNEL.md / SAFETY_RULES.md §7). Stays false until a licensed
    // reviewer has signed a contract. While false, only FALLBACK strings render.
    return str("REVIEWER_SIGNED") === "true";
  },
  get displayTimeZone() {
    return str("DISPLAY_TZ", "America/Los_Angeles");
  },
  get supportEmail() {
    return str("SUPPORT_EMAIL", "help@strongyears.example");
  },
  /** Shown on the policy pages. Set once the company is formed. */
  get legalEntity() {
    return str("LEGAL_ENTITY_NAME", "[Legal entity name to be confirmed]");
  },
  /** Billing questions line (canon: exists; nobody ever needs to call to cancel). */
  get billingPhone() {
    return str("BILLING_PHONE", "");
  },
  get privacyEmail() {
    return str("PRIVACY_EMAIL", str("SUPPORT_EMAIL", "help@strongyears.example"));
  },
  get mailingAddress() {
    return str("MAILING_ADDRESS", "[Company mailing address — set MAILING_ADDRESS]");
  },
  get friendshipLine() {
    // FUNNEL.md 4.14: verify the number before launch; blank = not shown.
    return str("FRIENDSHIP_LINE_NUMBER");
  },
};

export const mode = {
  get mockDb() {
    return !(env.supabaseUrl && env.supabaseServiceKey);
  },
  get mockStripe() {
    return !env.stripeSecretKey;
  },
  get mockAi() {
    return !env.anthropicKey;
  },
  get anyMock() {
    return this.mockDb || this.mockStripe;
  },
};

/** Prices in cents. Monthly price is a split-test input ($12/$15/$20/$25/$30). */
export const prices = {
  /**
   * What a $1 trial renews at. In blitz mode that's the founding test price
   * (default $25, BLITZ_TRIAL_PRICE_CENTS), not the old $20.
   */
  get monthly() {
    if (blitz.enabled) return num("BLITZ_TRIAL_PRICE_CENTS", blitz.defaultPriceCents);
    return num("PRICE_MONTHLY_CENTS", 2000);
  },
  get founding() {
    return num("PRICE_FOUNDING_CENTS", num("PRICE_MONTHLY_CENTS", 2000));
  },
  essentials: 1200,
  /** Founding annual from L35 (canon: $249). Not sold in the app yet. */
  annual: 24900,
  partner: 800,
  trialFee: 100,
  reset: 700,
  kitchen: 1700,
  bump: 900,
  programUpsell: 2700,
  kitUpsell: 2900,
  printablesDownsell: 700,
  gift3: 4900,
  gift12: 11900,
};

export const offerRules = {
  trialDays: 7,
  /** Arm A: 14-day money-back on the first full membership charge, counted from that charge. */
  guaranteeDaysTrialArm: 14,
  /** Arm B founding membership: 14-day money-back (BRIEF blitz addendum). */
  guaranteeDaysFoundingArm: 14,
  get foundingCap() {
    return num("FOUNDING_COHORT_CAP", 5000);
  },
  /** Share of visitors in arm B (founding, charge today). The rest see the $1 trial. */
  get armBShare() {
    return Math.min(1, Math.max(0, num("ARM_B_SHARE", 0.5)));
  },
  reminderHoursBeforeCharge: 48,
  annualReminderDays: 30,
};

function bool(name: string, fallback: boolean): boolean {
  const raw = process.env[name];
  if (raw === undefined || raw === "") return fallback;
  return raw === "true" || raw === "1";
}

/**
 * BLITZ CANON (BRIEF.md, Sep 30 2026) — the default configuration.
 * One primary offer: the founding membership, first month charged today, 14-day
 * money-back guarantee, price locked while subscribed, real capped cohort.
 * Set OFFER_MODE=standard to return to the OFFER.md $1-trial funnel.
 */
export const blitz = {
  get enabled() {
    return str("OFFER_MODE", "blitz") !== "standard";
  },
  /** Days 1–5 price test ($25 vs $30). When off, everyone sees the default price. */
  get priceTestOn() {
    return bool("BLITZ_PRICE_TEST", true);
  },
  get priceCells(): number[] {
    const cells = str("BLITZ_PRICE_CELLS", "2500,3000")
      .split(",")
      .map((x) => Number(x.trim()))
      .filter((x) => Number.isFinite(x) && x > 0);
    return cells.length ? cells : [2500, 3000];
  },
  get defaultPriceCents() {
    return num("BLITZ_DEFAULT_PRICE_CENTS", 2500);
  },
  /** Price for new members once the founding cohort is full (client decision, default $35). */
  get standardPriceCents() {
    return num("STANDARD_PRICE_CENTS", 3500);
  },
  /**
   * Both arms run from day 1: founding charge-today ($25 / $30 cells) vs the $1
   * trial (then the trial price). Split by ARM_B_SHARE (default 50/50), sticky per visitor.
   */
  get trialArmEnabled() {
    // CANON UPDATE 2 (Oct 1 2026): "No $1 trial. Ever." The arm stays in the code
    // (old tests, history) but nothing can switch it on, whatever TRIAL_ARM_ENABLED says.
    return false;
  },
  /** Standalone $7 / $17 front-end pages: built, but off in blitz mode (they're bumps now). */
  get frontEndPagesEnabled() {
    return bool("FRONTEND_PAGES_ENABLED", !this.enabled);
  },
};

/** SMS stays off until 10DLC / toll-free verification is approved (3–6 weeks). */
export const messaging = {
  get smsEnabled() {
    return bool("SMS_ENABLED", false);
  },
};

/** Payment processor routing (Stripe primary; Braintree adapter stubbed). */
export const processorConfig = {
  get routing(): "failover" | "split" {
    return str("PROCESSOR_ROUTING", "failover") === "split" ? "split" : "failover";
  },
  get braintreeShare() {
    return Math.min(1, Math.max(0, num("PROCESSOR_SPLIT_BRAINTREE", 0)));
  },
  get braintreeEnabled() {
    return bool("BRAINTREE_ENABLED", false);
  },
  /** Rolling 30-day volume guards in cents (0 = no cap). */
  get stripeCap() {
    return num("STRIPE_MONTHLY_CAP_CENTS", 0);
  },
  get braintreeCap() {
    return num("BRAINTREE_MONTHLY_CAP_CENTS", 0);
  },
};
