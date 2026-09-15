"""Sanity tests for Agent B's physical model registry.

Run with: pytest tests/unit/physics/test_registry.py -v
"""

import sympy as sp
import pytest

from src.physics.models import get_registry, get_model, registry_summary
from src.physics.constraints import run_all_checks

EXPECTED_MODEL_IDS = {
    "mass_spring_damper",
    "series_rlc",
    "torsional_pendulum",
    "rc_circuit",
    "newtons_cooling",
}


def test_all_five_models_registered():
    ids = {m.model_id for m in get_registry()}
    assert ids == EXPECTED_MODEL_IDS


def test_insertion_order_is_stable_and_matches_import_order():
    ids = [m.model_id for m in get_registry()]
    assert ids == [
        "mass_spring_damper",
        "series_rlc",
        "torsional_pendulum",
        "rc_circuit",
        "newtons_cooling",
    ]


def test_governing_equations_are_real_sympy_equations():
    for model in get_registry():
        assert isinstance(model.governing_equation, sp.Eq)
        # every equation must be a genuine equality, not trivially 0 = 0
        assert (model.governing_equation.lhs - model.governing_equation.rhs) != 0


def test_second_order_alt_realizations_share_class_and_tag():
    second_order_ids = ["mass_spring_damper", "series_rlc", "torsional_pendulum"]
    models = {mid: get_model(mid) for mid in second_order_ids}
    class_ids = {m.alt_realizations_of for m in models.values()}
    assert class_ids == {"second_order_linear_constant_coefficient_ode"}
    for m in models.values():
        assert "second_order_linear_constant_coefficient_ode" in m.equation_class_tags


def test_first_order_alt_realizations_share_class_and_tag():
    first_order_ids = ["rc_circuit", "newtons_cooling"]
    models = {mid: get_model(mid) for mid in first_order_ids}
    class_ids = {m.alt_realizations_of for m in models.values()}
    assert class_ids == {"first_order_linear_constant_coefficient_ode"}
    for m in models.values():
        assert "first_order_linear_constant_coefficient_ode" in m.equation_class_tags


def test_to_dict_from_dict_roundtrip_preserves_equation_string_form():
    # NOTE: to_dict()/from_dict() use plain str(), not a canonical/sorted
    # printer (see registry.py docstring). sympify()-ing that string back
    # produces symbols WITHOUT the original assumptions (e.g. `positive=True`
    # on m, c, k), so the restored expression is only guaranteed to match
    # textually, not to be symbol-for-symbol substitutable with the
    # original. Full semantic round-tripping is Agent A's canonical
    # printer's job (src/symbolic/engine.py), not this convenience method's.
    model = get_model("mass_spring_damper")
    d = model.to_dict()
    assert isinstance(d["governing_equation"], str)
    from src.physics.models.registry import PhysicalModel

    restored = PhysicalModel.from_dict(d)
    assert str(restored.governing_equation) == str(model.governing_equation)


def test_registry_summary_shape():
    summary = registry_summary()
    assert len(summary) == 5
    for entry in summary:
        assert set(entry.keys()) == {"model_id", "display_name", "domain"}


@pytest.mark.parametrize(
    "model_id,values,expect_violation_substring",
    [
        ("mass_spring_damper", {"m": 0.5, "c": 1.0, "k": 50.0}, None),
        ("mass_spring_damper", {"m": 100.0, "c": 1.0, "k": 50.0}, "exceeds maximum"),
        ("series_rlc", {"L": 0.01, "R": 10.0, "C": 1e-6}, None),
        ("rc_circuit", {"R": 1000.0, "C": 1e-6}, None),
        ("rc_circuit", {"R": 1e9, "C": 1e-6}, "exceeds maximum"),
        ("newtons_cooling", {"k": 0.01}, None),
        ("torsional_pendulum", {"I": 0.001, "b": 0.001, "k_t": 0.1}, None),
    ],
)
def test_parameter_range_checks(model_id, values, expect_violation_substring):
    model = get_model(model_id)
    violations = run_all_checks(model, values)
    if expect_violation_substring is None:
        assert not any("exceeds maximum" in v or "below minimum" in v for v in violations)
    else:
        assert any(expect_violation_substring in v for v in violations)


def test_every_model_has_nonempty_safety_notes_and_construction_requirements():
    for model in get_registry():
        assert len(model.safety_notes) >= 1
        assert "components" in model.construction_requirements
        assert len(model.construction_requirements["components"]) >= 1
