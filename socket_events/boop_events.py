# WebSocket event handlers for BOOPING App
# Created by Claude Opus 4.5

from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from models.boop import create_boop, get_global_stats
from models.badge import check_and_award_badges
from models.user import User


def register_socket_events(socketio):
    """Register all socket event handlers."""

    @socketio.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            # Join user's personal room for notifications
            join_room(f'user_{current_user.id}')
            emit('connected', {'user_id': current_user.id})

    @socketio.on('disconnect')
    def handle_disconnect():
        if current_user.is_authenticated:
            leave_room(f'user_{current_user.id}')

    @socketio.on('send_boop')
    def handle_send_boop(data):
        if not current_user.is_authenticated:
            return

        recipient_id = data.get('recipient_id')
        paw_style = data.get('paw_style', current_user.paw_style)

        if not recipient_id:
            return

        # Verify recipient exists
        recipient = User.get_by_id(recipient_id)
        if not recipient:
            return

        # Create the boop
        boop_id = create_boop(current_user.id, recipient_id, paw_style)

        # Notify the recipient
        emit('boop_received', {
            'sender': {
                'id': current_user.id,
                'display_name': current_user.display_name,
                'color_theme': current_user.color_theme,
                'paw_style': paw_style
            },
            'boop_id': boop_id
        }, room=f'user_{recipient_id}')

        # Check for new badges
        new_badges = check_and_award_badges(current_user.id)

        # Notify sender of new badges
        if new_badges:
            emit('badges_unlocked', {'badges': new_badges})

        # Broadcast updated global stats to everyone
        stats = get_global_stats()
        emit('global_stats_update', stats, broadcast=True)

        # Confirm boop was sent
        emit('boop_sent', {
            'success': True,
            'recipient_id': recipient_id,
            'new_badges': new_badges
        })
