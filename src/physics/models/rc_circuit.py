"""Simple RC circuit: electrical realization of the 1st-order linear
constant-coefficient ODE class. See data/physical_models/rc_circuit.yaml
for metadata.
"""

import sympy as sp

from .registry import register_model, build_model_from_yaml

_MODEL_ID = "rc_circuit"

t = sp.symbols("t", real=True)
R, C = sp.symbols("R C", positive=True)
V_in = sp.Function("V_in")
Vc = sp.Function("Vc")

# R*C*Vc' + Vc = V_in(t)
GOVERNING_EQUATION = sp.Eq(
    R * C * sp.diff(Vc(t), t) + Vc(t),
    V_in(t),
)


@register_model
def build_rc_circuit():
    return build_model_from_yaml(_MODEL_ID, GOVERNING_EQUATION)
