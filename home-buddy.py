import cv2 as cv
import serial
import time
import math
from ultralytics import YOLO
from Rosmaster_Lib import Rosmaster

# Creating an object for the ROSMASTER X3 PLUS
homeBuddy = Rosmaster()

# Import fine-tuned yolo model for object detection
yolo_model = YOLO(
    "/home/pi/Desktop/HomeBuddy/scripts/object-detection/training/runs/detect/object-detection-model-2/weights/best.pt")

LINEAR_SPEED = 0.3
ANGULAR_SPEED = 0.8

# Function to make the robot rotate by a given degree
def rotate_by_degree(degrees):
    radians = math.radians(degrees)
    duration = abs(radians / ANGULAR_SPEED)
    speed = ANGULAR_SPEED if degrees > 0 else -ANGULAR_SPEED
    homeBuddy.set_car_motion(0, 0, speed)
    time.sleep(duration)
    homeBuddy.set_car_motion(0, 0, 0)

# Function to make the robot move straight by a given distance
def move_straight(distance):
    duration = abs(distance / LINEAR_SPEED)
    homeBuddy.set_car_motion(LINEAR_SPEED, 0, 0)
    time.sleep(duration)
    homeBuddy.set_car_motion(0, 0, 0)

# Function to return to the starting position
def return_to_start(distance):
    print("Returning to start position...")
    rotate_by_degree(220)
    move_straight(distance)

# Function to navigate to a specific point
def navigate_sequence(angle, distance, target_name, target_object):
    print(f"Going to {target_name}")

    # Step 1: Rotate and move
    rotate_by_degree(angle)
    move_straight(distance)

    # Step 2: Lower camera to detect object
    homeBuddy.set_uart_servo_angle_array([90, 15, 15, 55, 90, 30])
    time.sleep(2)

    print(f"Scanning for {target_object}...")

    # Object detection
    cap = cv.VideoCapture(0)
    object_found = False

    for _ in range(10):
        ret, frame = cap.read()
        if not ret:
            continue

        results = yolo_model(frame)

        for r in results:
            cls_names = r.names

            for box in r.boxes:
                cls_id = int(box.cls[0])
                detected_name = cls_names[cls_id]

                if detected_name.lower() == target_object.lower():
                    print(f"TARGET OBJECT FOUND: {detected_name}")
                    object_found = True
                    break
            if object_found:
                break
        if object_found:
            break

    cap.release()

    # Step 3: Grab the object if the detected object matches the target object
    if object_found:
        print(f"{target_object} detected. Grabbing...")

        # Grab motion
        homeBuddy.set_uart_servo_angle_array([90, 15, 25, 55, 90, 140])
        time.sleep(2)

        # Lift arm
        homeBuddy.set_uart_servo_angle_array([90, 90, 0, 90, 90, 140])
        time.sleep(2)

    else:
        print(f"{target_object} NOT found. Skipping grab.")

    # Return to the starting position if not found
    return_to_start(distance)


# Function to go fetch phone
def go_to_point_A():
    print("Going to point A")
    navigate_sequence(55, 0.75, "A", "phone")


# Function to bring cup
def go_to_point_B():
    print("Going to point B")
    navigate_sequence(-30, 1.0, "B", "cup")


# Function to bring glasses
def go_to_point_C():
    print("Going to point C")
    navigate_sequence(30, 1.2, "C", "glasses")


# Function to bring shoes
def go_to_point_D():
    print("Going to point D")
    navigate_sequence(-50, 0.90, "D", "shoes")


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
    time.sleep(2)
    homeBuddy.set_uart_servo_angle_array([90, 90, 0, 90, 90, 180])
    time.sleep(2)

    # Initialize voice module
    try:
        ser = serial.Serial("/dev/ttyUSB2", 115200, timeout=1)
        time.sleep(1)
    except Exception as e:
        print("Serial port error:", e)
        return

    cmds = [b'AT+ASR=ON\r\n', b'AT+CMD=1\r\n', b'AT+DEBUG=1\r\n']
    for cmd in cmds:
        ser.write(cmd)
        time.sleep(0.2)
    ser.flushInput()
    print("Voice module ready to listen to commands..")

    while True:
        try:
            if ser.in_waiting:
                data = ser.readline()
                if data:
                    command_received = data.decode(errors="ignore").strip().lower()
                    print("Voice command_received heard: ", command_received)

                    # Wake up robot using wake word "Hi Yahboom!"
                    if command_received == "$b000#":
                        print("Wake word detected.")

                    # Going to Location A (location of phone)
                    elif command_received == "$b019#":
                        send_voice_feedback(ser, "$A019#")
                        go_to_point_A()

                    # Going to location B (Location of cup)
                    elif command_received == "$b020#":
                        send_voice_feedback(ser, "$A020#")
                        go_to_point_B()

                    # Going to location C (Location of glasses)
                    elif command_received == "$b021#":
                        send_voice_feedback(ser, "$A021#")
                        go_to_point_C()

                    # Going to location D (Location of shoes)
                    elif command_received == "$b022#":
                        send_voice_feedback(ser, "$A022#")
                        go_to_point_D()


        except KeyboardInterrupt:
            print("Exiting...")
            ser.close()
            break


if __name__ == "__main__":
    main()
