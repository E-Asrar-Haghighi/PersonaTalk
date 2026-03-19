from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from ..config import get_settings
from ..repositories.settings import SettingsRepository
from ..schemas.chat import ConversationCreate, ConversationUpdate, MessageCreate
from ..schemas.persona import PersonaCreate, PersonaUpdate
from ..services.chat import ChatService
from ..services.personas import PersonaService
from .dependencies import get_chat_service, get_persona_service, get_settings_repository


router = APIRouter()


@router.get("/health")
def healthcheck():
    return {"status": "ok"}


@router.get("/personas")
def list_personas(service: PersonaService = Depends(get_persona_service)):
    return service.list_personas()


@router.post("/personas", status_code=201)
def create_persona(payload: PersonaCreate, service: PersonaService = Depends(get_persona_service)):
    return service.create_persona(payload)


@router.put("/personas/{persona_id}")
def update_persona(persona_id: str, payload: PersonaUpdate, service: PersonaService = Depends(get_persona_service)):
    persona = service.update_persona(persona_id, payload)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found.")
    return persona


@router.delete("/personas/{persona_id}", status_code=204)
def delete_persona(persona_id: str, service: PersonaService = Depends(get_persona_service)):
    if not service.delete_persona(persona_id):
        raise HTTPException(status_code=404, detail="Persona not found.")


@router.get("/conversations")
def list_conversations(
    q: str | None = Query(default=None, min_length=1),
    service: ChatService = Depends(get_chat_service),
):
    return service.list_conversations(query=q)


@router.post("/conversations", status_code=201)
def create_conversation(payload: ConversationCreate, service: ChatService = Depends(get_chat_service)):
    return service.create_conversation(payload)


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, service: ChatService = Depends(get_chat_service)):
    conversation = service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation


@router.put("/conversations/{conversation_id}")
def update_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    service: ChatService = Depends(get_chat_service),
):
    conversation = service.update_conversation(conversation_id, payload)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str, service: ChatService = Depends(get_chat_service)):
    if not service.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found.")


@router.get("/conversations/{conversation_id}/messages")
def list_messages(conversation_id: str, service: ChatService = Depends(get_chat_service)):
    return service.list_messages(conversation_id)


@router.post("/messages")
def send_message(payload: MessageCreate, service: ChatService = Depends(get_chat_service)):
    return service.send_text_message(payload)


@router.post("/voice/{conversation_id}")
async def send_voice(
    conversation_id: str,
    audio: UploadFile = File(...),
    system_prompt_override: str | None = None,
    temperature_override: float | None = None,
    voice_preference_override: str | None = None,
    llm_provider_override: str | None = None,
    service: ChatService = Depends(get_chat_service),
):
    return await service.send_voice_message(
        conversation_id=conversation_id,
        audio=audio,
        system_prompt_override=system_prompt_override,
        temperature_override=temperature_override,
        voice_preference_override=voice_preference_override,
        llm_provider_override=llm_provider_override,
    )


@router.get("/settings")
def list_settings(repository: SettingsRepository = Depends(get_settings_repository)):
    return repository.list()


@router.put("/settings/{key}")
def upsert_setting(key: str, value: str, repository: SettingsRepository = Depends(get_settings_repository)):
    return repository.upsert(key, value)


@router.get("/audio/{filename}")
def get_audio(filename: str):
    path = get_settings().audio_cache_dir / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")
    return FileResponse(path)
