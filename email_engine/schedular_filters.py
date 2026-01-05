import json
import re
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def safe_json_extract(text: str) -> dict:
    """
    Extract first valid JSON object from LLM output
    """
    if not text:
        return {}

    # Remove markdown
    text = re.sub(r"```json|```", "", text).strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {}
