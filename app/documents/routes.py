import os
import uuid
from flask import render_template, redirect, url_for, flash, current_app, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.documents import bp
from app.documents.forms import UploadDocumentForm
from app.models import Document
from app.search import add_document_to_index, remove_document_from_index

def allowed_file(filename):
    """Check if a file has an allowed extension"""
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    # First check if it's in excluded extensions
    if extension in current_app.config.get('EXCLUDED_EXTENSIONS', set()):
        return False
        
    # Then check if it's in allowed extensions
    return extension in current_app.config['ALLOWED_EXTENSIONS']

def get_human_readable_allowed_extensions():
    """Return a human-readable list of allowed file extensions"""
    allowed = current_app.config['ALLOWED_EXTENSIONS']
    
    # Group extensions by category for better readability
    categories = {
        'Text': ['txt', 'csv', 'md', 'log'],
        'Config': ['json', 'yaml', 'yml', 'ini', 'cfg', 'conf', 'xml', 'toml'],
        'Programming': ['py', 'js', 'java', 'c', 'cpp', 'h', 'cs', 'php', 'rb', 'go', 'rs', 'sql', 'sh', 'bat', 'ps1'],
        'Other': ['tex', 'bib']
    }
    
    # Find any extension not in our categories and add to 'Other'
    for ext in allowed:
        found = False
        for cat_exts in categories.values():
            if ext in cat_exts:
                found = True
                break
        if not found:
            categories['Other'].append(ext)
    
    # Build the readable string
    readable = []
    for category, exts in categories.items():
        # Only include categories that have extensions in our allowed list
        cat_exts = [e for e in exts if e in allowed]
        if cat_exts:
            readable.append(f"{category} files ({', '.join(['.' + e for e in cat_exts])})")
    
    return ', '.join(readable)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Handle document uploads"""
    form = UploadDocumentForm()
    
    if request.method == 'POST':
        # Don't use form.validate_on_submit() as we're handling file validation manually
        
        # Check if the post request has the file part
        if 'documents' not in request.files:
            flash('No file part in the request. Please try again with valid files.', 'danger')
            return redirect(request.url)
            
        uploaded_files = request.files.getlist('documents')
        
        # Check if any files were selected
        if len(uploaded_files) == 0 or (len(uploaded_files) == 1 and uploaded_files[0].filename == ''):
            flash('No files selected. Please select at least one document to upload.', 'danger')
            return redirect(request.url)
            
        upload_count = 0
        skipped_files = []
        
        for uploaded_file in uploaded_files:
            if not uploaded_file or not uploaded_file.filename:
                continue
                
            if not allowed_file(uploaded_file.filename):
                ext = uploaded_file.filename.rsplit('.', 1)[1].lower() if '.' in uploaded_file.filename else 'unknown'
                if ext in current_app.config.get('EXCLUDED_EXTENSIONS', set()):
                    skipped_files.append(f'"{uploaded_file.filename}" (excluded file type)')
                else:
                    skipped_files.append(f'"{uploaded_file.filename}" (unsupported format)')
                continue
            
            # Generate a unique filename to prevent collisions
            original_filename = secure_filename(uploaded_file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            
            # Save the file
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            uploaded_file.save(file_path)
            
            # Read file content for indexing and preview
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Create a preview of the first 500 characters
                    content_preview = content[:500] + ('...' if len(content) > 500 else '')
            except Exception as e:
                error_message = str(e)
                flash(f'Error reading file "{original_filename}": {error_message}. The file might be binary or use an unsupported encoding.', 'danger')
                os.remove(file_path)  # Remove the file if we can't read it
                continue
            
            # Create document record in database
            document = Document(
                filename=unique_filename,
                original_filename=original_filename,
                user_id=current_user.id,
                content_preview=content_preview
            )
            db.session.add(document)
            db.session.commit()
            
            # Index the document for search
            add_document_to_index(document, content)
            
            upload_count += 1
    
        if upload_count > 0:
            flash(f'Successfully uploaded {upload_count} document(s)', 'success')
            
            if skipped_files:
                flash(f'Skipped {len(skipped_files)} file(s): {", ".join(skipped_files[:3])}' + 
                      (f' and {len(skipped_files) - 3} more...' if len(skipped_files) > 3 else ''), 
                      'warning')
        else:
            allowed_exts = get_human_readable_allowed_extensions()
            flash(f'No documents were uploaded. Supported file types are: {allowed_exts}', 'warning')
            
        return redirect(url_for('documents.my_documents'))
    
    # For GET requests, show the allowed file types in the template
    allowed_exts = get_human_readable_allowed_extensions()
    return render_template('documents/upload.html', 
                          title='Upload Documents', 
                          form=form, 
                          allowed_extensions=allowed_exts)

@bp.route('/my-documents')
@login_required
def my_documents():
    """View user's documents"""
    documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.upload_date.desc()).all()
    return render_template('documents/my_documents.html', title='My Documents', documents=documents)

@bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    """Delete a document"""
    document = Document.query.get_or_404(doc_id)
    
    # Check if the user owns the document or is an admin
    if document.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this document', 'danger')
        return redirect(url_for('documents.my_documents'))
    
    # Delete file from disk
    try:
        file_path = document.get_file_path()
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        flash(f'Error deleting file: {str(e)}', 'danger')
    
    # Remove document from search index
    remove_document_from_index(document.id)
    
    # Delete document record from database
    db.session.delete(document)
    db.session.commit()
    
    flash('Document deleted successfully', 'success')
    
    if current_user.is_admin and document.user_id != current_user.id:
        return redirect(url_for('admin.manage_documents'))
    else:
        return redirect(url_for('documents.my_documents')) 