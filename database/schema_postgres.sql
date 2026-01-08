-- BOOPING App Database Schema (PostgreSQL)
-- Created by Claude Opus 4.5

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name TEXT NOT NULL,
    tagline TEXT DEFAULT '',
    color_theme TEXT DEFAULT '#FF69B4',
    paw_style TEXT DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK(length(display_name) <= 200),
    CHECK(length(tagline) <= 300)
);

CREATE INDEX IF NOT EXISTS idx_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_last_active ON users(last_active);

-- Boops table
CREATE TABLE IF NOT EXISTS boops (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES users(id),
    recipient_id INTEGER NOT NULL REFERENCES users(id),
    paw_style TEXT DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sender ON boops(sender_id);
CREATE INDEX IF NOT EXISTS idx_recipient ON boops(recipient_id);
CREATE INDEX IF NOT EXISTS idx_boop_created ON boops(created_at);

-- Favorites table
CREATE TABLE IF NOT EXISTS favorites (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    favorite_user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, favorite_user_id)
);

CREATE INDEX IF NOT EXISTS idx_user_favorites ON favorites(user_id);

-- Badges table
CREATE TABLE IF NOT EXISTS badges (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    threshold INTEGER NOT NULL,
    icon TEXT,
    unlocks_paw TEXT
);

-- User badges junction table
CREATE TABLE IF NOT EXISTS user_badges (
    user_id INTEGER NOT NULL REFERENCES users(id),
    badge_id INTEGER NOT NULL REFERENCES badges(id),
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, badge_id)
);

CREATE INDEX IF NOT EXISTS idx_user_badges_user ON user_badges(user_id);

-- Global stats (single row)
CREATE TABLE IF NOT EXISTS global_stats (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    total_boops INTEGER DEFAULT 0,
    total_users INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Initialize global stats
INSERT INTO global_stats (id, total_boops, total_users) VALUES (1, 0, 0)
ON CONFLICT (id) DO NOTHING;

-- Seed badges (all rewards are for boops GIVEN, not received)
-- Thresholds are intentionally high to make unlocks feel earned
INSERT INTO badges (name, description, threshold, icon, unlocks_paw) VALUES
    ('First Boop', 'Sent your first boop!', 1, '🐾', NULL),
    ('Booper', 'Sent 100 boops', 100, '🐾🐾', 'sparkle'),
    ('Super Booper', 'Sent 200 boops', 200, '✨🐾', 'ghost'),
    ('Boop Master', 'Sent 1,000 boops', 1000, '👑🐾', 'fire'),
    ('Boop Legend', 'Sent 2,000 boops', 2000, '🌟👑🐾', 'rainbow'),
    ('Generous Soul', 'Sent 4,000 boops', 4000, '💯', 'star'),
    ('Boop Giver', 'Sent 10,000 boops', 10000, '🌟', 'heart'),
    ('Boop Philanthropist', 'Sent 10,000 boops', 10000, '💖', 'galaxy')
ON CONFLICT (name) DO UPDATE SET
    threshold = EXCLUDED.threshold,
    description = EXCLUDED.description;
