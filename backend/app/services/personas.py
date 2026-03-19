from ..repositories.personas import PersonaRepository
from ..schemas.persona import Persona, PersonaCreate, PersonaUpdate


STARTER_PERSONAS: list[PersonaCreate] = [
    PersonaCreate(
        name="Friend",
        system_prompt="You are a warm, practical companion who listens closely, responds clearly, and stays grounded.",
        temperature=0.8,
        voice_preference="female",
    ),
    PersonaCreate(
        name="Writer",
        system_prompt="You are a collaborative writing partner who helps brainstorm, edit, and tighten ideas without losing voice.",
        temperature=0.9,
        voice_preference="female",
    ),
    PersonaCreate(
        name="Business Consultant",
        system_prompt="You are a concise business strategist focused on actionable tradeoffs, priorities, and next steps.",
        temperature=0.5,
        voice_preference="male",
    ),
    PersonaCreate(
        name="Filmmaker",
        system_prompt="You are a creative filmmaking collaborator who helps shape stories, scenes, shot ideas, and production decisions.",
        temperature=0.85,
        voice_preference="male",
    ),
]


class PersonaService:
    def __init__(self, repository: PersonaRepository) -> None:
        self.repository = repository

    def list_personas(self) -> list[Persona]:
        return self.repository.list()

    def get_persona(self, persona_id: str) -> Persona | None:
        return self.repository.get(persona_id)

    def create_persona(self, payload: PersonaCreate) -> Persona:
        return self.repository.create(payload)

    def update_persona(self, persona_id: str, payload: PersonaUpdate) -> Persona | None:
        return self.repository.update(persona_id, payload)

    def delete_persona(self, persona_id: str) -> bool:
        return self.repository.delete(persona_id)

    def seed_defaults(self) -> None:
        if self.repository.list():
            return
        for persona in STARTER_PERSONAS:
            self.repository.create(persona)
