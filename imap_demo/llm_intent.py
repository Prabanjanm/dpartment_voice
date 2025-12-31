import os, json, re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_intent(text: str) -> dict:
    prompt = f"""
Convert the user request into JSON only.

User request:
"{text}"

Actions:
- read
- delete

Search types:
- content
- sender
- subject
- none

Return JSON:
{{
  "action": "",
  "search_type": "",
  "query": "",
  "scope": "latest",
  "count": 5
}}

Examples:
"read email about internship" → search_type=content, query=internship
"delete mail from amazon" → search_type=sender, query=amazon
"""

    # same OpenAI call as before


    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = re.sub(r"```json|```", "", res.choices[0].message.content)

    try:
        return json.loads(raw)
    except:
        return {"action": "unknown"}
