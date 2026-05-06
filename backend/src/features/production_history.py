import gzip
import hashlib
import json
import math
import unicodedata
from functools import lru_cache
from statistics import pstdev
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


SIDRA_TABLE_PAM = "1612"
SIDRA_API_BASE = f"https://apisidra.ibge.gov.br/values/t/{SIDRA_TABLE_PAM}"
IBGE_LOCALIDADES_BASE = "https://servicodados.ibge.gov.br/api/v1/localidades"
REQUEST_TIMEOUT_SECONDS = 15
YEARS_WINDOW = 5

PAM_VARIABLE_CODES = ["109", "216", "214", "112", "215"]
PAM_VARIABLE_TO_BUCKET = {
    "109": "area_planted_ha",
    "216": "area_harvested_ha",
    "214": "production_tons",
    "112": "yield_kg_ha",
    "215": "value_mil_reais",
}

DEFAULT_CROP_CODES = {
    "soja": "2713",
    "milho": "2711",
    "algodao": "2689",
}

CULTURE_ALIASES = {
    "soja": {"soja", "soja em grao", "soja (em grao)"},
    "milho": {"milho", "milho em grao", "milho (em grao)"},
    "algodao": {"algodao", "algodao herbaceo", "algodao herbaceo (em caroco)"},
}


def _normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower().strip()


def _normalize_uf(value: str | None) -> str:
    return _normalize_text(value).upper()


def _hash_ratio(seed_text: str) -> float:
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    raw = str(value).strip()
    if raw in {"", "..", "-", "..."}:
        return None
    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        raw = raw.replace(",", ".")
    try:
        parsed = float(raw)
    except ValueError:
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _to_int(value: Any) -> int | None:
    parsed = _to_float(value)
    if parsed is None:
        return None
    return int(parsed)


def _safe_mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _coefficient_of_variation(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean_value = _safe_mean(values)
    if mean_value <= 0:
        return 0.0
    return float(pstdev(values) / mean_value)


def _trend_label(first: float, last: float, stable_band: float = 0.03) -> str:
    if first <= 0:
        return "estavel"
    delta = (last - first) / first
    if delta > stable_band:
        return "alta"
    if delta < -stable_band:
        return "queda"
    return "estavel"


def _http_get_json(url: str) -> Any:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "SafraViva/1.0",
        },
    )
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        payload = response.read()
        content_encoding = str(response.headers.get("Content-Encoding", "")).lower()
    if "gzip" in content_encoding or payload[:2] == b"\x1f\x8b":
        payload = gzip.decompress(payload)
    payload = payload.decode("utf-8")
    return json.loads(payload)


@lru_cache(maxsize=27)
def _list_municipios_by_uf(uf: str) -> list[dict[str, Any]]:
    uf_code = _normalize_uf(uf)
    if not uf_code:
        return []
    url = f"{IBGE_LOCALIDADES_BASE}/estados/{quote(uf_code)}/municipios"
    response = _http_get_json(url)
    if not isinstance(response, list):
        return []
    return [item for item in response if isinstance(item, dict)]


def _resolve_municipio_code(municipio: str, uf: str) -> str | None:
    target = _normalize_text(municipio)
    if not target:
        return None

    municipios = _list_municipios_by_uf(uf)
    exact_match: dict[str, Any] | None = None
    partial_match: dict[str, Any] | None = None

    for item in municipios:
        name = str(item.get("nome", ""))
        normalized = _normalize_text(name)
        if normalized == target:
            exact_match = item
            break
        if partial_match is None and (target in normalized or normalized in target):
            partial_match = item

    selected = exact_match or partial_match
    if selected is None:
        return None
    code = selected.get("id")
    return str(code) if code is not None else None


@lru_cache(maxsize=2048)
def _list_crop_rows_by_municipio(municipio_code: str) -> list[dict[str, Any]]:
    url = f"{SIDRA_API_BASE}/n6/{quote(municipio_code)}/v/214/p/last%201/c81/all"
    response = _http_get_json(url)
    if not isinstance(response, list):
        return []
    return [row for row in response if isinstance(row, dict)]


def _resolve_crop_code(culture: str, municipio_code: str) -> str | None:
    normalized_culture = _normalize_text(culture)
    if not normalized_culture:
        return None

    aliases = CULTURE_ALIASES.get(normalized_culture, {normalized_culture})
    known_code = DEFAULT_CROP_CODES.get(normalized_culture)

    rows = _list_crop_rows_by_municipio(municipio_code)
    for row in rows:
        crop_name = _normalize_text(row.get("D4N"))
        crop_code = str(row.get("D4C", "")).strip()
        if not crop_name or not crop_code:
            continue
        for alias in aliases:
            if alias in crop_name:
                return crop_code

    return known_code


def _parse_pam_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    yearly: dict[int, dict[str, Any]] = {}
    for row in rows:
        metric_code = str(row.get("D2C", "")).strip()
        metric_bucket = PAM_VARIABLE_TO_BUCKET.get(metric_code)
        year = _to_int(row.get("D3N") or row.get("D3C"))
        value = _to_float(row.get("V"))
        if metric_bucket is None or year is None:
            continue
        current = yearly.setdefault(year, {"year": year})
        if value is not None:
            current[metric_bucket] = value
    return [yearly[year] for year in sorted(yearly.keys())]


def _fetch_history_series(culture: str, municipio: str, uf: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    municipio_code = _resolve_municipio_code(municipio=municipio, uf=uf)
    if municipio_code is None:
        return [], {"reason": "municipio_not_found"}

    crop_code = _resolve_crop_code(culture=culture, municipio_code=municipio_code)
    if crop_code is None:
        return [], {"reason": "crop_not_found", "municipio_code": municipio_code}

    variables = ",".join(PAM_VARIABLE_CODES)
    url = (
        f"{SIDRA_API_BASE}/n6/{quote(municipio_code)}/v/{variables}/"
        f"p/last%20{YEARS_WINDOW}/c81/{quote(crop_code)}"
    )
    response = _http_get_json(url)
    if not isinstance(response, list):
        return [], {"reason": "unexpected_response", "municipio_code": municipio_code, "crop_code": crop_code}

    rows = [row for row in response if isinstance(row, dict)]
    return _parse_pam_rows(rows), {"municipio_code": municipio_code, "crop_code": crop_code}


def _fallback_context(culture: str, municipio: str, uf: str) -> dict[str, Any]:
    seed = f"{uf}:{municipio}:{culture}"
    volatility = round(0.08 + (_hash_ratio(seed + ":volatility") * 0.18), 3)
    mean_index = round(0.85 + (_hash_ratio(seed + ":mean") * 0.35), 3)
    trend_selector = _hash_ratio(seed + ":trend")
    if trend_selector < 0.33:
        trend = "queda"
    elif trend_selector < 0.66:
        trend = "estavel"
    else:
        trend = "alta"

    return {
        "provider": "IBGE/PAM (fallback heuristico)",
        "source": "heuristic",
        "scope": "municipio/cultura sintetico",
        "period_start": None,
        "period_end": None,
        "yield_mean_index": mean_index,
        "yield_volatility": volatility,
        "yield_trend": trend,
        "signals": [
            "Historico de producao nao encontrado via API do IBGE/SIDRA.",
            "Aplicado contexto historico heuristico para manter o score operacional.",
        ],
    }


def get_historical_yield_context(culture: str, municipio: str, uf: str = "MT") -> dict[str, Any]:
    try:
        history_rows, metadata = _fetch_history_series(culture=culture, municipio=municipio, uf=uf)
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return _fallback_context(culture=culture, municipio=municipio, uf=uf)
    except Exception:
        return _fallback_context(culture=culture, municipio=municipio, uf=uf)

    if not history_rows:
        return _fallback_context(culture=culture, municipio=municipio, uf=uf)

    years = [int(row["year"]) for row in history_rows]
    yield_series = [float(row["yield_kg_ha"]) for row in history_rows if row.get("yield_kg_ha") is not None]
    production_per_ha_series: list[float] = []
    for row in history_rows:
        area_harvested = row.get("area_harvested_ha")
        production_tons = row.get("production_tons")
        if area_harvested is None or production_tons is None:
            continue
        if float(area_harvested) <= 0:
            continue
        production_per_ha_series.append((float(production_tons) * 1000.0) / float(area_harvested))

    if len(yield_series) >= 3:
        proxy_series = yield_series
        proxy_label = "rendimento medio (kg/ha)"
    elif len(production_per_ha_series) >= 3:
        proxy_series = production_per_ha_series
        proxy_label = "producao por area colhida (kg/ha)"
    else:
        return _fallback_context(culture=culture, municipio=municipio, uf=uf)

    proxy_mean = _safe_mean(proxy_series)
    latest_proxy = proxy_series[-1]
    volatility = round(max(0.0, _coefficient_of_variation(proxy_series)), 3)
    yield_mean_index = round(max(0.4, min(1.8, latest_proxy / max(proxy_mean, 1e-6))), 3)
    trend = _trend_label(proxy_series[0], latest_proxy)

    signals = [
        "Historico de producao integrado via API IBGE/SIDRA (PAM).",
        f"Serie usada para contexto de produtividade: {proxy_label}.",
        f"Janela historica carregada: {years[0]}-{years[-1]} (municipio/cultura).",
    ]
    if production_per_ha_series:
        signals.append(f"Producao por hectare no ultimo ano: {round(production_per_ha_series[-1], 2)} kg/ha.")

    return {
        "provider": "IBGE/SIDRA (PAM API)",
        "source": "api",
        "scope": "municipio/cultura",
        "period_start": years[0],
        "period_end": years[-1],
        "yield_mean_index": yield_mean_index,
        "yield_volatility": volatility,
        "yield_trend": trend,
        "municipio_code": metadata.get("municipio_code"),
        "crop_code": metadata.get("crop_code"),
        "years": years,
        "yield_kg_ha_series": [round(value, 2) for value in yield_series],
        "production_per_ha_series": [round(value, 2) for value in production_per_ha_series],
        "signals": signals,
    }
