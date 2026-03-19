# PersonaTalk

PersonaTalk is a local-first single-user web app for chatting with saved AI personas by text or voice. It ships with a FastAPI backend, React/TypeScript frontend, SQLite persistence, and provider adapters so the LLM, STT, and TTS layers can be swapped later.

## MVP features

- Persona CRUD with reusable presets
- Conversation history with local persistence and search
- Text chat, push-to-talk voice flow, and mixed-mode threads
- Editable persona prompt, temperature, and voice preference during a conversation
- SQLite snapshots so old chats keep their original persona configuration
- Local run support via Python venv or Docker Compose

## Project structure

- `backend/app/api`: REST endpoints
- `backend/app/services`: orchestration logic
- `backend/app/providers`: LLM, STT, and TTS adapters
- `backend/app/repositories`: SQLite access
- `backend/app/schemas`: typed API contracts
- `frontend/src`: React SPA

## Quick start with Python + Node

1. Create and activate a virtual environment.
2. Install backend dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env`.
4. Install the local speech runtime:

```powershell
pip install -r requirements-local-cpu.txt
```

This installs local `faster-whisper` STT and local Kokoro TTS.
5. Start the backend:

```powershell
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

6. In a second terminal, install frontend dependencies and run Vite:

```powershell
cd frontend
npm install
npm run dev
```

7. Open [http://localhost:5173](http://localhost:5173).

## Quick start with Docker Compose

1. Copy `.env.example` to `.env`.
2. Run:

```powershell
docker compose up --build
```

3. Open [http://localhost:5173](http://localhost:5173).

## Provider notes

- `LLM_PROVIDER=openai` calls `gpt-4o-mini`.
- `STT_PROVIDER=whisper` uses local `faster-whisper` on your machine.
- `STT_MODEL` can be `tiny`, `base`, `small`, and so on. `base` is a good default for CPU.
- `WHISPER_COMPUTE_TYPE=int8` is a good CPU-friendly default.
- `WHISPER_CPU_THREADS` controls local transcription threading.
- `STT_TIMEOUT_SECONDS` controls how long a voice transcription request is allowed to run before the API returns an error instead of hanging.
- `TTS_PROVIDER=kokoro` uses `pykokoro` and writes generated WAV files into the local audio cache.
- If you want a no-dependency demo mode, switch providers back to `mock`.

## Core API paths

- `GET/POST/PUT/DELETE /api/personas`
- `GET/POST/PUT/DELETE /api/conversations`
- `GET /api/conversations/{id}/messages`
- `POST /api/messages`
- `POST /api/voice/{conversation_id}`
- `GET /api/audio/{filename}`

## Notes

- The app is intentionally single-user and local-first.
- Authentication, billing, streaming tokens/audio, uploads, and multi-user sync are out of scope for this MVP.
- The recommended local voice stack in this repo is `faster-whisper` for STT plus Kokoro for TTS.
