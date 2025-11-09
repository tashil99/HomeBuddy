import os
from collections import defaultdict

def find_duplicate_filenames(root_folder):

    filenames = defaultdict(list)
    duplicates = []

    print(f"Scanning for duplicate filenames in '{root_folder}'...")

    for dirpath, _, file_list in os.walk(root_folder):
        for filename in file_list:
            filenames[filename].append(os.path.join(dirpath, filename))

    for filename, paths in filenames.items():
        if len(paths) > 1:
            duplicates.append(paths)

    if not duplicates:
        print("No duplicate filenames found.")
    else:
        print("Found the following sets of duplicate filenames:")
        for i, path_list in enumerate(duplicates, 1):
            print(f"\nSet {i} (Filename: '{os.path.basename(path_list[0])}'):")
            for filepath in path_list:
                print(f"  - {filepath}")


DATASET_DIR = "C:/Middlesex/HomeBuddy/merged-dataset"

find_duplicate_filenames(DATASET_DIR)
