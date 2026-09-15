from src.canonical.ir import DifferentialEquationIR, canonicalize


def _spec(terms, rhs_forcing, input_source="web_builder"):
    return {
        "spec_version": "1.0",
        "domain_type": "ODE",
        "independent_vars": ["t"],
        "dependent_var": "x",
        "order": 2,
        "terms": terms,
        "rhs_forcing": rhs_forcing,
        "initial_conditions": None,
        "boundary_conditions": None,
        "input_source": input_source,
        "raw_text": None,
    }


def test_canonicalize_produces_matching_form_and_hash_for_equivalent_specs():
    spec1 = _spec(
        terms=[
            {"derivative_order": 2, "wrt": "t", "coefficient": 1},
            {"derivative_order": 1, "wrt": "t", "coefficient": 2},
            {"derivative_order": 0, "wrt": "t", "coefficient": 1},
        ],
        rhs_forcing={"type": "zero", "params": {}, "expr": None},
        input_source="web_builder",
    )
    spec2 = _spec(
        terms=[{"derivative_order": 2, "wrt": "t", "coefficient": 1}],
        rhs_forcing={"type": "custom_expr", "params": {}, "expr": "-2*Derivative(x(t), t) - x(t)"},
        input_source="text_parser",
    )

    ir1 = canonicalize(spec1)
    ir2 = canonicalize(spec2)

    assert isinstance(ir1, DifferentialEquationIR)
    assert ir1.canonical_form == ir2.canonical_form
    assert ir1.equivalence_hash == ir2.equivalence_hash
    # only input_source/raw_text-derived provenance fields should differ
    assert ir1.source_spec_ref != ir2.source_spec_ref


def test_canonicalize_leaves_classification_fields_blank_for_classifier_to_fill():
    spec = _spec(
        terms=[{"derivative_order": 1, "wrt": "t", "coefficient": 1}],
        rhs_forcing={"type": "zero", "params": {}, "expr": None},
    )
    ir = canonicalize(spec)
    assert ir.linearity == ""
    assert ir.homogeneity == ""
    assert ir.classification_tags == []


def test_ir_round_trips_through_to_dict_from_dict():
    spec = _spec(
        terms=[{"derivative_order": 1, "wrt": "t", "coefficient": 1}],
        rhs_forcing={"type": "zero", "params": {}, "expr": None},
    )
    ir = canonicalize(spec)
    d = ir.to_dict()
    ir2 = DifferentialEquationIR.from_dict(d)
    assert ir == ir2


def test_order_derived_from_terms_not_trusted_spec_field():
    spec = _spec(
        terms=[{"derivative_order": 1, "wrt": "t", "coefficient": 1}],
        rhs_forcing={"type": "zero", "params": {}, "expr": None},
    )
    spec["order"] = 99  # deliberately wrong / untrusted
    ir = canonicalize(spec)
    assert ir.order == 1
