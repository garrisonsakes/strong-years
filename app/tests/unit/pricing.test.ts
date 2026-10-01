import { describe, expect, it } from "vitest";
import { addMonths, foundingSpots, quoteCheckout, validateCheckout, type ConsentInput } from "@/lib/pricing";
import { buildMetaPayload, containsConditionWord, MetaSafetyError, safeSourceUrl } from "@/lib/analytics/meta";
import { attributionFromUrl, withMcId } from "@/lib/analytics/attribution";

const now = new Date("2026-10-01T17:00:00Z");
const opts = { now, monthlyCents: 2000, foundingCents: 2000, timeZone: "America/Los_Angeles", domain: "strongyears.com" };

describe("quoteCheckout — arm A ($1 trial)", () => {
  const q = quoteCheckout({ ...opts, offer: "trial", arm: "A", bump: false });
  it("charges $1 today and $20/month from day 7", () => {
    expect(q.todayCents).toBe(100);
    expect(q.recurring).toMatchObject({ priceCents: 2000, trialDays: 7, founding: false });
    expect(q.recurring!.nextChargeAt.toISOString()).toBe("2026-10-08T17:00:00.000Z");
  });
  it("puts every material term in the box above the button", () => {
    const text = q.terms.join(" ");
    expect(text).toMatch(/Today: \$1\.00/);
    expect(text).toMatch(/Thursday, October 8, 2026/);
    expect(text).toMatch(/renews at \$20\.00/);
    expect(text).toMatch(/until you cancel/);
    expect(text).toMatch(/at most two screens/);
    expect(text).toMatch(/48 hours/);
    expect(q.requiresAutoRenewConsent).toBe(true);
    expect(q.consentLabel).toMatch(/I agree to the automatic renewal terms/);
    expect(q.buttonLabel).toBe("Start my $1 trial");
    expect(q.guaranteeDays).toBe(14);
  });
  it("adds the $9 bump only when ticked", () => {
    expect(quoteCheckout({ ...opts, offer: "trial", arm: "A", bump: true }).todayCents).toBe(1000);
  });
  it("gentle (Safe Mode / P6) path never shows a bump", () => {
    const g = quoteCheckout({ ...opts, offer: "trial", arm: "A", bump: true, gentle: true });
    expect(g.bumpAllowed).toBe(false);
    expect(g.todayCents).toBe(100);
  });
});

describe("quoteCheckout — arm B (founding, charge today)", () => {
  const q = quoteCheckout({ ...opts, offer: "founding", arm: "B", bump: false });
  it("charges the first month today, renews one month later, 14-day guarantee, founding price", () => {
    expect(q.todayCents).toBe(2000);
    expect(q.recurring).toMatchObject({ trialDays: 0, founding: true });
    expect(q.recurring!.nextChargeAt.toISOString()).toBe(addMonths(now, 1).toISOString());
    expect(q.guaranteeDays).toBe(14);
    expect(q.terms.join(" ")).toMatch(/14-day money-back/);
    expect(q.terms.join(" ")).toMatch(/as long as you stay subscribed/);
  });
});

describe("front ends", () => {
  it("arm A $7 Reset includes 7 days of membership", () => {
    const q = quoteCheckout({ ...opts, offer: "reset", arm: "A", bump: false });
    expect(q.todayCents).toBe(700);
    expect(q.recurring!.trialDays).toBe(7);
    expect(q.terms[0]).toMatch(/includes 7 days of Strong Years/);
  });
  it("arm B $17 Kitchen charges product + first month today", () => {
    const q = quoteCheckout({ ...opts, offer: "kitchen", arm: "B", bump: true });
    expect(q.lines.map((l) => l.kind)).toEqual(["front_end", "membership_first_month", "bump"]);
    expect(q.todayCents).toBe(1700 + 2000 + 900);
    expect(q.recurring!.founding).toBe(true);
  });
  it("gifts are prepaid, never auto-renew and need no auto-renew consent", () => {
    const q = quoteCheckout({ ...opts, offer: "gift12", arm: "A", bump: true });
    expect(q.todayCents).toBe(11900);
    expect(q.recurring).toBeNull();
    expect(q.requiresAutoRenewConsent).toBe(false);
    expect(q.terms.join(" ")).toMatch(/never renews automatically/);
    expect(q.bumpAllowed).toBe(false);
  });
});

describe("validateCheckout (express consent)", () => {
  const quote = quoteCheckout({ ...opts, offer: "trial", arm: "A", bump: false });
  const ok: ConsentInput = { quote, autoRenewChecked: true, ageChecked: true, email: "a@b.co", firstName: "Ann", smsChecked: false, phone: "", foundingSpotsLeft: 10 };
  it("passes with every box ticked", () => expect(validateCheckout(ok)).toEqual([]));
  it("requires the unticked auto-renew box to be ticked", () => {
    expect(validateCheckout({ ...ok, autoRenewChecked: false }).map((e) => e.field)).toContain("auto_renew");
  });
  it("requires 18+", () => expect(validateCheckout({ ...ok, ageChecked: false }).map((e) => e.field)).toContain("age_18"));
  it("SMS is optional, but needs a number when ticked", () => {
    expect(validateCheckout({ ...ok, smsChecked: true, phone: "" }).map((e) => e.field)).toContain("phone");
    expect(validateCheckout({ ...ok, smsChecked: true, phone: "+1 555 555 0100" })).toEqual([]);
  });
  it("a full founding cohort closes arm B (real cap, no fake scarcity)", () => {
    const fq = quoteCheckout({ ...opts, offer: "founding", arm: "B", bump: false });
    expect(validateCheckout({ ...ok, quote: fq, foundingSpotsLeft: 0 }).map((e) => e.field)).toContain("offer");
    expect(foundingSpots(4998, 5000)).toEqual({ claimed: 4998, cap: 5000, left: 2, open: true });
    expect(foundingSpots(5003, 5000).open).toBe(false);
  });
});

describe("Meta CAPI safety (OFFER.md 2.6)", () => {
  it("only allows the four standard events", () => {
    expect(() => buildMetaPayload({ name: "BadKneesLead" as never, eventId: "x", sourcePath: "/" }, "https://s.com")).toThrow(MetaSafetyError);
  });
  it("aliases quiz URLs and strips condition words from URLs and custom data", () => {
    expect(safeSourceUrl("https://s.com", "/quiz/gut-energy/result/123?x=1")).toBe("https://s.com/q/b");
    expect(safeSourceUrl("https://s.com", "/knee-pain-lesson")).toBe("https://s.com/");
    const p = buildMetaPayload(
      { name: "Lead", eventId: "e1", sourcePath: "/quiz/strength-age", email: "A@B.co ", attribution: { utm_campaign: "knee-promo", utm_source: "ig", mc_id: "123" }, contentName: "quiz_a" },
      "https://s.com",
    );
    expect(p.event_source_url).toBe("https://s.com/q/a");
    expect(p.custom_data.utm_campaign).toBeUndefined();
    expect(p.custom_data.utm_source).toBe("ig");
    expect(p.custom_data.mc_id).toBe("123");
    expect(JSON.stringify(p)).not.toMatch(/knee|gut|pain|balance/i);
    expect((p.user_data.em as string[])[0]).toMatch(/^[a-f0-9]{64}$/);
  });
  it("detects condition words", () => {
    expect(containsConditionWord("back-strong")).toBe(true);
    expect(containsConditionWord("trial")).toBe(false);
  });
  it("captures UTMs and passes the ManyChat mc_id through", () => {
    const a = attributionFromUrl(new URL("https://s.com/start?utm_source=ig&utm_medium=dm&mc_id=987"));
    expect(a).toMatchObject({ utm_source: "ig", utm_medium: "dm", mc_id: "987", landing_path: "/start" });
    expect(attributionFromUrl(new URL("https://s.com/start"))).toBeNull();
    expect(withMcId("/quiz/strength-age?utm_source=ig", "987")).toBe("/quiz/strength-age?utm_source=ig&mc_id=987");
  });
});
