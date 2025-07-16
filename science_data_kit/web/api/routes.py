"""
API Routes for the Flask Application

This module defines the REST API endpoints for the Flask application.
"""

from flask import Blueprint, jsonify, request, session
from functools import wraps

from science_data_kit.core.pages.dashboard import DashboardPage
from science_data_kit.core.pages.file_browser import FileBrowserPage
from science_data_kit.core.pages.connect import ConnectPage
from science_data_kit.core.pages.explore import ExplorePage
from science_data_kit.web.adapters.flask_adapter import render_page_api

# Create a blueprint for the API routes
api_bp = Blueprint('api', __name__)

def api_login_required(f):
    """
    Decorator to require login for API routes.

    If the user is not logged in, a 401 Unauthorized response is returned.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def register_api_routes(app):
    """
    Register API routes with the Flask application.

    Args:
        app: The Flask application instance.
    """
    # Register the API blueprint with the API prefix
    app.register_blueprint(api_bp, url_prefix=app.config['API_PREFIX'])

@api_bp.route('/dashboard')
@api_login_required
def dashboard():
    """Get dashboard data."""
    page = DashboardPage()
    return render_page_api(page)

@api_bp.route('/files')
@api_login_required
def files():
    """Get file browser data."""
    # Get query parameters
    path = request.args.get('path', '')
    view_mode = request.args.get('view_mode', 'list')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'ascending')
    filter_pattern = request.args.get('filter', None)

    page = FileBrowserPage(
        current_path=path,
        view_mode=view_mode,
        sort_by=sort_by,
        sort_order=sort_order,
        filter_pattern=filter_pattern
    )
    return render_page_api(page)

@api_bp.route('/connect')
@api_login_required
def connect():
    """Get connection data."""
    page = ConnectPage()
    return render_page_api(page)

@api_bp.route('/connect/create', methods=['POST'])
@api_login_required
def create_connection():
    """Create a new connection."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    connection_type = data.get('type')
    name = data.get('name')
    config = data.get('config', {})

    if not connection_type or not name:
        return jsonify({'error': 'Connection type and name are required'}), 400

    page = ConnectPage()
    success = page.connect(connection_type, config, name)

    if success:
        return jsonify({
            'success': True,
            'message': f'Connection {name} created successfully',
            'data': render_page_api(page).json
        })
    else:
        return jsonify({
            'success': False,
            'message': f'Failed to create connection: {page.connection_errors.get(list(page.connection_errors.keys())[-1], "Unknown error")}',
            'data': render_page_api(page).json
        }), 400

@api_bp.route('/connect/test', methods=['POST'])
@api_login_required
def test_connection():
    """Test a connection without saving it."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    connection_type = data.get('type')
    config = data.get('config', {})

    if not connection_type:
        return jsonify({'error': 'Connection type is required'}), 400

    page = ConnectPage()
    result = page.test_connection(connection_type, config)

    return jsonify(result)

@api_bp.route('/connect/disconnect', methods=['POST'])
@api_login_required
def disconnect():
    """Disconnect from a data source."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    connection_id = data.get('connection_id')

    if not connection_id:
        return jsonify({'error': 'Connection ID is required'}), 400

    page = ConnectPage()
    success = page.disconnect(connection_id)

    if success:
        return jsonify({
            'success': True,
            'message': 'Connection disconnected successfully',
            'data': render_page_api(page).json
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Failed to disconnect',
            'data': render_page_api(page).json
        }), 400

@api_bp.route('/connect/oauth/initiate', methods=['POST'])
@api_login_required
def initiate_oauth():
    """Initiate OAuth authorization flow."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    connection_type = data.get('type')
    config = data.get('config', {})

    if not connection_type:
        return jsonify({'error': 'Connection type is required'}), 400

    # Get the base URL for constructing the redirect URI
    base_url = request.host_url.rstrip('/')

    page = ConnectPage()
    success, message, auth_url = page.initiate_oauth(connection_type, config, base_url)

    if success:
        return jsonify({
            'success': True,
            'message': message,
            'auth_url': auth_url,
            'data': render_page_api(page).json
        })
    else:
        return jsonify({
            'success': False,
            'message': message,
            'data': render_page_api(page).json
        }), 400

@api_bp.route('/connect/oauth/callback')
@api_login_required
def oauth_callback():
    """Handle OAuth callback."""
    # Get query parameters
    code = request.args.get('code')
    state = request.args.get('state')

    if not code or not state:
        return jsonify({'error': 'Code and state parameters are required'}), 400

    # Get the base URL for constructing the redirect URI
    base_url = request.host_url.rstrip('/')

    page = ConnectPage()
    success, message, connection_id = page.handle_oauth_callback(code, state, base_url)

    if success:
        # Redirect to the connect page with a success message
        return jsonify({
            'success': True,
            'message': message,
            'connection_id': connection_id,
            'data': render_page_api(page).json
        })
    else:
        # Redirect to the connect page with an error message
        return jsonify({
            'success': False,
            'message': message,
            'data': render_page_api(page).json
        }), 400

@api_bp.route('/explore')
@api_login_required
def explore():
    """Get explore data."""
    page = ExplorePage()
    return render_page_api(page)

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """Handle API login."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Simple authentication for demonstration purposes
    # In a real application, you would validate against a database
    if username == 'admin' and password == 'password':
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@api_bp.route('/auth/logout', methods=['POST'])
def logout():
    """Handle API logout."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logout successful'})

@api_bp.route('/auth/status')
def auth_status():
    """Get authentication status."""
    if session.get('logged_in'):
        return jsonify({
            'authenticated': True,
            'username': session.get('username')
        })
    else:
        return jsonify({'authenticated': False})
