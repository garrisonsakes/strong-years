"use server";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { billingMembership, requireEntitled, requireMember } from "@/lib/auth/server";
import { getStore } from "@/lib/db";
import type { Track } from "@/lib/db/types";
import { mode } from "@/lib/config";
import {
  addPartnerSeat,
  cancelMembership,
  downgradeToEssentials,
  pauseMembership,
  portalUrl,
  removePartnerSeat,
  resumeMembership,
  undoCancel,
} from "@/lib/billing/actions";
import { isCancelReason, saveOfferFor } from "@/lib/billing/cancel";
import { runMockBillingClock, runReminders } from "@/lib/billing/clock";
import { computeStrengthAgeNumber } from "@/lib/quiz/strengthAge";
import { weekKey } from "@/lib/practice";
import { PROGRAMS, SMS_CONSENT_TEXT } from "@/lib/pricing";
import { alertOnCall, sendEmail } from "@/lib/notify";
import { phoneDigits } from "@/lib/members";
import { isShopify } from "@/lib/billing/provider";
import { billingProvider } from "@/lib/billing/active";
import { shopifyConfig } from "@/lib/billing/shopify";

/** Shopify mode: cancel, pause, downgrade, card and partner changes happen on the Shopify customer account page. */
function shopifyManagesThis() {
  if (isShopify()) redirect(shopifyConfig.customerAccountUrl());
}

const TRACKS: Track[] = ["rebuild", "steady", "strong", "iron"];

export async function setTrack(form: FormData) {
  const { member } = await requireEntitled();
  const t = String(form.get("track")) as Track;
  if (TRACKS.includes(t)) await (await getStore()).update("members", member.id, { track: t });
  revalidatePath("/app");
  redirect("/app");
}

export async function completeSession(form: FormData) {
  const { member } = await requireEntitled();
  const store = await getStore();
  const day = new Date().toISOString().slice(0, 10);
  const key = String(form.get("session_key") ?? "");
  const already = await store.findOne("practice_logs", { member_id: member.id, day });
  if (!already) {
    await store.insert("practice_logs", {
      member_id: member.id,
      day,
      session_key: key,
      track: member.track,
      swap: form.get("swap") ? String(form.get("swap")) : null,
      minutes: Number(form.get("minutes") ?? 8),
    });
  }
  const feel = String(form.get("feel") ?? "");
  if (feel === "easy" || feel === "hard") {
    const idx = TRACKS.indexOf(member.track);
    const next = feel === "easy" ? TRACKS[Math.min(3, idx + 1)]! : TRACKS[Math.max(0, idx - 1)]!;
    await store.update("members", member.id, { track: next });
  }
  revalidatePath("/app");
  redirect("/app?done=1");
}

export async function protectWeek() {
  const { member } = await requireEntitled();
  const wk = weekKey(new Date());
  if (!member.protected_weeks.includes(wk)) {
    await (await getStore()).update("members", member.id, { protected_weeks: [...member.protected_weeks, wk] });
  }
  redirect("/app/progress?protected=1");
}

export async function saveRetest(form: FormData) {
  const { member } = await requireEntitled();
  const store = await getStore();
  const n = (k: string) => {
    const v = form.get(k);
    return v === null || v === "" ? null : Number(v);
  };
  const reps = Math.max(0, Math.min(40, n("chair_reps") ?? 0));
  const stage = Math.max(0, Math.min(4, n("balance_stage") ?? 0));
  const usedHands = form.get("used_hands") === "on";
  let age = member.age;
  let sex = member.sex;
  if (!age) {
    age = Math.max(45, Math.min(95, n("age") ?? 70));
    const s = String(form.get("sex") ?? "na");
    sex = s === "woman" || s === "man" ? s : "na";
    await store.update("members", member.id, { age, sex });
  }
  const sa = computeStrengthAgeNumber({ age, sex, chairReps: reps, usedHands, balanceStage: stage, selfReport: 0 });
  const prev = await store.findOne("retests", { member_id: member.id }, { orderBy: "created_at", desc: true });
  await store.insert("retests", {
    member_id: member.id,
    chair_reps: reps,
    balance_stage: stage,
    used_hands: usedHands,
    strength_age: sa,
    age_at_test: age,
    extra: { step_test: n("step_test"), arm_curl: n("arm_curl"), sit_reach: n("sit_reach"), up_and_go: n("up_and_go") },
  });
  // FUNNEL.md 7.4: a big drop gets the Rebuild track and a human check-in.
  if (prev && (sa - prev.strength_age >= 5 || prev.chair_reps - reps >= 4 || prev.balance_stage - stage >= 2)) {
    await store.update("members", member.id, { track: "rebuild" });
    await store.insert("support_tickets", { member_id: member.id, email: member.email, reason: "retest_drop", message: `Strength Age ${prev.strength_age} → ${sa}; reps ${prev.chair_reps} → ${reps}; stage ${prev.balance_stage} → ${stage}`, status: "open" });
    await sendEmail({ to: member.email, template: "retest_drop_checkin", subject: "Checking in after your retest", text: `Hi ${member.first_name}, this is the Strong Years team (real people). Your retest changed more than usual. It may be nothing, but sudden changes in strength or balance are worth mentioning to your doctor, especially if you've been unwell, changed medicines or felt dizzy. We've set you to the Rebuild track for now. Reply to this email if anything feels off.` });
  }
  revalidatePath("/app/progress");
  redirect(`/app/retest?result=${sa}${prev ? `&prev=${prev.strength_age}&reps=${reps}&prevReps=${prev.chair_reps}&stage=${stage}&prevStage=${prev.balance_stage}` : ""}`);
}

export async function chooseProgram(form: FormData) {
  const { member } = await requireEntitled();
  const slug = String(form.get("program") ?? "");
  if (PROGRAMS.some((p) => p.slug === slug)) {
    await (await getStore()).update("members", member.id, { active_program: slug, program_started_at: new Date().toISOString() });
  }
  revalidatePath("/app/programs");
  redirect("/app/programs");
}

export async function saveSettings(form: FormData) {
  const member = await requireMember();
  const store = await getStore();
  const time = String(form.get("reminder_time") ?? "07:30");
  const channel = String(form.get("reminder_channel")) === "sms" ? "sms" : "email";
  const smsOptIn = form.get("sms_opt_in") === "on";
  const phone = String(form.get("phone") ?? "").trim();
  if (smsOptIn && !member.sms_opt_in) {
    if (!/^\+?[0-9 ()-]{10,20}$/.test(phone)) redirect("/app/settings?error=phone");
    await store.insert("consent_log", { email: member.email, member_id: member.id, kind: "sms", checked: true, text_shown: SMS_CONSENT_TEXT, price_cents: null, first_charge_at: null, offer_code: null, ip: null, user_agent: null });
  }
  await store.update("members", member.id, {
    reminder_time: /^\d{2}:\d{2}$/.test(time) ? time : "07:30",
    reminder_channel: smsOptIn ? channel : "email",
    sms_opt_in: smsOptIn,
    phone: smsOptIn ? phone || member.phone : member.phone,
    phone_digits: phoneDigits(smsOptIn ? phone || member.phone : member.phone),
  });
  redirect("/app/settings?saved=1");
}

export async function setMemory(form: FormData) {
  const member = await requireMember();
  const store = await getStore();
  const on = form.get("memory") === "on";
  await store.update("members", member.id, { memory_enabled: on });
  await store.insert("consent_log", { email: member.email, member_id: member.id, kind: "memory", checked: on, text_shown: on ? "Let Ask Chang and Ask Sun remember what I tell them. I can see and delete it anytime." : "Memory turned off.", price_cents: null, first_charge_at: null, offer_code: null, ip: null, user_agent: null });
  redirect("/app/settings?saved=1#memory");
}

export async function deleteMemory(form: FormData) {
  const member = await requireMember();
  const store = await getStore();
  const id = String(form.get("id") ?? "");
  if (id === "all") await store.remove("memory_items", { member_id: member.id });
  else await store.remove("memory_items", { member_id: member.id, id });
  redirect("/app/settings?deleted=1#memory");
}

export async function confirmAdult() {
  const member = await requireMember();
  const store = await getStore();
  await store.update("members", member.id, { age_confirmed_at: new Date().toISOString() });
  await store.insert("consent_log", { email: member.email, member_id: member.id, kind: "age_18", checked: true, text_shown: "I am 18 or older.", price_cents: null, first_charge_at: null, offer_code: null, ip: null, user_agent: null });
  redirect("/app/chat");
}

export async function talkToHuman(form: FormData) {
  const member = await requireMember();
  const store = await getStore();
  const message = String(form.get("message") ?? "").slice(0, 2000);
  await store.insert("support_tickets", { member_id: member.id, email: member.email, reason: "talk_to_human", message, status: "open" });
  const ticket = await store.findOne("support_tickets", { member_id: member.id, reason: "talk_to_human" }, { orderBy: "created_at", desc: true });
  await alertOnCall("Member asked for a human", ticket ? `ticket-${ticket.id}` : "tickets");
  redirect("/app/chat?human=sent");
}

export async function addPartner(form: FormData) {
  shopifyManagesThis();
  const member = await requireMember();
  const store = await getStore();
  const m = await billingMembership(member.id);
  if (!m || m.plan === "gift") redirect("/app/partner?error=plan");
  if (form.get("consent") !== "on") redirect("/app/partner?error=consent");
  const name = String(form.get("name") ?? "").trim();
  const email = String(form.get("email") ?? "").trim();
  if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) redirect("/app/partner?error=details");
  await store.insert("consent_log", { email: member.email, member_id: member.id, kind: "partner_auto_renew", checked: true, text_shown: "Add my partner for $8.00/month, added to my membership charge and renewing monthly until I remove them or cancel.", price_cents: 800, first_charge_at: m.current_period_end, offer_code: "partner", ip: null, user_agent: null });
  await addPartnerSeat(store, member, m, { name, email, share: form.get("share") === "on" });
  redirect("/app/partner?added=1");
}

export async function removePartner() {
  shopifyManagesThis();
  const member = await requireMember();
  const store = await getStore();
  const m = await billingMembership(member.id);
  if (m) await removePartnerSeat(store, member, m);
  redirect("/app/partner?removed=1");
}

/* ---------------- account & cancel ---------------- */

/** H3: account actions act on the membership that bills, never on a gift row. */
async function mine() {
  const member = await requireMember();
  const m = await billingMembership(member.id);
  if (!m) redirect("/app/account");
  return { member, m, store: await getStore() };
}

export async function finishCancel(form: FormData) {
  shopifyManagesThis();
  const { m, store } = await mine();
  const reason = form.get("reason");
  const r = isCancelReason(reason) ? reason : null;
  await cancelMembership(store, m, r, r ? saveOfferFor(r, m) : null);
  redirect("/app/account/cancel?done=canceled");
}

export async function acceptPause(form: FormData) {
  shopifyManagesThis();
  const { m, store } = await mine();
  const reason = form.get("reason");
  const r = isCancelReason(reason) ? reason : null;
  await pauseMembership(store, m, Number(form.get("months") ?? 1), r, saveOfferFor(r, m));
  redirect("/app/account/cancel?done=paused");
}

export async function acceptDowngrade(form: FormData) {
  shopifyManagesThis();
  const { m, store } = await mine();
  const reason = form.get("reason");
  const r = isCancelReason(reason) ? reason : null;
  await downgradeToEssentials(store, m, r, saveOfferFor(r, m));
  redirect("/app/account/cancel?done=downgraded");
}

/** Shopify launch path: the Essentials save offer is a request a person applies (planChange.ts). */
export async function requestEssentials() {
  const { member, m, store } = await mine();
  const { canOfferEssentials, requestEssentialsSwitch } = await import("@/lib/billing/planChange");
  if (!isShopify() || !canOfferEssentials(m)) redirect("/app/account/cancel");
  await requestEssentialsSwitch(store, member, m);
  redirect("/app/account/cancel?done=essentials_requested");
}

/** Founding → annual ($249) on the launch path: the same request path as Essentials (Shopify can't swap products self-serve). */
export async function requestAnnual() {
  const { member, m, store } = await mine();
  const { canOfferAnnual, requestPlanSwitch } = await import("@/lib/billing/planChange");
  const chargeCount = await store.count("sy_orders", { membership_id: m.id, kind: "membership_charge", status: "paid" });
  if (!isShopify() || !canOfferAnnual(m, chargeCount)) redirect("/app/account");
  await requestPlanSwitch(store, member, m, "annual");
  redirect("/app/account?annual=requested");
}

export async function undoCancellation() {
  shopifyManagesThis();
  const { m, store } = await mine();
  await undoCancel(store, m);
  redirect("/app/account?undone=1");
}

export async function resume() {
  shopifyManagesThis();
  const { m, store } = await mine();
  await resumeMembership(store, m);
  redirect("/app/account?resumed=1");
}

export async function requestRefund() {
  const { m, store } = await mine();
  const r = await billingProvider().refundMembership(store, m);
  redirect(`/app/account?refund=${r.state}`);
}

export async function openPortal() {
  shopifyManagesThis();
  const { member } = await mine();
  redirect(await portalUrl(member));
}

/** Demo only: run the billing clock + reminder job now. */
export async function runDemoClock(form: FormData) {
  const { m, store } = await mine();
  if (!mode.mockStripe) redirect("/app/account");
  if (form.get("fast_forward") === "on") {
    await store.update("memberships", m.id, { current_period_end: new Date(Date.now() - 60_000).toISOString() });
  }
  await runReminders(store);
  await runMockBillingClock(store);
  redirect("/app/account?clock=1");
}
