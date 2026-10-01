/**
 * AUDIT_FINAL §6 R2-2: the gift page's quotes were never signed, so every gift
 * checkout failed the M1 "terms changed" check. The page now signs them.
 */
import { beforeEach, describe, expect, it } from "vitest";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { startCheckout, type StartCheckoutInput } from "@/lib/billing/checkout";
import { buildGiftQuotes } from "@/lib/checkoutQuotes";

let store: MemoryStore;
beforeEach(() => {
  store = new MemoryStore();
  setStoreForTests(store);
});

const gift = (months: 3 | 12, arm: "A" | "B", quoteSig: string): StartCheckoutInput => ({
  offer: months === 3 ? "gift3" : "gift12",
  arm, // /api/checkout passes the visitor's arm cookie for gifts
  gentle: false,
  email: "kid@example.com",
  firstName: "Kim",
  phone: "",
  smsConsent: false,
  autoRenewConsent: false,
  ageConsent: true,
  gift: { recipient_name: "Mom", recipient_email: "mom@example.com", message: "Love you", months },
  attribution: null,
  leadId: null,
  ip: null,
  userAgent: null,
  quoteSig,
});

describe("R2-2 gift checkout", () => {
  it.each([
    [3, "A"],
    [3, "B"],
    [12, "A"],
    [12, "B"],
  ] as const)("R2-2: the %i-month gift quote shown on /gift is accepted (visitor arm %s)", async (months, arm) => {
    const { q3, q12 } = buildGiftQuotes(new Date());
    const q = months === 3 ? q3 : q12;
    expect(q.sig).toBeTruthy();
    const r = await startCheckout(store, gift(months, arm, q.sig!));
    expect(r.ok).toBe(true);
  });

  it("R2-2: the signature still protects the terms (an empty or other quote's signature is refused)", async () => {
    const { q3, q12 } = buildGiftQuotes(new Date());
    expect((await startCheckout(store, gift(3, "A", ""))).ok).toBe(false);
    expect((await startCheckout(store, gift(3, "A", q12.sig!))).ok).toBe(false);
    expect((await startCheckout(store, gift(12, "A", q3.sig!))).ok).toBe(false);
  });
});
