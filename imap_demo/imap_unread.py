import imaplib
import email

# =====================
# CONFIG (EDIT THESE)
# =====================
IMAP_SERVER = "imap.gmail.com"
EMAIL = "prabanjanm22@gmail.com"
APP_PASSWORD = "pcde wxpc pcbp qldv"


def read_latest_unseen_email():
    # Connect to IMAP
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, APP_PASSWORD)
    mail.select("INBOX")

    # Search for unread emails
    status, data = mail.search(None, "UNSEEN")
    if status != "OK" or not data[0]:
        print("📭 No unread emails.")
        mail.logout()
        return

    # Get latest unread email ID
    latest_email_id = data[0].split()[-1]

    # Fetch email
    status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
    if status != "OK":
        print("Failed to fetch email.")
        mail.logout()
        return

    msg = email.message_from_bytes(msg_data[0][1])

    sender = msg.get("From", "")
    subject = msg.get("Subject", "")

    # Extract body
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(errors="ignore")
                break
    else:
        body = msg.get_payload(decode=True).decode(errors="ignore")

    # Mark email as seen
    mail.store(latest_email_id, "+FLAGS", "\\Seen")

    print("\n📧 Unread Email")
    print("----------------------")
    print("From   :", sender)
    print("Subject:", subject)
    print("\nMessage:")
    print(body[:500])  # limit output

    mail.logout()


if __name__ == "__main__":
    read_latest_unseen_email()
