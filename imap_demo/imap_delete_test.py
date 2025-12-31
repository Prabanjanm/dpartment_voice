import imaplib
import email

# =====================
# CONFIG (EDIT THESE)
# =====================
IMAP_SERVER = "imap.gmail.com"
EMAIL = "prabanjanm22@gmail.com"
APP_PASSWORD = "pcde wxpc pcbp qldv"


def delete_latest_email():
    # Connect to IMAP
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, APP_PASSWORD)
    mail.select("INBOX")

    # Search all emails
    status, data = mail.search(None, "ALL")
    if status != "OK" or not data[0]:
        print("No emails found.")
        return

    # Get latest email ID
    latest_email_id = data[0].split()[-1]

    # Fetch email
    status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
    if status != "OK":
        print("Failed to fetch email.")
        return

    msg = email.message_from_bytes(msg_data[0][1])

    sender = msg.get("From", "")
    subject = msg.get("Subject", "")

    print("\n📧 Latest Email Details")
    print("----------------------")
    print("From   :", sender)
    print("Subject:", subject)

    # Ask user permission
    choice = input("\n❓ Do you want to delete this email? (yes/no): ").strip().lower()

    if choice in ["yes", "y"]:
        # Mark email as deleted
        mail.store(latest_email_id, "+FLAGS", "\\Deleted")
        mail.expunge()
        print("✅ Email deleted successfully.")
    else:
        print("❌ Delete cancelled.")

    mail.logout()


if __name__ == "__main__":
    delete_latest_email()
