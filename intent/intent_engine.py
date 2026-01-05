import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_json(text: str) -> dict:
    text = re.sub(r"```json|```", "", text).strip()
    try:
        return json.loads(text)
    except:
        return {"intent": "unknown", "content": ""}


def detect_intent(text: str) -> dict:
    user_text = text.lower().strip()

    # =====================================================
    # 🔒 HARD RULE ROUTING (HIGH CONFIDENCE)
    # =====================================================

    # ---------- GMAIL SCHEDULE SEND ----------
    if any(p in user_text for p in [
        "schedule mail",
        "schedule email",
        "send later",
        "send at",
        "send this at",
        "schedule this mail",
        "send this email later"
    ]):
        return {
            "intent": "schedule_send",
            "content": user_text
        }

    # ---------- FOLLOW UP ----------
    if any(p in user_text for p in [
        "follow up", "follow-up", "remind me", "set reminder"
    ]):
        return {
            "intent": "followup_schedule",
            "content": user_text
        }

    # ---------- SUMMARIZE ----------
    if re.search(r"\bsummary|summarize|summarie|summarise\b", user_text):
        return {
            "intent": "summarize",
            "content": user_text
        }

    # ---------- SEARCH ----------
    if re.search(r"\bsearch|find|lookup\b", user_text):
        return {
            "intent": "search",
            "content": user_text
        }

    # ---------- CATEGORIZE ----------
    if re.search(r"\bcategorize|classify|group\b", user_text):
        return {
            "intent": "categorize",
            "content": user_text
        }

    # ---------- READ ----------
    if re.search(r"\b(read|open|check)\b", user_text):
        return {
            "intent": "read",
            "content": user_text
        }

    # =====================================================
    # 🧠 LLM FALLBACK
    # =====================================================
    prompt = f"""
Classify the intent of the command.

Allowed intents:
- send
- read
- delete
- summarize
- search
- categorize
- followup_schedule
- schedule_send
- unknown

Command:
"{text}"

Return ONLY JSON:
{{ "intent": "<intent>", "content": "<filters>" }}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return extract_json(response.choices[0].message.content)
