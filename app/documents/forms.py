from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField, MultipleFileField
from flask import current_app

class UploadDocumentForm(FlaskForm):
    """Form for uploading documents"""
    # Use a more flexible MultipleFileField without strict validation
    # since we're handling validation in the view function
    documents = MultipleFileField('Select Documents')
    submit = SubmitField('Upload Documents') 
 