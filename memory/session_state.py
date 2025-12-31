class SessionState:
    def __init__(self):
        self.mode = "IDLE"
        self.recipient = None
        self.message = None
        self.attachments = []
        self.links = []

    def reset(self):
        self.mode = "IDLE"
        self.recipient = None
        self.message = None
        self.attachments = []
        self.links = []
state = SessionState()