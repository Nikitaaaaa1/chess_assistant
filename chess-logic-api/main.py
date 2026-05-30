from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
import json
import chess
import pika
import os
import threading
import time
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GLAS")

# Game State Manager with Difference Engine
class GameSession:
    def __init__(self):
        self.board = chess.Board()
        self.connections: List[WebSocket] = []
        self.lock = asyncio.Lock()
        
        # Tracking for Difference Engine
        self.last_raw_state = {}
        self.stable_state = {}
        self.stability_counter = 0
        self.STABILITY_THRESHOLD = 3 # Number of identical frames to confirm state

    async def connect(self, websocket: WebSocket):
        async with self.lock:
            self.connections.append(websocket)
        logger.info(f"UI client registered. Total: {len(self.connections)}")
        await self.send_state(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            if websocket in self.connections:
                self.connections.remove(websocket)
        logger.info(f"UI client disconnected. Total: {len(self.connections)}")

    async def send_state(self, websocket: WebSocket):
        is_valid, validation_msg = self.validate_board_for_game()
        payload = {
            "type": "GAME_STATE",
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn == chess.WHITE else "black",
            "is_valid": is_valid,
            "validation_msg": validation_msg
        }
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception as e:
            logger.error(f"Failed to send state: {e}")

    def validate_board_for_game(self):
        fen = self.board.fen()
        if 'K' not in fen: return False, "Missing White King"
        if 'k' not in fen: return False, "Missing Black King"
        return True, "Valid"

    async def broadcast_state(self):
        is_valid, validation_msg = self.validate_board_for_game()
        payload = {
            "type": "GAME_STATE",
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn == chess.WHITE else "black",
            "is_valid": is_valid,
            "validation_msg": validation_msg
        }
        message = json.dumps(payload)
        async with self.lock:
            disconnected = []
            for connection in self.connections:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            for conn in disconnected:
                if conn in self.connections:
                    self.connections.remove(conn)

    def process_vision_update(self, fused_state: Dict[str, str]):
        """
        Difference Engine: Analyzes changes between physical and virtual boards.
        """
        # 1. Noise filtering
        if fused_state == self.last_raw_state:
            self.stability_counter += 1
        else:
            self.last_raw_state = fused_state
            self.stability_counter = 0
            return False # State not stable yet

        if self.stability_counter < self.STABILITY_THRESHOLD:
            return False
            
        # 2. Check if anything actually changed from our confirmed stable state
        if fused_state == self.stable_state:
            return False
            
        logger.info(f"Stable Vision Update: {len(fused_state)} pieces detected.")
        
        # 3. Infer Move or Hard Sync
        # For development/mocking, we allow "Radical Change" detection
        diff_count = self.calculate_difference(fused_state)
        
        if diff_count > 4: # Too many changes at once, likely a new game or huge jump
            logger.info("Radical change detected. Performing Hard Sync.")
            self.hard_sync(fused_state)
        elif diff_count > 0:
            logger.info(f"Minor change detected ({diff_count} squares). Attempting move inference.")
            if not self.infer_move(fused_state):
                logger.warning("Could not infer a legal move. Forcing sync.")
                self.hard_sync(fused_state)
        
        self.stable_state = fused_state
        return True

    def calculate_difference(self, physical_state):
        """Counts squares that differ between current board and vision."""
        diffs = 0
        # Check all 64 squares
        for i in range(64):
            sq_name = chess.square_name(i)
            piece = self.board.piece_at(i)
            virt_label = self.get_piece_label(piece) if piece else None
            phys_label = physical_state.get(sq_name)
            
            if virt_label != phys_label:
                diffs += 1
        return diffs

    def infer_move(self, physical_state):
        """
        Tries to find a legal move that transitions board to physical_state.
        Simple logic: Look for one square that became empty and one that became occupied.
        """
        vacated = [] # (sq_index, piece_label)
        occupied = [] # (sq_index, piece_label)
        
        for i in range(64):
            sq_name = chess.square_name(i)
            virt_p = self.board.piece_at(i)
            virt_l = self.get_piece_label(virt_p) if virt_p else None
            phys_l = physical_state.get(sq_name)
            
            if virt_l and not phys_l:
                vacated.append((i, virt_l))
            elif phys_l and virt_l != phys_l:
                occupied.append((i, phys_l))
                
        # Case 1: Simple Move or Capture (1 vacated, 1 occupied)
        if len(vacated) == 1 and len(occupied) == 1:
            from_sq = vacated[0][0]
            to_sq = occupied[0][0]
            move = chess.Move(from_sq, to_sq)
            
            # Check for promotion (simplification: always queen for now)
            if self.board.piece_at(from_sq).piece_type == chess.PAWN:
                if (chess.square_rank(to_sq) == 7 and self.board.turn == chess.WHITE) or \
                   (chess.square_rank(to_sq) == 0 and self.board.turn == chess.BLACK):
                    move.promotion = chess.QUEEN

            if move in self.board.legal_moves:
                self.board.push(move)
                logger.info(f"Inferred Move: {move.uci()}")
                return True
                
        # Case 2: Castling (usually 2 vacated, 2 occupied)
        # TODO: Implement castling detection
        
        return False

    def hard_sync(self, fused_state):
        """Forces the virtual board to match the physical detection exactly."""
        new_board = chess.Board(None) 
        piece_map = {
            "wP": chess.PAWN, "wN": chess.KNIGHT, "wB": chess.BISHOP, 
            "wR": chess.ROOK, "wQ": chess.QUEEN, "wK": chess.KING,
            "bP": chess.PAWN, "bN": chess.KNIGHT, "bB": chess.BISHOP, 
            "bR": chess.ROOK, "bQ": chess.QUEEN, "bK": chess.KING
        }
        for sq_name, label in fused_state.items():
            try:
                sq_idx = chess.parse_square(sq_name)
                color = chess.WHITE if label.startswith('w') else chess.BLACK
                p_type = piece_map.get(label)
                if p_type:
                    new_board.set_piece_at(sq_idx, chess.Piece(p_type, color))
            except: pass
        self.board = new_board

    def get_piece_label(self, piece: chess.Piece):
        color_prefix = 'w' if piece.color == chess.WHITE else 'b'
        type_map = {
            chess.PAWN: 'P', chess.KNIGHT: 'N', chess.BISHOP: 'B',
            chess.ROOK: 'R', chess.QUEEN: 'Q', chess.KING: 'K'
        }
        return f"{color_prefix}{type_map[piece.piece_type]}"

session = GameSession()

# RabbitMQ Consumer
def start_rabbitmq_consumer(loop):
    host = os.environ.get('RABBITMQ_HOST', 'rabbitmq-broker')
    queue = 'board_state_queue'
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, heartbeat=600))
            channel = connection.channel()
            channel.queue_declare(queue=queue)
            def callback(ch, method, properties, body):
                try:
                    fused_state = json.loads(body)
                    asyncio.run_coroutine_threadsafe(handle_vision_update(fused_state), loop)
                except Exception as e:
                    logger.error(f"Error in callback: {e}")
            channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
            logger.info("GLAS consuming from RabbitMQ")
            channel.start_consuming()
        except Exception as e:
            logger.error(f"RabbitMQ lost: {e}")
            time.sleep(5)

async def handle_vision_update(fused_state):
    if session.process_vision_update(fused_state):
        await session.broadcast_state()

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()
    threading.Thread(target=start_rabbitmq_consumer, args=(loop,), daemon=True).start()
    yield

app = FastAPI(title="Chess Logic API (GLAS)", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root(): return {"status": "ok"}

@app.get("/health")
async def health(): return {"status": "healthy"}

@app.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await session.connect(websocket)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect: await session.disconnect(websocket)
    except Exception as e:
        logger.error(f"WS error: {e}")
        await session.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
