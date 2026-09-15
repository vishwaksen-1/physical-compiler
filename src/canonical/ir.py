"""
src/canonical/ir.py

Builds DifferentialEquationIR (INTERFACE_CONTRACTS.md §2) from an
EquationSpec dict. Owns `equivalence_hash`. Never imports sympy directly —
all symbolic work goes through src/symbolic/engine.py.

Owner: Agent A.

Field-population split with src/classifier/ (documented here since the
contract only pins data shapes, not which module writes which field first):
  - canonicalize() fills every IR field it can derive purely structurally
    from the spec: canonical_form, order, domain_type (copied from the
    validated spec), independent_vars, dependent_var, coefficients,
    forcing_term, equivalence_hash, source_spec_ref.
  - canonicalize() leaves `linearity`, `homogeneity`, and
    `classification_tags` blank (empty string / empty list) — those require
    symbolic analysis that is squarely src/classifier/'s job per
    PROJECT_PLAN.md §2's track split. src/classifier/classifier.classify(ir)
    fills them in (mutating the IR in place) and also returns
    classification_tags, matching INTERFACE_CONTRACTS.md §8's declared
    `classify(ir) -> list[str]` signature.
  - Callers (src/api/ integration layer, not built in this session) should
    call `canonicalize(spec)` then `classify(ir)` before treating an IR as
    complete.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

from src.symbolic import engine as sym

IR_VERSION = "1.0"


@dataclass
class DifferentialEquationIR:
    ir_version: str
    canonical_form: str
    domain_type: str
    order: int
    linearity: str
    homogeneity: str
    independent_vars: list[str]
    dependent_var: str
    coefficients: dict[str, str]
    forcing_term: str
    classification_tags: list[str]
    equivalence_hash: str
    source_spec_ref: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "DifferentialEquationIR":
        return cls(**d)


def _coefficient_key(term: dict) -> str:
    order = term["derivative_order"]
    wrt = term["wrt"]
    if order == 0:
        return "d0"
    if isinstance(wrt, list):
        return f"d{order}_" + "_".join(wrt)
    return f"d{order}_{wrt}"


def _spec_ref(spec: dict) -> str:
    """Stable-ish provenance breadcrumb for logs/tests — NOT a content hash
    (that's equivalence_hash's job), just enough to trace an IR back to the
    EquationSpec that produced it."""
    return f"{spec.get('input_source', 'unknown')}:{spec.get('dependent_var', '?')}"


def canonicalize(spec: dict) -> DifferentialEquationIR:
    """INTERFACE_CONTRACTS.md §8: canonicalize(spec: EquationSpec) -> DifferentialEquationIR."""
    lhs, rhs, _symbol_table = sym.spec_to_lhs_rhs(spec)

    canonical = sym.canonical_expr(lhs, rhs)
    canonical_form = sym.canonical_srepr(canonical)
    eq_hash = sym.equivalence_hash(canonical)
    forcing_term = sym.canonical_srepr(rhs)

    coefficients = {_coefficient_key(term): str(term["coefficient"]) for term in spec["terms"]}

    return DifferentialEquationIR(
        ir_version=IR_VERSION,
        canonical_form=canonical_form,
        domain_type=spec["domain_type"],
        order=sym.max_derivative_order(spec),
        linearity="",
        homogeneity="",
        independent_vars=list(spec["independent_vars"]),
        dependent_var=spec["dependent_var"],
        coefficients=coefficients,
        forcing_term=forcing_term,
        classification_tags=[],
        equivalence_hash=eq_hash,
        source_spec_ref=_spec_ref(spec),
    )
