"""Tests for cli/physcompile.py -- invoked via subprocess, matching how a
real user actually runs it (this is a CLI entry point, not a library import).

Run with: pytest tests/unit/cli/test_physcompile.py -v
"""
import json
import os
import subprocess
import sys

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_CLI = os.path.join(_REPO_ROOT, "cli", "physcompile.py")


def run_cli(*args):
    env = dict(os.environ, PYTHONHASHSEED="0")
    return subprocess.run(
        [sys.executable, _CLI, *args],
        cwd=_REPO_ROOT, env=env, capture_output=True, text=True, timeout=30,
    )


class TestHumanOutput:
    def test_successful_compile_exits_zero_and_names_the_model(self):
        result = run_cli("y'' + 2y' + 5y = 0")
        assert result.returncode == 0
        assert "Mass-Spring-Damper" in result.stdout
        assert "Fill in the setup:" in result.stdout
        assert "EXACT" in result.stdout

    def test_typesets_the_equation_at_the_top(self):
        result = run_cli("y'' + 2y' + 5y = 0")
        assert "y\u2032\u2032" in result.stdout  # double-prime for the 2nd derivative

    def test_no_match_exits_nonzero_with_graceful_message(self):
        result = run_cli("y''' + y'' + y' + y = 0")
        assert result.returncode == 1
        assert "No physical model" in result.stdout

    def test_parse_error_exits_nonzero_with_message_on_stderr(self):
        result = run_cli("not an equation")
        assert result.returncode == 1
        assert "Couldn't compile" in result.stderr


class TestFlags:
    def test_json_flag_prints_valid_experiment_output(self):
        result = run_cli("y'' + 2y' + 5y = 0", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["selected_candidate"]["model_id"] == "mass_spring_damper"
        assert "description_blanks" in data

    def test_seed_is_echoed_and_reproducible(self):
        r1 = run_cli("y' + 4y = 0", "--seed", "42", "--json")
        r2 = run_cli("y' + 4y = 0", "--seed", "42", "--json")
        d1, d2 = json.loads(r1.stdout), json.loads(r2.stdout)
        assert d1["config"]["candidate_seed"] == 42
        assert d1["selected_candidate"]["model_id"] == d2["selected_candidate"]["model_id"]

    def test_spec_file(self, tmp_path):
        spec = {
            "spec_version": "1.0", "domain_type": "ODE", "independent_vars": ["t"],
            "dependent_var": "y", "order": 1,
            "terms": [
                {"derivative_order": 1, "wrt": "t", "coefficient": 1},
                {"derivative_order": 0, "wrt": "t", "coefficient": 4},
            ],
            "rhs_forcing": {"type": "zero", "params": {}, "expr": None},
            "initial_conditions": None, "boundary_conditions": None,
        }
        spec_file = tmp_path / "spec.json"
        spec_file.write_text(json.dumps(spec))
        result = run_cli("--spec-file", str(spec_file))
        assert result.returncode == 0
        assert "rc_circuit" in result.stdout.lower() or "RC Circuit" in result.stdout


class TestArgValidation:
    def test_no_arguments_is_a_usage_error(self):
        result = run_cli()
        assert result.returncode == 2

    def test_both_equation_and_spec_file_is_a_usage_error(self, tmp_path):
        spec_file = tmp_path / "spec.json"
        spec_file.write_text("{}")
        result = run_cli("y' + y = 0", "--spec-file", str(spec_file))
        assert result.returncode == 2


class TestBrokenPipe:
    def test_piping_into_head_does_not_traceback(self):
        # Regression check for the BrokenPipeError fix -- run through a real
        # shell pipeline to `head`, and confirm no traceback reaches stderr.
        result = subprocess.run(
            f'{sys.executable} {_CLI} "y\'\' + 2y\' + 5y = 0" | head -1',
            shell=True, cwd=_REPO_ROOT, capture_output=True, text=True, timeout=30,
        )
        assert "Traceback" not in result.stderr
        assert "BrokenPipeError" not in result.stderr
