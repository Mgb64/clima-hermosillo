CREATE TABLE IF NOT EXISTS observations (
  id BIGSERIAL PRIMARY KEY,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  observed_at TIMESTAMP NOT NULL,
  temperature DOUBLE PRECISION,
  humidity DOUBLE PRECISION,
  apparent_temperature DOUBLE PRECISION,
  precipitation DOUBLE PRECISION,
  wind_speed DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS ix_observations_fetched ON observations(fetched_at DESC);
CREATE TABLE IF NOT EXISTS forecasts (
  id BIGSERIAL PRIMARY KEY,
  fetched_at TIMESTAMPTZ NOT NULL,
  forecast_for TIMESTAMP NOT NULL,
  temperature DOUBLE PRECISION,
  precipitation DOUBLE PRECISION,
  precipitation_probability DOUBLE PRECISION,
  UNIQUE(fetched_at, forecast_for)
);
CREATE INDEX IF NOT EXISTS ix_forecasts_times ON forecasts(fetched_at DESC, forecast_for);
CREATE TABLE IF NOT EXISTS comparisons (
  id BIGSERIAL PRIMARY KEY,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  valid_hour TIMESTAMP NOT NULL,
  current_temperature DOUBLE PRECISION,
  predicted_temperature_24h DOUBLE PRECISION,
  current_precipitation DOUBLE PRECISION,
  predicted_precipitation_24h DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS ix_comparisons_fetched ON comparisons(fetched_at DESC);
