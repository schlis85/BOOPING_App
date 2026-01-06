# Configuration for BOOPING App
# Created by Claude Opus 4.5

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'boop-secret-key-change-in-production'
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'booping.db')

    # Rate limiting
    MAX_BOOPS_PER_MINUTE = 10

    # User constraints
    MAX_DISPLAY_NAME_LENGTH = 50
    MAX_TAGLINE_LENGTH = 300
