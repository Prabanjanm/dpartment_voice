import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_json(text: str) -> dict:
    """
    Safely extract JSON object from LLM output
    """
    # Remove markdown code blocks if any
    text = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "intent": "unknown",
            "content": ""
        }


def detect_intent(text: str) -> dict:
    """
    Detect user intent using:
    1. Rule-based hard overrides (HIGH PRIORITY)
    2. LLM classification (fallback)
    """

    user_text = text.lower().strip()

    # =====================================================
    # 🔒 HARD RULE OVERRIDES (NEVER FAIL)
    # =====================================================
    if any(word in user_text for word in ["summarize", "summary"]):
        return {
            "intent": "summarize",
            "content": user_text
        }

    if any(word in user_text for word in ["search", "find", "lookup"]):
        return {
            "intent": "search",
            "content": user_text
        }

    if any(word in user_text for word in ["categorize", "classify", "group"]):
        return {
            "intent": "categorize",
            "content": user_text
        }

    # =====================================================
    # 🧠 LLM-BASED INTENT CLASSIFICATION
    # =====================================================
    prompt = f"""
You are an email assistant intent classifier.

Classify the user's command into EXACTLY ONE intent
from the list below:

- send       → sending a new email
- read       → reading emails aloud
- delete     → deleting emails
- summarize  → summarizing emails
- search     → searching emails
- categorize → grouping/classifying emails
- unknown    → if nothing matches

Rules:
- If user asks to summarize emails → intent MUST be "summarize"
- If user asks to find/search emails → intent MUST be "search"
- If user asks to group/classify → intent MUST be "categorize"
- If user asks to read emails → intent MUST be "read"

User command:
"{text}"

Return ONLY valid JSON.
NO markdown.
NO explanation.

JSON format:
{{
  "intent": "<intent>",
  "content": "<important keywords or filters>"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()
    print("🧠 Raw LLM output:", raw)

    result = extract_json(raw)

    # =====================================================
    # 🛡️ SAFETY FALLBACK
    # =====================================================
    if "intent" not in result:
        return {
            "intent": "unknown",
            "content": ""
        }

    return result
