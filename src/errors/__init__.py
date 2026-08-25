"""
errors — error / approximation modeling (Phase 3, spec §21) and safety
boundary checks (spec §30).

Owner: Agent A.

Consumes: CandidateMapping (INTERFACE_CONTRACTS.md §4) and the matched
PhysicalModel's `approximation_model` / `error_model` fields
(INTERFACE_CONTRACTS.md §3).
Produces: populated `error_model` context feeding into ExperimentOutput's
`warnings` list (INTERFACE_CONTRACTS.md §5).

Not started — Phase 3 dependency.
"""
