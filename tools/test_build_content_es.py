"""Spanish validator tests: the real library passes, and each Spanish rule catches its violation."""
import copy
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bces", os.path.join(HERE, "build_content_es.py"))
ES = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ES)
BC = ES._load_bc()
HOOKS = ES.load_hooks()
EV = BC.load_evidence_ids()


def _scripts():
    return ES.load_scripts(HOOKS)


def _problems(mutate):
    ss = _scripts()
    mutate(ss)
    return ES.validate(ss, HOOKS, EV, BC)


def test_library_passes():
    assert ES.validate(_scripts(), HOOKS, EV, BC) == []


def _set_beat(i, k, text):
    def m(ss):
        b = list(ss[i]["beats"][k]); b[2] = text; ss[i]["beats"][k] = tuple(b)
    return m


def test_diabetes_claim_blocked():
    p = _problems(_set_beat(13, 2, "Caminar después de comer baja el azúcar y controla la diabetes, dicen los estudios."))
    assert any("BC27" in x for x in p), p


def test_remedy_for_condition_blocked_even_in_myth():
    p = _problems(_set_beat(2, 0, "¿Agua de cebolla para la presión? No, mija. La cebolla va en el caldo."))
    assert any("BC30" in x for x in p), p


def test_medication_and_cure_blocked():
    p = _problems(_set_beat(5, 2, "Con esto ya no vas a necesitar pastillas. Esto cura."))
    assert any("BC31" in x for x in p) and any("BC26" in x for x in p), p


def test_de_por_vida_and_garantia_rules():
    def m(ss):
        ss[27]["caption"] = ss[27]["caption"].replace("bloqueado mientras sigas suscrito", "bloqueado de por vida")
        ss[27]["caption"] += " Garantía de resultados."
    p = _problems(m)
    assert any("de por vida" in x for x in p) and any("bloqueado mientras sigas suscrito" in x for x in p)
    assert any("garantía" in x.lower() for x in p), p


def test_runway_price_and_membership_blocked():
    def m(ss):
        ss[0]["caption"] += " Membresía $25 al mes."
    p = _problems(m)
    assert any("runway script states a price" in x for x in p) and any("mentions" in x for x in p), p


def test_condition_hashtag_and_prominent_terms():
    def m(ss):
        ss[1]["ig"] = ss[1]["ig"] + ["#diabetesmexicana"]
        ss[1]["thumb"] = "ADIÓS ARTRITIS"
    p = _problems(m)
    assert any("condition hashtag" in x for x in p) and any("prominent" in x for x in p), p


def test_offer_needs_ai_line_and_urgency_blocked():
    def m(ss):
        ss[25]["beats"][1] = ("3-11", "CHUY", "Quedan pocos lugares, apúrese: siete mañanas, ocho minutos, una silla.", "Siete mañanas", "same")
    p = _problems(m)
    assert any("AI line" in x for x in p) and any("urgency" in x for x in p), p


def test_falls_blocked():
    p = _problems(_set_beat(7, 3, "Esta prueba ayuda a evitar caídas en casa."))
    assert any("BC29" in x or "fall wording" in x for x in p), p


def test_grammar_tag_must_match():
    def m(ss):
        ss[1]["grammar"] = ["WATCH"]
    p = _problems(m)
    assert any("grammar tag WATCH" in x for x in p), p
