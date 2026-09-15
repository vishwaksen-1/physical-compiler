import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.parser.validator import structurally_equivalent_ignoring_source, validate_equation_spec


def _valid_web_builder_spec():
    return {
        "spec_version": "1.0",
        "domain_type": "ODE",
        "independent_vars": ["t"],
        "dependent_var": "x",
        "order": 2,
        "terms": [
            {"derivative_order": 2, "wrt": "t", "coefficient": "m"},
            {"derivative_order": 1, "wrt": "t", "coefficient": "c"},
            {"derivative_order": 0, "wrt": "t", "coefficient": "k"},
        ],
        "rhs_forcing": {"type": "zero", "params": {}, "expr": None},
        "initial_conditions": None,
        "boundary_conditions": None,
        "input_source": "web_builder",
        "raw_text": None,
    }


def test_valid_web_builder_spec_passes():
    result = validate_equation_spec(_valid_web_builder_spec())
    assert result.valid, result.errors


def test_missing_key_fails():
    spec = _valid_web_builder_spec()
    del spec["rhs_forcing"]
    result = validate_equation_spec(spec)
    assert not result.valid
    assert any("rhs_forcing" in e for e in result.errors)


def test_bad_domain_type_fails():
    spec = _valid_web_builder_spec()
    spec["domain_type"] = "SDE"
    result = validate_equation_spec(spec)
    assert not result.valid
    assert any("domain_type" in e for e in result.errors)


def test_term_order_exceeding_spec_order_fails():
    spec = _valid_web_builder_spec()
    spec["terms"][0]["derivative_order"] = 5
    result = validate_equation_spec(spec)
    assert not result.valid
    assert any("derivative_order" in e for e in result.errors)


def test_order_with_no_matching_term_fails():
    spec = _valid_web_builder_spec()
    spec["order"] = 3
    result = validate_equation_spec(spec)
    assert not result.valid


def test_term_wrt_not_in_independent_vars_fails():
    spec = _valid_web_builder_spec()
    spec["terms"][0]["wrt"] = "z"
    result = validate_equation_spec(spec)
    assert not result.valid
    assert any("wrt" in e for e in result.errors)


def test_bad_forcing_type_fails():
    spec = _valid_web_builder_spec()
    spec["rhs_forcing"]["type"] = "sawtooth"
    result = validate_equation_spec(spec)
    assert not result.valid


def test_custom_expr_requires_expr_field():
    spec = _valid_web_builder_spec()
    spec["rhs_forcing"] = {"type": "custom_expr", "params": {}, "expr": None}
    result = validate_equation_spec(spec)
    assert not result.valid
    assert any("custom_expr" in e for e in result.errors)


def test_text_parser_source_requires_raw_text():
    spec = _valid_web_builder_spec()
    spec["input_source"] = "text_parser"
    spec["raw_text"] = None
    result = validate_equation_spec(spec)
    assert not result.valid


def test_coefficient_must_be_float_or_str_not_bool():
    spec = _valid_web_builder_spec()
    spec["terms"][0]["coefficient"] = True
    result = validate_equation_spec(spec)
    assert not result.valid


def test_structurally_equivalent_ignoring_source():
    a = _valid_web_builder_spec()
    b = _valid_web_builder_spec()
    b["input_source"] = "text_parser"
    b["raw_text"] = "m*x'' + c*x' + k*x = 0"
    assert structurally_equivalent_ignoring_source(a, b)

    b["terms"][0]["coefficient"] = "M"  # genuine structural difference
    assert not structurally_equivalent_ignoring_source(a, b)


def test_equation_spec_roundtrip_via_from_dict():
    from src.parser.equation_spec import EquationSpec

    d = _valid_web_builder_spec()
    spec = EquationSpec.from_dict(d)
    assert spec.to_dict() == d
    result = validate_equation_spec(spec)
    assert result.valid
