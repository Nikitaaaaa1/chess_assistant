import unittest
from fusion import FusionManager

class TestFusionManager(unittest.TestCase):
    def setUp(self):
        self.fm = FusionManager(confidence_threshold=0.5)

    def test_fusion_highest_confidence(self):
        """Verify that the highest confidence detection is chosen for a square."""
        detections_a = [{'square': 'e4', 'piece': 'wP', 'conf': 0.6}]
        detections_b = [{'square': 'e4', 'piece': 'bP', 'conf': 0.9}]
        
        fused = self.fm.fuse(detections_a, detections_b)
        self.assertEqual(fused['e4'], 'bP')

    def test_fusion_threshold(self):
        """Verify that detections below the threshold are ignored."""
        detections_a = [{'square': 'e4', 'piece': 'wP', 'conf': 0.4}]
        detections_b = []
        
        fused = self.fm.fuse(detections_a, detections_b)
        self.assertNotIn('e4', fused)

    def test_fusion_dual_coverage(self):
        """Verify that disparate squares from both cameras are combined."""
        detections_a = [{'square': 'a1', 'piece': 'wR', 'conf': 0.8}]
        detections_b = [{'square': 'h8', 'piece': 'bR', 'conf': 0.8}]
        
        fused = self.fm.fuse(detections_a, detections_b)
        self.assertEqual(len(fused), 2)
        self.assertEqual(fused['a1'], 'wR')
        self.assertEqual(fused['h8'], 'bR')

if __name__ == "__main__":
    unittest.main()
