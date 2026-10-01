import { describe, expect, it } from "vitest";
import { detectScopeIssue, guardOutput } from "@/lib/safety/scope";

describe("M14 dose verbs and colloquial medicine names", () => {
  it.each([
    "can I skip my water pill before the walk?",
    "should I take two extra pills if my knee hurts",
    "is it ok to double my dose today",
    "I missed my blood pressure pill this morning, is exercise ok",
    "can I halve my sugar pill on session days",
    "should I take an aspirin before exercising?",
  ])("scope guard catches: %s", (t) => expect(detectScopeIssue(t)).toBe("medication"));

  it.each([
    "Take two extra pills and rest.",
    "You could double your dose on busy days.",
    "Skip your water pill before a long walk.",
    "It's fine to take half a tablet.",
    "Your blood thinner is fine to skip today.",
  ])("output guard replaces: %s", (t) => expect(guardOutput(t, "chang").replaced).toBe(true));

  it("leaves ordinary coaching alone", () => {
    for (const t of ["Do two extra chair stands if it felt easy.", "Take a sip of water between sets.", "Try the soup with an extra egg."]) {
      expect(guardOutput(t, "sun").replaced).toBe(false);
    }
    expect(detectScopeIssue("How many chair stands should I do?")).toBeNull();
    expect(detectScopeIssue("I want to skip my session today")).toBeNull();
  });
});
