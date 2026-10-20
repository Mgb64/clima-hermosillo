import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine, text

st.set_page_config(page_title='Clima Hermosillo', page_icon='☀️', layout='wide')
st.title('Clima de Hermosillo')
st.caption('Open-Meteo · actualización de la vista cada 60 segundos · horario de Sonora (UTC−7)')
engine = create_engine(os.environ['DATABASE_URL'].replace('postgresql://', 'postgresql+psycopg://', 1))

@st.cache_data(ttl=50, show_spinner=False)
def load():
    with engine.connect() as conn:
        latest = pd.read_sql(text('SELECT * FROM observations ORDER BY fetched_at DESC LIMIT 1'), conn)
        history = pd.read_sql(text('SELECT * FROM observations ORDER BY fetched_at DESC LIMIT 300'), conn)
        last = pd.read_sql(text('SELECT MAX(fetched_at) AS latest FROM forecasts'), conn).iloc[0]['latest']
        forecast = pd.read_sql(text('SELECT * FROM forecasts WHERE fetched_at = :ts ORDER BY forecast_for'), conn, params={'ts': last}) if pd.notna(last) else pd.DataFrame()
        comparisons = pd.read_sql(text('SELECT * FROM comparisons ORDER BY fetched_at DESC LIMIT 300'), conn)
    return latest, history, forecast, comparisons

@st.fragment(run_every='60s')
def main():
    try:
        latest, history, forecast, comparisons = load()
    except Exception as e:
        st.error(f'Base de datos todavía no disponible: {e}')
        return
    if latest.empty:
        st.info('Esperando la primera lectura del contenedor collector. Revisa: docker compose logs -f collector')
        return
    point = latest.iloc[0]
    st.caption(f"Último registro: {point['fetched_at']} UTC | Valor del modelo: {point['observed_at']} (hora local)")
    a,b,c,d = st.columns(4)
    a.metric('Temperatura', f"{point['temperature']:.1f} °C")
    b.metric('Sensación térmica', f"{point['apparent_temperature']:.1f} °C")
    c.metric('Humedad', f"{point['humidity']:.0f} %")
    d.metric('Viento', f"{point['wind_speed']:.1f} km/h")
    st.subheader('Pronóstico (próximas 72 horas)')
    if not forecast.empty:
        forecast['forecast_for'] = pd.to_datetime(forecast['forecast_for'])
        now_local = pd.Timestamp.now(tz='America/Hermosillo').tz_localize(None)
        forecast = forecast[forecast['forecast_for'] >= now_local.floor('h')]
        fig = go.Figure()
        fig.add_scatter(x=forecast['forecast_for'], y=forecast['temperature'], mode='lines+markers', name='Temperatura (°C)')
        fig.update_layout(xaxis_title='Hora local', yaxis_title='Temperatura (°C)', margin=dict(t=20,b=20))
        st.plotly_chart(fig, use_container_width=True)
        left,right = st.columns(2)
        with left:
            st.markdown('**Lluvia pronosticada (mm por hora)**')
            st.bar_chart(forecast.set_index('forecast_for')['precipitation'])
        with right:
            st.markdown('**Probabilidad de precipitación (%)**')
            st.line_chart(forecast.set_index('forecast_for')['precipitation_probability'])
    st.subheader('Desviación respecto al pronóstico de hace 24 horas')
    st.caption('Comparación de modelos: valor actual estimado frente a predicción emitida 24 h antes. No representa error frente a una estación meteorológica.')
    if not comparisons.empty:
        comparisons['temp_deviation'] = comparisons['current_temperature'] - comparisons['predicted_temperature_24h']
        comparisons['rain_deviation'] = comparisons['current_precipitation'] - comparisons['predicted_precipitation_24h']
        latest_comp = comparisons.iloc[0]
        x,y = st.columns(2)
        x.metric('Desviación de temperatura', f"{latest_comp['temp_deviation']:+.1f} °C" if pd.notna(latest_comp['temp_deviation']) else 'Sin dato')
        y.metric('Desviación de lluvia horaria', f"{latest_comp['rain_deviation']:+.1f} mm" if pd.notna(latest_comp['rain_deviation']) else 'Sin dato')
        # Una muestra por hora para evitar repetir el mismo valor en el gráfico.
        chart = comparisons.sort_values('fetched_at').drop_duplicates('valid_hour', keep='last')
        st.line_chart(chart.set_index('valid_hour')[['temp_deviation']])
        st.markdown('**Desviación de lluvia horaria (mm)**')
        st.bar_chart(chart.set_index('valid_hour')['rain_deviation'])
    st.subheader('Historial de temperatura registrado en PostgreSQL')
    history = history.sort_values('fetched_at')
    st.line_chart(history.set_index('fetched_at')['temperature'])
    st.caption('El historial local se va formando cada 10 minutos desde que se inicia el proyecto; no se generan datos ficticios.')

main()
