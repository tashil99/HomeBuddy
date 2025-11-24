#!/usr/bin/env python3
import threading
import time
import json
import queue
import cv2
import numpy as np
from Rosmaster_Lib import Rosmaster
from ultralytics import YOLO
import pyaudio
import vosk
from collections import deque


class VoiceControlledNavigationRobot:
    def __init__(self):
        # Initialize the robot car
        self.car = Rosmaster()
        self.car.create_receive_threading()

        # Camera initialization
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # Load YOLOv8 model (make sure best.pt is in your working directory)
        try:
            self.yolo_model = YOLO('best.pt')
            print("YOLOv8 model loaded successfully")
        except:
            print("Warning: Could not load best.pt, using YOLOv8n as fallback")
            self.yolo_model = YOLO('C:/Middlesex/HomeBuddy/scripts/object-detection/training/runs/detect/object-detection-model-3/weights/best.pt')

        # Voice recognition setup
        self.sample_rate = 16000
        self.chunk_size = 4096
        self.audio_queue = queue.Queue()

        # Load Vosk model (download from https://alphacephei.com/vosk/models)
        # Example: vosk-model-small-en-us-0.15
        try:
            self.vosk_model = vosk.Model("vosk-model-small-en-us-0.15")
            print("Vosk model loaded successfully")
        except:
            print("Warning: Vosk model not found. Please download a model from:")
            print("https://alphacephei.com/vosk/models")
            self.vosk_model = None

        # Audio setup
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self.audio_callback
        )

        # Recognition setup
        self.recognizer = vosk.KaldiRecognizer(self.vosk_model, self.sample_rate) if self.vosk_model else None

        # State variables
        self.target_object = None
        self.navigation_active = False
        self.last_detection_time = 0
        self.object_lost_count = 0
        self.search_direction = 1
        self.detection_history = deque(maxlen=10)

        print("Robot initialization complete!")
        print("Say commands like: 'go to person' or 'find chair'")

    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream"""
        self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def listen_for_commands(self):
        """Continuous voice command listening"""
        print("Voice listener started...")

        while True:
            if self.recognizer is None:
                time.sleep(1)
                continue

            try:
                # Get audio data from queue
                if not self.audio_queue.empty():
                    data = self.audio_queue.get()

                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '').lower()

                        if text:
                            print(f"Recognized: {text}")
                            self.process_voice_command(text)

                    # Process partial results for real-time feedback
                    else:
                        partial = json.loads(self.recognizer.PartialResult())
                        partial_text = partial.get('partial', '')
                        if partial_text:
                            print(f"Listening: {partial_text}", end='\r')

            except Exception as e:
                print(f"Audio processing error: {e}")

            time.sleep(0.1)

    def process_voice_command(self, text):
        """Process recognized voice commands"""
        # Common object names that might be in your YOLO model
        object_keywords = {
            'person': 'person',
            'chair': 'chair',
            'cup': 'cup',
            'bottle': 'bottle',
            'car': 'car',
            'dog': 'dog',
            'cat': 'cat',
            'book': 'book',
            'cell phone': 'cell phone',
            'laptop': 'laptop'
        }

        # Look for navigation commands
        if any(word in text for word in ['go to', 'find', 'navigate to', 'locate']):
            for obj_name, yolo_name in object_keywords.items():
                if obj_name in text:
                    self.target_object = yolo_name
                    print(f"Target set to: {self.target_object}")

                    # Stop current navigation if any
                    self.navigation_active = False
                    time.sleep(0.5)

                    # Start new navigation
                    self.navigation_active = True
                    nav_thread = threading.Thread(target=self.navigate_to_object)
                    nav_thread.daemon = True
                    nav_thread.start()
                    return

        # Stop command
        elif any(word in text for word in ['stop', 'halt', 'cancel']):
            self.navigation_active = False
            self.car.set_car_motion(0, 0, 0)
            print("Navigation stopped")

    def detect_object(self):
        """Detect target object using YOLOv8"""
        if self.target_object is None:
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        # Run YOLO inference
        results = self.yolo_model(frame, verbose=False)

        # Process results
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Get class name and confidence
                    class_id = int(box.cls[0])
                    confidence = box.conf[0]
                    class_name = self.yolo_model.names[class_id]

                    # Check if this is our target object
                    if class_name == self.target_object and confidence > 0.5:
                        bbox = box.xyxy[0].cpu().numpy()
                        return {
                            'bbox': bbox,
                            'confidence': confidence,
                            'frame': frame
                        }

        return None

    def navigate_to_object(self):
        """Main navigation logic to reach the target object"""
        print(f"Starting navigation to: {self.target_object}")

        while self.navigation_active:
            detection = self.detect_object()

            if detection is not None:
                self.object_lost_count = 0
                self.last_detection_time = time.time()

                bbox = detection['bbox']
                frame = detection['frame']

                # Calculate object position in frame
                image_center_x = 320
                object_center_x = (bbox[0] + bbox[2]) / 2
                object_width = bbox[2] - bbox[0]
                object_height = bbox[3] - bbox[1]

                # Calculate control parameters
                turn_gain = 0.005
                forward_gain = 0.002

                # X-axis error (for turning)
                error_x = object_center_x - image_center_x
                turn_speed = -error_x * turn_gain
                turn_speed = np.clip(turn_speed, -1.0, 1.0)

                # Object size (for distance control)
                bbox_area = object_width * object_height
                max_area = 30000  # Stop when object is this big in frame

                if bbox_area < max_area:
                    # Move forward proportionally to how centered we are
                    forward_speed = 0.8 * (1 - abs(error_x) / image_center_x)
                    forward_speed = np.clip(forward_speed, 0.1, 0.8)
                else:
                    # Object is close enough, stop
                    forward_speed = 0
                    turn_speed = 0
                    print(f"Reached target: {self.target_object}")
                    self.navigation_active = False

                # Apply movement
                self.car.set_car_motion(forward_speed, 0, turn_speed)

                # Display info on frame (optional)
                cv2.rectangle(frame,
                              (int(bbox[0]), int(bbox[1])),
                              (int(bbox[2]), int(bbox[3])),
                              (0, 255, 0), 2)
                cv2.putText(frame, f'{self.target_object}: {detection["confidence"]:.2f}',
                            (int(bbox[0]), int(bbox[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                cv2.imshow('Object Detection', frame)
                cv2.waitKey(1)

            else:
                # Object not detected - search behavior
                self.object_lost_count += 1
                self.car.set_car_motion(0, 0, 0.3 * self.search_direction)

                # Change search direction periodically
                if self.object_lost_count > 50:  # ~5 seconds
                    self.search_direction *= -1
                    self.object_lost_count = 0
                    print("Changing search direction...")

                # Give up after prolonged search
                if time.time() - self.last_detection_time > 30:  # 30 seconds
                    print("Object not found. Stopping search.")
                    self.navigation_active = False
                    self.car.set_car_motion(0, 0, 0)

            time.sleep(0.1)  # Control loop frequency

    def main(self):
        """Main program loop"""
        try:
            # Start voice recognition thread
            voice_thread = threading.Thread(target=self.listen_for_commands)
            voice_thread.daemon = True
            voice_thread.start()

            print("Robot is ready! Voice commands active.")
            print("Available commands: 'go to [object]', 'find [object]', 'stop'")


            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            # Cleanup
            self.navigation_active = False
            self.car.set_car_motion(0, 0, 0)
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            self.cap.release()
            cv2.destroyAllWindows()


if __name__ == "__main__":
    robot = VoiceControlledNavigationRobot()
    robot.main()