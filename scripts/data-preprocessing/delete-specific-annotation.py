import os

def delete_specific_class(label_dir, target_class_id):
    """
    Deletes all lines from YOLO label files where the class ID equals `target_class_id`.
    """
    total_files_checked = 0
    total_files_modified = 0
    total_lines_deleted = 0

    print(f"\nScanning label directory: {label_dir}")
    print(f"Target class ID to delete: {target_class_id}\n")

    # Iterate through each label file
    for filename in os.listdir(label_dir):
        if not filename.endswith(".txt"):
            continue

        total_files_checked += 1
        filepath = os.path.join(label_dir, filename)

        try:
            with open(filepath, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            print(f"⚠️ Error reading {filename}: {e}")
            continue

        new_lines = []
        lines_deleted = 0

        for line in lines:
            parts = line.split()
            if not parts:
                continue

            try:
                class_id = int(parts[0])
                if class_id == target_class_id:
                    lines_deleted += 1
                else:
                    new_lines.append(line)
            except ValueError:
                # keep malformed lines
                new_lines.append(line)

        # If any lines were deleted, overwrite the file
        if lines_deleted > 0:
            try:
                with open(filepath, 'w') as f:
                    for line in new_lines:
                        f.write(line + '\n')
                total_files_modified += 1
                total_lines_deleted += lines_deleted
            except Exception as e:
                print(f"Error writing to {filename}: {e}")

    # Summary
    print("\nDeletion Summary")
    print(f"Total label files checked: {total_files_checked}")
    print(f"Files modified: {total_files_modified}")
    print(f"Total lines deleted: {total_lines_deleted}")

    if total_lines_deleted > 0:
        print(f"All lines with class ID '{target_class_id}' have been removed.")
    else:
        print(f"No lines found with class ID '{target_class_id}'. Nothing deleted.")


# Example usage
if __name__ == "__main__":
    delete_specific_class(
        label_dir="C:/Middlesex/HomeBuddy/dataset/phone/valid/labels",
        target_class_id=0
    )
