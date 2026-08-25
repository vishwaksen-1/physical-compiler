"""
synthesis — candidate generation, parameter synthesis, scaling (Phase 2).

Owner: Agent A + Agent B jointly.

Consumes: DifferentialEquationIR (INTERFACE_CONTRACTS.md §2), the
PhysicalModel registry (INTERFACE_CONTRACTS.md §3), and
`data/ranking_policy.yaml` (INTERFACE_CONTRACTS.md §7).
Produces: list[CandidateMapping] (INTERFACE_CONTRACTS.md §4), ranked.

Implements INTERFACE_CONTRACTS.md §8:
- `generate_candidates(ir, registry) -> list[CandidateMapping]`
- `rank_candidates(candidates, policy, seed) -> list[CandidateMapping]`
- `synthesize_parameters(candidate) -> CandidateMapping`

Determinism / seed policy: INTERFACE_CONTRACTS.md §6. Tie-break must use
stable registry insertion order — never set/dict iteration order.

Not started — Phase 2 dependency.
"""
