# Dont Forgot To give Respect To Me(Arya) If you use It 

# SpeechToText.py
import os
import datetime
import wave
import json
import speech_recognition as sr
from vosk import Model, KaldiRecognizer

VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15"
DATA_DIR = "audio"
AUDIO_FILE = os.path.join(DATA_DIR, "audio.wav")
LOG_FILE = os.path.join("logs", "history1.log")

if not os.path.exists(VOSK_MODEL_PATH):
    raise FileNotFoundError(f"Model not found at: {VOSK_MODEL_PATH}")

model = Model(VOSK_MODEL_PATH)

os.makedirs("logs", exist_ok=True)
os.makedirs("audio", exist_ok=True)

def log_transcript(text):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {text.strip()}\n")

def listen_and_save(timeout=4, phrase_time_limit=7):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            with open(AUDIO_FILE, "wb") as f:
                f.write(audio.get_wav_data())
            return True
        except sr.WaitTimeoutError:
            print("⏱ Timeout: No speech detected.")
        except Exception as e:
            print(f"❌ Error: {e}")
    return False

def transcribe_audio():
    wf = wave.open(AUDIO_FILE, "rb")
    recognizer = KaldiRecognizer(model, wf.getframerate())
    final_text = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result_json = recognizer.Result()
            text = json.loads(result_json).get("text", "")
            final_text += text + " "

    final_result = recognizer.FinalResult()
    final_text += json.loads(final_result).get("text", "")
    wf.close()

    final_text = final_text.strip()
    if final_text:
        log_transcript(final_text)
        print(f"📝 You said: {final_text}")
    else:
        pass
    return final_text

def SpeechRecognition():
    if listen_and_save():
        return transcribe_audio()
    return ""
