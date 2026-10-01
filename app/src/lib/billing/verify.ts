import Stripe from "stripe";
import type { StripeLikeEvent } from "./webhook";

// Signature verification needs no API key or network; a placeholder key is fine here.
const verifier = new Stripe("sk_test_signature_verification_only");

export function verifyStripeSignature(payload: string, header: string | null, secret: string): StripeLikeEvent {
  if (!header) throw new Error("missing stripe-signature header");
  return verifier.webhooks.constructEvent(payload, header, secret) as unknown as StripeLikeEvent;
}

export function testSignatureHeader(payload: string, secret: string): string {
  return verifier.webhooks.generateTestHeaderString({ payload, secret });
}
