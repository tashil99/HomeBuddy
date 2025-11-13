import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
import spacy
import pyttsx3
import threading
from datetime import datetime

MODEL_PATH = "../vosk-model-small-en-us-0.15"
model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

nlp = spacy.load("en_core_web_sm")

audio_q = queue.Queue()
speech_q = queue.Queue()

engine = pyttsx3.init()
engine.setProperty('rate', 165)
engine.setProperty('volume', 1.0)


def tts_worker():
    while True:
        text = speech_q.get() 
        if text:
            print(f"Assistant: {text}")
            engine.say(text)
            engine.runAndWait()
        speech_q.task_done()


# Start the TTS thread
threading.Thread(target=tts_worker, daemon=True).start()


def speak(text):
    speech_q.put(text)


# AUDIO INPUT CALLBACK
def callback(indata, frames, time, status):
    if status:
        print(status)
    audio_q.put(bytes(indata))


# COMMAND PROCESSING
def process_command(text):
    understood = False

    if "light" in text:
        if "on" in text:
            speak("Okay, turning the lights on.")
            understood = True
        elif "off" in text:
            speak("Got it, turning the lights off.")
            understood = True

    elif "music" in text and "play" in text:
        speak("Sure, playing some music.")
        understood = True

    elif "temperature" in text or "weather" in text:
        speak("The room temperature is 23 degrees Celsius.")
        understood = True

    elif "time" in text:
        current_time = datetime.now().strftime("%H:%M")
        speak(f"The current time is {current_time}.")
        understood = True

    if not understood:
        speak("Sorry, I didn’t quite understand that command.")


# LISTEN & RECOGNIZE
def listen_and_recognize():
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        speak("I am now listening for your commands.")
        print("Listening...")

        while True:
            data = audio_q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text.strip():
                    print(f"🗣 Recognized: {text}")
                    process_command(text)
            else:
                partial = json.loads(recognizer.PartialResult())
                if partial.get("partial", "").strip():
                    print(f"…Recognizing: {partial['partial']}", end='\r')


if __name__ == "__main__":
    speak("Voice assistant is online and ready.")
    listen_and_recognize()
