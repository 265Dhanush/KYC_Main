from image_analysis.detectron_model import setup_model_config
from detectron2.engine import DefaultPredictor

AADHAR_CLASSES = ["Post_address", "Details", "uid", "Photo", "Address", "vid"]
AADHAR_METADATA_NAME = "aadhar_metadata"
NUM_CLASSES = 6

CFG_AADHAR = setup_model_config("image_analysis/Aadhar_model.pth", NUM_CLASSES, AADHAR_METADATA_NAME, AADHAR_CLASSES)

predictor_aadhar = DefaultPredictor(CFG_AADHAR)
