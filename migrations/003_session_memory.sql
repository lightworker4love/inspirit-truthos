CREATE TABLE IF NOT EXISTS session_memory (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  dimension_code TEXT NOT NULL,
  principle_code TEXT,
  message_snippet TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_session_memory_user ON session_memory(user_id);
