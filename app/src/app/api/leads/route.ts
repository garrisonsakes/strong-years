import { NextResponse } from "next/server";
import { getStore } from "@/lib/db";
import { env } from "@/lib/config";
import { trackMetaEvent } from "@/lib/analytics/meta";
import { scoreStrengthAge, type StrengthAgeAnswers } from "@/lib/quiz/strengthAge";
import { scoreGutEnergy, type GutEnergyAnswers } from "@/lib/quiz/gutEnergy";
import { SMS_CONSENT_TEXT } from "@/lib/pricing";
import { sendEmail } from "@/lib/notify";
import { clientMeta, getAttribution } from "@/lib/request";
import { LIMITS, clientIp, hit } from "@/lib/rateLimit";

interface Body {
  quiz?: "strength_age" | "gut_energy";
  answers?: Record<string, unknown>;
  firstName?: string;
  email?: string;
  sms?: boolean;
  phone?: string;
}

function num(v: unknown, fallback = 0): number {
  return typeof v === "number" && Number.isFinite(v) ? v : fallback;
}

const MAX_BODY = 8 * 1024;

export async function POST(req: Request) {
  // M12: cap the body; M5: rate limit per IP and per email.
  const raw = await req.text();
  if (raw.length > MAX_BODY) return NextResponse.json({ error: "That's more than we need." }, { status: 413 });
  let body: Body;
  try {
    body = JSON.parse(raw) as Body;
  } catch {
    return NextResponse.json({ error: "Bad request" }, { status: 400 });
  }
  if (!(await hit(`leads:ip:${clientIp(req)}`, LIMITS.leadsPerIp)) || !(await hit(`leads:email:${String(body.email ?? "").trim().toLowerCase()}`, LIMITS.leadsPerEmail))) {
    return NextResponse.json({ error: "We've already sent your result. Please check your email." }, { status: 429 });
  }
  const email = (body.email ?? "").trim().toLowerCase();
  const firstName = (body.firstName ?? "").trim().slice(0, 60);
  if (!firstName) return NextResponse.json({ error: "Please tell us your first name." }, { status: 400 });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return NextResponse.json({ error: "Please check your email address." }, { status: 400 });
  const phone = (body.phone ?? "").trim();
  if (body.sms && !/^\+?[0-9 ()-]{10,20}$/.test(phone)) return NextResponse.json({ error: "Please enter a mobile number, or untick the text box." }, { status: 400 });
  const a = body.answers ?? {};
  const store = await getStore();
  const attribution = await getAttribution();
  const meta = await clientMeta();

  let result: Record<string, unknown>;
  let validated: Record<string, unknown>;
  let profile: string;
  const flags: string[] = [];
  if (body.quiz === "strength_age") {
    const answers: StrengthAgeAnswers = {
      taker: a.taker === "helping" || a.taker === "other" ? a.taker : "self",
      sex: a.sex === "woman" || a.sex === "man" ? a.sex : "na",
      age: num(a.age, 70),
      safety: Array.isArray(a.safety) ? (a.safety.filter((x) => ["chest", "dizzy", "fall", "surgery", "doctor_limit"].includes(String(x))) as StrengthAgeAnswers["safety"]) : [],
      mobility: ["none", "cane_some", "cane_most", "walker", "wheelchair"].includes(String(a.mobility)) ? (a.mobility as StrengthAgeAnswers["mobility"]) : "none",
      chairReps: typeof a.chairReps === "number" ? a.chairReps : null,
      usedHands: a.usedHands === true,
      armCurls: typeof a.armCurls === "number" ? a.armCurls : null,
      balanceStage: typeof a.balanceStage === "number" ? a.balanceStage : null,
      jar: num(a.jar, 1),
      carry: num(a.carry, 1),
      floor: num(a.floor, 1),
      stairs: num(a.stairs, 1),
      walking: num(a.walking, 1),
      strengthFreq: num(a.strengthFreq, 2),
      aches: Array.isArray(a.aches) ? (a.aches.map(String) as StrengthAgeAnswers["aches"]) : ["nothing"],
      goal: num(a.goal, 0),
      minutes: num(a.minutes, 10),
    };
    const r = scoreStrengthAge(answers);
    validated = { ...answers };
    result = { ...r, sex: answers.sex };
    profile = r.profile;
    if (r.kind === "safe_mode") flags.push("safe_mode");
    if (r.adultChild) flags.push("adult_child");
  } else if (body.quiz === "gut_energy") {
    const answers: GutEnergyAnswers = {
      redFlags: Array.isArray(a.redFlags) ? (a.redFlags.map(String) as GutEnergyAnswers["redFlags"]) : [],
      ageBand: num(a.ageBand),
      weight: num(a.weight, 5),
      breakfast: num(a.breakfast),
      proteinMeals: num(a.proteinMeals),
      tiredWhen: num(a.tiredWhen),
      afterMeal: num(a.afterMeal),
      bloating: num(a.bloating),
      bathroom: num(a.bathroom),
      plants: num(a.plants),
      fluids: num(a.fluids),
      sleep: num(a.sleep),
      caffeine: num(a.caffeine),
      alcohol: num(a.alcohol),
      chewing: num(a.chewing),
      manyMeds: a.manyMeds === true,
    };
    const r = scoreGutEnergy(answers);
    validated = { ...answers };
    if (r.stop) return NextResponse.json({ error: "Please see your doctor first." }, { status: 400 });
    result = { ...r };
    profile = r.profile ?? "b6";
  } else {
    return NextResponse.json({ error: "Unknown quiz" }, { status: 400 });
  }

  const lead = await store.insert("leads", {
    email,
    first_name: firstName,
    phone: body.sms ? phone : null,
    sms_consent: Boolean(body.sms),
    quiz: body.quiz,
    profile_code: profile,
    result,
    // M12: only the validated, typed answers are kept, never the raw client JSON.
    answers: validated,
    flags,
    attribution,
  });
  if (body.sms) {
    await store.insert("consent_log", { email, member_id: null, kind: "sms", checked: true, text_shown: SMS_CONSENT_TEXT, price_cents: null, first_charge_at: null, offer_code: null, ip: meta.ip, user_agent: meta.userAgent });
  }
  const path = body.quiz === "strength_age" ? "strength-age" : "gut-energy";
  await sendEmail({
    to: email,
    from: body.quiz === "strength_age" ? "chang" : "sun",
    template: `quiz_${body.quiz === "strength_age" ? "a" : "b"}_result`,
    subject: body.quiz === "strength_age" ? "Your Strength Age and 7-day plan" : "Your 7-day kitchen plan from Sun Yoon",
    text: `${firstName}, here is your result and your 7-day plan: ${env.siteUrl}/quiz/${path}/result/${lead.id}`,
  });
  // Ads (AUDIT_BUSINESS F12/F23, Washington MHMD): the gut & energy quiz records
  // nothing for ad platforms. The Strength Age quiz records one local Lead row on the
  // neutral path /q/a, and it is never forwarded to Meta or TikTok (healthContext):
  // taking a strength quiz is itself health-adjacent. Organic opt-ins are measured
  // through the waitlist instead.
  if (body.quiz === "strength_age") {
    await trackMetaEvent({ name: "Lead", eventId: `lead_${lead.id}`, sourcePath: "/q/a", email, contentName: "quiz", attribution, leadId: lead.id, healthContext: true }, env.siteUrl);
  }
  return NextResponse.json({ id: lead.id });
}
