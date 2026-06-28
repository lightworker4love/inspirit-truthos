PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS hardcasebuffer (
  userid TEXT PRIMARY KEY,
  reasons TEXT NOT NULL,
  sessionid TEXT,
  createdat TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS promptversions (
  id TEXT PRIMARY KEY,
  hardcaseid TEXT NOT NULL,
  prompttemplate TEXT NOT NULL,
  promptlabel TEXT NOT NULL,
  prompttype TEXT NOT NULL,
  version INTEGER NOT NULL,
  parentversionid TEXT,
  createdat TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS promptabtests (
  id TEXT PRIMARY KEY,
  hardcaseid TEXT NOT NULL,
  promptaid TEXT NOT NULL,
  promptbid TEXT NOT NULL,
  status TEXT NOT NULL,
  winnerid TEXT,
  evaluationjson TEXT,
  startdat TEXT NOT NULL,
  completedat TEXT
);

CREATE TABLE IF NOT EXISTS designerreviews (
  id TEXT PRIMARY KEY,
  hardcaseid TEXT NOT NULL,
  reviewedby TEXT NOT NULL,
  findingsjson TEXT NOT NULL,
  newprincipleproposed INTEGER DEFAULT 0,
  promptwinner TEXT,
  action TEXT NOT NULL,
  createdat TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS knowledgeevolutions (
  id TEXT PRIMARY KEY,
  sourcetype TEXT NOT NULL,
  sourceid TEXT NOT NULL,
  changetype TEXT NOT NULL,
  targetid TEXT,
  rationaljson TEXT,
  createdat TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_promptversions_hardcaseid
  ON promptversions(hardcaseid);
CREATE INDEX IF NOT EXISTS idx_promptabtests_hardcaseid
  ON promptabtests(hardcaseid);
CREATE INDEX IF NOT EXISTS idx_designerreviews_hardcaseid
  ON designerreviews(hardcaseid);
CREATE INDEX IF NOT EXISTS idx_knowledgeevolutions_source
  ON knowledgeevolutions(sourcetype, sourceid);
