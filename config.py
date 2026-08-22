import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'campusconnect-super-secure-secret-key-2026')
    
    # Database configuration (SQLite default, PostgreSQL for Render if DATABASE_URL provided)
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        # Fix SQLAlchemy compatibility for Render postgres:// URLs
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
    SQLALCHEMY_DATABASE_URI = database_url or f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'campusconnect.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'zip'}
    
    # Session lifetime and cookie settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    WTF_CSRF_CHECK_DEFAULT = False
    
    # AI Chatbot settings
    AI_API_KEY = os.environ.get('AI_API_KEY', '')
    AI_MODEL = os.environ.get('AI_MODEL', 'gemini-1.5-flash')
    
    # Academic minimum attendance threshold (percentage)
    MIN_ATTENDANCE_PERCENTAGE = 75.0

    # Base Application URL (used in email links)
    APP_BASE_URL = os.environ.get('APP_BASE_URL', 'http://localhost:5000')

    # SMTP & Email Notification Settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true', '1', 't', 'yes')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ('true', '1', 't', 'yes')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'CampusConnect <noreply@campusconnect.edu>')
    MAIL_ENABLED = os.environ.get('MAIL_ENABLED', 'true').lower() in ('true', '1', 't', 'yes')
    MAIL_DEBUG_LOG = os.environ.get('MAIL_DEBUG_LOG', 'true').lower() in ('true', '1', 't', 'yes')


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
