PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS truth_evals (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  session_id TEXT,
  question TEXT,
  verification_track TEXT,
  life_evidence_confirmed INTEGER DEFAULT 0,
  discovery_triggered INTEGER DEFAULT 0,
  created_at TEXT NOT NULL
);
