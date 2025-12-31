import imaplib, email
from config import IMAP_SERVER, EMAIL, APP_PASSWORD


def _connect():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, APP_PASSWORD)
    mail.select("INBOX")
    return mail


def _fetch_ids(mail, criteria="ALL"):
    _, data = mail.search(None, criteria)
    return data[0].split() if data[0] else []


# ================= READ =================

def read_emails(scope="latest", count=1, email_id=None):
    mail = _connect()

    if scope == "unread":
        ids = _fetch_ids(mail, "UNSEEN")

    else:
        ids = _fetch_ids(mail, "ALL")

    if not ids:
        print("📭 No emails found.")
        mail.logout()
        return

    if scope == "old":
        target_ids = ids[:count]

    elif scope == "latest":
        target_ids = ids[-count:]

    elif scope == "id" and email_id:
        target_ids = [email_id.encode()]

    else:  # all
        target_ids = ids

    for eid in target_ids:
        _, msg_data = mail.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        print("\n📧 Email")
        print("ID     :", eid.decode())
        print("From   :", msg.get("From"))
        print("Subject:", msg.get("Subject"))

    mail.logout()


# ================= DELETE =================

def delete_emails(scope="latest", count=1, email_id=None):
    mail = _connect()
    ids = _fetch_ids(mail, "ALL")

    if not ids:
        print("📭 No emails found.")
        return

    if scope == "latest":
        target_ids = ids[-count:]

    elif scope == "old":
        target_ids = ids[:count]

    elif scope == "id" and email_id:
        target_ids = [email_id.encode()]

    elif scope == "unread":
        target_ids = _fetch_ids(mail, "UNSEEN")

    else:  # all
        target_ids = ids

    print(f"\n⚠️ You are about to delete {len(target_ids)} email(s).")
    confirm = input("Type YES to confirm: ").strip().lower()

    if confirm != "yes":
        print("❌ Delete cancelled.")
        mail.logout()
        return

    for eid in target_ids:
        mail.store(eid, "+FLAGS", "\\Deleted")

    mail.expunge()
    print("✅ Emails deleted successfully.")
    mail.logout()

def search_emails(search_type, query, limit=5):
    mail = _connect()

    if search_type == "sender":
        criteria = f'FROM "{query}"'
    elif search_type == "subject":
        criteria = f'SUBJECT "{query}"'
    elif search_type == "content":
        criteria = f'BODY "{query}"'
    else:
        criteria = "ALL"

    _, data = mail.search(None, criteria)
    ids = data[0].split()

    results = []
    for i, eid in enumerate(ids[-limit:], start=1):
        _, msg_data = mail.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        results.append({
            "index": i,
            "id": eid,
            "from": msg.get("From"),
            "subject": msg.get("Subject")
        })

    mail.logout()
    return results

