"""Series RLC circuit: electrical realization of the 2nd-order linear
constant-coefficient ODE class (alt realization of mass_spring_damper's
class). See data/physical_models/series_rlc.yaml for metadata.
"""

import sympy as sp

from .registry import register_model, build_model_from_yaml

_MODEL_ID = "series_rlc"

t = sp.symbols("t", real=True)
L, R, C = sp.symbols("L R C", positive=True)
V = sp.Function("V")
q = sp.Function("q")

# L*q'' + R*q' + q/C = V(t)   (KVL around the series loop, i = dq/dt)
GOVERNING_EQUATION = sp.Eq(
    L * sp.diff(q(t), t, 2) + R * sp.diff(q(t), t) + q(t) / C,
    V(t),
)


@register_model
def build_series_rlc():
    return build_model_from_yaml(_MODEL_ID, GOVERNING_EQUATION)
