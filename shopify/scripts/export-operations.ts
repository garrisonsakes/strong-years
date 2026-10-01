/**
 * Runs the plan in DRY_RUN for every phase/engine and writes:
 *  - test/fixtures/operations.graphql : each distinct operation with its variables INLINED as GraphQL
 *    literals, so Shopify's validate_graphql_codeblocks (read-only MCP tool) checks input shapes too,
 *    not just the documents.
 * Usage: node scripts/export-operations.ts [--print]
 */
import { writeFileSync, mkdirSync } from "node:fs";
import { dryRunner } from "../src/client.ts";
import { runPlan } from "../src/plan.ts";
import { OPS } from "../src/operations.ts";
import { factsFromEnv } from "../src/provision.ts";

const ENUM_KEYS = new Set(["status", "inventoryPolicy", "unit", "adjustmentType", "interval", "category", "format", "storefront", "ownerType", "all"]);

function lit(v: unknown, key: string, parent: string): string {
  if (v === null || v === undefined) return "null";
  if (Array.isArray(v)) return `[${v.map((x) => lit(x, key, parent)).join(", ")}]`;
  if (typeof v === "object") return `{ ${Object.entries(v as object).map(([k, x]) => `${k}: ${lit(x, k, key)}`).join(", ")} }`;
  if (typeof v === "string") {
    const isEnum = ENUM_KEYS.has(key) || (key === "type" && parent === "shopPolicy") || key === "topic";
    return isEnum ? v : JSON.stringify(v);
  }
  return String(v);
}

export function inline(opName: keyof typeof OPS, variables: Record<string, unknown>): string {
  const doc = OPS[opName].trim();
  const header = doc.match(/^(query|mutation)\s+\w+(\([^)]*\))?\s*\{/);
  if (!header) return doc;
  let body = doc.slice(header[0].length);
  for (const [k, v] of Object.entries(variables)) body = body.replace(new RegExp(`\\$${k}\\b`, "g"), lit(v, k, ""));
  return `${header[1]} ${opName}Inline {${body}`;
}

export async function collect() {
  const facts = factsFromEnv({ ...process.env });
  const seen = new Map<string, string>();
  const runs: Array<[any, any]> = [["shopify_subscriptions", "core"], ["app", "core"], ["shopify_subscriptions", "verify"]];
  for (const [engine, phase] of runs) {
    const g = dryRunner(() => {});
    await runPlan(g, { engine, phase, membersAppUrl: "https://members.strongyears.com", facts, foundingCloseDateIso: "2027-01-09", nowIso: "2026-10-01T00:00:00Z" });
    for (const op of g.recorded) {
      const key = `${op.op}:${op.step.replace(/[^A-Za-z]/g, "").slice(0, 18)}`;
      if (!seen.has(op.op) || op.op === "ProductUpsert" || op.op === "DiscountCodeCreate" || op.op === "SellingPlanGroupCreate") {
        seen.set(key, inline(op.op, op.variables));
      }
    }
  }
  return seen;
}

if (import.meta.url === new URL(`file://${process.argv[1]}`).href) {
  const seen = await collect();
  mkdirSync(new URL("../test/fixtures/", import.meta.url), { recursive: true });
  const out = [...seen.entries()].map(([k, v]) => `# ${k}\n${v}\n`).join("\n");
  writeFileSync(new URL("../test/fixtures/operations.graphql", import.meta.url), out);
  if (process.argv.includes("--print")) console.log(out);
  console.log(`wrote ${seen.size} inlined operations to test/fixtures/operations.graphql`);
}
