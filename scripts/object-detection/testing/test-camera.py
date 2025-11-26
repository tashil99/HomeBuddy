import cv2
import os
import time
from ultralytics import YOLO


# ------------------------------
# Load Your Custom YOLO Model
# ------------------------------
MODEL_PATH = "/home/pi/Desktop/HomeBuddy/scripts/object-detection/training/runs/detect/object-detection-model-3/weights/best.pt"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")

# Load model
model = YOLO(MODEL_PATH)


# ------------------------------
# Live Camera Detection Function
# ------------------------------
def yolo_live_camera_detection():

    # --- Choose the camera index ---
    # Try video0 first, else fallback
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("❌ Error: Could not open ANY camera (0 or 1)")
        return

    print("YOLO Live Camera Detection Started!")
    print("Press 'q' to quit, 's' to save a screenshot\n")

    # Class → color mapping
    class_colors = {
        'book': (0, 255, 0),
        'cup': (255, 0, 0),
        'glasses': (0, 0, 255),
        'keys': (255, 255, 0),
        'phone': (255, 0, 255),
        'shoes': (0, 255, 255)
    }

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠ Warning: Could not read frame")
            break

        # ---------------------------------
        # Run YOLO — IMPORTANT: use model()
        # ---------------------------------
        results = model(
            frame,
            imgsz=640,
            conf=0.25,
            iou=0.55,
            device="cpu",
            verbose=False
        )

        boxes = results[0].boxes

        # ---------------------------------
        # Draw detections
        # ---------------------------------
        if boxes is not None and len(boxes) > 0:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])

                # Correct class name access for UI 8.0.227
                class_name = model.model.names[cls_id]

                # Pick assigned color or default
                color = class_colors.get(class_name, (255, 255, 255))

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                label = f"{class_name}: {conf:.2f}"

                cv2.putText(frame, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        detection_count = len(boxes) if boxes is not None else 0

        cv2.putText(frame, f"Detections: {detection_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Display window
        cv2.imshow("YOLO Live Detection", frame)

        # Keyboard controls
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        elif key == ord('s'):
            timestamp = int(time.time())
            fname = f"detect_{timestamp}.jpg"
            cv2.imwrite(fname, frame)
            print(f"📸 Saved screenshot: {fname}")

    cap.release()
    cv2.destroyAllWindows()
    print("✅ Live detection stopped.")


# ------------------------------
# Entry Point
# ------------------------------
if __name__ == "__main__":
    yolo_live_camera_detection()
