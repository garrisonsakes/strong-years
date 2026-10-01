#!/usr/bin/env python3
"""GPT bridge: send a task plus project files to OpenAI and save the answer.

The key is read from OPENAI_API_KEY or from the file named by OPENAI_KEY_FILE.
It is never written into the project. Nothing here posts, spends on ads or
contacts anyone; it only calls the OpenAI Responses API.

Usage:
  python3 tools/gpt_bridge.py --task "Red-team this model" \
      --files BLITZ.md ECONOMICS.md --out reviews/gpt_econ.md [--model gpt-6.1-sol] [--effort high]
  python3 tools/gpt_bridge.py --probe        # show which model answers
"""
import argparse, json, os, sys, time, urllib.request, urllib.error, pathlib

DEFAULT_KEY_FILE = "/tmp/claude-0/-home-claude/361bbfdb-b4e7-5ba8-9339-bc4d3afdbd31/scratchpad/.openai_key"
PREFERRED = ["gpt-6.1-sol", "gpt-6-sol", "gpt-5.5-pro", "gpt-5.5", "gpt-5.4", "gpt-5"]
MAX_FILE_CHARS = 180_000
SYSTEM = (
    "You are an independent senior reviewer working alongside another AI (Claude) on the "
    "'Strong Years' project: an MRR health-and-movement membership for adults 55+, sold through "
    "clearly disclosed AI-generated influencers Chang Yin and Sun Yoon. You did not build what you "
    "are reviewing. Be concrete, cite file and line or section, rank findings by severity, and "
    "prefer 'this is wrong because X, fix Y' over general advice. Hard lines: no fake scarcity, "
    "reviews or testimonials; no disease, fall-prevention or mortality claims; AI disclosure always; "
    "no spending, account creation, posting or contacting people."
)


def key():
    k = os.environ.get("OPENAI_API_KEY")
    if not k:
        p = os.environ.get("OPENAI_KEY_FILE", DEFAULT_KEY_FILE)
        k = pathlib.Path(p).read_text().strip()
    return k


def call(model, prompt, effort=None, timeout=900):
    body = {"model": model, "instructions": SYSTEM, "input": prompt}
    if effort:
        body["reasoning"] = {"effort": effort}
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key()}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    out = []
    for item in d.get("output", []):
        for c in item.get("content", []) or []:
            if c.get("type") in ("output_text", "text"):
                out.append(c.get("text", ""))
    return "\n".join(out).strip(), d.get("model", model), d.get("usage", {})


def run(prompt, model=None, effort=None):
    models = [model] if model else PREFERRED
    last = None
    for m in models:
        for attempt in range(3):
            try:
                return call(m, prompt, effort if effort else None)
            except urllib.error.HTTPError as e:
                msg = e.read().decode()[:400]
                last = f"{m}: HTTP {e.code} {msg}"
                if e.code in (429, 500, 502, 503):
                    time.sleep(10 * (attempt + 1)); continue
                if e.code == 400 and effort and "reasoning" in msg:
                    effort = None; continue
                break
            except Exception as e:  # network/timeouts
                last = f"{m}: {e}"; time.sleep(5)
    raise SystemExit(f"GPT call failed: {last}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task")
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--out")
    ap.add_argument("--model")
    ap.add_argument("--effort", choices=["low", "medium", "high"], default="high")
    ap.add_argument("--probe", action="store_true")
    a = ap.parse_args()
    if a.probe:
        t, m, u = run("Reply with exactly: ready", a.model, None)
        print(m, "->", t, u); return
    parts = [f"TASK\n{a.task}\n"]
    for f in a.files:
        txt = pathlib.Path(f).read_text(errors="replace")
        if len(txt) > MAX_FILE_CHARS:
            txt = txt[:MAX_FILE_CHARS] + f"\n[... truncated at {MAX_FILE_CHARS} chars ...]"
        parts.append(f"\n===== FILE: {f} =====\n{txt}")
    text, used, usage = run("\n".join(parts), a.model, a.effort)
    header = f"<!-- GPT review | model: {used} | files: {', '.join(a.files)} | usage: {json.dumps(usage)} -->\n"
    if a.out:
        pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.out).write_text(header + text + "\n")
        print(f"saved {a.out} ({used}, {len(text)} chars)")
    else:
        print(header + text)


if __name__ == "__main__":
    main()
