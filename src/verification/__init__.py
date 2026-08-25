"""
verification — symbolic substitution + residual comparison (Phase 2).

Owner: Agent A.

Consumes: DifferentialEquationIR (INTERFACE_CONTRACTS.md §2) and a
CandidateMapping (INTERFACE_CONTRACTS.md §4) with parameter_values filled in.
Produces: an updated CandidateMapping with `verification_status`
("EXACT" | "APPROXIMATE" | "FAILED") and `residual_expr` set.

Implements INTERFACE_CONTRACTS.md §8:
`verify_mapping(ir: DifferentialEquationIR, candidate: CandidateMapping) ->
CandidateMapping`.

Not started — Phase 2 dependency (needs A's canonical/classifier and B's
registry to land first per PROJECT_PLAN.md Phase 2).
"""
