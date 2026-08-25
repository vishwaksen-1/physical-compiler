"""
parser — advanced-mode grammar/lexer/AST -> EquationSpec, plus a validator
any caller (parser or web frontend) can use to confirm schema conformance.

Owner: Agent C.

Consumes: raw_text: str (freeform advanced-mode equation text).
Produces: EquationSpec (INTERFACE_CONTRACTS.md §1) with
`input_source = "text_parser"`.

Implements INTERFACE_CONTRACTS.md §8: `parse_equation(raw_text: str) ->
EquationSpec`.

Owns the validation rule from INTERFACE_CONTRACTS.md §1: a web-builder-
produced spec and a text-parser-produced spec for the "same" equation must
be structurally identical except for `input_source` and `raw_text`.

Recommended implementation: `lark` grammar (PROJECT_PLAN.md Phase 1).
No logic implemented yet — Phase 0 stub only.
"""
