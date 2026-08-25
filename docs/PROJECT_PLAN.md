# Deterministic DiffEq → Physical Experiment Compiler — Project Plan

## 0. Roles

- **Origin** (this conversation) — architecture, contracts, phase planning, unblocking design questions. Also a free account — use it for design/review, not bulk code generation.
- **Agent A** — Symbolic core: SymPy adapter, canonical IR, classifier. Later: verification engine, error/safety modeling.
- **Agent B** — Physical model registry ("the map"): governing equations, parameter constraints, dimensional data. Later: registry breadth expansion.
- **Agent C** — Input layer: advanced-mode grammar/parser, EquationSpec validation shared by web frontend and parser. Later: deterministic NLG rendering.
- **Agent D** — Web frontend + deployment: browser-based equation builder, FastAPI backend wiring, Vercel deployment config. Later: wires the live frontend to the real API and owns the deploy pipeline.

Each agent works from their own free Claude account. No agent has memory across sessions or repo access — everything crosses the gap via files in the repo and the shared docs below. Treat every session as if the agent has amnesia the moment it ends.

## 1. Key decisions

1. **Python 3.11+, SymPy for symbolic math**, wrapped by a single adapter module (`src/symbolic/engine.py`) — no other module imports `sympy` directly.
2. **Determinism gotcha:** pin the exact SymPy version, set `PYTHONHASHSEED=0` in test/CI, and always serialize canonical forms via a sorted printer — never rely on default `str()` ordering.
3. **Dual input path, one contract.** The web equation-builder (buttons/forms) and the advanced-mode text parser both produce the exact same `EquationSpec` object. This is the seam that lets Agent C and Agent D work in true parallel.
4. **Determinism vs. variety — resolved, not in conflict.** Default: deterministic top-ranked candidate via a fixed ranking policy. A "Surprise me" mode draws an explicit seed, records it in `config.candidate_seed` in the response JSON, and re-running with that seed reproduces the exact same result.
5. **Registry as data-driven Python registration modules**, not pure YAML — governing equations need real SymPy expressions. Non-symbolic metadata (units, safety limits, costs) lives in companion YAML.
6. **Breadth target:** aim wide, but a physical model only "counts" once it passes verification.
7. **Demo safety net:** checkpoint the system so it's demo-able after Phase 3 with just the ODE cases (mass-spring-damper + RLC) fully working end-to-end through the deployed web app, before PDE breadth is finished.
8. **Deployment target: Vercel, single repo, single project.**
   - Backend: the `src/` Python package wrapped in a FastAPI app at `api/index.py`, deployed as a Vercel Python Serverless Function (zero extra adapter — Vercel runs FastAPI apps directly).
   - Frontend: a browser-based equation builder (plain HTML/CSS/JS, or a lightweight React/Vite app) served as static assets from the same project.
   - `vercel.json` routes `/api/*` to the Python function and everything else to the static frontend.
   - **Free-tier constraints that shape design:** ~10s execution timeout on Python functions (Hobby plan), 500MB bundle limit (a non-issue for sympy+fastapi). Candidate generation/verification must stay comfortably under the timeout — bound registry search, avoid expensive `simplify()` calls on large PDE expressions.
   - **Fallback if timeout bites:** move the FastAPI backend alone to Render/Railway/Fly.io free tier, keep the frontend on Vercel, add CORS headers. Documented so it's a known escape hatch, not a scramble.
   - **Side benefit:** every git push gets an automatic Vercel preview URL. Useful for your parallel-agent workflow — agents/teammates can sanity-check against a live deployment without everyone running the stack locally.
   - pygame is dropped entirely — it couldn't have run in a serverless backend anyway (no display), so this isn't a compromise, it's fixing an approach that wouldn't have deployed.

## 2. Repo structure

```
repo/
  api/
    index.py            # D — FastAPI app entrypoint; Vercel's Python Serverless Function.
                         # Thin HTTP wrapper around src/api/compile_equation() and friends.
  src/
    symbolic/            # A — SymPy adapter, canonicalization, equivalence testing
    canonical/            # A — DifferentialEquation IR construction & (de)serialization
    classifier/            # A — order / linearity / ODE-vs-PDE / nonlinearity detection
    verification/           # A (phase 2) — symbolic substitution + residual comparison
    errors/                  # A (phase 3) — error / approximation modeling
    physics/
      models/                # B — one file per physical model, @register_model decorated
      constraints/            # B — feasibility + safety limit checks per model
    parser/                    # C — grammar, lexer, AST → EquationSpec
    rendering/                  # C (phase 3) — deterministic NLG templates + renderer
    synthesis/                   # A+B (phase 2) — candidate generation, parameter synthesis, scaling
    api/                          # integration layer — compile_equation() and friends (pure Python, no HTTP)
  cli/                    # D — `physcompile` CLI for local/dev use, calls src/api/ directly (not deployed)
  web/                    # D — browser frontend: equation-builder UI + results viewer, calls /api/* over fetch
    index.html
    builder.js
    viewer.js
    styles.css
  data/
    physical_models/      # B — YAML metadata: units, safety limits, descriptions, costs
    ranking_policy.yaml    # frozen in Phase 0
  tests/
    unit/                  # mirrors src/ tree
    integration/            # end-to-end worked examples
    fixtures/                # canonical test equations from spec §31
  docs/
    PROJECT_PLAN.md
    INTERFACE_CONTRACTS.md
    KICKOFF_PROMPTS.md
    STATUS.md              # living log — see §4
  scripts/
    demo.py
  requirements.txt         # root-level — Vercel reads this to build the Python function
  vercel.json               # routes /api/* to api/index.py, everything else to web/
  README.md
```

`requirements.txt` (pin exact versions — matters for determinism, verify latest stable at implementation time):
```
sympy==1.12
lark==1.1.9
pyyaml==6.0.1
fastapi==0.109.0
uvicorn==0.27.0     # local dev server only, not required by Vercel itself
pytest==8.0.0
```

`vercel.json` (starting point — confirm current syntax against Vercel's docs at implementation time, this is the kind of config that shifts):
```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/index.py" }
  ]
}
```

## 3. Phased plan

See the phase diagram above. Gray boxes = sequential integration checkpoints everyone waits on; teal boxes = genuinely independent parallel tracks.

### Phase 0 — Foundations (series, one short pass)
Goal: freeze the contracts everything else is built against.
- Repo scaffold matching §2, `requirements.txt`, `vercel.json`, pytest config.
- A minimal `api/index.py` FastAPI app with just `GET /api/health` — proves the deploy pipeline end-to-end before any real logic exists.
- Freeze the schemas in `INTERFACE_CONTRACTS.md` (including the HTTP contract).
- Freeze `ranking_policy.yaml` and the determinism/seed policy (§1.4).
- **Definition of done:** every downstream agent can read `INTERFACE_CONTRACTS.md` and know exactly what shape their inputs/outputs are, AND `vercel deploy` succeeds and `/api/health` responds on the live URL.

### Phase 1 — Parallel build (4 independent tracks)
- **Agent A — Symbolic core.** `symbolic/engine.py`, `canonical/`, `classifier/`. Test against canonicalization-equivalence examples from spec §3.
- **Agent B — Physical model registry.** ≥10 physical model entries (target list below), each verification-ready per `INTERFACE_CONTRACTS.md §3`. Include ≥3 alternative realizations of the 2nd-order-linear-constant-coefficient ODE class.
- **Agent C — Input layer.** Advanced-mode grammar (recommend `lark`) → AST → `EquationSpec`, plus a validator any caller (parser or web frontend) can use to confirm schema conformance.
- **Agent D — Web frontend + deploy scaffolding.** Equation-builder page (order picker, coefficient inputs, forcing-function picker from the fixed list, IC/BC inputs) that constructs a valid `EquationSpec` client-side and POSTs it to a **stubbed** `/api/compile`. Results-viewer page rendering a hardcoded mock `ExperimentOutput`. Extend `api/index.py` with the stub endpoints matching the HTTP contract, returning schema-valid mock data. This proves the whole frontend↔backend wire format before any real logic lands.

Target physical model list for Agent B (Phase 1, expand more in Phase 3):
1. Mass-spring-damper (mechanical, 2nd-order linear ODE)
2. Series RLC circuit (electrical — alt realization of #1's class)
3. Damped torsional pendulum (mechanical rotational — third alt realization)
4. Simple RC circuit (electrical, 1st-order linear ODE)
5. Newton's-law-of-cooling apparatus (thermal — alt realization of #4's class)
6. Driven pendulum, small-angle (mechanical, nonlinear — stretch)
7. RC ladder network (electrical, 1D diffusion PDE approximation)
8. Discretized heat-conduction rod (thermal, 1D diffusion PDE — alt realization)
9. Coupled oscillator / beaded-string chain (mechanical, 1D wave equation)
10. Transmission-line segment (electrical, 1D wave equation — alt realization)
11. Resistor grid (electrical, 2D Laplace/Poisson, steady state)
12. Loaded membrane approximation (mechanical, 2D Poisson — alt realization, stretch)

### Phase 2 — Integration layer (depends on A + B landing)
- Candidate generation, verification (`EXACT`/`APPROXIMATE`/`FAILED` + residual), parameter synthesis, scaling, dimensional analysis, feasibility checks.
- Owner: Agent A continues; Agent B works in parallel on model-specific feasibility functions once the verification harness signature is frozen.
- **Definition of done:** `generate_candidates()` + `verify_mapping()` pass the worked examples in spec §31 for at least mass-spring-damper and RLC, AND complete in well under the 10s Vercel timeout for the full registry.

### Phase 3 — Output layer + real deployment (parallel, once Phase 2's output schema is stable)
- **Agent C** — Deterministic NLG (spec §22).
- **Agent D** — Replace the Phase 1 stub with the real `compile_equation()` call in `api/index.py`; wire the web frontend to real responses; add the "Surprise me" seeded-randomizer button; polish the results viewer (paragraph + JSON toggle); redeploy to Vercel and confirm the live URL works end-to-end for the ODE cases (demo safety net, §1.7).
- **Agent B** — Expand registry breadth (items 6–12 above).
- **Agent A** — Error/approximation modeling (spec §21), safety boundary checks (spec §30).

### Phase 4 — Integration, testing, polish, final deploy (mostly series at the end)
- Full pipeline integration tests, failure-case tests (spec §28).
- README, worked examples, demo script — include the live Vercel URL.
- One agent runs the full suite, fixes glue issues, and does a final production deploy + smoke test against the public URL.

## 4. Free-account workflow protocol

- **`docs/STATUS.md`** — append-only log. Every session ends with: what was built, deviations from frozen contracts, what's left, open questions, and — once deployed — the current preview/production URL so the next session (or a human teammate) can smoke-test live instead of only locally.
- **Session sizing.** Break each track into 2–4 sub-tasks sized to one sitting.
- **Contract changes require a broadcast** via `STATUS.md`, not a silent edit.
- **Commit convention:** `[Agent X][Phase N] <what>`.

## 5. Risk notes

- **Scope creep, not time, is the real risk** — use the Phase 3 demo-safety-net checkpoint to force a working, gradeable thing before chasing more physical models.
- **SymPy determinism** — don't skip `PYTHONHASHSEED` pinning.
- **Schema drift between web frontend and parser** — Agent C's validator exists specifically to catch this early.
- **Vercel Python function timeout (10s, Hobby)** — bound registry search cost; know the Render/Railway/Fly.io fallback path if this becomes real.
- **Statelessness** — Vercel functions are ephemeral; don't design around in-memory caching between requests or background jobs. `compile_equation()` should be a pure function per call.
