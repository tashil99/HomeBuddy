import cv2
import os
from ultralytics import YOLO
import time
import threading, cv2

MODEL_PATH = "C:/Middlesex/HomeBuddy/scripts/object-detection/training/runs/detect/object-detection-model-3/weights/best.pt"

# --- Check model exists ---
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")

# --- Load YOLO model ---
model = YOLO(MODEL_PATH)

def yolo_live_camera_detection():
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    print("Live camera testing started!")
    print("Press 'q' to quit, 's' to save screenshot")

    # Color mapping for your classes
    class_colors = {
        'book': (0, 255, 0),  # Green
        'cup': (255, 0, 0),  # Blue
        'glasses': (0, 0, 255),  # Red
        'keys': (255, 255, 0),  # Cyan
        'phone': (255, 0, 255),  # Magenta
        'shoes': (0, 255, 255)  # Yellow
    }

    while True:
        # Read frame from camera
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break

        results = model.predict(
            source=frame,
            imgsz=640,  # higher resolution = more accurate detections
            conf=0.25,  # detect even low-confidence objects
            iou=0.55,  # avoid duplicate overlapping boxes
            device="cpu",
            verbose=False
        )

        # Get detections
        boxes = results[0].boxes

        # Draw bounding boxes and labels
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # bounding box
                conf = float(box.conf[0])  # confidence
                cls = int(box.cls[0])  # class index
                class_name = results[0].names[cls]  # class name

                # Get color for this class
                color = class_colors.get(class_name, (255, 255, 255))  # default white

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                # Create label
                label = f"{class_name}: {conf:.2f}"

                # Draw label background
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                cv2.rectangle(frame, (x1, y1 - text_height - 10),
                              (x1 + text_width, y1), color, -1)

                # Draw label text
                cv2.putText(frame, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # Display detection info
        detection_count = len(boxes) if boxes is not None else 0
        cv2.putText(frame, f"Detections: {detection_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Show frame
        cv2.imshow('YOLO Live Detection - Office Objects', frame)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            # Save screenshot
            timestamp = int(time.time())
            cv2.imwrite(f'office_detection_{timestamp}.jpg', frame)
            print(f"Screenshot saved as office_detection_{timestamp}.jpg")

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Live detection stopped.")


# Running live camera detection
if __name__ == "__main__":
    yolo_live_camera_detection()