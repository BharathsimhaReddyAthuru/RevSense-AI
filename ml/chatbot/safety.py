import re
from typing import Tuple

DISALLOWED_PATTERNS = [
    r'ignore (previous|prior) instructions',
    r'disregard (previous|prior) instructions',
    r'start a new conversation',
    r'do not follow',
    r'password',
    r'secret',
    r'api[-_ ]key',
    r'token',
    r'private data',
]


def is_safe_input(user_input: str) -> Tuple[bool, str]:
    if not user_input or not user_input.strip():
        return False, 'Input is empty.'
    normalized = user_input.lower()
    for pattern in DISALLOWED_PATTERNS:
        if re.search(pattern, normalized):
            return False, f'Disallowed content detected: "{pattern}"'
    return True, ''
