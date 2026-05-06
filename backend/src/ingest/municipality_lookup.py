import gzip
import json
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.utils.geo import compute_centroid, extract_outer_ring, haversine_km


IBGE_MALHAS_BASE = "https://servicodados.ibge.gov.br/api/v3/malhas"
IBGE_LOCALIDADES_BASE = "https://servicodados.ibge.gov.br/api/v1/localidades"
REQUEST_TIMEOUT_SECONDS = 15
UNKNOWN_MUNICIPALITY = "Municipio nao identificado"

UF_CODE_TO_SIGLA = {
    "11": "RO",
    "12": "AC",
    "13": "AM",
    "14": "RR",
    "15": "PA",
    "16": "AP",
    "17": "TO",
    "21": "MA",
    "22": "PI",
    "23": "CE",
    "24": "RN",
    "25": "PB",
    "26": "PE",
    "27": "AL",
    "28": "SE",
    "29": "BA",
    "31": "MG",
    "32": "ES",
    "33": "RJ",
    "35": "SP",
    "41": "PR",
    "42": "SC",
    "43": "RS",
    "50": "MS",
    "51": "MT",
    "52": "GO",
    "53": "DF",
}


def _default_geojson_paths() -> list[Path]:
    backend_root = Path(__file__).resolve().parents[2]
    repo_root = Path(__file__).resolve().parents[3]
    return [
        backend_root / "data" / "raw" / "municipios_br.geojson",
        repo_root / "data" / "municipios_br.geojson",
        backend_root / "data" / "raw" / "municipios_mt.geojson",
        repo_root / "data" / "municipios_mt.geojson",
    ]


def _normalize_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower().strip()


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


def _get_name(properties: dict[str, Any]) -> str:
    preferred = ("nome", "name", "nm_mun", "nm_municipio", "municipio")
    normalized_map = {_normalize_key(key): key for key in properties.keys()}
    for candidate in preferred:
        key = normalized_map.get(candidate)
        if key:
            return str(properties[key]).strip().title()

    for key in properties.keys():
        lowered = _normalize_key(key)
        if "munic" in lowered or "nome" in lowered:
            return str(properties[key]).strip().title()
    return UNKNOWN_MUNICIPALITY


def _extract_municipio_code(properties: dict[str, Any]) -> str | None:
    normalized_map = {_normalize_key(key): key for key in properties.keys()}
    for candidate in ("codarea", "codigo", "cd_mun", "id"):
        key = normalized_map.get(candidate)
        if not key:
            continue
        raw = str(properties[key]).strip()
        digits = "".join(ch for ch in raw if ch.isdigit())
        if len(digits) >= 7:
            return digits[-7:]
    return None


def _extract_uf(properties: dict[str, Any]) -> str | None:
    normalized_map = {_normalize_key(key): key for key in properties.keys()}
    for candidate in ("uf", "sigla", "siglauf"):
        key = normalized_map.get(candidate)
        if key:
            value = str(properties[key]).strip().upper()
            if len(value) == 2:
                return value

    code_key = normalized_map.get("codarea") or normalized_map.get("codigo")
    if code_key:
        raw = str(properties[code_key]).strip()
        digits = "".join(ch for ch in raw if ch.isdigit())
        if len(digits) >= 2:
            return UF_CODE_TO_SIGLA.get(digits[:2])
    return None


def _feature_centroid(feature: dict[str, Any]) -> tuple[float, float] | None:
    geometry = feature.get("geometry", {})
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")

    if geometry_type == "Point" and isinstance(coordinates, list) and len(coordinates) == 2:
        lon = float(coordinates[0])
        lat = float(coordinates[1])
        return lat, lon

    if geometry_type == "Polygon":
        try:
            ring = extract_outer_ring(geometry)
            return compute_centroid(ring)
        except ValueError:
            return None

    if geometry_type == "MultiPolygon" and isinstance(coordinates, list):
        centroids: list[tuple[float, float]] = []
        for polygon in coordinates:
            if not isinstance(polygon, list) or not polygon:
                continue
            outer = polygon[0]
            try:
                ring = extract_outer_ring({"type": "Polygon", "coordinates": [outer]})
                centroids.append(compute_centroid(ring))
            except ValueError:
                continue
        if centroids:
            avg_lat = sum(item[0] for item in centroids) / len(centroids)
            avg_lon = sum(item[1] for item in centroids) / len(centroids)
            return avg_lat, avg_lon

    return None


def _point_in_ring(lon: float, lat: float, ring: list[list[float]]) -> bool:
    inside = False
    n = len(ring)
    if n < 3:
        return False

    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]
        intersects = ((y1 > lat) != (y2 > lat)) and (
            lon < ((x2 - x1) * (lat - y1) / ((y2 - y1) if (y2 - y1) != 0 else 1e-12)) + x1
        )
        if intersects:
            inside = not inside
    return inside


def _point_in_polygon(lon: float, lat: float, polygon: list[list[list[float]]]) -> bool:
    if not polygon:
        return False
    outer = polygon[0]
    if not _point_in_ring(lon, lat, outer):
        return False
    for hole in polygon[1:]:
        if _point_in_ring(lon, lat, hole):
            return False
    return True


def _feature_contains_point(feature: dict[str, Any], lat: float, lon: float) -> bool:
    geometry = feature.get("geometry", {})
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")

    if geometry_type == "Polygon" and isinstance(coordinates, list):
        return _point_in_polygon(lon, lat, coordinates)
    if geometry_type == "MultiPolygon" and isinstance(coordinates, list):
        return any(_point_in_polygon(lon, lat, polygon) for polygon in coordinates if isinstance(polygon, list))
    return False


@lru_cache(maxsize=1)
def _load_uf_features() -> list[dict[str, Any]]:
    url = (
        f"{IBGE_MALHAS_BASE}/paises/BR?"
        "intrarregiao=UF&qualidade=minima&formato=application/vnd.geo+json"
    )
    payload = _http_get_json(url)
    features = payload.get("features", []) if isinstance(payload, dict) else []
    return [feature for feature in features if isinstance(feature, dict)]


@lru_cache(maxsize=27)
def _load_municipality_features_by_uf(uf: str) -> list[dict[str, Any]]:
    url = (
        f"{IBGE_MALHAS_BASE}/estados/{uf}?"
        "intrarregiao=municipio&qualidade=minima&formato=application/vnd.geo+json"
    )
    payload = _http_get_json(url)
    features = payload.get("features", []) if isinstance(payload, dict) else []
    return [feature for feature in features if isinstance(feature, dict)]


@lru_cache(maxsize=27)
def _load_municipality_name_map_by_uf(uf: str) -> dict[str, str]:
    url = f"{IBGE_LOCALIDADES_BASE}/estados/{uf}/municipios"
    payload = _http_get_json(url)
    if not isinstance(payload, list):
        return {}
    name_map: dict[str, str] = {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        code = item.get("id")
        name = item.get("nome")
        if code is None or name is None:
            continue
        code_digits = "".join(ch for ch in str(code) if ch.isdigit())
        if len(code_digits) >= 7:
            name_map[code_digits[-7:]] = str(name).strip().title()
    return name_map


def _resolve_municipality_name(properties: dict[str, Any], uf: str) -> str:
    raw_name = _get_name(properties)
    if raw_name != UNKNOWN_MUNICIPALITY:
        return raw_name
    municipio_code = _extract_municipio_code(properties)
    if not municipio_code:
        return UNKNOWN_MUNICIPALITY
    try:
        resolved_name = _load_municipality_name_map_by_uf(uf).get(municipio_code)
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        resolved_name = None
    except Exception:
        resolved_name = None
    if resolved_name:
        return resolved_name
    return f"Municipio {municipio_code}"


def _resolve_by_ibge_malhas(lat: float, lon: float) -> tuple[str, str] | None:
    uf_features = _load_uf_features()
    if not uf_features:
        return None

    resolved_uf: str | None = None
    for feature in uf_features:
        if _feature_contains_point(feature, lat, lon):
            properties = feature.get("properties", {})
            if isinstance(properties, dict):
                resolved_uf = _extract_uf(properties)
            break

    if not resolved_uf:
        return None

    municipality_features = _load_municipality_features_by_uf(resolved_uf)
    if not municipality_features:
        return None

    for feature in municipality_features:
        if _feature_contains_point(feature, lat, lon):
            properties = feature.get("properties", {})
            if isinstance(properties, dict):
                return _resolve_municipality_name(properties, resolved_uf), resolved_uf

    # If point sits exactly on a boundary, use nearest centroid.
    nearest_name = None
    nearest_distance = float("inf")
    for feature in municipality_features:
        properties = feature.get("properties", {})
        if not isinstance(properties, dict):
            continue
        centroid = _feature_centroid(feature)
        if centroid is None:
            continue
        feature_lat, feature_lon = centroid
        distance = haversine_km(lat, lon, feature_lat, feature_lon)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_name = _resolve_municipality_name(properties, resolved_uf)

    if nearest_name:
        return nearest_name, resolved_uf
    return None


@lru_cache(maxsize=1)
def _load_local_geojson_features() -> list[dict[str, Any]]:
    for path in _default_geojson_paths():
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        features = payload.get("features", [])
        parsed = [feature for feature in features if isinstance(feature, dict)]
        if parsed:
            return parsed
    return []


def _resolve_by_local_geojson(lat: float, lon: float) -> tuple[str, str] | None:
    features = _load_local_geojson_features()
    if not features:
        return None

    for feature in features:
        if not _feature_contains_point(feature, lat, lon):
            continue
        properties = feature.get("properties", {})
        if not isinstance(properties, dict):
            continue
        uf = _extract_uf(properties) or "BR"
        return _resolve_municipality_name(properties, uf), uf

    centroid_records: list[tuple[str, str, float, float]] = []
    for feature in features:
        properties = feature.get("properties", {})
        if not isinstance(properties, dict):
            continue
        centroid = _feature_centroid(feature)
        if centroid is None:
            continue
        feature_lat, feature_lon = centroid
        feature_uf = _extract_uf(properties) or "BR"
        feature_name = _resolve_municipality_name(properties, feature_uf)
        centroid_records.append((feature_name, feature_uf, feature_lat, feature_lon))

    if not centroid_records:
        return None

    # For regional files (e.g., only MT), avoid returning unrelated municipalities.
    if len(features) < 3000:
        lat_values = [item[2] for item in centroid_records]
        lon_values = [item[3] for item in centroid_records]
        margin_deg = 1.0
        within_local_extent = (
            (min(lat_values) - margin_deg) <= lat <= (max(lat_values) + margin_deg)
            and (min(lon_values) - margin_deg) <= lon <= (max(lon_values) + margin_deg)
        )
        if not within_local_extent:
            return None

    nearest_name = None
    nearest_uf = "BR"
    nearest_distance = float("inf")
    for feature_name, feature_uf, feature_lat, feature_lon in centroid_records:
        distance = haversine_km(lat, lon, feature_lat, feature_lon)
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_uf = feature_uf
            nearest_name = feature_name

    if nearest_name:
        return nearest_name, nearest_uf
    return None


def _resolve_with_local_fallback(lat: float, lon: float) -> tuple[str, str]:
    resolved = _resolve_by_local_geojson(lat=lat, lon=lon)
    if resolved is not None:
        return resolved
    return UNKNOWN_MUNICIPALITY, "BR"


def resolve_municipality(lat: float, lon: float) -> tuple[str, str]:
    try:
        resolved = _resolve_by_ibge_malhas(lat=lat, lon=lon)
        if resolved is not None:
            return resolved
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        pass
    except Exception:
        pass
    return _resolve_with_local_fallback(lat=lat, lon=lon)
