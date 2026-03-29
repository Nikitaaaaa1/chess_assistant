import cv2
import numpy as np
import logging
import time
import json
import os
from grid import GridManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AVS")

class PerspectiveManager:
    """Handles 4-point perspective transformation for the chessboard."""
    def __init__(self, target_size=800):
        self.target_size = target_size
        self.destination_points = np.float32([
            [0, 0],
            [target_size, 0],
            [target_size, target_size],
            [0, target_size]
        ])

    def get_warp_matrix(self, corner_points):
        src = np.float32(corner_points)
        return cv2.getPerspectiveTransform(src, self.destination_points)

    def warp_frame(self, frame, corner_points):
        matrix = self.get_warp_matrix(corner_points)
        return cv2.warpPerspective(frame, matrix, (self.target_size, self.target_size))

class CaptureService:
    """Handles dual camera ingestion."""
    def __init__(self, cam_a_src=0, cam_b_src=1):
        self.cam_a = cv2.VideoCapture(cam_a_src)
        self.cam_b = cv2.VideoCapture(cam_b_src)
        
        if not self.cam_a.isOpened():
            logger.warning(f"Camera A (Source {cam_a_src}) failed to open. Simulation mode active.")
        if not self.cam_b.isOpened():
            logger.warning(f"Camera B (Source {cam_b_src}) failed to open. Simulation mode active.")

    def get_frames(self):
        ret_a, frame_a = self.cam_a.read()
        ret_b, frame_b = self.cam_b.read()
        
        if not ret_a:
            frame_a = np.zeros((480, 640, 3), dtype=np.uint8)
        if not ret_b:
            frame_b = np.zeros((480, 640, 3), dtype=np.uint8)
            
        return frame_a, frame_b

    def release(self):
        self.cam_a.release()
        self.cam_b.release()

def load_calibration(path="calibration_config.json"):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def main():
    logger.info("Initializing AI Vision Service (AVS)...")
    
    cap = CaptureService()
    pm = PerspectiveManager(target_size=800)
    gm = GridManager(board_size=800)
    
    # Default corners if no calibration exists
    default_corners = [(120, 40), (520, 40), (520, 440), (120, 440)]
    
    try:
        while True:
            config = load_calibration()
            frame_a, frame_b = cap.get_frames()
            
            # Process Camera A
            corners_a = config.get("camera_0", default_corners)
            warped_a = pm.warp_frame(frame_a, corners_a)
            
            # Draw algebraic grid for debugging
            debug_frame = gm.draw_grid(warped_a.copy())
            
            # In production, we'd pass warped_a to the YOLO inference service (Task 3)
            logger.info("AVS Loop active. Board perspective stabilized and grid mapped.")
            
            # Optional: Show debug frame if display is available
            # cv2.imshow("AVS Debug", debug_frame)
            # cv2.waitKey(1)
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        logger.info("Shutting down AVS...")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
