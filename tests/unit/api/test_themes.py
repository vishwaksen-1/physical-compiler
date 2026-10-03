import pytest
from src.api import _themed_registry, compile_equation

def test_themed_registry_classical():
    ids = {m.model_id for m in _themed_registry(None)}
    assert ids == {"mass_spring_damper", "series_rlc", "torsional_pendulum", "rc_circuit", "newtons_cooling"}

def test_themed_registry_celestial():
    ids = {m.model_id for m in _themed_registry("celestial")}
    assert ids == {"mirror_ringdown", "expansion_analog"}

def test_themed_registry_quantum():
    ids = {m.model_id for m in _themed_registry("quantum")}
    assert ids == {"optical_trap_oscillator", "nmr_relaxation"}

def test_themed_registry_unknown_fallback():
    assert _themed_registry("not_a_real_theme") == []

def test_compile_equation_classical_still_works():
    res = compile_equation("y'' + 2y' + 5y = 0", None, {})
    assert res.selected_candidate.model_id == "mass_spring_damper"

def test_compile_equation_classical_rc_circuit():
    res = compile_equation("y' + 4y = 0", None, {})
    assert res.selected_candidate.model_id == "rc_circuit"

def test_compile_equation_classical_no_themed_alternatives():
    res = compile_equation("y'' + 2y' + 5y = 0", None, {})
    alt_ids = {a.model_id for a in res.alternative_candidates}
    assert "mirror_ringdown" not in alt_ids
    assert "optical_trap_oscillator" not in alt_ids

def test_compile_equation_celestial():
    res = compile_equation("y'' + 2y' + 5y = 0", None, {"theme": "celestial"})
    assert res.selected_candidate.model_id == "mirror_ringdown"
    alt_ids = {a.model_id for a in res.alternative_candidates}
    assert "mass_spring_damper" not in alt_ids

def test_compile_equation_celestial_growth():
    res = compile_equation("y' - 4y = 0", None, {"theme": "celestial"})
    assert res.selected_candidate.model_id == "expansion_analog"
    assert res.selected_candidate.verification_status == "EXACT"

def test_compile_equation_celestial_decay():
    res = compile_equation("y' + 4y = 0", None, {"theme": "celestial"})
    assert res.selected_candidate is None

def test_compile_equation_quantum():
    res = compile_equation("y'' + 2y' + 5y = 0", None, {"theme": "quantum"})
    assert res.selected_candidate.model_id == "optical_trap_oscillator"
    
def test_compile_equation_quantum_decay():
    res = compile_equation("y' + 4y = 0", None, {"theme": "quantum"})
    assert res.selected_candidate.model_id == "nmr_relaxation"
    assert res.selected_candidate.verification_status == "EXACT"

def test_seeded_random_is_reproducible_with_themes():
    config = {"candidate_selection_mode": "seeded_random", "candidate_seed": 42, "theme": "quantum"}
    res1 = compile_equation("y'' + 2y' + 5y = 0", None, config)
    res2 = compile_equation("y'' + 2y' + 5y = 0", None, config)
    assert res1.selected_candidate.model_id == res2.selected_candidate.model_id
    assert res1.selected_candidate.parameter_values == res2.selected_candidate.parameter_values
