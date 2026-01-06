# Main routes for BOOPING App
# Created by Claude Opus 4.5

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.user import User
from models.boop import get_boop_count, get_global_stats

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('home.html')
    stats = get_global_stats()
    return render_template('index.html', stats=stats)


@main_bp.route('/home')
@login_required
def home():
    return render_template('home.html')


@main_bp.route('/profile')
@login_required
def profile():
    sent = get_boop_count(current_user.id, 'sent')
    received = get_boop_count(current_user.id, 'received')
    return render_template('profile.html', boops_sent=sent, boops_received=received)


@main_bp.route('/lore')
def lore():
    return render_template('lore.html')
