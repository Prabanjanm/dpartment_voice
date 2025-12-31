class SessionState:
    def __init__(self):
        self.reset()

    def reset(self):
        # Conversation mode
        self.mode = "IDLE"

        # Send email flow
        self.recipient = None
        self.message = None
        self.attachments = []
        self.links = []

        # Generic intent context (new features)
        self.intent = None
        self.query = None          # for search
        self.result_cache = None   # for summarize / categorize results


state = SessionState()
