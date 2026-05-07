import os
from datetime import datetime, timedelta
from typing import Any

from src.ingest.gee_client import get_ee_client, to_ee_polygon
from src.utils.time import ensure_utc, to_iso_z


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _recommended_zoom(area_ha: float) -> int:
    if area_ha <= 20:
        return 17
    if area_ha <= 80:
        return 16
    if area_ha <= 250:
        return 15
    if area_ha <= 1_000:
        return 14
    if area_ha <= 5_000:
        return 13
    return 12


def _display_min_zoom() -> int:
    raw = os.environ.get("SATELLITE_DISPLAY_MIN_ZOOM", "15").strip()
    try:
        parsed = int(raw)
    except Exception:
        parsed = 15
    return max(10, min(19, parsed))


def _build_bounds(spatial_context: dict[str, Any]) -> dict[str, float]:
    return {
        "min_lat": float(spatial_context["bbox_min_lat"]),
        "max_lat": float(spatial_context["bbox_max_lat"]),
        "min_lon": float(spatial_context["bbox_min_lon"]),
        "max_lon": float(spatial_context["bbox_max_lon"]),
    }


def _sentinel_vis_params() -> dict[str, Any]:
    # COPERNICUS/S2_SR_HARMONIZED bands are SR scaled by 10000.
    return {"bands": ["B4", "B3", "B2"], "min": 200, "max": 3200, "gamma": 1.15}


def _try_get_gee_true_color_layer(
    geometry: dict[str, Any],
    spatial_context: dict[str, Any],
    analysis_timestamp: datetime,
) -> dict[str, Any] | None:
    ee, gee_status = get_ee_client()
    if ee is None:
        return None

    try:
        analysis_utc = ensure_utc(analysis_timestamp)
        lookback_days = int(os.environ.get("SATELLITE_LOOKBACK_DAYS", "120"))
        cloud_threshold = float(os.environ.get("SATELLITE_MAX_CLOUD_PCT", "35"))
        cloud_relaxed = float(os.environ.get("SATELLITE_MAX_CLOUD_PCT_RELAXED", "75"))
        top_n_images = int(os.environ.get("SATELLITE_MOSAIC_TOP_N", "3"))

        start_dt = analysis_utc - timedelta(days=max(15, lookback_days))
        end_dt = analysis_utc + timedelta(days=1)
        polygon = to_ee_polygon(ee, geometry)

        base_collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(polygon)
            .filterDate(to_iso_z(start_dt), to_iso_z(end_dt))
        )
        base_count = int(_safe_float(base_collection.size().getInfo()))
        if base_count <= 0:
            return None

        filtered = base_collection.filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", cloud_threshold))
        filtered_count = int(_safe_float(filtered.size().getInfo()))
        if filtered_count <= 0:
            filtered = base_collection.filter(ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", cloud_relaxed))
            filtered_count = int(_safe_float(filtered.size().getInfo()))
        if filtered_count <= 0:
            filtered = base_collection
            filtered_count = base_count

        sorted_collection = filtered.sort("CLOUDY_PIXEL_PERCENTAGE")
        best_image = ee.Image(sorted_collection.first())
        image_time_start = best_image.get("system:time_start").getInfo()
        image_cloud_cover = best_image.get("CLOUDY_PIXEL_PERCENTAGE").getInfo()

        mosaic_count = max(1, min(5, top_n_images))
        true_color = ee.Image(sorted_collection.limit(mosaic_count).median()).clip(polygon)
        map_id = true_color.getMapId(_sentinel_vis_params())
        tile_url_template = map_id["tile_fetcher"].url_format

        if image_time_start:
            image_date = datetime.utcfromtimestamp(float(image_time_start) / 1000.0).date().isoformat()
        else:
            image_date = None

        area_ha = float(spatial_context["area_ha"])
        display_min_zoom = _display_min_zoom()
        return {
            "source": "gee",
            "provider": "Google Earth Engine",
            "dataset": "COPERNICUS/S2_SR_HARMONIZED",
            "mode": "xyz_tiles",
            "style": "true_color",
            "tile_url_template": tile_url_template,
            "bounds": _build_bounds(spatial_context),
            "recommended_zoom": _recommended_zoom(area_ha),
            "min_zoom": 8,
            "max_zoom": 19,
            "display_min_zoom": display_min_zoom,
            "display_max_zoom": 19,
            "availability": "high_zoom_only",
            "image_date": image_date,
            "cloud_cover_pct": round(_safe_float(image_cloud_cover, 0.0), 1) if image_cloud_cover is not None else None,
            "image_count_considered": int(filtered_count),
            "attribution": f"Contains modified Copernicus Sentinel data {analysis_utc.year}",
            "gee_status": gee_status,
        }
    except Exception:
        return None


def _fallback_satellite_layer(spatial_context: dict[str, Any], analysis_timestamp: datetime) -> dict[str, Any]:
    area_ha = float(spatial_context["area_ha"])
    analysis_utc = ensure_utc(analysis_timestamp)
    display_min_zoom = _display_min_zoom()
    return {
        "source": "fallback_xyz",
        "provider": "Esri World Imagery",
        "dataset": "ArcGIS/World_Imagery",
        "mode": "xyz_tiles",
        "style": "true_color",
        "tile_url_template": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "bounds": _build_bounds(spatial_context),
        "recommended_zoom": _recommended_zoom(area_ha),
        "min_zoom": 8,
        "max_zoom": 19,
        "display_min_zoom": display_min_zoom,
        "display_max_zoom": 19,
        "availability": "high_zoom_only",
        "image_date": None,
        "cloud_cover_pct": None,
        "image_count_considered": None,
        "attribution": "Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community",
        "generated_at": to_iso_z(analysis_utc),
    }


def get_satellite_imagery_layer(
    geometry: dict[str, Any],
    spatial_context: dict[str, Any],
    analysis_timestamp: datetime,
) -> dict[str, Any]:
    use_gee = os.environ.get("USE_GEE_SATELLITE_IMAGERY", "true").strip().lower() not in {"0", "false", "no"}
    if use_gee:
        gee_layer = _try_get_gee_true_color_layer(
            geometry=geometry,
            spatial_context=spatial_context,
            analysis_timestamp=analysis_timestamp,
        )
        if gee_layer is not None:
            return gee_layer
    return _fallback_satellite_layer(spatial_context=spatial_context, analysis_timestamp=analysis_timestamp)
