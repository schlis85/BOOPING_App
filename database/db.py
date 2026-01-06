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
            if 'INSERT' in query.upper() and 'RETURNING' not in query.upper():
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
                        print(f"Warning: {e}")
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


if __name__ == '__main__':
    init_db()
