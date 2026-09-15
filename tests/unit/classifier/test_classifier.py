from src.canonical.ir import canonicalize
from src.classifier.classifier import classify


def _spec(terms, rhs_forcing, independent_vars=None, domain_type="ODE"):
    return {
        "spec_version": "1.0",
        "domain_type": domain_type,
        "independent_vars": independent_vars or ["t"],
        "dependent_var": "x",
        "order": 2,
        "terms": terms,
        "rhs_forcing": rhs_forcing,
        "initial_conditions": None,
        "boundary_conditions": None,
        "input_source": "web_builder",
        "raw_text": None,
    }


def test_linear_homogeneous_second_order_constant_coefficient():
    spec = _spec(
        terms=[
            {"derivative_order": 2, "wrt": "t", "coefficient": 1},
            {"derivative_order": 1, "wrt": "t", "coefficient": 2},
            {"derivative_order": 0, "wrt": "t", "coefficient": 1},
        ],
        rhs_forcing={"type": "zero", "params": {}, "expr": None},
    )
    ir = canonicalize(spec)
    tags = classify(ir)

    assert ir.linearity == "linear"
    assert ir.homogeneity == "homogeneous"
    assert "ODE" in tags
    assert "linear" in tags
    assert "homogeneous" in tags
    assert "second_order" in tags
    assert "constant_coefficient" in tags


def test_nonhomogeneous_forcing():
    spec = _spec(
        terms=[
            {"derivative_order": 2, "wrt": "t", "coefficient": 1},
            {"derivative_order": 0, "wrt": "t", "coefficient": 1},
        ],
        rhs_forcing={"type": "sin", "params": {"amplitude": 1, "frequency": 1, "phase": 0}, "expr": None},
    )
    ir = canonicalize(spec)
    classify(ir)
    assert ir.homogeneity == "nonhomogeneous"
    assert ir.linearity == "linear"


def test_nonlinear_forcing_referencing_dependent_var():
    # small-angle-free driven pendulum style nonlinearity: forcing has sin(x)
    spec = _spec(
        terms=[
            {"derivative_order": 2, "wrt": "t", "coefficient": 1},
        ],
        rhs_forcing={"type": "custom_expr", "params": {}, "expr": "-sin(x(t))"},
    )
    ir = canonicalize(spec)
    classify(ir)
    assert ir.linearity == "nonlinear"


def test_nonlinear_coefficient_depending_on_dependent_var():
    spec = _spec(
        terms=[
            {"derivative_order": 1, "wrt": "t", "coefficient": "x(t)"},  # x * x' -> nonlinear
            {"derivative_order": 0, "wrt": "t", "coefficient": 1},
        ],
        rhs_forcing={"type": "zero", "params": {}, "expr": None},
    )
    ir = canonicalize(spec)
    classify(ir)
    assert ir.linearity == "nonlinear"


def test_non_constant_coefficient_still_linear():
    # k(t) * x' is linear in x even though the coefficient is time-varying
    spec = _spec(
        terms=[
            {"derivative_order": 1, "wrt": "t", "coefficient": "sin(t)"},
            {"derivative_order": 0, "wrt": "t", "coefficient": 1},
        ],
        rhs_forcing={"type": "zero", "params": {}, "expr": None},
    )
    ir = canonicalize(spec)
    tags = classify(ir)
    assert ir.linearity == "linear"
    assert "constant_coefficient" not in tags


def test_pde_domain_classified_correctly():
    spec = _spec(
        terms=[
            {"derivative_order": 2, "wrt": ["x", "x"], "coefficient": 1},
            {"derivative_order": 1, "wrt": "t", "coefficient": -1},
        ],
        rhs_forcing={"type": "zero", "params": {}, "expr": None},
        independent_vars=["x", "t"],
        domain_type="PDE",
    )
    spec["dependent_var"] = "u"
    ir = canonicalize(spec)
    tags = classify(ir)
    assert "PDE" in tags
    assert "domain_type_mismatch" not in tags


def test_domain_type_mismatch_is_flagged():
    spec = _spec(
        terms=[{"derivative_order": 1, "wrt": "t", "coefficient": 1}],
        rhs_forcing={"type": "zero", "params": {}, "expr": None},
        independent_vars=["t"],
        domain_type="PDE",  # wrong: only one independent var, this is an ODE
    )
    ir = canonicalize(spec)
    tags = classify(ir)
    assert "domain_type_mismatch" in tags


def test_first_order_tagging():
    spec = _spec(
        terms=[
            {"derivative_order": 1, "wrt": "t", "coefficient": 1},
            {"derivative_order": 0, "wrt": "t", "coefficient": 1},
        ],
        rhs_forcing={"type": "zero", "params": {}, "expr": None},
    )
    spec["order"] = 1
    ir = canonicalize(spec)
    tags = classify(ir)
    assert "first_order" in tags
