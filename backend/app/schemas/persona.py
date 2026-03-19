from datetime import datetime

from pydantic import BaseModel, Field


class PersonaBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    system_prompt: str = Field(min_length=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    voice_preference: str = Field(default="female", pattern="^(male|female)$")


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    system_prompt: str | None = Field(default=None, min_length=1)
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    voice_preference: str | None = Field(default=None, pattern="^(male|female)$")


class Persona(PersonaBase):
    id: str
    created_at: datetime
    updated_at: datetime
