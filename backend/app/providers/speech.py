import math
import logging
import struct
import time
import wave
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from ..config import Settings

logger = logging.getLogger(__name__)


class STTProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        raise NotImplementedError


class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, voice_preference: str) -> str:
        raise NotImplementedError


class MockSTTProvider(STTProvider):
    def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        if not audio_bytes:
            raise ValueError("No microphone input received.")
        return f"Transcribed from {filename or 'audio'} ({len(audio_bytes)} bytes)"


class MockTTSProvider(TTSProvider):
    def __init__(self, settings: Settings) -> None:
        self.audio_cache_dir = settings.audio_cache_dir

    def synthesize(self, text: str, voice_preference: str) -> str:
        filename = f"{uuid4()}.wav"
        destination = self.audio_cache_dir / filename
        duration_seconds = min(max(len(text) / 55.0, 1.0), 4.0)
        sample_rate = 22050
        tone = 180 if voice_preference == "male" else 260
        amplitude = 12000

        with wave.open(str(destination), "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            total_frames = int(sample_rate * duration_seconds)
            for frame in range(total_frames):
                taper = min(frame / (sample_rate * 0.05), 1.0)
                sample = int(amplitude * taper * math.sin(2 * math.pi * tone * frame / sample_rate))
                wav_file.writeframes(struct.pack("<h", sample))
        return f"/api/audio/{filename}"


class PlaceholderSTTProvider(STTProvider):
    def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        if not audio_bytes:
            raise ValueError("No microphone input received.")
        return "Local STT integration placeholder. Replace this adapter with a local inference runtime."


class PlaceholderTTSProvider(TTSProvider):
    def __init__(self, settings: Settings) -> None:
        self.audio_cache_dir = settings.audio_cache_dir

    def synthesize(self, text: str, voice_preference: str) -> str:
        filename = f"{uuid4()}.json"
        destination = self.audio_cache_dir / filename
        destination.write_text(
            f'{{"voice_preference":"{voice_preference}","text":"{text}","note":"Kokoro placeholder"}}',
            encoding="utf-8",
        )
        return f"/api/audio/{filename}"


class FasterWhisperSTTProvider(STTProvider):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._model = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="whisper-stt")

    def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        if not audio_bytes:
            raise ValueError("No microphone input received.")

        with NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = Path(temp_file.name)

        try:
            started_at = time.perf_counter()
            logger.info("STT started for %s (%s bytes)", filename or "audio.wav", len(audio_bytes))
            future = self._executor.submit(self._transcribe_path, temp_path)
            transcript = future.result(timeout=self.settings.stt_timeout_seconds).strip()
            logger.info("STT completed in %.2fs", time.perf_counter() - started_at)
            return transcript
        except FutureTimeoutError as exc:
            logger.error("STT timed out after %ss", self.settings.stt_timeout_seconds)
            raise RuntimeError(
                f"Whisper transcription timed out after {self.settings.stt_timeout_seconds} seconds. "
                "Try a smaller local model such as `tiny` or `base`, or reduce background CPU load."
            ) from exc
        finally:
            temp_path.unlink(missing_ok=True)

    def _transcribe_path(self, audio_path: Path) -> str:
        from faster_whisper import WhisperModel

        if self._model is None:
            started_at = time.perf_counter()
            logger.info(
                "Loading faster-whisper model=%s device=cpu compute_type=%s cpu_threads=%s",
                self.settings.stt_model,
                self.settings.whisper_compute_type,
                self.settings.whisper_cpu_threads,
            )
            self._model = WhisperModel(
                self.settings.stt_model,
                device="cpu",
                compute_type=self.settings.whisper_compute_type,
                cpu_threads=self.settings.whisper_cpu_threads,
            )
            logger.info("Whisper model loaded in %.2fs", time.perf_counter() - started_at)

        logger.info("Running faster-whisper transcription")
        started_at = time.perf_counter()
        segments, _info = self._model.transcribe(
            str(audio_path),
            beam_size=1,
            vad_filter=False,
            language="en",
            condition_on_previous_text=False,
        )
        text = " ".join(segment.text.strip() for segment in segments).strip()
        logger.info("Whisper transcription finished in %.2fs", time.perf_counter() - started_at)
        if not text:
            logger.warning("Whisper returned an empty transcript with primary settings; retrying with VAD fallback")
            retry_started_at = time.perf_counter()
            retry_segments, _retry_info = self._model.transcribe(
                str(audio_path),
                beam_size=1,
                vad_filter=True,
                condition_on_previous_text=False,
            )
            text = " ".join(segment.text.strip() for segment in retry_segments).strip()
            logger.info("Whisper fallback transcription finished in %.2fs", time.perf_counter() - retry_started_at)
        if not text:
            raise RuntimeError("Whisper returned an empty transcript. Try speaking a bit longer or increasing microphone input volume.")
        return text


class KokoroLocalTTSProvider(TTSProvider):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.audio_cache_dir = settings.audio_cache_dir
        self._pipeline = None
        self._voice: str | None = None

    def synthesize(self, text: str, voice_preference: str) -> str:
        voice = self._map_voice(voice_preference)
        logger.info("TTS started with Kokoro voice=%s", voice)
        started_at = time.perf_counter()
        pipeline = self._get_pipeline(voice)
        result = pipeline.run(text)

        filename = f"{uuid4()}.wav"
        destination = self.audio_cache_dir / filename

        import soundfile as sf

        sf.write(str(destination), result.audio, result.sample_rate)
        logger.info("TTS completed in %.2fs", time.perf_counter() - started_at)
        return f"/api/audio/{filename}"

    def _get_pipeline(self, voice: str):
        from pykokoro import KokoroPipeline, PipelineConfig
        from pykokoro.generation_config import GenerationConfig
        from pykokoro.tokenizer import TokenizerConfig

        if self._pipeline is not None and self._voice == voice:
            return self._pipeline

        config = PipelineConfig(
            voice=voice,
            provider=self.settings.kokoro_provider,
            generation=GenerationConfig(lang=self.settings.kokoro_lang, speed=self.settings.kokoro_speed),
            tokenizer_config=TokenizerConfig(
                use_spacy=False,
                use_espeak_fallback=True,
                use_goruut_fallback=False,
            ),
        )
        self._pipeline = KokoroPipeline(config)
        self._voice = voice
        return self._pipeline

    def _map_voice(self, voice_preference: str) -> str:
        if voice_preference == "male":
            return self.settings.kokoro_voice_male
        return self.settings.kokoro_voice_female


def build_stt_provider(settings: Settings) -> STTProvider:
    if settings.stt_provider == "mock":
        return MockSTTProvider()
    if settings.stt_provider == "whisper":
        return FasterWhisperSTTProvider(settings)
    return PlaceholderSTTProvider()


def build_tts_provider(settings: Settings) -> TTSProvider:
    if settings.tts_provider == "mock":
        return MockTTSProvider(settings)
    if settings.tts_provider == "kokoro":
        return KokoroLocalTTSProvider(settings)
    return PlaceholderTTSProvider(settings)
