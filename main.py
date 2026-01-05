import re
import os

from intent.intent_engine import detect_intent
from memory.session_state import state

from email_engine.gmail_service import (
    send_email,
    read_unread,
)

from email_engine.summarize import summarize_emails
from email_engine.search import search_email
from email_engine.categorize import categorize_emails
from email_engine.subscription_manage import manage_subscriptions

from utils.email_utils import extract_email


# =============================
# INPUT MODE
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
        print("👋 Exiting assistant")
        break

    print("📝 Command:", user_text)

    # =====================================================
    # STATE: IDLE
    # =====================================================
    if state.mode == "IDLE":
        intent_data = detect_intent(user_text)
        intent = intent_data.get("intent")
        content = intent_data.get("content", "")

        print("🧠 Intent:", intent)

        # ================= SEND =================
        if intent == "send":
            email = extract_email(content)

            attachments = []
            match = re.search(ATTACHMENT_REGEX, user_text)
            if match:
                file_name = match.group(1)
                if os.path.exists(file_name):
                    attachments.append(file_name)
                else:
                    print(f"⚠️ Attachment not found: {file_name}")

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
            read_unread()
            state.reset()
            continue

        # ================= SUMMARIZE =================
        if intent == "summarize":
            summaries = summarize_emails(user_text)
            print("\n📩 Email Summaries:\n")
            for i, summary in enumerate(summaries, 1):
                print(f"{i}. {summary}\n")
            state.reset()
            continue

        # ================= SEARCH =================
        if intent == "search":
            if not content:
                print("❌ Please specify what to search for.")
                continue

            result = search_email(content)
            print("🔍", result)
            state.reset()
            continue

        # ================= CATEGORIZE =================
        if intent == "categorize":
            categories = categorize_emails(limit=10)
            print("\n📂 Inbox Categorization:")
            for category, count in categories.items():
                print(f"- {category}: {count} emails")
            state.reset()
            continue

        # ================= SUBSCRIPTIONS =================
        if intent == "subscription":
            print("\n🤖 Managing your subscriptions...\n")
            results = manage_subscriptions(user_text)

            print("📬 Subscription Manager:\n")

            if not results:
                print("No subscriptions found.")
            else:
                for i, mail in enumerate(results, 1):

                    # unsubscribe action returns strings
                    if isinstance(mail, str):
                        print(f"{i}. {mail}")
                        continue

                    print(f"📧 {i}. {mail.get('subject', 'No subject')}")
                    print(f"   From   : {mail.get('from', 'Unknown')}")

                    methods = mail.get("unsubscribe_methods", [])

                    if not methods:
                        print("   Action : ❌ No unsubscribe option")
                    elif any(m.startswith("http") for m in methods):
                        print("   Action : 🔗 Unsubscribe via link")
                    elif any(m.startswith("mailto:") for m in methods):
                        print("   Action : ✉️ Unsubscribe via email")

                    print("-" * 45)

            state.reset()
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
