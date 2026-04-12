from fastapi import APIRouter

router = APIRouter()

CULTURAS = [
    {"id": "soja",     "label": "Soja",           "emoji": "🫘"},
    {"id": "milho",    "label": "Milho",          "emoji": "🌽"},
    {"id": "algodao",  "label": "Algodão",        "emoji": "🌿"},
    {"id": "arroz",    "label": "Arroz",          "emoji": "🌾"},
    {"id": "feijao",   "label": "Feijão",         "emoji": "🫘"},
    {"id": "trigo",    "label": "Trigo",          "emoji": "🌾"},
    {"id": "cana",     "label": "Cana-de-açúcar", "emoji": "🎋"},
    {"id": "girassol", "label": "Girassol",       "emoji": "🌻"},
    {"id": "sorgo",    "label": "Sorgo",          "emoji": "🌾"},
    {"id": "amendoim", "label": "Amendoim",       "emoji": "🥜"},
]


@router.get("/culturas")
def culturas():
    return CULTURAS
