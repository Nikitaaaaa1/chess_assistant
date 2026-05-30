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

class MultiCaptureService:
    """Supports 1, 2, or 4 cameras dynamically."""
    def __init__(self, camera_sources=[0]):
        self.caps = [cv2.VideoCapture(src) for src in camera_sources]
        self.num_cameras = len(self.caps)
        logger.info(f"Initialized MultiCapture with {self.num_cameras} cameras.")

    def get_all_frames(self):
        frames = []
        for i, cap in enumerate(self.caps):
            ret, frame = cap.read()
            if not ret:
                # Provide a blank frame if camera fails
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                logger.warning(f"Camera {i} failed to return frame.")
            frames.append(frame)
        return frames

    def release(self):
        for cap in self.caps:
            cap.release()

def load_calibration(path="calibration_config.json"):
    if os.path.exists(path):
        with open(path, 'r') as f: return json.load(f)
    return {}

def main():
    # Configuration: determine camera count and sources
    # Can be passed via env var or default to [0, 1] as before
    camera_env = os.environ.get("CAMERA_SOURCES", "0,1")
    try:
        sources = [int(s.strip()) if s.strip().isdigit() else s.strip() for s in camera_env.split(",")]
    except:
        sources = [0]
    
    logger.info(f"Initializing AI Vision Service (AVS) with sources: {sources}")
    
    cap = MultiCaptureService(camera_sources=sources)
    pm = PerspectiveManager(target_size=800)
    gm = GridManager(board_size=800)
    detector = PieceDetector()
    fusion = FusionManager()
    
    # Default corners if no calibration exists
    default_corners = [(120, 40), (520, 40), (520, 440), (120, 440)]
    
    try:
        while True:
            config = load_calibration()
            frames = cap.get_all_frames()
            
            all_detections = []
            
            for i, frame in enumerate(frames):
                # 1. Perspective Warping for each camera
                cam_key = f"camera_{i}"
                corners = config.get(cam_key, default_corners)
                
                warped = pm.warp_frame(frame, corners)
                
                # 2. YOLO Inference for each camera
                detections = detector.detect_pieces(warped, gm)
                all_detections.append(detections)
            
            # 3. Multi-Camera Fusion
            fused_state = fusion.fuse(all_detections)
            
            logger.info(f"AVS Cycle Complete. Sources: {len(frames)}, Total pieces: {len(fused_state)}")
            
            # TODO: Publish fused_state to RabbitMQ (Task 5)
            
            time.sleep(0.05) # Increased frequency for multi-cam responsiveness
            
    except KeyboardInterrupt:
        logger.info("Shutting down AVS...")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
