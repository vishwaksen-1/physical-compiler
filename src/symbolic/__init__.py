"""
symbolic — the ONLY module in this repo permitted to `import sympy`
(PROJECT_PLAN.md §1.1). Every other module talks to SymPy through here.

Owner: Agent A.

Consumes: raw SymPy-expressible equation text/structures fed in by callers
(canonical/, parser/).
Produces: no INTERFACE_CONTRACTS.md schema directly — this is infrastructure
underneath canonical.DifferentialEquationIR construction. `engine.py` should
expose canonicalization/equivalence-testing primitives that canonical/ calls.

Determinism note (PROJECT_PLAN.md §1.2): always serialize via a sorted
printer, never bare `str()` on a SymPy expression.
"""
