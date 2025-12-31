import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import base64
import mimetypes
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from .gmail_auth import get_gmail_service


SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def auth():
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

service = auth()

def read_unread():
    return service.users().messages().list(userId="me", q="is:unread").execute().get("messages", [])

def get_message(msg_id):
    msg = service.users().messages().get(userId="me", id=msg_id).execute()
    headers = msg["payload"]["headers"]
    body = msg["payload"]["body"].get("data","")
    body = base64.urlsafe_b64decode(body).decode() if body else ""
    sender = next(h["value"] for h in headers if h["name"]=="From")
    return sender, body

def create_message(
    to: str,
    subject: str,
    body: str,
    attachments: list = None,
    drive_links: list = None
):
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject

    # Add links to body if any
    if drive_links:
        body += "\n\nAttachments:\n"
        for link in drive_links:
            body += f"- {link}\n"

    message.attach(MIMEText(body, "plain"))

    # Attach local files
    if attachments:
        for file_path in attachments:
            if not os.path.exists(file_path):
                continue

            content_type, encoding = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = "application/octet-stream"

            main_type, sub_type = content_type.split("/", 1)

            with open(file_path, "rb") as f:
                part = MIMEBase(main_type, sub_type)
                part.set_payload(f.read())

            encoders.encode_base64(part)
            filename = os.path.basename(file_path)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{filename}"'
            )
            message.attach(part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw}


def send_email(
    to: str,
    body: str,
    subject: str = "Voice Assistant Mail",
    attachments: list = None,
    drive_links: list = None,
    schedule_time: str = None
):
    service = get_gmail_service()

    # Scheduling (simple demo-level)
    if schedule_time:
        print(f"⏳ Email scheduled for {schedule_time}")
        # For demo: just log
        # Real version: background scheduler / cron
        return

    message = create_message(
        to=to,
        subject=subject,
        body=body,
        attachments=attachments,
        drive_links=drive_links
    )

    service.users().messages().send(
        userId="me",
        body=message
    ).execute()



def reply_email(thread_id, to, text):
    msg = MIMEText(text)
    msg["to"] = to
    msg["subject"] = "Re: Voice Reply"
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(
        userId="me",
        body={"raw":raw,"threadId":thread_id}
    ).execute()
