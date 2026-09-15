from src.symbolic import engine as sym


def _mass_spring_damper_spec():
    return {
        "spec_version": "1.0",
        "domain_type": "ODE",
        "independent_vars": ["t"],
        "dependent_var": "x",
        "order": 2,
        "terms": [
            {"derivative_order": 2, "wrt": "t", "coefficient": 1},
            {"derivative_order": 1, "wrt": "t", "coefficient": 2},
            {"derivative_order": 0, "wrt": "t", "coefficient": 1},
        ],
        "rhs_forcing": {"type": "zero", "params": {}, "expr": None},
        "initial_conditions": None,
        "boundary_conditions": None,
        "input_source": "web_builder",
        "raw_text": None,
    }


def _mass_spring_damper_spec_rearranged():
    """Same equation, x'' isolated on the LHS and the rest moved across the
    equals sign onto rhs_forcing as a custom_expr referencing x(t)."""
    return {
        "spec_version": "1.0",
        "domain_type": "ODE",
        "independent_vars": ["t"],
        "dependent_var": "x",
        "order": 2,
        "terms": [
            {"derivative_order": 2, "wrt": "t", "coefficient": 1},
        ],
        "rhs_forcing": {
            "type": "custom_expr",
            "params": {},
            "expr": "-2*Derivative(x(t), t) - x(t)",
        },
        "initial_conditions": None,
        "boundary_conditions": None,
        "input_source": "text_parser",
        "raw_text": "x'' = -2x' - x",
    }


def test_spec_to_lhs_rhs_builds_expected_shape():
    lhs, rhs, table = sym.spec_to_lhs_rhs(_mass_spring_damper_spec())
    assert rhs == 0
    assert "t" in table
    assert "x" in table


def test_canonical_expr_matches_across_rearranged_specs():
    lhs1, rhs1, _ = sym.spec_to_lhs_rhs(_mass_spring_damper_spec())
    lhs2, rhs2, _ = sym.spec_to_lhs_rhs(_mass_spring_damper_spec_rearranged())

    c1 = sym.canonical_expr(lhs1, rhs1)
    c2 = sym.canonical_expr(lhs2, rhs2)

    assert sym.is_zero(c1 - c2)


def test_canonical_srepr_is_order_stable():
    lhs1, rhs1, _ = sym.spec_to_lhs_rhs(_mass_spring_damper_spec())
    lhs2, rhs2, _ = sym.spec_to_lhs_rhs(_mass_spring_damper_spec_rearranged())

    c1 = sym.canonical_expr(lhs1, rhs1)
    c2 = sym.canonical_expr(lhs2, rhs2)

    assert sym.canonical_srepr(c1) == sym.canonical_srepr(c2)


def test_equivalence_hash_matches_for_rearranged_equation():
    lhs1, rhs1, _ = sym.spec_to_lhs_rhs(_mass_spring_damper_spec())
    lhs2, rhs2, _ = sym.spec_to_lhs_rhs(_mass_spring_damper_spec_rearranged())

    c1 = sym.canonical_expr(lhs1, rhs1)
    c2 = sym.canonical_expr(lhs2, rhs2)

    assert sym.equivalence_hash(c1) == sym.equivalence_hash(c2)


def test_equivalence_hash_differs_for_a_different_equation():
    lhs1, rhs1, _ = sym.spec_to_lhs_rhs(_mass_spring_damper_spec())

    different = _mass_spring_damper_spec()
    different["terms"][1]["coefficient"] = 3  # 2x' -> 3x', different equation
    lhs2, rhs2, _ = sym.spec_to_lhs_rhs(different)

    c1 = sym.canonical_expr(lhs1, rhs1)
    c2 = sym.canonical_expr(lhs2, rhs2)

    assert sym.equivalence_hash(c1) != sym.equivalence_hash(c2)


def test_are_equivalent_true_for_rearranged_equation():
    lhs1, rhs1, _ = sym.spec_to_lhs_rhs(_mass_spring_damper_spec())
    lhs2, rhs2, _ = sym.spec_to_lhs_rhs(_mass_spring_damper_spec_rearranged())
    assert sym.are_equivalent(lhs1, rhs1, lhs2, rhs2)


def test_are_equivalent_false_for_different_equation():
    lhs1, rhs1, _ = sym.spec_to_lhs_rhs(_mass_spring_damper_spec())
    different = _mass_spring_damper_spec()
    different["terms"][1]["coefficient"] = 3
    lhs2, rhs2, _ = sym.spec_to_lhs_rhs(different)
    assert not sym.are_equivalent(lhs1, rhs1, lhs2, rhs2)


def test_named_forcing_shapes_are_deterministic_across_calls():
    spec = _mass_spring_damper_spec()
    spec["rhs_forcing"] = {"type": "sin", "params": {"amplitude": 2, "frequency": 3, "phase": 0}, "expr": None}
    lhs_a, rhs_a, _ = sym.spec_to_lhs_rhs(spec)
    lhs_b, rhs_b, _ = sym.spec_to_lhs_rhs(spec)
    assert sym.canonical_srepr(sym.canonical_expr(lhs_a, rhs_a)) == sym.canonical_srepr(
        sym.canonical_expr(lhs_b, rhs_b)
    )


def test_safe_sympify_rejects_unparseable_expression():
    try:
        sym.safe_sympify("this is not @@ valid", {})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_mixed_partial_pde_term_builds():
    spec = {
        "spec_version": "1.0",
        "domain_type": "PDE",
        "independent_vars": ["x", "t"],
        "dependent_var": "u",
        "order": 2,
        "terms": [
            {"derivative_order": 2, "wrt": ["x", "x"], "coefficient": 1},
            {"derivative_order": 1, "wrt": "t", "coefficient": -1},
        ],
        "rhs_forcing": {"type": "zero", "params": {}, "expr": None},
        "initial_conditions": None,
        "boundary_conditions": None,
        "input_source": "web_builder",
        "raw_text": None,
    }
    lhs, rhs, table = sym.spec_to_lhs_rhs(spec)
    assert rhs == 0
    assert "x" in table and "t" in table and "u" in table
