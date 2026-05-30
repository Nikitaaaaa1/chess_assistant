import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import sys
import os

# Add service dir to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../chess-vision-service')))
from main import PerspectiveManager

class TestPerspectiveManager(unittest.TestCase):
    
    def test_warp_matrix_generation(self):
        """Verify that a valid warp matrix is generated from 4 points."""
        pm = PerspectiveManager(target_size=800)
        corners = [[100, 100], [700, 100], [700, 700], [100, 700]]
        
        matrix = pm.get_warp_matrix(corners)
        
        self.assertEqual(matrix.shape, (3, 3))
        self.assertTrue(np.any(matrix != 0))

    @patch('cv2.warpPerspective')
    @patch('main.PerspectiveManager.get_warp_matrix')
    def test_warp_frame_call(self, mock_get_matrix, mock_warp):
        """Verify that cv2.warpPerspective is called with correct parameters."""
        pm = PerspectiveManager(target_size=800)
        mock_get_matrix.return_value = np.eye(3)
        mock_warp.return_value = np.ones((800, 800, 3))
        
        dummy_frame = np.zeros((720, 1280, 3))
        corners = [[0, 0], [100, 0], [100, 100], [0, 100]]
        
        result = pm.warp_frame(dummy_frame, corners)
        
        self.assertEqual(result.shape, (800, 800, 3))
        mock_warp.assert_called_once()

    def test_auto_detect_corners_empty(self):
        """Verify auto-detection fails gracefully on blank frames."""
        pm = PerspectiveManager(target_size=800)
        # Pitch black frame
        black_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        corners = pm.auto_detect_corners(black_frame)
        self.assertIsNone(corners)

    @patch('cv2.findContours')
    @patch('cv2.contourArea')
    @patch('cv2.arcLength')
    @patch('cv2.approxPolyDP')
    def test_auto_detect_corners_success(self, mock_approx, mock_arc, mock_area, mock_contours):
        """Verify auto-detection returns ordered points when a square is found."""
        pm = PerspectiveManager(target_size=800)
        
        # Mock a large contour that approxPolyDP says has 4 points
        mock_contours.return_value = ([np.array([[100, 100], [700, 100], [700, 700], [100, 700]])], None)
        mock_area.return_value = 500000 # Large area
        mock_arc.return_value = 2400
        # approxPolyDP returns the 4 corners
        mock_approx.return_value = np.array([[[100, 100]], [[700, 100]], [[700, 700]], [[100, 700]]])
        
        dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        corners = pm.auto_detect_corners(dummy_frame)
        
        self.assertIsNotNone(corners)
        self.assertEqual(len(corners), 4)
        # Verification of reordering (TL, TR, BR, BL)
        self.assertEqual(corners[0], [100.0, 100.0]) # TL
        self.assertEqual(corners[2], [700.0, 700.0]) # BR

if __name__ == "__main__":
    unittest.main()
