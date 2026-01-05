import base64
import os
import re
import requests
from datetime import datetime

from email_engine.gmail_service import get_gmail_service
from email_engine.subscription_filter import parse_subscription_filters


# ----------------------------------------------------
# Extract unsubscribe links (RFC 2369 / 8058 compliant)
# ----------------------------------------------------
def extract_unsubscribe_links(headers):
    for h in headers:
        if h["name"].lower() == "list-unsubscribe":
            value = h["value"]
            return re.findall(r'<([^>]+)>', value)
    return []


# ----------------------------------------------------
# HTTP unsubscribe
# ----------------------------------------------------
def http_unsubscribe(url):
    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True
        )
        return response.status_code in [200, 202, 204]
    except Exception:
        return False


# ----------------------------------------------------
# Mailto unsubscribe (send email via Gmail API)
# ----------------------------------------------------
def mailto_unsubscribe(service, mailto_link):
    try:
        email = mailto_link.replace("mailto:", "").split("?")[0]

        message = (
            f"To: {email}\r\n"
            f"Subject: Unsubscribe\r\n\r\n"
            f"Please unsubscribe me."
        )

        encoded = base64.urlsafe_b64encode(
            message.encode("utf-8")
        ).decode("utf-8")

        service.users().messages().send(
            userId="me",
            body={"raw": encoded}
        ).execute()

        return True
    except Exception:
        return False


# ----------------------------------------------------
# Main subscription manager
# ----------------------------------------------------
def manage_subscriptions(user_text: str):
    """
    Handles:
    - list subscriptions
    - unsubscribe
    - unsubscribe all
    """

    filters = parse_subscription_filters(user_text)
    service = get_gmail_service()

    response = service.users().messages().list(
        userId="me",
        q=filters["query"],
        maxResults=filters["count"]
    ).execute()

    messages = response.get("messages", [])
    if not messages:
        return ["No subscriptions found."]

    results = []

    def get_header(headers, name):
        for h in headers:
            if h["name"].lower() == name.lower():
                return h["value"]
        return "Unknown"

    for msg in messages:
        data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        payload = data.get("payload", {})
        headers = payload.get("headers", [])

        subject = get_header(headers, "Subject")
        from_email = re.sub(
            r"<.*?>", "", get_header(headers, "From")
        ).strip()

        unsubscribe_links = extract_unsubscribe_links(headers)

        internal_date = int(data.get("internalDate", 0))
        subscribed_on = datetime.fromtimestamp(
            internal_date / 1000
        ).strftime("%d %b %Y")

        # ---------------- LIST ----------------
        if filters["action"] == "list":
            results.append({
                "from": from_email,
                "subject": subject,
                "subscribed_on": subscribed_on,
                "unsubscribe_methods": unsubscribe_links or "None"
            })

        # ------------- UNSUBSCRIBE -------------
        elif filters["action"] == "unsubscribe":
            if not unsubscribe_links:
                results.append(
                    f"❌ No unsubscribe option for '{subject}'"
                )
                continue

            success = False

            for link in unsubscribe_links:
                if link.startswith("http"):
                    if http_unsubscribe(link):
                        results.append(
                            f"✅ Unsubscribed from '{subject}' (link)"
                        )
                        success = True
                        break

                elif link.startswith("mailto:"):
                    if mailto_unsubscribe(service, link):
                        results.append(
                            f"✅ Unsubscribed from '{subject}' (email)"
                        )
                        success = True
                        break

            if not success:
                results.append(
                    f"⚠️ Failed to unsubscribe from '{subject}'"
                )

    return results
