# User model for BOOPING App
# Created by Claude Opus 4.5

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import query_db, execute_db


class User(UserMixin):
    def __init__(self, id, username, password_hash, display_name, tagline='',
                 color_theme='#FF69B4', paw_style='default', created_at=None,
                 last_active=None, last_login=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.display_name = display_name
        self.tagline = tagline
        self.color_theme = color_theme
        self.paw_style = paw_style
        self.created_at = created_at
        self.last_active = last_active
        self.last_login = last_login

    @staticmethod
    def from_row(row):
        """Create a User from a database row."""
        if row is None:
            return None
        return User(
            id=row['id'],
            username=row['username'],
            password_hash=row['password_hash'],
            display_name=row['display_name'],
            tagline=row['tagline'],
            color_theme=row['color_theme'],
            paw_style=row['paw_style'],
            created_at=row['created_at'],
            last_active=row['last_active'],
            last_login=row['last_login'] if 'last_login' in row.keys() else None
        )

    @staticmethod
    def get_by_id(user_id):
        """Get a user by ID."""
        row = query_db('SELECT * FROM users WHERE id = ?', (user_id,), one=True)
        return User.from_row(row)

    @staticmethod
    def get_by_username(username):
        """Get a user by username."""
        row = query_db('SELECT * FROM users WHERE username = ?', (username,), one=True)
        return User.from_row(row)

    @staticmethod
    def create(username, password, display_name):
        """Create a new user."""
        password_hash = generate_password_hash(password)
        user_id = execute_db(
            '''INSERT INTO users (username, password_hash, display_name)
               VALUES (?, ?, ?)''',
            (username, password_hash, display_name)
        )
        # Update global user count
        execute_db('UPDATE global_stats SET total_users = total_users + 1')
        return User.get_by_id(user_id)

    @staticmethod
    def get_all(exclude_user_id=None):
        """Get all users, optionally excluding one."""
        if exclude_user_id:
            rows = query_db(
                'SELECT * FROM users WHERE id != ? ORDER BY last_active DESC',
                (exclude_user_id,)
            )
        else:
            rows = query_db('SELECT * FROM users ORDER BY last_active DESC')
        return [User.from_row(row) for row in rows]

    def check_password(self, password):
        """Verify password."""
        return check_password_hash(self.password_hash, password)

    def update_profile(self, display_name=None, tagline=None, color_theme=None, paw_style=None):
        """Update user profile."""
        if display_name:
            self.display_name = display_name
        if tagline is not None:
            self.tagline = tagline
        if color_theme:
            self.color_theme = color_theme
        if paw_style:
            self.paw_style = paw_style

        execute_db(
            '''UPDATE users SET display_name = ?, tagline = ?, color_theme = ?, paw_style = ?
               WHERE id = ?''',
            (self.display_name, self.tagline, self.color_theme, self.paw_style, self.id)
        )

    def update_last_active(self):
        """Update last active timestamp."""
        execute_db(
            'UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = ?',
            (self.id,)
        )

    def update_last_login(self):
        """Update last login timestamp (for tracking new boops)."""
        execute_db(
            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
            (self.id,)
        )

    def to_dict(self):
        """Convert to dictionary for JSON responses."""
        return {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'tagline': self.tagline,
            'color_theme': self.color_theme,
            'paw_style': self.paw_style,
            'last_active': self.last_active
        }
