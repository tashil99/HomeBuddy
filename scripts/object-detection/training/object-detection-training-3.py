import os
import pickle
from ultralytics import YOLO

def main():
    # Avoid OpenMP duplicate runtime crash
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

    # CPU-specific performance tweaks
    os.environ["OMP_NUM_THREADS"] = "4"  # limit CPU threading
    os.environ["MKL_NUM_THREADS"] = "4"  # limit MKL (PyTorch backend)
    os.environ["ULTRALYTICS_CACHE"] = "ram"  # speed up by caching to RAM

    # Load lightweight YOLOv8 model
    model = YOLO("runs/detect/object-detection-model-2/weights/best.pt")

    # Train (GPU-optimized config)
    results = model.train(
        data="../dataset/data.yaml",
        epochs=40,
        imgsz=640,
        batch=16,
        name="object-detection-model-3",
        verbose=True,
        optimizer="AdamW",
        lr0=0.0002,
        mosaic=1.0,
        augment=True,
    )

    # Save results
    results_dir = "runs/detect/object-detection-model-3"
    os.makedirs(results_dir, exist_ok=True)
    results_path = os.path.join(results_dir, "results.pkl")
    with open(results_path, "wb") as f:
        pickle.dump(results, f)

    print(f"\nTraining completed! Results saved to: {results_path}")
    print(f"Plots, labels, and checkpoints are in '{results_dir}'")

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()