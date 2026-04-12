import hashlib
import os
from datetime import datetime, timedelta
from typing import Any

from src.ingest.gee_client import get_ee_client, to_ee_polygon
from src.utils.time import ensure_utc, to_iso_z


def _hash_ratio(seed_text: str) -> float:
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _reduce_mean(ee: Any, image: Any, geometry: Any, scale: int = 500) -> float | None:
    try:
        result = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=scale,
            bestEffort=True,
            maxPixels=1_000_000_000,
        ).getInfo()
        if not result:
            return None
        value = next(iter(result.values()))
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _extract_outer_ring(geometry: dict[str, Any]) -> list[list[float]]:
    coordinates = geometry.get("coordinates", [])
    if not isinstance(coordinates, list) or not coordinates:
        return []
    ring = coordinates[0]
    if not isinstance(ring, list) or len(ring) < 3:
        return []
    normalized = [[float(point[0]), float(point[1])] for point in ring if isinstance(point, (list, tuple)) and len(point) >= 2]
    if len(normalized) < 3:
        return []
    if normalized[0] != normalized[-1]:
        normalized.append(normalized[0])
    return normalized


def _point_in_polygon(lon: float, lat: float, ring: list[list[float]]) -> bool:
    inside = False
    for idx in range(len(ring) - 1):
        lon1, lat1 = ring[idx]
        lon2, lat2 = ring[idx + 1]
        intersects = ((lat1 > lat) != (lat2 > lat)) and (
            lon < (lon2 - lon1) * (lat - lat1) / ((lat2 - lat1) or 1e-12) + lon1
        )
        if intersects:
            inside = not inside
    return inside


def _build_ndvi_grid_cells(geometry: dict[str, Any], resolution: int = 8) -> list[dict[str, Any]]:
    ring = _extract_outer_ring(geometry)
    if not ring:
        return []

    lons = [point[0] for point in ring]
    lats = [point[1] for point in ring]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    lon_span = max_lon - min_lon
    lat_span = max_lat - min_lat
    if lon_span <= 0 or lat_span <= 0:
        return []

    steps = max(4, min(12, resolution))
    d_lon = lon_span / steps
    d_lat = lat_span / steps
    cells: list[dict[str, Any]] = []
    cell_id = 0

    for row in range(steps):
        for col in range(steps):
            lon1 = min_lon + (col * d_lon)
            lon2 = lon1 + d_lon
            lat1 = min_lat + (row * d_lat)
            lat2 = lat1 + d_lat
            center_lon = (lon1 + lon2) / 2.0
            center_lat = (lat1 + lat2) / 2.0
            if not _point_in_polygon(center_lon, center_lat, ring):
                continue

            polygon = [[[lon1, lat1], [lon2, lat1], [lon2, lat2], [lon1, lat2], [lon1, lat1]]]
            cells.append(
                {
                    "id": f"cell_{cell_id}",
                    "center": [center_lon, center_lat],
                    "geometry": {"type": "Polygon", "coordinates": polygon},
                }
            )
            cell_id += 1

    return cells


def _ndvi_color(ndvi: float | None, anomaly: float | None) -> str:
    if ndvi is None:
        return "#9ca3af"
    if anomaly is not None and anomaly <= -0.10:
        return "#7f1d1d"
    if anomaly is not None and anomaly <= -0.05:
        return "#b91c1c"
    if ndvi < 0.30:
        return "#dc2626"
    if ndvi < 0.45:
        return "#f59e0b"
    if ndvi < 0.60:
        return "#84cc16"
    return "#166534"


def _ndvi_level(ndvi: float | None, anomaly: float | None) -> str:
    if ndvi is None:
        return "sem_dado"
    if anomaly is not None and anomaly <= -0.10:
        return "critico"
    if anomaly is not None and anomaly <= -0.05:
        return "alto"
    if ndvi < 0.35:
        return "alto"
    if ndvi < 0.50:
        return "moderado"
    return "baixo"


def _build_ndvi_heatmap(
    cells: list[dict[str, Any]],
    ndvi_by_id: dict[str, float],
    anomaly_by_id: dict[str, float] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    anomaly_by_id = anomaly_by_id or {}
    features: list[dict[str, Any]] = []
    ndvi_values: list[float] = []
    anomaly_values: list[float] = []

    for cell in cells:
        cell_id = str(cell["id"])
        ndvi = ndvi_by_id.get(cell_id)
        anomaly = anomaly_by_id.get(cell_id)
        if ndvi is not None:
            ndvi = round(float(ndvi), 3)
            ndvi_values.append(ndvi)
        if anomaly is not None:
            anomaly = round(float(anomaly), 3)
            anomaly_values.append(anomaly)

        level = _ndvi_level(ndvi, anomaly)
        fill_color = _ndvi_color(ndvi, anomaly)
        if ndvi is None:
            tooltip = "Sem dado NDVI para esta celula"
        elif anomaly is None:
            tooltip = f"NDVI {ndvi} | risco {level}"
        else:
            tooltip = f"NDVI {ndvi} | anomalia {anomaly} | risco {level}"

        features.append(
            {
                "type": "Feature",
                "geometry": cell["geometry"],
                "properties": {
                    "cell_id": cell_id,
                    "ndvi": ndvi,
                    "ndvi_anomaly": anomaly,
                    "risk_level": level,
                    "fill_color": fill_color,
                    "fill_opacity": 0.65,
                    "tooltip": tooltip,
                },
            }
        )

    if ndvi_values:
        ndvi_min = round(min(ndvi_values), 3)
        ndvi_max = round(max(ndvi_values), 3)
        ndvi_mean = round(sum(ndvi_values) / len(ndvi_values), 3)
    else:
        ndvi_min = None
        ndvi_max = None
        ndvi_mean = None

    if anomaly_values:
        anomaly_min = round(min(anomaly_values), 3)
        anomaly_max = round(max(anomaly_values), 3)
    else:
        anomaly_min = None
        anomaly_max = None

    heatmap = {"type": "FeatureCollection", "features": features}
    meta = {
        "cell_count": len(features),
        "ndvi_min": ndvi_min,
        "ndvi_max": ndvi_max,
        "ndvi_mean": ndvi_mean,
        "ndvi_anomaly_min": anomaly_min,
        "ndvi_anomaly_max": anomaly_max,
    }
    return heatmap, meta


def _build_synthetic_ndvi_heatmap(geometry: dict[str, Any], seed: str) -> tuple[dict[str, Any], dict[str, Any]]:
    cells = _build_ndvi_grid_cells(geometry)
    ndvi_by_id: dict[str, float] = {}
    anomaly_by_id: dict[str, float] = {}
    for cell in cells:
        cell_id = str(cell["id"])
        ndvi = 0.30 + (_hash_ratio(seed + ":" + cell_id) * 0.45)
        anomaly = -0.08 + (_hash_ratio(seed + ":" + cell_id + ":a") * 0.18)
        ndvi_by_id[cell_id] = _clamp(ndvi, 0.05, 0.95)
        anomaly_by_id[cell_id] = _clamp(anomaly, -0.25, 0.25)
    return _build_ndvi_heatmap(cells, ndvi_by_id, anomaly_by_id)


def _sample_modis_ndvi_heatmap(
    ee: Any,
    geometry: dict[str, Any],
    mod13_latest: Any,
    mod13_baseline: Any,
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    cells = _build_ndvi_grid_cells(geometry)
    if not cells:
        return None

    points = []
    for cell in cells:
        center_lon, center_lat = cell["center"]
        points.append(ee.Feature(ee.Geometry.Point([center_lon, center_lat]), {"cell_id": str(cell["id"])}))
    points_fc = ee.FeatureCollection(points)

    try:
        latest_features = (
            mod13_latest.select(["NDVI"])
            .sampleRegions(collection=points_fc, scale=250, geometries=False)
            .getInfo()
            .get("features", [])
        )
        baseline_features = (
            mod13_baseline.select(["NDVI"])
            .sampleRegions(collection=points_fc, scale=250, geometries=False)
            .getInfo()
            .get("features", [])
        )
    except Exception:
        return None

    latest_by_id: dict[str, float] = {}
    for feature in latest_features:
        props = feature.get("properties", {})
        cell_id = str(props.get("cell_id"))
        ndvi_raw = props.get("NDVI")
        if ndvi_raw is None:
            continue
        latest_by_id[cell_id] = _clamp(float(ndvi_raw) * 0.0001, -0.2, 1.0)

    baseline_by_id: dict[str, float] = {}
    for feature in baseline_features:
        props = feature.get("properties", {})
        cell_id = str(props.get("cell_id"))
        ndvi_raw = props.get("NDVI")
        if ndvi_raw is None:
            continue
        baseline_by_id[cell_id] = _clamp(float(ndvi_raw) * 0.0001, -0.2, 1.0)

    anomaly_by_id: dict[str, float] = {}
    for cell_id, ndvi_val in latest_by_id.items():
        baseline_val = baseline_by_id.get(cell_id)
        if baseline_val is None:
            continue
        anomaly_by_id[cell_id] = ndvi_val - baseline_val

    return _build_ndvi_heatmap(cells, latest_by_id, anomaly_by_id)


def _synthetic_territorial_context(
    geometry: dict[str, Any],
    spatial_context: dict[str, Any],
    analysis_timestamp: datetime,
) -> dict[str, Any]:
    seed = f"{spatial_context['centroid_lat']}:{spatial_context['centroid_lon']}:{ensure_utc(analysis_timestamp).date()}"
    ndvi = round(0.38 + _hash_ratio(seed + ":ndvi") * 0.34, 3)
    evi = round(0.28 + _hash_ratio(seed + ":evi") * 0.29, 3)
    lst_c = round(30 + _hash_ratio(seed + ":lst") * 8.5, 1)
    cloud_cover = round(5 + _hash_ratio(seed + ":cloud") * 35, 1)

    ndvi_norm = _clamp((0.68 - ndvi) / 0.48, 0.0, 1.0)
    lst_norm = _clamp((lst_c - 28) / 14, 0.0, 1.0)
    vegetation_stress = round(_clamp((0.65 * ndvi_norm) + (0.35 * lst_norm), 0.0, 1.0), 3)
    soil_buffer = round(_clamp((evi - 0.2) / 0.45, 0.0, 1.0), 3)
    vulnerability = round((vegetation_stress * 0.55) + ((1.0 - soil_buffer) * 0.45), 3)

    ndvi_timeseries = []
    base_dt = ensure_utc(analysis_timestamp).replace(hour=0, minute=0, second=0, microsecond=0)
    for idx in range(5):
        dt = base_dt - timedelta(days=(4 - idx) * 10)
        drift = -0.03 * (4 - idx)
        ndvi_timeseries.append({"date": dt.date().isoformat(), "ndvi": round(_clamp(ndvi + drift, 0.1, 0.9), 3)})

    heatmap_seed = f"{seed}:ndvi_heatmap"
    ndvi_heatmap, ndvi_heatmap_meta = _build_synthetic_ndvi_heatmap(geometry, heatmap_seed)

    return {
        "source": "synthetic",
        "provider": "SafraViva Synthetic Territory",
        "last_image": to_iso_z(base_dt - timedelta(days=2)),
        "cloud_cover_pct": cloud_cover,
        "ndvi": ndvi,
        "evi": evi,
        "lst_c": lst_c,
        "ndvi_timeseries": ndvi_timeseries,
        "vegetation_stress_index": vegetation_stress,
        "soil_water_buffer_index": soil_buffer,
        "vulnerability_index": vulnerability,
        "alphaearth_cluster": f"mt_cluster_{int(_hash_ratio(seed + ':cluster') * 5) + 1}",
        "ndvi_heatmap": ndvi_heatmap,
        "ndvi_heatmap_meta": ndvi_heatmap_meta,
        "signals": [
            f"NDVI medio recente: {ndvi} (fallback sintetico).",
            f"EVI medio recente: {evi} (fallback sintetico).",
            f"LST medio recente: {lst_c} C (fallback sintetico).",
        ],
    }


def _try_get_gee_territorial_context(
    geometry: dict[str, Any],
    spatial_context: dict[str, Any],
    analysis_timestamp: datetime,
) -> dict[str, Any] | None:
    ee, _status = get_ee_client()
    if ee is None:
        return None

    try:
        analysis_utc = ensure_utc(analysis_timestamp)
        end_dt = analysis_utc + timedelta(days=1)
        start_60d = analysis_utc - timedelta(days=60)
        start_30d = analysis_utc - timedelta(days=30)
        polygon = to_ee_polygon(ee, geometry)

        mod13 = (
            ee.ImageCollection("MODIS/061/MOD13Q1")
            .filterBounds(polygon)
            .filterDate(to_iso_z(start_60d), to_iso_z(end_dt))
            .sort("system:time_start")
        )
        if float(mod13.size().getInfo()) == 0:
            return None

        mod13_latest = ee.Image(mod13.sort("system:time_start", False).first())
        ndvi_raw = _reduce_mean(ee, mod13_latest.select(["NDVI"]), polygon, scale=250)
        evi_raw = _reduce_mean(ee, mod13_latest.select(["EVI"]), polygon, scale=250)
        if ndvi_raw is None or evi_raw is None:
            return None

        ndvi = _clamp(ndvi_raw * 0.0001, -0.2, 1.0)
        evi = _clamp(evi_raw * 0.0001, -0.2, 1.0)
        mod13_baseline = ee.Image(mod13.mean())

        mod11 = (
            ee.ImageCollection("MODIS/061/MOD11A2")
            .filterBounds(polygon)
            .filterDate(to_iso_z(start_30d), to_iso_z(end_dt))
            .sort("system:time_start", False)
        )
        lst_c = 33.0
        if float(mod11.size().getInfo()) > 0:
            mod11_latest = ee.Image(mod11.first())
            lst_raw = _reduce_mean(ee, mod11_latest.select(["LST_Day_1km"]), polygon, scale=1_000)
            if lst_raw is not None:
                lst_c = (lst_raw * 0.02) - 273.15

        s2 = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(polygon)
            .filterDate(to_iso_z(start_30d), to_iso_z(end_dt))
        )
        cloud_cover = 15.0
        last_image_iso = to_iso_z(analysis_utc - timedelta(days=2))
        if float(s2.size().getInfo()) > 0:
            cloud_mean = s2.aggregate_mean("CLOUDY_PIXEL_PERCENTAGE").getInfo()
            if cloud_mean is not None:
                cloud_cover = float(cloud_mean)
            last_millis = s2.aggregate_max("system:time_start").getInfo()
            if last_millis:
                last_image_iso = to_iso_z(datetime.utcfromtimestamp(float(last_millis) / 1000.0))

        ndvi_timeseries: list[dict[str, Any]] = []
        mod13_list = mod13.sort("system:time_start", False).limit(5).getInfo().get("features", [])
        for feature in reversed(mod13_list):
            props = feature.get("properties", {})
            ts = props.get("system:time_start")
            if ts:
                date_str = datetime.utcfromtimestamp(float(ts) / 1000.0).date().isoformat()
            else:
                date_str = analysis_utc.date().isoformat()
            image = ee.Image(feature["id"])
            ts_ndvi_raw = _reduce_mean(ee, image.select(["NDVI"]), polygon, scale=250)
            if ts_ndvi_raw is None:
                continue
            ndvi_timeseries.append({"date": date_str, "ndvi": round(_clamp(ts_ndvi_raw * 0.0001, -0.2, 1.0), 3)})

        heatmap_result = _sample_modis_ndvi_heatmap(ee, geometry, mod13_latest, mod13_baseline)
        if heatmap_result is None:
            seed_for_heatmap = f"{spatial_context['centroid_lat']}:{spatial_context['centroid_lon']}:{analysis_utc.date()}"
            ndvi_heatmap, ndvi_heatmap_meta = _build_synthetic_ndvi_heatmap(geometry, seed_for_heatmap)
        else:
            ndvi_heatmap, ndvi_heatmap_meta = heatmap_result

        ndvi_norm = _clamp((0.68 - ndvi) / 0.48, 0.0, 1.0)
        lst_norm = _clamp((lst_c - 28) / 14, 0.0, 1.0)
        vegetation_stress = round(_clamp((0.65 * ndvi_norm) + (0.35 * lst_norm), 0.0, 1.0), 3)
        soil_buffer = round(_clamp((evi - 0.2) / 0.45, 0.0, 1.0), 3)
        vulnerability = round((vegetation_stress * 0.55) + ((1.0 - soil_buffer) * 0.45), 3)

        seed = f"{spatial_context['centroid_lat']}:{spatial_context['centroid_lon']}"
        return {
            "source": "gee",
            "provider": "Google Earth Engine (MODIS/Sentinel-2)",
            "last_image": last_image_iso,
            "cloud_cover_pct": round(cloud_cover, 1),
            "ndvi": round(ndvi, 3),
            "evi": round(evi, 3),
            "lst_c": round(lst_c, 1),
            "ndvi_timeseries": ndvi_timeseries,
            "vegetation_stress_index": vegetation_stress,
            "soil_water_buffer_index": soil_buffer,
            "vulnerability_index": vulnerability,
            "alphaearth_cluster": f"mt_cluster_{int(_hash_ratio(seed + ':cluster') * 5) + 1}",
            "ndvi_heatmap": ndvi_heatmap,
            "ndvi_heatmap_meta": ndvi_heatmap_meta,
            "signals": [
                f"NDVI medio recente: {round(ndvi, 3)} (MOD13Q1).",
                f"EVI medio recente: {round(evi, 3)} (MOD13Q1).",
                f"LST medio recente: {round(lst_c, 1)} C (MOD11A2).",
            ],
        }
    except Exception:
        return None


def get_territorial_context(
    geometry: dict[str, Any],
    spatial_context: dict[str, Any],
    analysis_timestamp: datetime,
) -> dict[str, Any]:
    use_gee = os.environ.get("USE_GEE_TERRITORY", "true").strip().lower() not in {"0", "false", "no"}
    if use_gee:
        gee_context = _try_get_gee_territorial_context(geometry, spatial_context, analysis_timestamp)
        if gee_context is not None:
            return gee_context
    return _synthetic_territorial_context(geometry, spatial_context, analysis_timestamp)
