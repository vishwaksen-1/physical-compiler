# api/index.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import sys
import os

# Add src to path so that we can import later (stub doesn't need it yet)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

app = FastAPI()

# -------------------- Health --------------------
@app.get("/api/health")
async def health():
    return {"status": "ok", "compiler_version": "0.0.1"}

# -------------------- Stub: Parse --------------------
class ParseRequest(BaseModel):
    raw_text: str

@app.post("/api/parse")
async def parse_equation(req: ParseRequest):
    # Return a mock EquationSpec derived from the raw text (for demonstration)
    # In reality, this would call src.parser.parse_equation
    mock_spec = {
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
        "rhs_forcing": {
            "type": "sin",
            "params": {"amplitude": 1.0, "frequency": 1.0, "phase": 0.0},
            "expr": None
        },
        "initial_conditions": {"y": 1.0, "yprime": 0.0},
        "boundary_conditions": None,
        "input_source": "text_parser",
        "raw_text": req.raw_text
    }
    return mock_spec

# -------------------- Stub: Compile --------------------
class CompileRequest(BaseModel):
    raw_text: Optional[str] = None
    builder_state: Optional[Dict[str, Any]] = None
    config: Dict[str, Any]

@app.post("/api/compile")
async def compile_equation(req: CompileRequest):
    # Ensure exactly one input is provided
    if (req.raw_text is None) == (req.builder_state is None):
        raise HTTPException(status_code=422, detail="Exactly one of raw_text or builder_state must be provided")

    # Use the input to build a mock response.
    # If builder_state is present, we can echo its values; otherwise use raw_text.
    input_spec = None
    if req.builder_state:
        input_spec = req.builder_state
    else:
        # generate a mock spec from raw_text (simplified)
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
            "raw_text": req.raw_text
        }

    # Build a full mock ExperimentOutput
    mock_output = {
        "compiler_version": "0.0.1",
        "model_database_version": "0.1.0",
        "config": req.config,
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
            "source_spec_ref": "mock"
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
        "alternative_candidates": [
            {
                "candidate_id": "cand_002",
                "model_id": "rlc_series",
                "parameter_values": {"L": 1.0, "R": 0.5, "C": 0.5},
                "verification_status": "APPROXIMATE",
                "residual_expr": "0.01*sin(t)",
                "assumptions": ["linear"],
                "score": {"exactness": 0.7, "feasibility": 0.8, "simplicity": 0.6, "total": 0.71},
                "transformation_trace": {
                    "original_problem": "y'' + 0.5 y' + 2 y = sin(t)",
                    "transformed_problem": "i'' + (R/L) i' + (1/(LC)) i = (1/L) sin(t)",
                    "transformation_type": "scaled",
                    "symbolic_derivation_steps": ["Scaled to electrical domain"],
                    "equivalence_status": "approximate"
                }
            }
        ],
        "experiment_description": (
            "The input differential equation y'' + 0.5 y' + 2 y = sin(t) was matched to a mass-spring-damper system with m=1.0, c=0.5, k=2.0. "
            "This is an exact match. The system is underdamped and the forcing is sinusoidal. Suggested experiment: apply a sinusoidal force and measure displacement."
        ),
        "build_instructions": {
            "components": ["mass", "spring", "damper", "force actuator", "displacement sensor"],
            "assembly": "Connect mass to spring and damper in parallel, attach actuator to mass.",
            "parameters": {"m": 1.0, "c": 0.5, "k": 2.0}
        },
        "measurement_plan": {
            "measurements": [
                {"variable": "y", "sensor": "displacement sensor", "sampling_rate": 100}
            ],
            "conditions": "ambient temperature 25°C"
        },
        "warnings": ["None"]
    }
    return mock_output

# -------------------- Stub: Models --------------------
@app.get("/api/models")
async def list_models():
    return {
        "models": [
            {"model_id": "mass_spring_damper", "display_name": "Mass-Spring-Damper", "domain": "mechanical"},
            {"model_id": "rlc_series", "display_name": "Series RLC Circuit", "domain": "electrical"},
            {"model_id": "rc_circuit", "display_name": "RC Circuit", "domain": "electrical"},
            {"model_id": "cooling_law", "display_name": "Newton's Cooling Law", "domain": "thermal"},
            {"model_id": "torsional_pendulum", "display_name": "Torsional Pendulum", "domain": "mechanical"},
        ]
    }