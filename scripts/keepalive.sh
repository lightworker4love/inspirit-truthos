#!/bin/bash
# TruthOS Keep-Alive Ping
# Run via cron or an external scheduler to reduce Railway cold starts.
# Recommended cadence: every 10 minutes.

SERVICES=(
  "https://truth-api-production-0046.up.railway.app/health"
  "https://hermes-agent-production-848a.up.railway.app/health"
  "https://truthos-web-production.up.railway.app/"
)

for url in "${SERVICES[@]}"; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "$url")
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $url | HTTP $STATUS"
done
