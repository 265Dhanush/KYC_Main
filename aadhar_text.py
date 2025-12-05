import torch, sys
import cv2, math, re
import os, base64, easyocr, json
import numpy as np
from detectron2.data import MetadataCatalog
from image_analysis.aadhar import CFG_AADHAR,predictor_aadhar
from ocr import extract_text_from_box

def extract_aadhar(image_path):
    
    if not os.path.exists(image_path):
        return {"error": f"Image not found at {image_path}"}
        
    im = cv2.imread(image_path)
    outputs = predictor_aadhar(im)
    instances = outputs["instances"].to("cpu")
    metadata_name = CFG_AADHAR.DATASETS.TRAIN[0]
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
        
        # Store data using the region name as the key
        extracted_data[region_name] = extracted_text

    return extracted_data

def parse_and_clean_data(raw_data):
    cleaned = {}

    # --- 1. NAME (2nd line in Post_address) ---
    try:
        p_addr = raw_data.get("Post_address", "")
        lines = p_addr.split("\n")
        if len(lines) > 1:
            cleaned["name"] = lines[1].strip()
        else:
            # Fallback: Try getting it from 'Details' if Post_address fails
            cleaned["name"] = raw_data.get("Details", "").split("\n")[0]
    except:
        cleaned["name"] = ""

    # --- 2. UID (Extract specific pattern) ---
    # Looking for 4 digits, optional char (dot/space), 4 digits, opt char, 4 digits
    uid_source = raw_data.get("uid", "")
    uid_match = re.search(r'\b\d{4}[^0-9a-zA-Z]?\d{4}[^0-9a-zA-Z]?\d{4}\b', uid_source)
    if uid_match:
        # Remove dots or extra chars to get clean numbers
        cleaned["uid"] = re.sub(r'\D', ' ', uid_match.group(0)).strip()
    else:
        cleaned["uid"] = ""

    # --- 3. VID (Look for 'VID' followed by numbers) ---
    # We check both 'uid' and 'vid' keys because OCR sometimes mixes them
    vid_source = raw_data.get("uid", "") + " " + raw_data.get("vid", "")
    # Regex: Look for "VID" followed by digits/spaces (approx 16 digits)
    vid_match = re.search(r'VID[:\s]*([\d\s]{16,24})', vid_source)
    if vid_match:
        cleaned["vid"] = vid_match.group(1).strip()
    else:
        # Fallback: look for just 16 digits in a row
        vid_strict = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b', vid_source)
        cleaned["vid"] = vid_strict.group(0) if vid_strict else ""

    # --- 4. PHONE (10 digits, last line of Post_address) ---
    try:
        phone_match = re.search(r'\b\d{10}\b', raw_data.get("Post_address", ""))
        cleaned["phone"] = phone_match.group(0) if phone_match else 0
    except:
        cleaned["phone"] = ""

    # --- 5. ADDRESS (Remove \n) ---
    raw_addr = raw_data.get("Address", "")
    # Replace newlines with comma+space
    clean_addr = raw_addr.replace("\n", ", ")
    # Remove the word "Address:" if it exists
    cleaned["address"] = clean_addr.replace("Address:", "").strip()

    # --- 6. DOB (From Details) ---
    details = str(raw_data.get("Details", ""))
    print(details)
    lines = details.strip().split('\n')
    
    #cleaned["dob"] = "" # Default value

    def extract_dob(details):
        # --- STRATEGY 1: Keyword Anchoring (Most Accurate) --- Checks for: "DOB : 12/01/1990" or "Date of Birth: 12-01-1990"
        # (?i) ignores case
        # [:\s-]* allows for colons, spaces, or dashes between label and date
        keyword_pattern = r'(?i)(?:DOB|Date\s?of\s?Birth)\s*[:\s-]*\s*(\d{2}[/-]\d{2}[/-]\d{4})'
        match = re.search(keyword_pattern, details)
        
        if match:
            return match.group(1).replace('-', '/') # Standardize to /

        # --- STRATEGY 2: Year of Birth (Older Cards) ---
        # Checks for: "Year of Birth : 1985"
        yob_pattern = r'(?i)Year\s?of\s?Birth\s*[:\s-]*\s*(\d{4})'
        match_yob = re.search(yob_pattern, details)
        
        if match_yob:
            # Start of year defaults to Jan 1st for consistency if only Year is present
            return f"01/01/{match_yob.group(1)}" 

        # --- STRATEGY 3: General Date Search (Fallback) ---
        # Just looks for dd/mm/yyyy anywhere, but tries to avoid phone numbers
        # \b ensures word boundaries
        general_pattern = r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b'
        match_any = re.search(general_pattern, details)
        
        if match_any:
            return match_any.group(1).replace('-', '/')

        return "" # Return empty if nothing found

    # --- USAGE IN YOUR MAIN CODE ---
    # Assuming 'final_text' is your dictionary and 'details' is the full OCR string
    cleaned["dob"] = extract_dob(details)
    


    # --- 7. PHOTO (Keep as is) ---
    cleaned["photo"] = raw_data.get("Photo", "")

    return cleaned

if __name__ == "__main__":
    try:
        # Read the image path argument passed by Flask
        if len(sys.argv) > 1:
            image_path_arg = sys.argv[1]
            
            # 2. Call the Main Function
            result_data = extract_aadhar(image_path_arg)
            
            # 3. Print Result as JSON (This goes to Flask)
            print(json.dumps(result_data))
        else:
            print(json.dumps({"error": "No image path argument provided to text.py"}))
            
    except Exception as e:
        # Catch any unexpected crashes and print as JSON error
        print(json.dumps({"error": str(e)}))