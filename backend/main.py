from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mock import get_mock_analysis

app = FastAPI(title="SafraViva API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return get_mock_analysis(payload)
