# Dont Forgot To give Respect To Me(Arya) If you use It 

# TextToSpeech.py

import os
import pygame
import asyncio
import edge_tts
import time
import datetime
from dotenv import dotenv_values

# Paths
DATA_DIR = "Data"
AUDIO_FILE = os.path.join(DATA_DIR, "output_audio.mp3")
SILENCE_FILE = os.path.join(DATA_DIR, "silence.mp3")
LOG_FILE = os.path.join("logs", "history.log")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Voice setup
env_vars = dotenv_values(".env")
DEFAULT_VOICE = env_vars.get("AssistantVoice", "en-US-AriaNeural")
DEFAULT_PITCH = "+0Hz"
DEFAULT_RATE = "+0%"

# Init mixer
pygame.mixer.init()

# Save logs
def log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        f.write(f"{timestamp} {text.strip()}\n")

# Audio Generation
async def generate_audio(text, voice, pitch, rate):
    if os.path.exists(AUDIO_FILE):
        os.remove(AUDIO_FILE)
    communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate)
    await communicate.save(AUDIO_FILE)

# Play Audio
def play_audio(func=lambda: True):
    try:
        pygame.mixer.music.load(AUDIO_FILE)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if func() is False:
                break
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"[❌ Playback Error]: {e}")
    finally:
        try:
            pygame.mixer.music.stop()
            time.sleep(0.2)
            pygame.mixer.music.load(SILENCE_FILE)
        except:
            pass

# Split long text
def chunk_text(text, max_len=300):
    sentences = text.split(".")
    chunk = ""
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if len(chunk) + len(s) < max_len:
            chunk += s + ". "
        else:
            yield chunk.strip()
            chunk = s + ". "
    if chunk:
        yield chunk.strip()

# 🎙️ Main Exported TTS Function
def TextToSpeech(text, voice=DEFAULT_VOICE, pitch=DEFAULT_PITCH, rate=DEFAULT_RATE):
    chunks = list(chunk_text(text))
    for chunk in chunks:
        try:
            print(f"[🔊 Speaking chunk...]")
            asyncio.run(generate_audio(chunk, voice, pitch, rate))
            play_audio()
        except Exception as e:
            print(f"[❌ Error]: {e}")
    log(text)
    print("[✅ Done Speaking]")

# Optional CLI loop
def start_tts():
    print("=== Terminal Text-to-Speech ===")
    print("Enter 'file' to read from input.txt")
    print("Enter 'exit' to quit\n")

    while True:
        user_input = input("📝 Enter text: ").strip()
        if user_input.lower() == "exit":
            print("👋 Exiting.")
            break
        elif user_input.lower() == "file":
            if not os.path.exists("input.txt"):
                print("❌ No input.txt file found.")
                continue
            with open("input.txt", "r", encoding="utf-8") as f:
                content = f.read()
            TextToSpeech(content)
        else:
            TextToSpeech(user_input)

if __name__ == "__main__":
    start_tts()
