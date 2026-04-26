import cv2
import numpy as np
import logging
from ultralytics import YOLO

logger = logging.getLogger("AVS.Detector")

class PieceDetector:
    """Handles YOLOv8 inference and maps detections to the board grid."""
    def __init__(self, model_path="yolov8n.pt"):
        # Load a pre-trained YOLOv8 model (placeholder)
        # In production, this would be a custom-trained model for chess pieces
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            logger.warning(f"Failed to load YOLO model {model_path}: {e}. Simulation mode active.")
            self.model = None

    def detect_pieces(self, warped_frame, grid_manager):
        """Returns a list of detections: [{'square': 'e4', 'piece': 'wP', 'conf': 0.9}]"""
        if self.model is None:
            return [] # Mock empty detection for now
            
        results = self.model(warped_frame, verbose=False)
        detections = []
        
        # Results is a list of ultralytics.engine.results.Results
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                # Get center of bounding box
                x_c = (box.xyxy[0][0] + box.xyxy[0][2]) / 2
                y_c = (box.xyxy[0][1] + box.xyxy[0][3]) / 2
                
                # Identify which square this center belongs to
                square = self.identify_square(x_c, y_c, grid_manager)
                
                # Map YOLO class ID to piece notation (placeholder mapping)
                piece_label = self.map_class_id(int(box.cls[0]))
                
                detections.append({
                    "square": square,
                    "piece": piece_label,
                    "conf": float(box.conf[0])
                })
        
        return detections

    def identify_square(self, x, y, grid_manager):
        """Inverse mapping from pixel coordinates to algebraic notation."""
        sq_size = grid_manager.sq_size
        file_idx = int(x // sq_size)
        rank_idx = int(y // sq_size)
        
        # Clip indices to 0-7
        file_idx = max(0, min(7, file_idx))
        rank_idx = max(0, min(7, rank_idx))
        
        file = grid_manager.files[file_idx]
        rank = grid_manager.ranks[rank_idx]
        return f"{file}{rank}"

    def map_class_id(self, class_id):
        # Placeholder for custom chess piece model mapping
        return f"piece_{class_id}"
