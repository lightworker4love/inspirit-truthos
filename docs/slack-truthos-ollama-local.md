TruthOS local embeddings handoff is ready on commit `312a93f`.
Current health is: `embedding_gateway=false`, `embedding_mode=ollama-local`, `vector_index=true`, `retrieval_mode=vector`.
Primary local embeddings now come from host Ollama instead of official OpenAI fallback.
`./scripts/check_embedding_mode.sh` and `./scripts/smoke_test.sh` both passed.
This is a temporary local acceleration path, not real OpenClaw gateway mode.
`check_gateway_mode.sh` should still fail here, and that is expected.
OpenClaw gateway work is still pending a usable `/v1/embeddings` HTTP endpoint.
No unrelated dirty files were included in commit `312a93f`.
