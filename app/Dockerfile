FROM python:3.12-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dashboard.py .
CMD ["streamlit", "run", "dashboard.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
