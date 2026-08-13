"""Custom exception classes for LeetCode Analyzer module."""


class LeetCodeAnalyzerException(Exception):
    """Base exception class for LeetCode Analyzer module."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class LeetCodeUserNotFoundError(LeetCodeAnalyzerException):
    """Raised when the specified LeetCode user does not exist."""

    def __init__(self, username: str):
        message = f"LeetCode user '{username}' was not found."
        super().__init__(message=message, status_code=404)


class LeetCodeDataUnavailableError(LeetCodeAnalyzerException):
    """Raised when external LeetCode API/data source is unreachable or unavailable."""

    def __init__(self, message: str = "LeetCode data is currently unavailable. Please try again later."):
        super().__init__(message=message, status_code=503)


class ExternalAPIError(LeetCodeAnalyzerException):
    """Raised when a generic external API request fails."""

    def __init__(self, message: str = "External API request failed.", status_code: int = 502):
        super().__init__(message=message, status_code=status_code)
