import cv2
import numpy as np
import logging
import time
import json
import os
import random
import glob
import pika
import threading
from flask import Flask, Response
from grid import GridManager
from detector import PieceDetector
from fusion import FusionManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AVS")

app = Flask(__name__)
current_frame = None
frame_lock = threading.Lock()

class RabbitMQPublisher:
    def __init__(self, host='rabbitmq-broker', queue='board_state_queue'):
        self.host = host
        self.queue = queue
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, heartbeat=600))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue)
            logger.info(f"Connected to RabbitMQ at {self.host}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")

    def publish(self, state):
        if not self.channel or self.connection.is_closed:
            self.connect()
        if self.channel:
            try:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=self.queue,
                    body=json.dumps(state)
                )
            except Exception as e:
                logger.error(f"Error publishing to RabbitMQ: {e}")
                self.channel = None

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
        for src in sources:
            src_str = str(src)
            if os.path.isdir(src_str):
                files = []
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG', '*.mp4', '*.avi']:
                    found = glob.glob(os.path.join(src_str, ext))
                    files.extend(found)
                if not files:
                    logger.warning(f"No mock files found in directory: {src_str}")
                self.mock_files.append(files)
            else:
                self.mock_files.append([src_str])
        
        for file_list in self.mock_files:
            if file_list and (file_list[0].endswith(('.mp4', '.avi'))):
                self.caps.append(cv2.VideoCapture(file_list[0]))
            else:
                self.caps.append(None)

    def get_all_frames(self):
        frames = []
        source_count = len(self.mock_files) if self.use_mock else len(self.caps)
        for i in range(source_count):
            if self.use_mock:
                frame = self.get_mock_frame(i)
            else:
                ret, frame = self.caps[i].read()
                if not ret:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frames.append(frame)
        return frames

    def get_mock_frame(self, index):
        file_list = self.mock_files[index]
        if not file_list:
            return np.zeros((480, 640, 3), dtype=np.uint8)
        
        if self.caps[index] is not None:
            ret, frame = self.caps[index].read()
            if not ret:
                self.caps[index].set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.caps[index].read()
            return frame if ret else np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Pick a random file from the list (ensures we don't imread a directory)
        img_path = random.choice(file_list)
        if os.path.isdir(img_path):
            logger.warning(f"Path {img_path} is a directory, skipping.")
            return np.zeros((480, 640, 3), dtype=np.uint8)
            
        frame = cv2.imread(img_path)
        if frame is None:
            logger.warning(f"Failed to load image: {img_path}")
            return np.zeros((480, 640, 3), dtype=np.uint8)
        return frame

    def release(self):
        for cap in self.caps:
            if cap: cap.release()

@app.route('/stream')
def video_feed():
    def generate():
        global current_frame
        while True:
            with frame_lock:
                if current_frame is None:
                    time.sleep(0.1)
                    continue
                (flag, encodedImage) = cv2.imencode(".jpg", current_frame)
                if not flag:
                    time.sleep(0.1)
                    continue
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')
            time.sleep(0.1)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

def load_calibration(path="calibration_config.json"):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f: return json.load(f)
        except: return {}
    return {}

def vision_loop():
    global current_frame
    use_mock = os.environ.get("USE_MOCK_DATA", "false").lower() == "true"
    camera_env = os.environ.get("CAMERA_SOURCES", "0,1")
    
    if use_mock and "CAMERA_SOURCES" not in os.environ:
        sources = ["../mock-data"]
    else:
        sources = [s.strip() for s in camera_env.split(",")]
        if not use_mock:
            sources = [int(s) if s.isdigit() else s for s in sources]

    logger.info(f"Vision loop starting. Sources: {sources}, Mock: {use_mock}")
    cap = MultiCaptureService(sources=sources, use_mock=use_mock)
    pm = PerspectiveManager(target_size=800)
    gm = GridManager(board_size=800)
    detector = PieceDetector()
    fusion = FusionManager()
    publisher = RabbitMQPublisher(host=os.environ.get('RABBITMQ_HOST', 'rabbitmq-broker'))
    
    default_corners = [[100, 100], [700, 100], [700, 700], [100, 700]]
    
    try:
        while True:
            config = load_calibration()
            frames = cap.get_all_frames()
            
            all_detections = []
            display_frame = None
            
            for i, frame in enumerate(frames):
                if frame is None or frame.size == 0: continue
                
                cam_key = f"camera_{i}"
                corners = config.get(cam_key, default_corners)
                
                try:
                    warped = pm.warp_frame(frame, corners)
                    
                    if i == 0:
                        display_frame = warped.copy()
                        gm.draw_grid(display_frame)
                    
                    detections = detector.detect_pieces(warped, gm)
                    all_detections.append(detections)
                except Exception as e:
                    logger.error(f"Error processing source {i}: {e}")
            
            if all_detections:
                fused_state = fusion.fuse(all_detections)
                if fused_state:
                    logger.info(f"Publishing board state: {len(fused_state)} pieces.")
                    publisher.publish(fused_state)
            
            if display_frame is not None:
                with frame_lock:
                    current_frame = display_frame

            time.sleep(0.5 if use_mock else 0.05)
            
    except Exception as e:
        logger.error(f"Fatal error in vision loop: {e}")
    finally:
        cap.release()

if __name__ == "__main__":
    t = threading.Thread(target=vision_loop, daemon=True)
    t.start()
    logger.info("Starting MJPEG Stream Server on port 8001...")
    app.run(host='0.0.0.0', port=8001, debug=False, threaded=True)
