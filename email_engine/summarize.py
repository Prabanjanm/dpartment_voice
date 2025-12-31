import base64
import os
from openai import OpenAI

from email_engine.gmail_service import get_gmail_service
from email_engine.summarize_filter import parse_summarize_filters

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_body(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain" and "data" in part["body"]:
                return base64.urlsafe_b64decode(
                    part["body"]["data"]
                ).decode("utf-8", errors="ignore")
    return ""


def summarize_emails(user_text: str):
    """
    Summarize emails based on natural language filters
    """

    filters = parse_summarize_filters(user_text)

    service = get_gmail_service()
    response = service.users().messages().list(
        userId="me",
        q=filters["query"],
        maxResults=filters["count"]
    ).execute()

    messages = response.get("messages", [])

    if not messages:
        return ["No matching emails found."]

    summaries = []

    for msg in messages:
        data = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()

        body = extract_body(data["payload"])

        if not body.strip():
            continue

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Summarize this email briefly in 2 lines:\n{body}"
            }],
            temperature=0.3
        )

        summaries.append(completion.choices[0].message.content.strip())

    return summaries
