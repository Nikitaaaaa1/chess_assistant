import unittest
from fusion import FusionManager

class TestFusionManager(unittest.TestCase):
    def setUp(self):
        self.fm = FusionManager(confidence_threshold=0.5)

    def test_fusion_highest_confidence_multi(self):
        """Verify that the highest confidence detection is chosen for a square across multiple cameras."""
        # 4 cameras detecting the same square
        detections = [
            [{'square': 'e4', 'piece': 'wP', 'conf': 0.6}],
            [{'square': 'e4', 'piece': 'bP', 'conf': 0.9}],
            [{'square': 'e4', 'piece': 'wP', 'conf': 0.4}], # Below threshold
            [{'square': 'e4', 'piece': 'wP', 'conf': 0.7}]
        ]
        
        fused = self.fm.fuse(detections)
        self.assertEqual(fused['e4'], 'bP')

    def test_fusion_threshold(self):
        """Verify that detections below the threshold are ignored."""
        detections = [[{'square': 'e4', 'piece': 'wP', 'conf': 0.4}]]
        
        fused = self.fm.fuse(detections)
        self.assertNotIn('e4', fused)

    def test_fusion_multi_coverage(self):
        """Verify that disparate squares from multiple cameras are combined."""
        detections = [
            [{'square': 'a1', 'piece': 'wR', 'conf': 0.8}],
            [{'square': 'h8', 'piece': 'bR', 'conf': 0.8}],
            [{'square': 'd4', 'piece': 'wQ', 'conf': 0.9}],
            [{'square': 'e5', 'piece': 'bK', 'conf': 0.7}]
        ]
        
        fused = self.fm.fuse(detections)
        self.assertEqual(len(fused), 4)
        self.assertEqual(fused['a1'], 'wR')
        self.assertEqual(fused['h8'], 'bR')
        self.assertEqual(fused['d4'], 'wQ')
        self.assertEqual(fused['e5'], 'bK')

    def test_single_camera_fusion(self):
        """Verify fusion works with just one camera."""
        detections = [[{'square': 'e2', 'piece': 'wP', 'conf': 0.9}]]
        fused = self.fm.fuse(detections)
        self.assertEqual(fused['e2'], 'wP')

    def test_empty_detections(self):
        """Verify fusion handles empty lists safely."""
        fused = self.fm.fuse([])
        self.assertEqual(fused, {})
        
        fused = self.fm.fuse([[], []])
        self.assertEqual(fused, {})

if __name__ == "__main__":
    unittest.main()
