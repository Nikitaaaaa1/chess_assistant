import cv2
import numpy as np
import logging
import time
import json
import os
import random
import glob
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
    """Supports 1, 2, or 4 cameras/mock sources dynamically."""
    def __init__(self, sources=[0], use_mock=False):
        self.use_mock = use_mock
        self.sources = sources
        self.caps = []
        self.mock_files = []
        
        if use_mock:
            self.setup_mock_sources(sources)
        else:
            self.caps = [cv2.VideoCapture(src) for src in sources]
            
        self.num_sources = len(self.caps) if not use_mock else len(self.mock_files)
        logger.info(f"Initialized MultiCapture with {self.num_sources} sources (Mock: {use_mock}).")

    def setup_mock_sources(self, sources):
        """Prepares files for mock mode."""
        for src in sources:
            if os.path.isdir(str(src)):
                # If it's a directory, get all images/videos
                files = []
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.mp4', '*.avi']:
                    files.extend(glob.glob(os.path.join(src, ext)))
                self.mock_files.append(files)
            else:
                self.mock_files.append([src])
        
        # Initialize VideoCaptures for video files to enable looping
        for file_list in self.mock_files:
            if file_list and (file_list[0].endswith('.mp4') or file_list[0].endswith('.avi')):
                self.caps.append(cv2.VideoCapture(file_list[0]))
            else:
                self.caps.append(None) # Placeholder for images

    def get_all_frames(self):
        frames = []
        for i in range(len(self.mock_files) if self.use_mock else len(self.caps)):
            if self.use_mock:
                frame = self.get_mock_frame(i)
            else:
                ret, frame = self.caps[i].read()
                if not ret:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    logger.warning(f"Source {i} failed to return frame.")
            frames.append(frame)
        return frames

    def get_mock_frame(self, index):
        file_list = self.mock_files[index]
        if not file_list:
            return np.zeros((480, 640, 3), dtype=np.uint8)

        # If it's a video (already opened in self.caps)
        if self.caps[index] is not None:
            ret, frame = self.caps[index].read()
            if not ret:
                # Loop video
                self.caps[index].set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.caps[index].read()
            return frame if ret else np.zeros((480, 640, 3), dtype=np.uint8)
        
        # If it's an image or folder of images
        img_path = random.choice(file_list)
        frame = cv2.imread(img_path)
        if frame is None:
            return np.zeros((480, 640, 3), dtype=np.uint8)
        return frame

    def release(self):
        for cap in self.caps:
            if cap: cap.release()

def load_calibration(path="calibration_config.json"):
    if os.path.exists(path):
        with open(path, 'r') as f: return json.load(f)
    return {}

def main():
    use_mock = os.environ.get("USE_MOCK_DATA", "false").lower() == "true"
    camera_env = os.environ.get("CAMERA_SOURCES", "0,1")
    
    if use_mock:
        # If mock, and no sources defined, use the mock-data folder
        if "CAMERA_SOURCES" not in os.environ:
            sources = ["../mock-data"] # Relative to service dir if running from root
        else:
            sources = [s.strip() for s in camera_env.split(",")]
    else:
        try:
            sources = [int(s.strip()) if s.strip().isdigit() else s.strip() for s in camera_env.split(",")]
        except:
            sources = [0]
    
    logger.info(f"Starting AVS (Mock: {use_mock}) with sources: {sources}")
    
    cap = MultiCaptureService(sources=sources, use_mock=use_mock)
    pm = PerspectiveManager(target_size=800)
    gm = GridManager(board_size=800)
    detector = PieceDetector()
    fusion = FusionManager()
    
    default_corners = [(120, 40), (520, 40), (520, 440), (120, 440)]
    
    try:
        while True:
            config = load_calibration()
            frames = cap.get_all_frames()
            
            all_detections = []
            for i, frame in enumerate(frames):
                cam_key = f"camera_{i}"
                corners = config.get(cam_key, default_corners)
                
                # Check frame validity before warping
                if frame is None or frame.size == 0:
                    continue
                    
                warped = pm.warp_frame(frame, corners)
                detections = detector.detect_pieces(warped, gm)
                all_detections.append(detections)
            
            if all_detections:
                fused_state = fusion.fuse(all_detections)
                logger.info(f"AVS Cycle Complete. Sources: {len(frames)}, Pieces: {len(fused_state)}")
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        logger.info("Shutting down AVS...")
    finally:
        cap.release()

if __name__ == "__main__":
    main()
