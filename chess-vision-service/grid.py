import numpy as np
import cv2

class GridManager:
    """Subdivides a warped chessboard image into 64 squares with algebraic notation."""
    def __init__(self, board_size=800, white_on_bottom=True):
        self.board_size = board_size
        self.sq_size = board_size // 8
        self.white_on_bottom = white_on_bottom
        self.files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
        
        if not white_on_bottom:
            self.files.reverse()
            self.ranks.reverse()
        else:
            self.ranks.reverse() # Standard view: Rank 8 is top (y=0)

    def get_square_bounds(self, algebraic):
        """Returns (x, y, w, h) for a given algebraic notation like 'e4'."""
        file_idx = self.files.index(algebraic[0].lower())
        rank_idx = self.ranks.index(algebraic[1])
        
        x = file_idx * self.sq_size
        y = rank_idx * self.sq_size
        return (x, y, self.sq_size, self.sq_size)

    def get_all_squares(self):
        """Returns a dictionary mapping algebraic notation to bounding boxes."""
        grid = {}
        for r_idx, rank in enumerate(self.ranks):
            for f_idx, file in enumerate(self.files):
                notation = f"{file}{rank}"
                grid[notation] = (f_idx * self.sq_size, r_idx * self.sq_size, self.sq_size, self.sq_size)
        return grid

    def draw_grid(self, frame):
        """Debug function to draw the grid and labels on the warped frame."""
        for notation, (x, y, w, h) in self.get_all_squares().items():
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
            # Draw label in corner of square
            cv2.putText(frame, notation, (x + 5, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        return frame
