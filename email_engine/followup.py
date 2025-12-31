import json
from datetime import datetime, timedelta

FILE = "memory/followups.json"

def add_followup(email_id, days):
    follow_date = datetime.now() + timedelta(days=days)
    data = []

    try:
        with open(FILE, "r") as f:
            data = json.load(f)
    except:
        pass

    data.append({
        "email_id": email_id,
        "follow_at": follow_date.isoformat()
    })

    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

    return "Follow-up reminder set successfully"
