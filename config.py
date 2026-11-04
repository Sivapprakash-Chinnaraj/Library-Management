import os

class Config:
    # Secret key for session management and flash messages
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    
    # AWS RDS MySQL Connection Variables
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'library-app-db.cpoyi8asy7yx.ap-south-1.rds.amazonaws.com'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'admin'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'Hsakarppavis1634'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'library'
