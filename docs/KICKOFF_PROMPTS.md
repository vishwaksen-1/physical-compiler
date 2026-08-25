# Kickoff Prompts

**How to use these:** at the start of every session, attach `PROJECT_PLAN.md` and `INTERFACE_CONTRACTS.md`, plus the current `docs/STATUS.md`. Then paste the relevant prompt below. Once Phase 0 is deployed, also paste in the live Vercel preview URL from `STATUS.md` so agents can reference it.

---

## Phase 0 — Foundations (do this first)

```
I'm building a deterministic differential-equation-to-physical-experiment compiler
for a hackathon, deployed as a web app on Vercel (attached: master spec,
PROJECT_PLAN.md, INTERFACE_CONTRACTS.md). Do ONLY the following — don't start
on symbolic math, physics models, or the frontend UI yet:

1. Create the repo scaffold exactly matching PROJECT_PLAN.md §2, including
   api/, src/, web/, cli/, data/, tests/, docs/.
2. Write requirements.txt at the repo root with the exact pinned versions
   listed there (sympy, lark, pyyaml, fastapi, uvicorn, pytest).
3. Write api/index.py as a minimal FastAPI app exposing only
   GET /api/health returning {"status": "ok", "compiler_version": "0.0.1"}.
   This is deliberately the ONLY working endpoint right now — it exists to
   prove the deploy pipeline before any real logic exists.
4. Write vercel.json with a rewrite routing /api/(.*)  to api/index.py and
   everything else to the web/ static directory.
5. Add a minimal web/index.html that just fetches /api/health and displays
   the result — a trivial end-to-end smoke test.
6. Add empty module stubs under src/ with a docstring stating which
   INTERFACE_CONTRACTS.md schema each module produces/consumes.
7. Write data/ranking_policy.yaml exactly as specified in
   INTERFACE_CONTRACTS.md §7.
8. Set up pytest config with PYTHONHASHSEED=0 pinned, explaining briefly
   why (SymPy determinism).
9. Create docs/STATUS.md with a one-line header explaining its append-only
   log convention, and instructions to record the live Vercel URL once
   deployed.

Output everything as actual files. Don't implement real compiler logic yet.
After this, I'll run `vercel deploy` myself and confirm /api/health responds
before assigning the four parallel agent tracks.
```

---

## Phase 1 — Agent A: Symbolic core

```
You are Agent A on a 4-person team building a deterministic diffeq-to-physical-
experiment compiler, deployed as a web app on Vercel (attached: master spec,
PROJECT_PLAN.md, INTERFACE_CONTRACTS.md). The repo scaffold and a working
/api/health endpoint already exist.

Your job this phase, working ONLY in src/symbolic/, src/canonical/, and
src/classifier/:

1. src/symbolic/engine.py — a SymPy adapter. No other module should ever
   import sympy directly. Implement: parsing an EquationSpec into a SymPy
   expression, canonical simplification, symbolic equivalence testing,
   derivative/coefficient extraction. Serialize via sort_key()-ordered args
   before taking srepr — never rely on default str() ordering.
2. src/canonical/ — build the DifferentialEquationIR per
   INTERFACE_CONTRACTS.md §2, including the equivalence_hash.
3. src/classifier/ — order, linearity, ODE-vs-PDE, homogeneity,
   classification_tags.
4. Tests proving equivalent inputs (e.g. x'' + 2x' + x = 0 vs
   x'' = -2x' - x) produce identical canonical_form and equivalence_hash.

Keep an eye on cost: this code will eventually run inside a Vercel
serverless function with a ~10 second timeout, so avoid needlessly
expensive simplify() calls where a cheaper canonicalization path exists.

Do not touch physics models, the parser, or the web frontend. Append a
docs/STATUS.md entry when done. Output real files.
```

---

## Phase 1 — Agent B: Physical model registry

```
You are Agent B on a 4-person team building a deterministic diffeq-to-physical-
experiment compiler, deployed as a web app on Vercel (attached: master spec,
PROJECT_PLAN.md, INTERFACE_CONTRACTS.md). The repo scaffold already exists.

Your job: build the physical model registry in src/physics/models/,
src/physics/constraints/, and data/physical_models/.

Build these first (full target list in PROJECT_PLAN.md §3 Phase 1), each
matching the PhysicalModel schema in INTERFACE_CONTRACTS.md §3 exactly,
with a REAL SymPy expression for governing_equation:

1. Mass-spring-damper (mechanical, 2nd-order linear ODE)
2. Series RLC circuit (electrical — alt realization of #1's class,
   same equation_class_tags, shared alt_realizations_of)
3. Damped torsional pendulum (mechanical rotational — third alt realization)
4. Simple RC circuit (electrical, 1st-order linear ODE)
5. Newton's-law-of-cooling apparatus (thermal — alt realization of #4)

For each: governing equation, parameter_map, realistic parameter_constraints,
dimensional_constraints, measurable/controllable variables,
construction_requirements, safety_notes, minimal approximation_model/
error_model stubs (Agent A deepens these in Phase 3).

Use @register_model decorators. Non-symbolic metadata (constraints, costs,
safety notes) goes in a companion YAML file per model under
data/physical_models/.

Don't touch the symbolic engine, parser, or web frontend. Append a
docs/STATUS.md entry when done. Output real files.
```

---

## Phase 1 — Agent C: Input layer

```
You are Agent C on a 4-person team building a deterministic diffeq-to-physical-
experiment compiler, deployed as a web app on Vercel (attached: master spec,
PROJECT_PLAN.md, INTERFACE_CONTRACTS.md). The repo scaffold already exists.

Your job, working in src/parser/:

1. Design a grammar (use `lark`, not regex/string-matching) for an
   advanced-mode text syntax: ASCII (x'', dx/dt, d2x/dt2, standard
   arithmetic, sin/cos/step/impulse as named functions), optionally
   Unicode (ẍ, ∂²u/∂x²).
2. Build lexer/parser/AST → EquationSpec exactly per
   INTERFACE_CONTRACTS.md §1.
3. Write a validator function that checks ANY EquationSpec — regardless
   of whether it came from your parser or from the web frontend's
   equation-builder (built by Agent D, in parallel) — conforms to the
   schema. This is what keeps both input paths honest without you two
   needing to coordinate mid-phase.
4. Tests: parse a handful of equations (2nd-order linear ODE, 1st-order
   linear ODE, one with a sin() forcing term) and confirm output matches
   the schema exactly.

Append a docs/STATUS.md entry when done. Output real files.
```

---

## Phase 1 — Agent D: Web frontend + deploy scaffolding

```
You are Agent D on a 4-person team building a deterministic diffeq-to-physical-
experiment compiler, deployed as a web app on Vercel (attached: master spec,
PROJECT_PLAN.md, INTERFACE_CONTRACTS.md). The repo scaffold and a working
/api/health endpoint already exist (check docs/STATUS.md for the live
preview URL).

Your job this phase, working in web/, api/index.py, and cli/:

1. Build a browser-based equation-builder page in web/ — plain HTML/CSS/JS
   is fine (a lightweight React/Vite setup is also fine if you prefer
   component structure, your call, but keep the build step simple since
   this needs to deploy cleanly on Vercel). It needs: an ODE order picker
   (1st/2nd), coefficient inputs, a forcing-function picker limited to the
   fixed list in EquationSpec.rhs_forcing.type (zero/const/sin/cos/step/
   impulse/polynomial), and initial-condition inputs. On submit, construct
   a valid EquationSpec object client-side exactly matching
   INTERFACE_CONTRACTS.md §1 (input_source: "web_builder"), and POST it to
   /api/compile.
2. Build a results-viewer page that renders an ExperimentOutput
   (INTERFACE_CONTRACTS.md §5) — a readable description plus a raw-JSON
   toggle.
3. Extend api/index.py with STUBBED versions of the endpoints in
   INTERFACE_CONTRACTS.md §9 (/api/parse, /api/compile, /api/models) —
   each returns hardcoded, schema-valid mock data for now. This lets you
   build and deploy the full frontend↔backend wire format before Agents
   A/B/C's real logic lands.
4. Keep cli/ in sync — a thin CLI wrapper that will eventually call the
   same src/api/compile_equation() the HTTP layer calls, for local/dev use.
5. Confirm `vercel deploy` still succeeds and the live preview URL serves
   the working stubbed flow end-to-end (submit equation → see mock result).

You are intentionally NOT calling any real symbolic/physics/parser code
this phase. In Phase 3 you'll swap the stubs for the real
compile_equation() call.

Append a docs/STATUS.md entry when done, including the current preview URL.
Output real files.
```

---

## Phase 2 / 3 / 4 — templates

```
You are Agent [X], continuing work on [project name]. Attached:
PROJECT_PLAN.md, INTERFACE_CONTRACTS.md, and the current docs/STATUS.md
(read it — it tells you what exists, any schema deviations, and the
current live Vercel URL).

This phase your job is: [pull the relevant bullet from PROJECT_PLAN.md §3].

Constraints:
- Don't touch [modules owned by other agents this phase].
- Any endpoint you touch must stay well within Vercel's ~10s function
  timeout — check PROJECT_PLAN.md §1.8 / §5 if unsure.
- If the frozen schema doesn't fit reality, log it in docs/STATUS.md with
  your proposed fix instead of silently changing it.

Definition of done: [pull from PROJECT_PLAN.md §3].

Append a docs/STATUS.md entry when done, including the current preview
URL if you redeployed. Output real files.
```

When you reach Phase 2, paste in whatever Agent A and Agent B actually produced alongside the contracts — integration work needs the real shapes, not just the frozen schema, in case anything drifted.
