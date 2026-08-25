"""
Root conftest.py — pins PYTHONHASHSEED=0 for every test run.

Why (PROJECT_PLAN.md §1.2, "Determinism gotcha"): this project's core
guarantee is that the same input + config always produces the same
ExperimentOutput (INTERFACE_CONTRACTS.md §6). Python randomizes str/repr
hash ordering per-process by default, which can silently leak into
`set`/`dict` iteration order and therefore into SymPy expression printing,
registry traversal, or anywhere else code accidentally relies on hash-based
ordering instead of the sorted printer / stable insertion order the
contracts require. Pinning the hash seed makes any such accidental
dependency reproducible (and catchable) across runs instead of flaking.

PYTHONHASHSEED must be set before the interpreter starts — setting
`os.environ["PYTHONHASHSEED"]` mid-process has no effect on the *current*
process. So if it isn't already set correctly, this conftest re-executes
the current pytest invocation in a fresh subprocess with it set, once.
"""

import os
import sys

_REQUIRED_HASHSEED = "0"

if os.environ.get("PYTHONHASHSEED") != _REQUIRED_HASHSEED:
    os.environ["PYTHONHASHSEED"] = _REQUIRED_HASHSEED
    os.execv(sys.executable, [sys.executable] + sys.argv)
