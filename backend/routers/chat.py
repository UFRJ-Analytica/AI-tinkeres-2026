import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from chat_session import send_message

router = APIRouter()


class ChatRequest(BaseModel):
    conversation_id: str
    message: str


@router.post("/chat")
def chat(req: ChatRequest):
    if not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY não configurada.")
    try:
        return send_message(req.conversation_id, req.message)
    except KeyError:
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
