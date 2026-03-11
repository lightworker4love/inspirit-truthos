# TruthOS API Spec

## Endpoint List
- `GET /healthz`
- `POST /api/truth/query`

## Request / Response Examples

### GET /healthz
Response:
```json
{
  "status":"ok",
  "embedding_gateway": false,
  "vector_index": true,
  "embedding_mode": "sqlite"
}
```

### POST /api/truth/query
Request:
```json
{
  "user_id": "u1",
  "message": "I tried to help someone but it turned into conflict"
}
```

Response:
```json
{
  "mirror": "你描述的情境接近某種關係失衡模式。",
  "truth_view": "常見誤區是把支持誤當成接管。",
  "coach_question": "你是在支持，還是在替對方活？",
  "action": "先分清責任，再決定你要提供什麼支持。",
  "dimension": "relationship",
  "principles": ["REL_001", "COM_004", "EMO_002"]
}
```

## Error Format
```json
{
  "error": {
    "code": "invalid_request",
    "message": "Human-readable message"
  }
}
```

## Versioning Strategy
Round 1 uses unversioned routes. Future breaking changes should move under `/api/v1`.

## Local Base URL
- `http://localhost:18000`
