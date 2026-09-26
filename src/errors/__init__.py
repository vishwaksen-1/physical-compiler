"""
errors — error / approximation modeling (Phase 3, spec §21) and safety
boundary checks (spec §30).

Owner: Agent A's track; implemented in this session.

Consumes: CandidateMapping (INTERFACE_CONTRACTS.md §4) and the matched
PhysicalModel's `approximation_model` / `error_model` / `safety_notes` /
`parameter_constraints` fields (INTERFACE_CONTRACTS.md §3).
Produces: warning strings that compile_equation() folds into
ExperimentOutput.warnings (INTERFACE_CONTRACTS.md §5).

Everything here is deterministic: warnings are produced in a fixed order
(operating-point checks first, in the model's own parameter_map order, then
approximation warnings, then safety notes), never from dict iteration order.
"""
from __future__ import annotations

import math

# A parameter sitting within this fraction of a declared bound is flagged as
# near the edge of what's realistically buildable, even though it's legal.
#
# Proximity is measured on a LOG scale whenever both bounds are positive,
# because component ranges routinely span orders of magnitude (spring
# constants 1-2000 N/m, resistances 0.1-1000 Ohm) and are sourced
# log-uniformly — you buy a 10 N/m spring or a 100 N/m spring, not a
# linearly-interpolated one. Judging these linearly produced constant false
# positives: the geometric-mean anchor that synthesis picks for an
# underdetermined parameter always looks "near the minimum" on a linear
# axis for a wide range, so every anchored parameter got flagged.
_EDGE_FRACTION = 0.05


def _edge_position(value: float, lo: float, hi: float):
    """Where `value` sits in [lo, hi] as a 0..1 fraction, log-scaled when
    that's the meaningful axis. Returns None if the range is degenerate or
    the value is outside it (out-of-range is synthesize_parameters' job to
    clamp and verify_mapping's job to catch, not a warning here)."""
    if hi <= lo:
        return None
    if value < lo or value > hi:
        return None
    if lo > 0 and hi > 0:
        return (math.log(value) - math.log(lo)) / (math.log(hi) - math.log(lo))
    return (value - lo) / (hi - lo)


def _near_edge_warnings(model, candidate) -> list:
    """Parameters that are technically in range but close enough to a
    declared bound that a real build will struggle to hit them."""
    warnings = []
    ordered_names = [n for n in (model.parameter_map or {}) if n in candidate.parameter_values]
    ordered_names += sorted(n for n in candidate.parameter_values if n not in ordered_names)

    for name in ordered_names:
        value = candidate.parameter_values[name]
        constraint = (model.parameter_constraints or {}).get(name)
        if not constraint:
            continue
        lo, hi = constraint.get("min"), constraint.get("max")
        unit = constraint.get("unit", "")
        if lo is None or hi is None:
            continue
        position = _edge_position(value, lo, hi)
        if position is None:
            continue
        if position <= _EDGE_FRACTION:
            warnings.append(
                f"{name} = {value:.4g}{unit} sits near the bottom of its buildable range "
                f"[{lo}, {hi}]{unit} — sourcing this component may be difficult."
            )
        elif position >= 1.0 - _EDGE_FRACTION:
            warnings.append(
                f"{name} = {value:.4g}{unit} sits near the top of its buildable range "
                f"[{lo}, {hi}]{unit} — sourcing this component may be difficult."
            )
    return warnings


def _approximation_warnings(model) -> list:
    approximation = model.approximation_model or {}
    approx_type = approximation.get("type", "none")
    if approx_type == "none":
        return []
    if approx_type == "linearization":
        return [
            "This apparatus realizes the target equation only as a linearization — it "
            "matches near the operating point and diverges as amplitude grows."
        ]
    if approx_type == "discretization":
        return [
            "This apparatus realizes the target equation only as a spatial discretization — "
            "it approaches the continuum behavior as the element count rises, and deviates "
            "at short wavelengths."
        ]
    return [f"This apparatus involves an approximation of type '{approx_type}'."]


def _expected_error_warning(model) -> list:
    error_model = model.error_model or {}
    pct = error_model.get("expected_relative_error_pct")
    if pct is None:
        return []
    if float(pct) >= 10.0:
        return [
            f"Expected relative error is high ({float(pct):.4g}%) — this realization is "
            "qualitatively right but not a precision match."
        ]
    return []


def _safety_warnings(model) -> list:
    return [f"Safety: {note}" for note in (model.safety_notes or [])]


def analyze_candidate(model, candidate) -> list:
    """All error/approximation/safety warnings for one candidate, in a fixed
    deterministic order. Called by src/api/compile_equation() for the
    selected candidate only — alternatives don't contribute warnings, since
    the user isn't being told to build those."""
    warnings = []
    warnings.extend(_near_edge_warnings(model, candidate))
    warnings.extend(_approximation_warnings(model))
    warnings.extend(_expected_error_warning(model))
    warnings.extend(_safety_warnings(model))
    return warnings
