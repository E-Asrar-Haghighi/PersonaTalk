import uuid
from datetime import UTC, datetime

from ..database import db_cursor
from ..schemas.persona import Persona, PersonaCreate, PersonaUpdate


class PersonaRepository:
    def list(self) -> list[Persona]:
        with db_cursor() as connection:
            rows = connection.execute(
                "SELECT id, name, system_prompt, temperature, voice_preference, created_at, updated_at "
                "FROM personas ORDER BY updated_at DESC"
            ).fetchall()
        return [Persona.model_validate(dict(row)) for row in rows]

    def get(self, persona_id: str) -> Persona | None:
        with db_cursor() as connection:
            row = connection.execute(
                "SELECT id, name, system_prompt, temperature, voice_preference, created_at, updated_at "
                "FROM personas WHERE id = ?",
                (persona_id,),
            ).fetchone()
        return Persona.model_validate(dict(row)) if row else None

    def create(self, payload: PersonaCreate) -> Persona:
        now = datetime.now(UTC).isoformat()
        persona = Persona(
            id=str(uuid.uuid4()),
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
            **payload.model_dump(),
        )
        with db_cursor() as connection:
            connection.execute(
                "INSERT INTO personas (id, name, system_prompt, temperature, voice_preference, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    persona.id,
                    persona.name,
                    persona.system_prompt,
                    persona.temperature,
                    persona.voice_preference,
                    now,
                    now,
                ),
            )
        return persona

    def update(self, persona_id: str, payload: PersonaUpdate) -> Persona | None:
        existing = self.get(persona_id)
        if not existing:
            return None

        updated = existing.model_copy(update={k: v for k, v in payload.model_dump().items() if v is not None})
        timestamp = datetime.now(UTC).isoformat()
        with db_cursor() as connection:
            connection.execute(
                "UPDATE personas SET name = ?, system_prompt = ?, temperature = ?, voice_preference = ?, updated_at = ? "
                "WHERE id = ?",
                (
                    updated.name,
                    updated.system_prompt,
                    updated.temperature,
                    updated.voice_preference,
                    timestamp,
                    persona_id,
                ),
            )
        return self.get(persona_id)

    def delete(self, persona_id: str) -> bool:
        with db_cursor() as connection:
            result = connection.execute("DELETE FROM personas WHERE id = ?", (persona_id,))
        return result.rowcount > 0
