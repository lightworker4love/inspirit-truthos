FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn httpx
CMD ["uvicorn", "apps.hermes_agent.api:app", "--host", "0.0.0.0", "--port", "8001"]
