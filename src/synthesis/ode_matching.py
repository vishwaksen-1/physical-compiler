"""
src/synthesis/ode_matching.py

Shared linear constant-coefficient ODE structural-extraction helpers, used
by both src/synthesis/__init__.py (generate_candidates) and
src/verification/__init__.py (verify_mapping) — factored out here rather
than duplicated, since both need to recompute the same normalized
per-derivative-order coefficients from a DifferentialEquationIR and a
PhysicalModel. See src/synthesis/__init__.py's module docstring for the
overall Phase 2 scope and design rationale.

Never imports sympy directly (PROJECT_PLAN.md §1.1) — everything symbolic
goes through src/symbolic/engine.py.
"""
from __future__ import annotations

import math

from src.canonical.ir import DifferentialEquationIR
from src.physics.models.registry import PhysicalModel
from src.symbolic import engine as sym

ORDER_WORD = {1: "first_order", 2: "second_order", 3: "third_order"}


def required_class_tag(ir: DifferentialEquationIR):
    """The equation_class_tags entry a model must carry to be considered a
    candidate realization of `ir`, or None if `ir` is outside the linear
    constant-coefficient ODE family this matcher supports."""
    if ir.domain_type != "ODE":
        return None
    if len(ir.independent_vars) != 1:
        return None
    if ir.linearity != "linear":
        return None
    if "constant_coefficient" not in ir.classification_tags:
        return None
    word = ORDER_WORD.get(ir.order)
    if word is None:
        return None
    return f"{word}_linear_constant_coefficient_ode"


def extract_ode_coeffs(expr, y_applied, t_sym, max_order: int):
    """Per-derivative-order coefficients of `expr`, treated as a linear
    combination of y_applied and its derivatives up to max_order. Returns
    (coeffs: dict[int, Expr], leftover: Expr) — leftover should be exactly
    zero for a clean single-function linear ODE."""
    coeffs = {}
    reconstruction = sym.zero()
    for n in range(max_order, -1, -1):
        atom = sym.derivative_of(y_applied, t_sym, n)
        c = sym.coefficient_of(expr, atom)
        coeffs[n] = c
        reconstruction = reconstruction + c * atom
    leftover = expr - reconstruction
    return coeffs, leftover


def user_ode_structure(ir: DifferentialEquationIR):
    """(t_sym, y_applied, coeffs, forcing_expr, leftover) reconstructed from
    ir.canonical_form / ir.forcing_term."""
    t_sym = sym.make_independent_symbols(ir.independent_vars)[ir.independent_vars[0]]
    y_applied = sym.function_of(ir.dependent_var, t_sym)
    canon_expr = sym.parse_srepr(ir.canonical_form) if ir.canonical_form else sym.zero()
    forcing_expr = sym.parse_srepr(ir.forcing_term) if ir.forcing_term else sym.zero()
    # ir.canonical_form == canonical_srepr(expand(lhs - rhs)), so lhs == canonical_form + rhs.
    lhs_expr = canon_expr + forcing_expr
    coeffs, leftover = extract_ode_coeffs(lhs_expr, y_applied, t_sym, ir.order)
    return t_sym, y_applied, coeffs, forcing_expr, leftover


def model_structure(model: PhysicalModel):
    """(t_sym, y_applied, forcing_applied, param_symbols, coeffs,
    forcing_coeff, max_order) extracted structurally from
    model.governing_equation. Raises ValueError if the model isn't the
    clean single-state-variable linear-ODE shape this module supports —
    every currently-registered model is."""
    lhs, rhs = sym.split_eq(model.governing_equation)

    derivs = sym.all_derivatives(lhs)
    if not derivs:
        raise ValueError(f"{model.model_id}: governing_equation has no derivatives on lhs")
    max_order = max(sym.derivative_order_of(d) for d in derivs)
    y_bases = {sym.derivative_base_of(d) for d in derivs}
    if len(y_bases) != 1:
        raise ValueError(f"{model.model_id}: expected exactly one differentiated function, got {y_bases!r}")
    y_applied = next(iter(y_bases))

    lhs_funcs = sym.applied_undefined_functions(lhs)
    if lhs_funcs != {y_applied}:
        raise ValueError(
            f"{model.model_id}: lhs has unexpected function atoms {lhs_funcs!r}, expected only {y_applied!r}"
        )

    forcing_funcs = sym.applied_undefined_functions(rhs)
    if len(forcing_funcs) != 1:
        raise ValueError(f"{model.model_id}: expected exactly one forcing function on rhs, got {forcing_funcs!r}")
    forcing_applied = next(iter(forcing_funcs))

    t_sym = sym.applied_arg0(y_applied)

    coeffs, leftover = extract_ode_coeffs(lhs, y_applied, t_sym, max_order)
    if not sym.is_zero(leftover):
        raise ValueError(f"{model.model_id}: lhs has unexplained structure: {leftover!r}")

    forcing_coeff = sym.coefficient_of(rhs, forcing_applied)

    t_and_forcing = sym.free_symbols(forcing_applied) | {t_sym}
    param_symbols = sorted(
        (sym.free_symbols(lhs) | sym.free_symbols(rhs)) - t_and_forcing,
        key=sym.symbol_name,
    )

    return {
        "t_sym": t_sym,
        "y_applied": y_applied,
        "forcing_applied": forcing_applied,
        "param_symbols": param_symbols,
        "coeffs": coeffs,
        "forcing_coeff": forcing_coeff,
        "max_order": max_order,
    }


def anchor_value(model: PhysicalModel, param_name: str):
    """A deterministic default numeric value for a free parameter that a
    coefficient-matching system alone can't pin down, drawn from the
    model's own `parameter_constraints`. Returns (value, human-readable
    justification string)."""
    constraint = model.parameter_constraints.get(param_name, {})
    lo, hi = constraint.get("min"), constraint.get("max")
    unit = constraint.get("unit", "")

    if lo is not None and hi is not None:
        if lo > 0 and hi > 0:
            value = math.sqrt(lo * hi)
            reason = f"geometric mean of parameter_constraints range [{lo}, {hi}]{unit}"
        else:
            value = (lo + hi) / 2.0
            reason = f"midpoint of parameter_constraints range [{lo}, {hi}]{unit}"
    elif lo is not None:
        value = lo * 2.0
        reason = f"2x the declared minimum {lo}{unit} (no maximum declared)"
    elif hi is not None:
        value = hi / 2.0
        reason = f"half the declared maximum {hi}{unit} (no minimum declared)"
    else:
        value = 1.0
        reason = "no parameter_constraints declared -- arbitrary unit default"

    return value, reason
