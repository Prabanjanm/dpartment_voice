def parse_subscription_filters(user_text: str):
    text = user_text.lower()

    if "unsubscribe" in text:
        action = "unsubscribe"
    else:
        action = "list"

    if "all" in text:
        count = 50
    else:
        import re
        match = re.search(r"\d+", text)
        count = int(match.group()) if match else 5

    return {
        "action": action,
        "count": count,
        "query": (
            "(unsubscribe OR subscription OR newsletter "
            "OR mailing list OR manage preferences)"
        )
    }
