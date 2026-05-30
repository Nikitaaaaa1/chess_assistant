from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
import json
import chess
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GLAS")

app = FastAPI(title="Chess Logic API (GLAS)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game State Manager
class GameSession:
    def __init__(self):
        self.board = chess.Board()
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
        # Send current state on connection
        await self.broadcast_state()

    def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def broadcast_state(self):
        payload = {
            "type": "GAME_STATE",
            "fen": self.board.fen(),
            "turn": "white" if self.board.turn == chess.WHITE else "black"
        }
        message = json.dumps(payload)
        for connection in self.connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

session = GameSession()

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
            # Keep connection alive and handle client messages if any
            data = await websocket.receive_text()
            logger.info(f"Received from client: {data}")
    except WebSocketDisconnect:
        session.disconnect(websocket)
        logger.info("Client disconnected")

# Mock Background Task to simulate moves for testing
async def mock_game_loop():
    logger.info("Starting mock game loop...")
    await asyncio.sleep(5) # Wait for UI to settle
    
    # Simple predefined moves to show it's working
    test_moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1b5"]
    
    for move_str in test_moves:
        await asyncio.sleep(3)
        move = chess.Move.from_uci(move_str)
        if move in session.board.legal_moves:
            session.board.push(move)
            logger.info(f"Mock Move: {move_str}")
            await session.broadcast_state()

@app.on_event("startup")
async def startup_event():
    # Start the mock loop in the background
    asyncio.create_task(mock_game_loop())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
