# Personal AI Assistant - Local Setup Guide (with Multilingual & Voice Recognition)

# Note - This is not Actual Process is is just a Manual for upcoming Modifaction and some guid for you To How to Create Your Own Assistant You Can try My or Use your Own After Creating.

## 1. Install Required Software & Libraries

### a) Install Python & Dependencies
- Ensure Python 3.8+ is installed: https://www.python.org/downloads/
- Install required libraries:
  ```bash
  pip install speechrecognition pyttsx3 openai torch transformers nltk spacy langdetect librosa numpy pyaudio opencv-python dlib face_recognition flask sqlite3
  ```

### b) Setup Offline NLP & AI Models
- Download spaCy's English model:
  ```bash
  python -m spacy download en_core_web_sm
  ```

- Use OpenAI's GPT-2 locally (Hugging Face Transformers):
  ```python
  from transformers import pipeline
  chatbot = pipeline("text-generation", model="gpt2")
  response = chatbot("Hello, how can I help you?", max_length=50)
  print(response)
  ```

---

## 2. Setup Speech Recognition (Offline)
- Install CMU PocketSphinx:
  ```bash
  pip install pocketsphinx
  ```

- Code to recognize voice input:
  ```python
  import speech_recognition as sr
  recognizer = sr.Recognizer()
  with sr.Microphone() as source:
      print("Listening...")
      audio = recognizer.listen(source)
      text = recognizer.recognize_sphinx(audio)
      print("You said:", text)
  ```

---

## 3. Setup Text-to-Speech (Offline)
- Use pyttsx3 for offline voice response:
  ```python
  import pyttsx3
  engine = pyttsx3.init()
  engine.say("Hello Arya, how can I assist you?")
  engine.runAndWait()
  ```

---

## 4. Multilingual Support (Offline)
- Install **langdetect** for detecting the user's language:
  ```bash
  pip install langdetect
  ```

- Code to detect spoken language and respond accordingly:
  ```python
  from langdetect import detect

  def detect_language(text):
      lang = detect(text)
      print(f"Detected Language: {lang}")
      return lang

  user_input = "Hola, cómo estás?"
  language = detect_language(user_input)

  responses = {
      "es": "Estoy bien, ¿y tú?",
      "fr": "Je vais bien, et toi?",
      "en": "I'm fine, how about you?"
  }

  response = responses.get(language, "I'm fine, how about you?")
  print(response)
  ```

---

## 5. Voice Recognition for Personalized Responses
- Train the assistant to **identify who is speaking** and respond differently.
- Install necessary libraries:
  ```bash
  pip install librosa numpy pyaudio
  ```

- Code to recognize the speaker and respond accordingly:
  ```python
  import speech_recognition as sr
  import librosa
  import numpy as np

  # Load your voice sample
  your_voice, sr_rate = librosa.load("your_voice.wav", sr=16000)
  your_mfcc = np.mean(librosa.feature.mfcc(y=your_voice, sr=sr_rate, n_mfcc=40).T, axis=0)

  # Function to identify speaker
  def identify_speaker(audio_file):
      speaker_voice, sr_rate = librosa.load(audio_file, sr=16000)
      speaker_mfcc = np.mean(librosa.feature.mfcc(y=speaker_voice, sr=sr_rate, n_mfcc=40).T, axis=0)
      
      # Compare with your voice
      similarity = np.linalg.norm(your_mfcc - speaker_mfcc)
      
      if similarity < 50:  # Adjust this threshold as needed
          return "Arya"
      else:
          return "Guest"

  # Recognize voice and respond accordingly
  def recognize_and_respond():
      recognizer = sr.Recognizer()
      with sr.Microphone() as source:
          print("Listening...")
          audio = recognizer.listen(source)
          
          # Save audio to a temporary file
          with open("temp.wav", "wb") as f:
              f.write(audio.get_wav_data())
          
          speaker = identify_speaker("temp.wav")

          if speaker == "Arya":
              print("Hello Boss, how can I assist you?")
          else:
              print("Hello Guest, how may I help?")

  # Run the assistant
  recognize_and_respond()
  ```

---

## 6. Control ESP32 (Home Automation)
- Install Flask for a local API:
  ```bash
  pip install flask
  ```

- Create a simple API to send commands to ESP32:
  ```python
  from flask import Flask
  app = Flask(__name__)

  @app.route('/turn_on_light')
  def turn_on_light():
      # Send HTTP request to ESP32
      return "Light Turned ON!"

  if __name__ == '__main__':
      app.run(port=5000)
  ```
- ESP32 listens for API calls using MicroPython.

---

## 7. Face Recognition for Security
- Install OpenCV & Dlib:
  ```bash
  pip install opencv-python dlib face_recognition
  ```

- Code for face authentication:
  ```python
  import face_recognition
  import cv2

  known_face = face_recognition.load_image_file("arya.jpg")
  known_encoding = face_recognition.face_encodings(known_face)[0]

  video = cv2.VideoCapture(0)
  while True:
      ret, frame = video.read()
      face_locations = face_recognition.face_locations(frame)
      encodings = face_recognition.face_encodings(frame, face_locations)

      for encoding in encodings:
          match = face_recognition.compare_faces([known_encoding], encoding)
          if match[0]:
              print("Access Granted!")
          else:
              print("Access Denied!")

      cv2.imshow("Face Recognition", frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break

  video.release()
  cv2.destroyAllWindows()
  ```

---

## 8. Local Database for Storing Tasks & Notes
- Use SQLite for local storage:
  ```python
  import sqlite3
  conn = sqlite3.connect('assistant.db')
  c = conn.cursor()
  c.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, task TEXT)''')
  conn.commit()
  conn.close()
  ```

- Add a task:
  ```python
  def add_task(task):
      conn = sqlite3.connect('assistant.db')
      c = conn.cursor()
      c.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
      conn.commit()
      conn.close()
  ```

---

## 9. Running Everything Locally
- Launch Flask API for home automation:  
  ```bash
  python assistant_api.py
  ```
- Run the AI assistant:  
  ```bash
  python assistant.py
  ```

Your **personal AI assistant** is now running **completely offline** on your local system with **multilingual support and voice recognition!** 🚀
