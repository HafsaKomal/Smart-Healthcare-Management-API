import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key'
    
    # MongoDB Configuration
    MONGODB_SETTINGS = {
        'db': 'healthcare_db',
        'host': 'localhost',
        'port': 27017,
        'replicaset': 'rs0'  # If you are using Mongo replica sets for failover
    }
