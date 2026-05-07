# Frontend Guide - Satellite Imagery Layer

Este guia descreve como usar a nova camada satelital retornada pelo backend no endpoint:

- `POST /api/v1/analysis`
- `POST /api/v1/analyze` (alias)

## 1. Onde ler no payload

No resultado da analise:

- `data_sources.satellite.imagery_layer`

Estrutura esperada:

```json
{
  "source": "gee",
  "provider": "Google Earth Engine",
  "dataset": "COPERNICUS/S2_SR_HARMONIZED",
  "mode": "xyz_tiles",
  "style": "true_color",
  "tile_url_template": "https://.../{z}/{x}/{y}?...",
  "bounds": {
    "min_lat": -23.58,
    "max_lat": -23.50,
    "min_lon": -46.70,
    "max_lon": -46.60
  },
  "recommended_zoom": 13,
  "min_zoom": 8,
  "max_zoom": 19,
  "display_min_zoom": 15,
  "display_max_zoom": 19,
  "availability": "high_zoom_only",
  "image_date": "2026-05-02",
  "cloud_cover_pct": 12.7,
  "attribution": "Contains modified Copernicus Sentinel data 2026"
}
```

## 2. Comportamento recomendado no mapa

1. Sempre ajustar viewport para `bounds` da area analisada.
2. Usar `recommended_zoom` como ponto inicial.
3. Mostrar camada satelital somente quando `zoom >= display_min_zoom`.
4. Quando zoom menor que `display_min_zoom`, usar base map leve (street/light) para performance.
5. Manter poligono do talhao por cima da imagem (stroke destacado).
6. Manter `ndvi_heatmap` como overlay opcional no mesmo zoom alto.

## 3. Exemplo de logica (Leaflet)

```ts
const imagery = analysis.data_sources?.satellite?.imagery_layer
if (!imagery?.tile_url_template) return

const bounds = L.latLngBounds(
  [imagery.bounds.min_lat, imagery.bounds.min_lon],
  [imagery.bounds.max_lat, imagery.bounds.max_lon]
)
map.fitBounds(bounds, { padding: [24, 24] })
map.setZoom(imagery.recommended_zoom ?? 14)

const satLayer = L.tileLayer(imagery.tile_url_template, {
  minZoom: imagery.min_zoom ?? 8,
  maxZoom: imagery.max_zoom ?? 19,
  attribution: imagery.attribution ?? "",
  opacity: 0.95
})

const displayMin = imagery.display_min_zoom ?? 15
const displayMax = imagery.display_max_zoom ?? 19

const updateLayerVisibility = () => {
  const z = map.getZoom()
  const shouldShow = z >= displayMin && z <= displayMax
  if (shouldShow && !map.hasLayer(satLayer)) satLayer.addTo(map)
  if (!shouldShow && map.hasLayer(satLayer)) map.removeLayer(satLayer)
}

map.on("zoomend", updateLayerVisibility)
updateLayerVisibility()
```

## 4. Precisao e trade-off (recomendado para MVP)

1. Dataset recomendado: Sentinel-2 true color (10m) para identificar talhao e entorno.
2. Nao usar imagem submetrica no MVP (custo e peso maiores).
3. Melhor UX: satelite apenas em zoom alto (>= 15) para leitura util sem poluir a tela.
4. Em zoom baixo, priorizar performance e contexto (poligonos, score, alertas).

## 5. Fallback e resiliencia

1. `source = gee`: camada principal via GEE.
2. `source = fallback_xyz`: fallback automatico para basemap satelital publico.
3. Frontend deve tratar ambos sem diferenca de renderizacao (sempre XYZ tile).
4. Se `tile_url_template` faltar, ocultar toggle satelite e seguir com mapa vetorial.
