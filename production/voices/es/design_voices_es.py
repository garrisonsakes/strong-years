"""Spanish voice design: reuses production/voices/design_voices.py unchanged, pointed at voice_design_es.json.
DRY_RUN by default (writes voices/es/out/plan.json, calls nothing). STAGED voices (Doña Carmen) are skipped unless
--include-staged. Designed voices only, never cloned. Spend gated on the Spanish page's $30K retained-MRR rung.

  python3 production/voices/es/design_voices_es.py [--only chuy,lupe] [--include-staged]
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("design_voices", HERE.parent / "design_voices.py")
dv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dv)

if __name__ == "__main__":
    design = json.loads((HERE / "voice_design_es.json").read_text(encoding="utf-8"))
    if "--include-staged" not in sys.argv:
        design["voices"] = {k: v for k, v in design["voices"].items() if v.get("stage") != "STAGED"}
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    (out / "voice_design.json").write_text(json.dumps(design, indent=2, ensure_ascii=False), encoding="utf-8")
    dv.HERE, dv.OUT = out, out   # design_voices reads HERE/voice_design.json and writes OUT/plan.json
    sys.exit(dv.main([a for a in sys.argv[1:] if a != "--include-staged"]))
