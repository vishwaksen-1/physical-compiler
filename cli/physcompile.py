#!/usr/bin/env python3
# cli/physcompile.py
"""
Stub CLI for the Physical Compiler.
Eventually calls src.api.compile_equation directly.
"""
import argparse
import json
import sys
from typing import Optional, Dict, Any

# For mocking, we can reuse the same stub logic from api/index.py but that's not ideal.
# We'll just print a mock output.
def mock_compile(raw_text: Optional[str], builder_state: Optional[Dict], config: Dict) -> Dict:
    # Return a simple mock that echoes input
    input_spec = None
    if builder_state:
        input_spec = builder_state
    else:
        input_spec = {
            "spec_version": "1.0",
            "domain_type": "ODE",
            "independent_vars": ["t"],
            "dependent_var": "y",
            "order": 2,
            "terms": [
                {"derivative_order": 2, "wrt": ["t"], "coefficient": 1.0},
                {"derivative_order": 1, "wrt": ["t"], "coefficient": 0.5},
                {"derivative_order": 0, "wrt": ["t"], "coefficient": 2.0}
            ],
            "rhs_forcing": {"type": "sin", "params": {"amplitude": 1.0, "frequency": 1.0, "phase": 0.0}, "expr": None},
            "initial_conditions": {"y": 1.0, "yprime": 0.0},
            "boundary_conditions": None,
            "input_source": "text_parser",
            "raw_text": raw_text
        }

    return {
        "compiler_version": "0.0.1",
        "model_database_version": "0.1.0",
        "config": config,
        "input_equation_spec": input_spec,
        "canonical_ir": {
            "ir_version": "1.0",
            "canonical_form": "y'' + 0.5*y' + 2*y = sin(t)",
            "domain_type": "ODE",
            "order": 2,
            "linearity": "linear",
            "homogeneity": "nonhomogeneous",
            "independent_vars": ["t"],
            "dependent_var": "y",
            "coefficients": {"y''": "1.0", "y'": "0.5", "y": "2.0"},
            "forcing_term": "sin(t)",
            "classification_tags": ["second_order", "constant_coefficient", "linear"],
            "equivalence_hash": "abc123",
            "source_spec_ref": "cli_mock"
        },
        "selected_candidate": {
            "candidate_id": "cand_001",
            "model_id": "mass_spring_damper",
            "parameter_values": {"m": 1.0, "c": 0.5, "k": 2.0},
            "verification_status": "EXACT",
            "residual_expr": "0.0",
            "assumptions": ["linear", "small_damping"],
            "score": {"exactness": 0.95, "feasibility": 0.9, "simplicity": 0.8, "total": 0.92},
            "transformation_trace": {
                "original_problem": "y'' + 0.5 y' + 2 y = sin(t)",
                "transformed_problem": "same",
                "transformation_type": "direct",
                "symbolic_derivation_steps": ["Matched coefficients directly"],
                "equivalence_status": "exact"
            }
        },
        "alternative_candidates": [],
        "experiment_description": "Mock CLI output: equation matched to mass-spring-damper.",
        "build_instructions": {},
        "measurement_plan": {},
        "warnings": []
    }

def main():
    parser = argparse.ArgumentParser(description="Physical Compiler CLI (stub)")
    parser.add_argument("--raw-text", type=str, help="Raw equation text")
    parser.add_argument("--builder-state", type=str, help="JSON string of EquationSpec from builder")
    parser.add_argument("--config", type=str, required=True, help="JSON string of config")
    args = parser.parse_args()

    if (args.raw_text is None) == (args.builder_state is None):
        print("Error: Exactly one of --raw-text or --builder-state must be provided.", file=sys.stderr)
        sys.exit(1)

    builder_state = None
    if args.builder_state:
        try:
            builder_state = json.loads(args.builder_state)
        except json.JSONDecodeError:
            print("Error: builder-state must be valid JSON", file=sys.stderr)
            sys.exit(1)

    try:
        config = json.loads(args.config)
    except json.JSONDecodeError:
        print("Error: config must be valid JSON", file=sys.stderr)
        sys.exit(1)

    result = mock_compile(args.raw_text, builder_state, config)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()