import os

# This function checks if all images have their corresponding label files.
# Image files without label files will be asked for deletion.
def check_and_clean_labels(image_dir, label_dir):
    missing_labels = []
    total_files = 0
    label_files = 0

    for file in os.listdir(image_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            total_files += 1
            label_file = os.path.splitext(file)[0] + ".txt"
            label_files += 1

            label_path = os.path.join(label_dir, label_file)
            if not os.path.exists(label_path):
                missing_labels.append(file)

    print(f"\nTotal image files checked: {total_files}")
    print(f"Total label files expected: {label_files}")

    if not missing_labels:
        print("\nAll images have their label files..")
        return

    print(f"\n{len(missing_labels)} image files are missing labels!\n")
    for m in missing_labels:
        print(m)

    # Ask user before deleting missing label images
    choice = input("\nDo you want to delete these images with missing labels? (y/n): ").strip().lower()

    if choice == 'y':
        deleted_count = 0
        for img_file in missing_labels:
            img_path = os.path.join(image_dir, img_file)

            try:
                os.remove(img_path)
                deleted_count += 1
                print(f"Deleted image: {img_path}")
            except Exception as e:
                print(f"Error deleting {img_path}: {e}")

        print(f"\n{deleted_count} images without labels have been deleted.")
    else:
        print("\nNo files were deleted.")


check_and_clean_labels(
    image_dir="C:/Middlesex/HomeBuddy/merged-dataset/test/images",
    label_dir="C:/Middlesex/HomeBuddy/merged-dataset/test/labels"
)
