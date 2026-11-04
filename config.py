import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Used for securely signing session cookies and flash messages
    SECRET_KEY = 'dev-secret-key-replace-in-production'
    
    # Path to the local SQLite database
    DATABASE = os.path.join(BASE_DIR, 'library.db')