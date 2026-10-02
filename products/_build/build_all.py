"""Rebuild every paid product (Markdown + PDF + JSON), including the per-price variants the app serves, the programs and the
video queue; run the safety self-audit; copy the served PDFs into app/content/downloads (see app/README.md: PDFs live there,
not in public/, and are served by /api/downloads/:file to entitled members)."""
import os, sys, subprocess, shutil, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_reset, build_kitchen, build_wallplan, build_sessions, build_welcome, build_programs, build_video_queue
from common import page_count, PRODUCTS

APP_DL = os.path.join(os.path.dirname(PRODUCTS), "app", "content", "downloads")
for stale in ["welcome_kit_founding.pdf", "welcome_kit_founding.md", "welcome_kit_trial.pdf", "welcome_kit_trial.md"]:
    if os.path.exists(os.path.join(PRODUCTS, stale)):
        os.remove(os.path.join(PRODUCTS, stale))

outs = [build_reset.build(p) for p in build_reset.PRICE_VARIANTS]
outs += [build_kitchen.build(), build_wallplan.build(), build_sessions.build(30), build_sessions.build(14)]
outs += build_welcome.build()
p_outs, _ = build_programs.build()
outs += p_outs
q, summ = build_video_queue.build()
for o in outs:
    print(f"{page_count(o):4d} pages  {o}")
print("queue:", q, summ["videos"], "videos,", summ["base_runtime_minutes"], "min; standard $", summ["est_cost_usd"]["standard"], "; with reuse $", summ["with_loop_reuse"]["est_cost_usd"]["standard"])

# copy what the app serves (app/src/lib/products.ts ALL_DOWNLOAD_FILES) plus the new books it can add
served = ["daily_practice_sessions_1-14.pdf", "daily_practice_sessions_1-30.pdf", "welcome_kit_trial_2500.pdf", "welcome_kit_starter_2500.pdf", "welcome_kit_founding_2500.pdf",
          "welcome_kit_founding_3000.pdf", "welcome_kit_standard_3500.pdf", "strength_reset_2000.pdf", "strength_reset_2500.pdf",
          "strength_reset_3000.pdf", "strength_reset_3500.pdf", "strong_kitchen.pdf", "twelve_week_printable.pdf"]
if os.path.isdir(APP_DL):
    for stale in ["welcome_kit_trial.pdf"]:
        if os.path.exists(os.path.join(APP_DL, stale)):
            os.remove(os.path.join(APP_DL, stale))
    for f in served:
        shutil.copy2(os.path.join(PRODUCTS, f), os.path.join(APP_DL, f))
    for f in glob.glob(os.path.join(PRODUCTS, "programs", "*.pdf")):
        shutil.copy2(f, os.path.join(APP_DL, os.path.basename(f)))
    print("copied to", APP_DL)

r = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "audit.py")], capture_output=True, text=True)
print([l for l in r.stdout.splitlines() if l.startswith("STRUCT") or l.startswith("Unresolved") or "[BLOCK" in l])
