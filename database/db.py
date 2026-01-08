# Database utilities for BOOPING App
# Created by Claude Opus 4.5
# Updated: PostgreSQL support for Railway deployment

import os
import sqlite3
from contextlib import contextmanager
from urllib.parse import urlparse

# Check for PostgreSQL (Railway sets DATABASE_URL)
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    USE_POSTGRES = True
else:
    USE_POSTGRES = False
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'booping.db')

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


@contextmanager
def get_db():
    """Context manager for database connections."""
    if USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
    else:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
    try:
        yield conn
    finally:
        conn.close()


def _convert_query(query):
    """Convert SQLite ? placeholders to PostgreSQL %s."""
    if USE_POSTGRES:
        return query.replace('?', '%s')
    return query


def _row_to_dict(row, cursor):
    """Convert a database row to a dict-like object."""
    if USE_POSTGRES:
        if row is None:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    return row  # SQLite Row already supports dict-like access


class DictRow(dict):
    """Dict subclass that supports both dict and attribute access."""
    def keys(self):
        return super().keys()


def query_db(query, args=(), one=False):
    """Execute a query and return results."""
    query = _convert_query(query)
    with get_db() as conn:
        if USE_POSTGRES:
            cur = conn.cursor()
            cur.execute(query, args)
            rows = cur.fetchall()
            if not rows:
                return None if one else []
            columns = [desc[0] for desc in cur.description]
            results = [DictRow(zip(columns, row)) for row in rows]
            return results[0] if one else results
        else:
            cur = conn.execute(query, args)
            rv = cur.fetchall()
            return (rv[0] if rv else None) if one else rv


def execute_db(query, args=()):
    """Execute a query that modifies data."""
    query = _convert_query(query)
    with get_db() as conn:
        if USE_POSTGRES:
            cur = conn.cursor()
            # Handle RETURNING for INSERT statements
            # Skip for user_badges which has composite key, no id column
            if 'INSERT' in query.upper() and 'RETURNING' not in query.upper():
                if 'user_badges' not in query.lower():
                    query = query.rstrip(';') + ' RETURNING id'
            cur.execute(query, args)
            conn.commit()
            if cur.description:
                result = cur.fetchone()
                return result[0] if result else None
            return None
        else:
            cur = conn.execute(query, args)
            conn.commit()
            return cur.lastrowid


def init_db():
    """Initialize the database from schema."""
    with get_db() as conn:
        if USE_POSTGRES:
            cur = conn.cursor()
            with open(SCHEMA_PATH.replace('.sql', '_postgres.sql'), 'r') as f:
                schema = f.read()
            # Execute each statement separately for PostgreSQL
            for statement in schema.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        cur.execute(statement)
                    except Exception as e:
                        # Don't swallow errors - log them clearly
                        # Only ignore "already exists" type errors
                        error_msg = str(e).lower()
                        if 'already exists' in error_msg or 'duplicate' in error_msg:
                            print(f"Note (safe to ignore): {e}")
                        else:
                            print(f"ERROR in init_db: {e}")
                            print(f"Failed statement: {statement[:100]}...")
                            raise  # Re-raise non-ignorable errors
            conn.commit()
            print("PostgreSQL database initialized!")
        else:
            with open(SCHEMA_PATH, 'r') as f:
                conn.executescript(f.read())
            conn.commit()
            print(f"SQLite database initialized at {DATABASE_PATH}")


def check_db_initialized():
    """Check if database tables exist."""
    try:
        query_db('SELECT 1 FROM users LIMIT 1')
        return True
    except Exception:
        return False


def run_migrations():
    """Run any necessary database migrations."""
    if not USE_POSTGRES:
        return

    with get_db() as conn:
        cur = conn.cursor()
        try:
            # Update display_name constraint from 50 to 200 chars
            cur.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_display_name_check")
            cur.execute("ALTER TABLE users ADD CONSTRAINT users_display_name_check CHECK (length(display_name) <= 200)")
            conn.commit()
        except Exception as e:
            print(f"Migration note (constraint): {e}")
            conn.rollback()

        # Badge seeding/update migration - ensures badges exist with correct thresholds
        try:
            badge_data = [
                ('First Boop', 'Sent your first boop!', 1, '🐾', None),
                ('Booper', 'Sent 100 boops', 100, '🐾🐾', 'sparkle'),
                ('Super Booper', 'Sent 200 boops', 200, '✨🐾', 'ghost'),
                ('Boop Master', 'Sent 10,000 boops', 10000, '👑🐾', 'fire'),
                ('Boop Legend', 'Sent 100,000 boops', 100000, '🌟👑🐾', 'rainbow'),
                ('Generous Soul', 'Sent 1,000 boops', 1000, '💯', 'star'),
                ('Boop Giver', 'Sent 10,000 boops', 10000, '🌟', 'heart'),
                ('Boop Philanthropist', 'Sent 100,000 boops', 100000, '💖', 'galaxy'),
            ]
            for name, desc, threshold, icon, paw in badge_data:
                cur.execute('''
                    INSERT INTO badges (name, description, threshold, icon, unlocks_paw)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        description = EXCLUDED.description,
                        threshold = EXCLUDED.threshold,
                        icon = EXCLUDED.icon,
                        unlocks_paw = EXCLUDED.unlocks_paw
                ''', (name, desc, threshold, icon, paw))
            conn.commit()
            print("Badge migration completed - badges seeded/updated.")
        except Exception as e:
            print(f"Badge migration error: {e}")
            conn.rollback()

        print("Database migrations completed.")


if __name__ == '__main__':
    init_db()
