"""Unit tests for src/synthesis/ (Phase 2: generate_candidates,
synthesize_parameters, rank_candidates).

Run with: pytest tests/unit/synthesis/test_synthesis.py -v
"""

import pytest

from src.canonical.ir import canonicalize
from src.classifier.classifier import classify
from src.physics.models import get_registry, get_model
from src.synthesis import generate_candidates, rank_candidates, synthesize_parameters
from src.synthesis.candidate import CandidateMapping, Score


def _ir_for(order, coeffs, forcing=None, dependent_var="y"):
    """coeffs: dict order->coefficient (float), e.g. {2: 1.0, 1: 2.0, 0: 5.0}."""
    terms = [{"derivative_order": n, "wrt": "t", "coefficient": c} for n, c in coeffs.items()]
    spec = {
        "spec_version": "1.0", "domain_type": "ODE", "independent_vars": ["t"],
        "dependent_var": dependent_var, "order": order, "terms": terms,
        "rhs_forcing": forcing or {"type": "zero", "params": {}, "expr": None},
        "initial_conditions": None, "boundary_conditions": None,
        "input_source": "text_parser", "raw_text": "test",
    }
    ir = canonicalize(spec)
    classify(ir)
    return ir


class TestGenerateCandidates:
    def test_second_order_matches_all_five_second_order_models(self):
        ir = _ir_for(2, {2: 1.0, 1: 2.0, 0: 5.0})
        candidates = generate_candidates(ir, get_registry())
        model_ids = {c.model_id for c in candidates}
        assert model_ids == {"mass_spring_damper", "series_rlc", "torsional_pendulum", "mirror_ringdown", "optical_trap_oscillator"}

    def test_first_order_decay_matches_three_decay_models(self):
        ir = _ir_for(1, {1: 1.0, 0: 4.0})  # decay equation: y' + 4y = 0
        candidates = generate_candidates(ir, get_registry())
        model_ids = {c.model_id for c in candidates}
        assert model_ids == {"rc_circuit", "newtons_cooling", "nmr_relaxation"}
        assert "expansion_analog" not in model_ids  # growth model excluded

    def test_first_order_growth_matches_only_expansion_analog(self):
        ir = _ir_for(1, {1: 1.0, 0: -4.0})  # growth equation: y' - 4y = 0
        candidates = generate_candidates(ir, get_registry())
        model_ids = {c.model_id for c in candidates}
        assert model_ids == {"expansion_analog"}
        analog = candidates[0]
        assert analog.parameter_values["H"] == pytest.approx(4.0)

    def test_newtons_cooling_solves_directly_no_anchoring(self):
        ir = _ir_for(1, {1: 1.0, 0: 4.0})
        candidates = generate_candidates(ir, get_registry())
        cooling = next(c for c in candidates if c.model_id == "newtons_cooling")
        assert cooling.parameter_values["k"] == pytest.approx(4.0)
        assert cooling.transformation_trace.transformation_type == "direct"
        assert not any("fixed to" in a for a in cooling.assumptions)

    def test_rc_circuit_needs_anchoring_and_reproduces_target_time_constant(self):
        ir = _ir_for(1, {1: 1.0, 0: 4.0})  # time constant tau = 1/4
        candidates = generate_candidates(ir, get_registry())
        rc = next(c for c in candidates if c.model_id == "rc_circuit")
        assert rc.transformation_trace.transformation_type == "scaled"
        r, c = rc.parameter_values["R"], rc.parameter_values["C"]
        assert r * c == pytest.approx(1.0 / 4.0, rel=1e-6)

    def test_mass_spring_damper_underdetermined_but_ratios_correct(self):
        ir = _ir_for(2, {2: 1.0, 1: 2.0, 0: 5.0})
        candidates = generate_candidates(ir, get_registry())
        msd = next(c for c in candidates if c.model_id == "mass_spring_damper")
        m, c_, k = msd.parameter_values["m"], msd.parameter_values["c"], msd.parameter_values["k"]
        assert c_ / m == pytest.approx(2.0, rel=1e-6)
        assert k / m == pytest.approx(5.0, rel=1e-6)

    def test_nonlinear_or_unsupported_shape_returns_empty(self):
        # order 0 isn't a supported class -> no required_class_tag -> []
        ir = _ir_for(0, {0: 1.0})
        assert generate_candidates(ir, get_registry()) == []

    def test_pde_returns_empty(self):
        spec = {
            "spec_version": "1.0", "domain_type": "PDE", "independent_vars": ["x", "t"],
            "dependent_var": "u", "order": 2,
            "terms": [{"derivative_order": 2, "wrt": "x", "coefficient": 1.0}],
            "rhs_forcing": {"type": "zero", "params": {}, "expr": None},
            "initial_conditions": None, "boundary_conditions": None,
            "input_source": "text_parser", "raw_text": "test",
        }
        ir = canonicalize(spec)
        classify(ir)
        assert generate_candidates(ir, get_registry()) == []

    def test_forcing_shape_does_not_affect_matching(self):
        forcing = {"type": "sin", "params": {"amplitude": 1.0, "frequency": 1.0, "phase": 0.0}, "expr": None}
        ir = _ir_for(2, {2: 1.0, 1: 2.0, 0: 5.0}, forcing=forcing)
        candidates = generate_candidates(ir, get_registry())
        assert {c.model_id for c in candidates} == {"mass_spring_damper", "series_rlc", "torsional_pendulum", "mirror_ringdown", "optical_trap_oscillator"}

    def test_candidate_ids_are_unique(self):
        ir = _ir_for(2, {2: 1.0, 1: 2.0, 0: 5.0})
        candidates = generate_candidates(ir, get_registry())
        ids = [c.candidate_id for c in candidates]
        assert len(ids) == len(set(ids))

    def test_deterministic_across_repeated_calls(self):
        ir1 = _ir_for(2, {2: 1.0, 1: 2.0, 0: 5.0})
        ir2 = _ir_for(2, {2: 1.0, 1: 2.0, 0: 5.0})
        c1 = generate_candidates(ir1, get_registry())
        c2 = generate_candidates(ir2, get_registry())
        assert [c.model_id for c in c1] == [c.model_id for c in c2]
        assert [c.parameter_values for c in c1] == [c.parameter_values for c in c2]


class TestSynthesizeParameters:
    def test_idempotent_when_already_in_range(self):
        candidate = CandidateMapping(
            candidate_id="x", model_id="newtons_cooling", parameter_values={"k": 0.01},
        )
        once = synthesize_parameters(candidate)
        twice = synthesize_parameters(once)
        assert once.parameter_values == twice.parameter_values == {"k": 0.01}
        assert once.assumptions == []

    def test_clamps_out_of_range_value_and_logs_assumption(self):
        candidate = CandidateMapping(
            candidate_id="x", model_id="newtons_cooling", parameter_values={"k": 4.0},
        )
        result = synthesize_parameters(candidate)
        assert result.parameter_values["k"] == pytest.approx(0.05)  # newtons_cooling's declared max
        assert any("clamped" in a for a in result.assumptions)


class TestRankCandidates:
    def test_deterministic_top_rank_picks_highest_total(self):
        policy = {"weights": {"exactness": 0.5, "feasibility": 0.3, "simplicity": 0.2}}
        low = CandidateMapping(candidate_id="a", model_id="x", score=Score(exactness=0.5, feasibility=0.5, simplicity=0.5))
        high = CandidateMapping(candidate_id="b", model_id="y", score=Score(exactness=1.0, feasibility=1.0, simplicity=1.0))
        ranked = rank_candidates([low, high], policy, None)
        assert ranked[0].candidate_id == "b"

    def test_tie_break_is_registry_insertion_order_not_reshuffled(self):
        policy = {"weights": {"exactness": 1.0, "feasibility": 0.0, "simplicity": 0.0}}
        first = CandidateMapping(candidate_id="first", model_id="x", score=Score(exactness=1.0))
        second = CandidateMapping(candidate_id="second", model_id="y", score=Score(exactness=1.0))
        ranked = rank_candidates([first, second], policy, None)
        assert [c.candidate_id for c in ranked] == ["first", "second"]

    def test_seeded_random_is_reproducible(self):
        policy = {"weights": {"exactness": 1.0, "feasibility": 0.0, "simplicity": 0.0}}
        candidates = [
            CandidateMapping(candidate_id=str(i), model_id="x", score=Score(exactness=1.0))
            for i in range(6)
        ]
        ranked1 = rank_candidates(list(candidates), policy, 7)
        ranked2 = rank_candidates(list(candidates), policy, 7)
        assert [c.candidate_id for c in ranked1] == [c.candidate_id for c in ranked2]
