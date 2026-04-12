import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from mock import get_mock_analysis
from copilot import generate_copilot_response
from chat import start_conversation, send_message

load_dotenv()

app = FastAPI(title="SafraViva API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    conversation_id: str
    message: str

CULTURAS = [
    {"id": "soja",        "label": "Soja",           "emoji": "🫘"},
    {"id": "milho",       "label": "Milho",          "emoji": "🌽"},
    {"id": "algodao",     "label": "Algodão",        "emoji": "🌿"},
    {"id": "arroz",       "label": "Arroz",          "emoji": "🌾"},
    {"id": "feijao",      "label": "Feijão",         "emoji": "🫘"},
    {"id": "trigo",       "label": "Trigo",          "emoji": "🌾"},
    {"id": "cana",        "label": "Cana-de-açúcar", "emoji": "🎋"},
    {"id": "girassol",    "label": "Girassol",       "emoji": "🌻"},
    {"id": "sorgo",       "label": "Sorgo",          "emoji": "🌾"},
    {"id": "amendoim",    "label": "Amendoim",       "emoji": "🥜"},
]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/culturas")
def culturas():
    return CULTURAS


@app.post("/mock/analysis")
def mock_analysis(payload: dict):
    analysis = get_mock_analysis(payload)

    # Substitui o copilot_response pelo Gemini se a chave estiver configurada
    if os.environ.get("GEMINI_API_KEY"):
        try:
            analysis["copilot_response"] = generate_copilot_response(analysis)
        except Exception as e:
            print(f"[copilot] Gemini falhou, usando mock: {e}")

    # Inicia sessão de chat com o contexto da análise
    try:
        analysis["conversation_id"] = start_conversation(analysis)
    except Exception as e:
        print(f"[chat] Falha ao criar sessão: {e}")

    return analysis


@app.post("/chat")
def chat(req: ChatRequest):
    if not os.environ.get("GEMINI_API_KEY"):
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY não configurada.")
    try:
        return send_message(req.conversation_id, req.message)
    except KeyError:
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
