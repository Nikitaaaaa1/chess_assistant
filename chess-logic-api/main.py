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
from typing import List

logging.basicConfig(level=logging.INFO)
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
        logger.info(f"New client connected. Total clients: {len(self.connections)}")
        await self.send_state(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            if websocket in self.connections:
                self.connections.remove(websocket)

    async def send_state(self, websocket: WebSocket):
        payload = {
            "type": "GAME_STATE",
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn == chess.WHITE else "black"
        }
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception as e:
            logger.error(f"Error sending state: {e}")

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
        Compares physical state from AVS with current virtual state.
        Infers moves if possible.
        """
        # For now, to ensure UI updates during testing, we'll log the detection
        # and try to find a move that matches the change.
        if fused_state == self.last_physical_state:
            return
        
        logger.info(f"Vision Update Received: {len(fused_state)} pieces detected.")
        
        # Simple move inference logic (Draft):
        # 1. Identify which squares changed.
        # 2. If a piece disappeared from A and appeared on B, it's a move A->B.
        # This is a placeholder for a more robust difference engine.
        
        # For THIS mock-to-real transition, we will just SYNC the board if it's vastly different
        # or if we are in "setup" mode.
        # But per user request: "recognition based on mock data", we want to see the pieces.
        
        # Let's try to find a legal move that results in the state seen by vision.
        # If no single move matches, we might need manual sync.
        
        self.last_physical_state = fused_state
        # For testing purposes: Just log and broadcast current FEN
        # (Real move inference will be Task 5.2)

session = GameSession()

# RabbitMQ Consumer
def start_rabbitmq_consumer(loop):
    host = os.environ.get('RABBITMQ_HOST', 'rabbitmq-broker')
    queue = 'board_state_queue'
    
    def callback(ch, method, properties, body):
        try:
            fused_state = json.loads(body)
            # Use thread-safe way to call async method
            asyncio.run_coroutine_threadsafe(handle_vision_update(fused_state), loop)
        except Exception as e:
            logger.error(f"Error in RabbitMQ callback: {e}")

    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
            channel = connection.channel()
            channel.queue_declare(queue=queue)
            channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
            logger.info(f"GLAS consuming from RabbitMQ at {host}")
            channel.start_consuming()
        except Exception as e:
            logger.error(f"RabbitMQ connection failed, retrying in 5s: {e}")
            time.sleep(5)

async def handle_vision_update(fused_state):
    session.process_vision_update(fused_state)
    await session.broadcast_state()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    loop = asyncio.get_running_loop()
    consumer_thread = threading.Thread(target=start_rabbitmq_consumer, args=(loop,), daemon=True)
    consumer_thread.start()
    yield
    # Shutdown logic if any

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
    import time
    uvicorn.run(app, host="0.0.0.0", port=8000)
