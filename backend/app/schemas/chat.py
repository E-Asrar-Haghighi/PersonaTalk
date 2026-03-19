from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Mode = Literal["text", "voice", "mixed"]
Role = Literal["system", "user", "assistant"]
TranscriptSource = Literal["text", "voice", "voice-fallback"]


class PersonaSnapshot(BaseModel):
    name: str
    system_prompt: str
    temperature: float = Field(ge=0.0, le=2.0)
    voice_preference: Literal["male", "female"] = "female"


class ConversationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    persona_id: str | None = None
    persona_snapshot: PersonaSnapshot
    mode: Mode = "text"


class ConversationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    mode: Mode | None = None
    persona_id: str | None = None
    persona_snapshot: PersonaSnapshot | None = None


class ConversationSummary(BaseModel):
    id: str
    title: str
    persona_id: str | None = None
    persona_name: str | None = None
    persona_snapshot: PersonaSnapshot
    temperature: float
    voice_preference: Literal["male", "female"]
    mode: Mode
    created_at: datetime
    updated_at: datetime
    preview: str = ""


class MessageCreate(BaseModel):
    conversation_id: str
    content_text: str = Field(min_length=1)
    mode: Mode = "text"
    system_prompt_override: str | None = None
    temperature_override: float | None = Field(default=None, ge=0.0, le=2.0)
    voice_preference_override: Literal["male", "female"] | None = None


class MessageRecord(BaseModel):
    id: str
    conversation_id: str
    role: Role
    content_text: str
    audio_path: str | None = None
    transcript_source: TranscriptSource = "text"
    created_at: datetime


class SendMessageResponse(BaseModel):
    conversation: ConversationSummary
    user_message: MessageRecord
    assistant_message: MessageRecord


class VoiceReplyResponse(BaseModel):
    conversation: ConversationSummary
    user_message: MessageRecord
    assistant_message: MessageRecord
    transcription_text: str
    audio_url: str | None = None
