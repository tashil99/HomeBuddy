import os
import cv2
import numpy as np
from typing import Tuple

# This function checks image pixel ranges and deletes invalid images and their labels
def check_and_clean_pixel_range(image_dir, label_dir, valid_ext: Tuple[str, ...] = (".jpg", ".jpeg", ".png")):

    valid_range = []
    invalid_range = []
    unreadable = []
    total_files_checked = 0

    for root, _, files in os.walk(image_dir):
        for filename in files:
            if not filename.lower().endswith(valid_ext):
                continue
            total_files_checked += 1
            path = os.path.join(root, filename)
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is None:
                unreadable.append(path)
                continue

            min_val = float(np.min(img))
            max_val = float(np.max(img))

            if img.dtype == np.uint8 and 0 <= min_val <= 255 and 0 <= max_val <= 255:
                valid_range.append(f"{path} (range=[{min_val:.0f}, {max_val:.0f}])")
            else:
                invalid_range.append(f"{path} (range=[{min_val:.4f}, {max_val:.4f}], dtype={img.dtype})")

    print(f"\nTotal image files checked: {total_files_checked}\n")

    # --- Report ---
    if valid_range:
        print(f"{len(valid_range)} valid range images found..")
    if invalid_range:
        print(f"{len(invalid_range)} unexpected range images found..")
        for e in invalid_range:
            print(f" - {e}")
    if unreadable:
        print(f"Unreadable ({len(unreadable)} images):")
        for e in unreadable:
            print(f" - {e}")
    if not invalid_range and not unreadable:
        print("All images are in standard [0, 255] uint8 range")

    # --- Ask user for deletion ---
    files_to_delete = invalid_range + unreadable
    if not files_to_delete:
        return

    choice = input(f"\nDo you want to delete these {len(files_to_delete)} invalid images and their labels? (y/n): ").strip().lower()
    if choice != 'y':
        print("\nNo files were deleted!")
        return

    deleted_images = 0
    deleted_labels = 0

    print("\nDeleting files...\n")

    for entry in files_to_delete:
        # Extract the path (entry may include extra info like ranges)
        img_path = entry.split(" (")[0]
        label_path = os.path.join(label_dir, os.path.splitext(os.path.basename(img_path))[0] + ".txt")

        # Delete image
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
                deleted_images += 1
                print(f"Deleted image: {img_path}")
            except Exception as e:
                print(f"Error deleting image {img_path}: {e}")

        # Delete corresponding label if exists
        if os.path.exists(label_path):
            try:
                os.remove(label_path)
                deleted_labels += 1
                print(f"Deleted label: {label_path}")
            except Exception as e:
                print(f"Error deleting label {label_path}: {e}")

    print("\n**** SUMMARY ****")
    print(f"Total images deleted: {deleted_images}")
    print(f"Total labels deleted: {deleted_labels}")


check_and_clean_pixel_range(
    image_dir="C:/Middlesex/HomeBuddy/merged-dataset/test/images",
    label_dir="C:/Middlesex/HomeBuddy/merged-dataset/test/labels"
)
