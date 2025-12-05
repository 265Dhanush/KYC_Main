from image_analysis.detectron_model import setup_model_config
from detectron2.engine import DefaultPredictor

PAN_CLASSES = ["pan", "name", "father", "dob", "photo"]
PAN_METADATA_NAME = "pan_metadata"
NUM_CALSSES = 5

CFG_PAN = setup_model_config("image_analysis/Pan_model.pth", NUM_CALSSES, PAN_METADATA_NAME, PAN_CLASSES)

predictor_pan = DefaultPredictor(CFG_PAN)