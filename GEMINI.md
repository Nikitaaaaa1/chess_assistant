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
No task shall be marked **Completed** in `task-master` or this file until:
- The work is cross-checked against the original task description.
- Evidence of testing (logs, screenshots, or command output) is provided/verified.
- Documentation and edge cases have been addressed.

### 2. Status Lifecycle
- **Pending:** Task not yet started.
- **In-Progress:** Active development.
- **In Review:** Work claimed finished, awaiting verification.
- **Completed:** Verified and closed.

---

## Progress Log

### 1.1 - 2026-03-22
- **Work Done**: Created service directories; initialized base dependency files.
- **Verification Method**: Manual confirmation of directory structure.
- **Status**: Verified
- **BLOCKERS**: None

### 2.1, 2.2, & 2.3 - 2026-03-22
- **Work Done**: Implemented capture service, perspective warping, interactive calibration, and 64-square grid mapping (algebraic notation). Integrated all into `main.py`.
- **Verification Method**: Automated unit tests (3/3 passed) and visual code inspection of the `GridManager` mapping logic.
- **Status**: Verified
- **BLOCKERS**: None

---

## Project Roadmap (Master Table)

| Task ID | Task Name | Status | Last Updated |
| :--- | :--- | :--- | :--- |
| 1 | Project Setup & Docker Infrastructure | **In-Progress** | 2026-03-22 |
| 2 | AVS - Camera & Calibration | **Completed** | 2026-03-22 |
| 3 | AVS - YOLO & Piece Detection | Pending | 2026-03-22 |

*(Full details in `tasks/master_tasks.md`)*
