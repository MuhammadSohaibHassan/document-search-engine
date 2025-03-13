import os
import sys
from datetime import datetime
import shutil

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import Flask application components
from app import create_app, db
from app.models import User, Document

app = create_app()

def init_database():
    """Initialize the database and create admin user"""
    with app.app_context():
        print("Creating database...")
        # Create database tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if admin is None:
            print("Creating admin user...")
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('password')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created with username 'admin' and password 'password'")
            print("IMPORTANT: Please change this password after first login!")
        else:
            print("Admin user already exists")
        
        # Create upload directory if it doesn't exist
        uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        print(f"Created uploads directory: {uploads_dir}")
        
        # Create Whoosh index directory if it doesn't exist
        index_dir = app.config['WHOOSH_INDEX_DIR']
        os.makedirs(index_dir, exist_ok=True)
        print(f"Created search index directory: {index_dir}")
        
        print("Database initialization complete!")
        print("\nYou can now run the application with: python run.py")

if __name__ == '__main__':
    init_database() 