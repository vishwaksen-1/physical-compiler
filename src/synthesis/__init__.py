"""
synthesis — candidate generation, parameter synthesis, ranking (Phase 2).

Owner: Agent A + Agent B jointly (per PROJECT_PLAN.md §3); implemented in
this session against the real Agent A (symbolic/canonical/classifier) and
Agent B (physics registry) code already in the repo.

Consumes: DifferentialEquationIR (INTERFACE_CONTRACTS.md §2), the
PhysicalModel registry (INTERFACE_CONTRACTS.md §3), and
`data/ranking_policy.yaml` (INTERFACE_CONTRACTS.md §7).
Produces: list[CandidateMapping] (INTERFACE_CONTRACTS.md §4), ranked.

Implements INTERFACE_CONTRACTS.md §8:
- `generate_candidates(ir, registry) -> list[CandidateMapping]`
- `rank_candidates(candidates, policy, seed) -> list[CandidateMapping]`
- `synthesize_parameters(candidate) -> CandidateMapping`

Structural coefficient extraction (matching a model's shape against the
ir's) is shared with src/verification/ and lives in
src/synthesis/ode_matching.py — see that module for the linear-ODE-family
scope note and src/synthesis/candidate.py for the CandidateMapping
dataclass (neither existed before this Phase 2 session).

------------------------------------------------------------------------
DESIGN NOTE — splitting work between generate_candidates() and
synthesize_parameters(), logged here (and in docs/STATUS.md) because the
frozen signature `synthesize_parameters(candidate: CandidateMapping) ->
CandidateMapping` takes *only* a candidate — no ir, no model, no equation
system. That means it cannot re-derive "what coefficients am I matching
against" from scratch. So the split implemented here is:
  - generate_candidates() does the real work: filters compatible models,
    extracts both sides' per-derivative-order coefficients, solves the
    resulting (generally underdetermined-by-one) linear system for the
    model's parameters, and returns a CandidateMapping with
    `parameter_values` already populated with the raw solved/anchored
    numbers.
  - synthesize_parameters(candidate) is a narrower, genuinely
    candidate-only-input refinement pass: it looks the model back up via
    `candidate.model_id` and clamps any parameter that landed outside
    `parameter_constraints` back into range, logging the adjustment in
    `candidate.assumptions`. Idempotent — calling it twice is a no-op the
    second time.

THE UNDERDETERMINED-BY-ONE PATTERN: every registered model has exactly one
more free parameter than there are coefficient-matching equations (order
equations for an order-`n` ODE, but `n+1` parameters), *except*
newtons_cooling, whose leading-order coefficient is hardwired to 1 in the
model definition rather than being a free parameter. That extra degree of
freedom is physically real (e.g. m, c, k can all be scaled by the same
factor without changing the equation's shape — y'' + 2y' + 5y = 0 doesn't
pin down an absolute mass, only the ratios c/m and k/m). Rather than trust
`sympy.solve()`'s own (undocumented, though empirically hash-seed-stable
in the cases tested) choice of which symbol to leave free in an
underdetermined system, this module explicitly anchors the excess symbols
itself, in a fixed deterministic order (sorted by symbol name), using a
constraint-derived default value — see ode_matching.anchor_value(). This
is logged here as the "scaled" transformation_type case.
"""
from __future__ import annotations

from src.canonical.ir import DifferentialEquationIR
from src.physics.models.registry import PhysicalModel
from src.symbolic import engine as sym
from src.synthesis import ode_matching as odm
from src.synthesis.candidate import CandidateMapping, Score, TransformationTrace


def generate_candidates(ir: DifferentialEquationIR, registry: list) -> list:
    """INTERFACE_CONTRACTS.md §8: generate_candidates(ir, registry) -> list[CandidateMapping]."""
    required_tag = odm.required_class_tag(ir)
    if required_tag is None:
        return []

    t_sym, y_applied, user_coeffs, forcing_expr_user, leftover = odm.user_ode_structure(ir)
    if not sym.is_zero(leftover):
        return []  # ir has structure this matcher doesn't understand -- no candidates, not a crash

    leading_user = user_coeffs[ir.order]
    if sym.is_zero(leading_user) or sym.has_free_symbols(leading_user):
        return []  # degenerate (zero leading coefficient) or symbolic (not a concrete equation)

    norm_user = {n: (c / leading_user) for n, c in user_coeffs.items() if n < ir.order}

    candidates = []
    counter = 0
    for model in registry:
        if required_tag not in model.equation_class_tags:
            continue
        try:
            candidate = _build_candidate_for_model(model, ir, norm_user, counter)
        except (ValueError, ZeroDivisionError):
            continue  # structurally incompatible or unsolvable -- skip, don't crash the whole request
        if candidate is None:
            continue
        counter += 1
        candidates.append(candidate)

    return candidates


def _build_candidate_for_model(model: PhysicalModel, ir: DifferentialEquationIR, norm_user: dict, index: int):
    structure = odm.model_structure(model)
    max_order = structure["max_order"]
    if max_order != ir.order:
        return None  # class tag matched but structural order didn't -- shouldn't happen, defensive

    leading_model = structure["coeffs"][max_order]
    param_symbols = structure["param_symbols"]

    # Normalized coefficient-matching equations for n = 0 .. order-1:
    #   coeffs[n]/leading_model - norm_user[n] == 0
    equations = [(structure["coeffs"][n] / leading_model) - norm_user[n] for n in range(max_order)]

    class_tag_family = [t for t in model.equation_class_tags if t.endswith("_ode")]
    steps = [
        f"Matched equation class tag '{class_tag_family[0] if class_tag_family else model.equation_class_tags}'.",
        "Normalized both the user's equation and the model's governing equation "
        "by their own leading-order coefficient.",
    ]

    n_unknowns = len(param_symbols)
    n_equations = len(equations)
    excess = n_unknowns - n_equations

    assumptions = []
    anchor_map = {}
    if excess > 0:
        # Deterministic policy: anchor the last `excess` symbols in sorted-name
        # order (see module docstring) rather than trusting solve()'s implicit choice.
        anchor_symbols = param_symbols[n_unknowns - excess:]
        solve_for = param_symbols[: n_unknowns - excess]
        for psym in anchor_symbols:
            name = sym.symbol_name(psym)
            value, reason = odm.anchor_value(model, name)
            anchor_map[psym] = value
            steps.append(
                f"Anchored {name} = {value:.6g} ({reason}) -- absolute scale isn't fixed by equation shape alone."
            )
            assumptions.append(f"{name} fixed to {value:.6g} ({reason})")
        equations = [sym.substitute(eq, anchor_map) for eq in equations]
        transformation_type = "scaled"
    else:
        solve_for = param_symbols
        transformation_type = "direct"

    solutions = sym.solve_system(equations, solve_for) if solve_for else [{}]
    if not solutions:
        return None

    solution = solutions[0]
    # Any solve_for symbol absent from the solution dict is itself still free
    # (can happen if the equations don't actually constrain it) -- anchor it too.
    for psym in solve_for:
        if psym not in solution:
            name = sym.symbol_name(psym)
            value, reason = odm.anchor_value(model, name)
            solution[psym] = value
            steps.append(f"Anchored {name} = {value:.6g} ({reason}) -- left free by the coefficient match.")
            assumptions.append(f"{name} fixed to {value:.6g} ({reason})")
            transformation_type = "scaled"

    full_map = dict(anchor_map)
    full_map.update(solution)

    parameter_values = {}
    for psym in param_symbols:
        raw_val = full_map[psym]
        if isinstance(raw_val, (int, float)):
            val_expr = raw_val
        else:
            val_expr = sym.substitute(raw_val, full_map) if sym.has_free_symbols(raw_val) else raw_val
        name = sym.symbol_name(psym)
        parameter_values[name] = sym.to_float(val_expr) if not isinstance(val_expr, (int, float)) else float(val_expr)
        steps.append(f"Solved {name} = {parameter_values[name]:.6g}.")

    steps.append(
        f"Forcing function {structure['forcing_applied']!s} left free -- "
        "matches the user's forcing term directly, since the model's forcing is an unconstrained applied function."
    )

    candidate_id = f"{model.model_id}_{index}"
    return CandidateMapping(
        candidate_id=candidate_id,
        model_id=model.model_id,
        parameter_values=parameter_values,
        verification_status="APPROXIMATE",  # verify_mapping() sets the real status
        residual_expr="",
        assumptions=assumptions,
        # simplicity: a "direct" match (every parameter pinned by the coefficient
        # system alone) is simpler than a "scaled" one (needed an anchored
        # free-scale assumption) -- see module docstring's underdetermined-by-one note.
        score=Score(simplicity=1.0 if transformation_type == "direct" else 0.7),
        transformation_trace=TransformationTrace(
            original_problem=ir.canonical_form,
            transformed_problem=str(model.governing_equation),
            transformation_type=transformation_type,
            symbolic_derivation_steps=steps,
            equivalence_status="exact",
        ),
    )


def synthesize_parameters(candidate: CandidateMapping) -> CandidateMapping:
    """INTERFACE_CONTRACTS.md §8: synthesize_parameters(candidate) -> CandidateMapping.

    See module docstring for why this is a narrower refinement pass rather
    than the primary solver (that's generate_candidates' job, since only it
    has access to the ir). Idempotent: clamps any parameter_values entry
    that falls outside the model's parameter_constraints back into range,
    logging the adjustment; a candidate already within range is returned
    with the same values.
    """
    from src.physics.models.registry import get_model

    model = get_model(candidate.model_id)
    adjusted_values = dict(candidate.parameter_values)
    new_assumptions = list(candidate.assumptions)

    for name, value in candidate.parameter_values.items():
        constraint = model.parameter_constraints.get(name)
        if not constraint:
            continue
        lo, hi = constraint.get("min"), constraint.get("max")
        clamped = value
        if lo is not None and clamped < lo:
            clamped = lo
        if hi is not None and clamped > hi:
            clamped = hi
        if clamped != value:
            adjusted_values[name] = clamped
            new_assumptions.append(
                f"{name} clamped from {value:.6g} to {clamped:.6g} to satisfy parameter_constraints"
            )

    return CandidateMapping(
        candidate_id=candidate.candidate_id,
        model_id=candidate.model_id,
        parameter_values=adjusted_values,
        verification_status=candidate.verification_status,
        residual_expr=candidate.residual_expr,
        assumptions=new_assumptions,
        score=candidate.score,
        transformation_trace=candidate.transformation_trace,
    )


def rank_candidates(candidates: list, policy: dict, seed) -> list:
    """INTERFACE_CONTRACTS.md §8 + §6: rank_candidates(candidates, policy, seed) -> list[CandidateMapping].

    Computes score.total from policy['weights'] for every candidate, then:
      - seed is None (deterministic_top_rank, INTERFACE_CONTRACTS.md §6): stable
        sort by total score descending; ties broken by original list order,
        which callers must pass in registry insertion order
        (tie_break: "registry_insertion_order" -- never re-sorted by name/id/etc).
      - seed is an int (seeded_random): deterministically shuffle with that
        seed first (via Python's own `random.Random(seed)`, reproducible
        given the same seed every time), then stable-sort by score -- so a
        tied group's *order* varies by seed, but the top score still wins.
    """
    weights = policy.get("weights", {})
    w_exact = weights.get("exactness", 0.0)
    w_feas = weights.get("feasibility", 0.0)
    w_simple = weights.get("simplicity", 0.0)

    for c in candidates:
        c.score.total = (
            w_exact * c.score.exactness + w_feas * c.score.feasibility + w_simple * c.score.simplicity
        )

    ordered = list(candidates)
    if seed is not None:
        import random

        rng = random.Random(seed)
        rng.shuffle(ordered)

    return sorted(ordered, key=lambda c: c.score.total, reverse=True)
