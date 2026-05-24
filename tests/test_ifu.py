"""Smoke tests for meok-eu-ai-act-art-13-ifu-mcp."""
import sys, os, inspect, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import (
    generate_ifu,
    check_ifu_completeness,
    list_art_13_3_elements,
    list_art_14_oversight_measures,
    crosswalk_to_fria,
    generate_human_oversight_section,
    sign_ifu_chain,
)


def _build_basic_ifu():
    return generate_ifu(
        provider_legal_name="Acme AI Ltd",
        provider_contact="compliance@acme.example",
        system_name="Acme Hiring Recommender",
        system_version="1.0.0",
        intended_purpose="Score CV-to-role match for HR pre-screening",
        capabilities=["CV parsing", "role-match scoring"],
        limitations=["Performance degrades for niche roles <500 training samples"],
        accuracy_metrics={"precision": 0.86, "recall": 0.82, "f1": 0.84},
        human_oversight_design="Trained HR officer reviews every shortlist",
    )["ifu_document"]


def test_generate_ifu_basic():
    ifu = _build_basic_ifu()
    assert ifu["spec"] == "EU_AI_ACT_ART_13_3"
    assert "signature" in ifu


def test_generate_ifu_has_7_elements():
    ifu = _build_basic_ifu()
    assert len(ifu["art_13_3_elements"]) == 7


def test_check_completeness_passes_full_ifu():
    ifu = _build_basic_ifu()
    r = check_ifu_completeness(ifu)
    assert r["complete"] is True
    assert len(r["missing"]) == 0


def test_check_completeness_detects_missing():
    bad = {"art_13_3_elements": {"a_provider_identity": "x"}}  # only 1 element
    r = check_ifu_completeness(bad)
    assert r["complete"] is False
    assert len(r["missing"]) == 6


def test_list_art_13_3_elements():
    r = list_art_13_3_elements()
    assert r["count"] == 7


def test_list_art_14_oversight_measures():
    r = list_art_14_oversight_measures()
    assert r["count"] == 8
    assert "human_in_loop" in r["measures"]


def test_crosswalk_to_fria_returns_fields():
    ifu = _build_basic_ifu()
    r = crosswalk_to_fria(ifu)
    assert "g_provider_ifu_reference" in r["fria_input_fields"]
    assert "e_human_oversight" in r["fria_input_fields"]


def test_generate_human_oversight_loop():
    r = generate_human_oversight_section("human_in_loop", appeals_endpoint="appeals@acme.test")
    assert r["oversight_block"]["design_type"] == "human_in_loop"


def test_generate_human_oversight_unknown():
    r = generate_human_oversight_section("magic_oversight")
    assert "error" in r


def test_sign_ifu_chain():
    ifu = _build_basic_ifu()
    r = sign_ifu_chain(ifu)
    assert r["attestation_id"].startswith("IFU_")


if __name__ == "__main__":
    g = dict(globals())
    fns = [v for k, v in g.items() if k.startswith("test_") and inspect.isfunction(v)]
    p = f = 0
    for fn in fns:
        try:
            fn(); print(f"OK {fn.__name__}"); p += 1
        except Exception as e:
            print(f"X  {fn.__name__}: {type(e).__name__}: {e}"); traceback.print_exc(); f += 1
    print(f"\n{p} passed, {f} failed")
