PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS truth_dimensions (
  id TEXT PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  name_zh TEXT NOT NULL,
  name_en TEXT NOT NULL,
  description TEXT NOT NULL,
  order_index INTEGER NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS core_principles (
  id TEXT PRIMARY KEY,
  dimension_code TEXT NOT NULL,
  code TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  axiom TEXT NOT NULL,
  explanation TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (dimension_code) REFERENCES truth_dimensions(code)
);

CREATE TABLE IF NOT EXISTS truth_puzzles (
  id TEXT PRIMARY KEY,
  dimension_code TEXT NOT NULL,
  principle_code TEXT NOT NULL,
  title TEXT NOT NULL,
  statement TEXT NOT NULL,
  misbelief TEXT,
  truth_reframe TEXT,
  coach_prompt TEXT,
  tags TEXT,
  use_cases TEXT,
  source_doc TEXT NOT NULL,
  embedding_text TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (dimension_code) REFERENCES truth_dimensions(code),
  FOREIGN KEY (principle_code) REFERENCES core_principles(code)
);

CREATE TABLE IF NOT EXISTS belief_logs (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  session_id TEXT,
  belief_statement TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS blind_spot_archives (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT NOT NULL,
  trigger_pattern TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_truth_puzzles_dimension_code ON truth_puzzles(dimension_code);
CREATE INDEX IF NOT EXISTS idx_truth_puzzles_principle_code ON truth_puzzles(principle_code);
CREATE INDEX IF NOT EXISTS idx_belief_logs_user_id ON belief_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_blind_spot_archives_user_id ON blind_spot_archives(user_id);
