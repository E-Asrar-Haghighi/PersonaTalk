import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException, UploadFile

from ..providers.llm import LLMProviderRegistry
from ..providers.speech import STTProvider, TTSProvider
from ..repositories.conversations import ConversationRepository
from ..repositories.messages import MessageRepository
from ..repositories.personas import PersonaRepository
from ..schemas.chat import (
    ConversationCreate,
    ConversationSummary,
    ConversationUpdate,
    MessageCreate,
    SendMessageResponse,
    VoiceReplyResponse,
)


class ChatService:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        persona_repository: PersonaRepository,
        llm_registry: LLMProviderRegistry,
        stt_provider: STTProvider,
        tts_provider: TTSProvider,
    ) -> None:
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.persona_repository = persona_repository
        self.llm_registry = llm_registry
        self.stt_provider = stt_provider
        self.tts_provider = tts_provider
        self._tts_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="personatalk-tts")

    def list_conversations(self, query: str | None = None) -> list[ConversationSummary]:
        return self.conversation_repository.list(query=query)

    def get_conversation(self, conversation_id: str) -> ConversationSummary | None:
        return self.conversation_repository.get(conversation_id)

    def create_conversation(self, payload: ConversationCreate) -> ConversationSummary:
        return self.conversation_repository.create(payload)

    def update_conversation(self, conversation_id: str, payload: ConversationUpdate) -> ConversationSummary | None:
        return self.conversation_repository.update(conversation_id, payload)

    def delete_conversation(self, conversation_id: str) -> bool:
        return self.conversation_repository.delete(conversation_id)

    def list_messages(self, conversation_id: str):
        return self.message_repository.list_for_conversation(conversation_id)

    def send_text_message(self, payload: MessageCreate) -> SendMessageResponse:
        conversation = self._require_conversation(payload.conversation_id)
        snapshot = conversation.persona_snapshot.model_copy(
            update={
                "system_prompt": payload.system_prompt_override or conversation.persona_snapshot.system_prompt,
                "temperature": (
                    payload.temperature_override
                    if payload.temperature_override is not None
                    else conversation.persona_snapshot.temperature
                ),
                "voice_preference": payload.voice_preference_override or conversation.persona_snapshot.voice_preference,
            }
        )

        user_message = self.message_repository.create(
            conversation_id=conversation.id,
            role="user",
            content_text=payload.content_text,
            transcript_source="text",
        )

        history = self.message_repository.list_for_conversation(conversation.id)
        llm_provider_name = payload.llm_provider_override or conversation.llm_provider
        try:
            assistant_text = self.llm_registry.get(llm_provider_name).reply(
                conversation, history[:-1], snapshot, payload.content_text
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc

        assistant_message = self.message_repository.create(
            conversation_id=conversation.id,
            role="assistant",
            content_text=assistant_text,
            transcript_source="text",
            audio_path=None,
            tts_status="pending" if payload.mode in ("voice", "mixed") else "none",
        )

        if payload.mode in ("voice", "mixed"):
            self._queue_tts_generation(
                assistant_message.id,
                assistant_text,
                snapshot.voice_preference,
            )

        self.conversation_repository.touch(conversation.id)
        updated = self.conversation_repository.update(
            conversation.id,
            ConversationUpdate(mode=payload.mode, persona_snapshot=snapshot, llm_provider=llm_provider_name),
        )
        return SendMessageResponse(conversation=updated, user_message=user_message, assistant_message=assistant_message)

    async def send_voice_message(
        self,
        conversation_id: str,
        audio: UploadFile,
        system_prompt_override: str | None,
        temperature_override: float | None,
        voice_preference_override: str | None,
        llm_provider_override: str | None,
    ) -> VoiceReplyResponse:
        conversation = self._require_conversation(conversation_id)
        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Microphone input was empty.")

        snapshot = conversation.persona_snapshot.model_copy(
            update={
                "system_prompt": system_prompt_override or conversation.persona_snapshot.system_prompt,
                "temperature": (
                    temperature_override
                    if temperature_override is not None
                    else conversation.persona_snapshot.temperature
                ),
                "voice_preference": voice_preference_override or conversation.persona_snapshot.voice_preference,
            }
        )

        try:
            transcript = self.stt_provider.transcribe(audio_bytes, audio.filename or "voice.webm")
            transcript_source = "voice"
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"STT request failed: {exc}",
            ) from exc

        user_message = self.message_repository.create(
            conversation_id=conversation.id,
            role="user",
            content_text=transcript,
            transcript_source=transcript_source,
        )
        history = self.message_repository.list_for_conversation(conversation.id)
        llm_provider_name = llm_provider_override or conversation.llm_provider

        try:
            assistant_text = self.llm_registry.get(llm_provider_name).reply(
                conversation, history[:-1], snapshot, transcript
            )
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc

        assistant_message = self.message_repository.create(
            conversation_id=conversation.id,
            role="assistant",
            content_text=assistant_text,
            transcript_source="text",
            audio_path=None,
            tts_status="pending",
        )

        audio_url = None
        self._queue_tts_generation(
            assistant_message.id,
            assistant_text,
            snapshot.voice_preference,
        )

        self.conversation_repository.touch(conversation.id)
        updated = self.conversation_repository.update(
            conversation.id,
            ConversationUpdate(mode="mixed", persona_snapshot=snapshot, llm_provider=llm_provider_name),
        )
        return VoiceReplyResponse(
            conversation=updated,
            user_message=user_message,
            assistant_message=assistant_message,
            transcription_text=transcript,
            audio_url=audio_url,
        )

    def _queue_tts_generation(self, message_id: str, content_text: str, voice_preference: str) -> None:
        self._tts_executor.submit(self._generate_tts_for_message, message_id, content_text, voice_preference)

    def _generate_tts_for_message(self, message_id: str, content_text: str, voice_preference: str) -> None:
        try:
            audio_path = self.tts_provider.synthesize(content_text, voice_preference)
        except Exception:
            logger.exception("Background TTS failed for message %s", message_id)
            self.message_repository.update_tts_result(message_id, None, "failed")
            return
        self.message_repository.update_tts_result(message_id, audio_path, "ready")

    def _require_conversation(self, conversation_id: str) -> ConversationSummary:
        conversation = self.conversation_repository.get(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found.")
        return conversation


logger = logging.getLogger(__name__)
