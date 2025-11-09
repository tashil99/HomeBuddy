import os

# This function validates YOLO annotations
# If issues found, user confirmation is required for deletion
def validate_and_clean_annotations(label_dir, image_dir, num_classes=1):

    errors = []
    empty_files = []
    total_files_checked = 0
    total_annotations = 0

    for file in os.listdir(label_dir):
        if file.lower().endswith('.txt'):
            total_files_checked += 1
            label_path = os.path.join(label_dir, file)

            try:
                with open(label_path, 'r') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]

                if not lines:
                    empty_files.append(label_path)
                    continue

                for line_num, line in enumerate(lines, 1):
                    parts = line.split()
                    if len(parts) != 5:
                        errors.append(label_path)
                        break

                    try:
                        class_id = int(parts[0])
                        cx, cy, w, h = map(float, parts[1:])
                        total_annotations += 1

                        if not (0 <= class_id < num_classes):
                            errors.append(label_path)
                            break

                        if not (0 < w <= 1 and 0 < h <= 1 and 0 <= cx <= 1 and 0 <= cy <= 1):
                            errors.append(label_path)
                            break

                        if (cx - w / 2 < 0 or cx + w / 2 > 1 or cy - h / 2 < 0 or cy + h / 2 > 1):
                            errors.append(label_path)
                            break

                    except ValueError:
                        errors.append(label_path)
                        break

            except Exception as e:
                print(f"Error reading {label_path}: {e}")

    errors = list(set(errors))
    empty_files = list(set(empty_files))

    print(f"\nChecked {total_files_checked} label files with {total_annotations} total annotations.")
    print(f"{len(errors)} files have annotation errors.")
    print(f"{len(empty_files)} files are empty.\n")

    files_to_delete = errors + empty_files
    if not files_to_delete:
        print("All annotations are valid! Nothing to be deleted..")
        return

    # Ask before deleting
    confirm = input(f"Do you want to delete these {len(files_to_delete)} invalid/empty label files AND their images? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Deletion cancelled. No files were removed.")
        return

    deleted_labels = 0
    deleted_images = 0
    missing_images = []

    for label_path in files_to_delete:
        if not os.path.exists(label_path):
            continue

        try:
            os.remove(label_path)
            deleted_labels += 1
        except Exception as e:
            print(f"Error deleting label {label_path}: {e}")

        base_name = os.path.splitext(os.path.basename(label_path))[0]
        found_image = False
        for ext in [".jpg", ".jpeg", ".png"]:
            image_path = os.path.join(image_dir, base_name + ext)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    deleted_images += 1
                    found_image = True
                    break
                except Exception as e:
                    print(f"Error deleting image {image_path}: {e}")

        if not found_image:
            missing_images.append(base_name)

    print(f"\nDeleted {deleted_labels} label files and {deleted_images} images.")
    if missing_images:
        print("These labels had no matching images:")
        for name in missing_images:
            print(f"  - {name}")


validate_and_clean_annotations(
    image_dir="C:/Middlesex/HomeBuddy/dataset/shoes/test/images",
    label_dir="C:/Middlesex/HomeBuddy/dataset/shoes/test/labels",
    num_classes=1
)
