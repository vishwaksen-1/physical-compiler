"""
canonical — DifferentialEquation IR construction & (de)serialization.

Owner: Agent A.

Consumes: EquationSpec (INTERFACE_CONTRACTS.md §1), produced either by
src/parser/ (text input) or the web builder (via src/api/).
Produces: DifferentialEquationIR (INTERFACE_CONTRACTS.md §2).

Implements INTERFACE_CONTRACTS.md §8: `canonicalize(spec: EquationSpec) ->
DifferentialEquationIR`.

No logic implemented yet — Phase 0 stub only.
"""
