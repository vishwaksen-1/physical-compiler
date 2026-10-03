"""
Physical model registry package (Agent B).

Importing this package has the side effect of importing every model module
below, which runs their `@register_model` factories and populates the
registry. Import order here IS registration order, which IS the
deterministic tie-break order per INTERFACE_CONTRACTS.md §6 — don't reorder
these imports casually; treat reordering as a contract-affecting change and
log it in STATUS.md.
"""

from .registry import (
    PhysicalModel,
    register_model,
    get_registry,
    get_model,
    registry_summary,
    load_yaml_metadata,
    build_model_from_yaml,
)

# --- Phase 1 target list (PROJECT_PLAN.md §3), items 1-5 ---
from . import mass_spring_damper  # noqa: F401  (1) mechanical, 2nd-order linear ODE
from . import series_rlc  # noqa: F401          (2) electrical, alt realization of (1)
from . import torsional_pendulum  # noqa: F401  (3) mechanical rotational, alt realization of (1)
from . import rc_circuit  # noqa: F401          (4) electrical, 1st-order linear ODE
from . import newtons_cooling  # noqa: F401     (5) thermal, alt realization of (4)

# --- Themed "fun mode" models (theme != None) ---
# Deliberately registered AFTER the classical five: rank_candidates()
# tie-breaks by insertion order, so even if src/api's theme filtering were
# ever bypassed, a themed model could never win a tie against a classical one.
from . import mirror_ringdown  # noqa: F401          (6) celestial / God Mode, 2nd order
from . import expansion_analog  # noqa: F401         (7) celestial / God Mode, 1st order (growth)
from . import optical_trap_oscillator  # noqa: F401  (8) quantum / Antman Mode, 2nd order
from . import nmr_relaxation  # noqa: F401           (9) quantum / Antman Mode, 1st order

__all__ = [
    "PhysicalModel",
    "register_model",
    "get_registry",
    "get_model",
    "registry_summary",
    "load_yaml_metadata",
    "build_model_from_yaml",
]
