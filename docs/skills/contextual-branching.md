# Contextual Branching Skill

## Overview
This skill guides the agent on how to handle requests that deviate from the current task sequence or address different parts of the project roadmap.

## Instructions

### 1. Detection
Monitor user requests for:
- Tasks that are currently marked as **Pending** or **Deferred** while another task is **In-Progress**.
- Requests that jump ahead in the roadmap (e.g., asking for Task 11 while Task 5 is not started).
- Requests for features or bug fixes unrelated to the current scope.

### 2. Proactive Suggestion
When such a request is detected, the agent MUST:
- Acknowledge the request.
- Point out that it belongs to a different task or is out of the current sequence.
- **Propose creating a new feature branch** to keep the work isolated.
- **IMPORTANT**: Always use the **`develop`** branch as the base for new branches.

### 3. Branch Naming Convention
Follow [Conventional Branch](https://conventional-branch.github.io/) standards:
Format: `<type>/<description-in-kebab-case>`

**Allowed Types:**
- `feat`: New features.
- `fix`: Bug fixes.
- `docs`: Documentation changes.
- `style`: Formatting, missing semi colons, etc; no code change.
- `refactor`: Refactoring production code.
- `test`: Adding missing tests, refactoring tests; no production code change.
- `chore`: Updating grunt tasks etc; no production code change.
- `perf`: Code change that improves performance.
- `ci`: Changes to CI configuration files and scripts.
- `build`: Changes that affect the build system or external dependencies.
- `revert`: Reverts a previous commit.

**Examples:**
- `feat/rabbitmq-consumer`
- `fix/camera-stream-lag`
- `docs/api-reference`
- `refactor/vision-core-loop`
