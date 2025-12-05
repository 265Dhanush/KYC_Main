from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")  # Change if needed
db = client["KYC"]  # Database Name
adhar = db["adhar_collection"]  # Collection Name
pan  = db["pan_collection"] #Collection Name