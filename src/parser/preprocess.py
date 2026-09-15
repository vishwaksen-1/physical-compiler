"""
Unicode normalization pass for advanced-mode equation text.

The grammar (grammar.lark) only knows ASCII derivative forms
(x'', dx/dt, d2x/dt2) plus the literal Leibniz-PDE form using the
actual '∂' character. This module rewrites the two other Unicode
conventions the spec calls out — overdot notation (ẋ, ẍ) and
superscript derivative orders (∂²u/∂x², x²) — into the forms the
grammar already understands, so the grammar file itself never has to
special-case combining characters.

Kept deliberately separate from text_parser.py so the "what unicode
means what" mapping is easy to audit/extend in one place.
"""

import unicodedata

# Superscript digits -> plain digits. Used both for Leibniz-order
# superscripts (∂²u/∂x²) and bare exponents (x²) so "^" also works
# after this pass runs.
_SUPERSCRIPT_MAP = str.maketrans(
    {
        "\u2070": "0",  # ⁰
        "\u00b9": "1",  # ¹
        "\u00b2": "2",  # ²
        "\u00b3": "3",  # ³
        "\u2074": "4",  # ⁴
        "\u2075": "5",  # ⁵
        "\u2076": "6",  # ⁶
        "\u2077": "7",  # ⁷
        "\u2078": "8",  # ⁸
        "\u2079": "9",  # ⁹
    }
)

# Combining marks used (by convention) as Newton's-notation dots.
_COMBINING_SINGLE_DOT = "\u0307"  # combining dot above      -> one prime
_COMBINING_DOUBLE_DOT = "\u0308"  # combining diaeresis      -> two primes


def normalize_equation_text(raw_text: str) -> str:
    """Rewrite unicode derivative shorthand into the grammar's ASCII forms.

    Idempotent and safe to call on already-ASCII text (no-op in that case).
    """
    if raw_text is None:
        return raw_text

    text = raw_text.translate(_SUPERSCRIPT_MAP)

    # NFD so precomposed letters-with-dot (ẋ, ẍ) decompose into
    # base-letter + combining mark, same as if the user typed the
    # combining mark directly.
    text = unicodedata.normalize("NFD", text)

    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        # Only letters carry Newton-dot notation in this grammar.
        if ch.isalpha():
            j = i + 1
            primes = 0
            while j < n and text[j] in (_COMBINING_SINGLE_DOT, _COMBINING_DOUBLE_DOT):
                primes += 1 if text[j] == _COMBINING_SINGLE_DOT else 2
                j += 1
            out.append(ch)
            out.append("'" * primes)
            i = j
        else:
            out.append(ch)
            i += 1

    # Re-compose anything else that NFD decomposed but we didn't touch
    # (keeps non-derivative unicode, e.g. accented names, well-behaved).
    return unicodedata.normalize("NFC", "".join(out))
