"""
Main Routes for the Flask Application

This module defines the main routes for the Flask application.
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify, make_response
import json
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
from science_data_kit.core.pages.map import MapPage
from science_data_kit.core.pages.msgraph_connect import MSGraphConnectPage
from science_data_kit.core.pages.msgraph_explore import MSGraphExplorePage
from science_data_kit.core.pages.ontology import OntologyPage
from science_data_kit.core.pages.preferences import PreferencesPage
from science_data_kit.core.pages.analytics_dashboard import AnalyticsDashboardPage
from science_data_kit.core.pages.chat import ChatPage
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

@main_bp.route('/ontology')
@login_required
def ontology():
    """Ontology browser page for browsing and managing ontology terms."""
    page = OntologyPage()
    return render_page_html(page, 'ontology.html')

@main_bp.route('/api/ontology/connect', methods=['POST'])
@login_required
def connect_to_ontology_neo4j():
    """Connect to a Neo4j database for ontology browsing."""
    uri = request.form.get('uri')
    username = request.form.get('username')
    password = request.form.get('password')
    database = request.form.get('database')
    conn_name = request.form.get('conn_name')

    if not uri or not username or not password or not database:
        return jsonify({'success': False, 'error': 'URI, username, password, and database are required'}), 400

    page = OntologyPage()
    result = page.connect_to_database(uri, username, password, database, conn_name)

    if result.get('success'):
        # Store connection in session
        session['ontology_neo4j_connection'] = page.neo4j_connection
        session['ontology_neo4j_connected'] = True
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result.get('error', 'Failed to connect to Neo4j')}), 400

@main_bp.route('/api/ontology/disconnect', methods=['POST'])
@login_required
def disconnect_from_ontology_neo4j():
    """Disconnect from a Neo4j database for ontology browsing."""
    page = OntologyPage()

    # Restore connection from session if available
    if 'ontology_neo4j_connection' in session:
        page.neo4j_connection = session['ontology_neo4j_connection']

    result = page.disconnect_from_database()

    # Remove connection from session
    if 'ontology_neo4j_connection' in session:
        del session['ontology_neo4j_connection']
    session['ontology_neo4j_connected'] = False

    if result.get('success'):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result.get('error', 'Failed to disconnect from Neo4j')}), 400

@main_bp.route('/api/ontology/labels', methods=['GET'])
@login_required
def get_ontology_labels():
    """Get available labels from Neo4j for ontology browsing."""
    page = OntologyPage()

    # Restore connection from session if available
    if 'ontology_neo4j_connection' in session:
        page.neo4j_connection = session['ontology_neo4j_connection']
        page.neo4j_connected = session.get('ontology_neo4j_connected', False)

    if not page.neo4j_connected:
        return jsonify({'success': False, 'error': 'Not connected to Neo4j'}), 400

    return jsonify({'success': True, 'labels': page.available_labels})

@main_bp.route('/api/ontology/standard-terms', methods=['GET'])
@login_required
def add_standard_ontology_terms():
    """Add standard ISA terms to the ontology browser."""
    page = OntologyPage()
    return jsonify(page.add_standard_isa_terms())

@main_bp.route('/api/ontology/terms', methods=['GET'])
@login_required
def get_ontology_terms():
    """Get all terms from the ontology browser."""
    page = OntologyPage()
    return jsonify(page.get_terms())

@main_bp.route('/api/ontology/add-term', methods=['POST'])
@login_required
def add_ontology_term():
    """Add a new term to the ontology browser."""
    term_name = request.form.get('term_name')
    term_uri = request.form.get('term_uri')
    ontology_source = request.form.get('ontology_source')

    if not term_name or not term_uri or not ontology_source:
        return jsonify({'success': False, 'error': 'Term name, URI, and source are required'}), 400

    page = OntologyPage()
    return jsonify(page.add_term(term_name, term_uri, ontology_source))

@main_bp.route('/api/ontology/push-terms', methods=['POST'])
@login_required
def push_ontology_terms():
    """Push terms to Neo4j from the ontology browser."""
    page = OntologyPage()

    # Restore connection from session if available
    if 'ontology_neo4j_connection' in session:
        page.neo4j_connection = session['ontology_neo4j_connection']
        page.neo4j_connected = session.get('ontology_neo4j_connected', False)

    return jsonify(page.push_terms_to_neo4j())

@main_bp.route('/api/ontology/clear-terms', methods=['POST'])
@login_required
def clear_ontology_terms():
    """Clear all terms from the ontology browser."""
    page = OntologyPage()
    return jsonify(page.clear_terms())

@main_bp.route('/api/ontology/search-terms', methods=['GET'])
@login_required
def search_ontology_terms():
    """Search for ontology terms in the database."""
    search_term = request.args.get('term')

    if not search_term:
        return jsonify({'success': False, 'error': 'Search term is required'}), 400

    page = OntologyPage()

    # Restore connection from session if available
    if 'ontology_neo4j_connection' in session:
        page.neo4j_connection = session['ontology_neo4j_connection']
        page.neo4j_connected = session.get('ontology_neo4j_connected', False)

    return jsonify(page.search_terms(search_term))

@main_bp.route('/api/ontology/term-hierarchy', methods=['GET'])
@login_required
def get_ontology_term_hierarchy():
    """Get the hierarchy for a specific ontology term."""
    term = request.args.get('term')

    if not term:
        return jsonify({'success': False, 'error': 'Term is required'}), 400

    page = OntologyPage()

    # Restore connection from session if available
    if 'ontology_neo4j_connection' in session:
        page.neo4j_connection = session['ontology_neo4j_connection']
        page.neo4j_connected = session.get('ontology_neo4j_connected', False)

    return jsonify(page.get_term_hierarchy(term))

@main_bp.route('/preferences')
@login_required
def preferences():
    """User preferences page for customizing application settings."""
    page = PreferencesPage()
    return render_page_html(page, 'preferences.html')

@main_bp.route('/api/preferences/get', methods=['GET'])
@login_required
def get_preferences():
    """Get the current user preferences."""
    page = PreferencesPage()

    # Load preferences from file
    result = page.load_preferences()

    # If loading failed, return default preferences
    if not result.get('success'):
        return jsonify(page.get_preferences())

    return jsonify(result)

@main_bp.route('/api/preferences/save', methods=['POST'])
@login_required
def save_preferences():
    """Save the current user preferences to a file."""
    page = PreferencesPage()

    # Get current preferences
    preferences = page.user_preferences

    # Save preferences to file
    result = page.save_preferences(preferences)

    return jsonify(result)

@main_bp.route('/api/preferences/update', methods=['POST'])
@login_required
def update_preference():
    """Update a specific preference."""
    key = request.form.get('key')
    value = request.form.get('value')

    if not key:
        return jsonify({'success': False, 'error': 'Preference key is required'}), 400

    # Handle JSON values (like custom_colors)
    if value and (value.startswith('{') or value.startswith('[')):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass

    # Handle boolean values
    if value == 'true':
        value = True
    elif value == 'false':
        value = False

    # Handle numeric values
    if value and value.isdigit():
        value = int(value)

    page = PreferencesPage()

    # Load preferences from file
    page.load_preferences()

    # Update preference
    result = page.update_preference(key, value)

    return jsonify(result)

@main_bp.route('/api/preferences/reset', methods=['POST'])
@login_required
def reset_preferences():
    """Reset preferences to defaults."""
    page = PreferencesPage()

    # Reset preferences
    result = page.reset_preferences()

    return jsonify(result)

@main_bp.route('/api/preferences/language-names', methods=['GET'])
@login_required
def get_language_names():
    """Get the names of available languages."""
    page = PreferencesPage()

    # Get language names
    result = page.get_language_names()

    return jsonify(result)

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

@main_bp.route('/analytics')
@login_required
def analytics_dashboard():
    """Analytics dashboard page for viewing usage statistics."""
    page = AnalyticsDashboardPage()
    return render_page_html(page, 'analytics_dashboard.html')

@main_bp.route('/api/analytics/data', methods=['GET'])
@login_required
def get_analytics_data():
    """Get analytics data including page views and interactions."""
    page = AnalyticsDashboardPage()

    # Store session ID and start time in session if not already there
    if 'analytics_session_id' not in session:
        session['analytics_session_id'] = page.session_id
    if 'analytics_session_start' not in session:
        session['analytics_session_start'] = page.session_start

    # Use session values if available
    page.session_id = session.get('analytics_session_id', page.session_id)
    page.session_start = session.get('analytics_session_start', page.session_start)

    # Get page data
    page_data = page.get_page_data()

    return jsonify({
        'success': True,
        'page_views': page_data.page_views,
        'page_views_summary': page_data.page_views_summary,
        'interactions': page_data.interactions,
        'interactions_summary': page_data.interactions_summary,
        'session_id': page_data.session_id,
        'session_start': page_data.session_start,
        'session_duration': page_data.session_duration,
        'analytics_enabled': page_data.analytics_enabled,
        'analytics_storage_path': page_data.analytics_storage_path
    })

@main_bp.route('/api/analytics/toggle', methods=['POST'])
@login_required
def toggle_analytics():
    """Enable or disable analytics tracking."""
    data = request.json
    enabled = data.get('enabled', True)

    page = AnalyticsDashboardPage()

    # Use session values if available
    page.session_id = session.get('analytics_session_id', page.session_id)
    page.session_start = session.get('analytics_session_start', page.session_start)

    # Toggle analytics
    result = page.toggle_analytics(enabled)

    # Store analytics enabled state in session
    session['analytics_enabled'] = enabled

    return jsonify(result)

@main_bp.route('/api/analytics/storage-path', methods=['POST'])
@login_required
def update_analytics_storage_path():
    """Update the analytics storage path."""
    data = request.json
    path = data.get('path')

    if not path:
        return jsonify({'success': False, 'error': 'Storage path is required'}), 400

    page = AnalyticsDashboardPage()

    # Use session values if available
    page.session_id = session.get('analytics_session_id', page.session_id)
    page.session_start = session.get('analytics_session_start', page.session_start)

    # Update storage path
    result = page.update_storage_path(path)

    # Store storage path in session
    if result.get('success'):
        session['analytics_storage_path'] = path

    return jsonify(result)

@main_bp.route('/api/analytics/export', methods=['POST'])
@login_required
def export_analytics_data():
    """Export analytics data to CSV or JSON."""
    data = request.json
    format = data.get('format', 'csv')

    page = AnalyticsDashboardPage()

    # Use session values if available
    page.session_id = session.get('analytics_session_id', page.session_id)
    page.session_start = session.get('analytics_session_start', page.session_start)

    # Export data
    result = page.export_analytics_data(format)

    return jsonify(result)

@main_bp.route('/api/analytics/clear', methods=['POST'])
@login_required
def clear_analytics_data():
    """Clear all analytics data."""
    page = AnalyticsDashboardPage()

    # Use session values if available
    page.session_id = session.get('analytics_session_id', page.session_id)
    page.session_start = session.get('analytics_session_start', page.session_start)

    # Clear data
    result = page.clear_analytics_data()

    return jsonify(result)

@main_bp.route('/api/analytics/track-page-view', methods=['POST'])
@login_required
def track_page_view():
    """Track a page view."""
    data = request.json
    page_name = data.get('page_name')
    page_path = data.get('page_path')

    if not page_name:
        return jsonify({'success': False, 'error': 'Page name is required'}), 400

    page = AnalyticsDashboardPage()

    # Use session values if available
    page.session_id = session.get('analytics_session_id', page.session_id)
    page.session_start = session.get('analytics_session_start', page.session_start)
    page.analytics_enabled = session.get('analytics_enabled', page.analytics_enabled)

    # Track page view
    result = page.track_page_view(page_name, page_path)

    return jsonify(result)

@main_bp.route('/api/analytics/track-interaction', methods=['POST'])
@login_required
def track_interaction():
    """Track a user interaction."""
    data = request.json
    interaction_type = data.get('interaction_type')
    component_id = data.get('component_id')
    component_type = data.get('component_type')
    page_name = data.get('page_name')
    details = data.get('details')

    if not interaction_type or not component_id or not component_type or not page_name:
        return jsonify({'success': False, 'error': 'Interaction type, component ID, component type, and page name are required'}), 400

    page = AnalyticsDashboardPage()

    # Use session values if available
    page.session_id = session.get('analytics_session_id', page.session_id)
    page.session_start = session.get('analytics_session_start', page.session_start)
    page.analytics_enabled = session.get('analytics_enabled', page.analytics_enabled)

    # Track interaction
    result = page.track_interaction(interaction_type, component_id, component_type, page_name, details)

    return jsonify(result)

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

# Map Visualization Routes

@main_bp.route('/map')
@login_required
def map():
    """Render the Map visualization page."""
    page = MapPage()
    return render_page_html(page, 'map.html')

@main_bp.route('/api/map/connect-to-database', methods=['POST'])
@login_required
def connect_to_map_database():
    """Connect to a Neo4j database for map visualization."""
    try:
        page = MapPage()

        # Get form data
        uri = request.json.get('uri')
        username = request.json.get('username')
        password = request.json.get('password')
        database = request.json.get('database')
        conn_name = request.json.get('conn_name')

        # Connect to the database
        result = page.connect_to_database(uri, username, password, database, conn_name)

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/map/disconnect-from-database', methods=['POST'])
@login_required
def disconnect_from_map_database():
    """Disconnect from the Neo4j database for map visualization."""
    try:
        page = MapPage()

        # Disconnect from the database
        result = page.disconnect_from_database()

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/map/load-entities-from-file', methods=['POST'])
@login_required
def load_entities_from_file():
    """Load entities from a file for map visualization."""
    try:
        page = MapPage()

        # Get the uploaded file
        file = request.files.get('file')
        if not file:
            return jsonify({"success": False, "message": "No file provided"})

        # Get form data
        file_type = request.form.get('file_type')
        sheet_name = request.form.get('sheet_name')

        # Load entities from the file
        result = page.load_entities_from_file(file.read(), file.filename, file_type, sheet_name)

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/map/load-entities-from-database', methods=['POST'])
@login_required
def load_entities_from_database():
    """Load entities from the Neo4j database for map visualization."""
    try:
        page = MapPage()

        # Get form data
        label = request.json.get('label')

        # Load entities from the database
        result = page.load_entities_from_database(label)

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/map/create-entity-structure', methods=['POST'])
@login_required
def create_entity_structure():
    """Create a structure for entities in map visualization."""
    try:
        page = MapPage()

        # Get form data
        entity_data = request.json.get('entity_data')

        # Create entity structure
        result = page.create_entity_structure(entity_data)

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/map/push-entities-to-neo4j', methods=['POST'])
@login_required
def push_entities_to_neo4j():
    """Push entities to the Neo4j database for map visualization."""
    try:
        page = MapPage()

        # Get form data
        entity_data = request.json.get('entity_data')
        label = request.json.get('label')
        structure = request.json.get('structure')

        # Push entities to Neo4j
        result = page.push_entities_to_neo4j(entity_data, label, structure)

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/map/create-relationships', methods=['POST'])
@login_required
def create_map_relationships():
    """Create relationships between entities in the Neo4j database for map visualization."""
    try:
        page = MapPage()

        # Get form data
        source_label = request.json.get('source_label')
        target_label = request.json.get('target_label')
        relationship_type = request.json.get('relationship_type')
        source_property = request.json.get('source_property')
        target_property = request.json.get('target_property')

        # Create relationships
        result = page.create_relationships(source_label, target_label, relationship_type, source_property, target_property)

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/map/load-ontology', methods=['POST'])
@login_required
def load_map_ontology():
    """Load ontology data for map visualization."""
    try:
        page = MapPage()

        # Get the uploaded file
        file = request.files.get('file')
        if not file:
            return jsonify({"success": False, "message": "No file provided"})

        # Load ontology data
        result = page.load_ontology(file.read())

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/map/push-ontology-to-neo4j', methods=['POST'])
@login_required
def push_map_ontology_to_neo4j():
    """Push ontology data to the Neo4j database for map visualization."""
    try:
        page = MapPage()

        # Get form data
        ontology_data = request.json.get('ontology_data')

        # Push ontology data to Neo4j
        result = page.push_ontology_to_neo4j(ontology_data)

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/map/create-taxonomy', methods=['POST'])
@login_required
def create_map_taxonomy():
    """Create a taxonomy from entity data for map visualization."""
    try:
        page = MapPage()

        # Get form data
        entity_data = request.json.get('entity_data')
        taxonomy_keys = request.json.get('taxonomy_keys')

        # Create taxonomy
        result = page.create_taxonomy(entity_data, taxonomy_keys)

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/map/filter-entity-data', methods=['POST'])
@login_required
def filter_map_entity_data():
    """Filter entity data for map visualization."""
    try:
        page = MapPage()

        # Get form data
        entity_data = request.json.get('entity_data')
        filter_column = request.json.get('filter_column')
        filter_operation = request.json.get('filter_operation')
        filter_value = request.json.get('filter_value')

        # Filter entity data
        result = page.filter_entity_data(entity_data, filter_column, filter_operation, filter_value)

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

# Microsoft Graph Connection Routes

@main_bp.route('/msgraph-connect')
@login_required
def msgraph_connect():
    """Render the Microsoft Graph connection page."""
    page = MSGraphConnectPage()
    return render_page_html(page, 'msgraph_connect.html')

@main_bp.route('/api/msgraph/connect', methods=['POST'])
@login_required
def connect_to_msgraph():
    """Connect to Microsoft Graph API."""
    try:
        page = MSGraphConnectPage()

        # Get form data
        tenant_id = request.json.get('tenant_id')
        client_id = request.json.get('client_id')
        client_secret = request.json.get('client_secret')
        auth_method = request.json.get('auth_method', 'device_code')
        config_file = request.json.get('config_file')

        # Connect to Microsoft Graph API
        result = page.connect(tenant_id, client_id, client_secret, auth_method, config_file)

        # Store connection manager in session if connection was successful
        if result.get('success', False):
            session['msgraph_connection_manager'] = page.connection_manager
            session['msgraph_adapter'] = page.adapter

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/msgraph/disconnect', methods=['POST'])
@login_required
def disconnect_from_msgraph():
    """Disconnect from Microsoft Graph API."""
    try:
        page = MSGraphConnectPage()

        # Disconnect from Microsoft Graph API
        result = page.disconnect()

        # Remove connection manager from session
        if 'msgraph_connection_manager' in session:
            del session['msgraph_connection_manager']
        if 'msgraph_adapter' in session:
            del session['msgraph_adapter']

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/msgraph/status', methods=['GET'])
@login_required
def get_msgraph_status():
    """Get Microsoft Graph connection status."""
    try:
        page = MSGraphConnectPage()

        # Restore connection manager from session if available
        if 'msgraph_connection_manager' in session:
            page.connection_manager = session['msgraph_connection_manager']
        if 'msgraph_adapter' in session:
            page.adapter = session['msgraph_adapter']

        # Get connection status
        result = page.get_connection_status()

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/msgraph/load-config', methods=['POST'])
@login_required
def load_msgraph_config():
    """Load Microsoft Graph configuration from a file."""
    try:
        page = MSGraphConnectPage()

        # Get form data
        config_file = request.json.get('config_file')

        # Load configuration from file
        result = page.load_config_from_file(config_file)

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/api/msgraph/save-config', methods=['POST'])
@login_required
def save_msgraph_config():
    """Save Microsoft Graph configuration to a file."""
    try:
        page = MSGraphConnectPage()

        # Get form data
        config_file = request.json.get('config_file')

        # Restore connection manager from session if available
        if 'msgraph_connection_manager' in session:
            page.connection_manager = session['msgraph_connection_manager']
        if 'msgraph_adapter' in session:
            page.adapter = session['msgraph_adapter']

        # Save configuration to file
        result = page.save_config_to_file(config_file)

        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@main_bp.route('/msgraph_explore')
@login_required
def msgraph_explore():
    """
    Render the Microsoft Graph API explorer page.
    """
    return render_page_html(MSGraphExplorePage())

@main_bp.route('/api/msgraph/execute-query', methods=['POST'])
@login_required
def execute_msgraph_query():
    """
    Execute a query against Microsoft Graph API.
    """
    try:
        # Get data from request
        data = request.get_json()
        resource_path = data.get('resource_path')
        query_parameters = data.get('query_parameters', {})

        # Get page from session
        if 'msgraph_explore_page' in session:
            page = session['msgraph_explore_page']
        else:
            page = MSGraphExplorePage()
            session['msgraph_explore_page'] = page

        # Get connection manager from session
        if 'msgraph_connection_manager' in session:
            connection_manager = session['msgraph_connection_manager']
            # Check connection
            if page.check_connection(connection_manager):
                # Execute query
                result = page.execute_query(resource_path, query_parameters)
                return jsonify(result)

        return jsonify({
            "success": False,
            "message": "Not connected to Microsoft Graph API"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error executing query: {str(e)}"
        })

@main_bp.route('/api/msgraph/export-data', methods=['POST'])
@login_required
def export_msgraph_data():
    """
    Export Microsoft Graph API data to a file.
    """
    try:
        # Get data from request
        data = request.get_json()
        format = data.get('format', 'csv')

        # Get page from session
        if 'msgraph_explore_page' in session:
            page = session['msgraph_explore_page']
        else:
            return jsonify({
                "success": False,
                "message": "No data to export"
            })

        # Export data
        result = page.export_data(format)

        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error exporting data: {str(e)}"
        })

@main_bp.route('/api/msgraph/sample-queries', methods=['GET'])
@login_required
def get_msgraph_sample_queries():
    """
    Get sample queries for Microsoft Graph API.
    """
    try:
        # Get page from session
        if 'msgraph_explore_page' in session:
            page = session['msgraph_explore_page']
        else:
            page = MSGraphExplorePage()
            session['msgraph_explore_page'] = page

        # Get sample queries
        sample_queries = page.get_page_data().sample_queries

        return jsonify({
            "success": True,
            "sample_queries": sample_queries
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error getting sample queries: {str(e)}"
        })

@main_bp.route('/chat')
@login_required
def chat():
    """Chat page for interacting with data using retrieval-augmented generation."""
    page = ChatPage()
    return render_page_html(page, 'chat.html')

@main_bp.route('/api/chat/connect-neo4j', methods=['POST'])
@login_required
def chat_connect_to_neo4j():
    """Connect to Neo4j database for chat functionality."""
    try:
        data = request.json
        uri = data.get('uri')
        user = data.get('user')
        password = data.get('password')
        database = data.get('database')

        if not uri or not user or not password or not database:
            return jsonify({'success': False, 'error': 'All connection parameters are required'}), 400

        page = ChatPage()

        # Store page in session if needed for future requests
        if 'chat_page' not in session:
            session['chat_page'] = page

        result = page.connect_to_neo4j(uri, user, password, database)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error connecting to Neo4j: {str(e)}'}), 500

@main_bp.route('/api/chat/initialize-graph-rag', methods=['POST'])
@login_required
def initialize_graph_rag():
    """Initialize GraphRAG with current settings."""
    try:
        # Get page from session if available, otherwise create new
        if 'chat_page' in session:
            page = session['chat_page']
        else:
            page = ChatPage()
            session['chat_page'] = page

        result = page.initialize_graph_rag()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error initializing GraphRAG: {str(e)}'}), 500

@main_bp.route('/api/chat/settings', methods=['POST'])
@login_required
def update_chat_settings():
    """Update LLM settings."""
    try:
        data = request.json
        provider = data.get('provider')
        api_key = data.get('api_key')
        model = data.get('model')
        temperature = data.get('temperature')
        max_tokens = data.get('max_tokens')

        # Get page from session if available, otherwise create new
        if 'chat_page' in session:
            page = session['chat_page']
        else:
            page = ChatPage()
            session['chat_page'] = page

        # Update LLM settings
        result = page.update_llm_settings(provider, api_key, model, temperature, max_tokens)

        # If Ollama settings are provided, update them too
        if provider == 'Ollama':
            ollama_base_url = data.get('ollama_base_url')
            ollama_auth_enabled = data.get('ollama_auth_enabled')
            ollama_username = data.get('ollama_username')
            ollama_password = data.get('ollama_password')

            if ollama_base_url:
                page.update_ollama_settings(ollama_base_url, ollama_auth_enabled, ollama_username, ollama_password)

        # Store updated page in session
        session['chat_page'] = page

        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error updating settings: {str(e)}'}), 500

@main_bp.route('/api/chat/refresh-ollama-models', methods=['POST'])
@login_required
def refresh_ollama_models():
    """Refresh the list of available Ollama models."""
    try:
        data = request.json
        base_url = data.get('base_url')

        # Get page from session if available, otherwise create new
        if 'chat_page' in session:
            page = session['chat_page']
        else:
            page = ChatPage()
            session['chat_page'] = page

        # Update Ollama base URL if provided
        if base_url:
            page.ollama_base_url = base_url

        # Refresh models
        result = page.refresh_ollama_models()

        # Store updated page in session
        session['chat_page'] = page

        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error refreshing Ollama models: {str(e)}'}), 500

@main_bp.route('/api/chat/send-message', methods=['POST'])
@login_required
def send_chat_message():
    """Send a message to the chat and get a response."""
    try:
        data = request.json
        message = data.get('message')

        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        # Get page from session if available, otherwise create new
        if 'chat_page' in session:
            page = session['chat_page']
        else:
            page = ChatPage()
            session['chat_page'] = page

        # Send message
        result = page.send_message(message)

        # Store updated page in session
        session['chat_page'] = page

        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error sending message: {str(e)}'}), 500

@main_bp.route('/api/chat/clear-history', methods=['POST'])
@login_required
def clear_chat_history():
    """Clear the chat history."""
    try:
        # Get page from session if available, otherwise create new
        if 'chat_page' in session:
            page = session['chat_page']
        else:
            page = ChatPage()
            session['chat_page'] = page

        # Clear chat history
        result = page.clear_chat_history()

        # Store updated page in session
        session['chat_page'] = page

        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error clearing chat history: {str(e)}'}), 500
