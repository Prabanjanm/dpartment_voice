import re
from datetime import datetime, timedelta

def parse_summarize_filters(text: str) -> dict:
    text = text.lower()

    filters = {
        "count": 5,        # default
        "query": "",       # Gmail search query
    }

    # -----------------------------
    # COUNT (last N)
    # -----------------------------
    match = re.search(r"last\s+(\d+)", text)
    if match:
        filters["count"] = int(match.group(1))

    # -----------------------------
    # SEEN / UNSEEN
    # -----------------------------
    if "unseen" in text or "unread" in text:
        filters["query"] += " is:unread"

    if "seen" in text or "read" in text:
        filters["query"] += " is:read"

    # -----------------------------
    # SPAM
    # -----------------------------
    if "spam" in text:
        filters["query"] += " label:spam"

    # -----------------------------
    # PROMOTIONS / SOCIAL
    # -----------------------------
    if "promotion" in text:
        filters["query"] += " category:promotions"

    if "social" in text:
        filters["query"] += " category:social"

    # -----------------------------
    # FROM SENDER
    # -----------------------------
    from_match = re.search(r"from\s+([a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-.]+)", text)
    if from_match:
        filters["query"] += f" from:{from_match.group(1)}"

    # -----------------------------
    # SUBJECT KEYWORDS
    # -----------------------------
    subject_match = re.search(r"about\s+(.+)", text)
    if subject_match:
        keyword = subject_match.group(1)
        filters["query"] += f' subject:{keyword}'

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
