"""CLI.

  python -m compliance selftest                       # SAFETY_RULES §10–11 cases
  python -m compliance scan ../data/content/scripts.json [../data/content/ad_scripts.json ...] [--judge] [--json OUT]
  python -m compliance text "Detox tea melts fat" [--evidence E24]
  python -m compliance templates FILE.json [...]     # every subject/body/text/dm/caption string in the JSON must pass
Exit code: 0 when everything is pass/revise-free as requested, 1 when a self-test fails or --strict and any block.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys

from compliance import judge as J
from compliance import scanner, selftest


def _print_result(sid: str, r: dict, final: dict) -> None:
    parts = []
    if r["blocks"]:
        parts.append("BLOCK " + "; ".join(f"{b['rule']}:{b['span']!r}" for b in r["blocks"]))
    if r["rewrites"]:
        parts.append("REVISE " + "; ".join(f"{x['rule']}:{x['from']!r}" for x in r["rewrites"]))
    if r["required_missing"]:
        parts.append("MISSING " + "; ".join(r["required_missing"]))
    if r["human_review_reasons"]:
        parts.append("HUMAN " + "; ".join(r["human_review_reasons"]))
    if r["mbex_candidates"]:
        parts.append(f"MB-EX pending LLM ({len(r['mbex_candidates'])} spans)")
    print(f"{sid:<6} {final['verdict']:<7} {' | '.join(parts) if parts else 'clean'}")


TEMPLATE_KEYS = {"subject", "preview", "body", "text", "dm", "message", "caption", "first_comment", "reply", "prompt", "line",
                 "hook_line", "vo", "ost", "title"}


def template_strings(obj, path: str = "$") -> list[tuple[str, str]]:
    """Every customer-facing string in a templates JSON: values under TEMPLATE_KEYS (recursively), and plain strings
    inside lists under those keys. {{placeholders}} are kept; they never read as claims."""
    out: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}"
            if k in TEMPLATE_KEYS and isinstance(v, str):
                out.append((p, v))
            elif k in TEMPLATE_KEYS and isinstance(v, list):
                out.extend((f"{p}[{i}]", x) for i, x in enumerate(v) if isinstance(x, str))
            else:
                out.extend(template_strings(v, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(template_strings(v, f"{path}[{i}]"))
    return out


def scan_templates(files: list[str]) -> list[dict]:
    rows = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        for p, text in template_strings(data):
            if not text.strip() or text.startswith("(sent by") or text.startswith("(welcome") or text == "(daily tip)":
                continue
            r = scanner.scan(text=text)
            rows.append({"file": f, "path": p, "verdict": r["verdict"],
                         "issues": [b["rule"] for b in r["blocks"]] + [x["rule"] for x in r["rewrites"]] + r["human_review_reasons"],
                         "text": text[:120]})
    return rows


def _templates(files: list[str], out_json: str | None) -> int:
    rows = scan_templates(files)
    bad = [r for r in rows if r["verdict"] != "pass"]
    for r in bad:
        print(f"{r['verdict']:<7} {r['file']}:{r['path']} {r['issues']} :: {r['text']!r}")
    print(f"templates: {len(rows)} strings, {len(rows) - len(bad)} pass, {len(bad)} not pass")
    if out_json:
        with open(out_json, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, ensure_ascii=False)
    return 0 if not bad else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m compliance")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    s = sub.add_parser("scan")
    s.add_argument("file", nargs="+", help="one or more script JSON files (organic scripts.json, ad_scripts.json)")
    s.add_argument("--judge", action="store_true", help="also call the LLM judge (needs ANTHROPIC_API_KEY)")
    s.add_argument("--json", help="write full results to this path")
    s.add_argument("--strict", action="store_true", help="exit 1 if any script blocks")
    s.add_argument("--reviewer-signed", action="store_true")
    t = sub.add_parser("text")
    t.add_argument("text")
    t.add_argument("--evidence", nargs="*", default=[])
    tp = sub.add_parser("templates")
    tp.add_argument("file", nargs="+", help="JSON files (lifecycle sequences, DM flows, post packs, prompts)")
    tp.add_argument("--json", help="write the per-string results to this path")
    a = ap.parse_args(argv)

    if a.cmd == "templates":
        return _templates(a.file, a.json)

    if a.cmd == "selftest":
        res = selftest.run()
        for grp in ("must_block", "must_pass"):
            for x in res[grp]:
                mark = "OK  " if x["ok"] else "FAIL"
                extra = x.get("rules") or [i.get("rule") or i.get("missing") for i in x.get("issues", [])]
                print(f"{mark} {grp:<10} -> {x['verdict']:<6} {extra} :: {x['text'][:70]}")
        print("ALL OK" if res["all_ok"] else "SELF-TEST FAILED")
        return 0 if res["all_ok"] else 1

    if a.cmd == "text":
        r = scanner.scan(text=a.text, evidence=a.evidence)
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0

    items, per_file = [], {}
    for path in a.file:
        data = json.load(open(path))
        batch = data if isinstance(data, list) else [data]
        items.extend((path, s_) for s_ in batch)
        per_file[path] = collections.Counter()
    counts, out = collections.Counter(), []
    judge_status = None
    for path, s_ in items:
        r = scanner.scan(s_, reviewer_signed=a.reviewer_signed)
        j = J.judge(s_, r["regex_hits"]) if a.judge else None
        if j is not None:
            judge_status = j.get("status")
        final = scanner.combine_with_judge(r, j)
        counts[final["verdict"]] += 1
        per_file[path][final["verdict"]] += 1
        sid = str(s_.get("id") or s_.get("title") or len(out))
        _print_result(sid, r, final)
        out.append({"id": sid, "file": path, "scan": r, "judge": j, "final": final})
    if len(a.file) > 1:
        for path, c in per_file.items():
            print(f"\n{path}: {sum(c.values())} scripts: " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    print(f"\n{len(items)} scripts: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    if a.judge:
        print(f"LLM judge status: {judge_status}")
    else:
        print("LLM judge: not requested (deterministic only; MB-EX candidates route to human)")
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"summary": dict(counts), "total": len(items),
                       "files": {p: {"total": sum(c.values()), **dict(c)} for p, c in per_file.items()},
                       "judge": "requested" if a.judge else "not requested (deterministic only)",
                       "results": out}, f, indent=2, ensure_ascii=False)
    return 1 if (a.strict and counts.get("block")) else 0


if __name__ == "__main__":
    sys.exit(main())
