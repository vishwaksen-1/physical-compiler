"""
Vercel entrypoint (INTERFACE_CONTRACTS.md §9). Thin HTTP wrapper only —
request parsing, calling into src/api/, and JSON serialization. No compiler
logic lives here; see src/api/__init__.py for compile_equation() and
friends.

DEPLOYMENT FIX (this session): `api/index.py` is not one of Vercel's
zero-config FastAPI framework-preset entrypoint locations (app.py, index.py,
server.py, main.py, wsgi.py, asgi.py at the repo root or under src/ or
app/ — see https://vercel.com/docs/frameworks/backend/fastapi). Without an
explicitly declared entrypoint, Vercel falls back to file-based Python
Functions routing, under which a file inside /api serves *only its exact
path* — api/index.py would serve literally `/api` and nothing else, which
is why every route defined here beyond that (`/api/health`, `/api/parse`,
`/api/compile`, `/api/models`) was returning Starlette's default
`{"detail":"Not Found"}`: the request never reached this app at all.
Fixed by adding a `pyproject.toml` at the repo root with
`[tool.vercel] entrypoint = "api.index:app"`, which registers the FastAPI
framework preset explicitly and hands this app full control of routing
(and of serving public/, per the same doc). See docs/STATUS.md for the
full diagnosis.

ARTWORK MOUNTS (later session): `/media/images/*` and `/media/memes/*` are
mounted below via Starlette's StaticFiles, serving data/images/ and
data/memes/ directly from this app -- those directories aren't under
public/, so Vercel's platform-level static CDN never sees them; only this
app's own routing does. This *should* work under the same "framework
handles all requests" architecture as everything else here, but -- per
this file's own history above -- untested against a real Vercel deploy as
of this session. Verify `<preview-url>/media/images/anything.png` (or
`/media/memes/...`) actually resolves after deploying, the same way
docs/STATUS.md already asks for /api/health etc. to be checked for real.
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os

# Repo root on sys.path so `from src...` imports work regardless of how the
# process was launched (local uvicorn, pytest, or Vercel's runtime).
_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _REPO_ROOT)

from src.api import COMPILER_VERSION, compile_equation as _compile_equation  # noqa: E402
from src.parser.text_parser import parse_equation as _parse_equation, EquationParseError  # noqa: E402
from src.parser.validator import validate_equation_spec  # noqa: E402
from src.physics.models import registry_summary  # noqa: E402

app = FastAPI(title="DiffEq Compiler API")

# Serves the model-artwork images (src/physics/models/artwork.py) and their
# meme-placeholder fallbacks. These live in data/, not web/public/, since
# they're compiler data (like data/physical_models/*.yaml) rather than
# frontend source -- Vercel's platform-level static serving only covers
# public/, so this app mounts them itself. Directories are created (even if
# initially empty, README-only) alongside this change specifically so this
# mount never fails at import time for a missing directory.
_IMAGES_DIR = os.path.join(_REPO_ROOT, "data", "images")
_MEMES_DIR = os.path.join(_REPO_ROOT, "data", "memes")
if os.path.isdir(_IMAGES_DIR):
    app.mount("/media/images", StaticFiles(directory=_IMAGES_DIR), name="images")
if os.path.isdir(_MEMES_DIR):
    app.mount("/media/memes", StaticFiles(directory=_MEMES_DIR), name="memes")


# -------------------- Health --------------------

@app.get("/api/health")
async def health():
    return {"status": "ok", "compiler_version": COMPILER_VERSION}


# -------------------- Parse --------------------

class ParseRequest(BaseModel):
    raw_text: str


@app.post("/api/parse")
async def parse_endpoint(req: ParseRequest):
    try:
        spec = _parse_equation(req.raw_text)
    except EquationParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except ImportError as exc:
        # lark missing from the deployed environment -- a build/config
        # problem, not a bad request.
        raise HTTPException(status_code=500, detail=str(exc))

    spec_dict = spec.to_dict()
    result = validate_equation_spec(spec_dict)
    if not result.valid:
        raise HTTPException(status_code=422, detail="; ".join(result.errors))
    return spec_dict


# -------------------- Compile --------------------

class CompileRequest(BaseModel):
    raw_text: Optional[str] = None
    builder_state: Optional[Dict[str, Any]] = None
    config: Dict[str, Any] = {}


@app.post("/api/compile")
async def compile_endpoint(req: CompileRequest):
    if (req.raw_text is None) == (req.builder_state is None):
        raise HTTPException(status_code=422, detail="Exactly one of raw_text or builder_state must be provided")

    try:
        output = _compile_equation(req.raw_text, req.builder_state, req.config)
    except (ValueError, EquationParseError) as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except ImportError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:  # pragma: no cover - genuine unexpected server error
        raise HTTPException(status_code=500, detail=f"internal compiler error: {exc}")

    return output.to_dict()


# -------------------- Models --------------------

@app.get("/api/models")
async def models_endpoint():
    return {"models": registry_summary()}
