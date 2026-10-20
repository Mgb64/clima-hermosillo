# Clima Hermosillo — Streamlit, Open-Meteo, PostgreSQL y Docker

## Requisitos
Docker Desktop o Docker Engine con Docker Compose.

## Iniciar
Desde esta carpeta:

```bash
docker compose up --build -d
docker compose logs -f collector
```

Abrir: http://localhost:8501

## Consultar los datos
```bash
docker compose exec db psql -U clima -d clima -c "SELECT * FROM observations ORDER BY fetched_at DESC LIMIT 3;"
docker compose exec db psql -U clima -d clima -c "SELECT COUNT(*) FROM forecasts;"
docker compose exec db psql -U clima -d clima -c "SELECT * FROM comparisons ORDER BY fetched_at DESC LIMIT 3;"
```

## Detener
```bash
docker compose down
```

`docker compose down -v` también elimina los datos de PostgreSQL.

## Arquitectura
Open-Meteo (externa) -> collector (Ubuntu-based Python container) -> PostgreSQL -> Streamlit (Python container) -> navegador.

La API se consulta cada 600 segundos. La página consulta la BD cada 60 segundos.

## Tablas
- `observations`: instantáneas de las condiciones actuales estimadas por Open-Meteo.
- `forecasts`: pronósticos horarios, con `fetched_at` y `forecast_for` para conservar las versiones.
- `comparisons`: predicción hecha 24 horas antes vs dato actual estimado, alineado por hora.

## Precisión
Open-Meteo proporciona estimaciones de modelos, no lecturas directas de estación local. La lluvia instantánea y la lluvia acumulada por hora son intervalos distintos; la comparación de precipitación usa la serie horaria. Los datos históricos locales se acumulan con el funcionamiento del collector.

## Fuentes
- https://open-meteo.com/en/docs
- https://open-meteo.com/en/docs/previous-runs-api
