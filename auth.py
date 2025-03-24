import os
import json
import uuid
import logging
from functools import wraps
from flask import request, Response, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

# Path to store API keys
API_KEYS_FILE = 'api_keys.json'

# Default admin credentials - should be changed in production
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'

def requires_auth(f):
    """Decorator for routes that require authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def check_auth(username, password):
    """
    Check if the provided credentials are valid.
    In a production environment, use a more secure method.
    """
    # Get credentials from environment variables or use defaults
    admin_username = os.environ.get('ADMIN_USERNAME', DEFAULT_USERNAME)
    admin_password = os.environ.get('ADMIN_PASSWORD', DEFAULT_PASSWORD)
    
    return username == admin_username and password == admin_password

# Legacy function kept for API authentication
def authenticate():
    """Send the authentication challenge."""
    return Response(
        'Could not verify your access level.\n'
        'Please login with proper credentials',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def get_api_keys():
    """Retrieve stored API keys."""
    try:
        if not os.path.exists(API_KEYS_FILE):
            # Create initial API key if none exists
            keys = []
            with open(API_KEYS_FILE, 'w') as f:
                json.dump(keys, f)
            return keys
        
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error retrieving API keys: {e}")
        return []

def create_api_key():
    """Generate a new API key and store the hash."""
    try:
        # Generate a random API key
        api_key = str(uuid.uuid4())
        
        # Hash the key for storage
        hashed_key = generate_password_hash(api_key)
        
        # Store the hash
        keys = get_api_keys()
        keys.append(hashed_key)
        
        with open(API_KEYS_FILE, 'w') as f:
            json.dump(keys, f)
        
        logger.info(f"New API key generated: {api_key[:5]}...")
        return api_key
    except Exception as e:
        logger.error(f"Error creating API key: {e}")
        return None
