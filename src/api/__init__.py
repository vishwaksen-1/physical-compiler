"""
api (src/api/) — integration layer. Pure Python, no HTTP, no FastAPI
imports (that boundary lives in the repo-root `api/index.py` instead —
don't confuse the two `api` directories, see PROJECT_PLAN.md §2).

Owner: shared — this is the seam every other track's functions get wired
together through, per INTERFACE_CONTRACTS.md §8. Implemented in this
session (Phase 2), wiring together Agent A/B/C's already-real code.

Consumes: raw_text and/or builder_state (whichever is non-null) + a config
dict, per INTERFACE_CONTRACTS.md §9's POST /api/compile contract.
Produces: ExperimentOutput (INTERFACE_CONTRACTS.md §5).

Implements INTERFACE_CONTRACTS.md §8's top-level orchestration functions:
- `build_equation_spec_from_web(builder_state: dict) -> EquationSpec`
- `check_feasibility(candidate: CandidateMapping) -> CandidateMapping`
  (placement here rather than in src/physics/constraints/ follows that
  package's own docstring, written by Agent B's session)
- `compile_equation(raw_text, builder_state, config) -> ExperimentOutput`

Every function here is independently unit-testable outside the HTTP layer
(INTERFACE_CONTRACTS.md §9 closing note) — this is what lets
`api/index.py` (FastAPI) and `cli/` both call the exact same logic.

Phase 3 update (this session): `experiment_description` now comes from the
real `src.rendering.render_description()` (Agent C's deterministic-NLG
track), replacing the `_placeholder_description()` stand-in that lived here
during Phase 2. Warnings now also include error/approximation/safety
analysis from `src.errors.analyze_candidate()` (Agent A's Phase 3 track).
"""
from __future__ import annotations

import os

import yaml

from src.canonical.ir import canonicalize
from src.classifier.classifier import classify
from src.parser.equation_spec import EquationSpec
from src.parser.validator import validate_equation_spec
from src.physics.models import get_model, get_registry
from src.physics.constraints import run_all_checks
from src.synthesis import generate_candidates, rank_candidates, synthesize_parameters
from src.synthesis.candidate import CandidateMapping
from src.verification import verify_mapping
from src.rendering import render_description, render_fill_blanks
from src.errors import analyze_candidate
from src.api.experiment_output import ExperimentOutput

COMPILER_VERSION = "0.3.0"  # Phase 3: real NLG rendering + error/safety modeling
MODEL_DATABASE_VERSION = "0.1.0"  # bump when the physical_models registry composition changes

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_RANKING_POLICY_PATH = os.path.join(_REPO_ROOT, "data", "ranking_policy.yaml")


def _load_ranking_policy() -> dict:
    with open(_RANKING_POLICY_PATH, "r") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# build_equation_spec_from_web
# ---------------------------------------------------------------------------

def build_equation_spec_from_web(builder_state: dict) -> EquationSpec:
    """INTERFACE_CONTRACTS.md §8: build_equation_spec_from_web(builder_state) -> EquationSpec.

    The current web frontend (web/builder.js's buildEquationSpec()) already
    constructs a full EquationSpec-shaped dict client-side and sends it
    directly as `builder_state` — so this function's job is to validate
    that dict against INTERFACE_CONTRACTS.md §1 (the same
    validate_equation_spec() Agent C's text parser is checked against) and
    parse it into the shared EquationSpec dataclass. It is not a
    from-scratch UI-state translator; if a future web builder ever sends
    genuinely raw form state instead of an already-spec-shaped dict, that
    translation would need to be added here.
    """
    if not isinstance(builder_state, dict):
        raise ValueError("builder_state must be a dict")

    normalized = dict(builder_state)
    normalized.setdefault("spec_version", "1.0")
    normalized["input_source"] = "web_builder"
    normalized.setdefault("raw_text", None)

    result = validate_equation_spec(normalized)
    result.raise_if_invalid()

    return EquationSpec.from_dict(normalized)


# ---------------------------------------------------------------------------
# check_feasibility
# ---------------------------------------------------------------------------

def check_feasibility(candidate: CandidateMapping) -> CandidateMapping:
    """INTERFACE_CONTRACTS.md §8: check_feasibility(candidate) -> CandidateMapping.

    Runs src.physics.constraints.run_all_checks() and sets
    score.feasibility: 1.0 with no violations, decayed 0.25 per violation
    (floor 0.0). CandidateMapping has no dedicated warnings field, so
    violations are appended into `candidate.assumptions` tagged
    "feasibility: ..." — compile_equation() promotes the *selected*
    candidate's feasibility notes up into ExperimentOutput.warnings.
    """
    model = get_model(candidate.model_id)
    violations = run_all_checks(model, candidate.parameter_values)

    candidate.score.feasibility = max(0.0, 1.0 - 0.25 * len(violations))
    candidate.assumptions = list(candidate.assumptions) + [f"feasibility: {v}" for v in violations]
    return candidate


# ---------------------------------------------------------------------------
# Build-instructions / measurement-plan assembly
# (experiment_description comes from src.rendering, see module docstring)
# ---------------------------------------------------------------------------

def _build_instructions(model, candidate: CandidateMapping) -> dict:
    if model is None or candidate is None:
        return {}
    cr = model.construction_requirements or {}
    parameter_map = model.parameter_map or {}
    constraints = model.parameter_constraints or {}

    # parameter_roles / parameter_units let a client label the
    # coefficient -> component mapping without needing its own copy of the
    # registry metadata. Both are keyed by the same parameter names as
    # candidate.parameter_values.
    parameter_roles = {}
    parameter_units = {}
    for name in candidate.parameter_values:
        description = parameter_map.get(name, "")
        # parameter_map values look like "mass (kg)" -- split the unit out so
        # the role reads cleanly next to a separately-formatted value.
        role = description.split("(")[0].strip() if description else ""
        parameter_roles[name] = role
        parameter_units[name] = constraints.get(name, {}).get("unit", "")

    return {
        "model_id": model.model_id,
        "display_name": model.display_name,
        "components": cr.get("components", []),
        "estimated_build_time_hours": cr.get("estimated_build_time_hours"),
        "estimated_cost_usd": cr.get("estimated_cost_usd"),
        "notes": cr.get("notes", ""),
        "parameter_values": dict(candidate.parameter_values),
        "parameter_roles": parameter_roles,
        "parameter_units": parameter_units,
        "artwork": model.artwork,
        "safety_notes": list(model.safety_notes),
    }


def _measurement_plan(model) -> dict:
    if model is None:
        return {}
    return {
        "measurable_variables": list(model.measurable_variables),
        "controllable_variables": list(model.controllable_variables),
        "state_variables": dict(model.state_variables),
    }


# ---------------------------------------------------------------------------
# compile_equation
# ---------------------------------------------------------------------------

def compile_equation(raw_text, builder_state, config: dict) -> ExperimentOutput:
    """INTERFACE_CONTRACTS.md §8 + §9's POST /api/compile contract.

    Pipeline: parse/build EquationSpec -> canonicalize -> classify ->
    generate_candidates -> (synthesize_parameters -> verify_mapping ->
    check_feasibility) per candidate -> rank_candidates -> assemble
    ExperimentOutput. Exactly one of raw_text / builder_state must be
    non-null, per the HTTP contract.
    """
    if (raw_text is None) == (builder_state is None):
        raise ValueError("exactly one of raw_text / builder_state must be non-null")

    if raw_text is not None:
        from src.parser.text_parser import parse_equation

        spec_obj = parse_equation(raw_text)
    else:
        spec_obj = build_equation_spec_from_web(builder_state)

    spec_dict = spec_obj.to_dict()

    ir = canonicalize(spec_dict)
    classify(ir)

    registry = get_registry()
    candidates = generate_candidates(ir, registry)

    processed = []
    for candidate in candidates:
        candidate = synthesize_parameters(candidate)
        candidate = verify_mapping(ir, candidate)
        candidate = check_feasibility(candidate)
        processed.append(candidate)

    config = dict(config or {})
    selection_mode = config.get("candidate_selection_mode", "deterministic_top_rank")
    seed = config.get("candidate_seed") if selection_mode == "seeded_random" else None

    policy = _load_ranking_policy()
    ranked = rank_candidates(processed, policy, seed)

    selected = ranked[0] if ranked else None
    alternatives = ranked[1:] if ranked else []
    selected_model = get_model(selected.model_id) if selected else None

    warnings = []
    if not ranked:
        warnings.append(
            "No physical model in the registry currently matches this equation's shape "
            "-- see PROJECT_PLAN.md Phase 3 for planned registry breadth."
        )
    if selected:
        warnings.extend(a for a in selected.assumptions if a.startswith("feasibility:"))
        warnings.extend(analyze_candidate(selected_model, selected))

    output = ExperimentOutput(
        compiler_version=COMPILER_VERSION,
        model_database_version=MODEL_DATABASE_VERSION,
        config={"candidate_selection_mode": selection_mode, "candidate_seed": seed},
        input_equation_spec=spec_dict,
        canonical_ir=ir,
        selected_candidate=selected,
        alternative_candidates=alternatives,
        experiment_description="",  # filled immediately below
        description_blanks=[],       # filled immediately below
        build_instructions=_build_instructions(selected_model, selected),
        measurement_plan=_measurement_plan(selected_model),
        warnings=warnings,
    )
    # render_description()/render_fill_blanks() read the assembled output
    # (canonical_ir, selected_candidate, alternatives), so they run after
    # construction.
    output.experiment_description = render_description(output)
    output.description_blanks = render_fill_blanks(output)
    return output
