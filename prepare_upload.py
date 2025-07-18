import os
import sys
import shutil
import paramiko
from pathlib import Path
from PIL import Image
from credentials import SFTP_HOST, SFTP_PORT, SFTP_USERNAME, SFTP_PASSWORD, BASE_REMOTE_DIR


def get_highest_remote_folder(sftp, base_dir):
    try:
        folder_names = sftp.listdir(base_dir)
        numbered_folders = [int(name) for name in folder_names if name.isdigit()]
        return max(numbered_folders) if numbered_folders else 0
    except Exception as e:
        print(f"Error accessing remote folder: {e}")
        return 0

def rename_local_folders(main_dir, start_index):
    subfolders = sorted([f for f in Path(main_dir).iterdir() if f.is_dir()])
    renamed_folders = []
    for i, folder in enumerate(subfolders):
        new_name = str(start_index + i)
        new_path = folder.parent / new_name
        folder.rename(new_path)
        renamed_folders.append(new_path)
        print(f"Renamed {folder.name} → {new_name}")
    return renamed_folders

def copy_and_rename_jpgs(main_dir, uploads_dir):
    uploads_dir.mkdir(parents=True, exist_ok=True)
    for folder in Path(main_dir).iterdir():
        if folder.is_dir():
            upload_subfolder = uploads_dir / folder.name
            upload_subfolder.mkdir(parents=True, exist_ok=True)

            for img_file in folder.glob("*.jpg"):
                new_name = img_file.stem + "_normal.jpg"
                target_path = upload_subfolder / new_name
                shutil.copy(img_file, target_path)
                print(f"Copied: {img_file} → {target_path}")

def create_thumbnails(uploads_dir, thumb_size=400):
    for folder in uploads_dir.iterdir():
        if folder.is_dir():
            for img_file in folder.glob("*_normal.jpg"):
                with Image.open(img_file) as img:
                    img.thumbnail((thumb_size, thumb_size))
                    thumb_path = folder / (img_file.stem.replace("_normal", "_thumb") + ".jpg")
                    img.save(thumb_path, "JPEG")
                    print(f"Thumbnail saved: {thumb_path}")

def main(main_dir, uploads_parent_dir=None):
    main_dir = Path(main_dir).resolve()

    # Determine uploads directory
    if uploads_parent_dir:
        uploads_dir = Path(uploads_parent_dir).resolve() / "uploads"
    else:
        uploads_dir = main_dir.parent / "uploads"

    # 1. Connect to SFTP and get highest folder number
    print("Connecting to SFTP...")
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
    sftp = paramiko.SFTPClient.from_transport(transport)

    highest_remote = get_highest_remote_folder(sftp, BASE_REMOTE_DIR)
    print(f"Highest remote folder: {highest_remote}")

    # 2. Rename local subfolders
    renamed_folders = rename_local_folders(main_dir, highest_remote + 1)

    # 3. Copy JPGs to uploads and rename with _normal
    copy_and_rename_jpgs(main_dir, uploads_dir)

    # 4. Create thumbnails with _thumb suffix
    create_thumbnails(uploads_dir)

    sftp.close()
    transport.close()
    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python process_folders.py /path/to/main_dir [optional:/path/to/uploads_parent]")
    else:
        main_dir = sys.argv[1]
        uploads_dir = sys.argv[2] if len(sys.argv) == 3 else None
        main(main_dir, uploads_dir)
