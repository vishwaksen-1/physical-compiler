# Interface Contracts — FROZEN in Phase 0

Everything below is a contract, not a suggestion. If your module needs to deviate, log it in `docs/STATUS.md` before other agents build against the old shape.

Schemas shown as Python type-hinted pseudocode. Pick one implementation convention repo-wide (recommend `dataclasses` + `to_dict()`/`from_dict()`, since these round-trip through JSON for both the CLI and the web API).

## 1. EquationSpec
Produced identically by the web equation-builder (client-side JS) and the text parser (Python). This is the seam that lets Agent C and Agent D work without ever talking to each other mid-phase.

```python
EquationSpec = {
    "spec_version": "1.0",
    "domain_type": "ODE" | "PDE",
    "independent_vars": list[str],
    "dependent_var": str,
    "order": int,
    "terms": [
        {"derivative_order": int, "wrt": str | list[str], "coefficient": float | str},
        ...
    ],
    "rhs_forcing": {
        "type": "zero" | "const" | "sin" | "cos" | "step" | "impulse" | "polynomial" | "custom_expr",
        "params": dict,
        "expr": str | None,
    },
    "initial_conditions": dict | None,
    "boundary_conditions": dict | None,
    "input_source": "web_builder" | "text_parser",
    "raw_text": str | None,
}
```

Validation rule (Agent C owns this): a web-builder-produced spec and a text-parser-produced spec for the "same" equation must be structurally identical except for `input_source` and `raw_text`.

## 2. DifferentialEquation IR
```python
DifferentialEquationIR = {
    "ir_version": "1.0",
    "canonical_form": str,
    "domain_type": "ODE" | "PDE",
    "order": int,
    "linearity": "linear" | "nonlinear",
    "homogeneity": "homogeneous" | "nonhomogeneous",
    "independent_vars": list[str],
    "dependent_var": str,
    "coefficients": dict[str, str],
    "forcing_term": str,
    "classification_tags": list[str],
    "equivalence_hash": str,
    "source_spec_ref": str,
}
```

## 3. PhysicalModel (registry entry)
```python
PhysicalModel = {
    "model_id": str,
    "display_name": str,
    "domain": "mechanical" | "electrical" | "thermal" | "other",
    "equation_class_tags": list[str],
    "state_variables": dict[str, str],
    "governing_equation": "sympy.Expr",
    "parameter_map": dict[str, str],
    "parameter_constraints": dict[str, dict],
    "dimensional_constraints": dict,
    "measurable_variables": list[str],
    "controllable_variables": list[str],
    "construction_requirements": dict,
    "approximation_model": {"type": "none" | "linearization" | "discretization", "assumptions": list[str]},
    "error_model": {"sources": list[str], "expected_relative_error_pct": float},
    "safety_notes": list[str],
    "alt_realizations_of": str | None,
}
```

## 4. CandidateMapping
```python
CandidateMapping = {
    "candidate_id": str,
    "model_id": str,
    "parameter_values": dict[str, float],
    "verification_status": "EXACT" | "APPROXIMATE" | "FAILED",
    "residual_expr": str,
    "assumptions": list[str],
    "score": {"exactness": float, "feasibility": float, "simplicity": float, "total": float},
    "transformation_trace": {
        "original_problem": str, "transformed_problem": str,
        "transformation_type": "direct" | "scaled" | "nondimensionalized",
        "symbolic_derivation_steps": list[str], "equivalence_status": str,
    },
}
```

## 5. ExperimentOutput (final structured result)
```python
ExperimentOutput = {
    "compiler_version": str,
    "model_database_version": str,
    "config": {"candidate_selection_mode": "deterministic_top_rank" | "seeded_random", "candidate_seed": int | None},
    "input_equation_spec": EquationSpec,
    "canonical_ir": DifferentialEquationIR,
    "selected_candidate": CandidateMapping,
    "alternative_candidates": list[CandidateMapping],
    "experiment_description": str,
    "build_instructions": dict,
    "measurement_plan": dict,
    "warnings": list[str],
}
```

## 6. Determinism / randomness policy

- **Default (`"deterministic_top_rank"`):** fixed ranking policy (§7) picks the top candidate. `candidate_seed` is `null`. Same input + config → same output, always.
- **"Surprise me" (`"seeded_random"`):** the web frontend generates an explicit seed client-side (or the backend does on request) when the user asks for variety, sends it in the request body, and the response echoes it back in `config.candidate_seed`. Re-POSTing with the same seed reproduces the exact same candidate.
- Tie-break in deterministic mode: stable registry insertion order, never set/dict iteration order.

## 7. Default ranking policy (`data/ranking_policy.yaml`)
```yaml
ranking_policy_version: "1.0"
weights:
  exactness: 0.5
  feasibility: 0.3
  simplicity: 0.2
tie_break: "registry_insertion_order"
```

## 8. Core Python API (called from inside the HTTP layer, also directly by the CLI)
```python
def parse_equation(raw_text: str) -> EquationSpec: ...
def build_equation_spec_from_web(builder_state: dict) -> EquationSpec: ...
def canonicalize(spec: EquationSpec) -> DifferentialEquationIR: ...
def classify(ir: DifferentialEquationIR) -> list[str]: ...
def generate_candidates(ir: DifferentialEquationIR, registry: list[PhysicalModel]) -> list[CandidateMapping]: ...
def verify_mapping(ir: DifferentialEquationIR, candidate: CandidateMapping) -> CandidateMapping: ...
def rank_candidates(candidates: list[CandidateMapping], policy: dict, seed: int | None) -> list[CandidateMapping]: ...
def synthesize_parameters(candidate: CandidateMapping) -> CandidateMapping: ...
def check_feasibility(candidate: CandidateMapping) -> CandidateMapping: ...
def render_description(output: ExperimentOutput) -> str: ...
def compile_equation(raw_text: str | None, builder_state: dict | None, config: dict) -> ExperimentOutput: ...
```

## 9. HTTP API contract (Vercel Python Serverless Function, `api/index.py`)

This is a thin wrapper around §8 — no logic lives here, only request parsing, calling into `src/api/`, and JSON serialization. The web frontend (Agent D) and any local testing (curl, Postman) both target this contract.

| Method | Path | Request body | Response body | Notes |
|---|---|---|---|---|
| GET | `/api/health` | — | `{"status": "ok", "compiler_version": str}` | Build this first — proves the deploy pipeline works before real logic exists. |
| POST | `/api/parse` | `{"raw_text": str}` | `EquationSpec` or `{"error": str}` (422) | Lets the frontend live-validate advanced-mode text before full compile. Optional but cheap to add. |
| POST | `/api/compile` | `{"raw_text": str \| null, "builder_state": dict \| null, "config": dict}` | `ExperimentOutput` or `{"error": str}` (422/500) | Exactly one of `raw_text` / `builder_state` should be non-null. |
| GET | `/api/models` | — | `{"models": [{"model_id": str, "display_name": str, "domain": str}, ...]}` | Summary list for the frontend, not full `PhysicalModel` objects. |

- **CORS:** not needed if frontend and backend share the same Vercel domain via `vercel.json` rewrites (same-origin). If the backend is ever split off to Render/Railway/Fly.io (see PROJECT_PLAN.md §5 fallback), add explicit CORS headers for the Vercel frontend's origin.
- **Timeouts:** every endpoint must return well within Vercel's Hobby-tier 10s function timeout. `/api/compile` is the one to watch — bound registry search cost (PROJECT_PLAN.md §1.8).
- **Statelessness:** no endpoint may rely on in-memory state surviving between requests. Each call to `/api/compile` re-derives everything from its input.

Every function in §8 must remain independently unit-testable outside the HTTP layer — this is what lets Phase 1's four tracks run without waiting on each other, and what lets the CLI reuse the exact same logic as the web app.
