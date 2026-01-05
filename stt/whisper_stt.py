import speech_recognition as sr


class SpeechToText:
    """
    Handles microphone input and converts speech to text
    using Google Speech Recognition.
    """

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self, timeout: int = 5) -> str:
        """
        Listens to microphone input and returns recognized text.
        Allows pauses while speaking.
        """

        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=None  # 🔑 allow natural pauses
                )
            except sr.WaitTimeoutError:
                return ""

        try:
            text = self.recognizer.recognize_google(audio)
            return text.lower()

        except sr.UnknownValueError:
            return ""

        except sr.RequestError:
            return ""



# ✅ Singleton instance (used everywhere)
stt = SpeechToText()
