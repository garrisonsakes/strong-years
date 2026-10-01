import type { Metadata } from "next";
import Link from "next/link";
import { getStore } from "@/lib/db";
import { sha256Hex } from "@/lib/auth/session";
import { moneyExact } from "@/lib/pricing";

export const metadata: Metadata = { title: "Confirm your purchase", robots: { index: false } };
export const dynamic = "force-dynamic";

/** Opening this page changes nothing (mail scanners open links); the buttons do. */
export default async function VerifyPurchase({ searchParams }: { searchParams: Promise<{ token?: string; done?: string }> }) {
  const { token = "", done } = await searchParams;
  if (done === "rejected") {
    return (
      <div className="narrow py-12" data-testid="verify-rejected">
        <h1 className="text-4xl">Thank you. We&apos;ve stopped it.</h1>
        <p className="mt-4 text-lg">Nothing on your account changed. The purchase is cancelled and a person on our team will refund whoever paid. You don&apos;t need to do anything else.</p>
      </div>
    );
  }
  const intent = token ? await (await getStore()).findOne("checkout_intents", { verify_token_hash: await sha256Hex(token), verification: "pending" }) : null;
  const valid = intent && intent.verify_expires_at && new Date(intent.verify_expires_at) > new Date();
  if (!intent || !valid) {
    return (
      <div className="narrow py-12">
        <h1 className="text-4xl">This link has expired or was already used.</h1>
        <p className="mt-4 text-lg">If you&apos;ve already confirmed, just log in with your email.</p>
        <Link href="/login" className="btn-primary mt-6">Log in</Link>
      </div>
    );
  }
  return (
    <div className="narrow py-12" data-testid="verify-purchase">
      <h1 className="text-4xl">Did you just buy Strong Years?</h1>
      <p className="mt-4 text-lg">Someone paid {moneyExact(intent.amount_today_cents)} today using this email address. Please tell us if it was you.</p>
      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <form action="/api/checkout/verify" method="post">
          <input type="hidden" name="token" value={token} />
          <input type="hidden" name="action" value="confirm" />
          <button type="submit" className="btn-primary sm:w-full" data-testid="verify-confirm">Yes, this was me</button>
        </form>
        <form action="/api/checkout/verify" method="post">
          <input type="hidden" name="token" value={token} />
          <input type="hidden" name="action" value="reject" />
          <button type="submit" className="btn-outline sm:w-full" data-testid="verify-reject">This wasn&apos;t me</button>
        </form>
      </div>
    </div>
  );
}
