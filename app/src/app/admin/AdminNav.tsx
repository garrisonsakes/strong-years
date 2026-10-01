import Link from "next/link";
import { Logo } from "@/components/Chrome";

/** Shared header for the admin screens. Plain words, high contrast, no decorations. */
export function AdminNav({ current }: { current: "overview" | "today" | "exceptions" }) {
  const item = (href: string, label: string, key: typeof current) => (
    <Link href={href} className={`rounded-lg border-2 border-ink px-3 py-1 font-bold no-underline ${current === key ? "bg-ink text-rice" : "bg-rice text-ink"}`} aria-current={current === key ? "page" : undefined}>
      {label}
    </Link>
  );
  return (
    <header className="border-b-2 border-ink">
      <div className="wrap flex min-h-[68px] flex-wrap items-center justify-between gap-3 py-2">
        <Logo href="/admin" />
        <nav className="flex flex-wrap gap-2" aria-label="Admin">
          {item("/admin", "Overview", "overview")}
          {item("/admin/today", "Today", "today")}
          {item("/admin/exceptions", "Exceptions", "exceptions")}
        </nav>
      </div>
    </header>
  );
}
