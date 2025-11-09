import os
from collections import Counter

def count_class_ids(label_root, num_classes=6):

    file_count_per_class = Counter()

    for dirpath, _, files in os.walk(label_root):
        for file in files:
            if not file.endswith(".txt"):
                continue

            label_path = os.path.join(dirpath, file)
            try:
                with open(label_path, "r") as f:
                    lines = f.readlines()
            except:
                continue

            ids_in_file = set()

            for line in lines:
                parts = line.strip().split()
                if not parts:
                    continue

                try:
                    cls_id = int(parts[0])
                    if 0 <= cls_id < num_classes:
                        ids_in_file.add(cls_id)
                except ValueError:
                    continue

            for cls_id in ids_in_file:
                file_count_per_class[cls_id] += 1

    print("\nFile count per class ID:")
    for cls_id in range(num_classes):
        print(f"Class {cls_id}: {file_count_per_class[cls_id]} files")

# Example usage
LABELS_DIR = "C:/Middlesex/HomeBuddy/merged-dataset"
count_class_ids(LABELS_DIR, num_classes=6)
