"""
symbolic.engine — SymPy adapter (PROJECT_PLAN.md §1.1, §2).

Owner: Agent A.

Consumes: nothing schema-shaped yet at this layer (internal SymPy Expr
objects, canonical-form strings).
Produces: canonicalized SymPy expressions + deterministic string
serialization used by canonical.DifferentialEquationIR.canonical_form and
.equivalence_hash (INTERFACE_CONTRACTS.md §2).

No logic implemented yet — Phase 0 stub only.
"""
