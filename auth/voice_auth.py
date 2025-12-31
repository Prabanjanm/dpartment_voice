import numpy as np
import librosa
import sounddevice as sd
import scipy.io.wavfile as wav
import os
from numpy.linalg import norm
from config import AUTH_THRESHOLD

FS = 16000
DURATION = 3
VOICEPRINT_PATH = "auth/voiceprint.npy"

def authenticate():
    if not os.path.exists(VOICEPRINT_PATH):
        print("❌ Voice not enrolled")
        return False

    try:
        stored = np.load(VOICEPRINT_PATH)
    except Exception:
        print("❌ Corrupt voiceprint file")
        return False

    print("🎙️ Authenticating... Speak now")

    audio = sd.rec(int(DURATION * FS), samplerate=FS, channels=1)
    sd.wait()
    wav.write("auth.wav", FS, audio)

    y, _ = librosa.load("auth.wav", sr=FS)
    mfcc = librosa.feature.mfcc(y=y, sr=FS, n_mfcc=13)
    test = np.mean(mfcc, axis=1)

    score = np.dot(test, stored) / (norm(test) * norm(stored))
    print("🔐 Similarity score:", score)

    return score > AUTH_THRESHOLD
