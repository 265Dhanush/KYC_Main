from flask import Flask, render_template, request, jsonify, url_for
from aadhar_text import extract_aadhar, parse_and_clean_data
from pan_text import extract_pan, clean_pan_data
from handle_image import save_image, save_base64_photo, delete_file
from validate import validate_aadhar_data, validate_pan_data
import subprocess, json

app = Flask(__name__)

env = r"D:\Intern\Infosys Virtual-6.0\New folder (4)\kyc\Scripts\python.exe"
script = r"D:\Intern\Infosys Virtual-6.0\New folder (4)\app.py"

@app.route('/')
def main_page():
    return render_template('home.html')

@app.route('/Aadhar')
def aadhar():
    return render_template('Aadhar.html')

@app.route('/upload-aadhar-image', methods=['POST'])
def image_analysis_aadhar():
    if "image" not in request.files:    return jsonify({"error": "No file uploaded"}), 400

    img = request.files["image"]
    path = save_image(img)

    txt = extract_aadhar(path)
    final_text = parse_and_clean_data(txt)
    save_base64_photo(final_text['photo'], r"D:\Intern\Infosys Virtual-6.0\New folder (4)\output")
    final_text["file_path"] = r"D:\Intern\Infosys Virtual-6.0\New folder (4)\output\extracted_face.jpg"
    # -------- Facial recognition ------------
    delete_file(r"D:\Intern\Infosys Virtual-6.0\New folder (4)\output\kyc.jpg")
    return final_text

@app.route('/submit-aadhar-data', methods=["POST"])
def submit_aadhar():
    try:
        data = request.json
        is_valid, msg = validate_aadhar_data(data)
        delete_file(r"D:\Intern\Infosys Virtual-6.0\New folder (4)\output\extracted_face.jpg")
        if is_valid:
            return jsonify({
                'status' : "success",
                'message' : "Aadhar verified successfully",
                "redirect_url" : url_for('main_page')
            })
        else:
            return jsonify({
                'status' : "error",
                "message": msg
                })
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/Pan')
def pan():
    return render_template("Pan.html")

@app.route('/upload-pan-image', methods=['POST'])
def image_analysis_pan():
    if "image" not in request.files:    return jsonify({"error": "No file uploaded"}), 400

    img = request.files["image"]
    path = save_image(img)

    txt = extract_pan(path)
    final_text = clean_pan_data(txt)
    save_base64_photo(final_text["photo"], r"D:\Intern\Infosys Virtual-6.0\New folder (4)\output")
    final_text["file_path"] = r"D:\Intern\Infosys Virtual-6.0\New folder (4)\output\extracted_face.jpg"
    # -------- Facial recognition ------------
    delete_file(r"D:\Intern\Infosys Virtual-6.0\New folder (4)\output\kyc.jpg")
    return final_text

@app.route('/submit-pan-data', methods=["POST"])
def submit_pan():
    try:
        data = request.json
        is_valid, msg = validate_pan_data(data)
        delete_file(r"D:\Intern\Infosys Virtual-6.0\New folder (4)\output\extracted_face.jpg")
        if is_valid:
            return jsonify({
                'status' : "success",
                'message' : "PAN verified successfully",
                "redirect_url" : url_for('main_page')
            })
        else:
            return jsonify({
                'status' : "error",
                "message": msg
                })
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)