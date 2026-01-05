from collections import defaultdict
from email_engine.gmail_service import get_gmail_service
from email_engine.categorize_filters import parse_categorize_filters


def categorize_emails(user_text: str):
    """
    Categorize emails based on natural language filters
    """

    filters = parse_categorize_filters(user_text)

    service = get_gmail_service()
    response = service.users().messages().list(
        userId="me",
        q=filters["query"],
        maxResults=filters["count"]
    ).execute()

    messages = response.get("messages", [])

    if not messages:
        return {"No emails": 0}

    category_count = defaultdict(int)

    for msg in messages:
        data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["From", "Subject"]
        ).execute()

        headers = data.get("payload", {}).get("headers", [])
        subject = ""
        sender = ""

        for h in headers:
            if h["name"] == "Subject":
                subject = h["value"].lower()
            if h["name"] == "From":
                sender = h["value"].lower()

        # -----------------------------
        # SIMPLE CATEGORY RULES
        # -----------------------------
        if "amazon" in sender or "order" in subject:
            category_count["Shopping"] += 1

        elif "interview" in subject or "hr" in sender:
            category_count["Work"] += 1

        elif "newsletter" in subject:
            category_count["Newsletter"] += 1

        elif "offer" in subject or "sale" in subject:
            category_count["Promotion"] += 1

        else:
            category_count["General"] += 1

    return dict(category_count)
