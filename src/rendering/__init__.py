"""
rendering — deterministic NLG templates + renderer (Phase 3, spec §22).

Owner: Agent C.

Consumes: ExperimentOutput (INTERFACE_CONTRACTS.md §5) minus its own
`experiment_description` field.
Produces: `experiment_description: str` for ExperimentOutput.

Implements INTERFACE_CONTRACTS.md §8:
`render_description(output: ExperimentOutput) -> str`.

Not started — Phase 3 dependency.
"""
