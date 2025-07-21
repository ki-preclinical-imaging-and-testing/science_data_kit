"""
FHIR Viewer Integration Component for Science Data Kit

This module provides UI components for integrating with FHIR-compatible viewers like OHIF Viewer
for viewing DICOM medical imaging files.
"""

import os
import webbrowser
from typing import Dict, Any, Optional, List
import logging

from flask import render_template, url_for, request, jsonify, current_app

from science_data_kit.core.integrations.plugin_architecture import (
    get_file_interpreter_for_file,
    FileInterpreterPlugin
)

# Set up logging
logger = logging.getLogger(__name__)

def get_fhir_viewer_url(file_path: str) -> Optional[str]:
    """
    Get the FHIR viewer URL for a DICOM file.

    Args:
        file_path: Path to the DICOM file.

    Returns:
        URL to view the file in a FHIR-compatible viewer, or None if not available.
    """
    try:
        # Get file interpreter for the file
        interpreter = get_file_interpreter_for_file(file_path)

        if not interpreter:
            logger.warning(f"No interpreter found for file: {file_path}")
            return None

        # Extract metadata to get FHIR viewer URL
        metadata = interpreter.extract_metadata(file_path)

        # Check if FHIR viewer URL is available
        if 'fhir_viewer_url' in metadata:
            return metadata['fhir_viewer_url']

        # If not in metadata, try to extract structured data
        if hasattr(interpreter, 'extract_structured_data') and callable(getattr(interpreter, 'extract_structured_data')):
            try:
                fhir_data = interpreter.extract_structured_data(file_path, 'fhir')
                if isinstance(fhir_data, dict) and 'viewerUrl' in fhir_data:
                    return fhir_data['viewerUrl']
            except Exception as e:
                logger.warning(f"Error extracting FHIR data: {str(e)}")

        return None
    except Exception as e:
        logger.error(f"Error getting FHIR viewer URL: {str(e)}")
        return None

def open_in_fhir_viewer(file_path: str) -> Dict[str, Any]:
    """
    Open a DICOM file in a FHIR-compatible viewer.

    Args:
        file_path: Path to the DICOM file.

    Returns:
        Dictionary with status and message.
    """
    try:
        # Get FHIR viewer URL
        viewer_url = get_fhir_viewer_url(file_path)

        if not viewer_url:
            return {
                'status': 'error',
                'message': 'FHIR viewer URL not available for this file'
            }

        # Open URL in web browser
        webbrowser.open(viewer_url)

        return {
            'status': 'success',
            'message': f'Opened file in FHIR viewer: {viewer_url}'
        }
    except Exception as e:
        logger.error(f"Error opening file in FHIR viewer: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error opening file in FHIR viewer: {str(e)}'
        }

def render_fhir_viewer_button(file_path: str) -> str:
    """
    Render a button to open a DICOM file in a FHIR-compatible viewer.

    Args:
        file_path: Path to the DICOM file.

    Returns:
        HTML for the FHIR viewer button.
    """
    # Check if FHIR viewer URL is available
    viewer_url = get_fhir_viewer_url(file_path)

    if not viewer_url:
        return ""

    # Render button
    return f"""
    <div class="mt-3">
        <a href="{viewer_url}" target="_blank" class="btn btn-primary btn-sm">
            <i class="fas fa-external-link-alt"></i> Open in OHIF Viewer
        </a>
        <small class="text-muted ms-2">View this DICOM file in the OHIF Viewer</small>
    </div>
    """

def render_fhir_viewer_section(file_path: str) -> str:
    """
    Render a section with FHIR viewer information and button.

    Args:
        file_path: Path to the DICOM file.

    Returns:
        HTML for the FHIR viewer section.
    """
    # Check if FHIR viewer URL is available
    viewer_url = get_fhir_viewer_url(file_path)

    if not viewer_url:
        return ""

    # Get file interpreter for the file
    interpreter = get_file_interpreter_for_file(file_path)

    if not interpreter:
        return ""

    # Extract metadata to get DICOM information
    metadata = interpreter.extract_metadata(file_path)
    dicom_metadata = metadata.get('dicom_metadata', {})

    # Get patient and study information
    patient_name = dicom_metadata.get('PatientName', 'Unknown Patient')
    study_desc = dicom_metadata.get('StudyDescription', 'Unknown Study')
    modality = dicom_metadata.get('Modality', 'Unknown')
    study_date = dicom_metadata.get('StudyDate', 'Unknown Date')

    # Render section
    return f"""
    <div class="card mt-4">
        <div class="card-header bg-primary text-white">
            <h5 class="card-title mb-0">
                <i class="fas fa-x-ray me-2"></i> DICOM Viewer
            </h5>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Patient:</strong> {patient_name}</p>
                    <p><strong>Study:</strong> {study_desc}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Modality:</strong> {modality}</p>
                    <p><strong>Date:</strong> {study_date}</p>
                </div>
            </div>
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                This DICOM file can be viewed in the OHIF Viewer, a FHIR-compatible medical imaging viewer.
            </div>
            <a href="{viewer_url}" target="_blank" class="btn btn-primary">
                <i class="fas fa-external-link-alt me-2"></i> Open in OHIF Viewer
            </a>
        </div>
    </div>
    """

# Flask routes for FHIR viewer integration
def register_fhir_viewer_routes(app):
    """
    Register Flask routes for FHIR viewer integration.

    Args:
        app: Flask application instance.
    """
    @app.route('/api/fhir/viewer-url', methods=['POST'])
    def get_fhir_viewer_url_api():
        """API endpoint to get FHIR viewer URL for a file."""
        data = request.json
        file_path = data.get('file_path')

        if not file_path:
            return jsonify({
                'status': 'error',
                'message': 'File path is required'
            }), 400

        viewer_url = get_fhir_viewer_url(file_path)

        if not viewer_url:
            return jsonify({
                'status': 'error',
                'message': 'FHIR viewer URL not available for this file'
            }), 404

        return jsonify({
            'status': 'success',
            'viewer_url': viewer_url
        })

    @app.route('/api/fhir/open-viewer', methods=['POST'])
    def open_fhir_viewer_api():
        """API endpoint to open a file in FHIR viewer."""
        data = request.json
        file_path = data.get('file_path')

        if not file_path:
            return jsonify({
                'status': 'error',
                'message': 'File path is required'
            }), 400

        result = open_in_fhir_viewer(file_path)

        if result['status'] == 'error':
            return jsonify(result), 404

        return jsonify(result)

def is_dicom_file(file_path: str) -> bool:
    """
    Check if a file is a DICOM file.

    Args:
        file_path: Path to the file.

    Returns:
        True if the file is a DICOM file, False otherwise.
    """
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    # Check common DICOM extensions
    if ext in ['.dcm', '.dicom', '.dic']:
        return True

    # Try to get an interpreter for the file
    interpreter = get_file_interpreter_for_file(file_path)

    if not interpreter:
        return False

    # Check if the interpreter is for DICOM files
    metadata = interpreter.extract_metadata(file_path)
    return metadata.get('format') == 'DICOM'

def get_fhir_viewer_config() -> Dict[str, Any]:
    """
    Get configuration for FHIR viewer integration.

    Returns:
        Dictionary with configuration settings.
    """
    # Default configuration
    config = {
        'viewer_url': 'https://ohif-viewer-url/viewer/',
        'enabled': True,
        'open_in_new_tab': True
    }

    # Try to get configuration from app config
    try:
        if current_app and current_app.config:
            if 'FHIR_VIEWER_URL' in current_app.config:
                config['viewer_url'] = current_app.config['FHIR_VIEWER_URL']
            if 'FHIR_VIEWER_ENABLED' in current_app.config:
                config['enabled'] = current_app.config['FHIR_VIEWER_ENABLED']
            if 'FHIR_VIEWER_OPEN_IN_NEW_TAB' in current_app.config:
                config['open_in_new_tab'] = current_app.config['FHIR_VIEWER_OPEN_IN_NEW_TAB']
    except Exception:
        # Ignore errors if current_app is not available
        pass

    return config
