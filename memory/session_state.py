class SessionState:
    def __init__(self):
        self.reset()

    def reset(self):
        # =====================================================
        # GLOBAL CONVERSATION MODE
        # =====================================================
        self.mode = "IDLE"

        # =====================================================
        # SEND EMAIL FLOW (EXISTING)
        # =====================================================
        self.recipient = None
        self.message = None
        self.attachments = []
        self.links = []

        # =====================================================
        # GENERIC INTENT CONTEXT
        # =====================================================
        self.intent = None
        self.query = None          # for search
        self.result_cache = None   # summarize / categorize

        # =====================================================
        # FOLLOW-UP (REMINDER) FLOW
        # =====================================================
        self.followup_email_id = None
        self.followup_time = None

        # =====================================================
        # SCHEDULED SEND FLOW (NEW)
        # =====================================================
        self.schedule_to = None
        self.schedule_subject = None
        self.schedule_body = None
        self.schedule_send_at = None

        # Flag: waiting for user to provide message body
        self.awaiting_schedule_message = False


state = SessionState()
