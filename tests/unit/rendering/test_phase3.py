"""Unit tests for src/rendering/ (deterministic NLG) and src/errors/
(error/approximation/safety modeling) — Phase 3.

Run with: pytest tests/unit/rendering/test_phase3.py -v
"""

import pytest

from src.api import compile_equation
from src.errors import analyze_candidate, _edge_position
from src.physics.models import get_model
from src.rendering import render_description


class TestRenderDescription:
    def test_description_names_the_model_and_parameters(self):
        output = compile_equation("y'' + 2y' + 5y = 0", None, {})
        text = output.experiment_description
        assert "Mass-Spring-Damper" in text
        assert "m = " in text and "k = " in text

    def test_description_reports_exact_verification(self):
        output = compile_equation("y'' + 2y' + 5y = 0", None, {})
        assert "exact" in output.experiment_description.lower()

    def test_description_lists_alternative_realizations(self):
        output = compile_equation("y'' + 2y' + 5y = 0", None, {})
        text = output.experiment_description
        assert "RLC" in text or "Torsional" in text
        assert "identical governing mathematics" in text

    def test_default_mode_apparatus_and_values_are_deterministic_but_prose_may_vary(self):
        # Supersedes the old test_description_is_deterministic, which
        # asserted the full description string was byte-identical -- no
        # longer true, and deliberately so, per the human's clarification
        # that "deterministic by construction" means "no LLM/API calls,"
        # not "the wording never changes." See src/rendering/__init__.py's
        # module docstring RANDOMIZATION NOTE.
        a = compile_equation("y'' + 2y' + 5y = 0", None, {})
        b = compile_equation("y'' + 2y' + 5y = 0", None, {})
        # What must still never vary: which apparatus, and its numbers.
        assert a.selected_candidate.model_id == b.selected_candidate.model_id
        assert a.selected_candidate.parameter_values == b.selected_candidate.parameter_values
        assert a.selected_candidate.verification_status == b.selected_candidate.verification_status
        # What's now allowed to vary: the prose itself, over enough trials.
        seen = {compile_equation("y'' + 2y' + 5y = 0", None, {}).experiment_description for _ in range(30)}
        assert len(seen) > 1, "expected some variation in default-mode prose over 30 trials"

    def test_no_match_description_is_graceful(self):
        output = compile_equation("y''' + y'' + y' + y = 0", None, {})
        text = output.experiment_description
        assert "No physical model" in text
        assert output.selected_candidate is None

    def test_description_mentions_forcing_when_driven(self):
        builder_state = {
            "spec_version": "1.0", "domain_type": "ODE", "independent_vars": ["t"],
            "dependent_var": "y", "order": 2,
            "terms": [
                {"derivative_order": 2, "wrt": "t", "coefficient": 1.0},
                {"derivative_order": 1, "wrt": "t", "coefficient": 2.0},
                {"derivative_order": 0, "wrt": "t", "coefficient": 5.0},
            ],
            "rhs_forcing": {"type": "sin", "params": {"amplitude": 1.0, "frequency": 1.0, "phase": 0.0}, "expr": None},
            "initial_conditions": None, "boundary_conditions": None,
        }
        output = compile_equation(None, builder_state, {})
        assert "sinusoidal" in output.experiment_description


class TestRenderFillBlanks:
    def test_blanks_match_paragraph_values_and_order(self):
        from src.rendering import render_fill_blanks

        output = compile_equation("y'' + 2y' + 5y = 0", None, {})
        blanks = render_fill_blanks(output)
        symbols = [b["symbol"] for b in blanks]
        assert symbols == ["m", "c", "k"]  # mass_spring_damper's parameter_map order
        for b in blanks:
            assert b["template"] == f"{b['label']} ({b['symbol']})"
            # every blank's value must appear verbatim in the prose paragraph
            assert b["value"] in output.experiment_description

    def test_blanks_are_deterministic(self):
        from src.rendering import render_fill_blanks

        a = render_fill_blanks(compile_equation("y'' + 2y' + 5y = 0", None, {}))
        b = render_fill_blanks(compile_equation("y'' + 2y' + 5y = 0", None, {}))
        assert a == b

    def test_no_match_returns_empty_list_not_an_error(self):
        from src.rendering import render_fill_blanks

        output = compile_equation("y''' + y'' + y' + y = 0", None, {})
        assert render_fill_blanks(output) == []

    def test_compile_equation_populates_description_blanks(self):
        output = compile_equation("y' + 4y = 0", None, {})
        d = output.to_dict()
        assert d["description_blanks"]
        assert {"symbol", "label", "template", "value", "unit"} <= set(d["description_blanks"][0])


class TestQuirkyPreamble:
    def test_default_mode_prose_varies_across_calls(self):
        # Was "has no preamble" / asserted a fixed prefix -- deliberately
        # reversed. See src/rendering/__init__.py's RANDOMIZATION NOTE:
        # default mode now genuinely varies wording (true randomness, not
        # seeded), while apparatus selection and parameter values do not.
        seen = {compile_equation("y'' + 2y' + 5y = 0", None, {}).experiment_description for _ in range(30)}
        assert len(seen) > 1

    def test_default_mode_always_contains_the_substantive_content_regardless_of_wording(self):
        # However the opening/lead phrasing varies, the actual physics
        # content -- model name, verification verdict -- must always be
        # present. Randomizing prose must never randomize substance.
        for _ in range(10):
            output = compile_equation("y'' + 2y' + 5y = 0", None, {})
            assert "Mass-Spring-Damper" in output.experiment_description
            assert "exact" in output.experiment_description.lower()

    def test_seeded_mode_adds_a_reproducible_preamble(self):
        cfg = {"candidate_selection_mode": "seeded_random", "candidate_seed": 7}
        d1 = compile_equation("y'' + 2y' + 5y = 0", None, cfg).experiment_description
        d2 = compile_equation("y'' + 2y' + 5y = 0", None, cfg).experiment_description
        assert d1 == d2

    def test_different_seeds_can_give_different_preambles(self):
        seen = set()
        for seed in range(8):
            cfg = {"candidate_selection_mode": "seeded_random", "candidate_seed": seed}
            d = compile_equation("y'' + 2y' + 5y = 0", None, cfg).experiment_description
            seen.add(d.split("This second-order")[0])
        assert len(seen) > 1

    def test_seeded_mode_apparatus_selection_still_fully_reproducible(self):
        # The ACTUAL contract guarantee (INTERFACE_CONTRACTS.md §6) that
        # must hold regardless of any prose randomization: same seed ->
        # same apparatus, same parameter values, every time.
        cfg = {"candidate_selection_mode": "seeded_random", "candidate_seed": 7}
        out1 = compile_equation("y'' + 2y' + 5y = 0", None, cfg)
        out2 = compile_equation("y'' + 2y' + 5y = 0", None, cfg)
        assert out1.selected_candidate.model_id == out2.selected_candidate.model_id
        assert out1.selected_candidate.parameter_values == out2.selected_candidate.parameter_values


class TestEdgePosition:
    def test_log_scale_used_for_positive_ranges(self):
        # geometric mean of [0.01, 5.0] should land mid-range on a log axis,
        # NOT near the bottom (the false positive this fixed).
        import math

        geometric_mean = math.sqrt(0.01 * 5.0)
        position = _edge_position(geometric_mean, 0.01, 5.0)
        assert position == pytest.approx(0.5, abs=1e-9)

    def test_linear_scale_when_lower_bound_is_zero(self):
        assert _edge_position(10.0, 0.0, 20.0) == pytest.approx(0.5)

    def test_out_of_range_returns_none(self):
        assert _edge_position(50.0, 0.0, 20.0) is None
        assert _edge_position(-1.0, 0.0, 20.0) is None

    def test_degenerate_range_returns_none(self):
        assert _edge_position(1.0, 5.0, 5.0) is None


class TestAnalyzeCandidate:
    def test_safety_notes_are_surfaced(self):
        output = compile_equation("y'' + 2y' + 5y = 0", None, {})
        assert any(w.startswith("Safety:") for w in output.warnings)

    def test_warnings_are_deterministic(self):
        a = compile_equation("y'' + 2y' + 5y = 0", None, {}).warnings
        b = compile_equation("y'' + 2y' + 5y = 0", None, {}).warnings
        assert a == b

    def test_no_spurious_edge_warning_for_anchored_midrange_parameter(self):
        # m is the anchored (geometric-mean) parameter for mass_spring_damper;
        # it must NOT be flagged as near a bound -- see _edge_position's
        # log-scale rationale.
        output = compile_equation("y'' + 2y' + 5y = 0", None, {})
        assert not any(w.startswith("m = ") for w in output.warnings)


class TestFeasibilityGapClosed:
    """The Phase 2 session flagged that mass_spring_damper/series_rlc/
    torsional_pendulum were each missing a dimensional_constraints entry for
    their second state variable, permanently docking feasibility by 0.25."""

    @pytest.mark.parametrize("equation", ["y'' + 2y' + 5y = 0", "y' + 4y = 0"])
    def test_no_dimensional_constraint_violations(self, equation):
        output = compile_equation(equation, None, {})
        assert not any("no dimensional_constraints entry" in w for w in output.warnings)

    def test_selected_candidate_has_full_feasibility(self):
        output = compile_equation("y'' + 2y' + 5y = 0", None, {})
        assert output.selected_candidate.score.feasibility == pytest.approx(1.0)
