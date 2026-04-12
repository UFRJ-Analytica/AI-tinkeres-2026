import hashlib
import os
import random
from datetime import datetime, timedelta, timezone
from typing import Any

from src.ingest.gee_client import get_ee_client, to_ee_polygon
from src.utils.time import ensure_utc, to_iso_z


def _round(value: float, digits: int = 1) -> float:
    return round(float(value), digits)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _seed_from_context(lat: float, lon: float, analysis_timestamp: datetime) -> int:
    key = f"{lat:.4f}:{lon:.4f}:{analysis_timestamp.strftime('%Y%m%d')}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _shift_year_safe(value: datetime, years_back: int) -> datetime:
    target_year = value.year - years_back
    try:
        return value.replace(year=target_year)
    except ValueError:
        return value.replace(month=2, day=28, year=target_year)


def _build_daily_series_window(
    daily_totals_by_date: dict[str, float],
    start_dt: datetime,
    end_dt: datetime,
) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    cursor = start_dt
    while cursor < end_dt:
        date_str = cursor.date().isoformat()
        points.append({"date": date_str, "precip_mm": _round(max(0.0, daily_totals_by_date.get(date_str, 0.0)), 1)})
        cursor += timedelta(days=1)
    return points


def _sum_period_subdaily_mm(
    ee: Any,
    collection: Any,
    rate_band: str,
    step_hours: float,
    centroid: Any,
    start_dt: datetime,
    end_dt: datetime,
    scale: int,
) -> float | None:
    try:
        image_sum = collection.filterDate(to_iso_z(start_dt), to_iso_z(end_dt)).select([rate_band]).sum().multiply(step_hours)
        values = image_sum.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=centroid,
            scale=scale,
            bestEffort=True,
            maxPixels=1_000_000_000,
        ).getInfo()
        if not values:
            return None
        band_value = values.get(rate_band)
        if band_value is None:
            return None
        return float(band_value)
    except Exception:
        return None


def _extract_subdaily_daily_totals(
    ee: Any,
    collection: Any,
    centroid: Any,
    rate_band: str,
    step_hours: float,
    start_dt: datetime,
    end_dt: datetime,
    scale: int,
) -> dict[str, float] | None:
    try:
        rows = (
            collection.filterDate(to_iso_z(start_dt), to_iso_z(end_dt))
            .select([rate_band])
            .getRegion(centroid, scale)
            .getInfo()
        )
    except Exception:
        return None

    if not rows or len(rows) < 2:
        return None

    header = rows[0]
    if "time" not in header or rate_band not in header:
        return None
    time_idx = header.index("time")
    rate_idx = header.index(rate_band)

    daily_totals_by_date: dict[str, float] = {}
    for row in rows[1:]:
        if not row or len(row) <= max(time_idx, rate_idx):
            continue
        ts_ms = _optional_float(row[time_idx])
        rate_val = _optional_float(row[rate_idx])
        if ts_ms is None or rate_val is None:
            continue
        date_str = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).date().isoformat()
        mm = max(0.0, rate_val) * step_hours
        daily_totals_by_date[date_str] = daily_totals_by_date.get(date_str, 0.0) + mm

    return daily_totals_by_date


def _build_history_payload(
    *,
    provider: str,
    dataset: str,
    gee_status: str,
    source_label: str,
    analysis_day: datetime,
    latest_day_start: datetime,
    start_30d: datetime,
    end_dt: datetime,
    timeseries_30d: list[dict[str, Any]],
    precip_climatology_30d_mm: float | None,
) -> dict[str, Any]:
    precip_observed_30d_mm = sum(point["precip_mm"] for point in timeseries_30d)
    precip_observed_7d_mm = sum(point["precip_mm"] for point in timeseries_30d[-7:])
    dry_days_30d = sum(1 for point in timeseries_30d if point["precip_mm"] < 1.0)

    precip_anomaly_30d_mm = None
    precip_anomaly_30d_pct = None
    if precip_climatology_30d_mm is not None and precip_climatology_30d_mm > 0:
        precip_anomaly_30d_mm = precip_observed_30d_mm - precip_climatology_30d_mm
        precip_anomaly_30d_pct = (precip_anomaly_30d_mm / precip_climatology_30d_mm) * 100.0

    data_lag_days = max(0, (analysis_day - latest_day_start).days)
    signals = [
        f"{source_label} observado 7d: {_round(precip_observed_7d_mm)} mm.",
        f"{source_label} observado 30d: {_round(precip_observed_30d_mm)} mm.",
        f"Dias secos (<1mm) em 30d: {dry_days_30d}.",
        f"Ultimo dado {source_label} disponivel em {latest_day_start.date().isoformat()} (defasagem: {data_lag_days} dias).",
    ]
    if precip_anomaly_30d_pct is not None:
        signals.append(f"Anomalia de precipitacao 30d: {_round(precip_anomaly_30d_pct, 1)}%.")

    return {
        "source": "gee",
        "provider": provider,
        "dataset": dataset,
        "gee_status": gee_status,
        "window_start": to_iso_z(start_30d),
        "window_end": to_iso_z(end_dt),
        "latest_observed_date": latest_day_start.date().isoformat(),
        "data_lag_days": int(data_lag_days),
        "precip_observed_7d_mm": _round(precip_observed_7d_mm, 1),
        "precip_observed_30d_mm": _round(precip_observed_30d_mm, 1),
        "precip_climatology_30d_mm": _round(precip_climatology_30d_mm, 1) if precip_climatology_30d_mm is not None else None,
        "precip_anomaly_30d_mm": _round(precip_anomaly_30d_mm, 1) if precip_anomaly_30d_mm is not None else None,
        "precip_anomaly_30d_pct": _round(precip_anomaly_30d_pct, 1) if precip_anomaly_30d_pct is not None else None,
        "dry_days_30d": int(dry_days_30d),
        "timeseries_30d": timeseries_30d,
        "signals": signals,
    }


def _try_get_gee_subdaily_history(
    *,
    spatial_context: dict[str, Any],
    analysis_timestamp: datetime,
    geometry: dict[str, Any] | None,
    collection_id: str,
    dataset_label: str,
    source_label: str,
    rate_band: str,
    step_hours: float,
    scale: int,
    climatology_years: int = 3,
) -> dict[str, Any] | None:
    if geometry is None:
        return None

    ee, gee_status = get_ee_client()
    if ee is None:
        return None

    try:
        analysis_utc = ensure_utc(analysis_timestamp)
        analysis_day = analysis_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        polygon = to_ee_polygon(ee, geometry)
        centroid = ee.Geometry.Point([spatial_context["centroid_lon"], spatial_context["centroid_lat"]])

        base_collection = ee.ImageCollection(collection_id).filterBounds(polygon)
        if _safe_float(base_collection.size().getInfo()) == 0:
            return None

        latest_ms = int(_safe_float(base_collection.aggregate_max("system:time_start").getInfo()))
        if latest_ms <= 0:
            return None

        latest_time = datetime.fromtimestamp(latest_ms / 1000.0, tz=timezone.utc)
        latest_day_start = latest_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = min(analysis_day + timedelta(days=1), latest_day_start + timedelta(days=1))
        start_30d = end_dt - timedelta(days=30)
        start_7d = end_dt - timedelta(days=7)

        daily_totals_by_date = _extract_subdaily_daily_totals(
            ee=ee,
            collection=base_collection,
            centroid=centroid,
            rate_band=rate_band,
            step_hours=step_hours,
            start_dt=start_30d,
            end_dt=end_dt,
            scale=scale,
        )
        if not daily_totals_by_date:
            return None

        timeseries_30d = _build_daily_series_window(daily_totals_by_date, start_30d, end_dt)
        if len(timeseries_30d) < 7:
            return None

        climatology_values: list[float] = []
        for years_back in range(1, climatology_years + 1):
            hist_start = _shift_year_safe(start_30d, years_back)
            hist_end = _shift_year_safe(end_dt, years_back)
            hist_sum = _sum_period_subdaily_mm(
                ee=ee,
                collection=base_collection,
                rate_band=rate_band,
                step_hours=step_hours,
                centroid=centroid,
                start_dt=hist_start,
                end_dt=hist_end,
                scale=scale,
            )
            if hist_sum is not None:
                climatology_values.append(hist_sum)

        precip_climatology_30d_mm = None
        if climatology_values:
            precip_climatology_30d_mm = sum(climatology_values) / len(climatology_values)

        return _build_history_payload(
            provider="Google Earth Engine",
            dataset=dataset_label,
            gee_status=gee_status,
            source_label=source_label,
            analysis_day=analysis_day,
            latest_day_start=latest_day_start,
            start_30d=start_30d,
            end_dt=end_dt,
            timeseries_30d=timeseries_30d,
            precip_climatology_30d_mm=precip_climatology_30d_mm,
        )
    except Exception:
        return None


def _sum_period_daily_mm(
    ee: Any,
    collection: Any,
    band: str,
    centroid: Any,
    start_dt: datetime,
    end_dt: datetime,
    scale: int,
) -> float | None:
    try:
        image_sum = collection.filterDate(to_iso_z(start_dt), to_iso_z(end_dt)).select([band]).sum()
        values = image_sum.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=centroid,
            scale=scale,
            bestEffort=True,
            maxPixels=1_000_000_000,
        ).getInfo()
        if not values:
            return None
        band_value = values.get(band)
        if band_value is None:
            return None
        return float(band_value)
    except Exception:
        return None


def _try_get_gee_chirps_history(
    spatial_context: dict[str, Any],
    analysis_timestamp: datetime,
    geometry: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if geometry is None:
        return None

    ee, gee_status = get_ee_client()
    if ee is None:
        return None

    try:
        analysis_utc = ensure_utc(analysis_timestamp)
        analysis_day = analysis_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        polygon = to_ee_polygon(ee, geometry)
        centroid = ee.Geometry.Point([spatial_context["centroid_lon"], spatial_context["centroid_lat"]])
        base_collection = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").filterBounds(polygon)
        if _safe_float(base_collection.size().getInfo()) == 0:
            return None

        latest_ms = int(_safe_float(base_collection.aggregate_max("system:time_start").getInfo()))
        if latest_ms <= 0:
            return None
        latest_time = datetime.fromtimestamp(latest_ms / 1000.0, tz=timezone.utc)
        latest_day_start = latest_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = min(analysis_day + timedelta(days=1), latest_day_start + timedelta(days=1))
        start_30d = end_dt - timedelta(days=30)

        rows = base_collection.filterDate(to_iso_z(start_30d), to_iso_z(end_dt)).select(["precipitation"]).getRegion(centroid, 5000).getInfo()
        if not rows or len(rows) < 2:
            return None
        header = rows[0]
        time_idx = header.index("time")
        value_idx = header.index("precipitation")
        daily_totals_by_date: dict[str, float] = {}
        for row in rows[1:]:
            if not row or len(row) <= max(time_idx, value_idx):
                continue
            ts_ms = _optional_float(row[time_idx])
            precip = _optional_float(row[value_idx])
            if ts_ms is None or precip is None:
                continue
            date_str = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).date().isoformat()
            daily_totals_by_date[date_str] = max(0.0, float(precip))

        timeseries_30d = _build_daily_series_window(daily_totals_by_date, start_30d, end_dt)
        if len(timeseries_30d) < 7:
            return None

        climatology_values: list[float] = []
        for years_back in range(1, 4):
            hist_start = _shift_year_safe(start_30d, years_back)
            hist_end = _shift_year_safe(end_dt, years_back)
            hist_sum = _sum_period_daily_mm(
                ee=ee,
                collection=base_collection,
                band="precipitation",
                centroid=centroid,
                start_dt=hist_start,
                end_dt=hist_end,
                scale=5000,
            )
            if hist_sum is not None:
                climatology_values.append(hist_sum)

        precip_climatology_30d_mm = None
        if climatology_values:
            precip_climatology_30d_mm = sum(climatology_values) / len(climatology_values)

        return _build_history_payload(
            provider="Google Earth Engine",
            dataset="UCSB-CHG/CHIRPS/DAILY",
            gee_status=gee_status,
            source_label="CHIRPS",
            analysis_day=analysis_day,
            latest_day_start=latest_day_start,
            start_30d=start_30d,
            end_dt=end_dt,
            timeseries_30d=timeseries_30d,
            precip_climatology_30d_mm=precip_climatology_30d_mm,
        )
    except Exception:
        return None


def _get_synthetic_climate_history(spatial_context: dict[str, Any], analysis_timestamp: datetime) -> dict[str, Any]:
    centroid_lat = float(spatial_context["centroid_lat"])
    centroid_lon = float(spatial_context["centroid_lon"])
    analysis_utc = ensure_utc(analysis_timestamp)
    start_30d = analysis_utc.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=29)
    end_30d = start_30d + timedelta(days=30)

    rng = random.Random(_seed_from_context(centroid_lat, centroid_lon, analysis_utc))
    daily_values: list[float] = []
    timeseries_30d: list[dict[str, Any]] = []
    for step in range(30):
        current = start_30d + timedelta(days=step)
        precip_mm = max(0.0, 3.2 + rng.uniform(-2.5, 7.8))
        daily_values.append(precip_mm)
        timeseries_30d.append({"date": current.date().isoformat(), "precip_mm": _round(precip_mm, 1)})

    precip_observed_30d_mm = sum(daily_values)
    precip_observed_7d_mm = sum(daily_values[-7:])
    precip_climatology_30d_mm = precip_observed_30d_mm * (0.92 + rng.uniform(0.0, 0.22))
    precip_anomaly_30d_mm = precip_observed_30d_mm - precip_climatology_30d_mm
    precip_anomaly_30d_pct = (
        (precip_anomaly_30d_mm / precip_climatology_30d_mm) * 100.0
        if precip_climatology_30d_mm > 0
        else 0.0
    )
    dry_days_30d = sum(1 for value in daily_values if value < 1.0)

    return {
        "source": "synthetic",
        "provider": "SafraViva Synthetic Climate History",
        "dataset": "deterministic_mvp_v1",
        "window_start": to_iso_z(start_30d),
        "window_end": to_iso_z(end_30d),
        "latest_observed_date": (end_30d - timedelta(days=1)).date().isoformat(),
        "data_lag_days": 0,
        "precip_observed_7d_mm": _round(precip_observed_7d_mm, 1),
        "precip_observed_30d_mm": _round(precip_observed_30d_mm, 1),
        "precip_climatology_30d_mm": _round(precip_climatology_30d_mm, 1),
        "precip_anomaly_30d_mm": _round(precip_anomaly_30d_mm, 1),
        "precip_anomaly_30d_pct": _round(precip_anomaly_30d_pct, 1),
        "dry_days_30d": int(dry_days_30d),
        "timeseries_30d": timeseries_30d,
        "signals": [
            f"Precipitacao observada 7d: {_round(precip_observed_7d_mm)} mm (fallback sintetico).",
            f"Precipitacao observada 30d: {_round(precip_observed_30d_mm)} mm (fallback sintetico).",
            f"Anomalia 30d: {_round(precip_anomaly_30d_pct, 1)}% (fallback sintetico).",
        ],
    }


def get_climate_history(
    spatial_context: dict[str, Any],
    analysis_timestamp: datetime,
    geometry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    use_gee_imerg = os.environ.get("USE_GEE_IMERG", "true").strip().lower() not in {"0", "false", "no"}
    use_gee_gsmap = os.environ.get("USE_GEE_GSMAP", "true").strip().lower() not in {"0", "false", "no"}
    use_gee_chirps = os.environ.get("USE_GEE_CHIRPS", "true").strip().lower() not in {"0", "false", "no"}

    if use_gee_imerg:
        imerg_data = _try_get_gee_subdaily_history(
            spatial_context=spatial_context,
            analysis_timestamp=analysis_timestamp,
            geometry=geometry,
            collection_id="NASA/GPM_L3/IMERG_V07",
            dataset_label="NASA/GPM_L3/IMERG_V07",
            source_label="IMERG V07",
            rate_band="precipitation",
            step_hours=0.5,
            scale=11_132,
            climatology_years=3,
        )
        if imerg_data is not None:
            return imerg_data

    if use_gee_gsmap:
        gsmap_data = _try_get_gee_subdaily_history(
            spatial_context=spatial_context,
            analysis_timestamp=analysis_timestamp,
            geometry=geometry,
            collection_id="JAXA/GPM_L3/GSMaP/v8/operational",
            dataset_label="JAXA/GPM_L3/GSMaP/v8/operational",
            source_label="GSMaP V8",
            rate_band="hourlyPrecipRate",
            step_hours=1.0,
            scale=11_132,
            climatology_years=2,
        )
        if gsmap_data is not None:
            return gsmap_data

    if use_gee_chirps:
        chirps_data = _try_get_gee_chirps_history(
            spatial_context=spatial_context,
            analysis_timestamp=analysis_timestamp,
            geometry=geometry,
        )
        if chirps_data is not None:
            return chirps_data

    return _get_synthetic_climate_history(spatial_context, analysis_timestamp)

