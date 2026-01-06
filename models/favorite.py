# Favorite model for BOOPING App
# Created by Claude Opus 4.5

from database.db import query_db, execute_db


def add_favorite(user_id, favorite_user_id):
    """Add a user to favorites."""
    try:
        execute_db(
            '''INSERT INTO favorites (user_id, favorite_user_id)
               VALUES (?, ?)''',
            (user_id, favorite_user_id)
        )
        return True
    except Exception:
        # Already a favorite (UNIQUE constraint)
        return False


def remove_favorite(user_id, favorite_user_id):
    """Remove a user from favorites."""
    execute_db(
        '''DELETE FROM favorites
           WHERE user_id = ? AND favorite_user_id = ?''',
        (user_id, favorite_user_id)
    )


def get_favorites(user_id):
    """Get all favorited users for a user."""
    return query_db(
        '''SELECT u.id, u.username, u.display_name, u.color_theme, u.paw_style, u.last_active
           FROM favorites f
           JOIN users u ON f.favorite_user_id = u.id
           WHERE f.user_id = ?
           ORDER BY u.last_active DESC''',
        (user_id,)
    )


def get_favorite_ids(user_id):
    """Get just the IDs of favorited users (for quick lookup)."""
    rows = query_db(
        'SELECT favorite_user_id FROM favorites WHERE user_id = ?',
        (user_id,)
    )
    return [row['favorite_user_id'] for row in rows]


def is_favorite(user_id, favorite_user_id):
    """Check if a user is favorited."""
    result = query_db(
        '''SELECT 1 FROM favorites
           WHERE user_id = ? AND favorite_user_id = ?''',
        (user_id, favorite_user_id),
        one=True
    )
    return result is not None
