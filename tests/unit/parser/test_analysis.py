"""
Unit tests for the structural-extraction half of the parser
(src/parser/analysis.py + build_equation_spec_from_ast), driven by
hand-built ast_nodes trees rather than lark's output. These pass with
no dependency on the 'lark' package being installed, so they double as
a fast smoke test of the semantic layer independent of grammar/lexer
correctness (see test_text_parser.py for the end-to-end raw_text ->
EquationSpec tests, which do require lark).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.parser.ast_nodes import BinOp, Deriv, FuncCall, Num, Var
from src.parser.text_parser import build_equation_spec_from_ast
from src.parser.validator import validate_equation_spec


def _mass_spring_damper():
    lhs = BinOp(
        "+",
        BinOp("+", BinOp("*", Var("m"), Deriv("x", 2, None)), BinOp("*", Var("c"), Deriv("x", 1, None))),
        BinOp("*", Var("k"), Var("x")),
    )
    rhs = Num(0.0)
    return build_equation_spec_from_ast(lhs, rhs, "m*x'' + c*x' + k*x = 0")


def test_second_order_linear_ode_structure():
    spec = _mass_spring_damper()
    assert spec.domain_type == "ODE"
    assert spec.dependent_var == "x"
    assert spec.independent_vars == ["t"]
    assert spec.order == 2
    orders = sorted(t.derivative_order for t in spec.terms)
    assert orders == [0, 1, 2]
    by_order = {t.derivative_order: t for t in spec.terms}
    assert by_order[2].coefficient == "m"
    assert by_order[1].coefficient == "c"
    assert by_order[0].coefficient == "k"
    assert spec.rhs_forcing.type == "zero"
    assert validate_equation_spec(spec).valid


def test_first_order_linear_ode_with_division_coefficient():
    lhs = BinOp("+", Deriv("x", 1, "t"), BinOp("/", Var("x"), Var("RC")))
    rhs = Num(0.0)
    spec = build_equation_spec_from_ast(lhs, rhs, "dx/dt + x/RC = 0")

    assert spec.domain_type == "ODE"
    assert spec.order == 1
    by_order = {t.derivative_order: t for t in spec.terms}
    assert by_order[1].coefficient == 1.0
    assert by_order[0].coefficient == "1/RC"
    assert validate_equation_spec(spec).valid


def test_sin_forcing_term():
    lhs = BinOp("+", BinOp("+", Deriv("x", 2, None), BinOp("*", Num(2), Deriv("x", 1, None))), BinOp("*", Num(5), Var("x")))
    rhs = FuncCall("sin", [Var("t")])
    spec = build_equation_spec_from_ast(lhs, rhs, "x'' + 2*x' + 5*x = sin(t)")

    assert spec.rhs_forcing.type == "sin"
    assert spec.rhs_forcing.params["amplitude"] == 1.0
    assert spec.rhs_forcing.params["angular_frequency"] == 1.0
    assert spec.rhs_forcing.params["phase"] == 0.0
    assert validate_equation_spec(spec).valid


def test_sin_forcing_with_amplitude_frequency_and_phase():
    lhs = BinOp("+", Deriv("x", 2, None), Var("x"))
    rhs = BinOp("*", Num(3), FuncCall("sin", [BinOp("+", BinOp("*", Num(2), Var("t")), Num(1))]))
    spec = build_equation_spec_from_ast(lhs, rhs, "x'' + x = 3*sin(2*t + 1)")

    assert spec.rhs_forcing.type == "sin"
    assert spec.rhs_forcing.params == {"amplitude": 3.0, "angular_frequency": 2.0, "phase": 1.0}
    assert validate_equation_spec(spec).valid


def test_zero_rhs_is_classified_as_zero_not_const():
    spec = _mass_spring_damper()
    assert spec.rhs_forcing.type == "zero"
    assert spec.rhs_forcing.params == {}
    assert spec.rhs_forcing.expr is None


def test_const_forcing():
    lhs = BinOp("+", Deriv("x", 1, "t"), Var("x"))
    rhs = Num(9.8)
    spec = build_equation_spec_from_ast(lhs, rhs, "dx/dt + x = 9.8")
    assert spec.rhs_forcing.type == "const"
    assert spec.rhs_forcing.params == {"value": 9.8}
    assert validate_equation_spec(spec).valid


def test_pde_domain_and_independent_vars_from_two_leibniz_forms():
    lhs = BinOp("-", Deriv("u", 2, "t"), BinOp("*", BinOp("^", Var("c"), Num(2)), Deriv("u", 2, "x")))
    rhs = Num(0.0)
    spec = build_equation_spec_from_ast(lhs, rhs, "d2u/dt2 - c^2*d2u/dx2 = 0")

    assert spec.domain_type == "PDE"
    assert spec.independent_vars == ["t", "x"]
    assert spec.order == 2
    assert validate_equation_spec(spec).valid


def test_terms_with_dependent_var_on_both_sides_are_combined():
    # x' = -x  ->  standard form x' + x = 0
    lhs = Deriv("x", 1, "t")
    rhs = BinOp("*", Num(-1), Var("x"))
    spec = build_equation_spec_from_ast(lhs, rhs, "dx/dt = -1*x")

    orders = sorted(t.derivative_order for t in spec.terms)
    assert orders == [0, 1]
    by_order = {t.derivative_order: t for t in spec.terms}
    assert by_order[1].coefficient == 1.0
    assert by_order[0].coefficient == 1.0
    assert spec.rhs_forcing.type == "zero"
