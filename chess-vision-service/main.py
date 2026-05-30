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
        while True:
            try:
                logger.info(f"Connecting to RabbitMQ at {self.host}...")
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=self.host, 
                    heartbeat=600,
                    connection_attempts=10,
                    retry_delay=5
                ))
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue)
                logger.info("Successfully connected to RabbitMQ.")
                return
            except Exception as e:
                logger.warning(f"RabbitMQ connection failed: {e}. Retrying in 5s...")
                time.sleep(5)

    def publish(self, state):
        if not self.channel or self.connection.is_closed:
            self.connect()
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue,
                body=json.dumps(state)
            )
        except Exception as e:
            logger.error(f"Error publishing: {e}")
            self.channel = None

class MultiCaptureService:
    def __init__(self, sources=[0], use_mock=False):
        self.use_mock = use_mock
        self.sources = sources
        self.caps = []
        self.mock_files = []
        self.last_rescan = 0
        
        if use_mock:
            self.rescan_mock_sources()
        else:
            self.caps = [cv2.VideoCapture(src) for src in sources]
            
        logger.info(f"Capture Service: {len(self.mock_files if use_mock else self.caps)} sources (Mock: {use_mock})")

    def rescan_mock_sources(self):
        new_mock_files = []
        for src in self.sources:
            src_str = str(src)
            if os.path.isdir(src_str):
                files = []
                for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG', '*.mp4', '*.avi']:
                    found = glob.glob(os.path.join(src_str, ext))
                    files.extend(found)
                # Filter out directories just in case
                files = [f for f in files if os.path.isfile(f)]
                new_mock_files.append(sorted(list(set(files))))
            else:
                if os.path.isfile(src_str):
                    new_mock_files.append([src_str])
        
        if not self.caps and new_mock_files:
            for file_list in new_mock_files:
                if file_list and (file_list[0].lower().endswith(('.mp4', '.avi'))):
                    self.caps.append(cv2.VideoCapture(file_list[0]))
                else:
                    self.caps.append(None)
        
        self.mock_files = new_mock_files
        self.last_rescan = time.time()
        if self.use_mock:
            logger.info(f"Mock Rescan: Found {sum(len(f) for f in self.mock_files)} files across {len(self.mock_files)} sources.")

    def get_all_frames(self):
        if self.use_mock and (time.time() - self.last_rescan > 10):
            self.rescan_mock_sources()

        frames = []
        source_count = len(self.mock_files) if self.use_mock else len(self.caps)
        for i in range(source_count):
            if self.use_mock:
                frame = self.get_mock_frame(i)
            else:
                ret, frame = self.caps[i].read()
                if not ret:
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(frame, "CAM SIGNAL LOST", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            frames.append(frame)
        return frames

    def get_mock_frame(self, index):
        if index >= len(self.mock_files): return self.error_frame("INDEX ERROR")
        file_list = self.mock_files[index]
        if not file_list: return self.error_frame("NO FILES IN DIR")
        
        if self.caps[index] is not None:
            ret, frame = self.caps[index].read()
            if not ret:
                self.caps[index].set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.caps[index].read()
            return frame if ret else self.error_frame("VIDEO ERROR")
        
        img_path = random.choice(file_list)
        frame = cv2.imread(img_path)
        if frame is None:
            logger.error(f"Failed to read image: {img_path}")
            return self.error_frame(f"READ ERROR: {os.path.basename(img_path)}")
        return frame

    def error_frame(self, text):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, text, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
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
                    # Return a "WAITING" frame instead of nothing
                    frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(frame, "WAITING FOR VISION...", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    (flag, encodedImage) = cv2.imencode(".jpg", frame)
                else:
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
    camera_env = os.environ.get("CAMERA_SOURCES", "/mock-data") # Default to /mock-data
    
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
            raw_display_frames = []
            
            for i, frame in enumerate(frames):
                if frame is None or frame.size == 0: continue
                raw_display_frames.append(cv2.resize(frame, (640, 480)))
                
                cam_key = f"camera_{i}"
                corners = config.get(cam_key, default_corners)
                
                try:
                    warped = pm.warp_frame(frame, corners)
                    detections = detector.detect_pieces(warped, gm)
                    all_detections.append(detections)
                except Exception as e:
                    logger.error(f"Error source {i}: {e}")
            
            if all_detections:
                fused_state = fusion.fuse(all_detections)
                publisher.publish(fused_state)
            
            if raw_display_frames:
                if len(raw_display_frames) == 1:
                    display_frame = raw_display_frames[0]
                elif len(raw_display_frames) == 2:
                    display_frame = np.hstack(raw_display_frames)
                else: # 4
                    while len(raw_display_frames) < 4:
                        raw_display_frames.append(np.zeros((480, 640, 3), dtype=np.uint8))
                    top = np.hstack(raw_display_frames[:2])
                    bottom = np.hstack(raw_display_frames[2:4])
                    display_frame = np.vstack([top, bottom])
                
                with frame_lock:
                    current_frame = display_frame

            time.sleep(0.5 if use_mock else 0.05)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        cap.release()

if __name__ == "__main__":
    t = threading.Thread(target=vision_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=8001, debug=False, threaded=True)
