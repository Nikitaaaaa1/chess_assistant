import cv2
import numpy as np
import logging
import time
import json
import os
from grid import GridManager
from detector import PieceDetector
from fusion import FusionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AVS")

class PerspectiveManager:
    def __init__(self, target_size=800):
        self.target_size = target_size
        self.destination_points = np.float32([
            [0, 0], [target_size, 0], [target_size, target_size], [0, target_size]
        ])

    def get_warp_matrix(self, corner_points):
        src = np.float32(corner_points)
        return cv2.getPerspectiveTransform(src, self.destination_points)

    def warp_frame(self, frame, corner_points):
        matrix = self.get_warp_matrix(corner_points)
        return cv2.warpPerspective(frame, matrix, (self.target_size, self.target_size))

class CaptureService:
    def __init__(self, cam_a_src=0, cam_b_src=1):
        self.cam_a = cv2.VideoCapture(cam_a_src)
        self.cam_b = cv2.VideoCapture(cam_b_src)

    def get_frames(self):
        ret_a, frame_a = self.cam_a.read()
        ret_b, frame_b = self.cam_b.read()
        if not ret_a: frame_a = np.zeros((480, 640, 3), dtype=np.uint8)
        if not ret_b: frame_b = np.zeros((480, 640, 3), dtype=np.uint8)
        return frame_a, frame_b

    def release(self):
        self.cam_a.release()
        self.cam_b.release()

def load_calibration(path="calibration_config.json"):
    if os.path.exists(path):
        with open(path, 'r') as f: return json.load(f)
    return {}

def main():
    logger.info("Initializing AI Vision Service (AVS)...")
    
    cap = CaptureService()
    pm = PerspectiveManager(target_size=800)
    gm = GridManager(board_size=800)
    detector = PieceDetector()
    fusion = FusionManager()
    
    default_corners = [(120, 40), (520, 40), (520, 440), (120, 440)]
    
    try:
        while True:
            config = load_calibration()
            frame_a, frame_b = cap.get_frames()
            
            # 1. Perspective Warping
            corners_a = config.get("camera_0", default_corners)
            corners_b = config.get("camera_1", default_corners)
            
            warped_a = pm.warp_frame(frame_a, corners_a)
            warped_b = pm.warp_frame(frame_b, corners_b)
            
            # 2. YOLO Inference
            detections_a = detector.detect_pieces(warped_a, gm)
            detections_b = detector.detect_pieces(warped_b, gm)
            
            # 3. Dual-Camera Fusion
            fused_state = fusion.fuse(detections_a, detections_b)
            
            logger.info(f"AVS Detection Cycle Complete. {len(fused_state)} pieces detected.")
            # In Task 5, we will publish fused_state to RabbitMQ
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down AVS...")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
