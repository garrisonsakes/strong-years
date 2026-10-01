/**
 * Human on-call coverage (AUDIT_BUSINESS F14). The chat never promises a human
 * "right now" when nobody is on shift: outside ONCALL_HOURS it says when a person
 * will read the message and points to 911 / 988 until then.
 *
 *   ONCALL_HOURS = "07:00-23:00"  (local to ONCALL_TZ; "24/7" once a 24/7 rotation or BPO is contracted)
 *   ONCALL_TZ    = "America/New_York"  (canon: a person reads messages 7:00-23:00 Eastern, 7 days)
 */
export interface Coverage {
  staffedNow: boolean;
  /** e.g. "7:00 AM Pacific" */
  nextStaffed: string;
}

function parseHours(spec: string): { start: number; end: number } | "always" {
  if (/^24\s*\/\s*7$/i.test(spec.trim())) return "always";
  const m = spec.match(/^(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})$/);
  if (!m) return { start: 7 * 60, end: 23 * 60 };
  return { start: Number(m[1]) * 60 + Number(m[2]), end: Number(m[3]) * 60 + Number(m[4]) };
}

function minutesIn(tz: string, now: Date): number {
  const parts = new Intl.DateTimeFormat("en-US", { timeZone: tz, hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(now);
  const h = Number(parts.find((p) => p.type === "hour")?.value ?? 0);
  const mi = Number(parts.find((p) => p.type === "minute")?.value ?? 0);
  return h * 60 + mi;
}

export function tzLabel(tz: string): string {
  if (tz === "America/Los_Angeles") return "Pacific";
  if (tz === "America/New_York") return "Eastern";
  if (tz === "America/Chicago") return "Central";
  if (tz === "America/Denver") return "Mountain";
  return tz;
}

export function coverage(now = new Date(), spec = process.env.ONCALL_HOURS ?? "07:00-23:00", tz = process.env.ONCALL_TZ ?? "America/New_York"): Coverage {
  const hours = parseHours(spec);
  if (hours === "always") return { staffedNow: true, nextStaffed: "now" };
  const m = minutesIn(tz, now);
  const staffedNow = hours.start <= hours.end ? m >= hours.start && m < hours.end : m >= hours.start || m < hours.end;
  const h = Math.floor(hours.start / 60);
  const mm = String(hours.start % 60).padStart(2, "0");
  const label = `${h % 12 === 0 ? 12 : h % 12}:${mm} ${h < 12 ? "AM" : "PM"} ${tzLabel(tz)}`;
  return { staffedNow, nextStaffed: label };
}

/** The sentence under every crisis referral. */
export function humanLine(now = new Date()): string {
  const c = coverage(now);
  if (c.staffedNow) return "A real person on our team has been alerted and will read your message.";
  return `Our team is offline right now. A real person will read your message by ${c.nextStaffed}. Until then, if you need help, call or text 988, or call 911 in an emergency.`;
}
