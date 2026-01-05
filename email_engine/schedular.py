import base64
from email.mime.text import MIMEText
from email_engine.gmail_service import get_gmail_service
from email_engine.schedular_filters import parse_schedule_filters


def send_scheduled_email(data: dict):
    service = get_gmail_service()

    msg = MIMEText(data["body"])
    msg["To"] = data["to"]
    msg["Subject"] = data["subject"]

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={
            "raw": raw,
            "sendAt": int(data["send_at"])
        }
    ).execute()

    return (
        "📅 Email scheduled successfully!\n"
        f"📨 To: {data['to']}\n"
        f"📝 Subject: {data['subject']}"
    )