"""
rendering — deterministic NLG templates + renderer (Phase 3, spec §22).

Owner: Agent C's track; implemented in this session against the real
ExperimentOutput produced by src/api/compile_equation().

Consumes: ExperimentOutput (INTERFACE_CONTRACTS.md §5).
Produces: `experiment_description: str` for that same ExperimentOutput.

Implements INTERFACE_CONTRACTS.md §8:
`render_description(output: ExperimentOutput) -> str`.

Also provides `render_fill_blanks(output) -> list`, an additive extension
(not in INTERFACE_CONTRACTS.md, logged in docs/STATUS.md) supplying the
structured per-parameter data the frontend's fill-in-the-blanks worksheet
renders from -- this project's actual deliverable is "equation in, filled
experiment template out," and a flat prose string alone doesn't let a
client visually distinguish "the template" from "the number the compiler
computed," which is the whole point.

RANDOMIZATION NOTE (supersedes an earlier version of this docstring that
claimed this module was entirely randomness-free — that was true until
this note was added, and is deliberately no longer true): prose wording
(the opening line, a couple of phrase choices) now varies per call in the
default path, via `_pick()`. This is intentional, per the human's own
clarification: "deterministic by construction" in this project has always
meant "no LLM or external API generates any text," not "the wording never
changes" — hardcoded-but-randomly-picked phrasing is explicitly fine, and
was asked for, specifically so the default experience doesn't read as a
static lookup table. What is still fully deterministic, unconditionally,
regardless of this: WHICH apparatus gets selected and its parameter
values (INTERFACE_CONTRACTS.md §6's actual documented guarantee, and
still enforced — see src/synthesis/ and src/verification/, neither of
which this note touches). Only prose wording is allowed to vary. When a
`candidate_seed` is present (seeded_random mode), the SAME wording choices
are used every time for that seed — "Try another realization" stays fully
reproducible on repeat with the same seed, wording included.

This also means `experiment_description` is no longer safe to include in
a byte-for-byte determinism assertion for the default (unseeded) path —
see tests/unit/rendering/test_phase3.py's
`test_default_mode_apparatus_and_values_are_deterministic_but_prose_may_vary`,
which replaced the old `test_description_is_deterministic` for exactly
this reason.

This replaces the `_placeholder_description()` stand-in that previously
lived in src/api/__init__.py (Phase 2), per PROJECT_PLAN.md Phase 3.
"""
from __future__ import annotations

import random

_DOMAIN_ARTICLE = {
    "mechanical": "a mechanical",
    "electrical": "an electrical",
    "thermal": "a thermal",
    "other": "a",
}

_ORDER_NAME = {1: "first-order", 2: "second-order", 3: "third-order"}

_FORCING_PHRASE = {
    "zero": "with no external driving term",
    "const": "driven by a constant input",
    "sin": "driven by a sinusoidal input",
    "cos": "driven by a cosinusoidal input",
    "step": "driven by a step input",
    "impulse": "driven by an impulse input",
    "polynomial": "driven by a polynomial input",
    "custom_expr": "driven by a custom expression",
}


def _fmt(value: float) -> str:
    """Deterministic number formatting: 4 significant figures, no trailing
    zeros, no scientific notation for human-scale magnitudes."""
    if value == 0:
        return "0"
    formatted = f"{value:.4g}"
    return formatted


def _unit_for(model, param_name: str) -> str:
    constraint = (model.parameter_constraints or {}).get(param_name, {})
    return constraint.get("unit", "")


def _ordered_parameter_names(model, candidate) -> list:
    """Parameters in the model's own parameter_map order (a dict literal in
    the YAML, so insertion-ordered and stable), not dict-iteration order of
    the candidate's values. Any parameter the model didn't declare in
    parameter_map still gets included, appended in sorted order so output
    stays deterministic."""
    ordered_names = [n for n in (model.parameter_map or {}) if n in candidate.parameter_values]
    ordered_names += sorted(n for n in candidate.parameter_values if n not in ordered_names)
    return ordered_names


def _label_for(model, name: str) -> str:
    description = (model.parameter_map or {}).get(name, "")
    return description.split("(")[0].strip() if description else name


def _parameter_sentence(model, candidate) -> str:
    parts = []
    for name in _ordered_parameter_names(model, candidate):
        value = candidate.parameter_values[name]
        unit = _unit_for(model, name)
        label = _label_for(model, name)
        unit_suffix = f" {unit}" if unit else ""
        parts.append(f"{label} {name} = {_fmt(value)}{unit_suffix}")

    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + ", and " + parts[-1]


def _verification_sentence(candidate) -> str:
    status = candidate.verification_status
    if status == "EXACT":
        return (
            "Symbolic verification confirms this mapping is exact: the apparatus "
            "obeys the target equation identically, with zero residual."
        )
    if status == "APPROXIMATE":
        return (
            f"Symbolic verification puts this mapping within tolerance but not exact "
            f"(normalized coefficient residual {candidate.residual_expr}). Expect small "
            "systematic deviation from the ideal solution."
        )
    return (
        f"Symbolic verification failed for this mapping (normalized coefficient residual "
        f"{candidate.residual_expr}) — the realizable component values do not reproduce the "
        "target equation. Treat the numbers below as a starting point, not a solution."
    )


def _assumption_sentences(model, candidate) -> list:
    sentences = []

    approximation = model.approximation_model or {}
    assumptions = list(approximation.get("assumptions") or [])
    if assumptions:
        joined = "; ".join(assumptions)
        sentences.append(f"The mapping holds provided that: {joined}.")

    scale_notes = [a for a in candidate.assumptions if "fixed to" in a or "clamped" in a]
    if scale_notes:
        sentences.append(
            "Absolute component scale is not determined by the equation alone, so "
            + "; ".join(scale_notes)
            + "."
        )

    return sentences


def _error_sentence(model) -> str:
    error_model = model.error_model or {}
    sources = list(error_model.get("sources") or [])
    pct = error_model.get("expected_relative_error_pct")

    if not sources and pct is None:
        return ""

    lead = ""
    if pct is not None:
        lead = f"Expect roughly {_fmt(float(pct))}% relative error in practice"
    if sources:
        joined = "; ".join(sources)
        if lead:
            return f"{lead}, dominated by: {joined}."
        return f"The dominant error sources are: {joined}."
    return lead + "."


def _measurement_sentence(model) -> str:
    measurable = list(model.measurable_variables or [])
    controllable = list(model.controllable_variables or [])
    if not measurable and not controllable:
        return ""
    parts = []
    if controllable:
        parts.append(f"drive the system through {', '.join(controllable)}")
    if measurable:
        parts.append(f"record {', '.join(measurable)}")
    return "To run the experiment, " + " and ".join(parts) + "."


def _no_match_description(ir) -> str:
    return (
        f"No physical model in the current registry realizes this equation. It was "
        f"canonicalized successfully as {_ORDER_NAME.get(ir.order, f'order-{ir.order}')} "
        f"{ir.linearity} {ir.domain_type}, but the registry has no apparatus matching that "
        "class. Registry breadth is tracked in PROJECT_PLAN.md Phase 3."
    )


def render_fill_blanks(output) -> list:
    """The structured fill-in-the-blank data behind the frontend's worksheet
    view — this is the project's actual deliverable: a deterministic
    template ("connect a resistor of ___") with the compiler's own solved
    numbers dropped into the blanks, not AI-generated prose.

    Returns a list of dicts, one per parameter, in the same order
    render_description() would mention them:
        {"symbol": "R", "label": "resistance", "template": "resistance (R)",
         "value": "1000", "unit": "Ohm"}

    ExperimentOutput.description_blanks carries this (INTERFACE_CONTRACTS.md
    doesn't define this field -- it's an additive extension, logged in
    docs/STATUS.md, not a change to any frozen field). Returns [] when
    there's no selected candidate (the "no match" case) or the model can't
    be found -- callers should fall back to the plain description in that
    case, same as render_description() does.
    """
    from src.physics.models.registry import get_model

    candidate = output.selected_candidate
    if candidate is None:
        return []
    try:
        model = get_model(candidate.model_id)
    except KeyError:
        return []

    blanks = []
    for name in _ordered_parameter_names(model, candidate):
        value = candidate.parameter_values[name]
        blanks.append({
            "symbol": name,
            "label": _label_for(model, name),
            "template": f"{_label_for(model, name)} ({name})",
            "value": _fmt(value),
            "unit": _unit_for(model, name),
        })
    return blanks


_QUIRKY_PREAMBLES = [
    "Salutations, engineer — here's what the equation wants built:",
    "Fresh off the compiler's bench:",
    "Lab notebook entry, just compiled:",
    "The mathematics insists on the following apparatus:",
    "Breadboard (or rail, or beaker) time. Here's the plan:",
    "Straight from the registry, no notes:",
    "Your equation, translated into hardware:",
    "This one's a good one. Here's the build:",
    "Compiler's done its part — over to you, builder:",
    "Here's the apparatus your equation was hiding:",
]

_BUILD_LEAD_PHRASES = [
    "Build it with",
    "Assemble it using",
    "You'll need",
    "Put it together with",
    "Source",
]


def _pick(options: list, output) -> str:
    """One item from `options`, per this module's randomization policy
    (see module docstring's RANDOMIZATION NOTE): reproducible via
    `candidate_seed` when one is present (seeded_random mode, e.g. "Try
    another realization"), genuinely random otherwise (the default
    deterministic_top_rank path). This is deliberate, not an oversight —
    "deterministic by construction" refers to never calling an LLM or
    external API to generate text, not to the *wording* being frozen; the
    human explicitly asked for hardcoded-but-varied phrasing so the
    default experience doesn't read as "a simple lookup table." What
    stays fully deterministic regardless: WHICH apparatus is selected and
    its parameter values (INTERFACE_CONTRACTS.md §6's actual guarantee) --
    only prose wording varies.
    """
    seed = (output.config or {}).get("candidate_seed")
    if seed is None:
        return random.choice(options)
    return options[seed % len(options)]


def _quirky_preamble(output) -> str:
    """An opening line for the description. See _pick()'s docstring for
    the randomization policy — reproducible when seeded, genuinely varied
    otherwise, by explicit design."""
    return _pick(_QUIRKY_PREAMBLES, output) + " "


def render_description(output) -> str:
    """INTERFACE_CONTRACTS.md §8: render_description(output: ExperimentOutput) -> str.

    Renders the selected candidate into a deterministic prose paragraph.
    Takes the full ExperimentOutput (not just the candidate) because the
    description draws on the canonical IR's classification as well as the
    matched model's metadata.
    """
    from src.physics.models.registry import get_model

    ir = output.canonical_ir
    candidate = output.selected_candidate

    if candidate is None:
        return _no_match_description(ir)

    try:
        model = get_model(candidate.model_id)
    except KeyError:
        return _no_match_description(ir)

    order_name = _ORDER_NAME.get(ir.order, f"order-{ir.order}")
    forcing_type = (output.input_equation_spec or {}).get("rhs_forcing", {}).get("type", "zero")
    forcing_phrase = _FORCING_PHRASE.get(forcing_type, "with an unspecified driving term")
    domain_article = _DOMAIN_ARTICLE.get(model.domain, "a")

    sentences = [
        f"{_quirky_preamble(output)}This {order_name} {ir.linearity} {ir.domain_type}, {forcing_phrase}, is physically "
        f"realizable as {domain_article} {model.display_name}."
    ]

    param_sentence = _parameter_sentence(model, candidate)
    if param_sentence:
        sentences.append(f"{_pick(_BUILD_LEAD_PHRASES, output)} {param_sentence}.")

    sentences.append(_verification_sentence(candidate))
    sentences.extend(_assumption_sentences(model, candidate))

    error_sentence = _error_sentence(model)
    if error_sentence:
        sentences.append(error_sentence)

    measurement_sentence = _measurement_sentence(model)
    if measurement_sentence:
        sentences.append(measurement_sentence)

    alternatives = output.alternative_candidates or []
    if alternatives:
        alt_names = []
        for alt in alternatives:
            try:
                alt_names.append(get_model(alt.model_id).display_name)
            except KeyError:
                alt_names.append(alt.model_id)
        sentences.append(
            f"The same equation is equally realizable as: {', '.join(alt_names)} — "
            "different physics, identical governing mathematics."
        )

    return " ".join(sentences)
