"""
End-to-end tests of parse_equation(raw_text) through the real lark
grammar. These need the 'lark' package (pip install -r
requirements.txt); they're skipped automatically if it isn't
importable so `pytest` still passes cleanly on a minimal environment.
See test_analysis.py for lark-independent tests of the same semantics.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pytest

lark = pytest.importorskip("lark")

from src.parser.errors import EquationParseError
from src.parser.text_parser import parse_equation
from src.parser.validator import validate_equation_spec


def test_second_order_linear_ode_ascii_primes():
    spec = parse_equation("m*x'' + c*x' + k*x = 0")
    assert validate_equation_spec(spec).valid
    assert spec.domain_type == "ODE"
    assert spec.dependent_var == "x"
    assert spec.independent_vars == ["t"]
    assert spec.order == 2
    by_order = {t.derivative_order: t for t in spec.terms}
    assert by_order[2].coefficient == "m"
    assert by_order[1].coefficient == "c"
    assert by_order[0].coefficient == "k"
    assert spec.rhs_forcing.type == "zero"
    assert spec.input_source == "text_parser"
    assert spec.raw_text == "m*x'' + c*x' + k*x = 0"


def test_first_order_linear_ode_leibniz_notation():
    spec = parse_equation("dx/dt + x/RC = 0")
    assert validate_equation_spec(spec).valid
    assert spec.order == 1
    by_order = {t.derivative_order: t for t in spec.terms}
    assert by_order[1].coefficient == 1.0
    assert by_order[0].coefficient == "1/RC"


def test_sin_forcing_term():
    spec = parse_equation("x'' + 2*x' + 5*x = sin(t)")
    assert validate_equation_spec(spec).valid
    assert spec.rhs_forcing.type == "sin"
    assert spec.rhs_forcing.params["amplitude"] == 1.0
    assert spec.rhs_forcing.params["angular_frequency"] == 1.0


def test_leibniz_second_order_matches_prime_notation_structurally():
    # The validation rule in INTERFACE_CONTRACTS.md §1 is about
    # web-builder vs. text-parser parity, but the same equation written
    # two different ways through *this* parser should also agree on
    # everything except raw_text.
    from src.parser.validator import structurally_equivalent_ignoring_source

    spec_prime = parse_equation("x'' + 2*x' + 5*x = 0")
    spec_leibniz = parse_equation("d2x/dt2 + 2*dx/dt + 5*x = 0")
    assert structurally_equivalent_ignoring_source(spec_prime, spec_leibniz)


def test_unicode_overdot_notation():
    spec_unicode = parse_equation("ẍ + 2ẋ + 5x = sin(t)")
    spec_ascii = parse_equation("x'' + 2*x' + 5*x = sin(t)")
    from src.parser.validator import structurally_equivalent_ignoring_source

    assert validate_equation_spec(spec_unicode).valid
    assert structurally_equivalent_ignoring_source(spec_unicode, spec_ascii)


def test_unicode_partial_pde_notation():
    spec = parse_equation("∂²u/∂t² - c^2*∂²u/∂x² = 0")
    assert validate_equation_spec(spec).valid
    assert spec.domain_type == "PDE"
    assert spec.independent_vars == ["t", "x"]


def test_missing_derivative_raises_parse_error():
    with pytest.raises(EquationParseError):
        parse_equation("x + y = 0")


def test_empty_raw_text_raises_parse_error():
    with pytest.raises(EquationParseError):
        parse_equation("   ")


def test_syntax_error_raises_parse_error():
    with pytest.raises(EquationParseError):
        parse_equation("x'' + + = 0")
