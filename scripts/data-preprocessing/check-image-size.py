import os
from PIL import Image

def delete_large_images(image_dir, sizes, min_size=820):

    large_images = [s for s in sizes if s[0] > min_size or s[1] > min_size]
    very_large_images = [s for s in sizes if s[0] > 4000 or s[1] > 4000]

    if not large_images:
        print("\nNo large images to delete")
        return

    print(f"\n{len(large_images)} large images (>{min_size}px) found!")
    if very_large_images:
        print(f"Including {len(very_large_images)} very large images (>4000px)")

    # Determine label directory
    label_dir = image_dir.replace("/images", "/labels").replace("\\images", "\\labels")

    # Show the images that would be deleted
    print("\nImages and labels that will be deleted:")
    for width, height, filename in large_images[:20]:
        category = "VERY LARGE" if (width > 4000 or height > 4000) else "LARGE"
        label_name = os.path.splitext(filename)[0] + ".txt"
        label_path = os.path.join(label_dir, label_name)
        label_exists = "✓" if os.path.exists(label_path) else "✗"
        print(f"  [{category}] {filename}: {width}x{height} [Label: {label_exists}]")

    if len(large_images) > 20:
        print(f"  ... and {len(large_images) - 20} more")

    # Ask for confirmation
    print(f"\nDo you want to delete these {len(large_images)} large images and their labels?")
    response = input("Type 'yes' to confirm deletion, or anything else to cancel: ").strip().lower()

    if response == 'yes':
        deleted_images = 0
        deleted_labels = 0
        failed_images = 0
        failed_labels = 0

        for width, height, filename in large_images:
            image_path = os.path.join(image_dir, filename)
            label_name = os.path.splitext(filename)[0] + ".txt"
            label_path = os.path.join(label_dir, label_name)

            # Delete image
            try:
                os.remove(image_path)
                deleted_images += 1
                print(f"Deleted image: {filename}")
            except Exception as e:
                failed_images += 1
                print(f"Failed to delete image {filename}: {e}")

            # Delete corresponding label if it exists
            if os.path.exists(label_path):
                try:
                    os.remove(label_path)
                    deleted_labels += 1
                    print(f"Deleted label: {label_name}")
                except Exception as e:
                    failed_labels += 1
                    print(f"Failed to delete label {label_name}: {e}")

        print(f"\nDeletion Summary:")
        print(f"Successfully deleted: {deleted_images} images, {deleted_labels} labels")
        if failed_images > 0 or failed_labels > 0:
            print(f"Failed to delete: {failed_images} images, {failed_labels} labels")
        print(f"Remaining images: {len(sizes) - deleted_images}")
    else:
        print("\nDeletion cancelled")


def check_image_sizes(image_dir, target_width=640, target_height=640, ask_delete=False):

    sizes = []

    for file in os.listdir(image_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_path = os.path.join(image_dir, file)
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
                    sizes.append((width, height, file))
            except Exception as e:
                print(f"Error reading {file}: {e}")

    if not sizes:
        print("No images found")
        return

    # Check for target size
    target_size_images = [s for s in sizes if s[0] == target_width and s[1] == target_height]
    non_target_size_images = [s for s in sizes if s[0] != target_width or s[1] != target_height]

    # Check for perfect range (416x416 to 640x640)
    perfect_range_images = [s for s in sizes if 416 <= s[0] <= 640 and 416 <= s[1] <= 640]

    print(f"\nTarget Size Check ({target_width}x{target_height}):")
    print(f"Total images: {len(sizes)}")
    print(f"Matching target size: {len(target_size_images)} ({len(target_size_images) / len(sizes) * 100:.1f}%)")
    print(f"Perfect range (416-640): {len(perfect_range_images)} ({len(perfect_range_images) / len(sizes) * 100:.1f}%)")
    print(f"Not matching: {len(non_target_size_images)} ({len(non_target_size_images) / len(sizes) * 100:.1f}%)")

    if len(target_size_images) == len(sizes):
        print(f"\nAll images are {target_width}x{target_height}!")
    elif len(target_size_images) > 0:
        print(f"\nSome images match {target_width}x{target_height}")
    else:
        print(f"\nNo images are {target_width}x{target_height}")

    # Show non-matching images
    if non_target_size_images and len(non_target_size_images) <= 20:
        print(f"\nImages with different sizes:")
        for width, height, filename in non_target_size_images:
            print(f"  {filename}: {width}x{height}")

    # Show size categories
    small = sum(1 for w, h, _ in sizes if w < 416 or h < 416)
    medium = sum(1 for w, h, _ in sizes if 640 <= w <= 820 and 640 <= h <= 820)
    large = sum(1 for w, h, _ in sizes if w > 820 or h > 820)
    very_large = sum(1 for w, h, _ in sizes if w > 1920 or h > 1920)

    print(f"\nSize Categories:")
    print(f"  Small (<416px): {small}")
    print(f"  Medium (640-1920px): {medium}")
    print(f"  Large (1920-4000px): {large}")
    print(f"  Very Large (>4000px): {very_large}")

    if very_large > len(sizes) * 0.5:
        print(f"\nWarning: {very_large} very large images found - consider resizing")
    elif large > len(sizes) * 0.5:
        print(f"\nInfo: Many large images - resizing may improve training speed")
    else:
        print(f"\n Image sizes look reasonable for YOLO training")

    # Ask to delete large images
    if ask_delete and (large > 0 or very_large > 0):
        delete_large_images(image_dir, sizes)


check_image_sizes("../dataset/laptop/train/images", ask_delete=True)