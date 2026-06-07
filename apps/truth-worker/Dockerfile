FROM python:3.11-slim

WORKDIR /app/apps/truth-worker

RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/*

COPY apps/truth-worker/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --default-timeout=300 -r /tmp/requirements.txt

COPY . /app

CMD ["python", "-m", "jobs.export_analytics"]
