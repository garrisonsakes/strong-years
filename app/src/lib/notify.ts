/**
 * Email (Resend or Postmark), SMS (Twilio) and on-call alerts. With no provider keys,
 * every message is written to the `outbox` table and logged, so flows are testable
 * end to end without sending anything to a real person.
 */
import { emailConfigProblems, isDeployed } from "./deployEnv";
import { env, messaging } from "./config";
import { getStore } from "./db";
import type { OutboxMessage } from "./db/types";

const FOOTER =
  "Chang Yin and Sun Yoon are AI characters; their story is fictional. Sessions and recipes built from published guidelines for older adults. General education, not medical advice.";

/**
 * M6: the outbox is an audit trail, not a credential store. Login tokens, gift
 * claim tokens and gift codes are redacted before a row is written.
 */
export function redactSecrets(text: string, secrets: string[] = []): string {
  let out = text;
  for (const s of secrets) if (s) out = out.split(s).join("[redacted]");
  return out
    .replace(/([?&](?:token|claim|session_id|code)=)[A-Za-z0-9_\-.%]+/g, "$1[redacted]");
}

function maskEmail(e: string): string {
  const [u, d] = e.split("@");
  return d ? `${(u ?? "").slice(0, 1)}***@${d}` : "***";
}

async function record(msg: Omit<OutboxMessage, "id" | "created_at">, secrets: string[] = []) {
  const store = await getStore();
  const row = await store.insert("outbox", { ...msg, body: redactSecrets(msg.body, secrets), subject: msg.subject ? redactSecrets(msg.subject, secrets) : msg.subject });
  if (process.env.NODE_ENV !== "test" && msg.status === "stubbed") {
    console.info(`[outbox:${msg.channel}] to=${msg.channel === "email" ? maskEmail(msg.to) : "***"} template=${msg.template}`);
  }
  return row;
}

export interface EmailInput {
  to: string;
  subject: string;
  text: string;
  template: string;
  from?: "chang" | "sun" | "team";
  /** Values to redact from the stored copy (tokens, links). Common patterns are redacted anyway. */
  secrets?: string[];
  /** Replaces the "Manage membership" footer line (waitlist emails carry their unsubscribe link here). */
  manageLine?: string;
  /** Extra headers (lifecycle mail: List-Unsubscribe + List-Unsubscribe-Post, RFC 8058). */
  headers?: Record<string, string>;
}

/**
 * Local development only: with DEV_MAIL_SINK_DIR set and not a real deploy, every
 * email is also appended, unredacted, to <dir>/mail.jsonl (a "mail catcher", used by
 * the e2e test to follow confirmation links). Refused on any deploy.
 */
async function devMailSink(to: string, subject: string, body: string, template: string) {
  const dir = process.env.DEV_MAIL_SINK_DIR;
  if (!dir || isDeployed()) return;
  try {
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    await fs.mkdir(dir, { recursive: true });
    await fs.appendFile(path.join(dir, "mail.jsonl"), `${JSON.stringify({ to, subject, body, template, at: new Date().toISOString() })}\n`);
  } catch (err) {
    console.error("dev mail sink failed", (err as Error).message);
  }
}

const FROM_NAME = { chang: "Chang Yin (Strong Years)", sun: "Sun Yoon (Strong Years)", team: "Strong Years Team" };

let warnedConfig = false;

export async function sendEmail(input: EmailInput) {
  const body = `${input.text}\n\n--\n${FOOTER}\n${input.manageLine ?? `Manage membership: ${env.siteUrl}/app/account`}\n${env.mailingAddress}`;
  await devMailSink(input.to, input.subject, body, input.template);
  // Round 9: on a real deploy, never send mail with localhost links, a placeholder
  // postal address or a fake sender. /api/health reports it (503) and boot logs it.
  if (isDeployed()) {
    const problems = emailConfigProblems();
    if (problems.length) {
      if (!warnedConfig) console.error(`EMAIL BLOCKED: unsafe email config (${problems.join("; ")}). Fix the env vars; /api/health is failing.`);
      warnedConfig = true;
      return record({ channel: "email", to: input.to, subject: input.subject, body, template: input.template, provider: "blocked_config", status: "failed" }, input.secrets);
    }
  }
  const fromAddress = process.env.EMAIL_FROM ?? "hello@strongyears.example";
  const from = `${FROM_NAME[input.from ?? "team"]} <${fromAddress}>`;
  try {
    if (process.env.RESEND_API_KEY) {
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, "Content-Type": "application/json" },
        body: JSON.stringify({ from, to: [input.to], subject: input.subject, text: body, ...(input.headers ? { headers: input.headers } : {}) }),
      });
      return record({ channel: "email", to: input.to, subject: input.subject, body, template: input.template, provider: "resend", status: res.ok ? "sent" : "failed" }, input.secrets);
    }
    if (process.env.POSTMARK_SERVER_TOKEN) {
      const res = await fetch("https://api.postmarkapp.com/email", {
        method: "POST",
        headers: { "X-Postmark-Server-Token": process.env.POSTMARK_SERVER_TOKEN, "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ From: from, To: input.to, Subject: input.subject, TextBody: body, MessageStream: input.headers ? "broadcast" : "outbound", ...(input.headers ? { Headers: Object.entries(input.headers).map(([Name, Value]) => ({ Name, Value })) } : {}) }),
      });
      return record({ channel: "email", to: input.to, subject: input.subject, body, template: input.template, provider: "postmark", status: res.ok ? "sent" : "failed" }, input.secrets);
    }
  } catch (err) {
    console.error("email send failed", err);
    return record({ channel: "email", to: input.to, subject: input.subject, body, template: input.template, provider: "error", status: "failed" }, input.secrets);
  }
  return record({ channel: "email", to: input.to, subject: input.subject, body, template: input.template, provider: "stub", status: "stubbed" }, input.secrets);
}

export async function sendSms(to: string, text: string, template: string) {
  const body = text.startsWith("Strong Years") ? text : `Strong Years: ${text}`;
  // Until 10DLC / toll-free verification is approved, texts are not sent (email carries reminders).
  // On-call alerts to staff are exempt: they go to our own phone, not to consumers.
  if (!messaging.smsEnabled && template !== "oncall_alert") {
    return record({ channel: "sms", to, subject: null, body, template, provider: "sms_disabled", status: "skipped" });
  }
  const sid = process.env.TWILIO_ACCOUNT_SID;
  const token = process.env.TWILIO_AUTH_TOKEN;
  const from = process.env.TWILIO_FROM_NUMBER ?? process.env.TWILIO_MESSAGING_SERVICE_SID;
  if (sid && token && from) {
    try {
      const params = new URLSearchParams({ To: to, Body: body });
      if (from.startsWith("MG")) params.set("MessagingServiceSid", from);
      else params.set("From", from);
      const res = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${sid}/Messages.json`, {
        method: "POST",
        headers: {
          Authorization: `Basic ${Buffer.from(`${sid}:${token}`).toString("base64")}`,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: params,
      });
      return record({ channel: "sms", to, subject: null, body, template, provider: "twilio", status: res.ok ? "sent" : "failed" });
    } catch (err) {
      console.error("sms send failed", err);
      return record({ channel: "sms", to, subject: null, body, template, provider: "error", status: "failed" });
    }
  }
  return record({ channel: "sms", to, subject: null, body, template, provider: "stub", status: "stubbed" });
}

/**
 * Page the on-call human (crisis events, human-escalation requests).
 * M6: alerts carry no member text and no email address, only what happened and
 * a deep link into the admin (behind basic auth), where the details live.
 */
export async function alertOnCall(subject: string, ref?: string) {
  const text = `${subject}\n\nOpen the admin to see details: ${env.siteUrl}/admin${ref ? `#${ref}` : "#crisis"}`;
  const tasks: Promise<unknown>[] = [];
  if (process.env.ONCALL_SLACK_WEBHOOK_URL) {
    tasks.push(
      fetch(process.env.ONCALL_SLACK_WEBHOOK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      }).catch((e) => console.error("slack alert failed", e)),
    );
  }
  if (process.env.ONCALL_PHONE) tasks.push(sendSms(process.env.ONCALL_PHONE, `ALERT ${subject}. Check the admin.`, "oncall_alert"));
  if (process.env.ONCALL_EMAIL) tasks.push(sendEmail({ to: process.env.ONCALL_EMAIL, subject: `[Strong Years alert] ${subject}`, text, template: "oncall_alert" }));
  await Promise.all(tasks);
  await record({ channel: "alert", to: process.env.ONCALL_EMAIL ?? "on-call (not configured)", subject, body: text, template: "oncall_alert", provider: tasks.length ? "multi" : "stub", status: tasks.length ? "sent" : "stubbed" });
}
