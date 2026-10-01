import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Check your email", robots: { index: false } };

/** NEW-1: shown after paying with an email that already has an account. No session is created. */
export default function CheckEmail() {
  return (
    <div className="narrow py-12" data-testid="check-email">
      <h1 className="text-4xl">Payment received. One more step: check your email.</h1>
      <p className="mt-4 text-lg">
        That email address already has a Strong Years account, so for your privacy we don&apos;t open it from a checkout. We&apos;ve sent a link to that inbox. Open it to confirm the purchase and you&apos;ll go straight to your Daily Practice.
      </p>
      <p className="mt-4 text-lg">Didn&apos;t get it? Check spam, or log in with the same email and we&apos;ll send a fresh link.</p>
      <p className="mt-6">
        <Link href="/login" className="btn-outline">Log in by email</Link>
      </p>
    </div>
  );
}
