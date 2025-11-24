import rospy
from geometry_msgs.msg import Twist

import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
import spacy
import pyttsx3
import threading
from datetime import datetime

# -------------------------
# 1) ROS INITIALIZATION
# -------------------------

rospy.init_node("voice_control_node", anonymous=True)
cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)


def move_robot(linear_x=0.0, angular_z=0.0):
    msg = Twist()
    msg.linear.x = linear_x
    msg.angular.z = angular_z
    cmd_pub.publish(msg)


# -------------------------
# 2) SPEECH ENGINE SETUP
# -------------------------

MODEL_PATH = "/home/ubuntu/vosk-model-small-en-us-0.15"
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


threading.Thread(target=tts_worker, daemon=True).start()


def speak(text):
    speech_q.put(text)


# -------------------------
# 3) MICROPHONE CALLBACK
# -------------------------

def callback(indata, frames, time, status):
    if status:
        print(status)
    audio_q.put(bytes(indata))


# -------------------------
# 4) COMMAND LOGIC
# -------------------------

def process_command(text):
    text = text.lower()
    understood = False

    # MOVEMENT COMMANDS
    if "forward" in text:
        speak("Moving forward.")
        move_robot(0.2, 0)
        understood = True

    elif "back" in text or "backward" in text:
        speak("Reversing.")
        move_robot(-0.2, 0)
        understood = True

    elif "left" in text:
        speak("Turning left.")
        move_robot(0, 0.4)
        understood = True

    elif "right" in text:
        speak("Turning right.")
        move_robot(0, -0.4)
        understood = True

    elif "stop" in text or "halt" in text:
        speak("Stopping.")
        move_robot(0, 0)
        understood = True

    # EXTRA COMMANDS
    elif "time" in text:
        current_time = datetime.now().strftime("%H:%M")
        speak(f"The current time is {current_time}.")
        understood = True

    if not understood:
        speak("I didn't understand that command.")


# -------------------------
# 5) SPEECH RECOGNITION LOOP
# -------------------------

def listen_and_recognize():
    with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=callback
    ):
        speak("Voice control is active. Say a command.")
        print("Listening...")

        while not rospy.is_shutdown():
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


# -------------------------
# 6) START
# -------------------------

speak("Voice assistant is online and ready.")
listen_and_recognize()
