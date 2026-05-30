import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import sys
import os

# Add service dir to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import MultiCaptureService

class TestMultiCaptureService(unittest.TestCase):
    
    @patch('cv2.VideoCapture')
    def test_init_multi_cameras(self, mock_vc):
        """Verify that multiple cameras are initialized correctly."""
        sources = [0, 1, 2, 3]
        service = MultiCaptureService(camera_sources=sources)
        
        self.assertEqual(service.num_cameras, 4)
        self.assertEqual(mock_vc.call_count, 4)
        
    @patch('cv2.VideoCapture')
    def test_get_all_frames(self, mock_vc):
        """Verify that frames are collected from all cameras."""
        # Setup mock cameras to return success and a dummy frame
        mock_instance = MagicMock()
        mock_instance.read.return_value = (True, np.ones((480, 640, 3), dtype=np.uint8))
        mock_vc.return_value = mock_instance
        
        sources = [0, 1]
        service = MultiCaptureService(camera_sources=sources)
        frames = service.get_all_frames()
        
        self.assertEqual(len(frames), 2)
        self.assertEqual(frames[0].shape, (480, 640, 3))
        self.assertEqual(mock_instance.read.call_count, 2)

    @patch('cv2.VideoCapture')
    def test_camera_failure_fallback(self, mock_vc):
        """Verify fallback to blank frame when a camera fails."""
        mock_instance = MagicMock()
        mock_instance.read.return_value = (False, None)
        mock_vc.return_value = mock_instance
        
        service = MultiCaptureService(camera_sources=[0])
        frames = service.get_all_frames()
        
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0].shape, (480, 640, 3))
        # Ensure it's a black frame (zeros)
        self.assertTrue(np.all(frames[0] == 0))

if __name__ == "__main__":
    unittest.main()
