"""
physcompile — local/dev CLI, calls src/api/ directly (not deployed to
Vercel; see PROJECT_PLAN.md §2).

Owner: Agent D.

Consumes: CLI args (equation text or a path to a builder-state JSON file)
+ optional config flags.
Produces: prints an ExperimentOutput (INTERFACE_CONTRACTS.md §5) as JSON
and/or its rendered description to stdout.

Will call `src.api.compile_equation(...)` once that exists — the whole
point of the shared src/api/ layer is that this CLI and the web backend
never diverge in behavior.

No logic implemented yet — Phase 0 stub only.
"""


def main() -> None:
    raise NotImplementedError(
        "physcompile CLI not implemented yet — Phase 0 stub. "
        "See PROJECT_PLAN.md Phase 1, Agent D."
    )


if __name__ == "__main__":
    main()
