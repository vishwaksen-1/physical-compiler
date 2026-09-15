"""
Small internal expression AST.

This is *not* part of the frozen EquationSpec contract — it's a private
intermediate representation used only inside src/parser while turning a
lark parse tree into an EquationSpec. Kept deliberately dumb (no
simplification, no evaluation) since real symbolic work belongs to
Agent A's src/symbolic/engine.py, per PROJECT_PLAN.md §1.1: "no other
module imports sympy directly."

Every node knows how to render itself back to a canonical string via
`to_str()`, which is what we use as the fallback `raw` text for
coefficients/expr fields that aren't plain numbers.
"""

from dataclasses import dataclass, field
from typing import List, Union


class Expr:
    def to_str(self) -> str:  # pragma: no cover - overridden everywhere
        raise NotImplementedError


@dataclass
class Num(Expr):
    value: float

    def to_str(self) -> str:
        if float(self.value).is_integer():
            return str(int(self.value))
        return str(self.value)


@dataclass
class Var(Expr):
    name: str

    def to_str(self) -> str:
        return self.name


@dataclass
class Deriv(Expr):
    """A derivative of `var` of the given `order` with respect to `wrt`."""

    var: str
    order: int
    wrt: str

    def to_str(self) -> str:
        if self.order == 0:
            return self.var
        if self.order == 1:
            return f"d{self.var}/d{self.wrt}"
        return f"d{self.order}{self.var}/d{self.wrt}{self.order}"


@dataclass
class FuncCall(Expr):
    name: str
    args: List[Expr] = field(default_factory=list)

    def to_str(self) -> str:
        return f"{self.name}({', '.join(a.to_str() for a in self.args)})"


@dataclass
class Neg(Expr):
    operand: Expr

    def to_str(self) -> str:
        return f"-{_paren(self.operand)}"


@dataclass
class BinOp(Expr):
    op: str  # "+" | "-" | "*" | "/" | "^"
    left: Expr
    right: Expr

    def to_str(self) -> str:
        return f"{_paren(self.left)} {self.op} {_paren(self.right)}"


def _paren(e: Expr) -> str:
    # Cheap, always-safe parenthesization (not minimal, but unambiguous
    # and deterministic, which is what matters for round-tripping into
    # a `coefficient`/`expr` string).
    if isinstance(e, (Num, Var, Deriv, FuncCall)):
        return e.to_str()
    return f"({e.to_str()})"


Additive = Union[Neg, BinOp, Num, Var, Deriv, FuncCall]
