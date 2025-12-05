import os, base64

upload_folder = r"D:\Intern\Infosys Virtual-6.0\New folder (4)\output" 
new_base_name = "kyc"

def save_image(file_obj):
    _, ext = os.path.splitext(file_obj.filename)            # Extract the extension (e.g., gets ".jpg" or ".png")
    new_filename = new_base_name + ext                      # Create the new complete filename (e.g., "new_name.jpg")
    full_path = os.path.join(upload_folder, new_filename)   # Construct the full path
    file_obj.save(full_path)                                # Save the file
    return full_path

def save_base64_photo(base64_string, output_folder, file_name="extracted_face.jpg"):

    if not base64_string:
        return None

    # Ensure the folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    full_path = os.path.join(output_folder, file_name)

    try:
        # Decode the base64 string back to bytes
        img_data = base64.b64decode(base64_string)
        
        # Write bytes to file
        with open(full_path, "wb") as f:
            f.write(img_data)
            
        print(f"--- Face saved at: {full_path} ---")
        return full_path
    except Exception as e:
        print(f"Error saving base64 image: {e}")
        return None

def delete_file(file_path):
    """
    Deletes the file at the specified path.
    """
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"--- Deleted file: {file_path} ---")
        except Exception as e:
            print(f"Error deleting file: {e}")