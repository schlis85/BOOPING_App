-- BOOPING App Database Schema
-- Created by Claude Opus 4.5
-- Updated: Added larger display_name, last_login tracking, more paws

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    recipient_id INTEGER NOT NULL,
    paw_style TEXT DEFAULT 'default',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (recipient_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_sender ON boops(sender_id);
CREATE INDEX IF NOT EXISTS idx_recipient ON boops(recipient_id);
CREATE INDEX IF NOT EXISTS idx_boop_created ON boops(created_at);

-- Favorites table
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    favorite_user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (favorite_user_id) REFERENCES users(id),
    UNIQUE(user_id, favorite_user_id)
);

CREATE INDEX IF NOT EXISTS idx_user_favorites ON favorites(user_id);

-- Badges table
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    threshold INTEGER NOT NULL,
    icon TEXT,
    unlocks_paw TEXT
);

-- User badges junction table
CREATE TABLE IF NOT EXISTS user_badges (
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, badge_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (badge_id) REFERENCES badges(id)
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
INSERT OR IGNORE INTO global_stats (id, total_boops, total_users) VALUES (1, 0, 0);

-- Seed badges (all rewards are for boops GIVEN, not received)
-- Thresholds are intentionally high to make unlocks feel earned
INSERT OR IGNORE INTO badges (name, description, threshold, icon, unlocks_paw) VALUES
    ('First Boop', 'Sent your first boop!', 1, '🐾', NULL),
    ('Booper', 'Sent 100 boops', 100, '🐾🐾', 'sparkle'),
    ('Super Booper', 'Sent 200 boops', 200, '✨🐾', 'ghost'),
    ('Boop Master', 'Sent 1,000 boops', 1000, '👑🐾', 'fire'),
    ('Boop Legend', 'Sent 2,000 boops', 2000, '🌟👑🐾', 'rainbow'),
    ('Generous Soul', 'Sent 4,000 boops', 4000, '💯', 'star'),
    ('Boop Giver', 'Sent 10,000 boops', 10000, '🌟', 'heart'),
    ('Boop Philanthropist', 'Sent 10,000 boops', 10000, '💖', 'galaxy'),
    ('Spooky Booper', 'Sent 10,001 boops', 10001, '💀', 'skeleton'),
    ('Extraterrestrial', 'Sent 12,000 boops', 12000, '👽', 'alien'),
    ('Mechanical Mind', 'Sent 14,000 boops', 14000, '🤖', 'robot'),
    ('Solar Flare', 'Sent 16,000 boops', 16000, '☀️', 'sun'),
    ('Thunder Strike', 'Sent 18,000 boops', 18000, '⚡', 'lightning'),
    ('Frozen Heart', 'Sent 20,001 boops', 20001, '❄️', 'snowflake');
