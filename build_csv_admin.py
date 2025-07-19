import os
import csv
import sys
from pathlib import Path
from get_max_id import get_highest_ids, collection_exists

GROUP_TYPE = "g"

def create_csv(filepath, fieldnames):
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

def write_to_csv(filepath, row):
    with open(filepath, 'a', encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def main(input_path, collection_id, output_path=None):
    if not collection_exists(collection_id):
        print(f"❌ Collection ID {collection_id} does not exist in the database.")
        sys.exit(1)
        
    path = Path(input_path).resolve()
    
    if output_path:
        output_path = Path(output_path).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
        group_csv_path = output_path / "records_group.csv"
        record_csv_path = output_path / "records_record.csv"
        image_csv_path = output_path / "records_image.csv"
    else:
        group_csv_path = path / "csv_data" / "records_group.csv"
        record_csv_path = path / "csv_data" / "records_record.csv"
        image_csv_path = path / "csv_data" / "records_image.csv"

    # Create CSV files with headers
    create_csv(group_csv_path, ["id", "name", "group_type", "collection"])
    create_csv(record_csv_path, ["id", "group", "string"])
    create_csv(image_csv_path, ["id", "file", "text", "record", "search_vector", "type"])

    record_id = get_highest_ids("records_record") + 1
    image_id = get_highest_ids("records_image") + 1

    folders = sorted([folder for folder in os.listdir(path) if (path / folder).is_dir()])
    print(f"Found folders: {folders}")

    for folder in folders:
        folder_path = path / folder
        records = set()
        group_id = folder

        for file in os.listdir(folder_path):
            if file.endswith("jpg"):
                record = "_".join(file.split("_")[:2])
                if record not in records:
                    records.add(record)
                    record_id += 1
                    write_to_csv(record_csv_path, [record_id, group_id, record])

                img_file = file.rsplit(".", 1)[0]
                txt_file = folder_path / f"{img_file}.txt"
                
                try:
                    with open(txt_file, "r", encoding="utf-8") as f:
                        text_content = f.read().strip()
                except FileNotFoundError:
                    print(f"Warning: Missing TXT file for image: {txt_file}")
                    text_content = ""

                write_to_csv(image_csv_path, [image_id, img_file, text_content, record_id, "", GROUP_TYPE])
                image_id += 1

        if records:
            group_name = sorted(records).pop().split("_")[0]
            write_to_csv(group_csv_path, [group_id, group_name, GROUP_TYPE, collection_id])

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python build_csv_admin.py /path/to/main_dir <collection_id> [optional:/path/to/output_dir]")
        sys.exit(1)

    input_path = sys.argv[1]
    try:
        collection_id = int(sys.argv[2])
    except ValueError:
        print("❌ Error: collection_id must be an integer.")
        sys.exit(1)

    output_path = sys.argv[3] if len(sys.argv) == 4 else None
    main(input_path, collection_id, output_path)
