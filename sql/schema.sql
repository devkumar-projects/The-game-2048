PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL COLLATE NOCASE,
    last_name TEXT NOT NULL COLLATE NOCASE,
    class_name TEXT NOT NULL COLLATE NOCASE,
    best_score INTEGER NOT NULL DEFAULT 0 CHECK (best_score >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (first_name, last_name, class_name)
);

CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    score INTEGER NOT NULL DEFAULT 0 CHECK (score >= 0),
    highest_tile INTEGER NOT NULL DEFAULT 0 CHECK (highest_tile >= 0),
    won INTEGER NOT NULL DEFAULT 0 CHECK (won IN (0, 1)),
    played_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS saved_games (
    player_id INTEGER PRIMARY KEY,
    grid_json TEXT NOT NULL,
    score INTEGER NOT NULL DEFAULT 0 CHECK (score >= 0),
    won INTEGER NOT NULL DEFAULT 0 CHECK (won IN (0, 1)),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_players_best_score
    ON players(best_score DESC);

CREATE INDEX IF NOT EXISTS idx_games_player_id
    ON games(player_id);
