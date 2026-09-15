"""
Turns a parsed (LHS, RHS) pair of expression trees into the
`terms` / `rhs_forcing` shape required by EquationSpec
(INTERFACE_CONTRACTS.md §1).

Deliberately does NOT use sympy (PROJECT_PLAN.md §1.1: only
src/symbolic/engine.py may import sympy). This is structural
extraction, not symbolic simplification — full linearity/equivalence
classification is Agent A's job downstream (src/classifier/). When an
equation is too irregular for this module to confidently decompose
(e.g. a genuinely nonlinear coupling like x*x''), it degrades to a
best-effort single term rather than raising, and the resulting
EquationSpec should still validate; deeper classification happens
later in the pipeline.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .ast_nodes import BinOp, Deriv, Expr, FuncCall, Neg, Num, Var
from .equation_spec import RhsForcing, Term


# ---------------------------------------------------------------------------
# Additive flattening
# ---------------------------------------------------------------------------


def flatten_additive(expr: Expr) -> List[Tuple[int, Expr]]:
    """Split an expression into (sign, sub_expr) pieces at top-level +/-.

    Only descends through Add/Sub/Neg — a "*", "/", function call, or
    bare atom is a leaf here even though it may contain sums internally
    (e.g. inside a function argument), because those inner sums belong
    to that sub-expression, not to this equation's term structure.
    """
    pieces: List[Tuple[int, Expr]] = []

    def walk(node: Expr, sign: int):
        if isinstance(node, BinOp) and node.op == "+":
            walk(node.left, sign)
            walk(node.right, sign)
        elif isinstance(node, BinOp) and node.op == "-":
            walk(node.left, sign)
            walk(node.right, -sign)
        elif isinstance(node, Neg):
            walk(node.operand, -sign)
        else:
            pieces.append((sign, node))

    walk(expr, 1)
    return pieces


def sum_signed(pieces: List[Tuple[int, Expr]]) -> Optional[Expr]:
    """Rebuild a single Expr from signed additive pieces (or None if empty)."""
    result: Optional[Expr] = None
    for sign, expr in pieces:
        piece = expr if sign > 0 else Neg(expr)
        result = piece if result is None else BinOp("+", result, piece)
    return result


# ---------------------------------------------------------------------------
# Dependent-variable detection
# ---------------------------------------------------------------------------


def contains_var(expr: Expr, name: str) -> bool:
    if isinstance(expr, Var):
        return expr.name == name
    if isinstance(expr, Deriv):
        return expr.var == name
    if isinstance(expr, Neg):
        return contains_var(expr.operand, name)
    if isinstance(expr, BinOp):
        return contains_var(expr.left, name) or contains_var(expr.right, name)
    if isinstance(expr, FuncCall):
        return any(contains_var(a, name) for a in expr.args)
    return False


def find_all_derivs(expr: Expr) -> List[Deriv]:
    found: List[Deriv] = []

    def walk(node: Expr):
        if isinstance(node, Deriv):
            found.append(node)
        elif isinstance(node, Neg):
            walk(node.operand)
        elif isinstance(node, BinOp):
            walk(node.left)
            walk(node.right)
        elif isinstance(node, FuncCall):
            for a in node.args:
                walk(a)

    walk(expr)
    return found


def find_all_vars(expr: Expr) -> List[str]:
    found: List[str] = []

    def walk(node: Expr):
        if isinstance(node, Var):
            found.append(node.name)
        elif isinstance(node, Deriv):
            found.append(node.wrt)
        elif isinstance(node, Neg):
            walk(node.operand)
        elif isinstance(node, BinOp):
            walk(node.left)
            walk(node.right)
        elif isinstance(node, FuncCall):
            for a in node.args:
                walk(a)

    walk(expr)
    return found


# ---------------------------------------------------------------------------
# Multiplicative flattening + term decomposition
# ---------------------------------------------------------------------------


@dataclass
class _Factor:
    expr: Expr
    inverted: bool  # True if this factor came from a "/" (divisor)


def flatten_mul(expr: Expr) -> List[_Factor]:
    """Split a product/quotient chain into its multiplicative factors."""
    factors: List[_Factor] = []

    def walk(node: Expr, inverted: bool):
        if isinstance(node, BinOp) and node.op == "*":
            walk(node.left, inverted)
            walk(node.right, inverted)
        elif isinstance(node, BinOp) and node.op == "/":
            walk(node.left, inverted)
            walk(node.right, not inverted)
        else:
            factors.append(_Factor(node, inverted))

    walk(expr, False)
    return factors


def _factor_to_str(f: _Factor) -> str:
    s = f.expr.to_str()
    return f"1/{s}" if f.inverted else s


def decompose_term(expr: Expr, dependent_var: str, sign: int = 1, default_wrt=None) -> Term:
    """Best-effort split of a dependent-var-containing additive piece into
    (derivative_order, wrt, coefficient), per INTERFACE_CONTRACTS.md §1.

    Handles the common linear-ODE/PDE case: exactly one multiplicative
    factor is the dependent variable (bare or differentiated), and every
    other factor is a coefficient. Anything else (nonlinear coupling,
    the dependent var appearing more than once in a product, etc.) still
    produces a Term, just with a less precise coefficient string — this
    module only captures structure, not full symbolic linearity, so it
    intentionally does not raise on those inputs.

    `default_wrt` (the equation's independent variable, or list of them
    for a PDE) is used whenever a specific `wrt` can't be read off the
    expression itself (a bare, undifferentiated dependent-var factor, or
    the nonlinear fallback path below) — the contract requires `wrt` to
    always be a str or list[str], never None.
    """
    factors = flatten_mul(expr)

    deriv_factor_idx = None
    order = 0
    wrt = default_wrt
    for i, f in enumerate(factors):
        if f.inverted:
            continue
        if isinstance(f.expr, Deriv) and f.expr.var == dependent_var:
            deriv_factor_idx = i
            order = f.expr.order
            wrt = f.expr.wrt if f.expr.wrt is not None else default_wrt
            break
        if isinstance(f.expr, Var) and f.expr.name == dependent_var:
            deriv_factor_idx = i
            order = 0
            wrt = default_wrt
            break

    if deriv_factor_idx is None:
        # Dependent var is present but not isolable as a clean factor
        # (e.g. nested inside a function, or multiplied with itself).
        # Fall back to order 0 / whole expression as coefficient with
        # the raw text captured — downstream classification will
        # re-derive the real structure from canonical_str(expr).
        return Term(derivative_order=0, wrt=default_wrt, coefficient=_apply_sign(canonical_str(expr), sign))

    coeff_factors = [f for i, f in enumerate(factors) if i != deriv_factor_idx]
    coefficient = _combine_coefficient(coeff_factors, sign)
    return Term(derivative_order=order, wrt=wrt, coefficient=coefficient)


def _combine_coefficient(factors: List[_Factor], sign: int):
    if not factors:
        return float(sign)

    all_numeric = all(isinstance(f.expr, Num) and not f.inverted for f in factors)
    if all_numeric:
        value = 1.0
        for f in factors:
            value *= f.expr.value
        return sign * value

    parts = [_factor_to_str(f) for f in factors]
    text = " * ".join(parts)
    return _apply_sign(text, sign)


def _apply_sign(text: str, sign: int) -> str:
    return text if sign > 0 else f"-({text})"


def canonical_str(expr: Optional[Expr]) -> str:
    if expr is None:
        return "0"
    return expr.to_str()


# ---------------------------------------------------------------------------
# Forcing classification
# ---------------------------------------------------------------------------

_TRIG_FUNCS = {"sin", "cos"}
_PULSE_FUNCS = {"step", "impulse"}


def classify_forcing(expr: Optional[Expr], independent_var: Optional[str]) -> RhsForcing:
    if expr is None or _is_zero(expr):
        return RhsForcing(type="zero", params={}, expr=None)

    if isinstance(expr, Num):
        return RhsForcing(type="const", params={"value": expr.value}, expr=None)
    if isinstance(expr, Neg) and isinstance(expr.operand, Num):
        return RhsForcing(type="const", params={"value": -expr.operand.value}, expr=None)

    sinusoid = _match_named_single_arg_func(expr, _TRIG_FUNCS, independent_var)
    if sinusoid is not None:
        kind, amplitude, arg_expr = sinusoid
        freq, phase = _linear_arg_params(arg_expr, independent_var)
        return RhsForcing(
            type=kind,
            params={"amplitude": amplitude, "angular_frequency": freq, "phase": phase},
            expr=None,
        )

    pulse = _match_named_single_arg_func(expr, _PULSE_FUNCS, independent_var)
    if pulse is not None:
        kind, amplitude, arg_expr = pulse
        key = "start_time" if kind == "step" else "time"
        return RhsForcing(
            type=kind,
            params={"amplitude": amplitude, key: canonical_str(arg_expr)},
            expr=None,
        )

    poly = _match_polynomial(expr, independent_var)
    if poly is not None:
        return RhsForcing(type="polynomial", params={"coefficients": poly}, expr=None)

    return RhsForcing(type="custom_expr", params={}, expr=canonical_str(expr))


def _is_zero(expr: Expr) -> bool:
    return isinstance(expr, Num) and expr.value == 0


def _match_named_single_arg_func(expr: Expr, names: set, independent_var: Optional[str]):
    """Match `amplitude * fname(arg)` (amplitude optional, default 1)."""
    factors = flatten_mul(expr)
    func_idx = None
    for i, f in enumerate(factors):
        if f.inverted:
            continue
        if isinstance(f.expr, FuncCall) and f.expr.name in names and len(f.expr.args) == 1:
            func_idx = i
            break
    if func_idx is None:
        return None

    coeff_factors = [f for i, f in enumerate(factors) if i != func_idx]
    if not coeff_factors:
        amplitude = 1.0
    elif all(isinstance(f.expr, Num) and not f.inverted for f in coeff_factors):
        amplitude = 1.0
        for f in coeff_factors:
            amplitude *= f.expr.value
    else:
        # Symbolic amplitude (e.g. "F0 * sin(t)") — not float-representable;
        # bail to custom_expr so we don't silently drop information.
        return None

    fname = factors[func_idx].expr.name
    arg = factors[func_idx].expr.args[0]
    return fname, amplitude, arg


def _linear_arg_params(arg_expr: Expr, independent_var: Optional[str]):
    """Best-effort split of a sin/cos argument into (angular_frequency, phase)
    for the "amplitude * sin(angular_frequency * t + phase)" convention.
    Falls back to (1.0, 0.0) tagged via raw text if it isn't linear-in-t.
    """
    pieces = flatten_additive(arg_expr)
    freq = 0.0
    phase = 0.0
    freq_found = False
    for sign, piece in pieces:
        factors = flatten_mul(piece)
        var_idx = None
        for i, f in enumerate(factors):
            if not f.inverted and isinstance(f.expr, Var) and f.expr.name == independent_var:
                var_idx = i
                break
        if var_idx is not None:
            coeff_factors = [f for i, f in enumerate(factors) if i != var_idx]
            if not coeff_factors:
                c = 1.0
            elif all(isinstance(f.expr, Num) and not f.inverted for f in coeff_factors):
                c = 1.0
                for f in coeff_factors:
                    c *= f.expr.value
            else:
                c = None
            if c is not None:
                freq += sign * c
                freq_found = True
                continue
        if isinstance(piece, Num):
            phase += sign * piece.value
        # anything else (nonlinear argument) is silently dropped from the
        # numeric phase/frequency estimate; custom_expr is used instead
        # when the whole forcing term doesn't fit this convention at all.
    if not freq_found and independent_var is not None and _is_bare_var(arg_expr, independent_var):
        freq = 1.0
    return freq, phase


def _is_bare_var(expr: Expr, name: str) -> bool:
    return isinstance(expr, Var) and expr.name == name


def _match_polynomial(expr: Expr, independent_var: Optional[str]):
    """Match a sum of `coeff * t^n` / `coeff` terms with no other symbols."""
    if independent_var is None:
        return None
    pieces = flatten_additive(expr)
    degree_coeffs = {}
    for sign, piece in pieces:
        deg, coeff = _monomial(piece, independent_var)
        if deg is None:
            return None
        degree_coeffs[deg] = degree_coeffs.get(deg, 0.0) + sign * coeff
    if not degree_coeffs:
        return None
    max_deg = max(degree_coeffs)
    return [degree_coeffs.get(d, 0.0) for d in range(max_deg + 1)]


def _monomial(expr: Expr, independent_var: str):
    """Return (degree, coefficient) if expr is coeff * t^n, else (None, None)."""
    if isinstance(expr, Num):
        return 0, expr.value
    factors = flatten_mul(expr)
    deg = 0
    coeff = 1.0
    var_seen = False
    for f in factors:
        if f.inverted:
            return None, None
        e = f.expr
        if isinstance(e, Num):
            coeff *= e.value
        elif isinstance(e, Var) and e.name == independent_var:
            deg += 1
            var_seen = True
        elif (
            isinstance(e, BinOp)
            and e.op == "^"
            and isinstance(e.left, Var)
            and e.left.name == independent_var
            and isinstance(e.right, Num)
        ):
            deg += int(e.right.value)
            var_seen = True
        else:
            return None, None
    if not var_seen and deg == 0 and coeff == 1.0 and not factors:
        return 0, 1.0
    return deg, coeff
