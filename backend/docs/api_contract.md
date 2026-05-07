# API Contract (MVP)

## Endpoints

- `POST /api/v1/analysis` (principal)
- `POST /api/v1/analyze` (alias)

## Entrada

```json
{
  "field_id": "talhao_01",
  "property_name": "Fazenda Exemplo",
  "culture": "soja",
  "sowing_date": "2026-10-15",
  "crop_stage": null,
  "irrigated": false,
  "analysis_timestamp": "2026-04-11T20:30:00Z",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[-55.81, -12.43], [-55.74, -12.43], [-55.74, -12.49], [-55.81, -12.49], [-55.81, -12.43]]]
  }
}
```

## Saida

```json
{
  "field_info": {},
  "summary": {},
  "metrics": {},
  "risk_flags": {},
  "data_sources": {},
  "forecast_timeseries": [],
  "map_layer": {},
  "copilot_response": {}
}
```

## Funcoes implementadas

- `derive_spatial_context(inputs)`
- `get_climate_forecast(spatial_context, analysis_timestamp)`
- `get_climate_history(spatial_context, analysis_timestamp)`
- `get_territorial_context(geometry, spatial_context, analysis_timestamp)`
- `get_satellite_imagery_layer(geometry, spatial_context, analysis_timestamp)`
- `get_agro_context(inputs, spatial_context)`
- `calculate_risk_score(climate_data, agro_context)`
- `generate_alerts_and_recommendations(risk_result, climate_data, agro_context)`
- `build_map_layer(inputs, risk_result)`
- `build_frontend_response(...)`

## Novo contrato: imagem de satelite para mapa interativo

O endpoint retorna uma camada de imagem em:

- `data_sources.satellite.imagery_layer`

Campos:

- `source`: `gee` ou `fallback_xyz`
- `provider`
- `dataset`
- `mode`: `xyz_tiles`
- `style`: `true_color`
- `tile_url_template`: URL XYZ com `{z}/{y}/{x}`
- `bounds`: `{ min_lat, max_lat, min_lon, max_lon }`
- `recommended_zoom`
- `min_zoom`
- `max_zoom`
- `display_min_zoom` (zoom minimo recomendado para ativar satelite)
- `display_max_zoom`
- `availability`: `high_zoom_only`
- `image_date`
- `cloud_cover_pct`
- `attribution`

Observacoes:

- O backend envia apenas metadados e URL de tiles (payload leve).
- O frontend deve ativar a camada satelital apenas em zoom alto (`display_min_zoom`).
