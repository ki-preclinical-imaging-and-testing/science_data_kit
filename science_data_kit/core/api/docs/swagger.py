"""
Swagger UI for Science Data Kit API

This module provides utilities for serving the OpenAPI documentation using Swagger UI.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional

# Try to import Flask, which is commonly used for web applications
try:
    from flask import Flask, Blueprint, send_from_directory, render_template_string
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Try to import Streamlit, which is used in the Science Data Kit UI
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


def load_openapi_spec(spec_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load the OpenAPI specification from a YAML file.
    
    Args:
        spec_path: Path to the OpenAPI specification file. If None, the default
                  specification file in the same directory as this module is used.
                  
    Returns:
        The OpenAPI specification as a dictionary.
    """
    if spec_path is None:
        # Use the default specification file in the same directory as this module
        spec_path = os.path.join(os.path.dirname(__file__), 'openapi.yaml')
    
    with open(spec_path, 'r') as f:
        if spec_path.endswith('.yaml') or spec_path.endswith('.yml'):
            return yaml.safe_load(f)
        elif spec_path.endswith('.json'):
            return json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {spec_path}")


def create_flask_blueprint(spec_path: Optional[str] = None) -> Blueprint:
    """
    Create a Flask blueprint for serving the OpenAPI documentation using Swagger UI.
    
    Args:
        spec_path: Path to the OpenAPI specification file. If None, the default
                  specification file in the same directory as this module is used.
                  
    Returns:
        A Flask blueprint that can be registered with a Flask application.
        
    Raises:
        ImportError: If Flask is not installed.
    """
    if not FLASK_AVAILABLE:
        raise ImportError("Flask is required for this function. Install it with 'pip install flask'.")
    
    # Load the OpenAPI specification
    spec = load_openapi_spec(spec_path)
    
    # Create a blueprint
    blueprint = Blueprint('swagger_ui', __name__)
    
    # Define the Swagger UI HTML template
    SWAGGER_UI_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Science Data Kit API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui.css" />
        <style>
            html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
            *, *:before, *:after { box-sizing: inherit; }
            body { margin: 0; background: #fafafa; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    spec: {{ spec|tojson }},
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout",
                    docExpansion: "list",
                    defaultModelsExpandDepth: 1,
                    defaultModelExpandDepth: 1,
                    defaultModelRendering: "example",
                    displayRequestDuration: true,
                    showExtensions: true,
                    showCommonExtensions: true
                });
                window.ui = ui;
            };
        </script>
    </body>
    </html>
    """
    
    # Define the route for the Swagger UI
    @blueprint.route('/')
    def swagger_ui():
        return render_template_string(SWAGGER_UI_TEMPLATE, spec=spec)
    
    return blueprint


def create_streamlit_swagger_ui(spec_path: Optional[str] = None) -> None:
    """
    Create a Streamlit page for displaying the OpenAPI documentation using Swagger UI.
    
    Args:
        spec_path: Path to the OpenAPI specification file. If None, the default
                  specification file in the same directory as this module is used.
                  
    Raises:
        ImportError: If Streamlit is not installed.
    """
    if not STREAMLIT_AVAILABLE:
        raise ImportError("Streamlit is required for this function. Install it with 'pip install streamlit'.")
    
    # Load the OpenAPI specification
    spec = load_openapi_spec(spec_path)
    
    # Define the Swagger UI HTML
    swagger_ui_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Science Data Kit API Documentation</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui.css" />
        <style>
            html {{ box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }}
            *, *:before, *:after {{ box-sizing: inherit; }}
            body {{ margin: 0; background: #fafafa; }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4.5.0/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {{
                const ui = SwaggerUIBundle({{
                    spec: {json.dumps(spec)},
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout",
                    docExpansion: "list",
                    defaultModelsExpandDepth: 1,
                    defaultModelExpandDepth: 1,
                    defaultModelRendering: "example",
                    displayRequestDuration: true,
                    showExtensions: true,
                    showCommonExtensions: true
                }});
                window.ui = ui;
            }};
        </script>
    </body>
    </html>
    """
    
    # Display the Swagger UI in Streamlit
    st.title("Science Data Kit API Documentation")
    st.components.v1.html(swagger_ui_html, height=800)


if __name__ == "__main__":
    # If this module is run directly, start a Flask server to serve the documentation
    if FLASK_AVAILABLE:
        app = Flask(__name__)
        app.register_blueprint(create_flask_blueprint())
        app.run(debug=True, port=8000)
    else:
        print("Flask is not installed. Install it with 'pip install flask' to run this module directly.")