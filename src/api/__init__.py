"""
api (src/api/) — integration layer. Pure Python, no HTTP, no FastAPI
imports (that boundary lives in the repo-root `api/index.py` instead —
don't confuse the two `api` directories, see PROJECT_PLAN.md §2).

Owner: shared — this is the seam every other track's functions get wired
together through, per INTERFACE_CONTRACTS.md §8.

Consumes: raw_text and/or builder_state (whichever is non-null) + a config
dict, per INTERFACE_CONTRACTS.md §9's POST /api/compile contract.
Produces: ExperimentOutput (INTERFACE_CONTRACTS.md §5).

Implements INTERFACE_CONTRACTS.md §8's top-level orchestration functions:
- `build_equation_spec_from_web(builder_state: dict) -> EquationSpec`
- `compile_equation(raw_text: str | None, builder_state: dict | None,
   config: dict) -> ExperimentOutput`

Every function here must remain independently unit-testable outside the
HTTP layer (INTERFACE_CONTRACTS.md §9 closing note) — this is what lets
`api/index.py` (FastAPI) and `cli/` both call the exact same logic.

No logic implemented yet — Phase 0 stub only. `compile_equation()` doesn't
exist as a callable yet; Phase 1's Agent D stub endpoints should return
hardcoded mock ExperimentOutput data directly rather than importing from
here until Phase 2/3 wiring.
"""
