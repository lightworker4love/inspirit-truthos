# Release note: TruthOS ollama-local embeddings mode

TruthOS now supports a temporary local `ollama-local` embeddings mode for development. This allows local vector retrieval to use a host Ollama endpoint instead of relying on official OpenAI fallback as the primary embeddings path, while keeping health reporting explicit and truthful.

- Added an explicit `ollama-local` embedding mode
- `/healthz` now reports local non-gateway embeddings honestly with `embedding_gateway=false`
- Local Docker setup now targets host Ollama at `http://host.docker.internal:11434/v1`
- Added `scripts/check_embedding_mode.sh` to verify the active embedding mode
- Updated docs to distinguish temporary local mode, OpenAI fallback, SQLite fallback, and real OpenClaw gateway mode
- This is a temporary local embeddings path, not equivalent to real OpenClaw gateway mode
