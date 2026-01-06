# API routes for BOOPING App
# Created by Claude Opus 4.5

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.user import User
from models.boop import create_boop, get_boop_count, get_boops_received, get_global_stats, get_new_boops_since, get_mutual_boops
from models.badge import check_and_award_badges, get_user_badges, get_unlocked_paws, get_all_paws_with_status
from models.favorite import add_favorite, remove_favorite, get_favorites, get_favorite_ids

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/users')
@login_required
def get_users():
    """Get all users except current user."""
    users = User.get_all(exclude_user_id=current_user.id)
    return jsonify([u.to_dict() for u in users])


@api_bp.route('/users/me')
@login_required
def get_current_user():
    """Get current user info."""
    return jsonify(current_user.to_dict())


@api_bp.route('/users/me', methods=['PUT'])
@login_required
def update_profile():
    """Update current user profile."""
    data = request.get_json()
    current_user.update_profile(
        display_name=data.get('display_name'),
        tagline=data.get('tagline'),
        color_theme=data.get('color_theme'),
        paw_style=data.get('paw_style')
    )
    return jsonify(current_user.to_dict())


@api_bp.route('/users/me/stats')
@login_required
def get_user_stats():
    """Get current user's boop stats."""
    return jsonify({
        'boops_sent': get_boop_count(current_user.id, 'sent'),
        'boops_received': get_boop_count(current_user.id, 'received')
    })


@api_bp.route('/users/me/badges')
@login_required
def get_my_badges():
    """Get current user's badges."""
    badges = get_user_badges(current_user.id)
    return jsonify([dict(b) for b in badges])


@api_bp.route('/users/me/paws')
@login_required
def get_my_paws():
    """Get paw styles unlocked by current user."""
    paws = get_unlocked_paws(current_user.id)
    return jsonify(paws)


@api_bp.route('/users/me/all-paws')
@login_required
def get_all_paws():
    """Get all paw styles with unlock status."""
    paws = get_all_paws_with_status(current_user.id)
    return jsonify(paws)


@api_bp.route('/users/me/new-boops')
@login_required
def get_new_boops():
    """Get boops received since last login."""
    boops = get_new_boops_since(current_user.id, current_user.last_login)
    return jsonify([dict(b) for b in boops])


@api_bp.route('/users/me/seen', methods=['POST'])
@login_required
def mark_boops_seen():
    """Update last_login to mark boops as seen."""
    current_user.update_last_login()
    return jsonify({'success': True})


@api_bp.route('/boop', methods=['POST'])
@login_required
def send_boop():
    """Send a boop to another user."""
    data = request.get_json()
    recipient_id = data.get('recipient_id')
    paw_style = data.get('paw_style', current_user.paw_style)

    if not recipient_id:
        return jsonify({'error': 'recipient_id required'}), 400

    # Verify recipient exists
    recipient = User.get_by_id(recipient_id)
    if not recipient:
        return jsonify({'error': 'User not found'}), 404

    # Create the boop
    boop_id = create_boop(current_user.id, recipient_id, paw_style)

    # Check for new badges
    new_badges = check_and_award_badges(current_user.id)

    return jsonify({
        'success': True,
        'boop_id': boop_id,
        'new_badges': new_badges
    })


@api_bp.route('/boops/received')
@login_required
def get_received_boops():
    """Get boops received by current user."""
    boops = get_boops_received(current_user.id)
    return jsonify([dict(b) for b in boops])


@api_bp.route('/stats/global')
def get_stats():
    """Get global boop statistics."""
    return jsonify(get_global_stats())


# Favorites endpoints
@api_bp.route('/users/me/favorites')
@login_required
def get_my_favorites():
    """Get current user's favorite users."""
    favorites = get_favorites(current_user.id)
    return jsonify([dict(f) for f in favorites])


@api_bp.route('/users/me/favorite-ids')
@login_required
def get_my_favorite_ids():
    """Get IDs of favorited users (for quick lookup)."""
    return jsonify(get_favorite_ids(current_user.id))


@api_bp.route('/favorites/<int:user_id>', methods=['POST'])
@login_required
def add_user_favorite(user_id):
    """Add a user to favorites."""
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot favorite yourself'}), 400
    success = add_favorite(current_user.id, user_id)
    return jsonify({'success': success})


@api_bp.route('/favorites/<int:user_id>', methods=['DELETE'])
@login_required
def remove_user_favorite(user_id):
    """Remove a user from favorites."""
    remove_favorite(current_user.id, user_id)
    return jsonify({'success': True})


# Mutual boops (Boop Buddies)
@api_bp.route('/users/me/mutuals')
@login_required
def get_my_mutuals():
    """Get users with mutual boops (you booped them, they booped you)."""
    mutuals = get_mutual_boops(current_user.id)
    return jsonify([dict(m) for m in mutuals])
