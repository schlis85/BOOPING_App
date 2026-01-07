# Boop model for BOOPING App
# Created by Claude Opus 4.5

from database.db import query_db, execute_db, USE_POSTGRES
from datetime import datetime


def create_boop(sender_id, recipient_id, paw_style='default'):
    """Create a new boop."""
    boop_id = execute_db(
        '''INSERT INTO boops (sender_id, recipient_id, paw_style)
           VALUES (?, ?, ?)''',
        (sender_id, recipient_id, paw_style)
    )
    # Update global boop counter
    execute_db('UPDATE global_stats SET total_boops = total_boops + 1, last_updated = CURRENT_TIMESTAMP')
    return boop_id


def get_boops_sent(user_id, limit=50):
    """Get boops sent by a user."""
    return query_db(
        '''SELECT b.*, u.display_name as recipient_name, u.color_theme as recipient_color
           FROM boops b
           JOIN users u ON b.recipient_id = u.id
           WHERE b.sender_id = ?
           ORDER BY b.created_at DESC
           LIMIT ?''',
        (user_id, limit)
    )


def get_boops_received(user_id, limit=50):
    """Get boops received by a user."""
    return query_db(
        '''SELECT b.*, u.display_name as sender_name, u.color_theme as sender_color, u.paw_style as sender_paw
           FROM boops b
           JOIN users u ON b.sender_id = u.id
           WHERE b.recipient_id = ?
           ORDER BY b.created_at DESC
           LIMIT ?''',
        (user_id, limit)
    )


def get_new_boops_since(user_id, since_timestamp):
    """Get boops received since a specific timestamp."""
    if since_timestamp is None:
        # If no last_login, show recent boops (last 24 hours) as "new"
        # Use database-specific datetime syntax
        if USE_POSTGRES:
            time_filter = "NOW() - INTERVAL '1 day'"
        else:
            time_filter = "datetime('now', '-1 day')"
        return query_db(
            f'''SELECT b.*, u.display_name as sender_name, u.color_theme as sender_color, u.paw_style as sender_paw
               FROM boops b
               JOIN users u ON b.sender_id = u.id
               WHERE b.recipient_id = ? AND b.created_at > {time_filter}
               ORDER BY b.created_at DESC''',
            (user_id,)
        )
    return query_db(
        '''SELECT b.*, u.display_name as sender_name, u.color_theme as sender_color, u.paw_style as sender_paw
           FROM boops b
           JOIN users u ON b.sender_id = u.id
           WHERE b.recipient_id = ? AND b.created_at > ?
           ORDER BY b.created_at DESC''',
        (user_id, since_timestamp)
    )


def get_boop_count(user_id, direction='sent'):
    """Get boop count for a user."""
    if direction == 'sent':
        result = query_db(
            'SELECT COUNT(*) as count FROM boops WHERE sender_id = ?',
            (user_id,), one=True
        )
    else:
        result = query_db(
            'SELECT COUNT(*) as count FROM boops WHERE recipient_id = ?',
            (user_id,), one=True
        )
    return result['count'] if result else 0


def get_mutual_boops(user_id):
    """Get users who have mutual boops with the given user."""
    return query_db(
        '''SELECT DISTINCT u.id, u.display_name, u.color_theme, u.paw_style
           FROM boops b1
           JOIN boops b2 ON b1.sender_id = b2.recipient_id
                        AND b1.recipient_id = b2.sender_id
           JOIN users u ON u.id = b1.recipient_id
           WHERE b1.sender_id = ?''',
        (user_id,)
    )


def get_global_stats():
    """Get global boop statistics."""
    result = query_db('SELECT * FROM global_stats WHERE id = 1', one=True)
    if result:
        return {
            'total_boops': result['total_boops'],
            'total_users': result['total_users'],
            'last_updated': result['last_updated']
        }
    return {'total_boops': 0, 'total_users': 0, 'last_updated': None}


def get_user_boops_last_minute(user_id):
    """Count boops sent by user in the last minute (for rate limiting)."""
    if USE_POSTGRES:
        time_filter = "NOW() - INTERVAL '1 minute'"
    else:
        time_filter = "datetime('now', '-1 minute')"
    result = query_db(
        f'SELECT COUNT(*) as count FROM boops WHERE sender_id = ? AND created_at > {time_filter}',
        (user_id,), one=True
    )
    return result['count'] if result else 0
