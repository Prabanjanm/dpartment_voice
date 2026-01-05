import pyttsx3
import threading
import queue
import time

# ---------- TTS ENGINE ----------
engine = pyttsx3.init(driverName="sapi5")
engine.setProperty("rate", 170)
engine.setProperty("volume", 1.0)

for voice in engine.getProperty("voices"):
    if "english" in voice.name.lower():
        engine.setProperty("voice", voice.id)
        break

# ---------- SPEECH QUEUE ----------
_speech_queue = queue.Queue()

def _tts_worker():
    while True:
        text = _speech_queue.get()
        if text is None:
            break

        try:
            engine.say(text)
            engine.runAndWait()
        except RuntimeError:
            pass  # ignore run loop errors safely

        time.sleep(0.1)
        _speech_queue.task_done()

# ---------- START SINGLE WORKER ----------
_thread = threading.Thread(target=_tts_worker, daemon=True)
_thread.start()

def speak(text: str):
    if not text:
        return

    print("🤖", text)
    _speech_queue.put(text)
