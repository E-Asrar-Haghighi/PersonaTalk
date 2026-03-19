from functools import lru_cache

from ..config import get_settings
from ..providers.llm import build_llm_provider
from ..providers.speech import build_stt_provider, build_tts_provider
from ..repositories.conversations import ConversationRepository
from ..repositories.messages import MessageRepository
from ..repositories.personas import PersonaRepository
from ..repositories.settings import SettingsRepository
from ..services.chat import ChatService
from ..services.personas import PersonaService


@lru_cache(maxsize=1)
def get_persona_service() -> PersonaService:
    return PersonaService(PersonaRepository())


@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    settings = get_settings()
    return ChatService(
        conversation_repository=ConversationRepository(),
        message_repository=MessageRepository(),
        persona_repository=PersonaRepository(),
        llm_provider=build_llm_provider(settings),
        stt_provider=build_stt_provider(settings),
        tts_provider=build_tts_provider(settings),
    )


@lru_cache(maxsize=1)
def get_settings_repository() -> SettingsRepository:
    return SettingsRepository()
