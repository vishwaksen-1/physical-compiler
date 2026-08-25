"""
physics.models — one file per physical model, each `@register_model`
decorated (PROJECT_PLAN.md §2).

Owner: Agent B.

Produces: PhysicalModel entries (INTERFACE_CONTRACTS.md §3) that populate
the registry passed into
`generate_candidates(ir: DifferentialEquationIR, registry: list[PhysicalModel])`
(INTERFACE_CONTRACTS.md §8).

Target list (Phase 1, PROJECT_PLAN.md §3): mass-spring-damper, series RLC,
damped torsional pendulum, RC circuit, Newton's-law-of-cooling apparatus,
driven pendulum (stretch), RC ladder network, discretized heat-conduction
rod, coupled oscillator chain, transmission-line segment, resistor grid,
loaded membrane (stretch).

No models registered yet — Phase 0 stub only. `@register_model` decorator
itself doesn't exist yet either; Agent B defines it here in Phase 1.
"""
