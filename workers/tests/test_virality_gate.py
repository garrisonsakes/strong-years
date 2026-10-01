"""VIRALITY_SYSTEM.md §3: render-time rules R1–R6 (pure checks, no ffmpeg)."""
import pytest

from assemble import virality_gate as VG


def _m(**over):
    m = {"voice_track": "v.wav",
         "words": [{"word": w, "start_s": i * 0.4, "end_s": i * 0.4 + 0.35} for i, w in enumerate("Sit down stand up no hands".split())],
         "timeline": [{"n": 1, "start_s": 0, "duration_s": 1.8}, {"n": 2, "start_s": 1.8, "duration_s": 1.0}],
         "on_screen": [{"text": "CAN YOU DO 5?", "start_s": 0, "end_s": 2.0, "style": "hook"}],
         "captions": {"safe_top_pct": 12, "safe_bottom_pct": 22}}
    m.update(over)
    return m


def test_good_manifest_passes():
    r = VG.check(_m(), total=2.8)
    assert r["pass"], r["errors"]
    assert r["frame1_hook"] == "CAN YOU DO 5?"


@pytest.mark.parametrize("over,rule", [
    ({"on_screen": []}, "R1"),
    ({"on_screen": [{"text": "CAN YOU", "start_s": 0.5, "end_s": 2, "style": "hook"}]}, "R1"),
    ({"on_screen": [{"text": "one two three four five six seven eight", "start_s": 0, "end_s": 2, "style": "hook"}]}, "R1"),
    ({"words": []}, "R2"),
    ({"timeline": [{"n": 1, "start_s": 0, "duration_s": 9}]}, "R3"),
    ({"output": {"width": 1080, "height": 1080}}, "R5"),
    ({"captions": {"safe_bottom_pct": 10}}, "R5"),
    ({"cover_text": "this cover text is far too long to read"}, "R6"),
])
def test_each_rule_fails(over, rule):
    r = VG.check(_m(**over), total=2.8)
    assert not r["pass"] and any(e.startswith(rule) for e in r["errors"]), r["errors"]


def test_signoff_breaks_loop_and_dead_air_warns():
    ws = [{"word": w, "start_s": i * 0.4, "end_s": i * 0.4 + 0.3} for i, w in enumerate("do it again. See you tomorrow".split())]
    r = VG.check(_m(words=ws), total=2.4)
    assert any(e.startswith("R4") for e in r["errors"])
    r = VG.check(_m(), total=6.0)
    assert r["pass"] and any(w.startswith("R4") for w in r["warnings"])


def test_pattern_interrupt_from_explicit_cue():
    r = VG.check(_m(timeline=[{"n": 1, "start_s": 0, "duration_s": 9}], pattern_interrupts_s=[2.2]), total=9)
    assert r["pass"], r["errors"]


def test_assembler_refuses_and_warn_mode(monkeypatch):
    from assemble import assembler
    with pytest.raises(assembler.AssemblyError, match="virality gate"):
        assembler.assemble({"timeline": [{"n": 1, "start_s": 0, "duration_s": 3, "src": "x.mp4"}], "on_screen": []})


def test_variant_cover_rule():
    assert VG.cover_text_ok(None) and VG.cover_text_ok("ONE TWO THREE FOUR FIVE SIX SEVEN")
    assert VG.cover_text_ok("YOUR NUMBER?") == []
