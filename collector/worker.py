import os
import time
import logging
from datetime import datetime, timezone
import requests
import psycopg

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
DB = os.environ['DATABASE_URL']
INTERVAL = int(os.getenv('UPDATE_SECONDS', '600'))
LAT, LON = 29.0729, -110.9559
COMMON = {'latitude': LAT, 'longitude': LON, 'timezone': 'America/Hermosillo'}

def request_json(url, params):
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def sample():
    live = request_json('https://api.open-meteo.com/v1/forecast', {
        **COMMON,
        'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m',
        'hourly': 'temperature_2m,precipitation,precipitation_probability',
        'forecast_days': 3
    })
    previous = request_json('https://previous-runs-api.open-meteo.com/v1/forecast', {
        **COMMON,
        'hourly': 'temperature_2m_previous_day1,precipitation_previous_day1',
        'past_days': 1, 'forecast_days': 1
    })
    now = datetime.now(timezone.utc)
    current = live['current']
    obs_time = datetime.fromisoformat(current['time'])
    # Current 'precipitation' describes a short recent interval; the hourly
    # forecast precipitation is a 1-hour accumulation. Avoid conflating them.
    hourly = live['hourly']
    prior_hourly = previous.get('hourly', {})
    prior_times = prior_hourly.get('time', [])
    prior_map = {t: i for i, t in enumerate(prior_times)}
    valid_hour = obs_time.replace(minute=0, second=0, microsecond=0)
    match = prior_map.get(valid_hour.isoformat(timespec='minutes'))
    def old_value(field):
        values = prior_hourly.get(field, [])
        return values[match] if match is not None and match < len(values) else None
    with psycopg.connect(DB) as conn:
        with conn.cursor() as cur:
            cur.execute('''INSERT INTO observations
                (fetched_at, observed_at, temperature, humidity, apparent_temperature, precipitation, wind_speed)
                VALUES (%s,%s,%s,%s,%s,%s,%s)''',
                (now, obs_time, current.get('temperature_2m'), current.get('relative_humidity_2m'),
                 current.get('apparent_temperature'), current.get('precipitation'), current.get('wind_speed_10m')))
            rows = [(now, datetime.fromisoformat(t), a, b, c) for t, a, b, c in zip(
                hourly['time'], hourly['temperature_2m'], hourly['precipitation'], hourly['precipitation_probability'])]
            cur.executemany('''INSERT INTO forecasts
                (fetched_at, forecast_for, temperature, precipitation, precipitation_probability)
                VALUES (%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING''', rows)
            # Comparisons at same hour: current estimated temperature vs forecast
            # issued 24h earlier. Rain: compare hourly modeled precipitation
            # (not current 15-min interval) with 24h-ahead hourly prediction.
            live_hours = {t: i for i, t in enumerate(hourly['time'])}
            idx = live_hours.get(valid_hour.isoformat(timespec='minutes'))
            current_hour_rain = hourly['precipitation'][idx] if idx is not None else None
            cur.execute('''INSERT INTO comparisons
                (fetched_at, valid_hour, current_temperature, predicted_temperature_24h,
                 current_precipitation, predicted_precipitation_24h)
                 VALUES (%s,%s,%s,%s,%s,%s)''',
                (now, valid_hour, current.get('temperature_2m'), old_value('temperature_2m_previous_day1'),
                 current_hour_rain, old_value('precipitation_previous_day1')))
    logging.info('Datos almacenados: %s, %s pronósticos', obs_time, len(rows))

if __name__ == '__main__':
    while True:
        try:
            sample()
        except Exception:
            logging.exception('No se pudo actualizar; se intentará de nuevo')
        time.sleep(INTERVAL)
