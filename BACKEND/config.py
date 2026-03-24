"""
Configuration settings for Code Nest Backend
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///codenest.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # LLM API settings
    TOGETHER_API_KEY = os.environ.get('TOGETHER_API_KEY')
    TOGETHER_BASE_URL = 'https://api.together.xyz/v1'

    # Sandbox settings
    CODE_EXECUTION_TIMEOUT = 10  # seconds
    MAX_OUTPUT_SIZE = 10000  # characters
    MAX_MEMORY_MB = 50  # megabytes

    # Security settings
    ALLOWED_MODULES = {
        'math', 'random', 'datetime', 'json', 'string', 're',
        'itertools', 'collections', 'functools', 'operator'
    }

    FORBIDDEN_FUNCTIONS = {
        'exec', 'eval', 'compile', '__import__', 'open', 'file',
        'input', 'raw_input', 'reload', 'exit', 'quit'
    }

    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000

    # CORS settings
    CORS_ORIGINS = ['http://localhost:5000', 'https://codenest.app']

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    # Badge requirements
    BADGE_REQUIREMENTS = {
        'first_lesson': {'lessons_completed': 1},
        'getting_started': {'lessons_completed': 3},
        'loop_master': {'loop_lessons_completed': 5},
        'math_genius': {'math_challenges_completed': 3},
        'streak_keeper': {'streak_days': 7},
        'star_collector': {'total_stars': 50},
        'challenge_champion': {'challenges_completed': 10}
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # Use PostgreSQL in production
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}