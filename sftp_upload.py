import paramiko
import os
from pathlib import Path
from credentials import SFTP_HOST, SFTP_PORT, SFTP_USERNAME, SFTP_PASSWORD, BASE_REMOTE_DIR


def prompt_yes_no(question):
    while True:
        resp = input(f"{question} [y/n]: ").lower()
        if resp in ["y", "yes"]:
            return True
        elif resp in ["n", "no"]:
            return False

def prompt_choice(question, choices):
    """choices is a dict like {'s': 'skip', 'o': 'overwrite', 'a': 'abort'}"""
    keys = "/".join(choices.keys())
    while True:
        resp = input(f"{question} ({keys}): ").lower()
        if resp in choices:
            return choices[resp]

def connect_sftp():
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USERNAME, password=SFTP_PASSWORD)
    return paramiko.SFTPClient.from_transport(transport)

def remote_path_exists(sftp, path):
    try:
        sftp.stat(path)
        return True
    except FileNotFoundError:
        return False

def upload_directory(sftp, local_dir):
    local_dir = Path(local_dir).resolve()
    subfolders = [f for f in local_dir.iterdir() if f.is_dir()]

    for folder in subfolders:
        remote_folder = f"{REMOTE_BASE_DIR}/{folder.name}"
        print(f"\nProcessing folder: {folder.name}")

        if remote_path_exists(sftp, remote_folder):
            if not prompt_yes_no(f"Remote folder '{remote_folder}' exists. Add files to it?"):
                print("Aborting folder upload.")
                continue
        else:
            sftp.mkdir(remote_folder)
            print(f"Created remote folder: {remote_folder}")

        apply_all_decision = None  # ("skip" or "overwrite")
        for file in folder.glob("*"):
            if not file.is_file():
                continue

            remote_file = f"{remote_folder}/{file.name}"
            if remote_path_exists(sftp, remote_file):
                if apply_all_decision:
                    decision = apply_all_decision
                else:
                    decision = prompt_choice(
                        f"File '{file.name}' exists in '{remote_folder}'.",
                        {"s": "skip", "o": "overwrite", "a": "abort"}
                    )

                    if decision in ["skip", "overwrite"]:
                        if prompt_yes_no(f"Apply '{decision}' to all remaining files?"):
                            apply_all_decision = decision

                if decision == "abort":
                    print("Aborting entire transfer.")
                    return
                elif decision == "skip":
                    print(f"Skipped: {file.name}")
                    continue
                elif decision == "overwrite":
                    sftp.put(str(file), remote_file)
                    print(f"Overwritten: {file.name}")
            else:
                sftp.put(str(file), remote_file)
                print(f"Uploaded: {file.name}")

    print("\nAll folders processed.")

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python sftp_upload.py /path/to/local_main_dir")
        return

    local_main_dir = sys.argv[1]

    sftp = connect_sftp()
    try:
        upload_directory(sftp, local_main_dir)
    finally:
        sftp.close()
        print("SFTP connection closed.")

if __name__ == "__main__":
    main()
