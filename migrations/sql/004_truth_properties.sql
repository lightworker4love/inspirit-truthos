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

CREATE VIEW IF NOT EXISTS truthevals AS
SELECT
  id,
  user_id AS userid,
  session_id AS sessionid,
  question,
  verification_track,
  life_evidence_confirmed,
  discovery_triggered,
  created_at AS createdat
FROM truth_evals;
