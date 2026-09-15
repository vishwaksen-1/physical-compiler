"""Model-agnostic feasibility checks — operate purely off the
`parameter_constraints` / `dimensional_constraints` dicts every
`PhysicalModel` carries, per INTERFACE_CONTRACTS.md §3.
"""

from __future__ import annotations


def check_parameter_ranges(model, parameter_values: dict) -> list[str]:
    """Check each supplied parameter value against `model.parameter_constraints`.

    `parameter_values` maps parameter names (as used in `model.parameter_map`,
    e.g. "m", "c", "k") to proposed numeric values — this is the shape
    `CandidateMapping.parameter_values` takes per INTERFACE_CONTRACTS.md §4.
    """
    violations: list[str] = []
    for name, value in parameter_values.items():
        constraint = model.parameter_constraints.get(name)
        if constraint is None:
            continue  # no declared constraint for this parameter -> nothing to check
        lo = constraint.get("min")
        hi = constraint.get("max")
        unit = constraint.get("unit", "")
        if lo is not None and value < lo:
            violations.append(
                f"{model.model_id}: parameter '{name}'={value}{unit} is below "
                f"minimum {lo}{unit}"
            )
        if hi is not None and value > hi:
            violations.append(
                f"{model.model_id}: parameter '{name}'={value}{unit} exceeds "
                f"maximum {hi}{unit}"
            )
    return violations


def check_dimensional_consistency(model) -> list[str]:
    """Sanity check that `dimensional_constraints` declares an entry for
    every parameter in `parameter_map` and every state variable in
    `state_variables`. This is a structural/authoring check (catches a model
    file that forgot to document a dimension), not a numeric feasibility
    check — it should never fail for the five models in this file, but will
    catch drift as the registry grows in Phase 3.
    """
    violations: list[str] = []
    dims = model.dimensional_constraints
    for param_name in model.parameter_map:
        if param_name not in dims:
            violations.append(
                f"{model.model_id}: no dimensional_constraints entry for "
                f"parameter '{param_name}'"
            )
    for state_name in model.state_variables:
        if state_name not in dims:
            violations.append(
                f"{model.model_id}: no dimensional_constraints entry for "
                f"state variable '{state_name}'"
            )
    return violations
