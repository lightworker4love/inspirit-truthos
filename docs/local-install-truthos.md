# TruthOS 本機安裝與驗證

## 目的

這份文件只處理 `inspirit-truthos` 本機安裝、啟動、驗證與回退。

範圍限制：
- 以 `OpenClaw` 本地主線為錨點
- 不修改 `~/.openclaw/openclaw.json`
- 不把 Antigravity 視為正式依賴
- 只安裝 `truth-api` 與其本機驗證鏈路

## 實際本機整合點

- TruthOS repo: `/Users/tongwei/.openclaw/inspirit-truthos`
- truth-api 入口: `/Users/tongwei/.openclaw/inspirit-truthos/apps/truth-api/app/main.py`
- Docker Compose: `/Users/tongwei/.openclaw/inspirit-truthos/docker-compose.yml`
- OpenClaw -> TruthOS bridge: `/Users/tongwei/.openclaw/inspirit-truthos/scripts/openclaw_bridge.py`
- Bridge 預設目標: `TRUTHOS_INTERNAL_URL=http://localhost:18000`
- OpenClaw 本地主線錨點: `127.0.0.1:18789`

## 啟動模式

目前本機既有主流啟動方式是 `docker compose`。

已觀察到：
- `truth-api` 現場容器由 Compose 管理
- `scripts/dev-up.sh` 也是直接呼叫 `docker compose up`
- `uvicorn` 直跑可作為除錯備援，但不是本輪主安裝模式

## 必要環境變數

最小必要值：

```env
TRUTHOS_ENV=dev
TRUTHOS_DB_PATH=./data/truthos.db
LANCEDB_PATH=./data/lancedb
OPENAI_BASE_URL=http://host.docker.internal:11434/v1
OPENAI_API_KEY=ollama-local
EMBEDDING_PROVIDER=ollama-local
BLUEPRINT_WRITEBACK_ENABLED=true
```

目前正式入口：
- `.env.example`
- `env/truthos.dev.env`
- `env/truthos.staging.env`
- `env/truthos.prod.env`
- `docker-compose.yml` 的 `truth-api.environment`

## 安裝步驟

### 1. 準備本機 env

如果 repo root 尚未有 `.env`，先從 dev 樣板建立：

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
cp env/truthos.dev.env .env
```

如果 `.env` 已存在，只需確認至少包含：

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
rg -n '^BLUEPRINT_WRITEBACK_ENABLED=' .env
```

### 2. 啟動 truth-api

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
docker compose up -d --build truth-api
```

或沿用既有腳本：

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
./scripts/dev-up.sh
```

### 3. Health 驗證

```bash
curl -s http://127.0.0.1:18000/healthz | python3 -m json.tool
```

期待至少包含：
- `status = ok`
- `blueprint_writeback_enabled`
- `embedding_mode`
- `retrieval_mode`

### 4. Query 驗證

```bash
curl -s -X POST http://127.0.0.1:18000/api/truth/query \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "hank-login",
    "session_id": "local-install-001",
    "message": "I tried to help someone but it turned into conflict.",
    "preferred_name": "Hank",
    "login_username": "hank-login",
    "display_name": "Case Hank",
    "source_channel": "web"
  }' | python3 -m json.tool
```

期待：
- HTTP 200
- `case_id` 存在
- `mirror` 以 `Hank，` 開頭

## 非 Compose 備援啟動

只在本機除錯時使用：

```bash
cd /Users/tongwei/.openclaw/inspirit-truthos
python -m pip install -r apps/truth-api/requirements.txt
python scripts/seed_import.py
cd apps/truth-api
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

這不是本輪建議主模式；正式本機安裝仍以 Compose 為準。
