from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.speech_service import EmptyAudio, SpeechServiceError, UnsupportedAudio, speech_service


router = APIRouter(prefix="/api/v1/speech", tags=["Speech"])


@router.post("/transcribe")
async def transcribe_speech(audio: Annotated[UploadFile, File(description="Browser-recorded audio")]) -> dict[str, str | None]:
    try:
        payload = await audio.read(speech_service.MAX_AUDIO_BYTES + 1)
        result = speech_service.transcribe(
            payload,
            content_type=audio.content_type,
            filename=audio.filename,
        )
    except EmptyAudio as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except UnsupportedAudio as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except SpeechServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"status": "TRANSCRIBED", "text": result.text, "language": result.language}
