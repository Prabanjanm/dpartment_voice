import re
from datetime import datetime, timedelta

def parse_followup_time(text: str):
    text = text.lower()
    now = datetime.now()

    # in X minutes
    m = re.search(r"in\s+(\d+)\s+minute", text)
    if m:
        return now + timedelta(minutes=int(m.group(1)))

    # in X hours
    h = re.search(r"in\s+(\d+)\s+hour", text)
    if h:
        return now + timedelta(hours=int(h.group(1)))

    # in X days
    d = re.search(r"in\s+(\d+)\s+day", text)
    if d:
        return now + timedelta(days=int(d.group(1)))

    # tomorrow
    if "tomorrow" in text:
        return now + timedelta(days=1)

    # next week
    if "next week" in text:
        return now + timedelta(days=7)

    # specific date (e.g. 5 jan, jan 5)
    date_match = re.search(r"(\d{1,2})\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", text)
    if date_match:
        day = int(date_match.group(1))
        month = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"].index(date_match.group(2)) + 1
        return datetime(now.year, month, day, 9, 0)

    # default → 5 minutes
    return now + timedelta(minutes=5)
