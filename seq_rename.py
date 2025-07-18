import os
import argparse

def rename_jpgs_in_subfolders(main_dir, num_zeros=3):
    for root, dirs, files in os.walk(main_dir):
        jpg_files = sorted([f for f in files if f.lower().endswith(".jpg")])
        for idx, filename in enumerate(jpg_files, start=1):
            new_name = f"{str(idx).zfill(num_zeros)}.jpg"
            old_path = os.path.join(root, filename)
            new_path = os.path.join(root, new_name)
            if old_path != new_path:
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} -> {new_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename all .jpg files in subfolders to a numeric sequence.")
    parser.add_argument("main_dir", help="Path to the main directory.")
    parser.add_argument("num_zeros", nargs="?", default=4, type=int,
                        help="Number of leading zeros (default: 4)")

    args = parser.parse_args()
    rename_jpgs_in_subfolders(args.main_dir, args.num_zeros)
