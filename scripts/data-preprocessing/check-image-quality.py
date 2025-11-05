import os
import cv2
import numpy as np
from typing import Dict, List, Tuple


def check_image_quality(
    image_dir: str,
    min_size: Tuple[int, int] = (64, 64),
    max_aspect_ratio: float = 5.0,
    low_variance_thresh: float = 3.0,
    valid_ext: Tuple[str, ...] = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"),
) -> Dict[str, List[str]]:

    issues: Dict[str, List[str]] = {
        "unreadable": [],
        "zero_size": [],
        "too_small": [],
        "extreme_aspect": [],
        "low_variance": [],
    }

    min_w, min_h = min_size

    for root, _, files in os.walk(image_dir):
        for fname in files:
            if not fname.lower().endswith(valid_ext):
                continue
            path = os.path.join(root, fname)

            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is None:
                issues["unreadable"].append(path)
                continue

            h, w = img.shape[:2]
            if w == 0 or h == 0:
                issues["zero_size"].append(path)
                continue

            if w < min_w or h < min_h:
                issues["too_small"].append(f"{path} ({w}x{h})")

            ar = max(w / h, h / w)
            if ar > max_aspect_ratio:
                issues["extreme_aspect"].append(f"{path} (AR={ar:.2f}, {w}x{h})")

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            var = float(np.var(gray))
            if var < low_variance_thresh:
                issues["low_variance"].append(f"{path} (var={var:.2f})")

    return issues


def print_quality_report(issues: Dict[str, List[str]]) -> None:
    any_issues = any(issues.values())
    if not any_issues:
        print("No image quality issues found")
        return

    for key in ["unreadable", "zero_size", "too_small", "extreme_aspect", "low_variance"]:
        entries = issues.get(key, [])
        if entries:
            title = key.replace("_", " ").title()
            print(f"{title} ({len(entries)}):")
            for e in entries:
                print(e)


def remove_low_quality_images(
    issues: Dict[str, List[str]],
    issue_types_to_remove: List[str] = None,
    label_dir: str = None,
) -> None:

    if issue_types_to_remove is None:
        issue_types_to_remove = list(issues.keys())

    files_to_delete = []
    for issue_type in issue_types_to_remove:
        if issue_type in issues:
            for entry in issues[issue_type]:
                # Extract just the path (entries may have extra info like "(640x480)")
                path = entry.split(" (")[0]
                files_to_delete.append((path, issue_type))

    if not files_to_delete:
        print("No files to delete.")
        return

    print(f"\n{'='*70}")
    print(f"{len(files_to_delete)} images with quality issues found!")
    print(f"{'='*70}\n")

    # Prepare all file pairs
    all_pairs = []
    for img_path, issue_type in files_to_delete:
        # Find corresponding label file
        if label_dir:
            img_basename = os.path.basename(img_path)
            label_name = os.path.splitext(img_basename)[0] + ".txt"
            label_path = os.path.join(label_dir, label_name)
        else:
            img_dir = os.path.dirname(img_path)
            label_dir_auto = img_dir.replace("/images", "/labels").replace("\\images", "\\labels")
            img_basename = os.path.basename(img_path)
            label_name = os.path.splitext(img_basename)[0] + ".txt"
            label_path = os.path.join(label_dir_auto, label_name)

        all_pairs.append((img_path, label_path, issue_type))

    # Display all files
    for idx, (img_path, label_path, issue_type) in enumerate(all_pairs, 1):
        print(f"{idx}. Issue: {issue_type}")
        print(f"   Image: {img_path}")
        if os.path.exists(label_path):
            print(f"   Label: {label_path}")
        else:
            print(f"   Label: {label_path} (not found)")
        print()

    # Ask for confirmation once
    print(f"{'='*70}")
    response = input(f"Delete all {len(files_to_delete)} images and their labels? (y/yes/n/no): ").strip().lower()

    if response not in ['y', 'yes']:
        print("\nDeletion cancelled!")
        return

    deleted_images = 0
    deleted_labels = 0

    print(f"\n{'='*70}")
    print("Deleting files...")
    print(f"{'='*70}\n")

    for img_path, label_path, _ in all_pairs:
        # Delete image
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
                deleted_images += 1
                print(f"Deleted: {img_path}")
            except Exception as e:
                print(f"Error deleting {img_path}: {e}")

        # Delete label
        if os.path.exists(label_path):
            try:
                os.remove(label_path)
                deleted_labels += 1
                print(f"Deleted: {label_path}")
            except Exception as e:
                print(f"Error deleting {label_path}: {e}")

    # Summary
    print("****SUMMARY****")
    print(f"Total images deleted: {deleted_images}")
    print(f"Total labels deleted: {deleted_labels}")


if __name__ == "__main__":
    # Path of directory to check
    target_dir = "../dataset/laptop/train/images"
    results = check_image_quality(
        target_dir,
        min_size=(400, 400),
        max_aspect_ratio=6.0,
        low_variance_thresh=2.0,
    )
    print_quality_report(results)

    remove_low_quality_images(
        results,
        issue_types_to_remove=["too_small"],
    )