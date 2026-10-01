"use client";
import Link from "next/link";
import { useEffect, useState } from "react";

/** Mobile-only sticky CTA that appears once the hero has scrolled away (FUNNEL.md 2.1). */
export function StickyBar({ href, label, note }: { href: string; label: string; note: string }) {
  const [show, setShow] = useState(false);
  useEffect(() => {
    const hero = document.getElementById("hero");
    const pricing = document.getElementById("pricing");
    if (!hero) return;
    let heroGone = false;
    let pricingVisible = false;
    const update = () => setShow(heroGone && !pricingVisible);
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (e.target === hero) heroGone = !e.isIntersecting;
        if (e.target === pricing) pricingVisible = e.isIntersecting;
      }
      update();
    });
    io.observe(hero);
    if (pricing) io.observe(pricing);
    return () => io.disconnect();
  }, []);
  if (!show) return null;
  return (
    <div className="no-print fixed inset-x-0 bottom-0 z-40 border-t-2 border-ink bg-rice px-4 py-3 sm:hidden" data-testid="sticky-bar">
      <Link href={href} className="btn-primary min-h-[56px]">
        {label}
      </Link>
      <p className="mt-1 text-center text-[16px] font-bold text-ink">{note}</p>
    </div>
  );
}
