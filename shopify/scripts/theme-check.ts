/**
 * Runs Shopify's official Theme Check (@shopify/theme-check-node, the engine behind `shopify theme check`)
 * on ./theme with the recommended config. Exits 1 on any error-severity offense.
 * Usage: node scripts/theme-check.ts [--json]
 */
import path from "node:path";
import { themeCheckRun } from "@shopify/theme-check-node";

const root = path.resolve(new URL("../theme", import.meta.url).pathname);
const res: any = await themeCheckRun(root, undefined, (s: string) => process.stderr.write(""));
const offenses: any[] = res.offenses || res;
const sev = ["error", "warning", "info"];
const rows = offenses.map((o: any) => ({ severity: sev[o.severity] ?? o.severity, check: o.check, file: String(o.uri).replace(/^.*\/theme\//, "theme/"), line: (o.start?.line ?? 0) + 1, message: o.message }));
if (process.argv.includes("--json")) console.log(JSON.stringify(rows, null, 2));
else for (const r of rows) console.log(`${r.severity.padEnd(7)} ${r.check.padEnd(28)} ${r.file}:${r.line}  ${r.message}`);
const errors = rows.filter((r) => r.severity === "error").length;
console.log(`\nTheme Check: ${rows.length} offenses (${errors} errors, ${rows.length - errors} warnings/info).`);
process.exit(errors ? 1 : 0);
