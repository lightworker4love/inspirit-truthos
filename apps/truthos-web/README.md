# TruthOS Web

TruthOS Web is the v1 user-facing interface for the iN SPiRiT Life Blueprint flow.
It provides a calm intake page, guided Hermes chat, Soul Map insights, and a
placeholder for future conversation history.

This app connects directly to the verified Railway production services during
local development:

- Hermes Agent: `https://hermes-agent-production-848a.up.railway.app`
- Truth API: `https://truth-api-production-0046.up.railway.app`

The local Hermes Agent at `127.0.0.1:8642` is not used because it does not expose
the TruthOS tool layer required for `truth_layer` and Soul Map writes.

## Local Setup

```bash
cd apps/truthos-web
cp .env.local.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`.

## Build

```bash
npm run build
```

## Environment Variables

```bash
NEXT_PUBLIC_HERMES_AGENT_URL=https://hermes-agent-production-848a.up.railway.app
NEXT_PUBLIC_TRUTH_API_URL=https://truth-api-production-0046.up.railway.app
```

## Pages

- `/` Welcome and intake
- `/chat` Hermes conversation
- `/soul-map` emerged Soul Map patterns
- `/history` v1 placeholder
