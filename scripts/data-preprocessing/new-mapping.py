import os

# This function remaps class IDs in YOLO label files according to the new dataset
def remap_class_ids(label_dir, class_mapping):

    total_files_checked = 0
    total_files_modified = 0
    total_lines_changed = 0

    print(f"\nScanning label directory: {label_dir}")

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

        new_lines = []
        file_changed = False

        for line in lines:
            parts = line.split()
            if not parts:
                continue

            try:
                class_id = int(parts[0])
                if class_id in class_mapping:
                    new_class_id = class_mapping[class_id]
                    parts[0] = str(new_class_id)
                    file_changed = True
                    total_lines_changed += 1
                new_lines.append(" ".join(parts))
            except ValueError:
                print(f"Invalid format in {filename}: '{line}'")
                new_lines.append(line)

        # Save the updated label file if any changes were made
        if file_changed:
            try:
                with open(filepath, 'w') as f:
                    for line in new_lines:
                        f.write(line + '\n')
                total_files_modified += 1
            except Exception as e:
                print(f"Error writing to {filename}: {e}")

    print(f"\nClass ID remapping completed.")
    print(f"No of label files checked: {total_files_checked}")
    print(f"No of files modified: {total_files_modified}")
    print(f"Total lines changed: {total_lines_changed}")


remap_class_ids(
    label_dir="C:/Middlesex/HomeBuddy/dataset/shoes/test/labels",
    class_mapping={
        # old_id: new_id
        0: 5
    }
)
