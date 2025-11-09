import os
import cv2

# This function checks if there is any corrupted file in a specific directory.
# If corrupted file is found, user confirmation is required for deletion.
def check_and_clean_dataset(image_dir, label_dir=None):
    corrupted_files = []
    total_files = 0

    for root, _, files in os.walk(image_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                total_files += 1
                img_path = os.path.join(root, file)
                img = cv2.imread(img_path)

                if img is None:
                    corrupted_files.append(img_path)

    print(f"\nTotal image files checked: {total_files}")

    if not corrupted_files:
        print("All images are readable.")
        return

    print(f"\n{len(corrupted_files)} corrupted or unreadable images found:-\n")
    for f in corrupted_files:
        print(f" - {f}")

    # Ask before deleting corrupted files
    choice = input("\nDo you want to delete these corrupted files and their corresponding labels? (y/n): ").strip().lower()

    if choice == 'y':
        deleted_count = 0
        for img_path in corrupted_files:
            try:
                os.remove(img_path)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {img_path}: {e}")

            if label_dir:
                rel_path = os.path.relpath(img_path, image_dir)
                base_name = os.path.splitext(rel_path)[0] + ".txt"
                label_path = os.path.join(label_dir, base_name)

                if os.path.exists(label_path):
                    try:
                        os.remove(label_path)
                        print(f"Deleted label: {label_path}")
                    except Exception as e:
                        print(f"Error deleting label {label_path}: {e}")

        print(f"\n{deleted_count} corrupted images and their labels deleted..")
    else:
        print("\nNo files were deleted.")

check_and_clean_dataset(
    image_dir="C:/Middlesex/HomeBuddy/merged-dataset/test/images",
    label_dir="C:/Middlesex/HomeBuddy/merged-dataset/test/labels"
)
