import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";

/** Mark a crisis event handled (admin, behind basic auth in middleware). */
export async function POST(req: Request) {
  const f = await req.formData();
  const id = String(f.get("id") ?? "");
  const store = await getStore();
  if (id) await store.update("crisis_events", id, { handled_at: new Date().toISOString() });
  return NextResponse.redirect(`${new URL(req.url).origin}/admin#crisis`, 303);
}
