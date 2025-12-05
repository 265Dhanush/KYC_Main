import torch, sys
import cv2, math, re
import os, base64, easyocr, json
import numpy as np
from detectron2.data import MetadataCatalog
from image_analysis.pan import CFG_PAN,predictor_pan
from ocr import extract_text_from_box

def extract_pan(image_path):
    """Executes PAN model and extracts data for specific regions."""
    
    if not os.path.exists(image_path):
        return {"error": f"Image not found at {image_path}"}
        
    im = cv2.imread(image_path)
    outputs = predictor_pan(im)
    instances = outputs["instances"].to("cpu")
    metadata_name = CFG_PAN.DATASETS.TRAIN[0]
    class_names = MetadataCatalog.get(metadata_name).thing_classes

    extracted_data = {}

    for i in range(len(instances)):
        class_id = instances.pred_classes[i].item()
        bbox = instances.pred_boxes.tensor[i].tolist()
        region_name = class_names[class_id]

        # the 'photo' region
        if region_name.lower() == "photo":
            x1, y1, x2, y2 = map(int, bbox)
            
            # 2. Crop the image (Numpy slicing is [y:y+h, x:x+w])
            # Add boundary checks to ensure we don't slice outside image dimensions
            h, w, _ = im.shape
            y1, y2 = max(0, y1), min(h, y2)
            x1, x2 = max(0, x1), min(w, x2)
            
            cropped_img = im[y1:y2, x1:x2]
            
            # 3. Encode crop to Base64 string
            # Check if crop is valid (not empty)
            if cropped_img.size > 0:
                _, buffer = cv2.imencode('.jpg', cropped_img)
                photo_base64 = base64.b64encode(buffer).decode('utf-8')
                extracted_data[region_name] = photo_base64
            continue

        # Extract text using the core utility function
        extracted_text = extract_text_from_box(im, bbox)
        extracted_data[region_name] = extracted_text

    return extracted_data

def clean_pan_data(raw_data):
    cleaned = {}

    # --- 1. PAN Number ---
    # Logic: Look for the strict PAN pattern (5 chars, 4 nums, 1 char) first.
    # If not found, fallback to the user's request (Last Line).
    raw_pan = raw_data.get("pan", "")
    # Regex for PAN: [A-Z]{5} = 5 letters, [0-9]{4} = 4 digits, [A-Z] = 1 letter
    pan_match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', raw_pan)
    
    if pan_match:
        cleaned['pan'] = pan_match.group(0)
    else:
        # Fallback: Take the last line
        lines = raw_pan.strip().split('\n')
        cleaned['pan'] = lines[-1].strip() if lines else ""

    # --- 2. Date of Birth (DOB) ---
    # Logic: Find the date pattern dd/mm/yyyy
    raw_dob = raw_data.get("dob", "")
    dob_match = re.search(r'\d{2}/\d{2}/\d{4}', raw_dob)
    cleaned['dob'] = dob_match.group(0) if dob_match else ""

    # --- 3. Name ---
    # Logic: Take 2nd line if available, otherwise 1st line.
    raw_name = raw_data.get("name", "")
    name_lines = raw_name.strip().split('\n')
    
    if len(name_lines) > 1:
        # If we have multiple lines (e.g. "Name\nAYUSH"), take the second
        cleaned['name'] = name_lines[1].strip()
    else:
        # If we have only one line, take it (unless it's just the word "Name")
        val = name_lines[0].strip()
        cleaned['name'] = val if val.lower() != "name" else ""

    # --- 4. Father's Name ---
    # Logic: Take 2nd line if available, otherwise 1st line.
    raw_father = raw_data.get("father", "")
    father_lines = raw_father.strip().split('\n')
    
    if len(father_lines) > 1:
        cleaned['father'] = father_lines[1].strip()
    else:
        val = father_lines[0].strip()
        # cleaning up common headers just in case
        cleaned['father'] = val if "father" not in val.lower() else ""

    # --- 5. Photo (Pass through) ---
    cleaned['photo'] = raw_data.get("photo", "")

    return cleaned

if __name__ == "__main__":
    try:
        # Read the image path argument passed by Flask
        if len(sys.argv) > 1:
            image_path_arg = sys.argv[1]
            
            # 2. Call the Main Function
            result_data = extract_pan(image_path_arg)
            
            # 3. Print Result as JSON (This goes to Flask)
            print(json.dumps(result_data))
        else:
            print(json.dumps({"error": "No image path argument provided to text.py"}))
            
    except Exception as e:
        # Catch any unexpected crashes and print as JSON error
        print(json.dumps({"error": str(e)}))