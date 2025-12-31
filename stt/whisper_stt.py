import speech_recognition as sr

recognizer = sr.Recognizer()

def listen(seconds=5):
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)

        try:
            audio = recognizer.listen(
                source,
                timeout=seconds,
                phrase_time_limit=seconds
            )
        except sr.WaitTimeoutError:
            print("⏱️ Listening timed out")
            return "", "en"

    try:
        text = input("🧑 You: ").strip().lower()
        print("📝 Heard:", text)
        return text.lower(), "en"

    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return "", "en"

    except sr.RequestError as e:
        print("❌ Google STT error:", e)
        return "", "en"
