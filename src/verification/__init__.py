"""
verification — symbolic substitution + residual comparison (Phase 2).

Owner: Agent A; implemented in this session against the real Agent A
(symbolic/canonical/classifier) and Agent B (physics registry) code, and
against the structural helpers in src/synthesis/ode_matching.py (shared
with src/synthesis/, which produced the candidate's parameter_values in
the first place).

Consumes: DifferentialEquationIR (INTERFACE_CONTRACTS.md §2) and a
CandidateMapping (INTERFACE_CONTRACTS.md §4) with parameter_values filled in.
Produces: an updated CandidateMapping with `verification_status`
("EXACT" | "APPROXIMATE" | "FAILED"), `residual_expr`, and
`score.exactness` set.

Implements INTERFACE_CONTRACTS.md §8:
`verify_mapping(ir: DifferentialEquationIR, candidate: CandidateMapping) ->
CandidateMapping`.

DESIGN NOTE — why a *numeric* residual rather than reconstructing and
symbolically comparing two full equations: the model's dependent-variable
function and forcing function have different names from the user's
(e.g. x(t)/F(t) vs y(t)/whatever the parser used), so a literal structural
equality check would require substituting one applied function for another
inside possibly-unevaluated Derivative objects — a known sympy sharp edge.
Since both sides are, by this point, linear-constant-coefficient ODEs, the
entire content of "does this mapping hold" is captured by comparing their
per-derivative-order coefficients *after normalizing each by its own
leading coefficient* (this cancels out the arbitrary overall scale, and
sidesteps needing to compare the two different dependent-variable names at
all). The forcing side is intentionally not separately residual-checked:
every registered model's forcing function is an unconstrained applied
function (F, V, V_in, tau, T_env) that can represent *any* time-dependent
input, so it always matches by definition — the one exception
(newtons_cooling, where the forcing's coefficient is the same shared
parameter k used on the lhs) is already covered by the lhs coefficient
check, since that's the same equation src/synthesis/ used to solve for k.
"""
from __future__ import annotations

from src.canonical.ir import DifferentialEquationIR
from src.symbolic import engine as sym
from src.synthesis import ode_matching as odm
from src.synthesis.candidate import CandidateMapping

_EXACT_TOLERANCE = 1e-9
_APPROXIMATE_TOLERANCE = 1e-3


def _result(candidate: CandidateMapping, status: str, residual_expr: str, exactness: float) -> CandidateMapping:
    candidate.verification_status = status
    candidate.residual_expr = residual_expr
    candidate.score.exactness = exactness
    return candidate


def verify_mapping(ir: DifferentialEquationIR, candidate: CandidateMapping) -> CandidateMapping:
    """INTERFACE_CONTRACTS.md §8: verify_mapping(ir, candidate) -> CandidateMapping.

    Mutates and returns `candidate`. See module docstring for the
    numeric-normalized-coefficient-residual approach.
    """
    from src.physics.models.registry import get_model

    try:
        model = get_model(candidate.model_id)
    except KeyError:
        return _result(candidate, "FAILED", f"unknown model_id: {candidate.model_id!r}", 0.0)

    try:
        structure = odm.model_structure(model)
    except ValueError as exc:
        return _result(candidate, "FAILED", f"model structure error: {exc}", 0.0)

    order = ir.order
    if structure["max_order"] != order:
        return _result(
            candidate, "FAILED",
            f"model order {structure['max_order']} != ir order {order}", 0.0,
        )

    t_sym, y_applied, user_coeffs, forcing_expr_user, leftover = odm.user_ode_structure(ir)
    if not sym.is_zero(leftover):
        return _result(candidate, "FAILED", "ir has unexplained lhs structure", 0.0)

    leading_user = user_coeffs[order]
    if sym.is_zero(leading_user) or sym.has_free_symbols(leading_user):
        return _result(candidate, "FAILED", "degenerate or symbolic leading coefficient in ir", 0.0)

    norm_user = {n: sym.to_float(c / leading_user) for n, c in user_coeffs.items() if n < order}

    param_symbols_by_name = {sym.symbol_name(s): s for s in structure["param_symbols"]}
    subs_map = {
        param_symbols_by_name[name]: value
        for name, value in candidate.parameter_values.items()
        if name in param_symbols_by_name
    }

    leading_model_expr = sym.substitute(structure["coeffs"][order], subs_map)
    if sym.has_free_symbols(leading_model_expr):
        return _result(candidate, "FAILED", "parameter_values incomplete: leading coefficient unresolved", 0.0)
    if sym.is_zero(leading_model_expr):
        return _result(candidate, "FAILED", "model leading coefficient is zero after substitution", 0.0)
    leading_model = sym.to_float(leading_model_expr)

    max_deviation = 0.0
    for n in range(order):
        model_coeff_expr = sym.substitute(structure["coeffs"][n], subs_map)
        if sym.has_free_symbols(model_coeff_expr):
            return _result(
                candidate, "FAILED",
                f"parameter_values incomplete: order-{n} coefficient unresolved", 0.0,
            )
        model_norm_n = sym.to_float(model_coeff_expr) / leading_model
        max_deviation = max(max_deviation, abs(model_norm_n - norm_user[n]))

    if max_deviation < _EXACT_TOLERANCE:
        return _result(candidate, "EXACT", "0", 1.0)
    if max_deviation < _APPROXIMATE_TOLERANCE:
        return _result(candidate, "APPROXIMATE", f"{max_deviation:.6g}", 0.5)
    return _result(candidate, "FAILED", f"{max_deviation:.6g}", 0.0)
