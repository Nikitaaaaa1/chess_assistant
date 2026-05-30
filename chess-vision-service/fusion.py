import logging

logger = logging.getLogger("AVS.Fusion")

class FusionManager:
    """Fuses detections from multiple cameras to mitigate piece occlusion."""
    def __init__(self, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold

    def fuse(self, detection_sets):
        """
        Aggregates board state by comparing confidence scores from multiple sources.
        Expects a list of lists of detections.
        Priority is given to the highest confidence detection for each square.
        """
        final_state = {}
        
        # Flatten all detection sets into one list
        all_detections = [det for det_set in detection_sets for det in det_set]
        
        # Sort by confidence descending
        all_detections.sort(key=lambda x: x['conf'], reverse=True)
        
        for det in all_detections:
            sq = det['square']
            # Only add if confidence meets threshold and square isn't already filled by a higher-conf match
            if det['conf'] >= self.confidence_threshold:
                if sq not in final_state:
                    final_state[sq] = det['piece']
                    
        return final_state
