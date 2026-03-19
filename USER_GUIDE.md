# PersonaTalk User Guide

## What PersonaTalk Does

PersonaTalk lets you talk with saved personas using text, voice, or mixed mode in the same conversation. You can choose the model for each conversation, save past chats, search them later, and keep using the same persona setup over time.

## Main Layout

### Left panel

- Start a new chat
- Browse saved conversations
- Search by title or message text
- Rename a conversation title
- Delete old chats

### Center panel

- Read the active conversation
- Type a message
- Switch between `text`, `voice`, and `mixed`
- Choose the microphone
- Enable microphone access so the real microphone names appear
- Use `Push to talk`
- See the active model badge in the header
- Listen to assistant audio replies when available
- Edit the latest user message or transcript and regenerate the reply

### Right panel

- Choose a saved persona
- Edit the persona name
- Edit the system prompt
- Change temperature
- Choose male or female assistant voice
- Choose the active model provider

## Models

PersonaTalk supports three model paths.

### GPT-4o mini

- fastest and smoothest in most cases
- uses OpenAI
- requires a valid API key

### LM Studio Local

- fully local through LM Studio
- usually the best local-performance option if your LM Studio model already uses your GPU
- requires LM Studio's local server to be running

### Local GGUF

- fully local inside PersonaTalk
- uses a GGUF file directly
- often slower than LM Studio on Windows if it is running CPU-first

## Starting a Conversation

1. Pick a persona on the right.
2. Pick the model you want.
3. Click `New chat`.
4. Choose `text`, `voice`, or `mixed`.
5. Send a message.

## Personas

Each persona includes:

- name
- system prompt
- temperature
- voice preference

Important behavior:

- each conversation stores a snapshot of the persona settings used for that chat
- changing the saved persona later does not rewrite old conversations

## Voice Input

- Click `Push to talk` to start recording
- Click again to stop and send
- The selected microphone from the dropdown is used
- Voice is transcribed into text and saved in the conversation
- Before the first recording, you can enable microphone access so the dropdown shows the real device names instead of generic labels

## Voice Output

- In `voice` and `mixed` mode, the assistant reply appears as text first
- Kokoro then generates the spoken reply in the background
- When the audio is ready, the player appears on that latest assistant message
- If voice generation fails, the text reply still stays in the chat

## Microphone Selection

- Use the microphone dropdown above the composer actions
- The app cleans up raw browser microphone labels into friendlier names where possible
- Click `Refresh mics` if you plug in a device after opening the app
- The selected microphone is remembered across reloads

## Model Selection

- Choose the model from the right panel
- The current choice is shown in the chat header badge
- The selected model is saved with that conversation
- Reopening the chat restores the same model choice

## Conversation History

You can:

- reopen chats
- continue them
- search them
- rename them
- delete them

When you reopen a conversation, PersonaTalk restores:

- persona snapshot
- temperature
- voice preference
- model choice
- mode

## Editing the Latest Message

- The newest user message in a conversation can be edited
- If it was a voice-origin message, the UI shows `Edit transcript`
- If it was a typed message, the UI shows `Edit last message`
- Saving the edit removes the later reply and regenerates the assistant response in the same thread

## Good Defaults

### Fastest normal use

- model: `GPT-4o mini`
- STT: Whisper `base`
- TTS: Kokoro
- mode: `text` or `mixed`

### Best local GPU workflow

- model: `LM Studio Local`
- STT: Whisper `base`
- TTS: Kokoro

### Most self-contained local stack

- model: `Local GGUF`
- STT: Whisper `base`
- TTS: Kokoro

## If Something Feels Slow

### GPT-4o mini in mixed mode

- text should appear first
- Kokoro audio still takes extra time afterward
- `text` mode is still the fastest path overall

### Local GGUF feels slow

- that is normal when it is CPU-first
- LM Studio is usually faster for local GPU use on Windows

### Voice transcription feels slow

Try:

- shorter recordings
- less background CPU load
- `STT_MODEL=tiny` if you want more speed

## If Something Fails

### OpenAI replies fail

Check:

- `OPENAI_API_KEY`
- internet access
- `GPT-4o mini` is selected

### LM Studio replies fail

Check:

- LM Studio is open
- the local server is enabled
- the model is loaded
- `http://127.0.0.1:1234/v1/models` responds

### Local GGUF replies fail

Check:

- `LOCAL_LLM_MODEL_PATH`
- the file exists
- the model fits your available memory

### Microphone list is empty

Check:

- browser microphone permission
- Windows microphone permission
- `Refresh mics`

### TTS does not finish

Check:

- the backend was restarted
- Kokoro dependencies are installed
- the app shows whether the latest voice generation failed

## Notes

- The selected microphone is remembered across reloads
- The selected model is remembered across reloads
- Old chats preserve their original persona snapshot
- Audio playback requests that log `206 Partial Content` are normal browser behavior
