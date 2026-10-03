"""NMR spin-lattice relaxation apparatus (Antman Mode / theme "quantum"):
longitudinal nuclear magnetization relaxing toward equilibrium, the same
structural shape as newtons_cooling (a single rate parameter, forced toward
an external equilibrium value). See data/physical_models/nmr_relaxation.yaml
for metadata.
"""

import sympy as sp

from .registry import register_model, build_model_from_yaml

_MODEL_ID = "nmr_relaxation"

t = sp.symbols("t", real=True)
Gamma = sp.symbols("Gamma", positive=True)
M_eq = sp.Function("M_eq")
Mz = sp.Function("Mz")

# Mz' + Gamma*Mz = Gamma*M_eq(t)      (Gamma = 1/T1)
GOVERNING_EQUATION = sp.Eq(
    sp.diff(Mz(t), t) + Gamma * Mz(t),
    Gamma * M_eq(t),
)


@register_model
def build_nmr_relaxation():
    return build_model_from_yaml(_MODEL_ID, GOVERNING_EQUATION)
