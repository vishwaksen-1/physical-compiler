"""Unit tests for src/verification/ (Phase 2: verify_mapping).

Run with: pytest tests/unit/verification/test_verification.py -v
"""

import pytest

from src.canonical.ir import canonicalize
from src.classifier.classifier import classify
from src.physics.models import get_registry
from src.synthesis import generate_candidates, synthesize_parameters
from src.synthesis.candidate import CandidateMapping
from src.verification import verify_mapping


def _ir_for(order, coeffs, forcing=None):
    terms = [{"derivative_order": n, "wrt": "t", "coefficient": c} for n, c in coeffs.items()]
    spec = {
        "spec_version": "1.0", "domain_type": "ODE", "independent_vars": ["t"],
        "dependent_var": "y", "order": order, "terms": terms,
        "rhs_forcing": forcing or {"type": "zero", "params": {}, "expr": None},
        "initial_conditions": None, "boundary_conditions": None,
        "input_source": "text_parser", "raw_text": "test",
    }
    ir = canonicalize(spec)
    classify(ir)
    return ir


class TestVerifyMapping:
    def test_correctly_synthesized_candidate_verifies_exact(self):
        ir = _ir_for(2, {2: 1.0, 1: 2.0, 0: 5.0})
        candidate = next(c for c in generate_candidates(ir, get_registry()) if c.model_id == "mass_spring_damper")
        result = verify_mapping(ir, candidate)
        assert result.verification_status == "EXACT"
        assert result.residual_expr == "0"
        assert result.score.exactness == pytest.approx(1.0)

    def test_all_first_order_candidates_from_generate_candidates_verify_exact(self):
        ir = _ir_for(1, {1: 1.0, 0: 4.0})
        for candidate in generate_candidates(ir, get_registry()):
            result = verify_mapping(ir, candidate)
            assert result.verification_status == "EXACT", candidate.model_id

    def test_wrong_parameter_values_fail_verification(self):
        candidate = CandidateMapping(
            candidate_id="x", model_id="mass_spring_damper",
            parameter_values={"m": 1.0, "c": 1.0, "k": 1.0},  # doesn't match c/m=2, k/m=5
        )
        ir = _ir_for(2, {2: 1.0, 1: 2.0, 0: 5.0})
        result = verify_mapping(ir, candidate)
        assert result.verification_status == "FAILED"
        assert result.score.exactness == 0.0

    def test_clamped_out_of_range_candidate_correctly_fails(self):
        # k=4 solves y'+4y=0 exactly, but newtons_cooling's max k is 0.05 --
        # synthesize_parameters clamps it, and verify_mapping must catch that
        # the clamped value no longer actually solves the equation.
        ir = _ir_for(1, {1: 1.0, 0: 4.0})
        candidate = next(c for c in generate_candidates(ir, get_registry()) if c.model_id == "newtons_cooling")
        assert candidate.parameter_values["k"] == pytest.approx(4.0)  # raw solve, pre-synthesis
        clamped = synthesize_parameters(candidate)
        assert clamped.parameter_values["k"] == pytest.approx(0.05)
        result = verify_mapping(ir, clamped)
        assert result.verification_status == "FAILED"

    def test_incomplete_parameter_values_fail_gracefully(self):
        candidate = CandidateMapping(candidate_id="x", model_id="mass_spring_damper", parameter_values={"m": 1.0})
        ir = _ir_for(2, {2: 1.0, 1: 2.0, 0: 5.0})
        result = verify_mapping(ir, candidate)
        assert result.verification_status == "FAILED"

    def test_unknown_model_id_fails_gracefully(self):
        candidate = CandidateMapping(candidate_id="x", model_id="not_a_real_model", parameter_values={})
        ir = _ir_for(2, {2: 1.0, 1: 2.0, 0: 5.0})
        result = verify_mapping(ir, candidate)
        assert result.verification_status == "FAILED"
