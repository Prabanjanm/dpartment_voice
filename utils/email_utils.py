import re

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

def extract_email(text: str):
    if not text:
        return None

    match = re.search(EMAIL_REGEX, text)
    return match.group(0) if match else None
