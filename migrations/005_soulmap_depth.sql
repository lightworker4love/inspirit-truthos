PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS soulmaps (
  id TEXT PRIMARY KEY,
  userid TEXT NOT NULL UNIQUE,
  recurringpatternsjson TEXT,
  limitingbeliefsjson TEXT,
  emotionalsignaturesjson TEXT,
  activelessonsjson TEXT,
  evolutionstage TEXT,
  lasttruthshiftat TEXT,
  createdat TEXT NOT NULL,
  updatedat TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS blindspotarchives (
  id TEXT PRIMARY KEY,
  userid TEXT NOT NULL,
  title TEXT NOT NULL,
  triggerpattern TEXT NOT NULL,
  knowntheory TEXT,
  practicalfailuremode TEXT,
  suggestedanchorsjson TEXT,
  relatedpuzzlesjson TEXT,
  frequency INTEGER DEFAULT 1,
  lastseenat TEXT,
  createdat TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hardcasebuffer (
  userid TEXT PRIMARY KEY,
  reasons TEXT NOT NULL,
  sessionid TEXT,
  createdat TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_soulmaps_userid ON soulmaps(userid);
CREATE INDEX IF NOT EXISTS idx_blindspotarchives_userid ON blindspotarchives(userid);
