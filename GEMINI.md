# GEMINI.md - Project Context: Chess Assistant System

## Project Overview
The **Real-Time AI Chess Tracking & Assistant System** is a Raspberry Pi-based platform designed to track physical chess games in real-time using dual cameras.

### Architecture (Microservices)
1.  **AI Vision Service (AVS):** Python 3.11, OpenCV, YOLO, RabbitMQ.
2.  **Game Logic & API Service (GLAS):** FastAPI, `python-chess`, Stockfish 16.
3.  **Frontend UI:** React.js, TailwindCSS, `react-chessboard`.
4.  **Message Broker:** RabbitMQ (3-management-alpine).

---

## Senior Project Controller & QA Mandate

### 1. The "Verification First" Rule
No task shall be marked **Completed** in `task-master` or this file until work is cross-checked and testing evidence is provided.

### 2. Status Lifecycle
- **Pending / In-Progress / In Review / Completed**

---

## Progress Log

### 1.1 - 2026-03-22
- **Work Done**: Created service directories; initialized base dependency files.
- **Verification Method**: Manual confirmation of directory structure.
- **Status**: Verified

### 2 - 2026-03-22
- **Work Done**: Implemented capture service, perspective warping, interactive calibration, and grid mapping.
- **Verification Method**: Automated unit tests (3/3 passed).
- **Status**: Verified

### 3 - 2026-03-22
- **Work Done**: Implemented `PieceDetector` (YOLOv8) and `FusionManager` (dual-camera merger); integrated into AVS core loop.
- **Verification Method**: Automated unit tests for fusion logic (3/3 passed); modular logic review.
- **Status**: Verified
- **BLOCKERS**: None

---

## Project Roadmap (Master Table)

| Task ID | Task Name | Status | Last Updated |
| :--- | :--- | :--- | :--- |
| 1 | Project Setup & Docker Infrastructure | **In-Progress** | 2026-03-22 |
| 2 | AVS - Camera & Calibration | **Completed** | 2026-03-22 |
| 3 | AVS - YOLO & Piece Detection | **Completed** | 2026-03-22 |
| 4 | GLAS - Core Game Logic & API | **In-Progress** | 2026-03-22 |

*(Full details in `tasks/master_tasks.md`)*
