"""Cheap, physically-meaningful cross-parameter checks per model.

These catch things a bare min/max range check on individual parameters
can't: e.g. three parameters can each be individually in-range while their
*combination* gives an unbuildable or untestable damping ratio. Each check
takes `(model, parameter_values)` and returns a list of warning/violation
strings (empty = no issues found).

Kept intentionally lightweight for Phase 1 — these are warnings, not hard
verification. Agent A's Phase 2 `verify_mapping()` / `check_feasibility()`
own the authoritative pass/fail call; this module just gives that pass
something Phase-1-ready to call for the five models built so far.
"""

from __future__ import annotations

import math


def _damping_ratio_check(model_id: str, mass_like: float, damping: float, stiffness: float) -> list[str]:
    """Shared logic for the three 2nd-order mechanical/electrical analogs:
    zeta = damping / (2 * sqrt(mass_like * stiffness)).
    zeta < 1: underdamped (oscillates) — usually the interesting demo regime.
    zeta >= 1: critically/over-damped (no oscillation) — still valid, but
    worth flagging since it changes what the experiment demonstrates.
    """
    warnings: list[str] = []
    if mass_like <= 0 or stiffness <= 0:
        warnings.append(f"{model_id}: mass/inertia-like and stiffness-like terms must be positive")
        return warnings
    zeta = damping / (2 * math.sqrt(mass_like * stiffness))
    if zeta >= 1.0:
        warnings.append(
            f"{model_id}: damping ratio zeta={zeta:.3f} >= 1 (critically/over-damped) "
            f"— system will not oscillate; fine if that's the intended demo"
        )
    if zeta > 5.0:
        warnings.append(
            f"{model_id}: damping ratio zeta={zeta:.3f} is very high — response will "
            f"look like a slow first-order decay, may be hard to distinguish from noise"
        )
    return warnings


def _mass_spring_damper_check(model, values: dict) -> list[str]:
    if not {"m", "c", "k"} <= values.keys():
        return []
    return _damping_ratio_check(model.model_id, values["m"], values["c"], values["k"])


def _series_rlc_check(model, values: dict) -> list[str]:
    if not {"L", "R", "C"} <= values.keys():
        return []
    # For L*q'' + R*q' + q/C = V(t), the stiffness-like term is 1/C.
    stiffness_like = 1.0 / values["C"] if values["C"] else float("inf")
    return _damping_ratio_check(model.model_id, values["L"], values["R"], stiffness_like)


def _torsional_pendulum_check(model, values: dict) -> list[str]:
    if not {"I", "b", "k_t"} <= values.keys():
        return []
    return _damping_ratio_check(model.model_id, values["I"], values["b"], values["k_t"])


def _time_constant_check(model_id: str, tau: float) -> list[str]:
    """First-order systems (RC circuit, Newton's cooling) are characterized
    by a single time constant tau. Flag time constants outside a range a
    benchtop data logger/oscilloscope can comfortably resolve
    (roughly 1 ms to ~1 hour)."""
    warnings: list[str] = []
    if tau <= 0:
        warnings.append(f"{model_id}: time constant must be positive, got {tau}")
        return warnings
    if tau < 1e-3:
        warnings.append(
            f"{model_id}: time constant tau={tau:.2e}s is faster than typical "
            f"low-cost DAQ sampling rates can resolve cleanly"
        )
    if tau > 3600.0:
        warnings.append(
            f"{model_id}: time constant tau={tau:.2e}s (>1hr) makes for a very "
            f"long single run — consider adjusting parameters or expected runtime"
        )
    return warnings


def _rc_circuit_check(model, values: dict) -> list[str]:
    if not {"R", "C"} <= values.keys():
        return []
    return _time_constant_check(model.model_id, values["R"] * values["C"])


def _newtons_cooling_check(model, values: dict) -> list[str]:
    if "k" not in values or values["k"] == 0:
        return []
    return _time_constant_check(model.model_id, 1.0 / values["k"])


# --- Themed models (God Mode / Antman Mode) ---

def _mirror_ringdown_check(model, values: dict) -> list[str]:
    if not {"m", "c", "k"} <= values.keys():
        return []
    return _damping_ratio_check(model.model_id, values["m"], values["c"], values["k"])


def _optical_trap_oscillator_check(model, values: dict) -> list[str]:
    if not {"m", "c", "k"} <= values.keys():
        return []
    return _damping_ratio_check(model.model_id, values["m"], values["c"], values["k"])


def _expansion_analog_check(model, values: dict) -> list[str]:
    # Growth, not decay: 1/H is the e-folding time of the runaway, which has
    # to be slow enough to log before the op-amp output hits the rail.
    if "H" not in values or values["H"] == 0:
        return []
    return _time_constant_check(model.model_id, 1.0 / values["H"])


def _nmr_relaxation_check(model, values: dict) -> list[str]:
    """T1 = 1/Gamma. A benchtop pulse spectrometer resolves far faster
    timescales than a generic DAQ (pulse spacing ~ microseconds), so this
    uses its own bounds instead of _time_constant_check's 1 ms floor."""
    if "Gamma" not in values or values["Gamma"] <= 0:
        return []
    t1 = 1.0 / values["Gamma"]
    warnings: list[str] = []
    if t1 < 1e-5:
        warnings.append(
            f"{model.model_id}: T1={t1:.2e}s is shorter than a benchtop spectrometer's "
            f"minimum pulse spacing can sample"
        )
    if t1 > 10.0:
        warnings.append(
            f"{model.model_id}: T1={t1:.2e}s makes each inversion-recovery point take "
            f"minutes (repetition time ~5*T1)"
        )
    return warnings


MODEL_SPECIFIC_CHECKS = {
    "mass_spring_damper": _mass_spring_damper_check,
    "series_rlc": _series_rlc_check,
    "torsional_pendulum": _torsional_pendulum_check,
    "rc_circuit": _rc_circuit_check,
    "newtons_cooling": _newtons_cooling_check,
    "mirror_ringdown": _mirror_ringdown_check,
    "expansion_analog": _expansion_analog_check,
    "optical_trap_oscillator": _optical_trap_oscillator_check,
    "nmr_relaxation": _nmr_relaxation_check,
}


def check_model_specific(model, parameter_values: dict) -> list[str]:
    check_fn = MODEL_SPECIFIC_CHECKS.get(model.model_id)
    if check_fn is None:
        return []
    return check_fn(model, parameter_values)
