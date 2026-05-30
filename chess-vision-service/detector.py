import cv2
import numpy as np
import logging
from ultralytics import YOLO
import os

logger = logging.getLogger("AVS.Detector")

class PieceDetector:
    """Handles YOLOv8 inference and maps detections to the board grid."""
    def __init__(self, model_path="yolov8n.pt"):
        # Load a pre-trained YOLOv8 model
        self.use_mock = os.environ.get("USE_MOCK_DATA", "false").lower() == "true"
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            logger.warning(f"Failed to load YOLO model {model_path}: {e}. Simulation mode active.")
            self.model = None

    def detect_pieces(self, warped_frame, grid_manager):
        """Returns a list of detections: [{'square': 'e4', 'piece': 'wP', 'conf': 0.9}]"""
        
        # If we are in mock data mode AND no real model, generate some dummy pieces for visual feedback
        if self.use_mock and self.model is None:
            return self.generate_mock_detections()

        if self.model is None:
            return []
            
        results = self.model(warped_frame, verbose=False)
        detections = []
        
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for box in boxes:
                x_c = (box.xyxy[0][0] + box.xyxy[0][2]) / 2
                y_c = (box.xyxy[0][1] + box.xyxy[0][3]) / 2
                
                square = self.identify_square(x_c, y_c, grid_manager)
                piece_label = self.map_class_id(int(box.cls[0]))
                
                detections.append({
                    "square": square,
                    "piece": piece_label,
                    "conf": float(box.conf[0])
                })
        
        return detections

    def generate_mock_detections(self):
        """Generates static mock detections for testing the pipeline without a model."""
        # Just put a few pieces on the board to see them on the frontend
        return [
            {"square": "e2", "piece": "wP", "conf": 0.95},
            {"square": "e4", "piece": "wP", "conf": 0.88},
            {"square": "e7", "piece": "bP", "conf": 0.92},
            {"square": "e5", "piece": "bP", "conf": 0.85},
            {"square": "g1", "piece": "wN", "conf": 0.99}
        ]

    def identify_square(self, x, y, grid_manager):
        """Inverse mapping from pixel coordinates to algebraic notation."""
        sq_size = grid_manager.sq_size
        file_idx = int(x // sq_size)
        rank_idx = int(y // sq_size)
        
        file_idx = max(0, min(7, file_idx))
        rank_idx = max(rank_idx, 0) # Handle orientation if needed
        rank_idx = min(rank_idx, 7)
        
        file = grid_manager.files[file_idx]
        rank = grid_manager.ranks[rank_idx]
        return f"{file}{rank}"

    def map_class_id(self, class_id):
        # Example mapping (actual IDs depend on the model weights used)
        mapping = {
            0: "wP", 1: "wN", 2: "wB", 3: "wR", 4: "wQ", 5: "wK",
            6: "bP", 7: "bN", 8: "bB", 9: "bR", 10: "bQ", 11: "bK"
        }
        return mapping.get(class_id, f"piece_{class_id}")
