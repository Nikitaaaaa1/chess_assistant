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
from typing import List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GLAS")

# Game State Manager
class GameSession:
    def __init__(self):
        self.board = chess.Board()
        self.connections: List[WebSocket] = []
        self.lock = asyncio.Lock()
        self.last_physical_state = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.connections.append(websocket)
        logger.info(f"New UI client connected. Total: {len(self.connections)}")
        await self.send_state(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            if websocket in self.connections:
                self.connections.remove(websocket)
        logger.info(f"UI client disconnected. Total: {len(self.connections)}")

    async def send_state(self, websocket: WebSocket):
        payload = {
            "type": "GAME_STATE",
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn == chess.WHITE else "black"
        }
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception as e:
            logger.error(f"Error sending state to UI: {e}")

    async def broadcast_state(self):
        payload = {
            "type": "GAME_STATE",
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn == chess.WHITE else "black"
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

    def process_vision_update(self, fused_state):
        """
        Updates the virtual board state based on AVS detections.
        Currently implements a 'Hard Sync' for testing.
        """
        if fused_state == self.last_physical_state:
            return
        
        logger.info(f"Processing Vision Update: {len(fused_state)} pieces detected.")
        
        # Hard Sync logic (for development): 
        # Rebuild board from detection results.
        # Mapping: 'e2' -> 'wP' (white Pawn)
        
        new_board = chess.Board(None) # Empty board
        
        piece_map = {
            "wP": chess.PAWN, "wN": chess.KNIGHT, "wB": chess.BISHOP, 
            "wR": chess.ROOK, "wQ": chess.QUEEN, "wK": chess.KING,
            "bP": chess.PAWN, "bN": chess.KNIGHT, "bB": chess.BISHOP, 
            "bR": chess.ROOK, "bQ": chess.QUEEN, "bK": chess.KING
        }
        
        for square_name, piece_label in fused_state.items():
            try:
                square_index = chess.parse_square(square_name)
                color = chess.WHITE if piece_label.startswith('w') else chess.BLACK
                piece_type = piece_map.get(piece_label)
                if piece_type:
                    new_board.set_piece_at(square_index, chess.Piece(piece_type, color))
            except Exception as e:
                logger.warning(f"Failed to set piece {piece_label} at {square_name}: {e}")

        # Basic validation: If the board is valid enough, update the active session
        # For mock-mode development, we'll just force the FEN.
        self.board = new_board
        self.last_physical_state = fused_state
        logger.info(f"Board synced. New FEN: {self.board.fen()}")

session = GameSession()

# RabbitMQ Consumer
def start_rabbitmq_consumer(loop):
    host = os.environ.get('RABBITMQ_HOST', 'rabbitmq-broker')
    queue = 'board_state_queue'
    
    while True:
        try:
            logger.info(f"Connecting to RabbitMQ at {host}...")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, heartbeat=600))
            channel = connection.channel()
            channel.queue_declare(queue=queue)
            
            def callback(ch, method, properties, body):
                try:
                    fused_state = json.loads(body)
                    asyncio.run_coroutine_threadsafe(handle_vision_update(fused_state), loop)
                except Exception as e:
                    logger.error(f"Error in RabbitMQ callback: {e}")

            channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
            logger.info("GLAS successfully consuming from board_state_queue")
            channel.start_consuming()
        except Exception as e:
            logger.error(f"RabbitMQ connection lost, retrying in 5s: {e}")
            time.sleep(5)

async def handle_vision_update(fused_state):
    session.process_vision_update(fused_state)
    await session.broadcast_state()

@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()
    consumer_thread = threading.Thread(target=start_rabbitmq_consumer, args=(loop,), daemon=True)
    consumer_thread.start()
    yield

app = FastAPI(title="Chess Logic API (GLAS)", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Chess Logic API is running", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.websocket("/ws/game")
async def websocket_endpoint(websocket: WebSocket):
    await session.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await session.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await session.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
