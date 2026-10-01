import Link from "next/link";

export default function NotFound() {
  return (
    <main id="main" className="narrow py-16">
      <h1 className="text-4xl">We couldn&apos;t find that page.</h1>
      <Link href="/start" className="btn-primary mt-6">Go to the start page</Link>
    </main>
  );
}
