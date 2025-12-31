from stt.whisper_stt import listen
from tts.speaker import speak
import time

def wait_for_wake_word():
    speak("System is idle. Say Jarvis to wake me.")
    print("🟡 Waiting for wake word...")

    while True:
        try:
            text, _ = listen(2)
            print("Heard (wake check):", text)

            if "email" in text.lower():
                print("🟢 Wake word detected")
                speak("Yes, I am listening")
                return

        except Exception as e:
            print("Wake word error:", e)

        time.sleep(0.5)
