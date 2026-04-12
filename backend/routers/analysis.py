import os

from fastapi import APIRouter

from mock import get_mock_analysis
from copilot import generate_copilot_response
from chat_session import start_conversation

router = APIRouter()


@router.post("/mock/analysis")
def mock_analysis(payload: dict):
    analysis = get_mock_analysis(payload)

    if os.environ.get("GEMINI_API_KEY"):
        try:
            analysis["copilot_response"] = generate_copilot_response(analysis)
        except Exception as e:
            print(f"[copilot] Gemini falhou, usando mock: {e}")

    try:
        analysis["conversation_id"] = start_conversation(analysis)
    except Exception as e:
        print(f"[chat] Falha ao criar sessão: {e}")

    return analysis
