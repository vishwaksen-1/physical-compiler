"""
Vercel Python Serverless Function entrypoint (INTERFACE_CONTRACTS.md §9).

Phase 0 scope, deliberately: this exposes ONLY `GET /api/health`. That is
the whole point of Phase 0 per PROJECT_PLAN.md — prove the deploy pipeline
(repo -> Vercel build -> live URL -> working Python function) before any
real compiler logic exists to debug alongside deploy problems.

When Phase 1+ lands, this module should stay a THIN wrapper: request
parsing, calling into `src/api/` (see src/api/__init__.py), and JSON
serialization only. No compiler logic belongs here — see
INTERFACE_CONTRACTS.md §9 preamble ("no logic lives here").

Do not add /api/parse, /api/compile, or /api/models yet — those come with
Agent D's Phase 1 stub work (schema-valid mock responses) and then the
Phase 3 real wiring. Adding them early with real logic would violate the
Phase 0 definition of done.
"""

from fastapi import FastAPI

# Bump this string whenever the compiler's externally-visible behavior
# changes. Phase 0: no compiler exists yet, so this is a placeholder.
COMPILER_VERSION = "0.0.1"

app = FastAPI(title="DiffEq Compiler API")


@app.get("/api/health")
def health() -> dict:
    """Liveness / deploy-pipeline smoke test. See INTERFACE_CONTRACTS.md §9."""
    return {"status": "ok", "compiler_version": COMPILER_VERSION}
