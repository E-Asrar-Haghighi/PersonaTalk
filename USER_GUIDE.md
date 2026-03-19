# PersonaTalk User Guide

## What PersonaTalk Is

PersonaTalk is a local-first app for talking with saved personas using text, voice, or both in the same conversation. You can choose which model powers each conversation, save past chats, and keep using the same persona setup later.

## Main Layout

### Left panel

- View saved conversations
- Search chats by title or message text
- Start a new chat
- Delete old chats

### Center panel

- Read the active conversation
- Type messages
- Use push-to-talk for voice input
- Choose which microphone to use
- See the active model badge in the chat header

### Right panel

- Select a saved persona
- Edit persona name and prompt
- Adjust temperature
- Choose assistant voice
- Choose the active model provider

## Choosing a Model

PersonaTalk lets you choose the model per conversation.

### GPT-4o mini

Use this when you want the fastest and smoothest response quality.

- Requires an OpenAI API key
- Cloud-based, not local

### LM Studio Local

Use this when you want a local model and already have LM Studio serving a model on your machine.

- Fully local inference through LM Studio
- Usually the best local-performance choice on a GPU laptop

### Local GGUF

Use this when you want PersonaTalk itself to load a local GGUF model directly.

- Fully local
- Can be slower than LM Studio depending on your machine and install

## Starting a Chat

1. Pick or create a persona in the right panel.
2. Pick the model you want that conversation to use.
3. Click `New chat`.
4. Type a message or use the voice button.

## Persona Settings

Each persona includes:

- Name
- System prompt
- Temperature
- Voice preference

Important behavior:

- The conversation stores a snapshot of the persona settings used at the time
- If you edit the saved persona later, old conversations still keep their original snapshot

## Switching Models

You can switch between:

- `GPT-4o mini`
- `LM Studio Local`
- `Local GGUF`

The selected model:

- is shown in the center header badge
- is saved with the conversation
- is restored when you reopen that chat

## Voice Chat

### Input

- Click `Push to talk` to start recording
- Click again to stop and send
- The selected microphone from the dropdown is used
- Your voice is transcribed into text and stored in the conversation

### Output

- The assistant reply appears as text
- The app also tries to generate local audio with Kokoro
- Audio replies appear with a built-in player in the chat

## Microphone Selection

PersonaTalk includes a microphone selector in the composer area.

- Pick your external mic or laptop mic
- Click `Refresh mics` if you plugged a device in after opening the app
- Your selected mic is remembered across reloads

## Conversation History

You can:

- reopen old chats
- search them
- continue them
- delete them

When you reopen a conversation, PersonaTalk restores:

- the persona snapshot
- the temperature
- the voice preference
- the model choice

## Recommended Ways To Use It

### Fastest setup

- `GPT-4o mini`
- local Whisper STT
- local Kokoro TTS

### Best local GPU workflow

- `LM Studio Local`
- local Whisper STT
- local Kokoro TTS

### Most self-contained

- `Local GGUF`
- local Whisper STT
- local Kokoro TTS

## If Something Is Slow

### Local GGUF feels slow

That is normal if it is running CPU-first. LM Studio is often faster for local GPU usage on Windows laptops.

### Voice transcription feels slow

Try:

- a smaller Whisper model
- shorter recordings
- less background CPU load

### TTS fails

Check that your Python environment includes the Kokoro dependencies and restart the backend.

## If Something Is Not Working

### OpenAI replies fail

Check:

- `OPENAI_API_KEY`
- `LLM_PROVIDER`
- internet access

### LM Studio replies fail

Check:

- LM Studio is running
- its local server is enabled
- the model is loaded
- `LM_STUDIO_BASE_URL` matches your LM Studio server

### Local GGUF replies fail

Check:

- `LOCAL_LLM_MODEL_PATH`
- the GGUF file exists
- the model can fit in your current memory budget

### Microphone list is empty

Check:

- browser microphone permission
- OS microphone permission
- whether the device appears after clicking `Refresh mics`

## Good Defaults

For most users:

- Model: `GPT-4o mini` or `LM Studio Local`
- STT: Whisper `base`
- TTS: Kokoro default voices
- Temperature: `0.7`

## Final Notes

- Old chats preserve their original persona snapshot
- The selected mic and selected model are remembered across reloads
- Audio playback logs with `206 Partial Content` are normal browser behavior
