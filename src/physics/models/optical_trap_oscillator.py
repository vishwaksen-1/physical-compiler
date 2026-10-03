"""Optically-trapped nanoparticle oscillator (Antman Mode / theme "quantum"):
a levitated nanosphere in a laser trap, realizing the 2nd-order linear
constant-coefficient ODE class at nanoscale parameter values. See
data/physical_models/optical_trap_oscillator.yaml for metadata.
"""

import sympy as sp

from .registry import register_model, build_model_from_yaml

_MODEL_ID = "optical_trap_oscillator"

t = sp.symbols("t", real=True)
m, c, k = sp.symbols("m c k", positive=True)
F = sp.Function("F")
x = sp.Function("x")

# m*x'' + c*x' + k*x = F(t)
GOVERNING_EQUATION = sp.Eq(
    m * sp.diff(x(t), t, 2) + c * sp.diff(x(t), t) + k * x(t),
    F(t),
)


@register_model
def build_optical_trap_oscillator():
    return build_model_from_yaml(_MODEL_ID, GOVERNING_EQUATION)
