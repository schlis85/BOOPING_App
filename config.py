# Configuration for BOOPING App
# Created by Claude Opus 4.5

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'boop-secret-key-change-in-production'
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'booping.db')

    # Rate limiting
    # NOTE: 60/minute is a starting point - will likely need tuning based on usage
    MAX_BOOPS_PER_MINUTE = 60

    # User constraints (5 lines × 40 chars = 200)
    MAX_DISPLAY_NAME_LENGTH = 200
    MAX_TAGLINE_LENGTH = 300
