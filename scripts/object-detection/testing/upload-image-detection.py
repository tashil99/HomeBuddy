import os
import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import filedialog

MODEL_PATH = "C:/Middlesex/HomeBuddy/scripts/object-detection/training/runs/detect/object-detection-model-2/weights/best.pt"
SAVE_DIR = "C:/Middlesex/HomeBuddy/scripts/object-detection/testing"

# --- Check model exists ---
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at: {MODEL_PATH}")

# --- Load YOLO model ---
model = YOLO(MODEL_PATH)

# --- File upload dialog ---
root = tk.Tk()
root.withdraw()
image_path = filedialog.askopenfilename(
    title="Select an image",
    filetypes=[("Image files", "*.jpg *.jpeg *.png")]
)

if image_path and os.path.exists(image_path):
    print(f"✅ Selected image: {image_path}")

    # --- Run inference ---
    results = model.predict(
        source=image_path,
        imgsz=640,
        conf=0.25,
        save=True,
        save_dir=SAVE_DIR,
        device="cpu"
    )

    # --- Load original image ---
    img = cv2.imread(image_path)

    # --- Draw bounding boxes and confidence on the image ---
    for box in results[0].boxes:  # iterate over detections
        x1, y1, x2, y2 = map(int, box.xyxy[0])  # bounding box coordinates
        conf = float(box.conf[0])  # confidence
        cls = int(box.cls[0])      # class index
        label = f"{results[0].names[cls]}: {conf:.2f}"
        print("The image you have inserted contains a " + label)

        # Draw rectangle
        cv2.rectangle(img, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=2)
        # Draw label background
        (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (x1, y1 - 20), (x1 + text_width, y1), (0, 255, 0), -1)
        # Draw text
        cv2.putText(img, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

    # --- Display image with bounding boxes ---
    cv2.imshow("Prediction", img)

    print(f"Results saved to: {results[0].path}")
    print("Press any key to close the image window...")


    cv2.waitKey(0)
    cv2.destroyAllWindows()

else:
    print("No image selected or file does not exist.")
