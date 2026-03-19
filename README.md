# PersonaTalk

PersonaTalk is a local-first single-user web app for chatting with saved AI personas by text or voice. It combines a FastAPI backend, a React/TypeScript frontend, SQLite persistence, local speech tooling, and multiple LLM provider options so you can choose between cloud and fully local setups.

## What You Can Do

- Create, save, edit, reuse, and delete personas
- Start and continue conversations with saved history
- Search conversations by title or message text
- Chat by text, voice, or mixed mode in the same thread
- Choose the active LLM per conversation:
  - `GPT-4o mini`
  - `LM Studio Local`
  - `Local GGUF`
- Choose the microphone from the UI
- Generate assistant audio replies locally with Kokoro
- Run a mostly or fully local setup, depending on your preferred LLM provider

## Stack

### Frontend

- React
- TypeScript
- Vite

### Backend

- FastAPI
- SQLite
- Provider adapters for:
  - OpenAI
  - LM Studio local server
  - direct GGUF via `llama-cpp-python`
  - local Whisper STT via `faster-whisper`
  - local Kokoro TTS via `pykokoro`

## Project Structure

- `backend/app/api`: REST endpoints
- `backend/app/services`: orchestration logic
- `backend/app/providers`: LLM, STT, and TTS adapters
- `backend/app/repositories`: SQLite access
- `backend/app/schemas`: typed request and response contracts
- `frontend/src`: React SPA

## Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install backend dependencies

Base backend:

```powershell
pip install -r requirements.txt
```

Local speech stack:

```powershell
pip install -r requirements-local-cpu.txt
```

Optional direct GGUF LLM stack:

```powershell
pip install -r requirements-local-llm.txt
```

### 3. Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

### 4. Copy environment config

```powershell
Copy-Item .env.example .env
```

### 5. Start the backend

```powershell
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start the frontend

```powershell
cd frontend
npm run dev
```

### 7. Open the app

[http://localhost:5173](http://localhost:5173)

## LLM Provider Options

PersonaTalk now supports three conversation-time LLM choices from the UI.

### Option 1: OpenAI

Use this when you want the fastest and smoothest UX.

`.env`:

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_key_here
```

Notes:

- This is cloud-hosted, not local
- The UI can still switch to another provider per conversation

### Option 2: LM Studio Local

Use this when you want a local model with GPU acceleration through LM Studio.

LM Studio should expose its OpenAI-compatible local server first.

`.env`:

```env
LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
LM_STUDIO_MODEL=meta-llama-3.1-8b-instruct
```

Notes:

- This is usually the best local-performance option on a laptop with GPU
- PersonaTalk talks to LM Studio through its OpenAI-compatible API
- You can select `LM Studio Local` from the right panel

### Option 3: Local GGUF via llama.cpp

Use this when you want PersonaTalk itself to load a GGUF file directly.

Example `.env`:

```env
LLM_PROVIDER=llama_cpp
LLM_MODEL=meta-llama-3.1-8b-instruct
LOCAL_LLM_MODEL_PATH=E:\path\to\model.gguf
LOCAL_LLM_CHAT_FORMAT=
LOCAL_LLM_N_CTX=8192
LOCAL_LLM_N_THREADS=6
LOCAL_LLM_N_GPU_LAYERS=0
LOCAL_LLM_MAX_TOKENS=512
```

Notes:

- This works fully locally
- On this project’s current setup, direct GGUF is still CPU-first unless `llama-cpp-python` is rebuilt with GPU support
- For many Windows laptop setups, LM Studio is the easier way to get local GPU acceleration

## Speech Provider Options

### STT

PersonaTalk uses local Whisper transcription through `faster-whisper`.

`.env`:

```env
STT_PROVIDER=whisper
STT_MODEL=base
WHISPER_COMPUTE_TYPE=int8
WHISPER_CPU_THREADS=4
STT_TIMEOUT_SECONDS=180
```

Notes:

- `tiny` is faster but lower quality
- `base` is a good CPU default

### TTS

PersonaTalk uses local Kokoro TTS.

`.env`:

```env
TTS_PROVIDER=kokoro
TTS_MODEL=kokoro-82m
KOKORO_PROVIDER=auto
KOKORO_VOICE_MALE=am_michael
KOKORO_VOICE_FEMALE=af_sarah
KOKORO_LANG=en-us
KOKORO_SPEED=1.0
```

Notes:

- Assistant audio is saved to the local audio cache
- The app stores transcript text in the conversation history

## Important Environment Variables

### OpenAI

- `OPENAI_API_KEY`
- `LLM_PROVIDER`
- `LLM_MODEL`

### LM Studio

- `LM_STUDIO_BASE_URL`
- `LM_STUDIO_MODEL`

### Direct GGUF

- `LOCAL_LLM_MODEL_PATH`
- `LOCAL_LLM_CHAT_FORMAT`
- `LOCAL_LLM_N_CTX`
- `LOCAL_LLM_N_THREADS`
- `LOCAL_LLM_N_GPU_LAYERS`
- `LOCAL_LLM_MAX_TOKENS`

### Whisper STT

- `STT_PROVIDER`
- `STT_MODEL`
- `WHISPER_COMPUTE_TYPE`
- `WHISPER_CPU_THREADS`
- `STT_TIMEOUT_SECONDS`

### Kokoro TTS

- `TTS_PROVIDER`
- `TTS_MODEL`
- `KOKORO_PROVIDER`
- `KOKORO_VOICE_MALE`
- `KOKORO_VOICE_FEMALE`
- `KOKORO_LANG`
- `KOKORO_SPEED`

## Conversation Behavior

- Each conversation stores its persona snapshot
- Each conversation also stores its selected LLM provider
- Continuing a conversation restores its previous model choice
- Editing the right panel affects future turns, not old ones
- Deleting a persona does not break old chats because the conversation keeps a prompt snapshot

## UI Notes

- Left panel:
  - conversation list
  - search
  - new chat
- Center panel:
  - active thread
  - text composer
  - push-to-talk
  - mic selector
  - model badge in the header
- Right panel:
  - persona presets
  - persona editor
  - temperature
  - voice preference
  - model selector

## API Summary

- `GET/POST/PUT/DELETE /api/personas`
- `GET/POST/PUT/DELETE /api/conversations`
- `GET /api/conversations/{id}/messages`
- `POST /api/messages`
- `POST /api/voice/{conversation_id}`
- `GET /api/audio/{filename}`

## Docker

Basic Docker files are included:

- `Dockerfile.backend`
- `Dockerfile.frontend`
- `docker-compose.yml`

Run:

```powershell
docker compose up --build
```

Note:

- Docker support is scaffolded, but local speech and local model stacks are easiest to manage directly on the host machine during MVP development

## Known Practical Notes

- `206 Partial Content` logs on audio files are normal browser playback behavior
- LM Studio is typically the simplest route for local GPU-accelerated LLM usage on Windows
- Direct `llama-cpp-python` GPU acceleration may require a CUDA-enabled install, depending on your environment
- If an API key was exposed during development, rotate it before continued use

## Recommended Modes

### Best speed

- `GPT-4o mini` + local Whisper + local Kokoro

### Best local GPU experience

- `LM Studio Local` + local Whisper + local Kokoro

### Most self-contained inside PersonaTalk

- `Local GGUF` + local Whisper + local Kokoro
