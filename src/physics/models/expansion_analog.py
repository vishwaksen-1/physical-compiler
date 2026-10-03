"""Positive-feedback expansion analog (God Mode / theme "celestial"): an
op-amp integrator with positive feedback whose output grows exponentially,
the same shape as a dark-energy-dominated scale factor. The first registered
model in the exponential-*growth* regime. See
data/physical_models/expansion_analog.yaml for metadata.

The right-hand side must be an applied forcing function F(t), not a bare 0:
ode_matching.model_structure() requires exactly one applied undefined
function on the rhs, and a model with none is silently skipped by
generate_candidates().

H is declared positive=True on purpose. For a decay-shaped equation
(y' + 4y = 0) the coefficient match solves to H = -4, which sympy's solve()
rejects under that assumption. The model then yields no candidate at all,
rather than a clamped candidate that fails verification later.
"""

import sympy as sp

from .registry import register_model, build_model_from_yaml

_MODEL_ID = "expansion_analog"

t = sp.symbols("t", real=True)
H = sp.symbols("H", positive=True)
F = sp.Function("F")
V = sp.Function("V")

# V' - H*V = F(t)      (H > 0: growth, not decay)
GOVERNING_EQUATION = sp.Eq(
    sp.diff(V(t), t) - H * V(t),
    F(t),
)


@register_model
def build_expansion_analog():
    return build_model_from_yaml(_MODEL_ID, GOVERNING_EQUATION)
