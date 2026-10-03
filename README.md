# Deterministic DiffEq → Physical Experiment Compiler

Status: **Phase 2 — candidate generation, verification, and the
integration layer are real and tested (103 tests passing).** See
`docs/PROJECT_PLAN.md` for the full plan, `docs/INTERFACE_CONTRACTS.md`
for the frozen schemas everything is built against, and `docs/STATUS.md`
for the session-by-session log (including this session's Vercel routing
fix — see that file before assuming anything about the live deployment's
current state).

## What exists right now

- `api/index.py` — a FastAPI app with `GET /api/health`, `GET /api/models`,
  `POST /api/parse`, and `POST /api/compile`, all wired to real logic in
  `src/api/` (not mocks).
- `pyproject.toml` — declares `api.index:app` as Vercel's zero-config
  FastAPI entrypoint. Required for anything beyond the bare `/api` path to
  route correctly — see `docs/STATUS.md`'s "Vercel routing fix" entry if
  you're wondering why this exists.
- `web/` — a browser equation-builder + results viewer. `app.js` is an ES
  module; `index.html` loads it with `<script type="module">`.
- `scripts/sync_static.py` — copies `web/` to Vercel's generated `public/`
  directory during deploy (`vercel.json`'s `buildCommand`).
- `src/` — real implementations for symbolic canonicalization,
  classification, the physical-model registry (5 models), the text parser,
  candidate generation/verification, and the `compile_equation()`
  integration layer. `src/rendering/` (Agent C's deterministic-NLG,
  Phase 3) is still a docstring-only stub; `experiment_description` is
  currently filled by a clearly-labeled placeholder in `src/api/`.
- `data/ranking_policy.yaml` — frozen ranking policy (§7 of the contracts).
- `pytest.ini` + `tests/conftest.py` — pins `PYTHONHASHSEED=0` for
  deterministic test runs (see the conftest docstring for why).

## Local CLI

You can compile equations directly from the terminal without running the web server using `cli/physcompile.py`:

```bash
# Classical theme (default)
python3 cli/physcompile.py "y'' + 2y' + 5y = 0"

# Celestial theme (God Mode)
python3 cli/physcompile.py "y'' + 0.05y' + 100y = 0" --theme celestial

# Quantum theme (Antman Mode)
python3 cli/physcompile.py "y'' + 100y' + 1e9y = 0" --theme quantum
```

## Running the web server locally

```bash
pip install -r requirements.txt
uvicorn api.index:app --reload
```

For the frontend, serve `web/` over HTTP rather than opening
`index.html` directly (`file://`) — `app.js` is an ES module, and browsers
block module imports from the `file://` scheme:

```bash
cd web && python -m http.server 8000
# then open http://localhost:8000
```

## Running the tests

```bash
PYTHONHASHSEED=0 pytest -q
```

Frontend smoke tests (`tests/frontend/`, executing the real `web/app.js`
against a real DOM via jsdom) are optional and skip automatically if you
haven't run `npm install` — do that once to enable them:

```bash
npm install
PYTHONHASHSEED=0 pytest -q   # now also runs tests/unit/frontend/test_frontend_smoke.py
# or directly:
node tests/frontend/run.mjs
```

## Deploying

```bash
vercel deploy
```

Confirm **all four** endpoints on the live preview URL, not just
`/api/health` — `docs/STATUS.md` notes that an earlier session's "smoke
test" of `/api/health` was likely asserted rather than actually run, so
treat the whole deployment as unverified until someone checks it for real:

```bash
curl <preview-url>/api/health
curl <preview-url>/api/models
curl -X POST <preview-url>/api/parse -H "Content-Type: application/json" \
  -d "{\"raw_text\": \"y'' + 2y' + 5y = 0\"}"
curl -X POST <preview-url>/api/compile -H "Content-Type: application/json" \
  -d "{\"raw_text\": \"y'' + 2y' + 5y = 0\", \"builder_state\": null, \"config\": {}}"
```

Then record the URL and results in `docs/STATUS.md`.
