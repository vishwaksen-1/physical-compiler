"""
`parse_equation(raw_text) -> EquationSpec`, per INTERFACE_CONTRACTS.md §8.

Pipeline: normalize unicode shorthand -> lark parse -> internal AST ->
structural term/forcing extraction -> EquationSpec.

This module is the only place in src/parser that imports `lark`; grammar
mechanics stay here, semantic extraction stays in analysis.py, so the
"what does the text mean" logic can be unit-tested independent of the
grammar/lexer.
"""

from pathlib import Path
from typing import List, Tuple

try:
    from lark import Lark, Transformer, Token, v_args
    from lark.exceptions import LarkError

    _LARK_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only when lark isn't installed
    _LARK_AVAILABLE = False

    class LarkError(Exception):
        pass

    class Transformer:  # minimal stand-in so `class _ToAST(Transformer)` still defines
        def transform(self, tree):
            raise ImportError(
                "The 'lark' package is required to parse equation text "
                "(pip install -r requirements.txt). "
                "build_equation_spec_from_ast() works without it if you "
                "already have an AST."
            )

    def v_args(*args, **kwargs):
        def deco(cls):
            return cls

        return deco

    Token = str

from .analysis import (
    classify_forcing,
    contains_var,
    decompose_term,
    find_all_derivs,
    find_all_vars,
    flatten_additive,
    sum_signed,
)
from .ast_nodes import BinOp, Deriv, Expr, FuncCall, Neg, Num, Var
from .equation_spec import EquationSpec
from .errors import EquationParseError
from .preprocess import normalize_equation_text

_GRAMMAR_PATH = Path(__file__).parent / "grammar.lark"
_GRAMMAR_TEXT = _GRAMMAR_PATH.read_text(encoding="utf-8")

# Earley over LALR on purpose: the grammar allows an implicit
# "NUMBER atom" multiplication (2x, 3sin(t)) alongside explicit "*",
# which is easiest to keep unambiguous-by-construction with Earley's
# priority-based disambiguation rather than hand-tuning LALR conflicts.
# Equations are short single lines, so Earley's extra cost is a non-issue.
_lark = Lark(_GRAMMAR_TEXT, start="start", parser="earley", ambiguity="resolve") if _LARK_AVAILABLE else None


import re

# Non-greedy name groups: the trailing \d* (derivative order) has to win
# any ambiguity over the name itself, so "d2x/dt2" splits as
# name="x", denom_name="t", order=2 rather than swallowing the "2" into
# the name. This still lets multi-character/alphanumeric-tailed names
# work correctly (e.g. "dV1/dt" -> name="V1") because the engine only
# backtrack-extends the (non-greedy) name group while what's left of the
# string is entirely digits.
_DERIV_ODE_RE = re.compile(r"^d(\d*)([A-Za-z_][A-Za-z_0-9]*?)/d([A-Za-z_][A-Za-z_0-9]*?)(\d*)$")
_DERIV_PDE_RE = re.compile(r"^\u2202(\d*)([A-Za-z_][A-Za-z_0-9]*?)/\u2202([A-Za-z_][A-Za-z_0-9]*?)(\d*)$")
_PRIME_RE = re.compile(r"^([A-Za-z_][A-Za-z_0-9]*)('+)$")


@v_args(inline=True)
class _ToAST(Transformer):
    """Builds the internal ast_nodes.Expr tree from the lark parse tree.

    Each method name matches a rule/alias in grammar.lark.
    """

    def start(self, equation):
        return equation

    def equation(self, lhs, rhs):
        return (lhs, rhs)

    def add(self, a, b):
        return BinOp("+", a, b)

    def sub(self, a, b):
        return BinOp("-", a, b)

    def mul(self, a, b):
        return BinOp("*", a, b)

    def div(self, a, b):
        return BinOp("/", a, b)

    def mul_implicit(self, number_tok, atom):
        return BinOp("*", Num(float(number_tok)), atom)

    def neg(self, a):
        return Neg(a)

    def pow(self, a, b):
        return BinOp("^", a, b)

    def number(self, tok):
        return Num(float(tok))

    def var(self, tok):
        return Var(str(tok))

    def arglist(self, *args):
        return list(args)

    def func_call(self, name_tok, args):
        return FuncCall(str(name_tok), list(args))

    def deriv_ode(self, tok):
        m = _DERIV_ODE_RE.match(str(tok))
        order_num, dep, indep, order_den = m.groups()
        order = int(order_num) if order_num else 1
        return Deriv(var=dep, order=order, wrt=indep)

    def deriv_pde(self, tok):
        m = _DERIV_PDE_RE.match(str(tok))
        order_num, dep, indep, order_den = m.groups()
        order = int(order_num) if order_num else 1
        return Deriv(var=dep, order=order, wrt=indep)

    def prime_deriv(self, tok):
        m = _PRIME_RE.match(str(tok))
        name, primes = m.groups()
        return Deriv(var=name, order=len(primes), wrt=None)


def _resolve_prime_wrt(expr: Expr, independent_var: str) -> Expr:
    """Prime notation (x'') doesn't name its independent variable, so once
    we know the equation's single independent variable, fill it in.
    """
    if isinstance(expr, Deriv) and expr.wrt is None:
        return Deriv(var=expr.var, order=expr.order, wrt=independent_var)
    if isinstance(expr, Neg):
        return Neg(_resolve_prime_wrt(expr.operand, independent_var))
    if isinstance(expr, BinOp):
        return BinOp(expr.op, _resolve_prime_wrt(expr.left, independent_var), _resolve_prime_wrt(expr.right, independent_var))
    if isinstance(expr, FuncCall):
        return FuncCall(expr.name, [_resolve_prime_wrt(a, independent_var) for a in expr.args])
    return expr


def parse_equation(raw_text: str) -> EquationSpec:
    if raw_text is None or not raw_text.strip():
        raise EquationParseError("raw_text must be a non-empty string", raw_text=raw_text)
    if not _LARK_AVAILABLE:
        raise ImportError(
            "The 'lark' package is required to parse equation text "
            "(pip install -r requirements.txt)."
        )

    normalized = normalize_equation_text(raw_text)
    try:
        tree = _lark.parse(normalized)
    except LarkError as e:
        raise EquationParseError(f"Could not parse equation: {e}", raw_text=raw_text, cause=e) from e

    lhs, rhs = _ToAST().transform(tree)
    return build_equation_spec_from_ast(lhs, rhs, raw_text)


def build_equation_spec_from_ast(lhs: Expr, rhs: Expr, raw_text) -> EquationSpec:
    """Everything past "we have two Expr trees" — split out from
    parse_equation() so this half of the pipeline (structural extraction)
    is unit-testable by directly constructing ast_nodes trees, without
    needing the lark grammar/lexer at all. See tests/unit/parser/test_analysis.py.
    """
    all_derivs = find_all_derivs(lhs) + find_all_derivs(rhs)
    if not all_derivs:
        raise EquationParseError(
            "No derivative term found — the parser needs at least one "
            "derivative (e.g. x'', dx/dt, d2x/dt2) to identify the "
            "dependent variable and order.",
            raw_text=raw_text,
        )

    # Independent variable(s) named explicitly via Leibniz/partial forms
    # take precedence; prime notation (x'', no named wrt) is resolved
    # afterwards once we've picked one.
    named_wrt = {d.wrt for d in all_derivs if d.wrt is not None}
    is_pde = len(named_wrt) > 1
    if named_wrt:
        independent_vars = sorted(named_wrt)
        default_indep = independent_vars[0]
    else:
        # Only prime notation was used anywhere -> assume the conventional
        # single independent variable "t" for an ODE.
        default_indep = "t"
        independent_vars = [default_indep]

    lhs = _resolve_prime_wrt(lhs, default_indep)
    rhs = _resolve_prime_wrt(rhs, default_indep)
    all_derivs = find_all_derivs(lhs) + find_all_derivs(rhs)

    dependent_var_counts = {}
    for d in all_derivs:
        dependent_var_counts[d.var] = dependent_var_counts.get(d.var, 0) + 1
    dependent_var = max(dependent_var_counts, key=dependent_var_counts.get)

    order = max(d.order for d in all_derivs if d.var == dependent_var)
    domain_type = "PDE" if is_pde else "ODE"

    lhs_pieces = flatten_additive(lhs)
    rhs_pieces = flatten_additive(rhs)
    combined = [(sign, expr) for sign, expr in lhs_pieces] + [(-sign, expr) for sign, expr in rhs_pieces]

    term_pieces: List[Tuple[int, Expr]] = []
    forcing_pieces: List[Tuple[int, Expr]] = []
    for sign, expr in combined:
        if contains_var(expr, dependent_var):
            term_pieces.append((sign, expr))
        else:
            forcing_pieces.append((sign, expr))

    if not term_pieces:
        raise EquationParseError(
            f"Could not find any term involving the dependent variable "
            f"'{dependent_var}' on either side of the equation.",
            raw_text=raw_text,
        )

    wrt_default = independent_vars if is_pde else default_indep
    terms = [decompose_term(expr, dependent_var, sign, default_wrt=wrt_default) for sign, expr in term_pieces]

    # term_pieces already carries the sign such that sum(term_pieces) is
    # what equals the forcing function, so the forcing itself is the
    # NEGATION of forcing_pieces (see analysis.flatten_additive docstring
    # and the module-level derivation in analysis.py).
    forcing_negated = [(-sign, expr) for sign, expr in forcing_pieces]
    forcing_expr = sum_signed(forcing_negated)
    rhs_forcing = classify_forcing(forcing_expr, default_indep if not is_pde else None)

    return EquationSpec(
        domain_type=domain_type,
        independent_vars=independent_vars,
        dependent_var=dependent_var,
        order=order,
        terms=terms,
        rhs_forcing=rhs_forcing,
        input_source="text_parser",
        raw_text=raw_text,
    )
