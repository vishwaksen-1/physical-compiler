"""Newton's law of cooling apparatus: thermal realization of the 1st-order
linear constant-coefficient ODE class (alt realization of rc_circuit's
class). See data/physical_models/newtons_cooling.yaml for metadata.
"""

import sympy as sp

from .registry import register_model, build_model_from_yaml

_MODEL_ID = "newtons_cooling"

t = sp.symbols("t", real=True)
k = sp.symbols("k", positive=True)
T_env = sp.Function("T_env")
T = sp.Function("T")

# T' + k*T = k*T_env(t)      (equivalently: dT/dt = -k*(T - T_env(t)))
GOVERNING_EQUATION = sp.Eq(
    sp.diff(T(t), t) + k * T(t),
    k * T_env(t),
)


@register_model
def build_newtons_cooling():
    return build_model_from_yaml(_MODEL_ID, GOVERNING_EQUATION)
