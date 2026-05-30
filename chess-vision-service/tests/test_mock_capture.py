import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import sys
import os

# Add service dir to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import MultiCaptureService

class TestMockCaptureMode(unittest.TestCase):
    
    @patch('os.path.isfile')
    @patch('os.path.isdir')
    @patch('glob.glob')
    def test_init_mock_directory(self, mock_glob, mock_isdir, mock_isfile):
        """Verify that a directory source is correctly expanded in mock mode."""
        mock_isdir.return_value = True
        mock_isfile.return_value = True
        # glob.glob is called for each extension
        mock_glob.side_effect = [['mock1.jpg'], [], [], [], [], [], [], []]
        
        service = MultiCaptureService(sources=['mock_dir'], use_mock=True)
        
        self.assertEqual(len(service.mock_files), 1)
        self.assertEqual(len(service.mock_files[0]), 1)
        self.assertIn('mock1.jpg', service.mock_files[0])

    @patch('cv2.imread')
    def test_get_mock_frame_image(self, mock_imread):
        """Verify picking a random image from the mock list."""
        mock_imread.return_value = np.ones((100, 100, 3), dtype=np.uint8)
        
        # Manually setup the service state
        service = MultiCaptureService(sources=[], use_mock=True)
        service.mock_files = [['fake_img.jpg']]
        service.caps = [None]
        service.current_mock_idx = [0]
        
        frames = service.get_all_frames()
        
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0].shape, (720, 1280, 3)) # Resized
        mock_imread.assert_called_with('fake_img.jpg')

    @patch('cv2.VideoCapture')
    def test_mock_video_looping(self, mock_vc):
        """Verify that mock video sources are looped."""
        mock_cap = MagicMock()
        # First call returns frame, second fails (end of video), third returns frame (after reset)
        mock_cap.read.side_effect = [(True, np.ones((480, 640, 3))), (False, None), (True, np.ones((480, 640, 3)))]
        mock_vc.return_value = mock_cap
        
        # Setup for video
        with patch('os.path.isdir', return_value=False):
            with patch('os.path.isfile', return_value=True):
                service = MultiCaptureService(sources=['test.mp4'], use_mock=True)
        
        # Frame 1: Success
        f1 = service.get_all_frames()[0]
        self.assertTrue(f1 is not None)
        
        # Frame 2: End reached in first read, then code should set POS_FRAMES and read again
        f2 = service.get_all_frames()[0]
        self.assertTrue(f2 is not None)
        
        import cv2
        mock_cap.set.assert_called_with(cv2.CAP_PROP_POS_FRAMES, 0)

if __name__ == "__main__":
    unittest.main()
