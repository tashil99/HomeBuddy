import os

# This function checks if all images have their corresponding label files
def check_labels(image_dir, label_dir):
    missing_labels = []
    for file in os.listdir(image_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            label_file = os.path.splitext(file)[0] + ".txt"
            if not os.path.exists(os.path.join(label_dir, label_file)):
                missing_labels.append(file)

    if missing_labels:
        print(f"No of image files with missing labels: {len(missing_labels)}")
        for m in missing_labels:
            print(m)
    else:
        print("All images have their label files..")


check_labels("../dataset/test/images", "../dataset/test/labels")