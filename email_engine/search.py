from email_engine.gmail_service import get_gmail_service

def search_email(query):
    service = get_gmail_service()
    result = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=5
    ).execute()

    messages = result.get("messages", [])
    return f"Found {len(messages)} emails for query '{query}'"
