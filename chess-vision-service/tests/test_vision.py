import unittest
import numpy as np
import os
import json
from main import PerspectiveManager
from calibrate import Calibrator

class TestVisionService(unittest.TestCase):
    def setUp(self):
        self.target_size = 800
        self.pm = PerspectiveManager(target_size=self.target_size)
        self.test_config = "test_calibration.json"

    def tearDown(self):
        if os.path.exists(self.test_config):
            os.remove(self.test_config)

    def test_perspective_warp_dimensions(self):
        """Verify that warped frame has the correct target dimensions."""
        # Create a dummy 640x480 frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Mock corners (TL, TR, BR, BL)
        corners = [(100, 100), (500, 100), (500, 400), (100, 400)]
        
        warped = self.pm.warp_frame(frame, corners)
        self.assertEqual(warped.shape, (self.target_size, self.target_size, 3))

    def test_warp_matrix_calculation(self):
        """Verify that the warp matrix is a 3x3 numpy array."""
        corners = [(0, 0), (100, 0), (100, 100), (0, 100)]
        matrix = self.pm.get_warp_matrix(corners)
        self.assertEqual(matrix.shape, (3, 3))

    def test_calibration_persistence(self):
        """Verify that Calibrator correctly saves points to JSON."""
        calib = Calibrator(cam_src=99, config_path=self.test_config)
        test_points = [(10, 10), (100, 10), (100, 100), (10, 100)]
        calib.points = test_points
        
        calib.save_config()
        
        self.assertTrue(os.path.exists(self.test_config))
        with open(self.test_config, 'r') as f:
            data = json.load(f)
            self.assertIn("camera_99", data)
            self.assertEqual(data["camera_99"], [[10, 10], [100, 10], [100, 100], [10, 100]])

if __name__ == "__main__":
    unittest.main()
