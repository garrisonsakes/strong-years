import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

/** TikTok bio link: the same hub as /go with platform=tt (ORGANIC_ENGINE.md §3.2). */
export default async function Tt({ searchParams }: { searchParams: Promise<Record<string, string | undefined>> }) {
  const sp = await searchParams;
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(sp)) if (typeof v === "string" && v.length <= 200 && /^[a-z_]{1,20}$/.test(k)) q.set(k, v);
  if (!q.get("platform")) q.set("platform", "tt");
  if (!q.get("p") && !q.get("page")) q.set("p", "tt-changyin");
  redirect(`/go?${q.toString()}`);
}
