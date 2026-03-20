from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "PersonaTalk"
    api_prefix: str = "/api"
    database_path: Path = Field(default=BASE_DIR / "backend" / "app" / "data" / "personatalk.db")
    audio_cache_dir: Path = Field(default=BASE_DIR / "backend" / "app" / "data" / "audio")
    llm_provider: str = "mock"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str | None = None
    lm_studio_base_url: str = "http://127.0.0.1:1234/v1"
    lm_studio_model: str = "meta-llama-3.1-8b-instruct"
    local_llm_model_path: Path | None = None
    local_llm_chat_format: str | None = None
    local_llm_n_ctx: int = 4096
    local_llm_n_threads: int = 6
    local_llm_n_gpu_layers: int = 0
    local_llm_max_tokens: int = 512
    stt_provider: str = "mock"
    stt_model: str = "base"
    whisper_compute_type: str = "int8"
    whisper_cpu_threads: int = 4
    tts_provider: str = "mock"
    tts_model: str = "kokoro-82m"
    parakeet_backend: str = "auto"
    parakeet_device: str | None = None
    stt_timeout_seconds: int = 180
    tts_timeout_seconds: int = 90
    tts_chunk_char_limit: int = 260
    kokoro_provider: str = "auto"
    kokoro_voice_male: str = "am_michael"
    kokoro_voice_female: str = "af_sarah"
    kokoro_lang: str = "en-us"
    kokoro_speed: float = 1.0
    default_voice_male: str = "baritone"
    default_voice_female: str = "alto"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    settings.audio_cache_dir.mkdir(parents=True, exist_ok=True)
    return settings
