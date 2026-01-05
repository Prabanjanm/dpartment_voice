import json
from datetime import datetime
from email_engine.gmail_service import get_gmail_service
from email_engine.followup_filter import parse_followup_time

FOLLOWUP_FILE = "memory/followups.json"

def schedule_followup(user_text: str):
    service = get_gmail_service()

    # find latest matching email
    result = service.users().messages().list(
        userId="me",
        maxResults=1
    ).execute()

    messages = result.get("messages", [])
    if not messages:
        return "❌ No email found to follow up."

    email_id = messages[0]["id"]

    msg = service.users().messages().get(
        userId="me",
        id=email_id,
        format="metadata",
        metadataHeaders=["From", "Subject"]
    ).execute()

    headers = msg["payload"]["headers"]
    sender = subject = ""

    for h in headers:
        if h["name"] == "From":
            sender = h["value"]
        if h["name"] == "Subject":
            subject = h["value"]

    follow_at = parse_followup_time(user_text)

    try:
        with open(FOLLOWUP_FILE, "r") as f:
            followups = json.load(f)
    except:
        followups = []

    followups.append({
        "email_id": email_id,
        "from": sender,
        "subject": subject,
        "follow_at": follow_at.isoformat()
    })

    with open(FOLLOWUP_FILE, "w") as f:
        json.dump(followups, f, indent=2)

    return f"⏰ Follow-up scheduled for {follow_at.strftime('%Y-%m-%d %H:%M')}."




def list_followups():
    try:
        with open(FOLLOWUP_FILE, "r") as f:
            followups = json.load(f)
    except:
        return "📭 No follow-ups scheduled."

    if not followups:
        return "📭 No follow-ups scheduled."

    service = get_gmail_service()
    output = ["📌 Follow-up Emails:\n"]

    updated = False  # track schema repair

    for i, item in enumerate(followups, 1):
        follow_time = datetime.fromisoformat(item["follow_at"])

        sender = item.get("from")
        subject = item.get("subject")

        # 🔧 BACKWARD COMPATIBILITY FIX
        if not sender or not subject:
            try:
                msg = service.users().messages().get(
                    userId="me",
                    id=item["email_id"],
                    format="metadata",
                    metadataHeaders=["From", "Subject"]
                ).execute()

                for h in msg.get("payload", {}).get("headers", []):
                    if h["name"] == "From":
                        sender = h["value"]
                    if h["name"] == "Subject":
                        subject = h["value"]

                # update old record
                item["from"] = sender
                item["subject"] = subject
                updated = True

            except Exception:
                sender = "(Sender unavailable)"
                subject = "(Subject unavailable)"

        output.append(
            f"{i}. ⏰ {follow_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"   From: {sender}\n"
            f"   Subject: {subject}\n"
        )

    # 🔄 SAVE repaired records
    if updated:
        with open(FOLLOWUP_FILE, "w") as f:
            json.dump(followups, f, indent=2)

    return "\n".join(output)
