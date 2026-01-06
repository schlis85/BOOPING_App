# BOOPING App - Main Application
# Created by Claude Opus 4.5

import os
import sys

# Add the app directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_socketio import SocketIO
from flask_login import LoginManager
from config import Config
from database.db import init_db

# Initialize extensions
socketio = SocketIO()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    socketio.init_app(app, cors_allowed_origins="*")
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.get_by_id(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Register socket events
    from socket_events.boop_events import register_socket_events
    register_socket_events(socketio)

    # Initialize database if it doesn't exist
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'booping.db')
    if not os.path.exists(db_path):
        with app.app_context():
            init_db()
            print("Database initialized!")

    return app


app = create_app()

if __name__ == '__main__':
    print("\n🐾 BOOPING App starting...")
    print("   Visit http://localhost:5000 to start booping!\n")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
