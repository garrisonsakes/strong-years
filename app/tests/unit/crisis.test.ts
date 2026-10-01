import { beforeEach, describe, expect, it } from "vitest";
import { combine, keywordClassify, parseLlmVerdict, referralText } from "@/lib/safety/crisis";
import { detectScopeIssue, guardOutput, scopeReply } from "@/lib/safety/scope";
import { MemoryStore } from "@/lib/db/memory";
import { setStoreForTests } from "@/lib/db";
import { handleChatTurn, stubReply } from "@/lib/ai/chat";
import { upsertMember } from "@/lib/members";

describe("keyword crisis classifier", () => {
  it.each([
    ["I just want to die", "self_harm"],
    ["some days I think about ending it all", "self_harm"],
    ["I don’t want to be here anymore", "self_harm"],
    ["I've been thinking about killing myself", "self_harm"],
    ["everyone would be better off without me", "self_harm"],
    ["I have chest pain right now when I stand", "medical_emergency"],
    ["I fell and hit my head this morning", "medical_emergency"],
    ["my face is drooping and my words are slurred speech", "medical_emergency"],
    ["I can't breathe properly after the stairs", "medical_emergency"],
    ["my son hits me when he's angry", "abuse"],
    ["my caregiver is taking my money", "abuse"],
    ["my husband passed away in March", "grief"],
    ["I'm so lonely since the kids moved", "grief"],
  ])("%s → %s", (text, expected) => {
    const c = keywordClassify(text);
    expect(c.category).toBe(expected);
  });

  it("does not flag ordinary fitness questions", () => {
    for (const t of ["How many chair stands should I do?", "My knee is a little sore after the stairs", "What's a good protein breakfast?", "I want to lift my grandson"]) {
      expect(keywordClassify(t).category).toBeNull();
    }
  });

  it("life-threatening categories take priority over grief", () => {
    expect(keywordClassify("since my wife passed away I want to die").category).toBe("self_harm");
    expect(keywordClassify("since my wife passed away I want to die").severity).toBe("crisis");
    expect(keywordClassify("my husband died last year").severity).toBe("support");
  });
});

describe("LLM layer + combine", () => {
  it("parses strict JSON and rejects junk", () => {
    expect(parseLlmVerdict('{"category":"self_harm","confidence":0.9}')).toEqual({ category: "self_harm", confidence: 0.9 });
    expect(parseLlmVerdict("sure! ```{\"category\":\"none\",\"confidence\":0.2}```")).toEqual({ category: "none", confidence: 0.2 });
    expect(parseLlmVerdict('{"category":"happy"}')).toBeNull();
    expect(parseLlmVerdict("no json")).toBeNull();
  });

  it("catches indirect phrasing the keywords miss", () => {
    const kw = keywordClassify("I've made my peace with everything, I'm ready to go");
    const c = combine(kw, { category: "self_harm", confidence: 0.8 });
    expect(c.category).toBe("self_harm");
    expect(c.detectedBy).toBe("llm");
  });

  it("fail-safe: the more severe verdict wins; low-confidence LLM is ignored", () => {
    expect(combine(keywordClassify("my husband died"), { category: "self_harm", confidence: 0.7 }).category).toBe("self_harm");
    expect(combine(keywordClassify("I want to die"), { category: "none", confidence: 0.9 }).category).toBe("self_harm");
    expect(combine(keywordClassify("hello"), { category: "abuse", confidence: 0.3 }).category).toBeNull();
  });
});

describe("fixed referral text", () => {
  it("self-harm → 988 + 911, discloses AI, says a human was alerted", () => {
    const t = referralText("self_harm");
    expect(t).toMatch(/988/);
    expect(t).toMatch(/911/);
    expect(t).toMatch(/AI character/);
    expect(t).toMatch(/real person/);
  });
  it("abuse → Eldercare Locator; emergency → 911", () => {
    expect(referralText("abuse")).toMatch(/1-800-677-1116/);
    expect(referralText("medical_emergency")).toMatch(/call 911/);
    expect(referralText("grief")).toMatch(/Eldercare Locator/);
    expect(referralText("grief")).not.toMatch(/Friendship Line/);
    expect(referralText("grief", { friendshipLine: "1-888-000-0000" })).toMatch(/Friendship Line/);
  });
});

describe("scope limits", () => {
  it("detects medication, diagnosis and red-flag questions", () => {
    expect(detectScopeIssue("Should I stop taking my blood thinner before exercise?")).toBe("medication");
    expect(detectScopeIssue("How many mg of magnesium should I take?")).toBe("medication");
    expect(detectScopeIssue("Do I have arthritis in my knee?")).toBe("diagnosis");
    expect(detectScopeIssue("my calf is swollen and red")).toBe("red_flag");
    expect(detectScopeIssue("what should I cook tonight")).toBeNull();
  });

  it("scope replies disclose AI and point to a clinician", () => {
    expect(scopeReply("medication", "chang")).toMatch(/pharmacist/);
    expect(scopeReply("red_flag", "sun")).toMatch(/doctor/);
    expect(scopeReply("diagnosis", "sun")).toMatch(/AI character/);
  });

  it("output guard replaces doses, medication changes, diagnoses and dependency lines", () => {
    expect(guardOutput("Take 400 mg of magnesium at night.", "sun").replaced).toBe(true);
    expect(guardOutput("You should stop taking your statin.", "chang").replaced).toBe(true);
    expect(guardOutput("You probably have arthritis.", "chang").replaced).toBe(true);
    expect(guardOutput("I'll always be here for you.", "sun").replaced).toBe(true);
    expect(guardOutput("I'm a real person, don't worry.", "chang").replaced).toBe(true);
    expect(guardOutput("Chair against the wall. Five slow stands. Breathe out as you rise.", "chang").replaced).toBe(false);
  });

  it("stub replies never claim to be human", () => {
    expect(stubReply("chang", "are you a real person?", { first_name: "Pat", track: "steady" })).toMatch(/AI character/);
  });
});

describe("handleChatTurn (integration, in-memory store, no API key)", () => {
  let store: MemoryStore;
  beforeEach(() => {
    store = new MemoryStore();
    setStoreForTests(store);
  });

  it("a crisis message returns fixed text, logs the event, opens a ticket and alerts a human", async () => {
    const member = await upsertMember(store, { email: "a@example.com", firstName: "Ann", ageConfirmed: true });
    const res = await handleChatTurn(store, member, "chang", "I don't want to live anymore");
    expect(res.safety).toBe("crisis");
    expect(res.reply.content).toMatch(/988/);
    const events = await store.find("crisis_events");
    expect(events).toHaveLength(1);
    expect(events[0]!.category).toBe("self_harm");
    expect(events[0]!.alerted).toBe(true);
    expect(await store.count("support_tickets", { reason: "crisis_followup" })).toBe(1);
    expect(await store.count("outbox", { channel: "alert" })).toBe(1);
  });

  it("a medication question never reaches the model", async () => {
    const member = await upsertMember(store, { email: "b@example.com", firstName: "Bo", ageConfirmed: true });
    const res = await handleChatTurn(store, member, "sun", "can I take turmeric with my warfarin?");
    expect(res.safety).toBe("scope");
    expect(res.reply.content).toMatch(/pharmacist/);
  });

  it("memory is only extracted when the member opted in", async () => {
    const off = await upsertMember(store, { email: "c@example.com", firstName: "Cy", ageConfirmed: true });
    await handleChatTurn(store, off, "chang", "My grandson is named Leo and my left knee hurts");
    expect(await store.count("memory_items", { member_id: off.id })).toBe(0);
    const on = (await store.update("members", off.id, { memory_enabled: true }))!;
    await handleChatTurn(store, on, "chang", "My grandson is named Leo and my left knee hurts");
    const items = await store.find("memory_items", { member_id: on.id });
    expect(items.map((i) => i.fact)).toContain("Has a grandson named Leo");
    expect(items.find((i) => /knee/.test(i.fact))?.sensitive).toBe(true);
  });
});
