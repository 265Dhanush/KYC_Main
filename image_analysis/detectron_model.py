from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2 import model_zoo

def setup_model_config(weights_path, num_classes, metadata_name, class_names):
    """Initializes and returns the Detectron2 config, and registers metadata."""
    cfg = get_cfg()
    
    # Using a common base Mask R-CNN config (MUST match your trained architecture)
    cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
    
    # 1. Register Metadata with custom class names (FIXES LABELING ISSUE)
    MetadataCatalog.get(metadata_name).set(thing_classes=class_names)

    # 2. Link the registered name to the config for visualization
    cfg.DATASETS.TRAIN = (metadata_name,) 

    # 3. Apply model-specific settings
    cfg.MODEL.WEIGHTS = weights_path
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = num_classes
    cfg.MODEL.DEVICE = "cpu" # Enforce CPU usage
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7 # Minimum detection confidence

    return cfg