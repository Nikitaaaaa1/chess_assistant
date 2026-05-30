from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
import json
import chess
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GLAS")

# Game State Manager
class GameSession:
    def __init__(self):
        self.board = chess.Board()
        self.connections: List[WebSocket] = []
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.connections.append(websocket)
        logger.info(f"New client connected. Total clients: {len(self.connections)}")
        # Send current state on connection
        await self.send_state(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            if websocket in self.connections:
                self.connections.remove(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.connections)}")

    async def send_state(self, websocket: WebSocket):
        payload = {
            "type": "GAME_STATE",
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn == chess.WHITE else "black"
        }
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception as e:
            logger.error(f"Error sending state to client: {e}")

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
                except Exception as e:
                    logger.warning(f"Failed to send to a client, marking for removal: {e}")
                    disconnected.append(connection)
            
            for conn in disconnected:
                if conn in self.connections:
                    self.connections.remove(conn)

session = GameSession()

# Mock Background Task to simulate moves for testing
async def mock_game_loop():
    logger.info("Starting mock game loop...")
    while True: # Keep it running or repeatable
        await asyncio.sleep(10) # Initial delay
        
        test_moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"]
        session.board.reset()
        await session.broadcast_state()
        
        for move_str in test_moves:
            await asyncio.sleep(4)
            try:
                move = chess.Move.from_uci(move_str)
                if move in session.board.legal_moves:
                    session.board.push(move)
                    logger.info(f"Mock Move: {move_str}")
                    await session.broadcast_state()
                else:
                    logger.warning(f"Mock move {move_str} is illegal now.")
            except Exception as e:
                logger.error(f"Error in mock loop move: {e}")
        
        await asyncio.sleep(20) # Wait before restarting loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mock_task = asyncio.create_task(mock_game_loop())
    yield
    # Shutdown
    mock_task.cancel()
    try:
        await mock_task
    except asyncio.CancelledError:
        pass

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
            # We mostly push from server, but need to keep socket alive
            # Wait for data or ping
            data = await websocket.receive_text()
            logger.info(f"Received from client: {data}")
    except WebSocketDisconnect:
        await session.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await session.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
