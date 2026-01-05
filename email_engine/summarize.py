import base64
import os
from openai import OpenAI

from email_engine.gmail_service import get_gmail_service
from email_engine.summarize_filter import parse_summarize_filters

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import base64
import re
from html import unescape


def extract_body(payload) -> str:
    """
    Extract FULL readable content from Gmail message payload
    (handles multipart, HTML, nested parts)
    """

    texts = []

    def walk_parts(part):
        mime_type = part.get("mimeType", "")
        body = part.get("body", {})

        # -------------------------
        # Plain text
        # -------------------------
        if mime_type == "text/plain" and "data" in body:
            data = body["data"]
            decoded = base64.urlsafe_b64decode(data).decode(
                "utf-8", errors="ignore"
            )
            texts.append(decoded)

        # -------------------------
        # HTML → convert to text
        # -------------------------
        elif mime_type == "text/html" and "data" in body:
            data = body["data"]
            html = base64.urlsafe_b64decode(data).decode(
                "utf-8", errors="ignore"
            )
            texts.append(html_to_text(html))

        # -------------------------
        # Multipart → recurse
        # -------------------------
        for sub_part in part.get("parts", []):
            walk_parts(sub_part)

    walk_parts(payload)

    # Remove duplicates & clean
    final_text = "\n".join(texts)
    final_text = clean_text(final_text)

    return final_text.strip()


def html_to_text(html: str) -> str:
    """
    Convert HTML email body to readable text
    """
    html = unescape(html)

    # Remove scripts & styles
    html = re.sub(r"<(script|style).*?>.*?</\1>", "", html, flags=re.S)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", html)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_text(text: str) -> str:
    """
    Final cleanup for summarization
    """
    # Remove excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove tracking junk
    text = re.sub(r"unsubscribe.*", "", text, flags=re.I)

    return text.strip()


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
