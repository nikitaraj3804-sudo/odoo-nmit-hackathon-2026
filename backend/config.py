import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file at workspace root if present
basedir = os.path.abspath(os.path.dirname(__file__))
rootdir = os.path.abspath(os.path.join(basedir, '..'))
load_dotenv(os.path.join(rootdir, '.env'))

class Config:
    """
    Centralized Flask application configuration class.
    Supports local .env variables as well as Railway auto-injected MySQL variables.
    """
    
    # Secret Key Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dayflow_default_secret_key_2026')
    
    # Database Environment Variable Discovery (Supports standard DB_* and Railway MYSQL* names)
    DB_HOST = os.environ.get('DB_HOST') or os.environ.get('MYSQLHOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT') or os.environ.get('MYSQLPORT', '3306')
    DB_USER = os.environ.get('DB_USER') or os.environ.get('MYSQLUSER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or os.environ.get('MYSQLPASSWORD', 'password')
    DB_NAME = os.environ.get('DB_NAME') or os.environ.get('MYSQLDATABASE', 'dayflow_hrms')
    
    # Construct default MySQL URI
    default_mysql_uri = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Allow full database URL overrides from environment (e.g., MYSQL_URL, DATABASE_URL, SQLALCHEMY_DATABASE_URI)
    db_uri_env = (
        os.environ.get('SQLALCHEMY_DATABASE_URI') or
        os.environ.get('MYSQL_URL') or
        os.environ.get('DATABASE_URL')
    )
    
    if db_uri_env:
        # Convert standard mysql:// or postgresql:// scheme to mysql+pymysql:// if needed for SQLAlchemy compatibility
        if db_uri_env.startswith('mysql://'):
            db_uri_env = db_uri_env.replace('mysql://', 'mysql+pymysql://', 1)
        SQLALCHEMY_DATABASE_URI = db_uri_env
    else:
        SQLALCHEMY_DATABASE_URI = default_mysql_uri
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dayflow_jwt_secret_key_hackathon_2026')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 24)))
    
    # CORS Configuration - parse comma-separated origin list or accept string
    cors_env = os.environ.get('CORS_ORIGINS') or os.environ.get('CORS_ORIGIN', '*')
    if cors_env == '*':
        CORS_ORIGINS = '*'
    else:
        CORS_ORIGINS = [origin.strip() for origin in cors_env.split(',') if origin.strip()]
