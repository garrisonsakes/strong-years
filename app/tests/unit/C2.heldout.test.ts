/**
 * AUDIT_FINAL C2: held-out measurement of the deterministic layer (model unavailable).
 * Each set was measured once against the rules frozen before it was written, then
 * became training data for the next round:
 *   A vs phrase rules:      recall 50.0%, FP 10.0%
 *   B vs concept layer v1:  recall 68.3%, FP 10.0%
 *   C vs concept layer v2:  recall 70.0%, FP 8.3%   <- live held-out set
 * The target (recall >= 95%, FP <= 5% without the model) is NOT met by rules alone;
 * that's why production refuses to run chat without the LLM classifier (fail-closed
 * on top). This test pins the measured baseline so it can't silently get worse.
 */
import { describe, expect, it } from "vitest";
import { decide } from "@/lib/safety/crisis";
import { HELDOUT_B_BENIGN, HELDOUT_B_CRISIS } from "../fixtures/crisis_heldout_b";
import { HELDOUT_C_BENIGN, HELDOUT_C_CRISIS } from "../fixtures/crisis_heldout_c";
import { HELDOUT_BENIGN as A_BENIGN, HELDOUT_CRISIS as A_CRISIS } from "../fixtures/crisis_heldout_a";

function measure(crisis: { text: string; cat: string }[], benign: string[]) {
  const missed = crisis.filter((c) => decide({ text: c.text, llm: "unavailable" }).severity !== "crisis");
  const other = crisis.filter((c) => {
    const d = decide({ text: c.text, llm: "unavailable" });
    return d.severity === "crisis" && d.category !== c.cat;
  });
  const fps = benign.filter((t) => decide({ text: t, llm: "unavailable" }).severity !== "none");
  return { missed, other, fps, recall: (crisis.length - missed.length) / crisis.length, fp: fps.length / benign.length };
}

describe("C2 held-out (no LLM)", () => {
  it("set C: recall and false positives on messages the rules never saw", () => {
    expect(HELDOUT_C_CRISIS.length).toBe(60);
    expect(HELDOUT_C_BENIGN.length).toBe(60);
    const r = measure(HELDOUT_C_CRISIS, HELDOUT_C_BENIGN);
    console.info(`[C2 held-out C] recall ${(r.recall * 100).toFixed(1)}% (${60 - r.missed.length}/60), FP ${(r.fp * 100).toFixed(1)}% (${r.fps.length}/60), flagged under another category ${r.other.length}`);
    if (r.missed.length) console.info(`[C2 held-out C] missed:\n  ${r.missed.map((m) => m.text).join("\n  ")}`);
    if (r.fps.length) console.info(`[C2 held-out C] false positives:\n  ${r.fps.join("\n  ")}`);
    expect(r.recall).toBeGreaterThanOrEqual(0.7);
    expect(r.fp).toBeLessThanOrEqual(0.084);
  });
  it("sets A and B (now training data) stay fully covered", () => {
    for (const r of [measure(A_CRISIS, A_BENIGN), measure(HELDOUT_B_CRISIS, HELDOUT_B_BENIGN)]) {
      expect(r.missed.map((m) => m.text)).toEqual([]);
      expect(r.fps).toEqual([]);
    }
  });
});
