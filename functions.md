## Contrato de retorno para o frontend

### Inputs esperados do frontend
O frontend envia:

- `geometry`: polígono da área desenhada pelo usuário
- `culture`: cultura selecionada (ex.: soja, milho, algodão)
- `sowing_date`: data de plantio
- `crop_stage` *(opcional)*: estágio da cultura
- `irrigated`: irrigado ou não
- `analysis_timestamp`: timestamp da análise
- `field_id` *(opcional)*: identificador da área
- `property_name` *(opcional)*: nome da propriedade

---

## O que o backend deriva a partir disso

Com base nos inputs, o backend calcula:

- centroide (`centroid_lat`, `centroid_lon`)
- bounding box / extremos
- área em hectares (`area_ha`)
- município(s) interceptado(s)
- UF
- forecast climático para a área
- métricas agregadas de clima
- score de risco
- alertas e recomendação
- payload para mapa e gráficos

---

## Funções e retornos para o frontend

### 1. `derive_spatial_context(inputs)`
Deriva informações espaciais básicas a partir do polígono.

**Retorna:**
- `centroid_lat`
- `centroid_lon`
- `bbox_min_lat`
- `bbox_max_lat`
- `bbox_min_lon`
- `bbox_max_lon`
- `area_ha`
- `municipio`
- `uf`

---

### 2. `get_climate_forecast(spatial_context, analysis_timestamp)`
Consulta o forecast climático para a área.

**Retorna:**
- `forecast_run_timestamp`
- `precip_forecast_7d_mm`
- `precip_forecast_14d_mm`
- `temp_mean_7d_c`
- `temp_max_7d_c`
- `humidity_mean_7d_pct`
- `wind_mean_7d_ms`
- `forecast_timeseries`

**Formato de `forecast_timeseries`:**
- `forecast_time`
- `precip_mm`
- `temp_c`
- `humidity_pct`

---

### 3. `get_agro_context(inputs, spatial_context)`
Enriquece a análise com contexto agrícola e territorial.

**Retorna:**
- `culture`
- `sowing_date`
- `crop_stage`
- `irrigated`
- `zarc_flag`
- `historical_yield_context` *(se disponível)*
- `territorial_context` *(ex.: sinais satelitais / AlphaEarth)*

---

### 4. `calculate_risk_score(climate_data, agro_context)`
Calcula o risco principal do MVP.

**Retorna:**
- `risk_score` (0 a 100)
- `risk_level` (`baixo`, `moderado`, `alto`, `crítico`)
- `risk_flags`

**Formato de `risk_flags`:**
- `dry_risk_flag`
- `heat_risk_flag`
- `outside_zarc_flag`
- `vegetation_stress_flag`

---

### 5. `generate_alerts_and_recommendations(risk_score, climate_data, agro_context)`
Traduz o risco em informação acionável.

**Retorna:**
- `primary_alert`
- `recommended_action`
- `copilot_response`

**Formato de `copilot_response`:**
- `summary`
- `why` (lista de fatores principais)
- `action`

---

### 6. `build_map_layer(inputs, risk_score)`
Monta a camada pronta para o mapa.

**Retorna:**
- `geometry`
- `fill_color`
- `stroke_color`
- `tooltip_summary`

---

### 7. `build_frontend_response(...)`
Agrega tudo em um payload final pronto para renderização.

**Retorna:**
- `field_info`
- `summary`
- `metrics`
- `risk_flags`
- `forecast_timeseries`
- `map_layer`
- `copilot_response`

---

## Estrutura final esperada pelo frontend

```json
{
  "field_info": {
    "field_id": "talhao_01",
    "property_name": "Fazenda Exemplo",
    "culture": "soja",
    "municipio": "Sorriso",
    "uf": "MT",
    "area_ha": 124.8,
    "irrigated": false
  },
  "summary": {
    "risk_score": 78,
    "risk_level": "alto",
    "primary_alert": "Risco elevado de estresse hídrico nos próximos 10 dias.",
    "recommended_action": "Priorizar monitoramento e irrigação nos talhões mais sensíveis.",
    "analysis_timestamp": "2026-04-11T20:30:00Z",
    "forecast_run_timestamp": "2026-04-11T18:00:00Z"
  },
  "metrics": {
    "precip_forecast_7d_mm": 18.4,
    "precip_forecast_14d_mm": 42.7,
    "temp_mean_7d_c": 28.1,
    "temp_max_7d_c": 34.6,
    "humidity_mean_7d_pct": 61.2
  },
  "risk_flags": {
    "dry_risk_flag": true,
    "heat_risk_flag": true,
    "outside_zarc_flag": false,
    "vegetation_stress_flag": true
  },
  "forecast_timeseries": [
    {
      "forecast_time": "2026-04-12T00:00:00Z",
      "precip_mm": 1.1,
      "temp_c": 23.6,
      "humidity_pct": 87.2
    }
  ],
  "map_layer": {
    "geometry": {
      "type": "Polygon",
      "coordinates": [[[...]]]
    },
    "fill_color": "#ef4444",
    "stroke_color": "#991b1b",
    "tooltip_summary": "Risco alto | soja | precipitação baixa nos próximos 7 dias"
  },
  "copilot_response": {
    "summary": "Esta área apresenta risco alto de estresse hídrico nos próximos dias.",
    "why": [
      "Baixa precipitação prevista.",
      "Temperaturas elevadas na janela de 7 dias.",
      "Maior vulnerabilidade da área no contexto territorial."
    ],
    "action": "Priorize monitoramento e manejo hídrico nesta área."
  }
}