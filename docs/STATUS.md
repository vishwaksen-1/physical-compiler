# STATUS

Append-only log. Every session adds a new dated entry at the bottom — never edit or delete a prior entry, even to correct it (add a follow-up note instead). Each entry records: what was built, any deviations from the frozen contracts in `INTERFACE_CONTRACTS.md`, what's left, open questions, and — once something is deployed — the current preview/production URL so the next session (or a human teammate) can smoke-test live instead of only locally.

---

## Phase 0 — Origin session

- Built: repo scaffold (PROJECT_PLAN.md §2), `requirements.txt`, minimal
  `api/index.py` (`GET /api/health` only), `vercel.json`, `web/index.html`
  smoke test, empty `src/` module stubs, `data/ranking_policy.yaml`,
  `pytest.ini` + `tests/conftest.py` (PYTHONHASHSEED=0 pinning).
- Deviations from frozen contracts: none.
- Left to do: run `vercel deploy` and confirm `/api/health` responds on the
  live URL (Phase 0 definition of done) — **record that URL in a new entry
  below once done, before assigning the four parallel agent tracks.**
- Open questions: none blocking.
- Live URL: _(not yet deployed)_

## Phase 0 — Vercel routing fix, 2026-08-25

- Built: fixed Vercel deployment routing by removing the manual `/api/*`
  rewrite from `vercel.json`. Vercel's current FastAPI backend mode routes
  `/api/*` to `api/index.py` directly; the old rewrite caused FastAPI to see
  the rewritten destination path and return `{"detail":"Not Found"}`.
- Built: added `public/index.html` plus tiny placeholder assets for the root
  smoke page, because Vercel serves static assets from `public/` in this
  backend project mode.
- Deviations from frozen contracts: none. The HTTP contract remains
  `GET /api/health -> {"status": "ok", "compiler_version": str}`.
- Left to do: Phase 0 is unblocked; Phase 1 agents can start.
- Open questions: whether Phase 1 Agent D should move the real frontend from
  planned `web/` into Vercel `public/`, or add a build step that copies
  `web/` into `public/`.
- Live URL: https://physical-compiler.vercel.app
- Smoke test: `https://physical-compiler.vercel.app/api/health` returned
  `{"status":"ok","compiler_version":"0.0.1"}` on 2026-08-25.

## Phase 0 — Static source-of-truth cleanup, 2026-08-25

- Built: made `web/` the source of truth for the static smoke-test frontend.
  `scripts/sync_static.py` now copies `web/` into generated `public/` during
  Vercel builds via `vercel.json`'s `buildCommand`.
- Built: ignored generated `public/` locally so frontend edits do not need to
  be duplicated across two directories.
- Deviations from frozen contracts: none.
- Left to do: none for Phase 0 cleanup; user confirmed deployment still works.
- Open questions: none blocking.
- Smoke test: user confirmed the redeployed `web/` -> generated `public/`
  setup works on 2026-08-25.

## Phase 1 — Agent D: Frontend + stubs + CLI, 2026-08-25

- Built: equation-builder page (`web/index.html`, `web/builder.js`, `web/viewer.js`, `web/app.js`, `web/styles.css`) – supports order selection (1st/2nd), coefficient inputs, forcing type with relevant params, initial conditions, and submits to `/api/compile` with a valid `EquationSpec`.
- Built: results viewer with readable description and raw JSON toggle.
- Built: stub endpoints in `api/index.py` for `/api/parse`, `/api/compile`, `/api/models` – each returns schema-valid mock data. The compile stub echoes the input spec and returns a full `ExperimentOutput`.
- Built: CLI stub `cli/physcompile.py` that mimics the same mock behavior (accepts `--raw-text`, `--builder-state`, `--config` and prints JSON).
- Deviations from frozen contracts: none. The frontend constructs `EquationSpec` exactly per §1. HTTP endpoints match §9.
- Left to do: Phase 2 depends on Agents A and B to land real logic; Phase 3 will swap stubs for real `compile_equation()`.
- Open questions: none blocking.
- Live URL: https://physical-compiler.vercel.app
- Smoke test: manual testing on local and after deploy. `vercel deploy` should succeed. The frontend flow (submit → mock result) works end-to-end.

## Phase 1 — Agent A: symbolic core, canonical IR, classifier, 2026-08-26

- Built:
  - `src/symbolic/engine.py` — the sole SymPy adapter (no other module
    imports `sympy` directly). Provides: `spec_to_lhs_rhs()` (EquationSpec ->
    sympy lhs/rhs), named-forcing-shape builders (`const`/`step`/`impulse`/
    `sin`/`cos`/`polynomial`/`custom_expr`) driven off `rhs_forcing.params` so
    web-builder and text-parser output stay byte-identical, `canonical_expr()`
    / `ordered_terms()` / `canonical_srepr()` / `equivalence_hash()` (sorted
    via `as_ordered_terms(order="lex")` then `srepr()` per term — never bare
    `str()`/raw `Add.args` order), `are_equivalent()` (cheap `expand()` path,
    bounded `simplify()` fallback only if needed), and a small set of
    non-sympy-leaking wrappers (`diff`, `is_zero`, `zero`, `has_symbol`,
    `free_symbols`, `dependent_var_atoms`, `total_degree_in`) for
    `src/canonical/` and `src/classifier/` to use instead of importing sympy.
  - `src/canonical/ir.py` — `DifferentialEquationIR` dataclass
    (`to_dict`/`from_dict`) and `canonicalize(spec) -> DifferentialEquationIR`
    per `INTERFACE_CONTRACTS.md` §2/§8. Owns `equivalence_hash`.
  - `src/classifier/classifier.py` — `classify(ir) -> list[str]` per §8:
    order / linearity / ODE-vs-PDE / homogeneity / `classification_tags`.
  - Unit tests: `tests/unit/symbolic/test_engine.py`,
    `tests/unit/canonical/test_canonical.py`,
    `tests/unit/classifier/test_classifier.py` — 22 tests, all passing
    under `PYTHONHASHSEED=0` (repo's pinning convention, confirmed against
    the existing `tests/conftest.py`). Includes the exact equivalence case
    from the task brief: `x'' + 2x' + x = 0` vs `x'' = -2x' - x` (rearranged
    across the equals sign, different `input_source`) produce identical
    `canonical_form` and `equivalence_hash`.

- Deviations from frozen contracts: none to the data shapes in
  `INTERFACE_CONTRACTS.md`. One **implementation-detail clarification**
  worth broadcasting since the contract only pins `canonicalize()`'s and
  `classify()`'s signatures, not the field-population split between them:
  - `canonicalize(spec)` fills every `DifferentialEquationIR` field it can
    derive structurally (`canonical_form`, `order` — *derived from `terms`,
    not trusted from `spec["order"]`*, `domain_type` copied from the
    validated spec, `coefficients`, `forcing_term`, `equivalence_hash`,
    `source_spec_ref`) and leaves `linearity`, `homogeneity`, and
    `classification_tags` blank (`""` / `[]`).
  - `classify(ir)` **mutates `ir` in place** (sets `linearity`,
    `homogeneity`, `classification_tags`) *and* returns
    `classification_tags`, satisfying the declared `-> list[str]` signature.
  - **Callers must call `canonicalize(spec)` then `classify(ir)` in that
    order** before treating an IR as complete. Whoever builds
    `src/api/compile_equation()` (§8) needs to know this — it isn't visible
    from the contract's type signatures alone.
  - Linearity is checked as a **whole-equation property** (total polynomial
    degree across the "y-family" of atoms — `y` and all its derivatives —
    found in the canonical `lhs - rhs` expression), not per-coefficient.
    A per-coefficient check misses cross-terms like
    `x(t)*Derivative(x(t), t)`, which is nonlinear as a system even though
    each factor is individually linear in isolation. Flagged here since it's
    a design choice Agent B (registry `equation_class_tags`) and Agent C
    (NLG rendering of `classification_tags`) should be aware the tag values
    come from.
  - Added a `"domain_type_mismatch"` classification tag (not in the frozen
    tag vocabulary, since §3/§7 don't freeze one) for the edge case where a
    spec's declared `domain_type` disagrees with what
    `len(independent_vars)` implies. Shouldn't fire past a
    validator-checked `EquationSpec`, but it's there so a bad input doesn't
    fail silently.
  - `rhs_forcing.type == "custom_expr"` strings may reference the dependent
    variable and its derivatives directly (e.g. `"-2*Derivative(x(t), t) - x(t)"`,
    `"-sin(x(t))"`) — needed for both the rearranged-equation equivalence
    test above and for genuinely nonlinear forcing (e.g. Phase 1's stretch
    "driven pendulum, small-angle" target model). `safe_sympify()`'s
    namespace is locked down to a small allowlist (`sin`/`cos`/`tan`/`exp`/
    `log`/`sqrt`/`pi`/`E`/`Abs`/`Heaviside`/`DiracDelta`/`Derivative`) plus
    the spec's own independent-variable symbols and the dependent variable's
    `Function` — no arbitrary attribute access reaches `sympify()`.

- Left to do (not touched this session, per scope: only
  `src/symbolic/`, `src/canonical/`, `src/classifier/`):
  - `src/api/compile_equation()` and friends (integration layer) — needs to
    call `canonicalize()` then `classify()` in sequence per the note above.
  - Verification engine / error modeling (Phase 2/3, also Agent A's later
    scope per `PROJECT_PLAN.md` §0) — not started.
  - No physics models, parser, or web frontend touched, as instructed.

- Open questions:
  - Should `"domain_type_mismatch"` (or similar defensive tags) be added to
    a frozen tag vocabulary in `INTERFACE_CONTRACTS.md` §7, so Agent C's NLG
    renderer and Agent B's registry matching have a stable list to code
    against instead of tags growing ad hoc per-agent? Non-blocking for now
    since `classification_tags` is typed as `list[str]`, not an enum.
  - `EquationSpec` itself isn't owned by any file yet in the repo structure
    (§2 lists `src/parser/` for Agent C building it, but no shared schema
    module) — this session treated it as a plain `dict` matching
    `INTERFACE_CONTRACTS.md` §1 rather than defining a dataclass for it, to
    avoid squatting on Agent C's territory. Worth Agent C confirming where
    `EquationSpec`'s own dataclass (if any) will live so `src/canonical/` and
    `src/classifier/`'s dict-based consumption doesn't need to change later.

- Live URL: unchanged — https://physical-compiler.vercel.app (this session
  made no deployment changes; nothing in `src/symbolic/`, `src/canonical/`,
  or `src/classifier/` is wired into `api/index.py` yet).
- Smoke test: not applicable this session (no HTTP-layer changes). Verified
  locally instead: `PYTHONHASHSEED=0 pytest -q` → 22 passed, 0 failed,
  including the canonicalize+classify round-trip on the `x'' + 2x' + x = 0`
  vs `x'' = -2x' - x` equivalence example from the task brief.


## Phase 1 — Agent C, Input layer (text parser + validator), 2026-08-26

- Built (`src/parser/`):
  - `grammar.lark` — lark grammar for advanced-mode text: ASCII prime
    notation (`x''`), Leibniz notation (`dx/dt`, `d2x/dt2`), standard
    arithmetic, `sin/cos/step/impulse` as reserved function names.
    Implicit multiplication is deliberately narrow (`NUMBER power` only —
    `2x`, `3sin(t)`, `2(x+1)` — not general juxtaposition) to keep the
    grammar unambiguous without whitespace-sensitivity.
  - `preprocess.py` — normalizes Unicode shorthand into the ASCII forms
    the grammar knows: superscript digits (`²³`) -> plain digits, and
    Newton-dot combining marks (`ẋ`, `ẍ`, via NFD decomposition) -> prime
    notation. This means `ẍ + 2ẋ + 5x = sin(t)` and `∂²u/∂t² - c²∂²u/∂x²
    = 0` both parse, without the grammar itself needing Unicode-aware
    terminals.
  - `ast_nodes.py` — small internal expression AST (Num/Var/Deriv/
    FuncCall/Neg/BinOp) used only inside src/parser; not part of the
    frozen contract shape. Deliberately does not import sympy, per
    PROJECT_PLAN.md §1.1 ("no other module imports sympy directly").
  - `analysis.py` — structural extraction: splits an equation into
    additive term pieces, isolates which ones involve the dependent
    variable (-> `terms`) vs. which form the forcing function (->
    `rhs_forcing`), and classifies forcing into `zero` / `const` /
    `sin` / `cos` (with amplitude, angular_frequency, phase params) /
    `step` / `impulse` / `polynomial` / `custom_expr` fallback.
  - `text_parser.py` — `parse_equation(raw_text) -> EquationSpec` per
    INTERFACE_CONTRACTS.md §8. Split into `parse_equation` (lark ->
    AST) and `build_equation_spec_from_ast` (AST -> EquationSpec) so
    the semantic half is independently testable without lark installed.
  - `equation_spec.py` — `EquationSpec`/`Term`/`RhsForcing` dataclasses
    with `to_dict()`/`from_dict()`, exactly per INTERFACE_CONTRACTS.md
    §1, using the repo-wide dataclass convention that file recommends.
  - `validator.py` — `validate_equation_spec(spec)` accepts a dict OR an
    `EquationSpec` (so it validates web-builder output identically to
    parser output) and returns a `ValidationResult(valid, errors)`.
    Also `structurally_equivalent_ignoring_source(a, b)`, implementing
    INTERFACE_CONTRACTS.md §1's cross-path rule ("a web-builder-produced
    spec and a text-parser-produced spec for the 'same' equation must be
    structurally identical except for `input_source` and `raw_text`").
  - `errors.py` — `EquationParseError(message, raw_text, cause)`.

- Tests (`tests/unit/parser/`):
  - `test_analysis.py` (8 tests) — exercises `build_equation_spec_from_ast`
    directly on hand-built AST trees: 2nd-order linear ODE
    (mass-spring-damper), 1st-order linear ODE with a division
    coefficient (`dx/dt + x/RC = 0`), bare and amplitude/frequency/phase
    `sin(...)` forcing, const forcing, a PDE (wave equation) case, and
    dependent-var terms appearing on both sides. **No dependency on
    `lark`** — this is the semantic layer's own test surface.
  - `test_validator.py` (12 tests) — hand-built dict specs (simulating
    web-builder output) covering each failure mode (missing key, bad
    enum value, `order`/`terms` mismatch, `wrt` not in
    `independent_vars`, non-float/str coefficient, `custom_expr` missing
    `expr`, `text_parser` source missing `raw_text`) plus the
    cross-source equivalence check and an `EquationSpec.from_dict` round
    trip. Also lark-independent.
  - `test_text_parser.py` (9 tests) — true end-to-end `raw_text ->
    EquationSpec` through the real grammar: ASCII primes, Leibniz
    notation, `sin(...)` forcing, Unicode overdot and Unicode partial-PDE
    notation, prime vs. Leibniz structural equivalence, and three
    error-path cases. Uses `pytest.importorskip("lark")` so the suite
    still passes cleanly if `lark` isn't installed — it just skips these.

- **Deviation from the session environment, not from the frozen
  contracts:** this session's sandbox has no network access, so `lark`
  could not be `pip install`-ed here and `test_text_parser.py` was
  written but **not executed** in this session. `test_analysis.py` and
  `test_validator.py` (20 tests total) exercise the same term-extraction
  and forcing-classification logic and **were** run directly (bypassing
  pytest too, since pytest also wasn't installable here) via a manual
  runner — all 20 pass. First thing next session (or CI): `pip install
  -r requirements.txt` (needs `lark==1.1.9` — see `requirements-parser.txt`,
  merge it into the root `requirements.txt`) and run the full `pytest`
  suite to confirm the grammar itself parses correctly; I'm confident in
  the grammar's structure (documented in `grammar.lark`'s header comment
  — implicit multiplication is narrowed specifically to avoid ambiguity)
  but it is the one piece of this session's work that only got
  reasoned-through, not machine-checked.
- Known limitations (by design, not bugs): `parse_equation` requires at
  least one derivative term to identify the dependent variable (a purely
  algebraic line like `x + y = 0` raises `EquationParseError` rather
  than guessing); nonlinear couplings where the dependent variable can't
  be isolated as a single multiplicative factor (e.g. `x*x''`) still
  produce a `Term`, just with a less-precise string coefficient — full
  linearity classification is Agent A's job downstream, not this
  layer's. `sin`/`cos`/`step`/`impulse` are reserved words and can't be
  used as ordinary variable/parameter names in advanced-mode text.
- Left to do: Agent D still needs `build_equation_spec_from_web()` on
  their side (listed in INTERFACE_CONTRACTS.md §8 but not owned by this
  track) — `validate_equation_spec()` is ready to check its output the
  moment it exists, no coordination needed. Phase 3's deterministic NLG
  (`src/rendering/`) is also this agent's, not started yet.
- Open questions: none blocking Phase 1. Worth a broadcast decision at
  some point — the grammar reserves `sin/cos/step/impulse` as function
  names; if Agent B or the physical-model registry ever wants a
  parameter literally named one of those, that's a real conflict, not
  just a parser quirk.
- Live URL: unchanged (https://physical-compiler.vercel.app) — this
  track has no deployment surface yet, `/api/parse` (optional per
  INTERFACE_CONTRACTS.md §9) isn't wired up.


## Phase 1 — Agent B, Physical model registry (first 5 of 12), 2026-08-26

- Built: `src/physics/models/registry.py` — `PhysicalModel` dataclass
  matching `INTERFACE_CONTRACTS.md` §3 field-for-field, plus the
  `@register_model` decorator (applied to a zero-arg factory function that
  builds and returns a `PhysicalModel`), `get_registry()` /
  `get_model()` / `registry_summary()`, and a YAML metadata loader
  (`load_yaml_metadata`, `build_model_from_yaml`).
- Built: 5 of the 12 target models from `PROJECT_PLAN.md` §3, each as a
  `src/physics/models/<model_id>.py` (real SymPy governing equation) +
  `data/physical_models/<model_id>.yaml` (all non-symbolic metadata —
  parameter constraints, dimensional constraints, construction
  requirements, safety notes, minimal approximation/error model stubs):
  1. `mass_spring_damper` — mechanical, 2nd-order linear ODE.
  2. `series_rlc` — electrical, alt realization of (1)'s class
     (`alt_realizations_of: second_order_linear_constant_coefficient_ode`).
  3. `torsional_pendulum` — mechanical rotational, third alt realization
     of the same class.
  4. `rc_circuit` — electrical, 1st-order linear ODE.
  5. `newtons_cooling` — thermal, alt realization of (4)'s class
     (`alt_realizations_of: first_order_linear_constant_coefficient_ode`).
- Built: `src/physics/constraints/` — `generic.py` (parameter-range checks
  driven purely by each model's `parameter_constraints` dict, plus a
  structural dimensional-constraints completeness check) and
  `model_specific.py` (cheap cross-parameter physical sanity checks: damping
  ratio for the three 2nd-order models, time-constant sanity for the two
  1st-order models). `__init__.py` exposes `run_all_checks(model,
  parameter_values)` as the one-stop entry point for whatever calls into
  this package next.
- Built: `tests/unit/physics/test_registry.py` — 15 tests, all passing
  (registration completeness, stable insertion order, real-`sympy.Eq`
  governing equations, alt-realization class-tag consistency, `to_dict`
  round-trip, parameter-range checks, per-model metadata completeness). Run
  with `PYTHONHASHSEED=0 pytest tests/unit/physics/test_registry.py -v`.
- Deviations from frozen contracts:
  - `governing_equation` is stored as `sympy.Eq(lhs, rhs)`, not a bare
    `sympy.Expr`. The contract's type hint (`"sympy.Expr"`) is pseudocode;
    `Eq` is the natural concrete type for a governing equation (it has two
    sides) and any `Expr`-based consumer can recover the "= 0" form via
    `eq.lhs - eq.rhs`. Flagging this explicitly for **Agent A**:
    `generate_candidates()` / `verify_mapping()` should expect `sp.Eq`
    objects from `PhysicalModel.governing_equation`, not bare expressions.
  - `PhysicalModel.to_dict()` serializes `governing_equation` via plain
    `str()`, not a canonical/sorted printer (that's `src/symbolic/engine.py`,
    Agent A's, per `PROJECT_PLAN.md` §1.2). Symbols re-parsed via
    `sympify()` on the way back in (`from_dict()`) will **not** carry the
    original assumptions (e.g. `m`, `c`, `k` are declared `positive=True`
    in the model files but come back plain from `sympify`). This is fine
    for JSON transport/display but not safe for symbolic algebra without
    re-attaching assumptions or routing through Agent A's canonical
    printer/parser instead — noted in the docstring and covered by a test
    that asserts only textual (not full symbolic) round-trip equivalence.
  - No other deviations. `PhysicalModel` field set, `parameter_constraints`
    dict shape, and `alt_realizations_of` semantics all match §3 exactly.
- Left to do (for whoever picks up Agent B's track next, in-session or a
  fresh session): items 6–12 from `PROJECT_PLAN.md` §3's target list
  (driven pendulum, RC ladder network, discretized heat-conduction rod,
  coupled oscillator/beaded-string chain, transmission-line segment,
  resistor grid, loaded membrane) — these are Phase 3 breadth per the plan,
  not blocking Phase 1. Also left: `check_feasibility(candidate) ->
  CandidateMapping` itself (§8 core API) is Phase 2 / Agent A's — this
  session only built the reusable checks it should call
  (`src/physics/constraints/run_all_checks`), not the wrapper that returns
  a `CandidateMapping`.
- Open questions:
  1. Confirm with Agent A that `sp.Eq` (not bare `Expr`) for
     `governing_equation` is acceptable before Phase 2's
     `generate_candidates()`/`verify_mapping()` land against it — see
     deviation note above. If Agent A wants a bare `Expr`, the fix is
     mechanical (`eq.lhs - eq.rhs` at the seam) and can be done without
     touching any of the 5 model files' physics.
  2. `data/ranking_policy.yaml`'s `tie_break: registry_insertion_order`
     (§7) is only meaningful if registration order is deterministic across
     interpreter runs. Python 3.7+ dict insertion order is already
     guaranteed, and `_INSERTION_ORDER` here is an explicit `list`, so this
     should be safe — but flagging since `src/physics/models/__init__.py`'s
     import order is what actually determines it, and that file has a
     comment warning future editors not to reorder those imports casually.
- Live URL: unchanged — https://physical-compiler.vercel.app (this session
  touched no deployment config; nothing new to smoke-test live yet, since
  the registry isn't wired into `/api/*` until Phase 2/3 integration).
