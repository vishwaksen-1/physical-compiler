class EquationParseError(ValueError):
    """Raised when raw_text cannot be parsed into an EquationSpec.

    Carries the original text and, where available, the underlying
    lark error so a caller (CLI or /api/parse) can surface a useful
    422 message per INTERFACE_CONTRACTS.md §9.
    """

    def __init__(self, message: str, raw_text: str = None, cause: Exception = None):
        super().__init__(message)
        self.raw_text = raw_text
        self.cause = cause
