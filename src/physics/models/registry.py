"""
Physical model registry — core dataclass + registration machinery.

Owned by Agent B. This module implements the `PhysicalModel` schema frozen in
`docs/INTERFACE_CONTRACTS.md` §3, plus the `@register_model` decorator every
model file in this package uses.

Design:
- Non-symbolic metadata (units, constraints, costs, safety notes, ...) lives
  in a companion YAML file at `data/physical_models/<model_id>.yaml`.
- The real SymPy `governing_equation` is constructed in Python, in the
  model's own file (e.g. `mass_spring_damper.py`), because YAML can't hold a
  live SymPy expression.
- `register_model` is a decorator applied to a zero-argument factory function
  that builds and returns a `PhysicalModel`. The factory is called once at
  import time; the resulting model is stored in insertion order, which is
  the tie-break rule in `INTERFACE_CONTRACTS.md` §6 ("stable registry
  insertion order, never set/dict iteration order").

Implementation note / open question for Agent A (logged in STATUS.md too):
`governing_equation` is stored as a `sympy.Eq(lhs, rhs)` object rather than a
bare `sympy.Expr`, since a governing equation naturally has two sides and
`Eq` round-trips losslessly (`eq.lhs - eq.rhs` recovers the "= 0" form any
`Expr`-based consumer would want). The contract's `"sympy.Expr"` type hint is
pseudocode; flagging the concrete type here so Agent A's canonicalizer knows
what to expect.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Optional

import sympy as sp
import yaml

# ---------------------------------------------------------------------------
# Registry state
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, "PhysicalModel"] = {}
_INSERTION_ORDER: list[str] = []

# repo_root/src/physics/models/registry.py -> repo_root is 3 parents up
_REPO_ROOT = Path(__file__).resolve().parents[3]
_MODEL_DATA_DIR = _REPO_ROOT / "data" / "physical_models"


# ---------------------------------------------------------------------------
# Schema (INTERFACE_CONTRACTS.md §3)
# ---------------------------------------------------------------------------

@dataclass
class PhysicalModel:
    model_id: str
    display_name: str
    domain: str  # "mechanical" | "electrical" | "thermal" | "optomechanical" | "magnetic" | "other"
    equation_class_tags: list[str]
    state_variables: dict[str, str]
    governing_equation: sp.Basic  # sp.Eq(lhs, rhs); see module docstring
    parameter_map: dict[str, str]
    parameter_constraints: dict[str, dict]
    dimensional_constraints: dict
    measurable_variables: list[str]
    controllable_variables: list[str]
    construction_requirements: dict
    approximation_model: dict = field(
        default_factory=lambda: {"type": "none", "assumptions": []}
    )
    error_model: dict = field(
        default_factory=lambda: {"sources": [], "expected_relative_error_pct": 0.0}
    )
    safety_notes: list[str] = field(default_factory=list)
    alt_realizations_of: Optional[str] = None
    # Additive, not in INTERFACE_CONTRACTS.md §3 -- see
    # src/physics/models/artwork.py's module docstring. Left None at
    # construction; register_model() fills it in once, at import time.
    artwork: Optional[dict] = field(default=None)
    # Additive, not in INTERFACE_CONTRACTS.md §3 (logged in docs/STATUS.md).
    # Which "fun mode" this model belongs to: None = classical (the default
    # experience), "celestial" = God Mode, "quantum" = Antman Mode. Unlike
    # `artwork`, this is author-declared directly as a top-level YAML key.
    # src/api's _themed_registry() filters on it before candidate generation.
    theme: Optional[str] = field(default=None)

    def to_dict(self) -> dict:
        """JSON-serializable form. `governing_equation` becomes a string.

        NOTE: uses plain `str()`, not a sorted/canonical printer. Per the
        determinism policy (PROJECT_PLAN.md §1.2), any consumer that needs a
        stable, order-independent serialization for hashing/comparison
        (e.g. `equivalence_hash` in the IR) should route through Agent A's
        canonical printer in `src/symbolic/engine.py`, not this method.
        """
        d = asdict(self)
        d["governing_equation"] = str(self.governing_equation)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "PhysicalModel":
        d = dict(d)
        d["governing_equation"] = sp.sympify(d["governing_equation"])
        return cls(**d)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register_model(factory: Callable[[], PhysicalModel]) -> Callable[[], PhysicalModel]:
    """Decorator. Calls `factory()` once at import time, registers the
    resulting `PhysicalModel`, and returns the factory unchanged (so it
    stays importable/callable for tests).

    Usage:
        @register_model
        def build_mass_spring_damper() -> PhysicalModel:
            return PhysicalModel(...)

    Also resolves and validates this model's illustrative image (see
    src/physics/models/artwork.py) exactly once here, at "compile-time" in
    the sense the human asked for -- import time, once per process, not
    re-checked on every request. A rejected image (wrong aspect ratio,
    unreadable file) prints a warning immediately, at registration, rather
    than surfacing silently only when someone happens to compile an
    equation that matches this model.
    """
    from src.physics.models.artwork import resolve_artwork

    model = factory()
    if not isinstance(model, PhysicalModel):
        raise TypeError(
            f"@register_model factory {factory.__name__!r} must return a "
            f"PhysicalModel, got {type(model)!r}"
        )
    if model.model_id in _REGISTRY:
        raise ValueError(f"duplicate model_id: {model.model_id!r}")

    model.artwork = resolve_artwork(model.model_id)
    if model.artwork["status"] == "rejected":
        print(f"[registry] image warning for {model.model_id!r}: {model.artwork['reason']}")

    _REGISTRY[model.model_id] = model
    _INSERTION_ORDER.append(model.model_id)
    return factory


def get_registry() -> list[PhysicalModel]:
    """All registered models, in stable insertion order — this order IS the
    tie-break policy from INTERFACE_CONTRACTS.md §6."""
    return [_REGISTRY[mid] for mid in _INSERTION_ORDER]


def get_model(model_id: str) -> PhysicalModel:
    return _REGISTRY[model_id]


def registry_summary() -> list[dict]:
    """Shape matching the `GET /api/models` response summary list, plus one
    additive extra key (`artwork`) not in INTERFACE_CONTRACTS.md §9's table
    -- any consumer reading only the three documented keys is unaffected."""
    return [
        {
            "model_id": m.model_id,
            "display_name": m.display_name,
            "domain": m.domain,
            "artwork": m.artwork,
        }
        for m in get_registry()
    ]


# ---------------------------------------------------------------------------
# YAML metadata loading
# ---------------------------------------------------------------------------

def load_yaml_metadata(model_id: str) -> dict[str, Any]:
    """Load the companion YAML file for a model (everything except
    `governing_equation`, which the model's Python file supplies directly)."""
    path = _MODEL_DATA_DIR / f"{model_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"no companion YAML metadata for model_id={model_id!r} at {path}"
        )
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data


def build_model_from_yaml(model_id: str, governing_equation: sp.Basic) -> PhysicalModel:
    """Convenience constructor: load YAML metadata for `model_id`, splice in
    the live SymPy `governing_equation`, and build a `PhysicalModel`."""
    meta = load_yaml_metadata(model_id)
    if meta.get("model_id") != model_id:
        raise ValueError(
            f"YAML model_id mismatch: file {model_id}.yaml declares "
            f"{meta.get('model_id')!r}"
        )
    return PhysicalModel(governing_equation=governing_equation, **meta)
