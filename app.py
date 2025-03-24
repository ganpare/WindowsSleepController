import os
import logging
from flask import Flask, request, jsonify, render_template, abort, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
import datetime
from sleep_controller import trigger_sleep
from auth import requires_auth, create_api_key, get_api_keys, check_auth

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("alexa_sleep.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

# Store sleep request history
sleep_requests = []

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if check_auth(username, password):
            session['logged_in'] = True
            session['username'] = username
            flash('ログインに成功しました', 'success')
            return redirect(url_for('index'))
        else:
            flash('ユーザー名かパスワードが間違っています', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user."""
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('ログアウトしました', 'info')
    return redirect(url_for('login'))

@app.route('/')
@requires_auth
def index():
    """Display the admin dashboard."""
    api_keys = get_api_keys()
    return render_template('index.html', 
                          api_keys=api_keys, 
                          sleep_requests=sleep_requests)

@app.route('/api/sleep', methods=['POST'])
def api_sleep():
    """API endpoint to trigger sleep mode."""
    # Option 1: API Key in header
    api_key = request.headers.get('X-API-Key')
    if api_key:
        # Verify API key
        api_keys = get_api_keys()
        if any(check_password_hash(stored_key, api_key) for stored_key in api_keys):
            # API key is valid, proceed
            pass
        else:
            logger.warning(f"Sleep request with invalid API key: {api_key[:5]}...")
            return jsonify({"error": "無効なAPIキー"}), 401
    
    # Option 2: Basic auth as fallback
    elif request.authorization:
        auth = request.authorization
        if not check_auth(auth.username, auth.password):
            logger.warning("Sleep request with invalid Basic auth")
            return jsonify({"error": "無効な認証情報"}), 401
    else:
        logger.warning("Sleep request received without authentication")
        return jsonify({"error": "Authentication required"}), 401
    
    # Log the request details
    timestamp = datetime.datetime.now()
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    logger.info(f"Sleep request accepted from {client_ip} with user agent: {user_agent}")
    
    # Add to request history
    sleep_requests.append({
        'timestamp': timestamp,
        'ip': client_ip,
        'user_agent': user_agent
    })
    
    # Limit history to last 20 entries
    if len(sleep_requests) > 20:
        sleep_requests.pop(0)
    
    # Trigger sleep
    success, message = trigger_sleep()
    
    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        logger.error(f"Failed to trigger sleep: {message}")
        return jsonify({"status": "error", "message": message}), 500

@app.route('/generate-api-key', methods=['POST'])
@requires_auth
def generate_api_key():
    """Generate a new API key."""
    key = create_api_key()
    flash('新しいAPIキーが正常に生成されました', 'success')
    return redirect(url_for('index'))

@app.route('/status')
def status():
    """Simple status endpoint to verify the service is running."""
    return render_template('status.html', uptime=datetime.datetime.now())

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
