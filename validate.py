from flask import jsonify
from db import adhar, pan

# -------------- Validator Method (API Logic for Aadhar) -----------------

def validate_aadhar_data(data_from_frontend):
    errors = []  # to collect mismatch reasons

    aadhaar_no = data_from_frontend.get("uid")
    record = adhar.find_one({"_id": aadhaar_no}, {"_id": 0})
    if not record:
        errors.append("Document not found")

    # Field-by-field comparison
    if record.get("name") != data_from_frontend.get("name"):
        errors.append("Name does not match")

    if record.get("dob") != data_from_frontend.get("dob"):
        errors.append("Date of Birth does not match")

    if record.get("address") != data_from_frontend.get("address"):
        errors.append("Address does not match")

    if record.get("phone") != data_from_frontend.get("phone"):
        errors.append("Phone number does not match")

    # If no errors -> verified success
    if len(errors) == 0:
        return True, "All fields matched"

    # Otherwise return failure with detailed mismatch info
    return False, "; ".join(errors)

# -------------- Validator Method (API Logic for PAN) -----------------

def validate_pan_data(data_from_frontend):
    errors = []  # to collect mismatch reasons

    pan_no = data_from_frontend.get("pan_number")
    record = pan.find_one({"_id": pan_no}, {"_id": 0})
    if not record:
        errors.append("Document not found")

    # Field-by-field comparison
    if record.get("name") != data_from_frontend.get("name"):
        errors.append("Name does not match")

    if record.get("dob") != data_from_frontend.get("dob"):
        errors.append("Date of Birth does not match")

    if record.get("father_name") != data_from_frontend.get("father_name"):
        errors.append("Father Name does not match")

    # If no errors -> verified success
    if len(errors) == 0:
        return True, "All fields matched"

    # Otherwise return failure with detailed mismatch info
    return False, "; ".join(errors) 


print("--- Inserting Sample Data ---")

# 1. SAMPLE AADHAAR DATA
# Note: We use the Aadhaar Number as the unique '_id' because 
# your validator does: adhar.find_one({"_id": aadhaar_no})
aadhar_data = {
    "_id": "949987697574",       # The Aadhaar Number
    "name": "Dhanush Kumar PV",
    "dob": "26/11/2003",         # Format must match your OCR output format
    "address": "C/O P J Venkatesh Reddy,#2345/434,Apoorva Ground Floor,4th Cross, Med Plud Opposite road, HKR circle, college Road, Davanagere,Davanagere,Karnataka-577004",
    "phone": "9876543210"
}

try:
    # duplicate key error prevention (upsert)
    adhar.replace_one({"_id": aadhar_data["_id"]}, aadhar_data, upsert=True)
    print(f"Successfully inserted/updated Aadhaar: {aadhar_data['_id']}")
except Exception as e:
    print(f"Error inserting Aadhaar: {e}")


# 2. SAMPLE PAN DATA
# Note: We use the PAN Number as the unique '_id'
pan_data = {
    "_id": "HLLPD4037B",         # The PAN Number
    "name": "DHANUSH KUMAR PV",
    "dob": "26/11/2003",
    "father_name": "VENKATESH REDDY"
}

try:
    pan.replace_one({"_id": pan_data["_id"]}, pan_data, upsert=True)
    print(f"Successfully inserted/updated PAN: {pan_data['_id']}")
except Exception as e:
    print(f"Error inserting PAN: {e}")

print("--- Done ---")