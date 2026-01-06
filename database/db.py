# Database utilities for BOOPING App
# Created by Claude Opus 4.5

import sqlite3
from contextlib import contextmanager
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'booping.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    try:
        yield conn
    finally:
        conn.close()


def query_db(query, args=(), one=False):
    """Execute a query and return results."""
    with get_db() as conn:
        cur = conn.execute(query, args)
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv


def execute_db(query, args=()):
    """Execute a query that modifies data."""
    with get_db() as conn:
        cur = conn.execute(query, args)
        conn.commit()
        return cur.lastrowid


def init_db():
    """Initialize the database from schema.sql."""
    with get_db() as conn:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        conn.commit()
    print(f"Database initialized at {DATABASE_PATH}")


if __name__ == '__main__':
    init_db()
