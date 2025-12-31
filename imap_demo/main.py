from llm_intent import get_intent
from imap_action import (
    read_emails,
    delete_emails,
    search_emails
)

print("📬 Smart IMAP Email Assistant")
print("Type a command (type 'exit' to quit)\n")

# Holds ambiguity state
pending_results = []
pending_action = None

while True:
    user_input = input("🧑 You: ").strip().lower()
    if user_input == "exit":
        break

    # ============================
    # HANDLE USER SELECTION (1,2,3)
    # ============================
    if pending_results and user_input.isdigit():
        choice = int(user_input)

        if 1 <= choice <= len(pending_results):
            selected = pending_results[choice - 1]
            email_id = selected["id"]

            if pending_action == "read":
                read_emails(scope="id", email_id=email_id)

            elif pending_action == "delete":
                delete_emails(scope="id", email_id=email_id)

        else:
            print("❌ Invalid selection.")

        pending_results = []
        pending_action = None
        continue

    # ============================
    # PARSE INTENT USING LLM
    # ============================
    intent = get_intent(user_input)
    print("DEBUG INTENT:", intent)

    action = intent.get("action")
    search_type = intent.get("search_type", "none")

    # ============================
    # DIRECT READ / DELETE (NO SEARCH)
    # ============================
    if search_type == "none":
        if action == "read":
            read_emails(
                scope=intent.get("scope", "latest"),
                count=intent.get("count", 1)
            )
            continue

        if action == "delete":
            delete_emails(
                scope=intent.get("scope", "latest"),
                count=intent.get("count", 1)
            )
            continue

        print("🤖 Sorry, I didn’t understand that.")
        continue

    # ============================
    # SEARCH-BASED FLOW
    # ============================
    results = search_emails(
        search_type=search_type,
        query=intent.get("query", ""),
        limit=intent.get("count", 5)
    )

    if not results:
        print("📭 No matching emails found.")
        continue

    # If only one match → act directly
    if len(results) == 1:
        email_id = results[0]["id"]
        if action == "read":
            read_emails(scope="id", email_id=email_id)
        elif action == "delete":
            delete_emails(scope="id", email_id=email_id)
        continue

    # Multiple matches → ask user
    print("\n📌 Multiple emails found:")
    for r in results:
        print(f"{r['index']}. From: {r['from']} | Subject: {r['subject']}")

    print("\n👉 Type the number of the email you want:")
    pending_results = results
    pending_action = action
