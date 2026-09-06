from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import edge_tts
import os
import tempfile

app = FastAPI(title="Edge TTS API")


class TTSRequest(BaseModel):
    text: str
    voice: str = "ar-EG-SalmaNeural"
    rate: str = "+0%"
    pitch: str = "+0Hz"


@app.get("/")
async def home():
    return {
        "status": "online",
        "service": "Edge TTS API"
    }


@app.post("/tts")
async def tts(data: TTSRequest):

    if not data.text or not data.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text is empty"
        )

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False
    )

    temp_file.close()

    try:
        communicate = edge_tts.Communicate(
            text=data.text,
            voice=data.voice,
            rate=data.rate,
            pitch=data.pitch
        )

        await communicate.save(temp_file.name)

        with open(temp_file.name, "rb") as f:
            audio = f.read()

        return Response(
            content=audio,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'attachment; filename="speech.mp3"'
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
