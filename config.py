import os
from pathlib import Path

class Config:
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # CSRF protection settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///docs_search.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    BASE_DIR = Path(__file__).resolve().parent
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    # Expanded list of allowed file extensions (textual, programming, and configuration files)
    ALLOWED_EXTENSIONS = {
        'txt', 'csv', 'md', 'json', 'yaml', 'yml', 'ini', 'cfg', 'conf',  # Text and config files
        'py', 'js', 'java', 'c', 'cpp', 'h', 'cs', 'php', 'rb', 'go', 'rs',  # Programming languages
        'sql', 'sh', 'bat', 'ps1',  # Scripts and database
        'log', 'xml', 'toml',  # Logs and data formats
        'tex', 'bib',  # LaTeX files
    }
    # Explicitly excluded extensions (even if they might contain text)
    EXCLUDED_EXTENSIONS = {'pdf', 'docx', 'doc', 'pptx', 'ppt', 'xlsx', 'xls', 'html', 'htm'}
    # No file size limit
    # MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Whoosh index settings
    WHOOSH_INDEX_DIR = 'whoosh_index'  # This will be created in Flask's instance folder
    
    # Admin settings
    ADMIN_USERNAME = 'admin'
    ADMIN_EMAIL = 'admin@example.com'
    ADMIN_PASSWORD = 'admin123'  # This should be changed in production 