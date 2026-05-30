import pytest
import chess
import sys
import os
import importlib.util

# Add service dir to path for imports
service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../chess-logic-api'))
sys.path.append(service_dir)

# Import GameSession from main.py
spec = importlib.util.spec_from_file_location("logic_main", os.path.join(service_dir, 'main.py'))
logic_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logic_main)
GameSession = logic_main.GameSession

@pytest.fixture
def session():
    return GameSession()

def test_initial_state(session):
    assert session.board.fen().startswith(chess.STARTING_FEN.split()[0])
    assert session.stability_counter == 0
    assert session.last_raw_state == {}

def test_noise_filtering(session):
    # e2e4 move in algebraic labels
    phys_state = {"e4": "wP"} # Simplified state
    
    # First frame
    assert session.process_vision_update(phys_state) == False
    assert session.stability_counter == 0
    assert session.last_raw_state == phys_state
    
    # Second frame (same state)
    assert session.process_vision_update(phys_state) == False
    assert session.stability_counter == 1
    
    # Third frame (stability threshold reached)
    assert session.process_vision_update(phys_state) == True
    assert session.stable_state == phys_state

def test_hard_sync_on_radical_change(session):
    # Setup initial stable state (Starting position simplified)
    start_state = {chess.square_name(i): session.get_piece_label(session.board.piece_at(i)) 
                   for i in range(64) if session.board.piece_at(i)}
    
    # Mock stability
    session.last_raw_state = start_state
    session.stable_state = start_state
    session.stability_counter = 5
    
    # Radical change (more than 4 squares)
    # Let's say all pawns disappeared, only kings left
    radical_state = {"e1": "wK", "e8": "bK"} 
    
    # Mock stability for the new state
    session.last_raw_state = radical_state
    session.stability_counter = 2
    
    assert session.process_vision_update(radical_state) == True
    
    # Verify board is now matching the radical state
    piece_e1 = session.board.piece_at(chess.E1)
    assert piece_e1 is not None
    assert piece_e1.piece_type == chess.KING
    assert piece_e1.color == chess.WHITE
    assert session.board.piece_at(chess.E2) is None

def test_move_inference_e2e4(session):
    # 1. Establish stable starting position
    start_state = {chess.square_name(i): session.get_piece_label(session.board.piece_at(i)) 
                   for i in range(64) if session.board.piece_at(i)}
    session.last_raw_state = start_state
    session.stable_state = start_state
    session.stability_counter = 5
    
    # 2. Simulate e2e4 (e2 becomes empty, e4 becomes wP)
    new_state = start_state.copy()
    del new_state["e2"]
    new_state["e4"] = "wP"
    
    # Mock stability
    session.last_raw_state = new_state
    session.stability_counter = 2
    
    assert session.process_vision_update(new_state) == True
    # The board should have pushed the move
    assert session.board.piece_at(chess.E4) is not None
    assert session.board.piece_at(chess.E4).piece_type == chess.PAWN
    assert session.board.piece_at(chess.E2) is None

def test_illegal_move_reverts_to_hard_sync(session):
    # Try to move a white pawn to e5 (illegal for white at start)
    start_state = {chess.square_name(i): session.get_piece_label(session.board.piece_at(i)) 
                   for i in range(64) if session.board.piece_at(i)}
    session.last_raw_state = start_state
    session.stable_state = start_state
    session.stability_counter = 5
    
    illegal_state = start_state.copy()
    del illegal_state["e2"]
    illegal_state["e5"] = "wP"
    
    session.last_raw_state = illegal_state
    session.stability_counter = 2
    
    # Should perform Hard Sync because move inference fails
    assert session.process_vision_update(illegal_state) == True
    # FEN should reflect the exact physical state (Piece at e5)
    assert session.board.piece_at(chess.E5) is not None
    assert session.board.piece_at(chess.E2) is None

def test_validate_board(session):
    # Valid starting board
    is_valid, msg = session.validate_board_for_game()
    assert is_valid == True
    
    # Remove white king
    session.board.remove_piece_at(chess.E1)
    is_valid, msg = session.validate_board_for_game()
    assert is_valid == False
    assert "White King" in msg
