import re

def parse_search_filters(text: str) -> dict:
    text = text.lower()

    filters = {
        "count": 5,      # default
        "query": ""
    }

    # -----------------------------
    # COUNT (last N)
    # -----------------------------
    match = re.search(r"last\s+(\d+)", text)
    if match:
        filters["count"] = int(match.group(1))

    # -----------------------------
    # READ / UNREAD
    # -----------------------------
    if "unread" in text or "unseen" in text:
        filters["query"] += " is:unread"

    if "read" in text:
        filters["query"] += " is:read"

    # -----------------------------
    # SPAM
    # -----------------------------
    if "spam" in text:
     filters["query"] += " label:spam -in:inbox"


    # -----------------------------
    # PROMOTIONS / SOCIAL
    # -----------------------------
    if "promotion" in text or "promotional" in text:
        filters["query"] += " category:promotions"

    if "social" in text:
        filters["query"] += " category:social"

    # -----------------------------
    # FROM EMAIL (IMPORTANT)
    # -----------------------------
    email_match = re.search(
        r"([a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-.]+)", text
    )
    if email_match:
        filters["query"] += f" from:{email_match.group(1)}"

    # -----------------------------
    # SUBJECT / CONTENT KEYWORDS
    # -----------------------------
    about_match = re.search(r"about\s+(.+)", text)
    if about_match:
        filters["query"] += f" {about_match.group(1)}"

    # -----------------------------
    # DATE FILTERS
    # -----------------------------
    if "today" in text:
        filters["query"] += " newer_than:1d"

    if "yesterday" in text:
        filters["query"] += " older_than:1d newer_than:2d"

    if "last week" in text:
        filters["query"] += " newer_than:7d"

    return filters
