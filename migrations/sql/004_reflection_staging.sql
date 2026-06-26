PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS reflection_runs (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 1.0,
  generated_from_run_date TEXT,
  payload_fingerprint TEXT NOT NULL,
  source_context_status_json TEXT NOT NULL,
  operator_summary_json TEXT NOT NULL,
  reflection_run_json TEXT NOT NULL,
  dashboard_snapshot_json TEXT NOT NULL,
  writeback_candidates_json TEXT NOT NULL,
  import_drafts_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date)
);

CREATE TABLE IF NOT EXISTS reflection_discernment_layers (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.0,
  layer_type TEXT NOT NULL,
  content TEXT NOT NULL,
  working_hypothesis INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date, layer_type, content)
);

CREATE TABLE IF NOT EXISTS reflection_truth_mappings (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.0,
  mapping_type TEXT NOT NULL,
  code TEXT NOT NULL,
  title TEXT,
  pattern_type TEXT,
  score REAL,
  generated_from_run_date TEXT NOT NULL,
  metadata_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date, mapping_type, code)
);

CREATE TABLE IF NOT EXISTS dashboard_snapshots (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.0,
  summary TEXT NOT NULL,
  snapshot_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date)
);

CREATE TABLE IF NOT EXISTS dashboard_daily_metrics (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.0,
  clarity_score INTEGER,
  emotional_intensity_score INTEGER,
  alignment_score INTEGER,
  boundary_score INTEGER,
  truth_discernment_score INTEGER,
  memory_confidence_score INTEGER,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date)
);

CREATE TABLE IF NOT EXISTS dashboard_pattern_snapshots (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.0,
  generated_from_run_date TEXT NOT NULL,
  snapshot_type TEXT NOT NULL,
  pattern_key TEXT NOT NULL,
  title TEXT NOT NULL,
  count_increment INTEGER NOT NULL DEFAULT 0,
  last_seen_at TEXT NOT NULL,
  metadata_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date, snapshot_type, pattern_key)
);

CREATE TABLE IF NOT EXISTS soul_map_candidate_events (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.0,
  generated_from_run_date TEXT NOT NULL,
  candidate_type TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  should_write INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date, candidate_type, payload_json)
);

CREATE TABLE IF NOT EXISTS blind_spot_candidate_events (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.0,
  generated_from_run_date TEXT NOT NULL,
  title TEXT NOT NULL,
  trigger_pattern TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  should_write INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date, title, trigger_pattern)
);

CREATE TABLE IF NOT EXISTS belief_log_candidate_events (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.0,
  generated_from_run_date TEXT NOT NULL,
  belief_before TEXT NOT NULL,
  belief_after TEXT NOT NULL,
  tag TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  should_write INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date, belief_before, belief_after, tag)
);

CREATE TABLE IF NOT EXISTS case_summary_candidate_events (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.0,
  generated_from_run_date TEXT NOT NULL,
  title TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  should_write INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date, title)
);

CREATE TABLE IF NOT EXISTS core_principle_draft_events (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.0,
  generated_from_run_date TEXT NOT NULL,
  draft_code TEXT NOT NULL,
  title TEXT NOT NULL,
  cross_day_support_count INTEGER NOT NULL DEFAULT 1,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date, draft_code)
);

CREATE TABLE IF NOT EXISTS truth_puzzle_draft_events (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.0,
  generated_from_run_date TEXT NOT NULL,
  draft_code TEXT NOT NULL,
  title TEXT NOT NULL,
  cross_day_support_count INTEGER NOT NULL DEFAULT 1,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date, draft_code)
);

CREATE TABLE IF NOT EXISTS writeback_audit_log (
  id TEXT PRIMARY KEY,
  run_date TEXT NOT NULL,
  user_id TEXT NOT NULL,
  tenant_id TEXT,
  source_file TEXT,
  source_run_id TEXT,
  stream_name TEXT NOT NULL,
  action TEXT NOT NULL,
  outcome TEXT NOT NULL,
  reason TEXT,
  status TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0.0,
  duplicate_key TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dashboard_overview_cache (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  window_days INTEGER NOT NULL,
  generated_at TEXT NOT NULL,
  overview_json TEXT NOT NULL,
  UNIQUE(user_id, window_days)
);

CREATE TABLE IF NOT EXISTS dimension_trends_cache (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  run_date TEXT NOT NULL,
  dimension_code TEXT NOT NULL,
  score REAL NOT NULL,
  generated_at TEXT NOT NULL,
  UNIQUE(user_id, run_date, dimension_code)
);

CREATE TABLE IF NOT EXISTS recurring_patterns_cache (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  pattern_key TEXT NOT NULL,
  title TEXT NOT NULL,
  frequency INTEGER NOT NULL,
  last_seen_at TEXT NOT NULL,
  generated_at TEXT NOT NULL,
  UNIQUE(user_id, pattern_key)
);

CREATE TABLE IF NOT EXISTS belief_shift_cache (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  belief_key TEXT NOT NULL,
  belief_before TEXT NOT NULL,
  belief_after TEXT NOT NULL,
  frequency INTEGER NOT NULL,
  last_seen_at TEXT NOT NULL,
  generated_at TEXT NOT NULL,
  UNIQUE(user_id, belief_key)
);

CREATE TABLE IF NOT EXISTS blind_spot_heatmap_cache (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  blind_spot_key TEXT NOT NULL,
  title TEXT NOT NULL,
  trigger_pattern TEXT NOT NULL,
  frequency INTEGER NOT NULL,
  last_seen_at TEXT NOT NULL,
  generated_at TEXT NOT NULL,
  UNIQUE(user_id, blind_spot_key)
);

CREATE VIEW IF NOT EXISTS dashboard_overview_view AS
SELECT user_id, window_days, generated_at, overview_json
FROM dashboard_overview_cache;

CREATE VIEW IF NOT EXISTS dimension_trends_view AS
SELECT user_id, run_date, dimension_code, score, generated_at
FROM dimension_trends_cache;

CREATE VIEW IF NOT EXISTS recurring_patterns_view AS
SELECT user_id, pattern_key, title, frequency, last_seen_at, generated_at
FROM recurring_patterns_cache;

CREATE VIEW IF NOT EXISTS belief_shift_view AS
SELECT user_id, belief_key, belief_before, belief_after, frequency, last_seen_at, generated_at
FROM belief_shift_cache;

CREATE VIEW IF NOT EXISTS blind_spot_heatmap_view AS
SELECT user_id, blind_spot_key, title, trigger_pattern, frequency, last_seen_at, generated_at
FROM blind_spot_heatmap_cache;

CREATE INDEX IF NOT EXISTS idx_reflection_runs_user_date ON reflection_runs(user_id, run_date);
CREATE INDEX IF NOT EXISTS idx_truth_mappings_user_date ON reflection_truth_mappings(user_id, run_date);
CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_user_date ON dashboard_daily_metrics(user_id, run_date);
CREATE INDEX IF NOT EXISTS idx_pattern_snapshots_user_date ON dashboard_pattern_snapshots(user_id, run_date);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_date ON writeback_audit_log(user_id, run_date);
