import cv2 as cv
import os
import serial
import time
import math
from ultralytics import YOLO
from Rosmaster_Lib import Rosmaster

# Creating an object for the ROSMASTER X3 PLUS
homeBuddy = Rosmaster()

# Import fine-tuned yolo model for object detection
yolo_model = YOLO("/home/pi/Desktop/HomeBuddy/scripts/object-detection/training/runs/detect/object-detection-model-12/weights/best.pt")

LINEAR_SPEED = 0.3
ANGULAR_SPEED = 0.8

def rotate_by_degree(degrees):
    # Convert degrees to radians
    radians = math.radians(degrees)

    # Formula to calculate time needed
    duration = abs(radians / ANGULAR_SPEED)

    # Determine direction: positive for left, negative for right
    speed = ANGULAR_SPEED if degrees > 0 else -ANGULAR_SPEED

    homeBuddy.set_car_motion(0, 0, speed)
    time.sleep(duration)
    homeBuddy.set_car_motion(0, 0, 0)  # Stop

def move_straight(distance):
    # Formula to calculate time needed
    duration = abs(distance / LINEAR_SPEED)

    homeBuddy.set_car_motion(LINEAR_SPEED, 0, 0)
    time.sleep(duration)
    homeBuddy.set_car_motion(0, 0, 0)

# Rotate and move back to the starting point
def return_to_start(angle, distance):
    print("Returning to start position...")
    rotate_by_degree(180)
    move_straight(distance)
    rotate_by_degree(180)
    rotate_by_degree(-angle)

# Detect target object using the camera
def detect_object_with_camera(target_object_name, timeout=10):
    print(f"Looking for {target_object_name}...")

    # Move camera downwards to look at the floor/object
    homeBuddy.set_uart_servo_angle_array([90, 90, 0, 90, 90, 180])
    time.sleep(1)

    cap = cv.VideoCapture(0)
    start_time = time.time()
    found = False

    while (time.time() - start_time) < timeout:
        ret, frame = cap.read()
        if not ret:
            continue

        # Run YOLO inference
        results = yolo_model(frame, verbose=False)

        # Check results for our target object
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                detected_name = yolo_model.names[cls_id]

                if detected_name == target_object_name and conf > 0.5:
                    print(f"Found {target_object_name} with confidence {conf:.2f}!")
                    found = True
                    break
            if found: break

        if found: break
        time.sleep(0.1)

    cap.release()

    # Reset arm/camera position
    homeBuddy.set_uart_servo_angle_array([90, 90, 90, 90, 90, 180])
    time.sleep(1)

    return found

# Rotate and move to a target point, detect and grab object, then move back to starting point
def navigate_sequence(angle, distance, target_name, target_object):
    print(f"Going to {target_name}")
    # Step 1: Rotate and position the robot to the target point
    rotate_by_degree(angle)
    # Step 2: Move towards the target point
    move_straight(distance)
    # Step 3: Detect the object and grab it
    found =  detect_object_with_camera(target_object)

    if found:
        print(f"Object {target_object} detected. Returning home.")
        # If the object is correctly detected, return to the starting position
        return_to_start(angle, distance)
        # TODO: To add function to release the object
    else:
        print(f"{target_object} NOT found.")
        return_to_start(angle, distance)

# To be replaced by go_fetch_my_keys 
def go_to_point_A():
    print("Going to point A")
    navigate_sequence(45, 2.5, "A", "keys")


# To be replaced by bring_my_cup
def go_to_point_B():
    print("Going to point B")
    navigate_sequence(-30, 5.5, "B", "cup")
    
# To be replaced by give_me_my_glasses
def go_to_point_C():
    print("Going to point C")
    navigate_sequence(90, 1.5, "C", "glasses")

def send_voice_feedback(ser, code):
    try:
        ser.write(code.encode())
        print(f"Voice feedback sent: {code}")
    except:
        print("Voice feedback FAILED!")

def main():
    print("HomeBuddy Initialized")
    
    # Initial arm position
    homeBuddy.set_uart_servo_angle_array([90, 90, 90, 90, 90, 180])
    time.sleep(1)
    homeBuddy.set_uart_servo_angle_array([90, 90, 0, 90, 90, 180])
    
    # Initialize voice module
    try:
        voice_serial = serial.Serial("/dev/ttyUSB2", 115200, timeout=5)
    except Exception as e:
        print("Serial port error:", e)
        return

    cmds = [b'AT+ASR=ON\r\n', b'AT+CMD=1\r\n', b'AT+DEBUG=1\r\n']
    for cmd in cmds:
        voice_serial.write(cmd)
        time.sleep(0.2)
    voice_serial.flushInput()
    print("Voice module ready to listen to commands..")
    
    while True:
        try:
            if voice_serial.in_waiting:
                data = voice_serial.readline()
                if data:
                    command_received = data.decode(errors="ignore").strip().lower()
                    print("Voice command_received heard: ", command_received)
                    if command_received == "$b000#":
                        print("Wake word detected.")
                    elif command_received == "$b019#":
                        send_voice_feedback(voice_serial, "$A019#")
                        go_to_point_A()
                    elif command_received == "$b020#":
                        send_voice_feedback(voice_serial, "$A020#")
                        go_to_point_B()
                    elif command_received == "$b021#":
                        send_voice_feedback(voice_serial, "$A021#")
                        go_to_point_C()

        except KeyboardInterrupt:
            print("Exiting...")
            voice_serial.close()
            break


if __name__ == "__main__":
    main()
    