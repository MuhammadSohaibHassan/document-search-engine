import os
import re
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, DATETIME, STORED, KEYWORD
from whoosh.qparser import QueryParser, OrGroup, MultifieldParser, WildcardPlugin, FuzzyTermPlugin
from whoosh.analysis import StemmingAnalyzer, LowercaseFilter, StandardAnalyzer
from whoosh.highlight import Highlighter, ContextFragmenter
from whoosh.query import Wildcard, Prefix, And, Or, Term
from flask import current_app
from datetime import datetime
import pytz

# Define a custom analyzer that includes stemming and lowercase handling
custom_analyzer = StemmingAnalyzer() | LowercaseFilter()

# Define the schema for our index
# Make sure fields that are intended for searching have proper analyzers
schema = Schema(
    doc_id=ID(stored=True),
    filename=TEXT(analyzer=custom_analyzer, stored=True),
    original_filename=TEXT(analyzer=custom_analyzer, stored=True),
    content=TEXT(analyzer=custom_analyzer, stored=True),
    upload_date=STORED,  # Changed back to STORED to avoid datetime parsing issues
    upload_date_iso=STORED,  # ISO format for client-side date processing
    user_id=KEYWORD(stored=True)  # Change from STORED to KEYWORD for searchability
)

def format_date_pakistan_time(date_obj):
    """Format date in Pakistan Standard Time with more user-friendly format"""
    if isinstance(date_obj, str):
        return date_obj  # Already formatted
        
    # Convert to Pakistan Standard Time
    pk_timezone = pytz.timezone('Asia/Karachi')
    
    if date_obj.tzinfo is None:
        # If date has no timezone info, explicitly set it to UTC
        # This is important since database may store naive datetime objects
        date_obj = date_obj.replace(tzinfo=pytz.UTC)
    
    # Convert to Pakistan time (PKT is UTC+5)
    pk_time = date_obj.astimezone(pk_timezone)
    return pk_time.strftime('%b %d, %Y %I:%M %p') + ' (PKT)'

def init_index():
    """Initialize the search index if it doesn't exist"""
    index_dir = current_app.config['WHOOSH_INDEX_DIR']
    
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    
    if not exists_in(index_dir):
        return create_in(index_dir, schema)
    else:
        return open_dir(index_dir)

def add_document_to_index(document, content):
    """Add or update a document in the search index"""
    index = init_index()
    
    with index.writer() as writer:
        # First, try to delete any existing document with the same ID
        writer.delete_by_term('doc_id', str(document.id))
        
        # Format the date for display
        formatted_date = format_date_pakistan_time(document.upload_date)
        
        # Then add the document to the index
        writer.add_document(
            doc_id=str(document.id),
            filename=document.filename,
            original_filename=document.original_filename,
            content=content,
            upload_date=formatted_date,
            upload_date_iso=document.upload_date.isoformat() if hasattr(document.upload_date, 'isoformat') else '',
            user_id=str(document.user_id)
        )

def remove_document_from_index(document_id):
    """Remove a document from the index"""
    index = init_index()
    
    with index.writer() as writer:
        writer.delete_by_term('doc_id', str(document_id))

def search_documents(query_string, limit=20, user_id=None, partial_match=True, case_sensitive=False, 
                    allow_multiple_results_per_doc=True, max_snippets_per_doc=5):
    """
    Search for documents matching the query string
    
    Args:
        query_string (str): The search query
        limit (int): Maximum number of results to return
        user_id (int): Optional filter by user ID. If None, searches all documents
        partial_match (bool): Whether to allow partial matches (default True)
        case_sensitive (bool): Whether the search is case sensitive (default False)
        allow_multiple_results_per_doc (bool): Whether to return multiple entries for a document (default True)
        max_snippets_per_doc (int): Maximum number of separate snippets per document (default 5)
    
    Returns:
        list: Search results with metadata and highlighted snippets
    """
    if not query_string:
        return []
    
    # Get the index but don't try to force commit - let Whoosh handle its own commits
    index = init_index()
    
    with index.searcher() as searcher:
        # Set up the query parser to search only in fields that have text formats
        # Only search in content and original_filename fields, not in STORED fields
        searchable_fields = ["content", "original_filename", "filename"]
        parser = MultifieldParser(searchable_fields, index.schema, group=OrGroup)
        
        # Add plugins for fuzzy and wildcard searching if partial matching is enabled
        if partial_match:
            parser.add_plugin(FuzzyTermPlugin())
            parser.add_plugin(WildcardPlugin())
            
            # Add wildcards to search terms for partial matching if they don't already have them
            terms = query_string.split()
            enhanced_terms = []
            
            for term in terms:
                if not any(char in term for char in ['*', '?', '~']):
                    # Add wildcard before and after term for partial matching
                    enhanced_terms.append(f"*{term}*")
                else:
                    enhanced_terms.append(term)
            
            query_string = " OR ".join(enhanced_terms)
        
        # Parse the query
        query = parser.parse(query_string)
        
        # If user_id is provided, filter results by user_id
        if user_id is not None:
            user_filter = Term("user_id", str(user_id))
            query = And([query, user_filter])
        
        # Execute search with a very high limit to ensure we get all matching documents
        # We'll manage the per-document snippets ourselves
        results = searcher.search(query, limit=1000)  # Set a very high limit to capture all matches
        
        # Configure highlighter for context snippets - use larger context and better formatting
        from whoosh.highlight import HtmlFormatter
        formatter = HtmlFormatter(tagname="span", classname="search-highlight", between="...")
        formatter.max_chars = 500  # Set max_chars after creating the formatter
        results.formatter = formatter
        fragmenter = ContextFragmenter(surround=60)  # Increase context size around matches
        results.fragmenter = fragmenter
        
        documents = []
        doc_counter = {}  # Track how many times we've seen each document
        unique_docs = set()  # Track unique document IDs
        
        for result in results:
            doc_id = result['doc_id']
            unique_docs.add(doc_id)  # Keep track of unique document IDs
            
            # If we don't want multiple results per document, check if we've already seen this one
            if not allow_multiple_results_per_doc and doc_id in doc_counter:
                continue
            
            # If we want multiple results but have reached the max for this document, skip
            if doc_id in doc_counter and doc_counter[doc_id] >= max_snippets_per_doc:
                continue
            
            # Increment the counter for this document
            doc_counter[doc_id] = doc_counter.get(doc_id, 0) + 1
            
            # Get the highlights for this document
            # The top parameter controls the number of separate fragments to extract
            # Set it higher to get more fragments
            highlight_count = max_snippets_per_doc  # Always try to get maximum number of snippets
            snippet = result.highlights("content", top=highlight_count)
            
            if not snippet:
                # If no highlight, take the beginning of the content
                snippet = result["content"][:350] + "..."
            
            # Create a result entry for this document/snippet
            documents.append({
                'id': doc_id,
                'filename': result['original_filename'],
                'snippet': snippet,
                'score': result.score,
                'upload_date': result['upload_date'],
                'occurrence_number': doc_counter[doc_id],  # Add occurrence number
                'match_terms': query_string  # Include the search terms for reference
            })
            
            # Only limit total results if we're not trying to show all matching documents
            if len(documents) >= limit * 2 and not allow_multiple_results_per_doc:
                break
        
        # Add a summary of total matches at the top-level
        total_docs_in_system = len(Document.query.all()) if 'Document' in globals() else 0
        
        for doc in documents:
            doc['total_matches_in_doc'] = doc_counter.get(doc['id'], 0)
            doc['total_unique_docs'] = len(unique_docs)
            doc['total_docs_in_system'] = total_docs_in_system
        
        return documents

def rebuild_index():
    """Rebuild the entire search index (admin function)"""
    from app.models import Document
    from app import db
    
    # Delete the existing index
    index_dir = current_app.config['WHOOSH_INDEX_DIR']
    if os.path.exists(index_dir):
        import shutil
        shutil.rmtree(index_dir)
    
    # Create a new index
    index = init_index()
    
    # Get all documents from the database
    documents = Document.query.all()
    indexed_count = 0
    
    for document in documents:
        try:
            # Get the file path
            file_path = document.get_file_path()
            
            # Read the content
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                # Add to index
                add_document_to_index(document, content)
                indexed_count += 1
        except Exception as e:
            current_app.logger.error(f"Error indexing document {document.id}: {str(e)}")
    
    return indexed_count 