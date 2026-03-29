# Task: Inter-Service Communication (RabbitMQ)
- **Status**: Pending
- **Date**: 2026-03-22
---
## Description of Work Done
- Shifted the architectural requirement from Redis Pub/Sub to RabbitMQ queues for better service decoupling.
- Defined the communication channel between `AVS` (AI Vision Service) and `GLAS` (Game Logic & API).
- Specified the `pika` library for Python-based message handling.

## Blockers
- AVS and GLAS must align on the JSON schema for the detected board state.
---
## Next Steps
- Implement the RabbitMQ publisher in the AVS service.
- Implement the RabbitMQ consumer and the "difference engine" in GLAS.
