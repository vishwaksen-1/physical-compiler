"""Phase 2 integration tests: the full compile_equation() pipeline,
covering PROJECT_PLAN.md's Phase 2 definition-of-done examples
(mass-spring-damper + RLC) plus the web builder_state path and the HTTP
layer in api/index.py.

Run with: pytest tests/integration/test_phase2_pipeline.py -v
"""

import asyncio
import sys
import os

import httpx
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.api import compile_equation


class TestCompileEquationTextPath:
    def test_mass_spring_damper_worked_example(self):
        # y'' + 2y' + 5y = 0 -- underdamped 2nd-order homogeneous
        output = compile_equation("y'' + 2y' + 5y = 0", None, {})
        d = output.to_dict()
        assert d["selected_candidate"]["model_id"] == "mass_spring_damper"
        assert d["selected_candidate"]["verification_status"] == "EXACT"
        assert d["canonical_ir"]["order"] == 2
        assert d["canonical_ir"]["homogeneity"] == "homogeneous"
        model_ids = {c["model_id"] for c in [d["selected_candidate"], *d["alternative_candidates"]]}
        assert "series_rlc" in model_ids  # RLC must appear as an alt realization of the same class

    def test_rlc_class_reachable_and_exact_when_component_values_are_realistic(self):
        # y'' + 20y' + 5000y = 0 -- picked so both mass_spring_damper's and
        # series_rlc's *raw* solved component values already land inside
        # their declared parameter_constraints (no clamping needed), so
        # both verify EXACT. (The y''+2y'+5y=0 example above is a case
        # where RLC's ideal L/C values fall outside breadboard-safe
        # ranges and legitimately get clamped by synthesize_parameters,
        # then correctly caught as FAILED by verify_mapping -- see
        # tests/unit/verification/test_verification.py's clamping test
        # for that behavior in isolation.)
        output = compile_equation("y'' + 20y' + 5000y = 0", None, {})
        d = output.to_dict()
        rlc = next(
            c for c in [d["selected_candidate"], *d["alternative_candidates"]]
            if c["model_id"] == "series_rlc"
        )
        assert rlc["verification_status"] == "EXACT"

    def test_first_order_worked_example(self):
        output = compile_equation("y' + 4y = 0", None, {})
        d = output.to_dict()
        assert d["selected_candidate"]["model_id"] == "rc_circuit"
        assert d["selected_candidate"]["verification_status"] == "EXACT"

    def test_experiment_output_is_schema_complete(self):
        output = compile_equation("y'' + 2y' + 5y = 0", None, {})
        d = output.to_dict()
        for key in (
            "compiler_version", "model_database_version", "config", "input_equation_spec",
            "canonical_ir", "selected_candidate", "alternative_candidates",
            "experiment_description", "build_instructions", "measurement_plan", "warnings",
        ):
            assert key in d, key

    def test_no_match_returns_empty_candidates_not_a_crash(self):
        # order 3 isn't in the supported family -> no candidates, but a
        # valid, schema-complete ExperimentOutput with a warning.
        spec_text = "y''' + y'' + y' + y = 0"
        output = compile_equation(spec_text, None, {})
        d = output.to_dict()
        assert d["selected_candidate"] is None
        assert d["alternative_candidates"] == []
        assert any("no physical model" in w.lower() for w in d["warnings"])


class TestCompileEquationWebPath:
    def test_builder_state_path_matches_text_path(self):
        builder_state = {
            "spec_version": "1.0", "domain_type": "ODE", "independent_vars": ["t"],
            "dependent_var": "y", "order": 2,
            "terms": [
                {"derivative_order": 2, "wrt": "t", "coefficient": 1.0},
                {"derivative_order": 1, "wrt": "t", "coefficient": 2.0},
                {"derivative_order": 0, "wrt": "t", "coefficient": 5.0},
            ],
            "rhs_forcing": {"type": "zero", "params": {}, "expr": None},
            "initial_conditions": None, "boundary_conditions": None,
        }
        output = compile_equation(None, builder_state, {})
        d = output.to_dict()
        assert d["input_equation_spec"]["input_source"] == "web_builder"
        assert d["selected_candidate"]["model_id"] == "mass_spring_damper"

    def test_rejects_both_inputs_present(self):
        with pytest.raises(ValueError):
            compile_equation("y'' + y = 0", {"domain_type": "ODE"}, {})

    def test_rejects_neither_input_present(self):
        with pytest.raises(ValueError):
            compile_equation(None, None, {})


class TestDeterminism:
    def test_same_input_same_config_same_output(self):
        out1 = compile_equation("y'' + 2y' + 5y = 0", None, {}).to_dict()
        out2 = compile_equation("y'' + 2y' + 5y = 0", None, {}).to_dict()
        assert out1["selected_candidate"] == out2["selected_candidate"]
        assert out1["config"] == out2["config"] == {"candidate_selection_mode": "deterministic_top_rank", "candidate_seed": None}

    def test_seeded_random_echoes_seed_and_is_reproducible(self):
        cfg = {"candidate_selection_mode": "seeded_random", "candidate_seed": 123}
        out1 = compile_equation("y'' + 2y' + 5y = 0", None, cfg).to_dict()
        out2 = compile_equation("y'' + 2y' + 5y = 0", None, cfg).to_dict()
        assert out1["config"]["candidate_seed"] == 123
        assert out1["selected_candidate"]["model_id"] == out2["selected_candidate"]["model_id"]


class _SyncASGIClient:
    """Minimal sync wrapper around httpx.AsyncClient + ASGITransport.

    Not using starlette.testclient.TestClient here: its implementation
    still passes the now-removed `app=` shortcut straight to
    httpx.Client.__init__(), which recent httpx versions reject outright
    (`TypeError: Client.__init__() got an unexpected keyword argument
    'app'`) -- see docs/STATUS.md. This sidesteps that version-coupling
    entirely rather than pinning an old httpx (which may not even have
    wheels for whatever Python version is running these tests).
    """

    def __init__(self, app):
        self._transport = httpx.ASGITransport(app=app)
        self._base_url = "http://testserver"

    def _request(self, method, path, **kwargs):
        async def _do():
            async with httpx.AsyncClient(transport=self._transport, base_url=self._base_url) as client:
                return await client.request(method, path, **kwargs)

        return asyncio.run(_do())

    def get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)


class TestHttpLayer:
    """Exercises api/index.py's actual FastAPI routes -- the layer that was
    returning {"detail": "Not Found"} for everything before this session's
    pyproject.toml fix (see docs/STATUS.md). This doesn't test the Vercel
    routing itself (can't, from here) but does confirm the app object's own
    route table and request/response handling are correct."""

    @pytest.fixture
    def client(self):
        from api.index import app

        return _SyncASGIClient(app)

    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_models(self, client):
        r = client.get("/api/models")
        assert r.status_code == 200
        ids = {m["model_id"] for m in r.json()["models"]}
        assert len(ids) == 9
        assert "mass_spring_damper" in ids
        assert "optical_trap_oscillator" in ids

    def test_parse(self, client):
        r = client.post("/api/parse", json={"raw_text": "y'' + 2y' + 5y = 0"})
        assert r.status_code == 200
        assert r.json()["order"] == 2

    def test_parse_invalid_returns_422(self, client):
        r = client.post("/api/parse", json={"raw_text": "not an equation at all"})
        assert r.status_code == 422

    def test_compile_text(self, client):
        r = client.post("/api/compile", json={"raw_text": "y'' + 2y' + 5y = 0", "builder_state": None, "config": {}})
        assert r.status_code == 200
        assert r.json()["selected_candidate"]["model_id"] == "mass_spring_damper"

    def test_compile_rejects_both_none(self, client):
        r = client.post("/api/compile", json={"raw_text": None, "builder_state": None, "config": {}})
        assert r.status_code == 422
