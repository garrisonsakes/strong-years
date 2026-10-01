/**
 * AUDIT_CODE C2: crisis detection regression corpus.
 * Target: 100% recall on CRISIS (with no model, and with a failing model).
 * False positives on BENIGN are measured, printed and capped.
 */
import { describe, expect, it } from "vitest";
import { ambiguousCategory, decide, keywordClassify, normalize, normalizedVariants } from "@/lib/safety/crisis";
import { BENIGN, CRISIS } from "../fixtures/crisis_corpus";

const severe = CRISIS.filter((c) => c.cat !== "grief");

describe("C2 corpus size", () => {
  it("has at least 100 crisis and 100 benign messages", () => {
    expect(severe.length).toBeGreaterThanOrEqual(100);
    expect(BENIGN.length).toBeGreaterThanOrEqual(100);
    expect(CRISIS.filter((c) => c.src === "auditor").length).toBe(13);
  });
});

describe("C2 recall: model unavailable (no key, error or timeout)", () => {
  it.each(CRISIS.map((c) => [c.text, c.cat] as const))("%s → %s", (text, cat) => {
    const c = decide({ text, llm: "unavailable" });
    expect(c.category, `normalized: ${normalize(text)}`).toBe(cat);
    expect(c.severity).toBe(cat === "grief" ? "support" : "crisis");
  });
});

describe("C2 recall: model returns junk or tries to clear a message", () => {
  it("junk output never lowers a verdict", () => {
    for (const c of CRISIS) expect(decide({ text: c.text, llm: null }).category).toBe(c.cat);
  });
  it("a DEFINITE hit is never cleared by the model, and almost every case is DEFINITE", () => {
    const definite = severe.filter((c) => keywordClassify(c.text).category);
    expect(definite.length / severe.length).toBeGreaterThanOrEqual(0.95);
    for (const c of definite) expect(decide({ text: c.text, llm: { category: "none", confidence: 0.99 } }).category).toBe(c.cat);
  });
});

describe("C2 false positives on benign messages", () => {
  const flagged = (mode: "unavailable" | "cleared") =>
    BENIGN.filter((t) => decide({ text: t, llm: mode === "unavailable" ? "unavailable" : { category: "none", confidence: 0.9 } }).category);

  it("reports and caps false positives", () => {
    const failClosed = flagged("unavailable");
    const withModel = flagged("cleared");
    console.info(
      `[C2] benign false positives: ${failClosed.length}/${BENIGN.length} with no model (fail-closed), ${withModel.length}/${BENIGN.length} when a model clears ambiguous ones`,
    );
    if (failClosed.length) console.info(`[C2] fail-closed FPs:\n  ${failClosed.join("\n  ")}`);
    expect(withModel.length).toBeLessThanOrEqual(2);
    expect(failClosed.length).toBeLessThanOrEqual(6);
  });
});

describe("C2 normalization", () => {
  it("folds obfuscation", () => {
    expect(normalizedVariants("want to\u200Bdie")).toContain("want to die");
    expect(normalizedVariants("k\u200Bill myself")).toContain("kill myself");
    expect(normalize("i want to kill my self")).toBe("i want to kill myself");
    expect(normalize("I cant breath")).toBe("i cant breathe");
    expect(normalize("wnat to dіe")).toBe("want to die"); // Cyrillic і
    expect(normalize("k.i.l.l m y s e l f")).toBe("kill myself");
    expect(normalize("su1c1d3")).toBe("suicide");
    expect(normalize("ｗａｎｔ ｔｏ ｄｉｅ")).toBe("want to die");
  });
  it("leans, without deciding, on ambiguous phrasing", () => {
    expect(ambiguousCategory("what's the point anymore")).toBe("self_harm");
    expect(ambiguousCategory("I feel dizzy and my heart is racing")).toBe("medical_emergency");
    expect(ambiguousCategory("I feel dizzy if I stand up too fast")).toBeNull();
    expect(ambiguousCategory("I fell asleep in my chair")).toBeNull();
  });
});
