"""Spanish reference pack renderer: reuses production/refs/render_refs.py unchanged, pointed at refs_es/.
DRY_RUN by default (writes refs_es/out/plan.json, calls nothing). STAGED items (Doña Carmen) are skipped unless
--include-staged. Generation spend is gated: the Spanish page opens at the $30K retained-MRR rung (CANON UPDATE 5).

  python3 production/refs_es/render_refs_es.py [--only CH01,LU01] [--include-staged]
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("render_refs", HERE.parent / "refs" / "render_refs.py")
rr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rr)
rr.HERE, rr.OUT = HERE, HERE / "out"            # locked refs live in refs_es/locked/, candidates in refs_es/out/
_load = rr.load_manifest


def load_es(path: Path = HERE / "manifest.json") -> dict:
    man = _load(path)                             # same sha256 lock check
    if "--include-staged" not in sys.argv:
        man["items"] = [it for it in man["items"] if it.get("stage", "LOCKED") != "STAGED"]
    return man


rr.load_manifest = load_es

if __name__ == "__main__":
    sys.exit(rr.main([a for a in sys.argv[1:] if a != "--include-staged"]))
