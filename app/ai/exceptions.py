class LLMError(Exception):
    """Raised when the configured LLM provider fails, times out, or returns
    output that cannot be parsed/validated.

    ``status_code`` carries the HTTP status that the API layer should return:
    502 for malformed/unusable provider output, 503 for provider failures and
    timeouts.
    """

    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.status_code = status_code