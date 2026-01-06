# Authentication routes for BOOPING App
# Created by Claude Opus 4.5

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')

        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            user.update_last_active()
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('index.html')


@auth_bp.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '')
    display_name = request.form.get('display_name', '').strip()

    # Validation
    if not username or not password or not display_name:
        flash('All fields are required', 'error')
        return redirect(url_for('auth.login'))

    if len(username) < 3 or len(username) > 20:
        flash('Username must be 3-20 characters', 'error')
        return redirect(url_for('auth.login'))

    if len(password) < 4:
        flash('Password must be at least 4 characters', 'error')
        return redirect(url_for('auth.login'))

    if len(display_name) > 50:
        flash('Display name must be 50 characters or less', 'error')
        return redirect(url_for('auth.login'))

    # Check if username exists
    existing = User.get_by_username(username)
    if existing:
        flash('Username already taken', 'error')
        return redirect(url_for('auth.login'))

    # Create user
    user = User.create(username, password, display_name)
    login_user(user)
    flash('Welcome to BOOPING!', 'success')
    return redirect(url_for('main.home'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
