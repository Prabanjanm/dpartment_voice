import sounddevice as sd
import numpy as np
import librosa
import scipy.io.wavfile as wav

FS = 16000
DURATION = 4

print("Speak clearly:")
print("My voice is my secure password")

audio = sd.rec(int(DURATION * FS), samplerate=FS, channels=1)
sd.wait()
wav.write("enroll.wav", FS, audio)

y, _ = librosa.load("enroll.wav", sr=FS)
mfcc = librosa.feature.mfcc(y=y, sr=FS, n_mfcc=13)
voiceprint = np.mean(mfcc, axis=1)

np.save("auth/voiceprint.npy", voiceprint)
print("✅ Voice enrolled successfully")
