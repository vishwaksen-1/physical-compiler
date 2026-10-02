"""Runs the real frontend smoke test suite (tests/frontend/run.mjs) as part
of the normal pytest run.

This is a thin wrapper, not a reimplementation: the actual assertions live
in tests/frontend/run.mjs, executed against a real DOM via jsdom (see that
file's docstring, and tests/frontend/harness.mjs, for why this exists --
in short, a real crash bug went undetected for two sessions because
nothing actually executed the frontend code, only syntax-checked it).

Skips (doesn't fail) if `npm install` hasn't been run -- this project's
Python test suite shouldn't hard-require a Node toolchain to be set up,
but if it IS set up, these tests run for real and must pass.
"""
import os
import subprocess
import sys

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_NODE_MODULES = os.path.join(_REPO_ROOT, "node_modules", "jsdom")
_RUNNER = os.path.join(_REPO_ROOT, "tests", "frontend", "run.mjs")


@pytest.mark.skipif(
    not os.path.isdir(_NODE_MODULES),
    reason="node_modules/jsdom not installed -- run `npm install` in the repo root to enable frontend tests",
)
def test_frontend_smoke_suite():
    result = subprocess.run(
        ["node", _RUNNER],
        cwd=_REPO_ROOT, capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        print(result.stdout, file=sys.stdout)
        print(result.stderr, file=sys.stderr)
    assert result.returncode == 0, "one or more frontend smoke tests failed -- see output above"
