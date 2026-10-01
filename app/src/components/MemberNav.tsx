"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  ["/app", "Today"],
  ["/app/progress", "Progress"],
  ["/app/kitchen", "Kitchen"],
  ["/app/programs", "Programs"],
  ["/app/chat", "Ask Chang & Sun"],
  ["/app/account", "Account"],
] as const;

export function MemberNav() {
  const path = usePathname();
  return (
    <nav aria-label="Member" className="wrap overflow-x-auto pb-3">
      <ul className="flex gap-2">
        {NAV.map(([href, label]) => {
          const active = href === "/app" ? path === "/app" : path.startsWith(href);
          return (
            <li key={href} className="flex-none">
              <Link
                href={href}
                aria-current={active ? "page" : undefined}
                className={`inline-flex min-h-[48px] items-center rounded-btn border-2 border-ink px-4 text-[18px] font-bold no-underline ${active ? "bg-ink text-rice" : "bg-rice text-ink hover:bg-cream"}`}
              >
                {label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
