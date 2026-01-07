# Badge model for BOOPING App
# Created by Claude Opus 4.5

from database.db import query_db, execute_db
from models.boop import get_boop_count

# Starter paws everyone gets
STARTER_PAWS = ['default', 'cat', 'sparkle', 'heart', 'moon']

# All available paws and how to unlock them (all based on boops GIVEN)
# Thresholds are high - unlocks should feel earned!
ALL_PAWS = {
    'default': {'emoji': '🐾', 'unlock': 'starter'},
    'cat': {'emoji': '🐱', 'unlock': 'starter'},
    'sparkle': {'emoji': '✨', 'unlock': 'starter'},
    'heart': {'emoji': '💖', 'unlock': 'starter'},
    'moon': {'emoji': '🌙', 'unlock': 'starter'},
    'ghost': {'emoji': '👻', 'unlock': 'Send 1,000 boops'},
    'fire': {'emoji': '🔥', 'unlock': 'Send 10,000 boops'},
    'rainbow': {'emoji': '🌈', 'unlock': 'Send 100,000 boops'},
    'star': {'emoji': '⭐', 'unlock': 'Send 1,000 boops'},
    'galaxy': {'emoji': '🌌', 'unlock': 'Send 100,000 boops'},
    'skeleton': {'emoji': '💀', 'unlock': 'Secret'},
    'alien': {'emoji': '👽', 'unlock': 'Secret'},
    'robot': {'emoji': '🤖', 'unlock': 'Secret'},
    'sun': {'emoji': '☀️', 'unlock': 'Secret'},
    'lightning': {'emoji': '⚡', 'unlock': 'Secret'},
    'snowflake': {'emoji': '❄️', 'unlock': 'Secret'},
    'frog': {'emoji': '🐸', 'unlock': 'Exclusive'},
}


def get_all_badges():
    """Get all available badges."""
    return query_db('SELECT * FROM badges ORDER BY threshold')


def get_user_badges(user_id):
    """Get badges earned by a user."""
    return query_db(
        '''SELECT b.*, ub.earned_at
           FROM badges b
           JOIN user_badges ub ON b.id = ub.badge_id
           WHERE ub.user_id = ?
           ORDER BY b.threshold''',
        (user_id,)
    )


def get_unlocked_paws(user_id):
    """Get paw styles unlocked by a user."""
    paws = list(STARTER_PAWS)  # Everyone gets starter paws
    badges = get_user_badges(user_id)
    for badge in badges:
        if badge['unlocks_paw'] and badge['unlocks_paw'] not in paws:
            paws.append(badge['unlocks_paw'])

    # Exclusive frog paw for user 'frog'
    from models.user import User
    user = User.get_by_id(user_id)
    if user and user.username == 'frog':
        paws.append('frog')

    return paws


def get_all_paws_with_status(user_id):
    """Get all paws with their unlock status for a user."""
    unlocked = get_unlocked_paws(user_id)
    result = []
    for paw_name, paw_info in ALL_PAWS.items():
        result.append({
            'name': paw_name,
            'emoji': paw_info['emoji'],
            'unlocked': paw_name in unlocked,
            'unlock_hint': paw_info['unlock'] if paw_name not in unlocked else None
        })
    return result


def check_and_award_badges(user_id):
    """Check if user has earned any new badges and award them."""
    boop_count = get_boop_count(user_id, 'sent')

    # Get badges user is eligible for but hasn't earned
    eligible = query_db(
        '''SELECT b.* FROM badges b
           WHERE b.threshold <= ?
           AND NOT EXISTS (
               SELECT 1 FROM user_badges ub
               WHERE ub.user_id = ? AND ub.badge_id = b.id
           )''',
        (boop_count, user_id)
    )

    newly_earned = []
    for badge in eligible:
        execute_db(
            'INSERT INTO user_badges (user_id, badge_id) VALUES (?, ?)',
            (user_id, badge['id'])
        )
        newly_earned.append({
            'name': badge['name'],
            'description': badge['description'],
            'icon': badge['icon'],
            'unlocks_paw': badge['unlocks_paw']
        })

    return newly_earned
