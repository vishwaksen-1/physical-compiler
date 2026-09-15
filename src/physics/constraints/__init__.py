"""Feasibility + safety-limit checks per model (Agent B).

`generic.py` implements checks that work off any `PhysicalModel`'s
`parameter_constraints` dict alone (range checks). `model_specific.py` adds
a few cheap, physically-meaningful cross-parameter checks per model
(e.g. damping-ratio sanity, resonance-frequency sanity) that a pure
range check can't catch.

These are building blocks. The actual `check_feasibility(candidate) ->
CandidateMapping` function from INTERFACE_CONTRACTS.md §8 lives in
`src/api/` (integration layer, Phase 2) and is expected to call into this
package rather than duplicate this logic.
"""

from .generic import check_parameter_ranges, check_dimensional_consistency
from .model_specific import check_model_specific, MODEL_SPECIFIC_CHECKS

__all__ = [
    "check_parameter_ranges",
    "check_dimensional_consistency",
    "check_model_specific",
    "MODEL_SPECIFIC_CHECKS",
    "run_all_checks",
]


def run_all_checks(model, parameter_values: dict) -> list[str]:
    """Run every applicable check for `model` against `parameter_values`.
    Returns a list of human-readable violation/warning strings (empty list
    means the candidate is feasible by these checks)."""
    violations: list[str] = []
    violations.extend(check_parameter_ranges(model, parameter_values))
    violations.extend(check_dimensional_consistency(model))
    violations.extend(check_model_specific(model, parameter_values))
    return violations
