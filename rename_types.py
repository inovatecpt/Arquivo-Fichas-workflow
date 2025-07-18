import os
import argparse
import re

def get_file_number(filename):
    """Extract the numeric part of the filename (e.g., 0001 from 0001.jpg)."""
    match = re.match(r"(\d+)\.jpg$", filename, re.IGNORECASE)
    return int(match.group(1)) if match else None

def rename_files(main_dir, mode):
    for root, dirs, files in os.walk(main_dir):
        folder_name = os.path.basename(root)
        jpg_files = sorted([f for f in files if f.lower().endswith('.jpg')])

        if mode == "all-f":
            for filename in jpg_files:
                number = get_file_number(filename)
                if number is None:
                    print(f"Skipping file without valid numeric name: {filename}")
                    continue

                new_name = f"{folder_name}_{str(number).zfill(4)}_f.jpg"
                old_path = os.path.join(root, filename)
                new_path = os.path.join(root, new_name)

                if old_path != new_path:
                    os.rename(old_path, new_path)
                    print(f"Renamed: {old_path} -> {new_path}")
                else:
                    print(f"Already correct: {old_path}")

        else:
            # Group images in pairs
            for i in range(0, len(jpg_files), 2):
                pair_number = (i // 2) + 1
                pair_number_str = str(pair_number).zfill(4)

                for j, suffix in enumerate(["_f", "_b"] if mode == "f-and-b" else ["_f", "_a"]):
                    if i + j >= len(jpg_files):
                        break  # Odd number of files, skip last unmatched one

                    filename = jpg_files[i + j]
                    number = get_file_number(filename)
                    if number is None:
                        print(f"Skipping file without valid numeric name: {filename}")
                        continue

                    new_name = f"{folder_name}_{pair_number_str}{suffix}.jpg"
                    old_path = os.path.join(root, filename)
                    new_path = os.path.join(root, new_name)

                    if old_path != new_path:
                        os.rename(old_path, new_path)
                        print(f"Renamed: {old_path} -> {new_path}")
                    else:
                        print(f"Already correct: {old_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename .jpg files with folder prefix and suffixes based on mode.")
    parser.add_argument("main_dir", help="Path to the main directory.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all-f", action="store_true", help="Add '_f' to all files")
    group.add_argument("--f-and-b", action="store_true", help="Add '_f' to odd-numbered, '_b' to even-numbered")
    group.add_argument("--f-and-a", action="store_true", help="Add '_f' to odd-numbered, '_a' to even-numbered")

    args = parser.parse_args()

    if args.all_f:
        selected_mode = "all-f"
    elif args.f_and_b:
        selected_mode = "f-and-b"
    elif args.f_and_a:
        selected_mode = "f-and-a"
    else:
        raise RuntimeError("No valid mode selected")

    rename_files(args.main_dir, selected_mode)
