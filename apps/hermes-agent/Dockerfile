FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir setuptools==83.0.0 fastapi uvicorn httpx

EXPOSE 8001

CMD ["sh", "-lc", "exec uvicorn apps.hermes_agent.api:app --host 0.0.0.0 --port ${PORT:-8001}"]
