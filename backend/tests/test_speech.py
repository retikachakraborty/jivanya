import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.services.speech_service import EmptyAudio, SpeechService, SpeechServiceError, UnsupportedAudio


class SpeechServiceTests(unittest.TestCase):
    def test_rejects_empty_and_unsupported_audio_before_provider_call(self):
        service = SpeechService(client=Mock())
        with self.assertRaises(EmptyAudio):
            service.transcribe(b"", content_type="audio/webm", filename="recording.webm")
        with self.assertRaises(UnsupportedAudio):
            service.transcribe(b"not-audio", content_type="text/plain", filename="recording.txt")
        service.client.audio.transcriptions.create.assert_not_called()

    def test_returns_provider_transcript_without_leaking_configuration(self):
        client = Mock()
        client.audio.transcriptions.create.return_value = SimpleNamespace(text="  give me breakfast  ", language="en")
        service = SpeechService(client=client)
        with patch.dict(os.environ, {"GROQ_WHISPER_MODEL": "whisper-large-v3-turbo"}, clear=False):
            result = service.transcribe(b"\x1aE\xdf\xa3audio", content_type="audio/webm", filename="recording.webm")
        self.assertEqual(result.text, "give me breakfast")
        self.assertEqual(result.language, "en")
        self.assertEqual(client.audio.transcriptions.create.call_args.kwargs["model"], "whisper-large-v3-turbo")

    def test_provider_failure_is_sanitized(self):
        client = Mock()
        client.audio.transcriptions.create.side_effect = RuntimeError("provider key=secret")
        with self.assertRaisesRegex(SpeechServiceError, "temporarily unavailable"):
            SpeechService(client=client).transcribe(b"\x1aE\xdf\xa3audio", content_type="audio/webm", filename="recording.webm")


if __name__ == "__main__":
    unittest.main()
