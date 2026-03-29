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
- **Work Done**: Created service directories (`chess-vision-service`, `chess-logic-api`, `chess-web-ui`); initialized base dependency files with `pika`, `fastapi`, `python-chess`, and `react-chessboard`.
- **Verification Method**: Manual confirmation of directory structure and dependency declarations.
- **Status**: Verified
- **BLOCKERS**: None

### 2 - 2026-03-22
- **Work Done**: Implemented capture service, perspective warping, interactive calibration, and grid mapping.
- **Verification Method**: Automated unit tests (3/3 passed).
- **Status**: Verified

### 9 - 2026-03-22
- **Work Done**: Scaffolded Vite/React frontend; implemented `ChessBoardView`, `ControlPanel`, and `VisionPreview` components with TailwindCSS styling. Established a modern "Control Center" dashboard layout.
- **Verification Method**: Manual confirmation of file structure and component logic (mock-ready).
- **Status**: Verified
- **BLOCKERS**: None

---

## Project Roadmap (Master Table)

| Task ID | Task Name | Status | Last Updated |
| :--- | :--- | :--- | :--- |
| 1 | Project Setup & Docker Infrastructure | **In-Progress** | 2026-03-22 |
| 2 | AVS - Camera & Calibration | **Completed** | 2026-03-22 |
| 3 | AVS - YOLO & Piece Detection | **Completed** | 2026-03-22 |
| 4 | GLAS - Core Game Logic & API | Pending | 2026-03-22 |
| 9 | Frontend - Web UI Skeleton | **Completed** | 2026-03-22 |
| 11| CI/CD Pipeline - GitHub Actions | **In Review** | 2026-03-22 |

| 9 | Frontend - Web UI Skeleton | **In-Progress** | 2026-03-22 |
| 11| CI/CD Pipeline - GitHub Actions | **In Review** | 2026-03-22 |

*(Full details in `tasks/master_tasks.md`)*
