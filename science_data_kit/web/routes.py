"""
Main Routes for the Flask Application

This module defines the main routes for the Flask application.
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify, make_response
from functools import wraps
import os

from science_data_kit.core.pages.dashboard import DashboardPage
from science_data_kit.core.pages.file_browser import FileBrowserPage
from science_data_kit.core.pages.connect import ConnectPage
from science_data_kit.core.pages.explore import ExplorePage
from science_data_kit.core.pages.plugin_connect import PluginConnectPage
from science_data_kit.core.pages.cbioportal_browser import CbioportalBrowserPage
from science_data_kit.core.pages.dropbox_connect import DropboxConnectPage
from science_data_kit.core.pages.dropbox_browser import DropboxBrowserPage
from science_data_kit.core.pages.isa_browser import IsaBrowserPage
from science_data_kit.web.adapters.flask_adapter import render_page_html, render_page_api

# Create a blueprint for the main routes
main_bp = Blueprint('main', __name__)

def login_required(f):
    """
    Decorator to require login for routes.

    If the user is not logged in, they will be redirected to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        # Simple authentication for demonstration purposes
        username = request.form.get('username')
        password = request.form.get('password')

        # In a real application, you would validate against a database
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            session['username'] = username
            flash('You have been logged in!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')

    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out!', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Render the dashboard page."""
    page = DashboardPage()
    return render_page_html(page)

@main_bp.route('/api/dashboard/data')
@login_required
def dashboard_data():
    """Get dashboard data."""
    page = DashboardPage()
    page_data = page.get_page_data()

    return jsonify({
        'metrics': page_data.metrics,
        'charts': page_data.charts,
        'tables': page_data.tables,
        'status_items': page_data.status_items,
        'connected_services': page_data.connected_services,
        'recent_activities': page_data.recent_activities,
        'feature_categories': page_data.feature_categories
    })

@main_bp.route('/api/dashboard/connect-database', methods=['POST'])
@login_required
def connect_to_database():
    """Connect to a database."""
    uri = request.form.get('uri')
    username = request.form.get('username')
    password = request.form.get('password')
    database = request.form.get('database')
    conn_name = request.form.get('conn_name')

    if not uri or not username or not password or not database:
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400

    page = DashboardPage()
    result = page.connect_to_database(uri, username, password, database, conn_name)

    if result['success']:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result['error']})

@main_bp.route('/api/dashboard/disconnect-database', methods=['POST'])
@login_required
def disconnect_from_database():
    """Disconnect from a database."""
    page = DashboardPage()
    result = page.disconnect_from_database()

    if result['success']:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result['error']})

@main_bp.route('/files')
@login_required
def files():
    """Render the file browser page."""
    path = request.args.get('path', os.path.expanduser('~'))
    view_mode = request.args.get('view_mode', 'list')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'ascending')
    filter_pattern = request.args.get('filter', None)

    page = FileBrowserPage(initial_path=path)
    page.set_view_mode(view_mode)
    page.set_sort(sort_by, sort_order)
    if filter_pattern:
        page.set_filter(filter_pattern)

    return render_page_html(page)

@main_bp.route('/api/files')
@login_required
def files_api():
    """API endpoint for the file browser page."""
    path = request.args.get('path', os.path.expanduser('~'))
    page = FileBrowserPage(initial_path=path)
    return render_page_api(page)

@main_bp.route('/api/files/navigate')
@login_required
def navigate_directory():
    """HTMX endpoint for navigating directories."""
    path = request.args.get('path', os.path.expanduser('~'))
    view_mode = request.args.get('view_mode', 'list')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'ascending')

    page = FileBrowserPage(initial_path=path)
    page.set_view_mode(view_mode)
    page.set_sort(sort_by, sort_order)

    return render_template('partials/file_listing.html',
                          files=page.get_page_data().files,
                          directories=page.get_page_data().directories,
                          current_path=page.get_page_data().current_path,
                          view_mode=view_mode,
                          selected_files=[])

@main_bp.route('/api/files/filter')
@login_required
def filter_files():
    """HTMX endpoint for filtering files."""
    path = request.args.get('path', os.path.expanduser('~'))
    filter_pattern = request.args.get('filter', '')
    view_mode = request.args.get('view_mode', 'list')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'ascending')

    page = FileBrowserPage(initial_path=path)
    page.set_view_mode(view_mode)
    page.set_sort(sort_by, sort_order)
    page.set_filter(filter_pattern)

    return render_template('partials/file_listing.html',
                          files=page.get_page_data().files,
                          directories=page.get_page_data().directories,
                          current_path=page.get_page_data().current_path,
                          view_mode=view_mode,
                          selected_files=[])

@main_bp.route('/api/files/preview')
@login_required
def preview_file():
    """HTMX endpoint for previewing a file."""
    file_path = request.args.get('path', '')
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found'}), 404

    file_type = os.path.splitext(file_path)[1].lower()

    # Read the first 100KB of the file for preview
    try:
        with open(file_path, 'rb') as f:
            content = f.read(102400)

        # Handle different file types
        text_file_extensions = [
            '.txt', '.md', '.csv', '.json', '.yaml', '.yml', 
            '.py', '.js', '.html', '.css', '.java', '.c', '.cpp', 
            '.cs', '.go', '.php', '.rb', '.rs', '.ts', '.sh', 
            '.xml', '.log', '.ini', '.conf', '.toml', '.sql'
        ]

        image_file_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
            '.svg', '.webp', '.ico', '.tiff', '.tif'
        ]

        pdf_file_extensions = ['.pdf']

        if file_type in text_file_extensions:
            # Text files
            try:
                content = content.decode('utf-8')
                return render_template('partials/preview_text.html', content=content, file_path=file_path)
            except UnicodeDecodeError:
                return render_template('partials/preview_binary.html', file_path=file_path)
        elif file_type in image_file_extensions:
            # Image files
            return render_template('partials/preview_image.html', file_path=file_path)
        elif file_type in pdf_file_extensions:
            # PDF files
            return render_template('partials/preview_pdf.html', file_path=file_path)
        else:
            # Binary files
            return render_template('partials/preview_binary.html', file_path=file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/files/download')
@login_required
def download_file():
    """Endpoint for downloading a file."""
    from flask import send_file

    file_path = request.args.get('path', '')
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/files/raw')
@login_required
def raw_file():
    """Endpoint for serving raw file content (e.g., for images)."""
    from flask import send_file

    file_path = request.args.get('path', '')
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        return send_file(file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/files/upload', methods=['POST'])
@login_required
def upload_file():
    """Endpoint for uploading files."""
    from werkzeug.utils import secure_filename

    # Get the target directory
    target_dir = request.form.get('path', os.path.expanduser('~'))

    if not os.path.isdir(target_dir):
        return jsonify({'error': 'Target directory not found'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(target_dir, filename)
        file.save(file_path)

        # Return updated file listing
        page = FileBrowserPage(initial_path=target_dir)
        page.set_view_mode(request.form.get('view_mode', 'list'))

        return render_template('partials/file_listing.html',
                              files=page.get_page_data().files,
                              directories=page.get_page_data().directories,
                              current_path=page.get_page_data().current_path,
                              view_mode=request.form.get('view_mode', 'list'),
                              selected_files=[])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/files/create-folder', methods=['POST'])
@login_required
def create_folder():
    """Endpoint for creating a new folder."""
    parent_dir = request.form.get('path', os.path.expanduser('~'))
    folder_name = request.form.get('folder_name', '')

    if not folder_name:
        return jsonify({'error': 'Folder name is required'}), 400

    if not os.path.isdir(parent_dir):
        return jsonify({'error': 'Parent directory not found'}), 404

    try:
        # Create the folder
        new_folder_path = os.path.join(parent_dir, folder_name)
        os.makedirs(new_folder_path, exist_ok=True)

        # Return updated file listing
        page = FileBrowserPage(initial_path=parent_dir)
        page.set_view_mode(request.form.get('view_mode', 'list'))

        return render_template('partials/file_listing.html',
                              files=page.get_page_data().files,
                              directories=page.get_page_data().directories,
                              current_path=page.get_page_data().current_path,
                              view_mode=request.form.get('view_mode', 'list'),
                              selected_files=[])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/files/delete', methods=['POST'])
@login_required
def delete_files():
    """Endpoint for deleting files and folders."""
    import shutil

    parent_dir = request.form.get('path', os.path.expanduser('~'))
    file_paths = request.form.getlist('file_paths[]')

    if not file_paths:
        return jsonify({'error': 'No files selected'}), 400

    try:
        for file_path in file_paths:
            # Ensure the file is within the parent directory (security check)
            if not file_path.startswith(parent_dir):
                continue

            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        # Return updated file listing
        page = FileBrowserPage(initial_path=parent_dir)
        page.set_view_mode(request.form.get('view_mode', 'list'))

        return render_template('partials/file_listing.html',
                              files=page.get_page_data().files,
                              directories=page.get_page_data().directories,
                              current_path=page.get_page_data().current_path,
                              view_mode=request.form.get('view_mode', 'list'),
                              selected_files=[])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/files/rename', methods=['POST'])
@login_required
def rename_file():
    """Endpoint for renaming a file or folder."""
    parent_dir = request.form.get('path', os.path.expanduser('~'))
    file_path = request.form.get('file_path', '')
    new_name = request.form.get('new_name', '')

    if not file_path or not new_name:
        return jsonify({'error': 'File path and new name are required'}), 400

    if not os.path.exists(file_path):
        return jsonify({'error': 'File or directory not found'}), 404

    try:
        # Get the directory containing the file
        dir_path = os.path.dirname(file_path)
        # Create the new path
        new_path = os.path.join(dir_path, new_name)
        # Rename the file or directory
        os.rename(file_path, new_path)

        # Return updated file listing
        page = FileBrowserPage(initial_path=parent_dir)
        page.set_view_mode(request.form.get('view_mode', 'list'))

        return render_template('partials/file_listing.html',
                              files=page.get_page_data().files,
                              directories=page.get_page_data().directories,
                              current_path=page.get_page_data().current_path,
                              view_mode=request.form.get('view_mode', 'list'),
                              selected_files=[])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/connect')
@login_required
def connect():
    """Render the connect page."""
    page = ConnectPage()
    return render_page_html(page)

@main_bp.route('/api/connect/available')
@login_required
def available_connections():
    """Get available connection types."""
    page = ConnectPage()
    return jsonify(page._get_available_connections())

@main_bp.route('/api/connect/active')
@login_required
def active_connections():
    """Get active connections."""
    page = ConnectPage()
    return jsonify(page._get_active_connections())

@main_bp.route('/api/connect/connect', methods=['POST'])
@login_required
def connect_to_source():
    """Connect to a data source."""
    connection_type = request.form.get('connection_type')
    name = request.form.get('name')

    # Build the config dictionary from form data
    config = {}
    for key, value in request.form.items():
        if key not in ['connection_type', 'name']:
            config[key] = value

    page = ConnectPage()
    success = page.connect(connection_type, config, name)

    if success:
        return jsonify({'success': True})
    else:
        error = page.connection_errors.get(f"{connection_type}_{len(page.active_connections)-1}", 
                                          "Failed to connect to data source")
        return jsonify({'success': False, 'error': error})

@main_bp.route('/api/connect/disconnect', methods=['POST'])
@login_required
def disconnect_from_source():
    """Disconnect from a data source."""
    connection_id = request.form.get('connection_id')

    page = ConnectPage()
    success = page.disconnect(connection_id)

    if success:
        return jsonify({'success': True})
    else:
        error = page.connection_errors.get(connection_id, "Failed to disconnect from data source")
        return jsonify({'success': False, 'error': error})

@main_bp.route('/api/connect/test', methods=['POST'])
@login_required
def test_connection_to_source():
    """Test a connection without saving it."""
    connection_type = request.form.get('connection_type')

    # Build the config dictionary from form data
    config = {}
    for key, value in request.form.items():
        if key != 'connection_type':
            config[key] = value

    page = ConnectPage()
    result = page.test_connection(connection_type, config)

    return jsonify(result)

@main_bp.route('/api/connect/oauth/initiate', methods=['POST'])
@login_required
def initiate_oauth_flow():
    """Initiate OAuth authorization flow."""
    connection_type = request.form.get('connection_type')

    # Build the config dictionary from form data
    config = {}
    for key, value in request.form.items():
        if key != 'connection_type':
            config[key] = value

    # Get the base URL
    base_url = request.host_url.rstrip('/')

    page = ConnectPage()
    success, message, auth_url = page.initiate_oauth(connection_type, config, base_url)

    if success:
        return jsonify({'success': True, 'message': message, 'auth_url': auth_url})
    else:
        return jsonify({'success': False, 'error': message})

@main_bp.route('/api/connect/oauth/callback')
def oauth_callback():
    """Handle OAuth callback."""
    code = request.args.get('code')
    state = request.args.get('state')

    if not code or not state:
        flash('OAuth authorization failed: Missing parameters', 'danger')
        return redirect(url_for('main.connect'))

    # Get the base URL
    base_url = request.host_url.rstrip('/')

    page = ConnectPage()
    success, message, conn_id = page.handle_oauth_callback(code, state, base_url)

    if success:
        flash('OAuth authorization successful', 'success')
    else:
        flash(f'OAuth authorization failed: {message}', 'danger')

    return redirect(url_for('main.connect'))

@main_bp.route('/explore')
@login_required
def explore():
    """Render the explore page."""
    page = ExplorePage()
    return render_page_html(page)

@main_bp.route('/api/explore/data-sources')
@login_required
def explore_data_sources():
    """Get available data sources for exploration."""
    page = ExplorePage()
    return jsonify(page._get_available_data_sources())

@main_bp.route('/api/explore/set-data-source', methods=['POST'])
@login_required
def set_explore_data_source():
    """Set the current data source for exploration."""
    data_source_id = request.form.get('data_source_id')

    if not data_source_id:
        return jsonify({'success': False, 'error': 'Data source ID is required'}), 400

    page = ExplorePage()
    success = page.set_data_source(data_source_id)

    if success:
        return jsonify({
            'success': True,
            'schema_info': page.schema_info
        })
    else:
        return jsonify({'success': False, 'error': f'Invalid data source ID: {data_source_id}'}), 400

@main_bp.route('/api/explore/execute-query', methods=['POST'])
@login_required
def execute_explore_query():
    """Execute a query on the current data source."""
    query = request.form.get('query')
    data_source_id = request.form.get('data_source_id')

    if not query:
        return jsonify({'success': False, 'error': 'Query is required'}), 400

    page = ExplorePage()

    # Set the data source if provided
    if data_source_id:
        if not page.set_data_source(data_source_id):
            return jsonify({'success': False, 'error': f'Invalid data source ID: {data_source_id}'}), 400

    # Execute the query
    success = page.execute_query(query)

    if success:
        return jsonify({
            'success': True,
            'query_results': page.query_results,
            'visualizations': page.visualizations
        })
    else:
        error = page.query_results.get('error', 'Failed to execute query') if page.query_results else 'Failed to execute query'
        return jsonify({'success': False, 'error': error}), 400

@main_bp.route('/api/explore/schema-info')
@login_required
def get_schema_info():
    """Get schema information for a data source."""
    data_source_id = request.args.get('data_source_id')

    if not data_source_id:
        return jsonify({'success': False, 'error': 'Data source ID is required'}), 400

    page = ExplorePage()
    schema_info = page._get_schema_info(data_source_id)

    if schema_info:
        return jsonify({'success': True, 'schema_info': schema_info})
    else:
        return jsonify({'success': False, 'error': f'Schema information not available for data source: {data_source_id}'}), 404

@main_bp.route('/plugin-connect')
@login_required
def plugin_connect():
    """Render the plugin connect page."""
    page = PluginConnectPage()
    return render_page_html(page)

@main_bp.route('/api/plugins/info')
@login_required
def plugin_info():
    """Get information about a plugin."""
    plugin_type = request.args.get('type')
    plugin_name = request.args.get('name')

    if not plugin_type or not plugin_name:
        return jsonify({'error': 'Plugin type and name are required'}), 400

    from science_data_kit.core.connections.manager import manager

    # Get the plugin class
    plugin_class = manager.get_plugin_class(plugin_type, plugin_name)
    if not plugin_class:
        return jsonify({'error': f'Plugin not found: {plugin_type}/{plugin_name}'}), 404

    # Create an instance to get plugin info
    plugin_instance = plugin_class()

    # Get plugin info
    plugin_info = {
        'name': plugin_name,
        'type': plugin_type,
        'version': getattr(plugin_instance, 'version', 'Unknown'),
        'description': getattr(plugin_instance, 'description', 'No description available'),
        'capabilities': getattr(plugin_instance, 'capabilities', [])
    }

    return jsonify(plugin_info)

@main_bp.route('/api/plugins/config-schema')
@login_required
def plugin_config_schema():
    """Get the configuration schema for a plugin."""
    plugin_type = request.args.get('type')
    plugin_name = request.args.get('name')

    if not plugin_type or not plugin_name:
        return jsonify({'error': 'Plugin type and name are required'}), 400

    from science_data_kit.core.connections.manager import manager

    # Get the plugin class
    plugin_class = manager.get_plugin_class(plugin_type, plugin_name)
    if not plugin_class:
        return jsonify({'error': f'Plugin not found: {plugin_type}/{plugin_name}'}), 404

    # Create an instance to get the config schema
    plugin_instance = plugin_class()

    # Get the config schema
    config_schema = plugin_instance.config_schema

    # Convert the schema to a dictionary
    schema_dict = {
        'fields': []
    }

    for field in config_schema.fields:
        field_dict = {
            'name': field.name,
            'type': field.field_type.value,
            'label': field.name.replace('_', ' ').title(),
            'description': field.description,
            'required': field.required,
            'default': field.default
        }

        if field.field_type.value == 'enum':
            field_dict['options'] = [{'value': v, 'label': v} for v in field.enum_values]

        schema_dict['fields'].append(field_dict)

    return jsonify(schema_dict)

@main_bp.route('/api/plugins/connect', methods=['POST'])
@login_required
def connect_plugin():
    """Connect to a plugin."""
    plugin_type = request.form.get('plugin_type')
    plugin_name = request.form.get('plugin_name')
    connection_name = request.form.get('connection_name')

    if not plugin_type or not plugin_name:
        return jsonify({'error': 'Plugin type and name are required'}), 400

    # Get the plugin connect page instance
    page = PluginConnectPage()

    # Select the plugin
    if not page.select_plugin(plugin_type, plugin_name):
        return jsonify({'error': f'Plugin not found: {plugin_type}/{plugin_name}'}), 404

    # Build the config dictionary from form data
    config = {}
    for key, value in request.form.items():
        if key not in ['plugin_type', 'plugin_name', 'connection_name']:
            config[key] = value

    # Connect to the plugin
    if page.connect_plugin(config, connection_name):
        return jsonify({'success': True})
    else:
        error = page.connection_errors.get(f"{plugin_type}_{plugin_name}_0", "Failed to connect to plugin")
        return jsonify({'success': False, 'error': error})

@main_bp.route('/api/plugins/disconnect', methods=['POST'])
@login_required
def disconnect_plugin():
    """Disconnect from a plugin."""
    connection_id = request.form.get('connection_id')

    if not connection_id:
        return jsonify({'error': 'Connection ID is required'}), 400

    # Get the plugin connect page instance
    page = PluginConnectPage()

    # Disconnect from the plugin
    if page.disconnect_plugin(connection_id):
        return jsonify({'success': True})
    else:
        error = page.connection_errors.get(connection_id, "Failed to disconnect from plugin")
        return jsonify({'success': False, 'error': error})

@main_bp.route('/api/plugins/test-connection', methods=['POST'])
@login_required
def test_plugin_connection():
    """Test a plugin connection."""
    connection_id = request.form.get('connection_id')

    if not connection_id:
        return jsonify({'error': 'Connection ID is required'}), 400

    # Get the plugin connect page instance
    page = PluginConnectPage()

    # Find the connection
    connection = None
    for conn in page.active_connections:
        if conn['id'] == connection_id:
            connection = conn
            break

    if not connection:
        return jsonify({'success': False, 'error': 'Connection not found'})

    # Test the connection
    from science_data_kit.core.connections.manager import manager

    try:
        # Get the plugin instance
        plugin_instance = manager.get_plugin_instance(connection['type'], connection['plugin'])
        if not plugin_instance:
            return jsonify({'success': False, 'error': f"Failed to create plugin instance: {connection['type']}/{connection['plugin']}"})

        # Test the connection
        if hasattr(plugin_instance, 'test_connection'):
            result = plugin_instance.test_connection()
            return jsonify({'success': result.get('success', False), 'message': result.get('message', '')})
        else:
            # If the plugin doesn't have a test_connection method, assume it's connected
            return jsonify({'success': True, 'message': 'Connection test successful'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@main_bp.route('/about')
def about():
    """About page with project information."""
    return render_template('about.html')

@main_bp.route('/cbioportal')
@login_required
def cbioportal_browser():
    """cBioPortal browser page for browsing and managing ontology terms."""
    page = CbioportalBrowserPage()
    return render_page_html(page, 'cbioportal_browser.html')

@main_bp.route('/dropbox-connect')
@login_required
def dropbox_connect():
    """Dropbox connection management page."""
    page = DropboxConnectPage()
    return render_page_html(page, 'dropbox_connect.html')

@main_bp.route('/api/dropbox/connect', methods=['POST'])
@login_required
def connect_to_dropbox():
    """Connect to Dropbox API."""
    app_key = request.form.get('app_key')
    app_secret = request.form.get('app_secret')
    refresh_token = request.form.get('refresh_token')
    save_config = request.form.get('save_config') == 'true'
    config_file = request.form.get('config_file')

    if not app_key or not app_secret:
        return jsonify({'success': False, 'error': 'App key and app secret are required'}), 400

    page = DropboxConnectPage()
    result = page.connect(app_key, app_secret, refresh_token, save_config, config_file)

    if result.get('success'):
        # Store connector in session
        session['dropbox_connector'] = page.connector
        session['dropbox_connected'] = True
        return jsonify({'success': True})
    elif result.get('auth_url'):
        # Return auth URL for OAuth flow
        return jsonify({'success': False, 'auth_url': result['auth_url']})
    else:
        return jsonify({'success': False, 'error': result.get('error', 'Failed to connect to Dropbox API')}), 400

@main_bp.route('/api/dropbox/complete-auth', methods=['POST'])
@login_required
def complete_dropbox_auth():
    """Complete Dropbox OAuth authentication."""
    auth_code = request.form.get('auth_code')

    if not auth_code:
        return jsonify({'success': False, 'error': 'Authorization code is required'}), 400

    page = DropboxConnectPage()

    # Restore connector from session if available
    if 'dropbox_connector' in session:
        page.connector = session['dropbox_connector']

    result = page.complete_authentication(auth_code)

    if result.get('success'):
        # Store connector in session
        session['dropbox_connector'] = page.connector
        session['dropbox_connected'] = True
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result.get('error', 'Failed to complete authentication')}), 400

@main_bp.route('/api/dropbox/disconnect', methods=['POST'])
@login_required
def disconnect_from_dropbox():
    """Disconnect from Dropbox API."""
    page = DropboxConnectPage()

    # Restore connector from session if available
    if 'dropbox_connector' in session:
        page.connector = session['dropbox_connector']

    result = page.disconnect()

    # Remove connector from session
    if 'dropbox_connector' in session:
        del session['dropbox_connector']
    session['dropbox_connected'] = False

    if result.get('success'):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result.get('error', 'Failed to disconnect from Dropbox API')}), 400

@main_bp.route('/api/dropbox/status', methods=['GET'])
@login_required
def get_dropbox_status():
    """Get Dropbox connection status."""
    page = DropboxConnectPage()

    # Restore connector from session if available
    if 'dropbox_connector' in session:
        page.connector = session['dropbox_connector']
        page.connection_status['dropbox'] = page.connector.is_connected()

        # Get account info if connected
        if page.connection_status['dropbox']:
            try:
                page.account_info = page.connector.get_account_info()
            except Exception as e:
                page.connection_errors['account_info'] = str(e)

    return jsonify({
        'connected': page.connection_status.get('dropbox', False),
        'account_info': page.account_info,
        'errors': page.connection_errors
    })

@main_bp.route('/api/dropbox/load-config', methods=['POST'])
@login_required
def load_dropbox_config():
    """Load Dropbox configuration from a file."""
    config_file = request.form.get('config_file')

    if not config_file:
        return jsonify({'success': False, 'error': 'Configuration file path is required'}), 400

    page = DropboxConnectPage()
    result = page.load_config_from_file(config_file)

    if result.get('success'):
        return jsonify({'success': True, 'config': result.get('config', {})})
    else:
        return jsonify({'success': False, 'error': result.get('error', 'Failed to load configuration')}), 400

@main_bp.route('/dropbox-browser')
@login_required
def dropbox_browser():
    """Dropbox file browser page."""
    # Get current path from query parameters
    current_path = request.args.get('path', '')

    # Create page instance
    page = DropboxBrowserPage(initial_path=current_path)

    # Restore connector from session if available
    if 'dropbox_connector' in session:
        page.set_connector(session['dropbox_connector'])

    return render_page_html(page, 'dropbox_browser.html')

@main_bp.route('/api/dropbox/files', methods=['GET'])
@login_required
def get_dropbox_files():
    """Get files and folders from Dropbox."""
    path = request.args.get('path', '')

    # Create page instance
    page = DropboxBrowserPage(initial_path=path)

    # Restore connector from session if available
    if 'dropbox_connector' in session:
        page.set_connector(session['dropbox_connector'])

    # Navigate to the specified path
    page.navigate_to(path)

    return jsonify({
        'current_path': page.current_path,
        'files': page.files,
        'directories': page.directories,
        'connection_status': page.connection_status,
        'connection_errors': page.connection_errors
    })

@main_bp.route('/api/dropbox/file', methods=['GET'])
@login_required
def get_dropbox_file():
    """Get file details from Dropbox."""
    file_path = request.args.get('path', '')

    if not file_path:
        return jsonify({'success': False, 'error': 'File path is required'}), 400

    # Create page instance
    page = DropboxBrowserPage()

    # Restore connector from session if available
    if 'dropbox_connector' in session:
        page.set_connector(session['dropbox_connector'])

    # Select the file
    if not page.select_file(file_path):
        return jsonify({'success': False, 'error': page.connection_errors.get('file_selection', 'Failed to select file')}), 400

    return jsonify({
        'success': True,
        'file': page.selected_file
    })

@main_bp.route('/api/dropbox/download', methods=['GET'])
@login_required
def download_dropbox_file():
    """Download a file from Dropbox."""
    file_path = request.args.get('path', '')

    if not file_path:
        return jsonify({'success': False, 'error': 'File path is required'}), 400

    # Create page instance
    page = DropboxBrowserPage()

    # Restore connector from session if available
    if 'dropbox_connector' in session:
        page.set_connector(session['dropbox_connector'])

    # Download the file
    result = page.download_file(file_path)

    if not result.get('success'):
        return jsonify({'success': False, 'error': result.get('error', 'Failed to download file')}), 400

    # Get file name from path
    file_name = file_path.split('/')[-1]

    # Create response with file content
    response = make_response(result['content'])
    response.headers['Content-Disposition'] = f'attachment; filename="{file_name}"'
    response.headers['Content-Type'] = 'application/octet-stream'

    return response

@main_bp.route('/api/dropbox/preview', methods=['GET'])
@login_required
def preview_dropbox_file():
    """Preview a file from Dropbox."""
    file_path = request.args.get('path', '')

    if not file_path:
        return jsonify({'success': False, 'error': 'File path is required'}), 400

    # Create page instance
    page = DropboxBrowserPage()

    # Restore connector from session if available
    if 'dropbox_connector' in session:
        page.set_connector(session['dropbox_connector'])

    # Download the file
    result = page.download_file(file_path)

    if not result.get('success'):
        return jsonify({'success': False, 'error': result.get('error', 'Failed to download file')}), 400

    # Get file extension
    file_ext = os.path.splitext(file_path)[1].lower()

    # Handle different file types
    text_file_extensions = [
        '.txt', '.md', '.csv', '.json', '.yaml', '.yml', 
        '.py', '.js', '.html', '.css', '.java', '.c', '.cpp', 
        '.cs', '.go', '.php', '.rb', '.rs', '.ts', '.sh', 
        '.xml', '.log', '.ini', '.conf', '.toml', '.sql'
    ]

    image_file_extensions = [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
        '.svg', '.webp', '.ico', '.tiff', '.tif'
    ]

    pdf_file_extensions = ['.pdf']

    if file_ext in text_file_extensions:
        # Text files
        try:
            content = result['content'].decode('utf-8')
            return render_template('partials/preview_text.html', content=content, file_path=file_path)
        except UnicodeDecodeError:
            return render_template('partials/preview_binary.html', file_path=file_path)
    elif file_ext in image_file_extensions:
        # Image files - return raw content with appropriate content type
        response = make_response(result['content'])
        response.headers['Content-Type'] = f'image/{file_ext[1:]}' if file_ext[1:] != 'jpg' else 'image/jpeg'
        return response
    elif file_ext in pdf_file_extensions:
        # PDF files
        response = make_response(result['content'])
        response.headers['Content-Type'] = 'application/pdf'
        return response
    else:
        # Binary files
        return render_template('partials/preview_binary.html', file_path=file_path)

@main_bp.route('/api/dropbox/search', methods=['GET'])
@login_required
def search_dropbox():
    """Search for files and folders in Dropbox."""
    query = request.args.get('query', '')
    path = request.args.get('path', '')
    extensions = request.args.get('extensions', '')

    if not query:
        return jsonify({'success': False, 'error': 'Search query is required'}), 400

    # Create page instance
    page = DropboxBrowserPage()

    # Restore connector from session if available
    if 'dropbox_connector' in session:
        page.set_connector(session['dropbox_connector'])

    # Parse extensions
    file_extensions = [ext.strip() for ext in extensions.split(',')] if extensions else None

    # Perform search
    if not page.search(query, path, file_extensions):
        return jsonify({'success': False, 'error': page.connection_errors.get('search', 'Failed to search')}), 400

    return jsonify({
        'success': True,
        'results': page.search_results
    })

@main_bp.route('/api/cbioportal/cancer-types', methods=['GET'])
@login_required
def get_cancer_types():
    """Get cancer types from cBioPortal API."""
    page = CbioportalBrowserPage()
    return jsonify(page._get_cancer_types())

@main_bp.route('/api/cbioportal/tumor-types', methods=['GET'])
@login_required
def get_tumor_types():
    """Get tumor types from OncoTree API."""
    page = CbioportalBrowserPage()
    return jsonify(page._get_oncotree_tumor_types())

@main_bp.route('/api/cbioportal/studies', methods=['GET'])
@login_required
def get_studies():
    """Get studies from cBioPortal API."""
    page = CbioportalBrowserPage()
    return jsonify(page._get_cbioportal_studies())

@main_bp.route('/api/cbioportal/study/<study_id>', methods=['GET'])
@login_required
def get_study_data(study_id):
    """Get study data from cBioPortal API."""
    page = CbioportalBrowserPage()
    return jsonify(page._load_cbioportal_study_data(study_id))

@main_bp.route('/api/cbioportal/add-cancer-types', methods=['POST'])
@login_required
def add_cancer_types():
    """Add cancer types to terms."""
    page = CbioportalBrowserPage()
    return jsonify(page.add_cancer_types_to_terms())

@main_bp.route('/api/cbioportal/add-tumor-types', methods=['POST'])
@login_required
def add_tumor_types():
    """Add tumor types to terms."""
    page = CbioportalBrowserPage()
    return jsonify(page.add_tumor_types_to_terms())

@main_bp.route('/api/cbioportal/add-study-data', methods=['POST'])
@login_required
def add_study_data():
    """Add study data to terms."""
    study_id = request.form.get('study_id')
    if not study_id:
        return jsonify({'success': False, 'message': 'Study ID is required'}), 400

    page = CbioportalBrowserPage()
    return jsonify(page.add_study_data_to_terms(study_id))

@main_bp.route('/api/cbioportal/add-term', methods=['POST'])
@login_required
def add_term():
    """Add a term manually."""
    term_name = request.form.get('term_name')
    term_uri = request.form.get('term_uri')
    ontology_source = request.form.get('ontology_source')

    if not term_name or not term_uri or not ontology_source:
        return jsonify({'success': False, 'message': 'Term name, URI, and ontology source are required'}), 400

    page = CbioportalBrowserPage()
    return jsonify(page.add_term_manually(term_name, term_uri, ontology_source))

@main_bp.route('/api/cbioportal/clear-terms', methods=['POST'])
@login_required
def clear_terms():
    """Clear all terms."""
    page = CbioportalBrowserPage()
    return jsonify(page.clear_terms())

@main_bp.route('/api/cbioportal/terms', methods=['GET'])
@login_required
def get_terms():
    """Get all terms."""
    page = CbioportalBrowserPage()
    return jsonify({
        'terms': page.terms,
        'existing_term_accessions': list(page.existing_term_accessions)
    })

@main_bp.route('/isa-browser')
@login_required
def isa_browser():
    """ISA browser page for browsing and managing ISA data and ontology terms."""
    page = IsaBrowserPage()
    return render_page_html(page, 'isa_browser.html')

@main_bp.route('/api/isa/connect', methods=['POST'])
@login_required
def connect_to_neo4j():
    """Connect to a Neo4j database."""
    uri = request.form.get('uri')
    username = request.form.get('username')
    password = request.form.get('password')
    database = request.form.get('database')
    conn_name = request.form.get('conn_name')

    if not uri or not username or not password or not database:
        return jsonify({'success': False, 'error': 'URI, username, password, and database are required'}), 400

    page = IsaBrowserPage()
    result = page.connect_to_database(uri, username, password, database, conn_name)

    if result.get('success'):
        # Store connection in session
        session['neo4j_connection'] = page.neo4j_connection
        session['neo4j_connected'] = True
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result.get('error', 'Failed to connect to Neo4j')}), 400

@main_bp.route('/api/isa/disconnect', methods=['POST'])
@login_required
def disconnect_from_neo4j():
    """Disconnect from a Neo4j database."""
    page = IsaBrowserPage()

    # Restore connection from session if available
    if 'neo4j_connection' in session:
        page.neo4j_connection = session['neo4j_connection']

    result = page.disconnect_from_database()

    # Remove connection from session
    if 'neo4j_connection' in session:
        del session['neo4j_connection']
    session['neo4j_connected'] = False

    if result.get('success'):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result.get('error', 'Failed to disconnect from Neo4j')}), 400

@main_bp.route('/api/isa/standard-terms', methods=['GET'])
@login_required
def get_standard_isa_terms():
    """Get standard ISA terms."""
    page = IsaBrowserPage()
    terms = page._get_standard_isa_terms()

    # Convert terms to dictionaries for JSON serialization
    terms_data = []
    for term in terms:
        source_name = term.term_source.name if hasattr(term.term_source, 'name') else str(term.term_source)
        terms_data.append({
            "term": term.term,
            "term_accession": term.term_accession,
            "term_source": source_name
        })

    return jsonify(terms_data)

@main_bp.route('/api/isa/cancer-types', methods=['GET'])
@login_required
def get_isa_cancer_types():
    """Get cancer types from cBioPortal API."""
    page = IsaBrowserPage()
    return jsonify(page._get_cancer_types())

@main_bp.route('/api/isa/tumor-types', methods=['GET'])
@login_required
def get_isa_tumor_types():
    """Get tumor types from OncoTree API."""
    page = IsaBrowserPage()
    return jsonify(page._get_oncotree_tumor_types())

@main_bp.route('/api/isa/studies', methods=['GET'])
@login_required
def get_isa_studies():
    """Get studies from cBioPortal API."""
    page = IsaBrowserPage()
    return jsonify(page._get_cbioportal_studies())

@main_bp.route('/api/isa/study/<study_id>', methods=['GET'])
@login_required
def get_isa_study_data(study_id):
    """Get study data from cBioPortal API."""
    page = IsaBrowserPage()
    return jsonify(page._load_cbioportal_study_data(study_id))

@main_bp.route('/api/isa/add-cancer-types', methods=['POST'])
@login_required
def add_isa_cancer_types():
    """Add cancer types to terms."""
    page = IsaBrowserPage()
    return jsonify(page.add_cancer_types_to_terms())

@main_bp.route('/api/isa/add-tumor-types', methods=['POST'])
@login_required
def add_isa_tumor_types():
    """Add tumor types to terms."""
    page = IsaBrowserPage()
    return jsonify(page.add_tumor_types_to_terms())

@main_bp.route('/api/isa/add-study-data', methods=['POST'])
@login_required
def add_isa_study_data():
    """Add study data to terms."""
    study_id = request.form.get('study_id')
    if not study_id:
        return jsonify({'success': False, 'message': 'Study ID is required'}), 400

    page = IsaBrowserPage()
    return jsonify(page.add_study_data_to_terms(study_id))

@main_bp.route('/api/isa/add-term', methods=['POST'])
@login_required
def add_isa_term():
    """Add a term manually."""
    term_name = request.form.get('term_name')
    term_uri = request.form.get('term_uri')
    ontology_source = request.form.get('ontology_source')

    if not term_name or not term_uri or not ontology_source:
        return jsonify({'success': False, 'message': 'Term name, URI, and ontology source are required'}), 400

    page = IsaBrowserPage()
    return jsonify(page.add_term_manually(term_name, term_uri, ontology_source))

@main_bp.route('/api/isa/clear-terms', methods=['POST'])
@login_required
def clear_isa_terms():
    """Clear all terms."""
    page = IsaBrowserPage()
    return jsonify(page.clear_terms())

@main_bp.route('/api/isa/terms', methods=['GET'])
@login_required
def get_isa_terms():
    """Get all terms."""
    page = IsaBrowserPage()

    # Convert terms to dictionaries for JSON serialization
    terms_data = []
    for term in page.terms:
        source_name = term.term_source.name if hasattr(term.term_source, 'name') else str(term.term_source)
        terms_data.append({
            "term": term.term,
            "term_accession": term.term_accession,
            "term_source": source_name
        })

    return jsonify({
        'terms': terms_data,
        'existing_term_accessions': list(page.existing_term_accessions)
    })

@main_bp.route('/api/isa/process-file', methods=['POST'])
@login_required
def process_isa_file():
    """Process an ISA file."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400

    page = IsaBrowserPage()
    return jsonify(page.process_isa_file(file))

@main_bp.route('/api/isa/load-to-neo4j', methods=['POST'])
@login_required
def load_isa_terms_to_neo4j():
    """Load ontology terms to Neo4j."""
    create_source_nodes = request.form.get('create_source_nodes', 'true').lower() == 'true'
    relationship_type = request.form.get('relationship_type', 'HAS_TERM')

    page = IsaBrowserPage()

    # Restore connection from session if available
    if 'neo4j_connection' in session:
        page.neo4j_connection = session['neo4j_connection']

    return jsonify(page.load_ontology_terms_to_neo4j(create_source_nodes, relationship_type))
