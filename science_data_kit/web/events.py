"""
WebSocket Events for Science Data Kit

This module defines WebSocket event handlers for the Flask application.
It provides real-time updates for various components of the application.
"""

from flask import request, session
from flask_socketio import emit, join_room, leave_room

from science_data_kit.web.app import socketio
from science_data_kit.core.pages.dashboard import DashboardPage

@socketio.on('connect')
def handle_connect():
    """Handle client connection to WebSocket."""
    # Check if user is authenticated
    if not session.get('logged_in'):
        return False  # Reject the connection
    
    # Join a room based on the user's session ID
    join_room(session.get('_id', 'anonymous'))
    
    # Emit a welcome message
    emit('status', {'message': 'Connected to WebSocket server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection from WebSocket."""
    # Leave the room
    leave_room(session.get('_id', 'anonymous'))

@socketio.on('join_dashboard')
def handle_join_dashboard(data):
    """
    Handle client joining the dashboard room.
    
    Args:
        data: Dictionary containing client data
    """
    # Join the dashboard room
    join_room('dashboard')
    
    # Get dashboard data
    page = DashboardPage()
    page_data = page.get_page_data()
    
    # Emit dashboard data to the client
    emit('dashboard_data', {
        'metrics': page_data.metrics,
        'charts': page_data.charts,
        'tables': page_data.tables,
        'status_items': page_data.status_items,
        'connected_services': page_data.connected_services
    })

@socketio.on('leave_dashboard')
def handle_leave_dashboard():
    """Handle client leaving the dashboard room."""
    leave_room('dashboard')

def emit_dashboard_update():
    """
    Emit dashboard updates to all clients in the dashboard room.
    
    This function can be called from other parts of the application
    to push updates to connected clients.
    """
    # Get dashboard data
    page = DashboardPage()
    page_data = page.get_page_data()
    
    # Emit dashboard data to all clients in the dashboard room
    socketio.emit('dashboard_update', {
        'metrics': page_data.metrics,
        'charts': page_data.charts,
        'tables': page_data.tables,
        'status_items': page_data.status_items,
        'connected_services': page_data.connected_services
    }, room='dashboard')