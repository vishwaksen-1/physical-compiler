"""Damped torsional pendulum: rotational-mechanical realization of the
2nd-order linear constant-coefficient ODE class (third alt realization,
alongside mass_spring_damper and series_rlc). See
data/physical_models/torsional_pendulum.yaml for metadata.
"""

import sympy as sp

from .registry import register_model, build_model_from_yaml

_MODEL_ID = "torsional_pendulum"

t = sp.symbols("t", real=True)
I, b, k_t = sp.symbols("I b k_t", positive=True)
tau = sp.Function("tau")
theta = sp.Function("theta")

# I*theta'' + b*theta' + k_t*theta = tau(t)
GOVERNING_EQUATION = sp.Eq(
    I * sp.diff(theta(t), t, 2) + b * sp.diff(theta(t), t) + k_t * theta(t),
    tau(t),
)


@register_model
def build_torsional_pendulum():
    return build_model_from_yaml(_MODEL_ID, GOVERNING_EQUATION)
