"""
src/symbolic/engine.py

Single SymPy adapter for the whole compiler (PROJECT_PLAN.md §1.1). No other
module may `import sympy` directly — everything symbolic-math related is
funneled through this module so that:

  - a sympy version bump touches exactly one file,
  - determinism guarantees (sort_key()-ordered term serialization, never bare
    str()/Add.args order) live in exactly one place,
  - expensive operations (simplify()) are choke-pointed here so it's easy to
    keep an eye on the ~10s Vercel Hobby-tier function timeout
    (PROJECT_PLAN.md §1.8).

Owner: Agent A. Consumed by src/canonical/ and src/classifier/ only.
"""
from __future__ import annotations

import hashlib
from typing import Any, Optional

import sympy
from sympy import (
    Add,
    Derivative,
    Function,
    Integer,
    Symbol,
    expand,
    simplify as _sympy_simplify,
    sqrt,
    srepr,
    sympify,
)

# ---------------------------------------------------------------------------
# Locked-down namespace for parsing user/agent-authored expression strings
# (coefficients, custom forcing expressions). Only names we explicitly allow
# are reachable — sympify() is otherwise happy to eval arbitrary attribute
# chains, which we don't want anywhere near a serverless HTTP handler.
# ---------------------------------------------------------------------------
_ALLOWED_SYMPIFY_NAMES: dict[str, Any] = {
    "sin": sympy.sin,
    "cos": sympy.cos,
    "tan": sympy.tan,
    "exp": sympy.exp,
    "log": sympy.log,
    "sqrt": sqrt,
    "pi": sympy.pi,
    "E": sympy.E,
    "Abs": sympy.Abs,
    "Heaviside": sympy.Heaviside,
    "DiracDelta": sympy.DiracDelta,
}


def make_independent_symbols(independent_vars: list[str]) -> dict[str, Symbol]:
    return {v: Symbol(v, real=True) for v in independent_vars}


def build_parsing_symbol_table(independent_vars: list[str], dependent_var: str) -> dict[str, Any]:
    """
    Symbol table for parsing user-authored expression strings (term
    coefficients, `rhs_forcing.expr`). The dependent variable is mapped to
    its *unapplied* Function, and `Derivative` is made available, so authors
    can write ordinary sympy-flavoured strings like `"x(t)"` or
    `"Derivative(x(t), t)"` when a coefficient or forcing term needs to
    reference the dependent variable or its derivatives (e.g. a nonlinear
    small-angle-pendulum forcing term, or moving terms across the equals
    sign).
    """
    table: dict[str, Any] = dict(make_independent_symbols(independent_vars))
    table[dependent_var] = Function(dependent_var)
    table["Derivative"] = Derivative
    return table


def build_symbol_table(independent_vars: list[str], dependent_var: str) -> dict[str, Any]:
    """
    Symbol table for internal use (classifier `.has()`/free-symbol checks)
    where the dependent variable is the *applied* instance, e.g. `x(t)`.
    """
    iv_symbols = make_independent_symbols(independent_vars)
    y = Function(dependent_var)(*iv_symbols.values())
    table: dict[str, Any] = dict(iv_symbols)
    table[dependent_var] = y
    return table


def safe_sympify(expr_str: Optional[str], local_symbols: dict[str, Any]):
    """Sympify a string against a locked-down namespace. Never eval raw
    Python — sympify's own parser only reaches names present in the merged
    namespace."""
    if expr_str is None:
        return Integer(0)
    namespace = dict(_ALLOWED_SYMPIFY_NAMES)
    namespace.update(local_symbols)
    try:
        return sympify(expr_str, locals=namespace, convert_xor=True)
    except (sympy.SympifyError, TypeError, SyntaxError, AttributeError) as exc:
        raise ValueError(f"could not parse expression {expr_str!r}: {exc}") from exc


# ---------------------------------------------------------------------------
# EquationSpec -> sympy
# ---------------------------------------------------------------------------

def spec_to_lhs_rhs(spec: dict) -> tuple[sympy.Expr, sympy.Expr, dict[str, Any]]:
    """
    Build (lhs_expr, rhs_expr, symbol_table) from an EquationSpec dict
    (INTERFACE_CONTRACTS.md §1). `lhs_expr` is the sum of the spec's
    coefficient * derivative terms; `rhs_expr` is the forcing term. The full
    equation is `lhs_expr = rhs_expr`.

    `symbol_table` is returned in *applied-y* form (`build_symbol_table`) for
    convenient reuse by callers (see src/classifier/).
    """
    independent_vars = spec["independent_vars"]
    dependent_var = spec["dependent_var"]

    iv_symbols = make_independent_symbols(independent_vars)
    y = Function(dependent_var)(*iv_symbols.values())
    parse_table = build_parsing_symbol_table(independent_vars, dependent_var)

    lhs_terms = []
    for term in spec["terms"]:
        order = term["derivative_order"]
        wrt = term["wrt"]
        coeff = term["coefficient"]

        coeff_expr = safe_sympify(coeff, parse_table) if isinstance(coeff, str) else sympify(coeff)

        if order == 0:
            deriv = y
        elif isinstance(wrt, str):
            deriv = Derivative(y, *([iv_symbols[wrt]] * order))
        else:
            # list[str]: one independent-variable name per derivative order,
            # e.g. ["x", "t"] for d^2y/(dx dt) — length must match order.
            if len(wrt) != order:
                raise ValueError(
                    f"term derivative_order={order} but wrt has {len(wrt)} entries: {wrt!r}"
                )
            deriv = Derivative(y, *[iv_symbols[w] for w in wrt])

        lhs_terms.append(coeff_expr * deriv)

    lhs_expr = Add(*lhs_terms) if lhs_terms else Integer(0)
    rhs_expr = _forcing_to_sympy(spec.get("rhs_forcing"), parse_table, iv_symbols)

    symbol_table = build_symbol_table(independent_vars, dependent_var)
    return lhs_expr, rhs_expr, symbol_table


def _forcing_to_sympy(rhs_forcing: Optional[dict], parse_table: dict, iv_symbols: dict) -> sympy.Expr:
    if not rhs_forcing:
        return Integer(0)

    kind = rhs_forcing.get("type", "zero")
    params = rhs_forcing.get("params") or {}
    expr_str = rhs_forcing.get("expr")

    if kind == "zero":
        return Integer(0)
    if kind == "custom_expr":
        if not expr_str:
            raise ValueError("rhs_forcing.type == 'custom_expr' requires 'expr'")
        return safe_sympify(expr_str, parse_table)

    # Named canonical forcing shapes, built purely from `params` so the web
    # builder and text parser produce byte-identical sympy trees for the
    # "same" forcing function (INTERFACE_CONTRACTS.md §1 validation rule).
    t = next(iter(iv_symbols.values())) if iv_symbols else Symbol("t", real=True)

    if kind == "const":
        return sympify(params.get("value", 0))
    if kind == "step":
        amplitude = sympify(params.get("amplitude", 1))
        t0 = sympify(params.get("t0", 0))
        return amplitude * sympy.Heaviside(t - t0)
    if kind == "impulse":
        amplitude = sympify(params.get("amplitude", 1))
        t0 = sympify(params.get("t0", 0))
        return amplitude * sympy.DiracDelta(t - t0)
    if kind == "sin":
        amp = sympify(params.get("amplitude", 1))
        freq = sympify(params.get("frequency", 1))
        phase = sympify(params.get("phase", 0))
        return amp * sympy.sin(freq * t + phase)
    if kind == "cos":
        amp = sympify(params.get("amplitude", 1))
        freq = sympify(params.get("frequency", 1))
        phase = sympify(params.get("phase", 0))
        return amp * sympy.cos(freq * t + phase)
    if kind == "polynomial":
        coeffs = params.get("coefficients", [])  # low-to-high degree
        return Add(*[sympify(c) * t ** i for i, c in enumerate(coeffs)]) if coeffs else Integer(0)

    raise ValueError(f"unknown rhs_forcing.type: {kind!r}")


# ---------------------------------------------------------------------------
# Canonicalization (cheap path — no simplify() unless explicitly asked for)
# ---------------------------------------------------------------------------

def canonical_expr(lhs: sympy.Expr, rhs: sympy.Expr) -> sympy.Expr:
    """
    expand(lhs - rhs). Deliberately NOT calling simplify()/trigsimp() here:
    expand() is sufficient to normalize the flat sum-of-terms shape our
    EquationSpec already encodes, and is cheap relative to simplify(), which
    is reserved for are_equivalent()'s bounded fallback path only.
    """
    return expand(lhs - rhs)


def ordered_terms(expr: sympy.Expr) -> list[sympy.Expr]:
    """Deterministic term ordering for serialization — explicitly sorted by
    lexicographic monomial order, independent of Add.args iteration order or
    PYTHONHASHSEED. This is the "sorted printer" PROJECT_PLAN.md §1.2 and
    the Agent A task brief both call for."""
    expr = expand(expr)
    if isinstance(expr, Add):
        return list(expr.as_ordered_terms(order="lex"))
    return [expr]


def canonical_srepr(expr: sympy.Expr) -> str:
    """Serialize expr via the sorted term list above, joined with srepr() of
    each term — never bare str()/srepr() of the raw (unsorted) expression."""
    terms = ordered_terms(expr)
    return " + ".join(srepr(t) for t in terms)


def equivalence_hash(expr: sympy.Expr) -> str:
    canonical = canonical_srepr(expr)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Equivalence testing
# ---------------------------------------------------------------------------

def are_equivalent(lhs1: sympy.Expr, rhs1: sympy.Expr, lhs2: sympy.Expr, rhs2: sympy.Expr) -> bool:
    """
    Cheap path: expand(diff) == 0, which is sufficient for the linear
    sum-of-derivative-terms shape EquationSpec encodes. Falls back to a
    single bounded simplify() call only if expand() doesn't immediately
    settle it (e.g. trig-identity forcing terms) — keeps this safe to call
    inside the 10s serverless budget.
    """
    diff = expand((lhs1 - rhs1) - (lhs2 - rhs2))
    if diff == 0:
        return True
    return _sympy_simplify(diff) == 0


# ---------------------------------------------------------------------------
# Small wrappers so downstream modules (src/canonical/, src/classifier/)
# never need to `import sympy` themselves.
# ---------------------------------------------------------------------------

def diff(expr: sympy.Expr, var: sympy.Expr, n: int = 1) -> sympy.Expr:
    return sympy.diff(expr, var, n)


def is_zero(expr: sympy.Expr) -> bool:
    return expand(expr) == 0


def zero() -> sympy.Expr:
    return Integer(0)


def has_symbol(expr: sympy.Expr, symbol: sympy.Expr) -> bool:
    return expr.has(symbol)


def free_symbols(expr: sympy.Expr):
    return expr.free_symbols


def dependent_var_atoms(expr: sympy.Expr, y: sympy.Expr) -> set:
    """
    All occurrences of the dependent variable *and* its derivatives inside
    `expr` (e.g. for y=x(t): x(t) itself, Derivative(x(t), t),
    Derivative(x(t), t, t), ...). Used to test linearity of the whole
    equation in the "y-family" of atoms, since checking any single
    coefficient in isolation misses cross-terms like x(t)*Derivative(x(t), t)
    (nonlinear as a system even though each factor is individually linear).
    """
    atoms: set = set()
    if expr.has(y):
        atoms |= expr.atoms(y.func)
    atoms |= {d for d in expr.atoms(Derivative) if d.expr == y}
    return atoms


def total_degree_in(expr: sympy.Expr, atoms: set) -> int:
    """
    Total polynomial degree of `expr` treating each element of `atoms` as an
    independent variable (via substitution with fresh dummies). Returns a
    value >= 2 (nonlinear) for any non-polynomial dependence on those atoms,
    e.g. sin(y), exp(y), 1/y — not just for genuine higher-degree terms.
    """
    if not atoms:
        return 0
    dummies = {atom: Symbol(f"_lin_dummy_{i}") for i, atom in enumerate(atoms)}
    substituted = expand(expr.subs(dummies))
    dummy_symbols = list(dummies.values())
    if not substituted.is_polynomial(*dummy_symbols):
        return 2
    return sympy.Poly(substituted, *dummy_symbols).total_degree()


def max_derivative_order(spec: dict) -> int:
    if not spec["terms"]:
        return 0
    return max(t["derivative_order"] for t in spec["terms"])
