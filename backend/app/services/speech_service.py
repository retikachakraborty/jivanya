"""Server-side Groq Whisper transcription for Jiv voice input."""

import os
from dataclasses import dataclass


SUPPORTED_AUDIO_TYPES = {
    "audio/webm", "audio/ogg", "audio/wav", "audio/wave", "audio/x-wav",
    "audio/mpeg", "audio/mp4", "audio/aac", "audio/3gpp",
}


class SpeechServiceError(RuntimeError):
    """Safe, user-facing transcription failure."""


class UnsupportedAudio(SpeechServiceError):
    pass


class EmptyAudio(SpeechServiceError):
    pass


@dataclass(frozen=True)
class Transcription:
    text: str
    language: str | None = None


class SpeechService:
    MAX_AUDIO_BYTES = 25 * 1024 * 1024

    def __init__(self, client=None) -> None:
        self._client = client

    @property
    def client(self):
        if self._client is None:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise SpeechServiceError("Speech transcription is not configured")
            try:
                from groq import Groq
                self._client = Groq(api_key=api_key)
            except Exception as exc:
                raise SpeechServiceError("Speech transcription is unavailable") from exc
        return self._client

    @staticmethod
    def validate_audio(payload: bytes, content_type: str | None, filename: str | None) -> None:
        if not payload:
            raise EmptyAudio("The recording was empty")
        if len(payload) > SpeechService.MAX_AUDIO_BYTES:
            raise UnsupportedAudio("The recording is too large")
        normalized_type = (content_type or "").split(";", 1)[0].strip().lower()
        extension = (filename or "").lower().rsplit(".", 1)[-1] if "." in (filename or "") else ""
        supported_extensions = {"webm", "ogg", "wav", "mp3", "mp4", "m4a", "aac", "3gp"}
        if normalized_type not in SUPPORTED_AUDIO_TYPES and extension not in supported_extensions:
            raise UnsupportedAudio("This audio format is not supported")
        signatures = (b"\x1aE\xdf\xa3", b"OggS", b"RIFF", b"ID3", b"ftyp")
        looks_like_audio = payload.startswith(signatures) or (
            len(payload) >= 2 and payload[0] == 0xFF and (payload[1] & 0xE0) == 0xE0
        )
        if not looks_like_audio:
            raise UnsupportedAudio("The uploaded file is not a valid audio recording")

    def transcribe(self, payload: bytes, *, content_type: str | None, filename: str | None) -> Transcription:
        self.validate_audio(payload, content_type, filename)
        model = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo") or "whisper-large-v3-turbo"
        safe_filename = filename or "jiv-recording.webm"
        try:
            response = self.client.audio.transcriptions.create(
                file=(safe_filename, payload),
                model=model,
                response_format="verbose_json",
                timeout=30.0,
            )
        except Exception as exc:
            # Do not leak provider exceptions, request details, or configuration.
            raise SpeechServiceError("Speech transcription is temporarily unavailable") from exc
        text = str(getattr(response, "text", "") or "").strip()
        if not text:
            raise EmptyAudio("No speech was detected in the recording")
        language = getattr(response, "language", None)
        return Transcription(text=text, language=str(language) if language else None)


speech_service = SpeechService()
