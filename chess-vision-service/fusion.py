import logging

logger = logging.getLogger("AVS.Fusion")

class FusionManager:
    """Fuses detections from dual cameras to mitigate piece occlusion."""
    def __init__(self, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold

    def fuse(self, detections_a, detections_b):
        """
        Aggregates board state by comparing confidence scores.
        Priority is given to the highest confidence detection for each square.
        """
        final_state = {}
        
        # Combine both detection lists
        all_detections = detections_a + detections_b
        
        # Sort by confidence descending
        all_detections.sort(key=lambda x: x['conf'], reverse=True)
        
        for det in all_detections:
            sq = det['square']
            # Only add if confidence meets threshold and square isn't already filled by a higher-conf match
            if det['conf'] >= self.confidence_threshold:
                if sq not in final_state:
                    final_state[sq] = det['piece']
                    
        return final_state
