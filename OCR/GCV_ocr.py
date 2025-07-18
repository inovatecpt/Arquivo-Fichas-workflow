import os
import json
import shutil
import sys
from pathlib import Path
from google.cloud import vision_v1
from google.cloud.vision_v1 import AnnotateImageResponse

# Initialize Vision API client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(Path(__file__).parent / "ServiceAccountToken.json")
client = vision_v1.ImageAnnotatorClient()

def get_all_subfolders_with_jpgs(root_dir):
    return [folder for folder in Path(root_dir).rglob("*") if folder.is_dir() and list(folder.glob("*.jpg"))]

def save_json_response(image_path, output_json_path):
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision_v1.types.Image(content=content)
    response = client.document_text_detection(image=image)

    output_json_path.parent.mkdir(parents=True, exist_ok=True)

    response_json = AnnotateImageResponse.to_json(response)
    with open(output_json_path, "w", encoding="utf-8") as f:
        f.write(response_json)

def extract_text_from_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    try:
        return data["fullTextAnnotation"]["text"]
    except KeyError:
        return ""

def process_folder(folder_path, temp_json_dir):
    folder_path = Path(folder_path)
    temp_json_dir = Path(temp_json_dir)

    print(f"Processing folder: {folder_path}")
    # Step 1: OCR each image and save temp JSON
    for img_path in folder_path.glob("*.jpg"):
        json_path = temp_json_dir / folder_path.name / img_path.name.replace(".jpg", ".json")
        save_json_response(img_path, json_path)

    # Step 2: Convert each JSON to TXT in the same folder as image
    for json_file in (temp_json_dir / folder_path.name).glob("*.json"):
        txt_filename = json_file.stem + ".txt"
        txt_path = folder_path / txt_filename
        try:
            text = extract_text_from_json(json_file)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Saved: {txt_path}")
        except Exception as e:
            print(f"Error processing {json_file}: {e}")

    # Step 3: Delete temp JSON folder for this subfolder
    try:
        shutil.rmtree(temp_json_dir / folder_path.name)
        print(f"Deleted temp folder: {temp_json_dir / folder_path.name}")
    except Exception as e:
        print(f"Failed to delete temp folder: {e}")

def process_all_folders(main_dir):
    main_dir = Path(main_dir)
    temp_json_dir = main_dir / "__temp_json__"
    subfolders = get_all_subfolders_with_jpgs(main_dir)

    for folder in subfolders:
        process_folder(folder, temp_json_dir)

    # Delete temp root if empty
    if temp_json_dir.exists() and not any(temp_json_dir.iterdir()):
        temp_json_dir.rmdir()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ocr_folder.py /path/to/main_directory")
    else:
        process_all_folders(sys.argv[1])
