from flask_login import UserMixin
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
import os
from app import db

def get_pakistan_time():
    """Return current time in Pakistan Standard Time"""
    # Get current UTC time with timezone info
    utc_now = datetime.now(pytz.UTC)
    # Convert to Pakistan time (PKT is UTC+5)
    return utc_now.astimezone(pytz.timezone('Asia/Karachi'))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_pakistan_time)
    custom_words = db.Column(db.Text, default='')  # Store custom dictionary words as comma-separated string
    
    # Relationship with documents
    documents = db.relationship('Document', backref='uploader', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def add_custom_word(self, word):
        """Add a word to the user's custom dictionary"""
        if not self.custom_words:
            self.custom_words = word
        else:
            words = self.custom_words.split(',')
            if word not in words:
                words.append(word)
                self.custom_words = ','.join(words)

    def get_custom_words(self):
        """Return the user's custom dictionary as a list"""
        if not self.custom_words:
            return []
        return self.custom_words.split(',')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    original_filename = db.Column(db.String(128), nullable=False)
    upload_date = db.Column(db.DateTime, default=get_pakistan_time)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content_preview = db.Column(db.Text)  # Store a preview of the content for quick display
    
    def get_file_path(self):
        """Return the full path to the document file"""
        from flask import current_app
        return os.path.join(current_app.config['UPLOAD_FOLDER'], self.filename)
    
    def __repr__(self):
        return f'<Document {self.original_filename}>' 