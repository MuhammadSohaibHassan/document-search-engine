from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.admin import bp
from app.models import User, Document
from app.admin.utils import admin_required
from werkzeug.security import generate_password_hash

@bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    users_count = User.query.count()
    documents_count = Document.query.count()
    
    return render_template('admin/index.html', 
                         title='Admin Dashboard',
                         users_count=users_count,
                         documents_count=documents_count)

@bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users"""
    users = User.query.all()
    return render_template('admin/users.html', title='Manage Users', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add a new user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'
        
        # Validate input
        if not username or not email or not password:
            flash('All fields are required', 'danger')
            return redirect(url_for('admin.add_user'))
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('admin.add_user'))
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=is_admin
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/add_user.html', title='Add User')

@bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit a user"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        is_admin = request.form.get('is_admin') == 'on'
        
        # Validate input
        if not username or not email:
            flash('Username and email are required', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        # Check if username is taken by another user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash('Username already exists', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        # Check if email is taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            flash('Email already registered', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        # Update user
        user.username = username
        user.email = email
        user.is_admin = is_admin
        
        # Update password if provided
        password = request.form.get('password')
        if password:
            user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html', title='Edit User', user=user)

@bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting the current user
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.manage_users'))

@bp.route('/documents')
@login_required
@admin_required
def manage_documents():
    """Manage all documents"""
    documents = Document.query.join(User).add_columns(User.username).order_by(Document.upload_date.desc()).all()
    return render_template('admin/documents.html', title='Manage Documents', documents=documents) 