import re
import os

from intent.intent_engine import detect_intent
from memory.session_state import state
from email_engine.gmail_service import (
    send_email,
    read_unread_email,
    delete_latest_email
)
from utils.email_utils import extract_email


# =============================
# INPUT MODE (TEXT FOR NOW)
# =============================
def get_input():
    return input("🧑 You: ").strip().lower()


# =============================
# REGEX HELPERS
# =============================
ATTACHMENT_REGEX = r"attachment\s+([^\s]+)"
URL_REGEX = r"https?://[^\s]+"


print("🚀 Gmail API Email Assistant Started")
print("Type 'exit' to quit\n")


while True:
    user_text = get_input()

    if not user_text:
        continue

    if user_text == "exit":
        break

    print("📝 Command:", user_text)

    # =====================================================
    # STATE: IDLE  → Detect intent
    # =====================================================
    if state.mode == "IDLE":
        intent_data = detect_intent(user_text)
        intent = intent_data.get("intent")
        content = intent_data.get("content", "")

        print("🧠 Intent:", intent)

        # ================= SEND =================
        if intent == "send":
            # ---- Extract email ----
            email = extract_email(content)

            # ---- Extract attachments ----
            attachments = []
            match = re.search(ATTACHMENT_REGEX, user_text)
            if match:
                file_name = match.group(1)
                if os.path.exists(file_name):
                    attachments.append(file_name)
                else:
                    print(f"⚠️ Attachment not found: {file_name}")

            # ---- Extract links ----
            links = re.findall(URL_REGEX, user_text)

            state.attachments = attachments
            state.links = links

            if email:
                state.recipient = email
                state.mode = "SEND_MESSAGE"
                print("🤖 What is the message?")
            else:
                state.mode = "ASK_EMAIL"
                print("🤖 Please say the recipient's email address.")
            continue

        # ================= READ =================
        if intent == "read":
            read_unread_email()
            state.reset()
            continue

        # ================= DELETE =================
        if intent == "delete":
            state.mode = "CONFIRM_DELETE"
            print("🤖 Are you sure you want to delete the latest email? (yes/no)")
            continue

        print("🤖 Sorry, I didn’t understand that.")
        continue

    # =====================================================
    # STATE: ASK_EMAIL
    # =====================================================
    if state.mode == "ASK_EMAIL":
        email = extract_email(user_text)

        if not email:
            print("❌ That doesn't look like a valid email. Please try again.")
            continue

        state.recipient = email
        state.mode = "SEND_MESSAGE"
        print("🤖 What is the message?")
        continue

    # =====================================================
    # STATE: SEND_MESSAGE
    # =====================================================
    if state.mode == "SEND_MESSAGE":
        state.message = user_text

        # Append links automatically
        if state.links:
            state.message += "\n\nLinks:\n"
            for link in state.links:
                state.message += f"- {link}\n"

        state.mode = "CONFIRM_SEND"
        print(f"🤖 Do you want to send this email to {state.recipient}? (yes/no)")
        continue

    # =====================================================
    # STATE: CONFIRM_SEND
    # =====================================================
    if state.mode == "CONFIRM_SEND":
        if user_text in ["yes", "y"]:
            send_email(
                to=state.recipient,
                body=state.message,
                attachments=state.attachments,
                drive_links=state.links
            )
            print("✅ Email sent successfully.")
        else:
            print("❌ Email cancelled.")

        state.reset()
        continue

    # =====================================================
    # STATE: CONFIRM_DELETE
    # =====================================================
    if state.mode == "CONFIRM_DELETE":
        if user_text in ["yes", "y"]:
            delete_latest_email()
            print("🗑️ Email deleted.")
        else:
            print("❌ Delete cancelled.")

        state.reset()
        continue
