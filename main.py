import re
import os

# =============================
# VOICE I/O
# =============================
from stt.whisper_stt import stt
from tts.speaker import speak

# =============================
# CORE LOGIC
# =============================
from intent.intent_engine import detect_intent
from memory.session_state import state

# =============================
# EMAIL FEATURES
# =============================
from email_engine.gmail_service import send_email, read_unread
from email_engine.summarize import summarize_emails
from email_engine.search import search_email
from email_engine.categorize import categorize_emails
from email_engine.followup import schedule_followup, list_followups
from email_engine.schedular_filters import safe_json_extract
from email_engine.schedular import send_scheduled_email
from utils.email_normalizer import normalize_spoken_email


from utils.email_utils import extract_email

# =============================
# REGEX
# =============================
ATTACHMENT_REGEX = r"attachment\s+([^\s]+)"
URL_REGEX = r"https?://[^\s]+"


# =============================
# START ASSISTANT
# =============================
speak("Gmail voice assistant started. Say exit to quit.")


while True:
    # 🎤 Listen to user
    user_text = stt.listen(timeout=5)

    if not user_text:
        continue

    print("🧑 You:", user_text)

    if user_text in ["exit", "quit", "stop"]:
        speak("Goodbye. Have a nice day.")
        break

    # =====================================================
    # STATE: IDLE → INTENT ROUTING
    # =====================================================
    if state.mode == "IDLE":
        intent_data = detect_intent(user_text)
        intent = intent_data.get("intent")
        content = intent_data.get("content", "")

        print("🧠 Intent:", intent)
        speak(f"I understood intent as {intent}")

        # ================= SEND =================
        if intent == "send":
            email = extract_email(content)
            state.links = re.findall(URL_REGEX, user_text)

            if email:
                state.recipient = email
                state.mode = "SEND_MESSAGE"
                speak("What is the message?")
            else:
                state.mode = "ASK_EMAIL"
                speak("Please say the recipient email address.")
            continue

        # ================= READ =================
        if intent == "read":
            read_unread()
            speak("I have read your unread emails.")
            state.reset()
            continue

        # ================= SUMMARIZE =================
        if intent == "summarize":
            summaries = summarize_emails(user_text)
            if not summaries:
                speak("No matching emails found.")
            else:
                for s in summaries:
                    speak(s)
            state.reset()
            continue

        # ================= SEARCH =================
        if intent == "search":
            cleaned_query = normalize_spoken_email(content or user_text)
            result = search_email(cleaned_query)
            speak(result)
            state.reset()
            continue

        # ================= CATEGORIZE =================
        if intent == "categorize":
            categories = categorize_emails(user_text)
            if not categories:
                speak("No emails found to categorize.")
            else:
                for cat, count in categories.items():
                    speak(f"{cat} has {count} emails")
            state.reset()
            continue

        # ================= FOLLOW UP (SCHEDULE) =================
        if intent == "followup_schedule":
            result = schedule_followup(user_text)
            speak(result)
            state.reset()
            continue

        # ================= FOLLOW UP (LIST) =================
        if intent == "followup_list":
            result = list_followups()
            speak(result)
            state.reset()
            continue

        # ================= SCHEDULE SEND =================
        if intent == "schedule_send":
            data = safe_json_extract(user_text)
            if not data or not data.get("send_at"):
                speak("I couldn't understand the schedule time. Please say it again.")
                continue

            # Ask for message if missing
            if not data.get("body"):
                state.mode = "ASK_SCHEDULE_MESSAGE"
                state.schedule_to = data["to"]
                state.schedule_subject = data["subject"]
                state.schedule_send_at = data["send_at"]
                speak("What message would you like to send?")
                continue

            speak(send_scheduled_email(data))
            state.reset()
            continue

        # ================= FALLBACK =================
        speak("Sorry, I did not understand that.")
        continue

    # =====================================================
    # STATE: ASK EMAIL
    # =====================================================
    if state.mode == "ASK_EMAIL":
        email = extract_email(user_text)

        if not email:
            speak("That does not look like a valid email. Please try again.")
            continue

        state.recipient = email
        state.mode = "SEND_MESSAGE"
        speak("What is the message?")
        continue

    # =====================================================
    # STATE: SEND MESSAGE
    # =====================================================
    if state.mode == "SEND_MESSAGE":
        state.message = user_text
        state.mode = "CONFIRM_SEND"
        speak(f"Do you want to send this email to {state.recipient}?")
        continue

    # =====================================================
    # STATE: CONFIRM SEND
    # =====================================================
    if state.mode == "CONFIRM_SEND":
        if user_text in ["yes", "yeah", "confirm"]:
            send_email(
                to=state.recipient,
                body=state.message,
                attachments=[],
                drive_links=state.links
            )
            speak("Email sent successfully.")
        else:
            speak("Email cancelled.")
        state.reset()
        continue

    # =====================================================
    # STATE: ASK SCHEDULE MESSAGE
    # =====================================================
    if state.mode == "ASK_SCHEDULE_MESSAGE":
        data = {
            "to": state.schedule_to,
            "subject": state.schedule_subject,
            "body": user_text,
            "send_at": state.schedule_send_at
        }

        speak(send_scheduled_email(data))
        state.reset()
        continue
