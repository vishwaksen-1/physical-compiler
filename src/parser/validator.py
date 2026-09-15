"""
Validates that a dict (or EquationSpec) conforms to
INTERFACE_CONTRACTS.md §1. This is the shared honesty-check between
Agent C's text parser and Agent D's web equation-builder — either path's
output should pass `validate_equation_spec()` with no coordination
needed mid-phase (INTERFACE_CONTRACTS.md §1: "the seam that lets Agent C
and Agent D work without ever talking to each other mid-phase").

Deliberately dependency-free (stdlib only) and independent of the lark
grammar, so it works on hand-built dicts from the web frontend just as
well as on this module's own parser output.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

from .equation_spec import EquationSpec

_DOMAIN_TYPES = {"ODE", "PDE"}
_INPUT_SOURCES = {"web_builder", "text_parser"}
_FORCING_TYPES = {"zero", "const", "sin", "cos", "step", "impulse", "polynomial", "custom_expr"}
_SPEC_VERSION = "1.0"


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid

    def raise_if_invalid(self):
        if not self.valid:
            raise ValueError("EquationSpec failed validation: " + "; ".join(self.errors))


def _as_dict(spec: Union[Dict[str, Any], EquationSpec]) -> Dict[str, Any]:
    if isinstance(spec, EquationSpec):
        return spec.to_dict()
    return spec


def validate_equation_spec(spec: Union[Dict[str, Any], EquationSpec]) -> ValidationResult:
    errors: List[str] = []
    try:
        d = _as_dict(spec)
    except Exception as e:  # noqa: BLE001 - defensively surface as a validation error
        return ValidationResult(valid=False, errors=[f"spec is not a dict or EquationSpec: {e}"])

    if not isinstance(d, dict):
        return ValidationResult(valid=False, errors=["spec must be a dict or EquationSpec"])

    required = [
        "spec_version",
        "domain_type",
        "independent_vars",
        "dependent_var",
        "order",
        "terms",
        "rhs_forcing",
        "input_source",
    ]
    for key in required:
        if key not in d:
            errors.append(f"missing required key: '{key}'")
    if errors:
        # Can't safely check field-level types on a spec that's missing
        # top-level keys.
        return ValidationResult(valid=False, errors=errors)

    if d["spec_version"] != _SPEC_VERSION:
        errors.append(f"spec_version must be '{_SPEC_VERSION}', got {d['spec_version']!r}")

    if d["domain_type"] not in _DOMAIN_TYPES:
        errors.append(f"domain_type must be one of {sorted(_DOMAIN_TYPES)}, got {d['domain_type']!r}")

    indep = d["independent_vars"]
    if not isinstance(indep, list) or not indep or not all(isinstance(v, str) and v for v in indep):
        errors.append("independent_vars must be a non-empty list of non-empty strings")

    if not isinstance(d["dependent_var"], str) or not d["dependent_var"]:
        errors.append("dependent_var must be a non-empty string")

    order = d["order"]
    if not isinstance(order, int) or isinstance(order, bool) or order < 0:
        errors.append("order must be a non-negative int")

    terms = d["terms"]
    if not isinstance(terms, list) or not terms:
        errors.append("terms must be a non-empty list")
    else:
        for i, t in enumerate(terms):
            errors.extend(_validate_term(t, i, indep if isinstance(indep, list) else None))
        if isinstance(order, int) and not isinstance(order, bool):
            term_orders = [t.get("derivative_order") for t in terms if isinstance(t, dict)]
            numeric_orders = [o for o in term_orders if isinstance(o, int) and not isinstance(o, bool)]
            if numeric_orders:
                if max(numeric_orders) > order:
                    errors.append(
                        f"a term has derivative_order {max(numeric_orders)} > spec order {order}"
                    )
                if order not in numeric_orders:
                    errors.append(
                        f"spec order is {order} but no term has derivative_order == {order}"
                    )

    errors.extend(_validate_rhs_forcing(d["rhs_forcing"]))

    for key in ("initial_conditions", "boundary_conditions"):
        if key in d and d[key] is not None and not isinstance(d[key], dict):
            errors.append(f"{key} must be a dict or null")

    if d["input_source"] not in _INPUT_SOURCES:
        errors.append(f"input_source must be one of {sorted(_INPUT_SOURCES)}, got {d['input_source']!r}")

    raw_text = d.get("raw_text")
    if raw_text is not None and not isinstance(raw_text, str):
        errors.append("raw_text must be a string or null")
    if d.get("input_source") == "text_parser" and not raw_text:
        errors.append("input_source == 'text_parser' requires a non-empty raw_text")

    return ValidationResult(valid=not errors, errors=errors)


def _validate_term(t: Any, index: int, independent_vars) -> List[str]:
    errs = []
    prefix = f"terms[{index}]"
    if not isinstance(t, dict):
        return [f"{prefix} must be a dict"]

    for key in ("derivative_order", "wrt", "coefficient"):
        if key not in t:
            errs.append(f"{prefix} missing key '{key}'")
    if errs:
        return errs

    do = t["derivative_order"]
    if not isinstance(do, int) or isinstance(do, bool) or do < 0:
        errs.append(f"{prefix}.derivative_order must be a non-negative int")

    wrt = t["wrt"]
    wrt_ok = (isinstance(wrt, str) and wrt) or (
        isinstance(wrt, list) and wrt and all(isinstance(v, str) and v for v in wrt)
    )
    if not wrt_ok:
        errs.append(f"{prefix}.wrt must be a non-empty string or non-empty list[str]")
    elif independent_vars:
        wrt_names = [wrt] if isinstance(wrt, str) else wrt
        unknown = [w for w in wrt_names if w not in independent_vars]
        if unknown:
            errs.append(
                f"{prefix}.wrt references {unknown} not present in independent_vars {independent_vars}"
            )

    coeff = t["coefficient"]
    if not isinstance(coeff, (float, int, str)) or isinstance(coeff, bool):
        errs.append(f"{prefix}.coefficient must be a float or str")

    return errs


def _validate_rhs_forcing(rf: Any) -> List[str]:
    errs = []
    if not isinstance(rf, dict):
        return ["rhs_forcing must be a dict"]

    for key in ("type", "params", "expr"):
        if key not in rf:
            errs.append(f"rhs_forcing missing key '{key}'")
    if errs:
        return errs

    if rf["type"] not in _FORCING_TYPES:
        errs.append(f"rhs_forcing.type must be one of {sorted(_FORCING_TYPES)}, got {rf['type']!r}")
    if not isinstance(rf["params"], dict):
        errs.append("rhs_forcing.params must be a dict")
    if rf["expr"] is not None and not isinstance(rf["expr"], str):
        errs.append("rhs_forcing.expr must be a string or null")
    if rf.get("type") == "custom_expr" and not rf.get("expr"):
        errs.append("rhs_forcing.type == 'custom_expr' requires a non-empty expr")

    return errs


def structurally_equivalent_ignoring_source(
    spec_a: Union[Dict[str, Any], EquationSpec], spec_b: Union[Dict[str, Any], EquationSpec]
) -> bool:
    """INTERFACE_CONTRACTS.md §1's cross-path check: a web-builder spec and
    a text-parser spec for the "same" equation must match except for
    `input_source` and `raw_text`.
    """
    a = dict(_as_dict(spec_a))
    b = dict(_as_dict(spec_b))
    for key in ("input_source", "raw_text"):
        a.pop(key, None)
        b.pop(key, None)
    return a == b
