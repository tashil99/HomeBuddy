import os

# This function verifies that all YOLO label files contain only the expected class ID
def check_class_ids(label_dirs, expected_id):
    total_files_checked = 0
    total_files_mismatched = 0
    mismatched_files = []

    print(f"\nVerifying that all class IDs equal '{expected_id}'...\n")

    for label_dir in label_dirs:
        if not os.path.isdir(label_dir):
            print(f"Warning: Directory not found, skipping: {label_dir}")
            continue

        print(f"Checking directory: {label_dir}")

        for filename in os.listdir(label_dir):
            if not filename.endswith(".txt"):
                continue

            total_files_checked += 1
            filepath = os.path.join(label_dir, filename)

            try:
                with open(filepath, 'r') as f:
                    lines = [line.strip() for line in f.readlines() if line.strip()]
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue

            for i, line in enumerate(lines, start=1):
                parts = line.split()
                if not parts:
                    continue

                try:
                    class_id = int(parts[0])
                    if class_id != expected_id:
                        mismatched_files.append((filepath, i, class_id))
                        total_files_mismatched += 1
                except ValueError:
                    print(f"Invalid format in {filename} on line {i}")

    print(f"Total label files checked: {total_files_checked}")

    if mismatched_files:
        print(f"{total_files_mismatched} mismatched class IDs")
        for file, line_num, found_id in mismatched_files:
            print(f"File: {file}, Line: {line_num}, Found ID: {found_id} (Expected: {expected_id})")
    else:
        print(f"Verification successful! All files contain only class ID '{expected_id}'.")


check_class_ids(
    label_dirs=[
        "C:/Middlesex/HomeBuddy/dataset/shoes/train/labels"
    ],
    expected_id=5
)
