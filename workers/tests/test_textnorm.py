"""AUDIT_FINAL H10 regression: normalisation hardening, a held-out corpus, and Python / n8n-JS / build_content parity."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from common import config
from compliance import rules as R
from compliance import scanner, textnorm

HELD = json.loads((Path(__file__).parent / "fixtures" / "scanner_heldout.json").read_text())
HELD3 = json.loads((Path(__file__).parent / "fixtures" / "scanner_heldout_r3.json").read_text())

# The verifier's 10 strings (AUDIT_FINAL.md §2a H10), with no condition word, so the obfuscated verb is what's tested
FINAL = ["ᴄᴜʀᴇs you overnight", "𝐜𝐮𝐫𝐞𝐬 you overnight", "Ⓒⓤⓡⓔⓢ you overnight", "c/u/r/e/s you overnight",
         "cüres you overnight", "c—u—r—e—s you overnight", "c*res you overnight", "Detöx your liver",
         "cúres you overnight", "mírácle tea", "ćures you overnight"]


@pytest.mark.parametrize("text", FINAL)
def test_final_verifier_strings_block(text):
    assert scanner.scan(text=text)["verdict"] == "block", text


def test_heldout_corpus_rates():
    missed = [t for t in HELD["bypass"] if scanner.scan(text=t)["verdict"] != "block"]
    fps = [t for t in HELD["benign"] if scanner.scan(text=t)["verdict"] == "block"]
    assert missed == [], missed                      # target: 100% of 40 bypass attempts blocked
    assert len(fps) <= 2, fps                        # target: <= 2 false positives on 40 look-alike benign lines


@pytest.mark.parametrize("fn,inp,out", [
    ("fold", "cüres Detöx mírácle", "cures Detox miracle"),
    ("collapse", "c — u — r — e — s", "cures"),
    ("unmask", "c*res d#tox m1racle", "cures detox miracle"),
    ("join_split", "de tox tea", "detox tea"),
    ("squash_stems", "cuures", "cures"),
])
def test_textnorm_steps(fn, inp, out):
    assert getattr(textnorm, fn)(inp) == out


def test_folds_are_match_only_and_keep_legit_words():
    assert textnorm.canon("Señora Sun cocina") == "Señora Sun cocina"       # displayed text keeps Spanish accents
    assert textnorm.squash_stems("Current coffee") == "Current coffee"
    assert textnorm.unmask("5g 30-second 4-6 70% E11 don't") == "5g 30-second 4-6 70% E11 don't"


def _block_regexes():
    bc = [(p["id"], p["regex"]) for p in R.blocked_claims_doc()["patterns"] if p["severity"] == "block"]
    sr = [(f"SR3.1-{i:02d}", r"\b(?:" + pat + ")") for i, (pat, sev, _n) in
          enumerate(R.parse_safety_31((config.SPEC_DIR / "SAFETY_RULES.md").read_text()), 1) if sev == "block"]
    return bc + sr


def _py_hit(rx: str, t: str) -> bool:
    r = re.compile(rx, re.I)
    vs = textnorm.variants(t)
    base = vs[0].lower()
    for vi, v in enumerate(vs):
        for m in r.finditer(v):
            if not m.group(0).strip() or (vi and m.group(0).lower() in base):
                continue
            sent = next((s for s in re.split(r"(?<=[.!?])\s+", v) if m.group(0) in s), v)
            if textnorm.is_benign(m.group(0), sent):
                continue
            return True
    return False


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
@pytest.mark.parametrize("node_name", ["Parse Script + Regex Pre-Scan", "Parse Packaging + Compliance Pass 2"])
def test_n8n_js_matches_python_on_heldout(node_name, tmp_path):
    wf = json.loads((config.SPEC_DIR / "n8n_core_workflow.json").read_text())
    code = next(n for n in wf["nodes"] if n["name"] == node_name)["parameters"]["jsCode"]
    js = code[code.index("// AUDIT H10 BEGIN"):code.index("// AUDIT H10 END")]
    texts = HELD["bypass"] + HELD["benign"] + FINAL + HELD3["bypass"] + HELD3["benign"] + [o for o, _p in ROUND2] + MULTI + SYMBOL + UNITS
    regs = _block_regexes()
    js += ("\nconst T=" + json.dumps(texts) + ";const R=" + json.dumps(regs) + ";\n"
           "console.log(JSON.stringify(T.map(t=>R.map(([id,rx])=>!!matchAny(new RegExp(rx,'i'),t)))));")
    f = tmp_path / "p.js"
    f.write_text(js)
    r = subprocess.run(["node", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-500:]
    got = json.loads(r.stdout)
    mism = [(regs[j][0], t) for i, t in enumerate(texts) for j in range(len(regs)) if _py_hit(regs[j][1], t) != got[i][j]]
    assert mism == [], mism[:10]


def test_n8n_block_is_generated_from_shared_tables():
    from tools.patch_workflow import TN_BLOCK
    wf = json.loads((config.SPEC_DIR / "n8n_core_workflow.json").read_text())
    for name in ("Parse Script + Regex Pre-Scan", "Parse Packaging + Compliance Pass 2"):
        code = next(n for n in wf["nodes"] if n["name"] == name)["parameters"]["jsCode"]
        assert TN_BLOCK in code, f"{name}: stale H10 block, run python -m tools.patch_workflow"


def test_build_content_uses_same_normalisation():
    spec = importlib.util.spec_from_file_location("bc_tool", config.SPEC_DIR / "tools" / "build_content.py")
    bc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bc)
    assert Path(bc.TEXTNORM.__file__).resolve() == Path(textnorm.__file__).resolve()
    hits = [m.group(0) for m, _v in bc.tn_finditer(r"\bcur(e|es|ed|ing)\b", "This tea c*res gout. Cured meats on the board.")]
    assert hits == ["cures"]
    probs = bc.blocked_claims_scan("T", {"caption": "Detöx your liver", "spoken": "Cured meats and olives."})
    assert len(probs) >= 1 and all("caption" in p for p in probs)


# AUDIT_FINAL §6 round 2: the 5 strings that passed while their plain form blocked or revised (+ the paraphrase)
ROUND2 = [("c‧u‧r‧e‧s you overnight", "cures you overnight"),
          ("c⸱u⸱r⸱e⸱s you overnight", "cures you overnight"),
          ("Boosts ur imm-une system", "Boosts your immune system"),
          ("clinicaIly proven", "clinically proven"),
          ("Lowers stress lnstantly", "Lowers stress instantly")]


@pytest.mark.parametrize("obf,plain", ROUND2)
def test_round2_obfuscations_match_plain_verdict(obf, plain):
    want = scanner.scan(text=plain)["verdict"]
    assert want in ("block", "revise")
    assert scanner.scan(text=obf)["verdict"] == want, obf


def test_round2_paraphrase_medication_exit_blocks():
    assert scanner.scan(text="Say goodbye to your pills forever")["verdict"] == "block"
    assert scanner.scan(text="Don't say goodbye to your pills.")["verdict"] == "pass"


@pytest.mark.parametrize("word", ["cares", "curas", "heels", "pulls", "blond", "sugars", "Current"])
def test_fuzzy_never_folds_real_words(word):
    assert textnorm.fuzzy(word) == word


def test_heldout_round3_rates():
    """Round-3 held-out set. First (untuned) run: 17/20 blocked, 1 FP. The 3 misses (Damerau transposition 'cuers',
    possessive "dettox's", uncovered 'Guaranteeing zero side effects') were fixed afterwards, so this now asserts
    the post-fix state. Remaining FP by design: D-07 'sacred' in the proper noun 'Sacred Heart Hospital'."""
    missed = [t for t in HELD3["bypass"] if scanner.scan(text=t)["verdict"] != "block"]
    fps = [t for t in HELD3["benign"] if scanner.scan(text=t)["verdict"] == "block"]
    assert missed == [] and len(fps) <= 1, (missed, fps)


# Round 3: multi-character leet / lookalikes
MULTI = ["c|_|res arthritis", "This tea c(_)res gout", "|)etox your liver", "A m1r/\\cle drink", "Rev3r$es diabetes",
         "c|_|r3s knee pain overnight"]


@pytest.mark.parametrize("text", MULTI)
def test_multichar_lookalikes_block(text):
    assert scanner.scan(text=text)["verdict"] == "block", text


@pytest.mark.parametrize("text", [":) Have a nice walk | see you tomorrow", "Frank <3 Sun", "Sets: 3 x 10 | rest 60 s",
                                  "Walk (_) then rest"])
def test_multichar_leaves_emoticons_and_separators(text):
    assert scanner.scan(text=text)["verdict"] != "block"


def test_multichar_parity_js_included():
    assert textnorm.multichar("c|_|res") == "cures"
    code = (Path(textnorm.__file__).with_name("textnorm.js")).read_text()
    assert "tnMulti" in code and "multichar" in (Path(textnorm.__file__).with_name("textnorm_data.json")).read_text()


# Round 4: symbol look-alikes inside words; units/numbers never folded
SYMBOL = ["¢ures you overnight", "©ures you overnight", "detøx tea", "miræcle? no: c®res? no: ©ures arthritis",
          "µures you overnight", "d£tox? no, d€tox your liver"]
UNITS = ["Take 20 μg of B12 with food.", "Take 20 µg daily with breakfast.", "Water at 60°C for the tea.",
         "10µl drops of vanilla.", "Straße walk with Frank.", "Æsop fable night at the library."]


@pytest.mark.parametrize("text", SYMBOL)
def test_symbol_letters_inside_words_block(text):
    assert scanner.scan(text=text)["verdict"] == "block", text


@pytest.mark.parametrize("text", UNITS)
def test_units_and_numbers_not_folded(text):
    r = scanner.scan(text=text)
    assert r["verdict"] != "block", (text, r["blocks"])
    assert textnorm.symletters("20 μg 5°C") == "20 μg 5°C"
