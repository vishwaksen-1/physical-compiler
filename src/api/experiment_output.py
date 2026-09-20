"""
ExperimentOutput dataclass, exactly per INTERFACE_CONTRACTS.md §5, plus one
additive field.

Same dataclass + to_dict()/from_dict() convention as the repo's other
frozen schemas. Didn't exist anywhere before the Phase 2 session.

`description_blanks` is NOT part of INTERFACE_CONTRACTS.md §5 -- it's an
additive extension (logged in docs/STATUS.md, not a silent contract change)
carrying src.rendering.render_fill_blanks()'s structured per-parameter data
for the frontend's fill-in-the-blanks worksheet. Every other field matches
the frozen schema exactly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.canonical.ir import DifferentialEquationIR
from src.synthesis.candidate import CandidateMapping


@dataclass
class ExperimentOutput:
    compiler_version: str
    model_database_version: str
    config: dict
    input_equation_spec: dict
    canonical_ir: DifferentialEquationIR
    selected_candidate: Optional[CandidateMapping]
    alternative_candidates: list = field(default_factory=list)
    experiment_description: str = ""
    description_blanks: list = field(default_factory=list)
    build_instructions: dict = field(default_factory=dict)
    measurement_plan: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "compiler_version": self.compiler_version,
            "model_database_version": self.model_database_version,
            "config": dict(self.config),
            "input_equation_spec": dict(self.input_equation_spec),
            "canonical_ir": self.canonical_ir.to_dict(),
            "selected_candidate": self.selected_candidate.to_dict() if self.selected_candidate else None,
            "alternative_candidates": [c.to_dict() for c in self.alternative_candidates],
            "experiment_description": self.experiment_description,
            "description_blanks": list(self.description_blanks),
            "build_instructions": dict(self.build_instructions),
            "measurement_plan": dict(self.measurement_plan),
            "warnings": list(self.warnings),
        }
