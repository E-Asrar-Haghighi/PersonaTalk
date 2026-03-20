import re
from abc import ABC, abstractmethod
from functools import lru_cache

from openai import OpenAI

from ..config import Settings
from ..schemas.chat import ConversationSummary, MessageRecord, PersonaSnapshot

PLAIN_TEXT_STYLE_INSTRUCTION = (
    "Respond in plain conversational text by default. "
    "Avoid Markdown headings, bullet lists, bold markers, and heavy formatting unless the user asks for them. "
    "If you need a list, write it in simple plain text."
)


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
        return _normalize_assistant_text(
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
        messages = _build_messages(history, prompt, user_input)

        completion = self.client.chat.completions.create(
            model=self.settings.llm_model,
            temperature=prompt.temperature,
            messages=messages,
        )
        return _normalize_assistant_text(completion.choices[0].message.content or "")


class LMStudioLLMProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(base_url=settings.lm_studio_base_url, api_key="lm-studio")

    def reply(
        self,
        conversation: ConversationSummary,
        history: list[MessageRecord],
        prompt: PersonaSnapshot,
        user_input: str,
    ) -> str:
        messages = _build_messages(history, prompt, user_input)

        completion = self.client.chat.completions.create(
            model=self.settings.lm_studio_model,
            temperature=prompt.temperature,
            messages=messages,
        )
        return _normalize_assistant_text(completion.choices[0].message.content or "")


class LocalLlamaCppProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        try:
            from llama_cpp import Llama
        except Exception as exc:
            raise RuntimeError(
                "llama-cpp-python is not installed. Install it with `pip install -r requirements-local-llm.txt`."
            ) from exc

        model_path = settings.local_llm_model_path
        if not model_path:
            raise RuntimeError("LOCAL_LLM_MODEL_PATH is required when llm_provider=llama_cpp")
        if not model_path.is_file():
            raise RuntimeError(f"LOCAL_LLM_MODEL_PATH does not exist: {model_path}")

        kwargs: dict[str, object] = {
            "model_path": str(model_path),
            "n_ctx": settings.local_llm_n_ctx,
            "n_threads": settings.local_llm_n_threads,
            "n_gpu_layers": settings.local_llm_n_gpu_layers,
            "verbose": False,
        }
        if settings.local_llm_chat_format:
            kwargs["chat_format"] = settings.local_llm_chat_format

        self.client = Llama(**kwargs)

    def reply(
        self,
        conversation: ConversationSummary,
        history: list[MessageRecord],
        prompt: PersonaSnapshot,
        user_input: str,
    ) -> str:
        messages = _build_messages(history, prompt, user_input)

        completion = self.client.create_chat_completion(
            messages=messages,
            temperature=prompt.temperature,
            max_tokens=self.settings.local_llm_max_tokens,
        )
        content = completion["choices"][0]["message"]["content"]
        return _normalize_assistant_text(content or "")


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when llm_provider=openai")
        return OpenAILLMProvider(settings)
    if settings.llm_provider == "lm_studio":
        return LMStudioLLMProvider(settings)
    if settings.llm_provider == "llama_cpp":
        return LocalLlamaCppProvider(settings)
    return MockLLMProvider()


class LLMProviderRegistry:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._providers: dict[str, LLMProvider] = {}
        self._provider_models: dict[str, str] = {
            "openai": "gpt-4o-mini",
            "lm_studio": settings.lm_studio_model,
            "llama_cpp": settings.llm_model,
            "mock": settings.llm_model,
        }

    def get(self, provider_name: str) -> LLMProvider:
        key = (provider_name or self.settings.llm_provider).lower()
        if key in self._providers:
            return self._providers[key]

        provider = self._build(key)
        self._providers[key] = provider
        return provider

    def _build(self, provider_name: str) -> LLMProvider:
        scoped = self.settings.model_copy(
            update={
                "llm_provider": provider_name,
                "llm_model": self._provider_models.get(provider_name, self.settings.llm_model),
            }
        )
        return build_llm_provider(scoped)


def _build_messages(history: list[MessageRecord], prompt: PersonaSnapshot, user_input: str) -> list[dict[str, str]]:
    system_prompt = f"{prompt.system_prompt.strip()}\n\n{PLAIN_TEXT_STYLE_INSTRUCTION}"
    messages = [{"role": "system", "content": system_prompt}]
    for item in history[-12:]:
        messages.append({"role": item.role, "content": item.content_text})
    messages.append({"role": "user", "content": user_input})
    return messages


def _normalize_assistant_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return ""

    normalized = re.sub(r"```(?:[\w+-]+\n)?", "", normalized)
    normalized = normalized.replace("```", "")
    normalized = re.sub(r"`([^`]+)`", r"\1", normalized)
    normalized = re.sub(r"\*\*(.*?)\*\*", r"\1", normalized, flags=re.DOTALL)
    normalized = re.sub(r"__(.*?)__", r"\1", normalized, flags=re.DOTALL)
    normalized = re.sub(r"(?<!\*)\*(?!\s)(.*?)(?<!\s)\*(?!\*)", r"\1", normalized, flags=re.DOTALL)
    normalized = re.sub(r"(?<!_)_(?!\s)(.*?)(?<!\s)_(?!_)", r"\1", normalized, flags=re.DOTALL)

    cleaned_lines: list[str] = []
    for raw_line in normalized.split("\n"):
        line = raw_line.strip()
        if not line:
            cleaned_lines.append("")
            continue
        line = re.sub(r"^#{1,6}\s+", "", line)
        line = re.sub(r"^>\s+", "", line)
        line = re.sub(r"^\s*(?:[-*+]|\d+[.)-])\s+", "", line)
        cleaned_lines.append(line)

    collapsed = "\n".join(cleaned_lines)
    collapsed = re.sub(r"\n{3,}", "\n\n", collapsed)
    return collapsed.strip()
