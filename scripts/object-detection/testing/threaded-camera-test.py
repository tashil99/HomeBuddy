import cv2
import os
import time
import threading
from ultralytics import YOLO

MODEL_PATH = "C:/Middlesex/HomeBuddy/scripts/object-detection/training/runs/detect/object-detection-model-3/weights/best.pt"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

model = YOLO(MODEL_PATH)

# ------------------------------
# GLOBAL SHARED VARIABLES
# ------------------------------
latest_frame = None  # raw camera frame from thread
processed_frame = None  # YOLO output frame
running = True  # for clean thread shutdown
lock = threading.Lock()  # thread safety


# ------------------------------
# THREAD 1: CAMERA CAPTURE
# ------------------------------
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
        if not ret:
            continue

        with lock:
            latest_frame = frame.copy()  # keep ONLY the latest frame

    cap.release()


# ------------------------------
# THREAD 2: YOLO INFERENCE
# ------------------------------
def yolo_thread():
    global latest_frame, processed_frame, running

    class_colors = {
        'book': (0, 255, 0),
        'cup': (255, 0, 0),
        'glasses': (0, 0, 255),
        'keys': (255, 255, 0),
        'phone': (255, 0, 255),
        'shoes': (0, 255, 255)
    }

    while running:
        frame = None

        with lock:
            if latest_frame is not None:
                frame = latest_frame.copy()

        if frame is None:
            time.sleep(0.001)
            continue

        results = model.predict(
            source=frame,
            imgsz=640,
            conf=0.25,
            iou=0.55,
            device="cpu",
            verbose=False
        )

        boxes = results[0].boxes
        names = results[0].names

        # Draw boxes
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                name = names[cls]
                color = class_colors.get(name, (255, 255, 255))

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"{name}: {conf:.2f}"

                (tw, th), base = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw, y1), color, -1)
                cv2.putText(frame, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        frame = cv2.putText(frame, f"Detections: {len(boxes)}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        processed_frame = frame  # update YOLO frame


# ------------------------------
# MAIN: DISPLAY LOOP
# ------------------------------
def main():
    global running, processed_frame

    print("Starting camera + YOLO threads...")

    t1 = threading.Thread(target=camera_thread, daemon=True)
    t2 = threading.Thread(target=yolo_thread, daemon=True)

    t1.start()
    t2.start()

    while True:
        if processed_frame is not None:
            cv2.imshow("YOLO Live Detection (Threaded)", processed_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            running = False
            break

        if key == ord('s') and processed_frame is not None:
            filename = f"det_{int(time.time())}.jpg"
            cv2.imwrite(filename, processed_frame)
            print(f"Saved: {filename}")

    cv2.destroyAllWindows()
    print("Stopping threads...")


if _name_ == "_main_":
    main()