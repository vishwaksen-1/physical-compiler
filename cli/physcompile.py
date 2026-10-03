#!/usr/bin/env python3
# cli/physcompile.py
"""
physcompile — local/dev CLI, calls src/api/ directly (not deployed to
Vercel; see PROJECT_PLAN.md §2). Same compile_equation() the web API and
tests call, so this can never drift from what the server actually does.

    $ physcompile "y'' + 2y' + 5y = 0"
    $ physcompile "y' + 4y = 0" --seed 42
    $ physcompile "y'' + 2y' + 5y = 0" --json
    $ physcompile --spec-file my_equation.json

No required flags beyond the equation itself. The previous version of this
file (found to be a hand-rolled mock returning a hardcoded fake response
regardless of input, requiring a mandatory `--config '{}'` just to run) is
gone -- see docs/STATUS.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from src.api import compile_equation  # noqa: E402

_PRIME = "\u2032"
_MINUS = "\u2212"


def _fmt_number(v: float) -> str:
    rounded = round(v, 4)
    return str(int(rounded)) if rounded == int(rounded) else str(rounded)


def _typeset(spec: dict) -> str:
    """Small Python port of web/typeset.js's typesetSpec(), for plain-text
    terminal output. Kept independently rather than shelling out to node --
    same logic, different rendering target (unicode text vs HTML spans)."""
    dep_var = spec.get("dependent_var", "y")
    terms = sorted(spec.get("terms", []), key=lambda t: -t["derivative_order"])
    parts = []

    for term in terms:
        value = float(term["coefficient"])
        if value == 0:
            continue
        magnitude = abs(value)
        sign = _MINUS if value < 0 else "+"
        coef_text = "" if magnitude == 1 else _fmt_number(magnitude)
        primes = _PRIME * term["derivative_order"]

        if parts:
            parts.append(sign)
        elif value < 0:
            parts.append(_MINUS)
        parts.append(f"{coef_text}{dep_var}{primes}")

    if not parts:
        parts = ["0"]

    t_name = (spec.get("independent_vars") or ["t"])[0]
    rhs = _typeset_forcing(spec.get("rhs_forcing") or {}, t_name)
    return f"{' '.join(parts)} = {rhs}"


def _typeset_forcing(forcing: dict, t_name: str) -> str:
    ftype = forcing.get("type", "zero")
    p = forcing.get("params") or {}

    def n(key, default=1):
        return _fmt_number(float(p.get(key, default)))

    if ftype == "const":
        return n("value")
    if ftype == "sin":
        phase = f" + {n('phase', 0)}" if p.get("phase") else ""
        return f"{n('amplitude')} sin({n('frequency')}{t_name}{phase})"
    if ftype == "cos":
        phase = f" + {n('phase', 0)}" if p.get("phase") else ""
        return f"{n('amplitude')} cos({n('frequency')}{t_name}{phase})"
    if ftype == "step":
        return f"{n('value')} \u00b7 H({t_name})"
    if ftype == "impulse":
        return f"{n('value')} \u00b7 \u03b4({t_name})"
    if ftype == "polynomial":
        return f"{n('slope')}{t_name}"
    return "0"


def _build_config(seed, theme) -> dict:
    config = {}
    if seed is None:
        config.update({"candidate_selection_mode": "deterministic_top_rank", "candidate_seed": None})
    else:
        config.update({"candidate_selection_mode": "seeded_random", "candidate_seed": seed})
    if theme:
        config["theme"] = theme
    return config


def _print_human(output_dict: dict) -> None:
    print(_typeset(output_dict["input_equation_spec"]))
    print()

    selected = output_dict["selected_candidate"]
    print(output_dict["experiment_description"])

    if selected is None:
        for w in output_dict["warnings"]:
            print(f"  ! {w}")
        return

    print()
    blanks = output_dict.get("description_blanks") or []
    if blanks:
        print("Fill in the setup:")
        width = max(len(b["template"]) for b in blanks) + 1
        for b in blanks:
            unit = f" {b['unit']}" if b["unit"] else ""
            print(f"  {(b['template'] + ':').ljust(width + 1)} {b['value']}{unit}")
        print()

    print(f"Verification: {selected['verification_status']} (residual {selected['residual_expr']})")

    alternatives = output_dict.get("alternative_candidates") or []
    if alternatives:
        names = ", ".join(a["model_id"] for a in alternatives)
        print(f"Also realizable as: {names}")

    for w in output_dict["warnings"]:
        print(f"  ! {w}")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="physcompile",
        description="Compile a differential equation into a physical experiment description.",
    )
    parser.add_argument("equation", nargs="?", help="Equation text, e.g. \"y'' + 2y' + 5y = 0\"")
    parser.add_argument(
        "--spec-file", type=Path, default=None,
        help="Path to a JSON file containing an EquationSpec (builder_state), instead of typed equation text.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Use seeded_random candidate selection with this seed.")
    parser.add_argument("--theme", type=str, default=None, help="Theme for the compile request (e.g. celestial, quantum).")
    parser.add_argument("--json", action="store_true", help="Print the full ExperimentOutput JSON instead of the human-readable summary.")
    args = parser.parse_args()

    if (args.equation is None) == (args.spec_file is None):
        parser.error("provide exactly one of: equation text, or --spec-file")

    builder_state = None
    if args.spec_file:
        try:
            builder_state = json.loads(args.spec_file.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Couldn't read --spec-file: {exc}", file=sys.stderr)
            return 1

    config = _build_config(args.seed, args.theme)

    try:
        output = compile_equation(args.equation, builder_state, config)
    except Exception as exc:  # noqa: BLE001 -- CLI boundary: report, don't traceback
        print(f"Couldn't compile that equation: {exc}", file=sys.stderr)
        return 1

    output_dict = output.to_dict()

    if args.json:
        print(json.dumps(output_dict, indent=2))
    else:
        _print_human(output_dict)

    return 0 if output_dict["selected_candidate"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # e.g. `physcompile ... | head` -- not an error, just a closed reader.
        devnull = None
        try:
            devnull = open("/dev/null", "wb")
            sys.stdout = devnull
        finally:
            sys.exit(0)
