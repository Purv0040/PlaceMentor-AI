"""Custom exception classes for the AI Resume Analyzer."""


class ResumeAnalyzerException(Exception):
    """Base exception class for Resume Analyzer module."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidPDFError(ResumeAnalyzerException):
    """Raised when an uploaded file is not a valid or readable PDF."""

    def __init__(self, message: str = "The provided file is not a valid PDF or is corrupted."):
        super().__init__(message=message, status_code=400)


class EmptyResumeError(ResumeAnalyzerException):
    """Raised when no readable text could be extracted from the PDF."""

    def __init__(self, message: str = "No readable text extracted from the PDF. The file may be image-only or empty."):
        super().__init__(message=message, status_code=422)


class ResumeTooLargeError(ResumeAnalyzerException):
    """Raised when the uploaded file exceeds maximum allowed size."""

    def __init__(self, max_mb: int = 10):
        message = f"File size exceeds the maximum limit of {max_mb} MB."
        super().__init__(message=message, status_code=413)


class SkillDatasetError(ResumeAnalyzerException):
    """Raised when the skill database CSV fails to load or parse."""

    def __init__(self, message: str = "Failed to load skill dataset from data/skills.csv."):
        super().__init__(message=message, status_code=500)
