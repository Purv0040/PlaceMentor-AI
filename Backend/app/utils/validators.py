import re


def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))


def is_valid_username(username: str) -> bool:
    pattern = r"^[a-zA-Z0-9_-]{3,30}$"
    return bool(re.match(pattern, username))
