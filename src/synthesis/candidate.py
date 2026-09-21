"""
CandidateMapping dataclass, exactly per INTERFACE_CONTRACTS.md §4.

Same dataclass + to_dict()/from_dict() convention as EquationSpec
(src/parser/equation_spec.py), DifferentialEquationIR (src/canonical/ir.py),
and PhysicalModel (src/physics/models/registry.py). This one didn't exist
anywhere in the repo before this Phase 2 session — no prior track's scope
needed to construct one.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Score:
    exactness: float = 0.0
    feasibility: float = 0.0
    simplicity: float = 0.0
    total: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Score":
        return cls(**d)


@dataclass
class TransformationTrace:
    original_problem: str = ""
    transformed_problem: str = ""
    transformation_type: str = "direct"  # "direct" | "scaled" | "nondimensionalized"
    symbolic_derivation_steps: list[str] = field(default_factory=list)
    equivalence_status: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "TransformationTrace":
        return cls(**d)


@dataclass
class CandidateMapping:
    candidate_id: str
    model_id: str
    parameter_values: dict[str, float] = field(default_factory=dict)
    verification_status: str = "APPROXIMATE"  # "EXACT" | "APPROXIMATE" | "FAILED"
    residual_expr: str = ""
    assumptions: list[str] = field(default_factory=list)
    score: Score = field(default_factory=Score)
    transformation_trace: TransformationTrace = field(default_factory=TransformationTrace)

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "model_id": self.model_id,
            "parameter_values": dict(self.parameter_values),
            "verification_status": self.verification_status,
            "residual_expr": self.residual_expr,
            "assumptions": list(self.assumptions),
            "score": self.score.to_dict(),
            "transformation_trace": self.transformation_trace.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CandidateMapping":
        d = dict(d)
        score = d.get("score") or {}
        trace = d.get("transformation_trace") or {}
        return cls(
            candidate_id=d["candidate_id"],
            model_id=d["model_id"],
            parameter_values=dict(d.get("parameter_values") or {}),
            verification_status=d.get("verification_status", "APPROXIMATE"),
            residual_expr=d.get("residual_expr", ""),
            assumptions=list(d.get("assumptions") or []),
            score=Score.from_dict(score) if score else Score(),
            transformation_trace=TransformationTrace.from_dict(trace) if trace else TransformationTrace(),
        )
