from email_engine.gmail_service import get_gmail_service
from openai import OpenAI
import os, base64

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def categorize_emails(limit=10):
    service = get_gmail_service()
    msgs = service.users().messages().list(
        userId="me", maxResults=limit
    ).execute().get("messages", [])

    categorized = {}

    for msg in msgs:
        data = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()

        body = ""
        payload = data["payload"]
        if "parts" in payload:
            for p in payload["parts"]:
                if p["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(
                        p["body"]["data"]
                    ).decode()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"""
                Classify this email into:
                Important, Work, Personal, Promotion, Spam.
                Email:
                {body}
                """
            }]
        )

        category = response.choices[0].message.content.strip()
        categorized.setdefault(category, 0)
        categorized[category] += 1

    return categorized
