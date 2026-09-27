import os
from typing import List

ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]


def is_allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS
