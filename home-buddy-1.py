import cv2
import os
import time
import math
import threading
from ultralytics import YOLO
from Rosmaster_Lib import Rosmaster

robot = Rosmaster()

MODEL_PATH = "/home/pi/Desktop/HomeBuddy/scripts/object-detection/training/runs/detect/object-detection-model-12/weights/best.pt"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

yolo_model = YOLO(MODEL_PATH)

latest_frame = None
processed_frame = None
detected_class = None
running = True
lock = threading.Lock()

TARGET_CLASS = "glasses"

# ---------------------------------------------
# Camera Thread
# ---------------------------------------------
def camera_thread():
    global latest_frame, running

    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("Camera error: cannot open.")
        running = False
        return

    while running:
        ret, frame = cap.read()
        if ret:
            with lock:
                latest_frame = frame.copy()

    cap.release()

# ---------------------------------------------
# YOLO Thread
# ---------------------------------------------
def yolo_thread():
    global latest_frame, processed_frame, detected_class, running

    class_colors = {
        'book': (0, 255, 0),
        'cup': (255, 0, 0),
        'glasses': (0, 0, 255),
        'keys': (255, 255, 0),
        'phone': (255, 0, 255),
        'shoes': (0, 255, 255)
    }

    while running:
        with lock:
            frame = latest_frame.copy() if latest_frame is not None else None

        if frame is None:
            time.sleep(0.001)
            continue

        results = yolo_model.predict(
            source=frame,
            imgsz=320,
            conf=0.25,
            iou=0.55,
            device="cpu",
            verbose=False
        )

        boxes = results[0].boxes
        names = results[0].names

        detected_class = None

        if boxes is not None:
            for box in boxes:
                cls = int(box.cls[0])
                name = names[cls]

                if name == TARGET_CLASS:
                    detected_class = name

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                color = class_colors.get(name, (255, 255, 255))

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"{name}: {float(box.conf[0]):.2f}"
                cv2.putText(frame, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        processed_frame = frame


# ---------------------------------------------
# Movement settings
# ---------------------------------------------
LINEAR_SPEED = 0.3
ANGULAR_SPEED = 0.8
STOP_DELAY = 0.5

# Manual extra rotation when returning (degrees)
RETURN_ROTATION_OFFSET = 42     # ← CHANGE THIS (positive or negative)

POINT_A = (0.0, 0.0)
POINT_B = (1.0, 0.0)

# ---------------------------------------------
# Movement functions
# ---------------------------------------------
def stop(bot):
    bot.set_car_motion(0, 0, 0)
    time.sleep(STOP_DELAY)

def rotate_to_angle(bot, target_angle):
    direction = 1 if target_angle > 0 else -1
    bot.set_car_motion(0, 0, direction * ANGULAR_SPEED)
    time.sleep(abs(target_angle) / ANGULAR_SPEED)
    stop(bot)

def move_straight(bot, distance_m):
    direction = 1 if distance_m > 0 else -1
    bot.set_car_motion(direction * LINEAR_SPEED, 0, 0)
    time.sleep(abs(distance_m) / LINEAR_SPEED)
    stop(bot)

def go_to_point(bot, x0, y0, xt, yt, extra_rotation_deg=0):
    dx = xt - x0
    dy = yt - y0
    angle = math.atan2(dy, dx)

    angle += math.radians(extra_rotation_deg)   # <── Manual override

    distance = math.sqrt(dx*dx + dy*dy)

    rotate_to_angle(bot, angle)
    move_straight(bot, distance)

# ---------------------------------------------
# Grab sequence
# ---------------------------------------------
def perform_grab_sequence(bot):
    print("Performing grab sequence...")
    bot.set_uart_servo_angle_array([90, 90, 0, 90, 90, 180])
    time.sleep(2)
    bot.set_uart_servo_angle_array([90, 47, 12, 90, 90, 140])
    time.sleep(2)
    bot.set_uart_servo_angle_array([90, 90, 0, 90, 90, 140])

# ---------------------------------------------
# Detection wait loop
# ---------------------------------------------
def wait_for_detection():
    global detected_class

    print(f"[INFO] Waiting for YOLO to detect: {TARGET_CLASS}")

    while running:
        if detected_class == TARGET_CLASS:
            print(f"[INFO] Target detected: {TARGET_CLASS}")
            return True

        if processed_frame is not None:
            cv2.imshow("YOLO Detection", processed_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return False

        time.sleep(0.01)

    return False

# ---------------------------------------------
# Main
# ---------------------------------------------
def main():
    global running

    robot.set_uart_servo_angle_array([90, 90, 0, 90, 90, 180])

    print("\n[INFO] Starting YOLO + Camera Threads...")
    threading.Thread(target=camera_thread, daemon=True).start()
    threading.Thread(target=yolo_thread, daemon=True).start()

    # Move forward to B
    go_to_point(robot, POINT_A[0], POINT_A[1], POINT_B[0], POINT_B[1])

    # Wait for object
    if wait_for_detection():
        perform_grab_sequence(robot)

        # Move BACK to A
        go_to_point(
            robot,
            POINT_B[0], POINT_B[1],
            POINT_A[0], POINT_A[1],
            extra_rotation_deg=RETURN_ROTATION_OFFSET
        )
    else:
        print("[WARN] Object not detected — aborting.")
        stop(robot)

    running = False
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
