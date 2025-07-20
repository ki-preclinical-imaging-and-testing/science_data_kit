"""
WebSocket Events for Science Data Kit

This module defines WebSocket event handlers for the Flask application.
It provides real-time updates for various components of the application.
"""

import threading
import time
from flask import request, session, current_app
from flask_socketio import emit, join_room, leave_room

from science_data_kit.web.app import socketio
from science_data_kit.core.pages.dashboard import DashboardPage

# Global variables for background task
dashboard_update_thread = None
dashboard_update_stop_event = threading.Event()
dashboard_client_count = 0  # Number of clients in the dashboard room

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
    global dashboard_client_count

    # Get the rooms the client is in
    from flask_socketio import rooms
    client_rooms = rooms()

    # Check if the client is in the dashboard room
    if 'dashboard' in client_rooms:
        # Leave the dashboard room
        leave_room('dashboard')

        # Decrement client count
        if dashboard_client_count > 0:
            dashboard_client_count -= 1

        print(f"Client disconnected from dashboard room. Total clients: {dashboard_client_count}")

        # If no clients are left in the dashboard room, stop the updates
        if dashboard_client_count == 0:
            print("No clients left in dashboard room. Stopping dashboard updates.")
            stop_dashboard_updates()

    # Leave the user's room
    leave_room(session.get('_id', 'anonymous'))

@socketio.on('join_dashboard')
def handle_join_dashboard(data):
    """
    Handle client joining the dashboard room.

    Args:
        data: Dictionary containing client data
    """
    global dashboard_client_count

    # Join the dashboard room
    join_room('dashboard')

    # Increment client count
    dashboard_client_count += 1
    print(f"Client joined dashboard room. Total clients: {dashboard_client_count}")

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

    # Ensure dashboard updates are running
    start_dashboard_updates()

@socketio.on('leave_dashboard')
def handle_leave_dashboard():
    """Handle client leaving the dashboard room."""
    global dashboard_client_count

    # Leave the dashboard room
    leave_room('dashboard')

    # Decrement client count
    if dashboard_client_count > 0:
        dashboard_client_count -= 1

    print(f"Client left dashboard room. Total clients: {dashboard_client_count}")

    # If no clients are left in the dashboard room, stop the updates
    if dashboard_client_count == 0:
        print("No clients left in dashboard room. Stopping dashboard updates.")
        stop_dashboard_updates()

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


def dashboard_update_task():
    """
    Background task to periodically update dashboard data.

    This function runs in a separate thread and periodically emits
    dashboard updates to all clients in the dashboard room.
    """
    global dashboard_update_thread

    print("Starting dashboard update task")
    while not dashboard_update_stop_event.is_set():
        # Check if there are still clients in the dashboard room
        if dashboard_client_count <= 0:
            print("No clients in dashboard room. Stopping dashboard updates.")
            break

        # Emit dashboard update
        emit_dashboard_update()

        # Sleep for the specified interval
        update_interval = current_app.config.get('DASHBOARD_UPDATE_INTERVAL', 10)
        dashboard_update_stop_event.wait(update_interval)

    # Reset the thread variable when the task stops
    dashboard_update_thread = None

    print("Dashboard update task stopped")


def start_dashboard_updates():
    """
    Start the dashboard update background task.

    This function starts a background thread that periodically
    emits dashboard updates to all clients in the dashboard room.
    """
    global dashboard_update_thread, dashboard_update_stop_event

    # Check if the thread is already running
    if dashboard_update_thread and dashboard_update_thread.is_alive():
        print("Dashboard update task is already running")
        return

    # Reset the stop event
    dashboard_update_stop_event.clear()

    # Create and start the thread
    dashboard_update_thread = threading.Thread(target=dashboard_update_task)
    dashboard_update_thread.daemon = True
    dashboard_update_thread.start()

    print("Dashboard update task started")


def stop_dashboard_updates():
    """
    Stop the dashboard update background task.

    This function stops the background thread that periodically
    emits dashboard updates to all clients in the dashboard room.
    """
    global dashboard_update_thread, dashboard_update_stop_event

    # Check if the thread is running
    if not dashboard_update_thread or not dashboard_update_thread.is_alive():
        print("Dashboard update task is not running")
        return

    # Set the stop event to signal the thread to stop
    dashboard_update_stop_event.set()

    # Wait for the thread to finish
    dashboard_update_thread.join(timeout=5.0)

    # Reset the thread
    dashboard_update_thread = None

    print("Dashboard update task stopped")
