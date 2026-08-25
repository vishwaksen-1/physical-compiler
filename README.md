# Deterministic DiffEq → Physical Experiment Compiler

Status: **Phase 0 — deploy-pipeline scaffold only.** No compiler logic
exists yet. See `docs/PROJECT_PLAN.md` for the full plan and
`docs/INTERFACE_CONTRACTS.md` for the frozen schemas everything downstream
builds against. Session-by-session progress is logged in `docs/STATUS.md`.

## What exists right now

- `api/index.py` — a FastAPI app with exactly one route, `GET /api/health`.
- `web/index.html` — calls `/api/health` and prints the result. Nothing else.
- `vercel.json` — routes `/api/*` to the Python function, everything else
  to `web/`.
- Empty, docstring-only stubs under `src/` for every module in the planned
  architecture, each stating which `INTERFACE_CONTRACTS.md` schema it will
  produce/consume once implemented.
- `data/ranking_policy.yaml` — frozen ranking policy (§7 of the contracts).
- `pytest.ini` + `tests/conftest.py` — pins `PYTHONHASHSEED=0` for
  deterministic test runs (see the conftest docstring for why).

## Running the smoke test locally

```bash
pip install -r requirements.txt
uvicorn api.index:app --reload
# then open web/index.html directly, or serve web/ with any static server
```

## Deploying

```bash
vercel deploy
```

Confirm `<preview-url>/api/health` returns
`{"status": "ok", "compiler_version": "0.0.1"}`, then record the URL in
`docs/STATUS.md`. That's the Phase 0 definition of done — after that, the
four parallel agent tracks (Phase 1) can be kicked off.
