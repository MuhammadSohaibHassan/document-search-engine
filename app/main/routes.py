from flask import render_template, request, jsonify, current_app, send_file, flash, redirect, url_for
from app.main import bp
from app.search import search_documents, rebuild_index
from app.models import Document
from app.spell_checker import spell_checker
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
import os
import logging

# Create a search form with CSRF protection and advanced options
class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    partial_match = BooleanField('Partial Match', default=True)
    case_sensitive = BooleanField('Case Sensitive', default=False)
    global_search = BooleanField('Search All Documents', default=True)
    multiple_results = BooleanField('Show Multiple Matches', default=True)
    submit = SubmitField('Search')

@bp.route('/')
@bp.route('/index')
def index():
    """Home page with search functionality"""
    search_form = SearchForm()
    
    # Get document count for display
    total_docs = Document.query.count()
    user_docs = Document.query.filter_by(user_id=current_user.id).count() if current_user.is_authenticated else 0
    
    return render_template('index.html', 
                           title='Document Search Engine', 
                           form=search_form,
                           total_docs=total_docs,
                           user_docs=user_docs)

@bp.route('/search', methods=['GET', 'POST'])
def search():
    """Handle search requests with advanced options"""
    search_form = SearchForm()
    
    if request.method == 'POST':
        # If form was submitted via POST but doesn't validate, it might be missing CSRF
        # Try to get the query directly from the form data
        if not search_form.validate_on_submit():
            query = request.form.get('query', '')
            partial_match = True
            case_sensitive = False
            global_search = True
            multiple_results = True
        else:
            query = search_form.query.data
            partial_match = search_form.partial_match.data
            case_sensitive = search_form.case_sensitive.data
            global_search = search_form.global_search.data
            multiple_results = search_form.multiple_results.data
    else:
        query = request.args.get('query', '')
        partial_match = request.args.get('partial_match', 'true').lower() == 'true'
        case_sensitive = request.args.get('case_sensitive', 'false').lower() == 'true'
        global_search = request.args.get('global_search', 'true').lower() == 'true'
        multiple_results = request.args.get('multiple_results', 'true').lower() == 'true'
    
    if not query:
        return render_template('search_results.html', 
                             title='Search Results',
                             query='',
                             results=[],
                             partial_match=partial_match,
                             case_sensitive=case_sensitive,
                             global_search=global_search,
                             multiple_results=multiple_results,
                             form=search_form)
    
    # Check for spelling errors
    user_id = current_user.id if current_user.is_authenticated else None
    spelling_errors = spell_checker.check_text(query, user_id)
    
    # Determine if we should filter by user_id
    search_user_id = None if global_search or not current_user.is_authenticated else current_user.id
    
    # Perform search with enhanced options
    try:
        results = search_documents(
            query_string=query,
            limit=100,  # Significantly increased limit to show more comprehensive results
            user_id=search_user_id,
            partial_match=partial_match,
            case_sensitive=case_sensitive,
            allow_multiple_results_per_doc=multiple_results,
            max_snippets_per_doc=5  # Allow up to 5 snippets per document
        )
    except Exception as e:
        # Log the error
        current_app.logger.error(f"Search error: {str(e)}")
        flash(f"Search error: {str(e)}. Please try with different search terms or options.", "danger")
        # Return empty results
        results = []
    
    return render_template('search_results.html', 
                         title='Search Results',
                         query=query,
                         results=results,
                         spelling_errors=spelling_errors,
                         partial_match=partial_match,
                         case_sensitive=case_sensitive,
                         global_search=global_search,
                         multiple_results=multiple_results,
                         form=search_form)

@bp.route('/view/<int:doc_id>')
def view_document(doc_id):
    """View a document"""
    document = Document.query.get_or_404(doc_id)
    
    # Check if file exists
    file_path = document.get_file_path()
    if not os.path.exists(file_path):
        return render_template('error.html', 
                             title='Error',
                             message='Document file not found')
    
    # Read file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return render_template('error.html', 
                             title='Error',
                             message=f'Error reading document: {str(e)}')
    
    return render_template('view_document.html',
                         title=document.original_filename,
                         document=document,
                         content=content)

@bp.route('/download/<int:doc_id>')
def download_document(doc_id):
    """Download a document"""
    document = Document.query.get_or_404(doc_id)
    
    # Check if file exists
    file_path = document.get_file_path()
    if not os.path.exists(file_path):
        return render_template('error.html', 
                             title='Error',
                             message='Document file not found')
    
    # Send file for download
    return send_file(file_path, 
                     as_attachment=True,
                     download_name=document.original_filename)

@bp.route('/api/spell-check', methods=['POST'])
def api_spell_check():
    """API endpoint for spell checking"""
    if not request.is_json:
        # Handle non-JSON requests with a 400 response
        return jsonify({'errors': {}, 'message': 'Request must be JSON'}), 400
    
    text = request.json.get('text', '')
    
    if not text:
        return jsonify({'errors': {}})
    
    # Check spelling
    user_id = current_user.id if current_user.is_authenticated else None
    spelling_errors = spell_checker.check_text(text, user_id)
    
    return jsonify({'errors': spelling_errors})

@bp.route('/api/add-to-dictionary', methods=['POST'])
def api_add_to_dictionary():
    """API endpoint to add a word to the user's custom dictionary"""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': 'You must be logged in'})
    
    if not request.is_json:
        # Handle non-JSON requests with a 400 response
        return jsonify({'success': False, 'message': 'Request must be JSON'}), 400
    
    word = request.json.get('word', '')
    
    if not word:
        return jsonify({'success': False, 'message': 'No word provided'})
    
    # Add word to dictionary
    success = spell_checker.add_to_dictionary(word, current_user.id)
    
    if success:
        return jsonify({'success': True, 'message': f'Added "{word}" to your dictionary'})
    else:
        return jsonify({'success': False, 'message': 'Failed to add word to dictionary'})

@bp.route('/admin/rebuild-index', methods=['POST'])
@login_required
def admin_rebuild_index():
    """Admin function to rebuild the search index"""
    if not current_user.is_admin:
        flash('You do not have permission to perform this action', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        indexed_count = rebuild_index()
        flash(f'Successfully rebuilt search index with {indexed_count} documents', 'success')
        return redirect(url_for('admin.index'))
    except Exception as e:
        current_app.logger.error(f"Index rebuild error: {str(e)}")
        flash(f'Error rebuilding index: {str(e)}', 'danger')
        return redirect(url_for('admin.index')) 