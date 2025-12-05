import torch, sys
import cv2, math, re
import os, base64, easyocr, json
import numpy as np
from detectron2.data import MetadataCatalog
from image_analysis.aadhar import CFG_AADHAR,predictor_aadhar

READER = easyocr.Reader(['en'], gpu=False)  # Initialize EasyOCR Reader (languages: English)

def extract_text_from_box(image_np, bbox, confidence=0.4):
    # --- 1. Crop the Region ---
    x1, y1, x2, y2 = [int(coord) for coord in bbox]
    cropped_region = image_np[y1:y2, x1:x2]
    if cropped_region.size == 0:    return "[Empty Region]"
        
    # --- 2. Perform OCR ---
    results = READER.readtext(cropped_region)
    if not results: return "[No Text Detected]"
    
    # --- 3. Filter and Pre-Calculate Metrics ---
    valid_results = []
    for (box, text, conf) in results:
        if conf >= confidence:
            # EasyOCR box format: [[tl], [tr], [br], [bl]]
            # Calculate centroid Y and X
            y_coords = [b[1] for b in box]
            x_coords = [b[0] for b in box]
            
            center_y = sum(y_coords) / 4
            center_x = sum(x_coords) / 4
            
            # Calculate approximate height of this specific word (avg vertical distance)
            height = (abs(box[3][1] - box[0][1]) + abs(box[2][1] - box[1][1])) / 2
            
            valid_results.append({'text': text, 'cy': center_y, 'cx': center_x, 'h': height})

    if not valid_results:
        return "[No Text Detected Above Confidence Threshold]"

    # --- 4. Primary Sort by Y (Top-to-Bottom) ---
    # This puts roughly top items first, but horizontal order might be mixed
    valid_results.sort(key=lambda k: k['cy'])

    # --- 5. Line Clustering ---
    lines = []
    # Start the first line with the top-most item
    current_line = [valid_results[0]]
    
    for i in range(1, len(valid_results)):
        item = valid_results[i]
        prev_item = current_line[-1]
        
        # Calculate vertical distance to the previous item added to the current line
        y_diff = abs(item['cy'] - prev_item['cy'])
        
        # Threshold: If the vertical difference is small (less than half the height of the previous word),
        # we consider them to be on the same line.
        if y_diff < (prev_item['h'] * 0.5):
            current_line.append(item)
        else:
            # The gap is too big; this item belongs to a new line below.
            lines.append(current_line)
            current_line = [item]
            
    # Append the last line being built
    lines.append(current_line)

    # --- 6. Secondary Sort (Left-to-Right) & Join ---
    final_text_lines = []
    for line in lines:
        # Sort words within this specific line by X coordinate
        line.sort(key=lambda k: k['cx'])
        
        # Join words in the line with a space
        line_text = " ".join([word['text'] for word in line])
        final_text_lines.append(line_text)

    # Join separate lines with a newline character
    final_text = "\n".join(final_text_lines)
    #cleaned_text = re.sub(r'[^\x00-\x7F]+', '', final_text)
    return final_text