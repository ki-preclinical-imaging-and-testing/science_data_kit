"""
Flask Application Factory for Science Data Kit

This module provides a factory function for creating a Flask application instance.
It sets up the application with the necessary configuration, blueprints, and extensions.
"""

import atexit
from flask import Flask, render_template
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO

from science_data_kit.web.api import register_api_routes
from science_data_kit.web.config import Config

# Initialize SocketIO without an app (will be initialized in create_app)
socketio = SocketIO()

def create_app(config_class=Config):
    """
    Create and configure a Flask application instance.

    Args:
        config_class: Configuration class to use for the application.
                     Defaults to the Config class from science_data_kit.web.config.

    Returns:
        A configured Flask application instance.
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')

    # Load configuration
    app.config.from_object(config_class)

    # Initialize extensions
    Session(app)
    csrf = CSRFProtect(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Register blueprints
    from science_data_kit.web.routes import main_bp
    app.register_blueprint(main_bp)

    # Register API routes
    register_api_routes(app)

    # Import WebSocket events (this registers the event handlers)
    import science_data_kit.web.events

    # Start dashboard updates when the app starts
    from science_data_kit.web.events import start_dashboard_updates, stop_dashboard_updates
    start_dashboard_updates()

    # Register function to stop dashboard updates when the app stops
    atexit.register(stop_dashboard_updates)

    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app
