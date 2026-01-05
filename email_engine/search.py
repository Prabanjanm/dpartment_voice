from email_engine.gmail_service import get_gmail_service
from email_engine.search_filters import parse_search_filters


def search_email(user_text: str):
    """
    Search emails using natural language:
    - from email address
    - unread / read
    - subject keywords
    - date
    - spam / promotions
    """

    filters = parse_search_filters(user_text)
    service = get_gmail_service()

    response = service.users().messages().list(
        userId="me",
        q=filters["query"],
        maxResults=filters["count"]
    ).execute()

    messages = response.get("messages", [])

    if not messages:
        return "❌ No matching emails found."

    results = []

    for msg in messages:
        data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["From", "Subject"]
        ).execute()

        headers = data.get("payload", {}).get("headers", [])
        sender = subject = ""

        for h in headers:
            if h["name"] == "From":
                sender = h["value"]
            elif h["name"] == "Subject":
                subject = h["value"]

        results.append(f"📧 From: {sender} | Subject: {subject}")

    return "\n".join(results)
