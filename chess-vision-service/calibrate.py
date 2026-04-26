import cv2
import numpy as np
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Calibration")

class Calibrator:
    def __init__(self, cam_src=0, config_path="calibration_config.json"):
        self.cam_src = cam_src
        self.config_path = config_path
        self.points = []
        self.window_name = f"Calibrate Camera {cam_src} (Select 4 corners: TL, TR, BR, BL)"

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(self.points) < 4:
                self.points.append((int(x), int(y)))
                logger.info(f"Point {len(self.points)} captured: ({x}, {y})")

    def run(self):
        cap = cv2.VideoCapture(self.cam_src)
        if not cap.isOpened():
            logger.error(f"Cannot open camera {self.cam_src}")
            return

        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)

        logger.info("Click the 4 corners of the chessboard in order: Top-Left, Top-Right, Bottom-Right, Bottom-Left.")

        while True:
            ret, frame = cap.read()
            if not ret:
                # Simulation mode (fallback)
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "SIMULATION MODE", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            for i, p in enumerate(self.points):
                cv2.circle(frame, p, 5, (0, 255, 0), -1)
                cv2.putText(frame, str(i+1), (p[0]+10, p[1]+10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            cv2.imshow(self.window_name, frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or len(self.points) == 4:
                break
            if key == ord('r'): # Reset
                self.points = []
                logger.info("Calibration reset.")

        cap.release()
        cv2.destroyAllWindows()

        if len(self.points) == 4:
            self.save_config()
        else:
            logger.warning("Calibration incomplete. Not saved.")

    def save_config(self):
        config = {}
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)

        config[f"camera_{self.cam_src}"] = self.points
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        logger.info(f"Calibration for Camera {self.cam_src} saved to {self.config_path}")

if __name__ == "__main__":
    import sys
    src = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    calib = Calibrator(cam_src=src)
    calib.run()
