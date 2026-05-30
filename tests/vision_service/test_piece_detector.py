import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import sys
import os

# Add service dir to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../chess-vision-service')))
from detector import PieceDetector
from grid import GridManager

class TestPieceDetector(unittest.TestCase):
    
    @patch('detector.YOLO')
    def test_mock_detection_mode(self, mock_yolo):
        """Verify that mock detections are returned when USE_MOCK_DATA is true."""
        os.environ["USE_MOCK_DATA"] = "true"
        detector = PieceDetector()
        
        # detector.detect_pieces ignores the frame in mock mode
        detections = detector.detect_pieces(None, None)
        
        self.assertEqual(len(detections), 6)
        self.assertEqual(detections[0]['square'], 'e2')
        self.assertEqual(detections[0]['piece'], 'wP')

    @patch('detector.YOLO')
    def test_yolo_inference_mapping(self, mock_yolo):
        """Verify that YOLO output is correctly mapped to squares and labels."""
        os.environ["USE_MOCK_DATA"] = "false"
        
        # Setup mock model results
        mock_model_instance = MagicMock()
        mock_yolo.return_value = mock_model_instance
        
        # Mock result object from Ultralytics
        mock_result = MagicMock()
        mock_box = MagicMock()
        # box.xyxy[0] = [x1, y1, x2, y2]
        # For square e2 (approx 450, 650 in 800x800 grid)
        # file e = 4, rank 2 = 6 (if 0 is top) -> x ~ 450, y ~ 650
        mock_box.xyxy = [[410, 610, 490, 690]] 
        mock_box.cls = [0] # White Pawn
        mock_box.conf = [0.95]
        
        mock_result.boxes.cpu().numpy.return_value = [mock_box]
        mock_model_instance.return_value = [mock_result]
        
        detector = PieceDetector()
        gm = GridManager(board_size=800)
        
        dummy_frame = np.zeros((800, 800, 3), dtype=np.uint8)
        detections = detector.detect_pieces(dummy_frame, gm)
        
        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0]['square'], 'e2')
        self.assertEqual(detections[0]['piece'], 'wP')
        self.assertEqual(detections[0]['conf'], 0.95)

    def test_identify_square(self):
        """Verify pixel-to-square mapping."""
        detector = PieceDetector()
        gm = GridManager(board_size=800)
        
        # (0, 0) should be a8
        self.assertEqual(detector.identify_square(10, 10, gm), 'a8')
        # (790, 790) should be h1
        self.assertEqual(detector.identify_square(790, 790, gm), 'h1')
        # (450, 450) -> file e, rank 4
        # files: a=0, b=1, c=2, d=3, e=4, f=5, g=6, h=7
        # ranks: 8=0, 7=1, 6=2, 5=3, 4=4, 3=5, 2=6, 1=7
        self.assertEqual(detector.identify_square(450, 450, gm), 'e4')

    def test_map_class_id(self):
        """Verify class ID to piece label mapping."""
        detector = PieceDetector()
        self.assertEqual(detector.map_class_id(0), 'wP')
        self.assertEqual(detector.map_class_id(5), 'wK')
        self.assertEqual(detector.map_class_id(11), 'bK')
        self.assertEqual(detector.map_class_id(99), 'piece_99')

if __name__ == "__main__":
    unittest.main()
