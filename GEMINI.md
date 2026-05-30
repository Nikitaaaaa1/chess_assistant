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

### 3. Contextual Branching & Task Order
- If a user request addresses a task out of the current roadmap sequence or is unrelated to the active focus, the agent **MUST** propose creating a new branch.
- New branches **MUST** be created from the **`develop`** branch (not `main`).
- Branch names **MUST** follow [Conventional Branch](https://conventional-branch.github.io/) standards: `<type>/<description>`.
- Refer to `docs/skills/contextual-branching.md` for full guidelines.

### 4. PR & Merge Policy (STRICT)
- **NO automatic Pull Requests**: The agent must ask for explicit confirmation before creating a PR.
- **NO automatic Merges**: The agent is STRICTLY FORBIDDEN from merging into the `main` branch. 
- All integrations into `develop` or `main` require direct user instructions.

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
- **Work Done**: Implemented `PieceDetector` (YOLOv8) and `FusionManager` (multi-camera merger); integrated into AVS core loop. Added support for 1, 2, and 4 camera configurations.
- **Verification Method**: Automated unit tests for fusion logic (3/3 passed); modular logic review for multi-camera scalability.
- **Status**: Verified

### 12 - 2026-05-30
- **Work Done**: Implemented Mock Capture Mode in AVS, supporting looped videos and image folders for offline development.
- **Verification Method**: Automated unit tests for video looping and directory ingestion (`test_mock_capture.py`).
- **Status**: Verified

### 5 - 2026-05-30
- **Work Done**: Established real-time data flow between AVS and GLAS using RabbitMQ. Implemented MJPEG streaming in AVS for frontend visual feedback.
- **Verification Method**: Manual verification of MJPEG stream in UI and state updates via RabbitMQ logs.
- **Status**: In-Progress

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
| 4 | GLAS - Core Game Logic & API | **In-Progress** | 2026-03-22 |
| 9 | Frontend - Web UI Skeleton | **Completed** | 2026-03-22 |
| 11| CI/CD Pipeline - GitHub Actions | **In Review** | 2026-03-22 |

*(Full details in `tasks/master_tasks.md`)*
