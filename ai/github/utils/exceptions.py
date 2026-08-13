"""Custom exception classes for GitHub Analyzer module."""


class GitHubAnalyzerException(Exception):
    """Base exception class for GitHub Analyzer module."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GitHubUserNotFoundError(GitHubAnalyzerException):
    """Raised when the specified GitHub user does not exist."""

    def __init__(self, username: str):
        message = f"GitHub user '{username}' was not found."
        super().__init__(message=message, status_code=404)


class GitHubRateLimitError(GitHubAnalyzerException):
    """Raised when GitHub API rate limit is exceeded."""

    def __init__(self, message: str = "GitHub API rate limit exceeded. Please configure GITHUB_TOKEN or try again later."):
        super().__init__(message=message, status_code=429)


class GitHubAPIError(GitHubAnalyzerException):
    """Raised when an error occurs during GitHub API requests."""

    def __init__(self, message: str = "An error occurred while communicating with the GitHub API.", status_code: int = 502):
        super().__init__(message=message, status_code=status_code)


class ExternalAPIError(GitHubAnalyzerException):
    """Raised when a generic external service API failure occurs."""

    def __init__(self, message: str = "External service unavailable.", status_code: int = 503):
        super().__init__(message=message, status_code=status_code)
