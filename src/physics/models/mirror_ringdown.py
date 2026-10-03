"""Suspended-mirror ringdown analog (God Mode / theme "celestial"): a tabletop
analog of a gravitational-wave detector's suspended test mass, realizing the
2nd-order linear constant-coefficient ODE class. See
data/physical_models/mirror_ringdown.yaml for metadata.
"""

import sympy as sp

from .registry import register_model, build_model_from_yaml

_MODEL_ID = "mirror_ringdown"

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
def build_mirror_ringdown():
    return build_model_from_yaml(_MODEL_ID, GOVERNING_EQUATION)
