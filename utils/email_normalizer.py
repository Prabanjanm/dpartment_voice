import re

def normalize_spoken_email(text: str) -> str:
    """
    Converts spoken email patterns into valid email addresses.

    Examples:
    - "john doe at gmail dot com"
    - "john.doe gmail com"
    - "john doe 08@gmail.com"
    """

    t = text.lower()

    # Common speech replacements
    t = t.replace(" at ", "@")
    t = t.replace(" dot ", ".")
    t = t.replace(" underscore ", "_")
    t = t.replace(" dash ", "-")
    t = t.replace(" space ", "")

    # Remove spaces around @ and .
    t = re.sub(r"\s*@\s*", "@", t)
    t = re.sub(r"\s*\.\s*", ".", t)

    # Remove remaining spaces inside email-like tokens
    t = re.sub(r"([a-z0-9._%+-])\s+([a-z0-9._%+-])", r"\1\2", t)

    return t
