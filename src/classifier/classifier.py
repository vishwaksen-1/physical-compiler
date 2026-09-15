"""
src/classifier/classifier.py

order / linearity / ODE-vs-PDE / homogeneity / classification_tags
(PROJECT_PLAN.md §2's "Agent A — classifier" track). Never imports sympy
directly — reaches all symbolic operations through src/symbolic/engine.py.

See src/canonical/ir.py's module docstring for the canonicalize() / classify()
field-population split.
"""
from __future__ import annotations

from src.canonical.ir import DifferentialEquationIR
from src.symbolic import engine as sym

_ORDER_WORDS = {0: "zeroth_order", 1: "first_order", 2: "second_order", 3: "third_order"}


def classify_domain(independent_vars: list[str]) -> str:
    return "ODE" if len(independent_vars) <= 1 else "PDE"


def classify_linearity(canonical_equation_expr, dependent_var_applied) -> str:
    """
    Linearity is a whole-equation property, not a per-coefficient one:
    checking coefficients in isolation misses cross-terms like
    x(t)*Derivative(x(t), t) (e.g. a nonlinear drag term), which is
    nonlinear as a system even though x(t) and Derivative(x(t), t) are each
    individually linear on their own. So this treats the dependent
    variable's whole "y-family" (y and all its derivatives appearing in the
    canonical LHS-RHS expression) as a set of independent variables and
    checks the total polynomial degree across all of them: <=1 is linear,
    >=2 (including any non-polynomial dependence, e.g. sin(y)) is nonlinear.
    """
    y = dependent_var_applied
    atoms = sym.dependent_var_atoms(canonical_equation_expr, y)
    degree = sym.total_degree_in(canonical_equation_expr, atoms)
    return "linear" if degree <= 1 else "nonlinear"


def classify_homogeneity(forcing_expr) -> str:
    return "homogeneous" if sym.is_zero(forcing_expr) else "nonhomogeneous"


def classify_constant_coefficients(coefficients: dict[str, str], parse_table) -> bool:
    for raw_coeff in coefficients.values():
        try:
            expr = sym.safe_sympify(str(raw_coeff), parse_table)
        except ValueError:
            return False
        if sym.free_symbols(expr):
            return False
    return True


def classify(ir: DifferentialEquationIR) -> list[str]:
    """
    INTERFACE_CONTRACTS.md §8: classify(ir: DifferentialEquationIR) -> list[str].

    Mutates ir.linearity, ir.homogeneity, and ir.classification_tags in
    place (see src/canonical/ir.py's docstring for why), and returns
    classification_tags, matching the declared return type.
    """
    symbol_table = sym.build_symbol_table(ir.independent_vars, ir.dependent_var)
    parse_table = sym.build_parsing_symbol_table(ir.independent_vars, ir.dependent_var)
    y = symbol_table[ir.dependent_var]

    # ir.canonical_form / ir.forcing_term are canonical_srepr() strings
    # (fully-qualified Symbol(...)/Function(...)(...)/Add(...)/... calls), so
    # they round-trip through sympify without needing either symbol table —
    # an empty table is passed since safe_sympify already exposes sympy's
    # own top-level names.
    canonical_equation_expr = sym.safe_sympify(ir.canonical_form, {}) if ir.canonical_form else sym.zero()
    forcing_expr = sym.safe_sympify(ir.forcing_term, {}) if ir.forcing_term else sym.zero()

    derived_domain = classify_domain(ir.independent_vars)
    linearity = classify_linearity(canonical_equation_expr, y)
    homogeneity = classify_homogeneity(forcing_expr)
    constant_coeffs = classify_constant_coefficients(ir.coefficients, parse_table)

    tags = [ir.domain_type, linearity, homogeneity]
    tags.append(_ORDER_WORDS.get(ir.order, f"order_{ir.order}"))
    if constant_coeffs:
        tags.append("constant_coefficient")
    if derived_domain != ir.domain_type:
        # Structural check (independent_vars count) disagrees with the
        # declared domain_type carried over from the EquationSpec. This
        # shouldn't happen past a valid Agent-C-validated spec, but we flag
        # rather than silently overwrite what canonicalize() copied in.
        tags.append("domain_type_mismatch")

    ir.linearity = linearity
    ir.homogeneity = homogeneity
    ir.classification_tags = tags
    return tags
