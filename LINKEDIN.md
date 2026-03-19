# LinkedIn Post

## Version 1

I just finished a new personal project: **PersonaTalk**.

It is a local-first web app for chatting with saved AI personas by **text, voice, or mixed mode** in the same conversation.

What I built:

- React + TypeScript frontend
- FastAPI + SQLite backend
- Persona system with reusable prompts
- Conversation history, search, and title editing
- Voice input with local Whisper STT
- Voice output with local Kokoro TTS
- Multiple model options:
  - OpenAI `gpt-4o-mini`
  - LM Studio local server
  - Direct local GGUF models

A few product details I’m happy with:

- you can edit the latest message or transcript and regenerate the reply in the same thread
- each conversation keeps its own persona snapshot and model choice
- the app supports a mostly local or fully local workflow, depending on the provider path you choose

This project was a good reminder that building AI apps is not only about the model itself. A lot of the real work is in UX, local tooling, state management, and making the whole flow feel smooth.

I’m still polishing it, but the MVP is working and the repo is almost ready to publish.

If you work on AI apps, local inference, or voice interfaces, I’d love to hear what you would add next.

#AI #OpenAI #FastAPI #React #TypeScript #Python #LLM #VoiceAI #BuildInPublic

## Version 2

Built a new MVP: **PersonaTalk**.

It’s a local-first AI chat app where you can:

- create and save personas
- chat by text or voice
- switch between cloud and local model providers
- keep conversation history and search it later
- edit the latest transcript/message and regenerate the reply

Tech stack:

- React
- TypeScript
- FastAPI
- SQLite
- Whisper
- Kokoro
- OpenAI / LM Studio / local GGUF

The most interesting part was making the UX feel coherent across text, voice, and local model options.

Now finishing the last GitHub polish pass before publishing the repo.

#BuildInPublic #AIEngineering #LLM #React #Python

## Short Version

I built **PersonaTalk**, a local-first AI persona chat app with text + voice conversations, saved personas, local Whisper STT, Kokoro TTS, and support for OpenAI, LM Studio, or direct GGUF models.

Now doing the last polish pass before publishing the repo.

#AI #LLM #FastAPI #React #TypeScript #Python
