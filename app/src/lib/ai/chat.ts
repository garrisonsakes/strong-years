/**
 * Ask Chang / Ask Sun. Pipeline for every member message:
 *   1. 18+ gate (member must have confirmed age)
 *   2. crisis classifier (keyword + LLM) → fixed referral text, log, alert a human
 *   3. scope guard (medication / diagnosis / red flags) → fixed safe reply
 *   4. model call with the voice-card + safety system prompt (or scripted stub offline)
 *   5. output guard → replace anything that slipped through
 *   6. opt-in memory extraction
 */
import Anthropic from "@anthropic-ai/sdk";
import { env, mode } from "../config";
import type { Store } from "../db/store";
import type { Character, ChatMessage, Member } from "../db/types";
import { alertOnCall } from "../notify";
import { LLM_CLASSIFIER_PROMPT, buildClassifierInput, decide, parseLlmVerdict, referralText, type Classification, type LlmVerdict } from "../safety/crisis";
import { humanLine } from "../safety/oncall";
import { offlineText } from "../safety/offline";
import { detectScopeIssue, guardOutput, scopeReply } from "../safety/scope";
import { MEMORY_EXTRACT_PROMPT, buildSystemPrompt } from "./prompts";

export function disclosureLine(character: Character): string {
  return character === "chang"
    ? "I'm Chang Yin, an AI character, not a doctor or physical therapist. For anything urgent, call 911."
    : "I'm Sun Yoon, an AI character, not a doctor or a nutritionist. For anything urgent, call 911.";
}

let client: Anthropic | null = null;
function anthropic(): Anthropic | null {
  if (mode.mockAi) return null;
  if (!client) client = new Anthropic({ apiKey: env.anthropicKey });
  return client;
}

async function llmText(system: string, messages: { role: "user" | "assistant"; content: string }[], maxTokens: number, timeoutMs = 20_000, maxRetries = 1): Promise<string | null> {
  if (replyOverride) return replyOverride(system, messages).catch(() => null);
  const c = anthropic();
  if (!c) return null;
  try {
    const res = await c.messages.create({ model: env.anthropicModel, max_tokens: maxTokens, system, messages }, { timeout: timeoutMs, maxRetries });
    return res.content
      .map((b) => (b.type === "text" ? b.text : ""))
      .join("")
      .trim();
  } catch (err) {
    console.error("anthropic call failed", err);
    return null;
  }
}

/** Test seams: replace the model calls (crisis classifier; coach replies). */
let classifierOverride: ((input: string) => Promise<string | null>) | null = null;
export function setClassifierModelForTests(fn: ((input: string) => Promise<string | null>) | null) {
  classifierOverride = fn;
}
type ReplyModel = (system: string, messages: { role: "user" | "assistant"; content: string }[]) => Promise<string | null>;
let replyOverride: ReplyModel | null = null;
export function setReplyModelForTests(fn: ReplyModel | null) {
  replyOverride = fn;
}

/** Round 7: one attempt, 2.5 s. A slow classifier must not hold a crisis message for ~9 s. */
export const CLASSIFIER_TIMEOUT_MS = 2_500;

export type ChatClassification = Classification & { modelAvailable: boolean; verdict: LlmVerdict | null };

/**
 * C2: keyword + context + LLM, failing closed. `"unavailable"` covers: no key,
 * API error, timeout. An ambiguous message with no usable verdict is a possible crisis.
 */
export async function classifyMessage(text: string, previous: string[] = []): Promise<ChatClassification> {
  let llm: LlmVerdict | null | "unavailable" = "unavailable";
  const input = buildClassifierInput(text, previous);
  const raw = classifierOverride
    ? await classifierOverride(input).catch(() => null)
    : await llmText(LLM_CLASSIFIER_PROMPT, [{ role: "user", content: input }], 60, CLASSIFIER_TIMEOUT_MS, 0);
  if (raw !== null) llm = parseLlmVerdict(raw);
  return { ...decide({ text, previous, llm }), modelAvailable: raw !== null, verdict: llm === "unavailable" ? null : llm };
}

/** NY GBL Art. 47: say "I'm an AI" at the start and at least every 3 hours of continuing chat. */
export const REDISCLOSE_MS = 3 * 60 * 60 * 1000;

export async function needsDisclosure(store: Store, memberId: string, now = Date.now()): Promise<boolean> {
  const last = await store.findOne("chat_messages", { member_id: memberId, role: "system_notice", safety: "disclosure" }, { orderBy: "created_at", desc: true });
  return !last || now - new Date(last.created_at).getTime() >= REDISCLOSE_MS;
}

export interface ChatTurnResult {
  reply: ChatMessage;
  /** Re-disclosure notice inserted before this reply, if one was due. */
  notice?: ChatMessage;
  safety: "crisis" | "support" | "scope" | "guarded" | "offline" | null;
  needsAgeGate?: boolean;
}

export async function handleChatTurn(store: Store, member: Member, character: Character, text: string): Promise<ChatTurnResult> {
  const trimmed = text.trim().slice(0, 2000);
  // Earlier un-flagged member turns give the classifier context (C2).
  const previous = (await store.find("chat_messages", { member_id: member.id, role: "user" }, { orderBy: "created_at", desc: true, limit: 4 }))
    .filter((m) => Date.now() - new Date(m.created_at).getTime() < 6 * 60 * 60 * 1000 && !m.safety)
    .reverse()
    .map((m) => m.content);
  let notice: ChatMessage | undefined;
  if (await needsDisclosure(store, member.id)) {
    notice = await store.insert("chat_messages", { member_id: member.id, character, role: "system_notice", content: `Reminder: ${disclosureLine(character)}`, safety: "disclosure" });
  }
  const userRow = await store.insert("chat_messages", { member_id: member.id, character, role: "user", content: trimmed, safety: null });

  const save = (content: string, safety: string | null) =>
    store.insert("chat_messages", { member_id: member.id, character, role: "assistant", content, safety });

  // 2. Crisis first, always, before any other logic.
  const cls = await classifyMessage(trimmed, previous);
  if (cls.category && (cls.severity === "crisis" || cls.severity === "support")) {
    await store.update("chat_messages", userRow.id, { safety: `flagged:${cls.category}` });
    const event = await store.insert("crisis_events", {
      member_id: member.id,
      surface: "chat",
      category: cls.category,
      detected_by: cls.detectedBy ?? "keyword",
      excerpt: trimmed.slice(0, 280),
      alerted: false,
      handled_at: null,
      chat_message_id: userRow.id,
      reply_message_id: null,
      member_cleared_at: null,
    });
    await store.insert("support_tickets", {
      member_id: member.id,
      email: member.email,
      reason: cls.severity === "crisis" ? "crisis_followup" : "grief_followup",
      message: trimmed.slice(0, 1000),
      status: "open",
    });
    // M6: no member words and no email in the page; details are in the admin.
    await alertOnCall(
      cls.severity === "crisis" ? `CRISIS (${cls.category}${cls.detectedBy === "fail_closed" ? ", possible" : ""}) in chat` : `Support follow-up (${cls.category})`,
      `crisis-${event.id}`,
    );
    await store.update("crisis_events", event.id, { alerted: true });
    const reply = await save(
      referralText(cls.category, { friendshipLine: env.friendshipLine || undefined, humanLine: humanLine(), possible: cls.detectedBy === "fail_closed" }),
      `crisis:${cls.category}`,
    );
    await store.update("crisis_events", event.id, { reply_message_id: reply.id });
    return { reply, notice, safety: cls.severity };
  }

  // Round 7: on a real deploy, no model means no coach. Rules alone miss too many
  // crisis messages to answer normally, so the chat goes offline for this message.
  if (env.chatRequiresModel && !cls.modelAvailable) return { reply: await goOffline(store, member, character, userRow.id, trimmed), notice, safety: "offline" };

  const answered = await coachReply(store, member, character, trimmed);
  if (!answered) return { reply: await goOffline(store, member, character, userRow.id, trimmed), notice, safety: "offline" };
  return { ...answered, notice };
}

/**
 * Round 7: the chat is offline for this message. Nothing rule-generated is sent
 * as a coach reply; a person reads the message (ticket + an hourly on-call page),
 * and the member sees 988, 911, the Eldercare Locator and how to reach a human.
 */
async function goOffline(store: Store, member: Member, character: Character, userRowId: string | null, text: string): Promise<ChatMessage> {
  if (userRowId) await store.update("chat_messages", userRowId, { safety: "offline" });
  await store.insert("support_tickets", { member_id: member.id, email: member.email, reason: "chat_offline_review", message: text.slice(0, 1000), status: "open" });
  const subject = `Coach chat offline: model unavailable (${new Date().toISOString().slice(0, 13)}h UTC)`;
  if (!(await store.findOne("outbox", { channel: "alert", subject }))) await alertOnCall(subject, "tickets");
  return store.insert("chat_messages", { member_id: member.id, character, role: "assistant", content: offlineText({ humanLine: humanLine() }), safety: "offline" });
}

/**
 * Steps 3-6 for a message the classifier has cleared (or the member cleared after
 * seeing the resources). Returns null when the model is required and unavailable.
 */
async function coachReply(store: Store, member: Member, character: Character, trimmed: string, prefix = ""): Promise<Omit<ChatTurnResult, "notice"> | null> {
  const save = (content: string, safety: string | null) =>
    store.insert("chat_messages", { member_id: member.id, character, role: "assistant", content, safety });
  // 3. Scope limits.
  const issue = detectScopeIssue(trimmed);
  if (issue) {
    const reply = await save(prefix + scopeReply(issue, character), `scope:${issue}`);
    return { reply, safety: "scope" };
  }

  // 4. Model (or offline stub).
  const memory = member.memory_enabled ? await store.find("memory_items", { member_id: member.id }) : [];
  const history = (await store.find("chat_messages", { member_id: member.id, character }, { orderBy: "created_at", desc: true, limit: 12 }))
    .reverse()
    .filter((m) => m.role !== "system_notice" && !/^(crisis|flagged|offline)/.test(m.safety ?? ""));
  const system = buildSystemPrompt(character, { firstName: member.first_name, track: member.track, memory, memoryEnabled: member.memory_enabled });
  const messages = history.map((m) => ({ role: m.role === "user" ? ("user" as const) : ("assistant" as const), content: m.content }));
  if (messages.length === 0 || messages[messages.length - 1]!.role !== "user") messages.push({ role: "user", content: trimmed });
  while (messages.length && messages[0]!.role !== "user") messages.shift();

  const modelReply = await llmText(system, messages, 400);
  // Round 7: scripted stubs are for local dev and the in-memory demo only.
  if (modelReply === null && env.chatRequiresModel) return null;
  const generated = modelReply ?? stubReply(character, trimmed, member);
  const guarded = guardOutput(generated, character);
  const reply = await save(prefix + guarded.text, guarded.replaced ? "guarded" : null);

  // 6. Opt-in memory.
  if (member.memory_enabled) await extractMemory(store, member, trimmed);

  return { reply, safety: guarded.replaced ? "guarded" : null };
}

/** How long after the resources were shown the member can still say "That's not what I meant". */
export const CLEAR_WINDOW_MS = 24 * 60 * 60 * 1000;
/** A model this sure it IS a crisis keeps the resources up even after the member taps clear. */
export const CLEAR_MODEL_VETO_CONFIDENCE = 0.8;

export type ClearFlagResult =
  | { ok: true; reply: ChatMessage; safety: ChatTurnResult["safety"] | "kept" }
  | { ok: false; reason: "not_found" | "already_cleared" | "expired" };

/**
 * Round 7: "That's not what I meant". Only offered under a resources reply, so the
 * member has always seen 988 / 911 first. Clearing records the member's word on the
 * crisis event (the alert, event and follow-up ticket stay), un-flags their message,
 * and lets the coach answer it. On a real deploy the model still has a say: if it is
 * confident the message is a crisis, the resources stay up; if it's unavailable, the
 * chat is offline as for any other message.
 */
export async function clearCrisisFlag(store: Store, member: Member, replyId: string, now = new Date()): Promise<ClearFlagResult> {
  const event = await store.findOne("crisis_events", { member_id: member.id, reply_message_id: replyId });
  const userRow = event?.chat_message_id ? await store.get("chat_messages", event.chat_message_id) : null;
  if (!event || !userRow || userRow.member_id !== member.id) return { ok: false, reason: "not_found" };
  if (event.member_cleared_at) return { ok: false, reason: "already_cleared" };
  if (now.getTime() - new Date(event.created_at).getTime() > CLEAR_WINDOW_MS) return { ok: false, reason: "expired" };
  // Single use, even with two taps racing.
  const [claimed] = await store.updateWhere("crisis_events", { id: event.id, member_cleared_at: null }, { member_cleared_at: now.toISOString() });
  if (!claimed) return { ok: false, reason: "already_cleared" };
  const character = userRow.character;
  const cls = await classifyMessage(userRow.content);
  const v = cls.verdict;
  if (v && v.category !== "none" && v.category !== "grief" && v.confidence >= CLEAR_MODEL_VETO_CONFIDENCE) {
    const reply = await store.insert("chat_messages", {
      member_id: member.id,
      character,
      role: "assistant",
      content: `Thank you for telling me. I'd still like to keep these numbers in front of you, just in case: call or text 988 any time, and call 911 in an emergency. ${humanLine()}`,
      safety: `crisis_kept:${event.category}`,
    });
    return { ok: true, reply, safety: "kept" };
  }
  await store.update("chat_messages", userRow.id, { safety: `cleared:${event.category}` });
  if (env.chatRequiresModel && !cls.modelAvailable) return { ok: true, reply: await goOffline(store, member, character, null, userRow.content), safety: "offline" };
  const answered = await coachReply(store, member, character, userRow.content, "Thanks for telling me. Let's carry on.\n\n");
  if (!answered) return { ok: true, reply: await goOffline(store, member, character, null, userRow.content), safety: "offline" };
  return { ok: true, reply: answered.reply, safety: answered.safety };
}

/** Offline, scripted replies in each character's voice (used when no API key). */
export function stubReply(character: Character, text: string, member: Pick<Member, "first_name" | "track">): string {
  const t = text.toLowerCase();
  const chang = character === "chang";
  if (/\b(real|human|person|robot|ai)\b/.test(t) && /\b(are you|you a|you're)\b/.test(t)) {
    return chang
      ? "No. I'm an AI character, made by the Strong Years team. My arms are pixels. Your legs are real. Let's use them."
      : "I'm AI. A team of people made me. My opinion of your breakfast is still real.";
  }
  if (/knee|stairs?/.test(t)) {
    return chang
      ? `Knees like strength, done gently. Try this. Chair against the wall. Sit tall. Stand up slowly, breathe out as you rise. Sit down slower. Five times. Too hard? Put a firm cushion on the seat. Sharp pain means stop. Mild ache that settles by tomorrow is okay. Today, tap "Sore knee" on your session and I'll swap it for you, ${member.first_name}.`
      : "Knees? Talk to Chang, he loves knees. From me: sit less, stand up more, and eat protein at breakfast. Muscles around the knee need material.";
  }
  if (/back|stiff/.test(t)) {
    return chang
      ? "Stiff mornings are common. Start in bed. Knees bent, rock them side to side, ten times. Then sit up slowly and wait a moment before you stand. At the counter, hinge at the hips, hands on the edge, back long. Breathe out. Sharp pain or numbness: stop and call your doctor. The \"Sore back\" swap is on today's session."
      : "Short version: move a little every hour. Sitting all day is the enemy. And a pillow that's older than your grandson? Replace it.";
  }
  if (/balance|fall|wobbl|steady/.test(t)) {
    return chang
      ? "Balance is trainable. Stand at the kitchen counter, one hand hovering above it. Feet together. Ten seconds. Then one foot a little ahead. Grab the counter any time. Pride is not a safety rail. Wednesday's session is all balance."
      : "I beat him at balance. 28 seconds. The chart is on our fridge. Practice while you brush your teeth, one hand on the sink. Two minutes a day.";
  }
  if (/protein|breakfast|eat|food|recipe|cook|soup|dinner|lunch/.test(t)) {
    return chang
      ? "Food is Sun's department. She'll tell you breakfast needs protein. She's right. Don't tell her I said that."
      : `Grams, not vibes, ${member.first_name}. Aim for about 25 to 30 grams of protein each meal. Two eggs and a cup of Greek yogurt gets you there. Or my silken tofu with soy and scallion. Kidney disease? Ask your doctor for your number first. This Sunday's recipes are in the Kitchen tab. Now go eat.`;
  }
  if (/sleep|tired|energy|awake/.test(t)) {
    return chang
      ? "Try the Sleep Wind-Down. Breathe in for 4, out for 6. Ten rounds, lying down. Never hold your breath. And a walk in the morning light helps the night."
      : "You drink coffee at 3 o'clock and then you blame the moon. Last caffeine before noon. Walk ten minutes after your biggest meal. Try that for a week, then tell me.";
  }
  if (/lonely|alone|friend/.test(t)) {
    return chang
      ? "Call one person today. Just to say hello. Then do your session. Both count."
      : "Call one person today. Sun Yoon says so. Then come to the Wednesday live. Real people there.";
  }
  return chang
    ? `Good question, ${member.first_name}. Today your track is ${member.track}. Eight minutes. Chair against the wall, breathe out when it's hard, stop if anything feels sharp. Press play and tell me your number after. Strong is a habit.`
    : `You want the truth or the nice version? Truth: eight minutes with Chang today, protein at breakfast, a walk after lunch. That's most of it. Write this down.`;
}

const STUB_MEMORY: { re: RegExp; fact: (m: RegExpMatchArray) => string; sensitive: boolean }[] = [
  { re: /[Mm]y (grandson|granddaughter|grandchild|grandkid)(?:'s name is| is named| named| is called)? ([A-Z][a-z]+)/, fact: (m) => `Has a ${m[1]} named ${m[2]}`, sensitive: false },
  { re: /my (left |right )?(knee|hip|back|shoulder|wrist|ankle)s? (hurts?|aches?|is sore|is stiff|are sore)/i, fact: (m) => `Mentioned a sore ${(m[1] ?? "").trim()} ${m[2]}`.replace(/\s+/g, " "), sensitive: true },
  { re: /i('m| am) (\d{2}) ?(years old)?\b/i, fact: (m) => `Is ${m[2]} years old`, sensitive: false },
  { re: /i (walk with|use) a (cane|walker)/i, fact: (m) => `Uses a ${m[2]}`, sensitive: true },
  { re: /my goal is (to )?([^.!?]{3,80})/i, fact: (m) => `Goal: ${m[2]}`, sensitive: false },
  { re: /i (have|own|got) (resistance bands?|a band|dumbbells|kettlebells?|a step)/i, fact: (m) => `Has ${m[2]} at home`, sensitive: false },
];

export async function extractMemory(store: Store, member: Member, text: string) {
  let facts: { fact: string; sensitive: boolean }[] = [];
  const raw = await llmText(MEMORY_EXTRACT_PROMPT, [{ role: "user", content: text }], 200);
  if (raw) {
    try {
      const parsed = JSON.parse(raw.match(/\{[\s\S]*\}/)?.[0] ?? "{}") as { facts?: { fact: string; sensitive?: boolean }[] };
      facts = (parsed.facts ?? []).filter((f) => typeof f.fact === "string" && f.fact.length < 200).map((f) => ({ fact: f.fact, sensitive: Boolean(f.sensitive) }));
    } catch {
      facts = [];
    }
  } else {
    for (const rule of STUB_MEMORY) {
      const m = text.match(rule.re);
      if (m) facts.push({ fact: rule.fact(m), sensitive: rule.sensitive });
    }
  }
  const existing = await store.find("memory_items", { member_id: member.id });
  for (const f of facts.slice(0, 5)) {
    if (existing.some((e) => e.fact.toLowerCase() === f.fact.toLowerCase())) continue;
    await store.insert("memory_items", { member_id: member.id, fact: f.fact, sensitive: f.sensitive, source: raw ? "llm" : "stub" });
  }
}
