"""
physics.constraints — feasibility + safety limit checks per model.

Owner: Agent B (Phase 2, in parallel with Agent A once the verification
harness signature is frozen — PROJECT_PLAN.md Phase 2).

Consumes: a CandidateMapping (INTERFACE_CONTRACTS.md §4) plus the matched
PhysicalModel's `parameter_constraints`, `dimensional_constraints`,
`construction_requirements`, and `safety_notes` (INTERFACE_CONTRACTS.md §3).
Produces: an updated CandidateMapping with `score.feasibility` populated.

Implements INTERFACE_CONTRACTS.md §8:
`check_feasibility(candidate: CandidateMapping) -> CandidateMapping`.

Not started — Phase 2 dependency.
"""
