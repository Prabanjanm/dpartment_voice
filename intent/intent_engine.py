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
    # Remove markdown code blocks
    text = re.sub(r"```json|```", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "intent": "unknown",
            "content": ""
        }

def detect_intent(text: str) -> dict:
    prompt = f"""
You are a voice-based email assistant.

User speech:
"{text}"

Return ONLY valid JSON.
No markdown.
No explanation.

JSON format:
{{
  "intent": "read | send | reply | confirm | unknown",
  "content": "optional text"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()
    print("🧠 Raw LLM output:", raw)

    return extract_json(raw)
