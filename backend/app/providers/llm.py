from abc import ABC, abstractmethod

from openai import OpenAI

from ..config import Settings
from ..schemas.chat import ConversationSummary, MessageRecord, PersonaSnapshot


class LLMProvider(ABC):
    @abstractmethod
    def reply(
        self,
        conversation: ConversationSummary,
        history: list[MessageRecord],
        prompt: PersonaSnapshot,
        user_input: str,
    ) -> str:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    def reply(
        self,
        conversation: ConversationSummary,
        history: list[MessageRecord],
        prompt: PersonaSnapshot,
        user_input: str,
    ) -> str:
        return (
            f"{prompt.name} says: I heard '{user_input}'. "
            f"This is a local mock reply for '{conversation.title}', so the app is usable before provider wiring."
        )


class OpenAILLMProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)

    def reply(
        self,
        conversation: ConversationSummary,
        history: list[MessageRecord],
        prompt: PersonaSnapshot,
        user_input: str,
    ) -> str:
        messages = [{"role": "system", "content": prompt.system_prompt}]
        for item in history[-12:]:
            messages.append({"role": item.role, "content": item.content_text})
        messages.append({"role": "user", "content": user_input})

        completion = self.client.chat.completions.create(
            model=self.settings.llm_model,
            temperature=prompt.temperature,
            messages=messages,
        )
        return completion.choices[0].message.content or ""


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when llm_provider=openai")
        return OpenAILLMProvider(settings)
    return MockLLMProvider()
