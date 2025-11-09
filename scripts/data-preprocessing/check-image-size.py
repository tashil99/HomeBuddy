import os
from PIL import Image

# This function checks image sizes and deletes large/very large images and their labels
def check_and_clean_large_images(image_dir, label_dir, target_width=640, target_height=640, min_size=820):

    sizes = []
    total_files_checked = 0

    for file in os.listdir(image_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            total_files_checked += 1
            image_path = os.path.join(image_dir, file)
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
                    sizes.append((width, height, file))
            except Exception as e:
                print(f"Error reading {file}: {e}")

    print(f"\nTotal image files checked: {total_files_checked}")

    if not sizes:
        print("No images found.")
        return

    target_size_images = [s for s in sizes if s[0] == target_width and s[1] == target_height]
    perfect_range_images = [s for s in sizes if 416 <= s[0] <= 640 and 416 <= s[1] <= 640]
    large_images = [s for s in sizes if s[0] > min_size or s[1] > min_size]
    very_large_images = [s for s in sizes if s[0] > 4000 or s[1] > 4000]

    print(f"Target size ({target_width}x{target_height}): {len(target_size_images)}")
    print(f"Perfect range (416–640px): {len(perfect_range_images)}")
    print(f"Large images (>{min_size}px): {len(large_images)}")
    print(f"Very large images (>4000px): {len(very_large_images)}")

    if not large_images:
        print("\nAll image sizes are within acceptable range.")
        return


    print("\nLarge images found!")
    for width, height, filename in large_images[:20]:
        category = "VERY LARGE" if (width > 4000 or height > 4000) else "LARGE"
        print(f" - [{category}] {filename}: {width}x{height}")

    if len(large_images) > 20:
        print(f"  ...and {len(large_images) - 20} more.")

    choice = input(f"\nDo you want to delete these {len(large_images)} large images AND their labels? (y/n): ").strip().lower()

    if choice != 'y':
        print("\nNo files were deleted.")
        return

    deleted_images = 0
    deleted_labels = 0

    print("\n🗑 Deleting files...\n")

    for width, height, filename in large_images:
        img_path = os.path.join(image_dir, filename)
        label_path = os.path.join(label_dir, os.path.splitext(filename)[0] + ".txt")

        # Delete image
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
                deleted_images += 1
                print(f"Deleted image: {img_path}")
            except Exception as e:
                print(f"Error deleting image {filename}: {e}")

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


check_and_clean_large_images(
    image_dir="C:/Middlesex/HomeBuddy/merged-dataset/valid/images",
    label_dir="C:/Middlesex/HomeBuddy/merged-dataset/valid/labels"
)
