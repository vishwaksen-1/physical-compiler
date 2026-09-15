"""
EquationSpec dataclass, exactly per INTERFACE_CONTRACTS.md §1.

dataclasses + to_dict()/from_dict() per the repo-wide convention
recommended in that file (round-trips through JSON for both the CLI
and the web API). This is the one shape both Agent C's text parser and
Agent D's web equation-builder must produce identically (module docstring
of INTERFACE_CONTRACTS.md §1: "the seam that lets Agent C and Agent D
work without ever talking to each other mid-phase").
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Union

SPEC_VERSION = "1.0"


@dataclass
class Term:
    derivative_order: int
    wrt: Union[str, List[str]]
    coefficient: Union[float, str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Term":
        return Term(
            derivative_order=d["derivative_order"],
            wrt=d["wrt"],
            coefficient=d["coefficient"],
        )


@dataclass
class RhsForcing:
    type: str
    params: Dict[str, Any] = field(default_factory=dict)
    expr: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RhsForcing":
        return RhsForcing(
            type=d["type"],
            params=dict(d.get("params") or {}),
            expr=d.get("expr"),
        )


@dataclass
class EquationSpec:
    domain_type: str  # "ODE" | "PDE"
    independent_vars: List[str]
    dependent_var: str
    order: int
    terms: List[Term]
    rhs_forcing: RhsForcing
    input_source: str  # "web_builder" | "text_parser"
    spec_version: str = SPEC_VERSION
    initial_conditions: Optional[Dict[str, Any]] = None
    boundary_conditions: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spec_version": self.spec_version,
            "domain_type": self.domain_type,
            "independent_vars": list(self.independent_vars),
            "dependent_var": self.dependent_var,
            "order": self.order,
            "terms": [t.to_dict() for t in self.terms],
            "rhs_forcing": self.rhs_forcing.to_dict(),
            "initial_conditions": self.initial_conditions,
            "boundary_conditions": self.boundary_conditions,
            "input_source": self.input_source,
            "raw_text": self.raw_text,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "EquationSpec":
        return EquationSpec(
            spec_version=d.get("spec_version", SPEC_VERSION),
            domain_type=d["domain_type"],
            independent_vars=list(d["independent_vars"]),
            dependent_var=d["dependent_var"],
            order=d["order"],
            terms=[Term.from_dict(t) for t in d["terms"]],
            rhs_forcing=RhsForcing.from_dict(d["rhs_forcing"]),
            initial_conditions=d.get("initial_conditions"),
            boundary_conditions=d.get("boundary_conditions"),
            input_source=d["input_source"],
            raw_text=d.get("raw_text"),
        )
