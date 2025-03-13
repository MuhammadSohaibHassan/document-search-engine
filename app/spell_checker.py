from spellchecker import SpellChecker
from flask import session
from app.models import User

class CustomSpellChecker:
    def __init__(self):
        self.spell = SpellChecker()
        self.user_custom_words = {}  # Cache for user custom dictionaries
    
    def load_user_dictionary(self, user_id):
        """Load a user's custom dictionary into the spell checker"""
        # Return cached dictionary if available
        if user_id in self.user_custom_words:
            return self.user_custom_words[user_id]
            
        # Get user's custom words from database
        from app import db
        user = User.query.get(user_id)
        
        if user:
            custom_words = user.get_custom_words()
            self.user_custom_words[user_id] = custom_words
            return custom_words
        
        return []
        
    def check_text(self, text, user_id=None):
        """
        Check spelling in a piece of text
        Returns a dict with misspelled words as keys and suggested corrections as values
        """
        if not text:
            return {}
            
        # Split text into words
        words = self._tokenize_text(text)
        
        # Add user custom words if available
        if user_id:
            custom_words = self.load_user_dictionary(user_id)
            for word in custom_words:
                self.spell.word_frequency.add(word)
        
        # Find misspelled words
        misspelled = {}
        for word in words:
            if not self._is_valid_word(word):
                continue
                
            if not self.spell.known([word]):
                # Get correction suggestions
                corrections = self.spell.candidates(word)
                if corrections:
                    misspelled[word] = list(corrections)
        
        return misspelled
    
    def add_to_dictionary(self, word, user_id):
        """Add a word to the user's custom dictionary"""
        if not word or not user_id:
            return False
            
        from app import db
        user = User.query.get(user_id)
        
        if user:
            user.add_custom_word(word)
            db.session.commit()
            
            # Update cache
            if user_id in self.user_custom_words:
                if word not in self.user_custom_words[user_id]:
                    self.user_custom_words[user_id].append(word)
            else:
                self.user_custom_words[user_id] = [word]
                
            return True
            
        return False
    
    def _tokenize_text(self, text):
        """Split text into words, ignoring punctuation"""
        import re
        return re.findall(r'\b\w+\b', text.lower())
    
    def _is_valid_word(self, word):
        """Check if a word should be spell-checked (ignore numbers, etc.)"""
        if not word or len(word) < 2:
            return False
            
        # Ignore words with numbers
        if any(char.isdigit() for char in word):
            return False
            
        return True

# Initialize the spell checker
spell_checker = CustomSpellChecker() 