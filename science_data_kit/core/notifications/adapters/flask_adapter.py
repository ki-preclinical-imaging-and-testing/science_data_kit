"""
Flask Notification Adapter for Science Data Kit

This module provides a notification adapter for Flask that uses Flask's flash messages
and JavaScript to display notifications.
"""

import logging
import json
from typing import Any, Dict, List, Optional, Union

from science_data_kit.core.notifications.adapters.base_adapter import NotificationAdapter
from science_data_kit.core.notifications.notification_types import (
    Notification, NotificationType, NotificationLevel, NotificationPosition
)

logger = logging.getLogger(__name__)

class FlaskNotificationAdapter(NotificationAdapter):
    """
    A notification adapter for Flask that uses Flask's flash messages and JavaScript
    to display notifications.
    
    This adapter stores notifications in Flask's session and uses JavaScript to
    display them as toast notifications, alerts, banners, modals, or snackbars.
    """
    
    def __init__(self, socketio=None):
        """
        Initialize the Flask notification adapter.
        
        Args:
            socketio: Optional Flask-SocketIO instance for real-time notifications
        """
        try:
            from flask import flash, session, request, current_app, has_request_context
            self._flash = flash
            self._session = session
            self._request = request
            self._current_app = current_app
            self._has_request_context = has_request_context
        except ImportError:
            raise ImportError("Flask is not installed. Please install it with 'pip install flask'.")
        
        self._socketio = socketio
    
    def display(self, notification: Notification) -> None:
        """
        Display a notification to the user.
        
        Args:
            notification: The notification to display
        """
        # Store the notification in session
        self._add_notification_to_session(notification)
        
        # Flash the notification for server-side rendering
        self._flash_notification(notification)
        
        # Emit the notification via WebSocket if available
        self._emit_notification(notification)
    
    def update(self, notification: Notification) -> None:
        """
        Update an existing notification.
        
        Args:
            notification: The notification to update
        """
        # Update the notification in session
        self._add_notification_to_session(notification)
        
        # Emit the updated notification via WebSocket if available
        self._emit_notification(notification, event="update_notification")
    
    def remove(self, notification_id: str) -> None:
        """
        Remove a notification from the UI.
        
        Args:
            notification_id: The ID of the notification to remove
        """
        # Remove the notification from session
        self._remove_notification_from_session(notification_id)
        
        # Emit the removal via WebSocket if available
        if self._socketio:
            self._socketio.emit("remove_notification", {"id": notification_id})
    
    def clear(self, type: Optional[NotificationType] = None) -> None:
        """
        Clear all notifications of a specific type, or all notifications if type is None.
        
        Args:
            type: The type of notifications to clear, or None to clear all notifications
        """
        if not self._has_request_context():
            return
        
        if type is None:
            # Clear all notifications
            self._session["notifications"] = {}
        else:
            # Clear notifications of the specified type
            if "notifications" in self._session:
                notifications = self._session["notifications"]
                for notification_id in list(notifications.keys()):
                    notification_data = notifications[notification_id]
                    if notification_data.get("type") == type:
                        del notifications[notification_id]
                self._session["notifications"] = notifications
        
        # Emit the clear via WebSocket if available
        if self._socketio:
            self._socketio.emit("clear_notifications", {"type": type})
    
    def mark_all_as_read(self) -> None:
        """Mark all notifications as read."""
        if not self._has_request_context():
            return
        
        if "notifications" in self._session:
            notifications = self._session["notifications"]
            for notification_id in notifications:
                notifications[notification_id]["read"] = True
            self._session["notifications"] = notifications
        
        # Emit the mark all as read via WebSocket if available
        if self._socketio:
            self._socketio.emit("mark_all_as_read")
    
    def _add_notification_to_session(self, notification: Notification) -> None:
        """
        Add a notification to the session.
        
        Args:
            notification: The notification to add
        """
        if not self._has_request_context():
            return
        
        # Initialize notifications in session if needed
        if "notifications" not in self._session:
            self._session["notifications"] = {}
        
        # Add the notification to session
        self._session["notifications"][notification.id] = notification.to_dict()
    
    def _remove_notification_from_session(self, notification_id: str) -> None:
        """
        Remove a notification from the session.
        
        Args:
            notification_id: The ID of the notification to remove
        """
        if not self._has_request_context():
            return
        
        if "notifications" in self._session and notification_id in self._session["notifications"]:
            del self._session["notifications"][notification_id]
    
    def _flash_notification(self, notification: Notification) -> None:
        """
        Flash a notification for server-side rendering.
        
        Args:
            notification: The notification to flash
        """
        if not self._has_request_context():
            return
        
        # Map notification level to Flask category
        level_map = {
            NotificationLevel.SUCCESS: "success",
            NotificationLevel.INFO: "info",
            NotificationLevel.WARNING: "warning",
            NotificationLevel.ERROR: "danger",
            NotificationLevel.DEBUG: "info",
        }
        
        # Get the appropriate category
        category = level_map.get(notification.level, "info")
        
        # Create the message
        message = notification.message
        if notification.title:
            message = f"{notification.title}: {message}"
        
        # Flash the message
        self._flash(message, category)
    
    def _emit_notification(self, notification: Notification, event: str = "new_notification") -> None:
        """
        Emit a notification via WebSocket.
        
        Args:
            notification: The notification to emit
            event: The event name to use
        """
        if self._socketio:
            self._socketio.emit(event, notification.to_dict())
    
    @staticmethod
    def get_javascript() -> str:
        """
        Get the JavaScript code for displaying notifications.
        
        Returns:
            The JavaScript code as a string
        """
        return """
        // Notification System
        document.addEventListener('DOMContentLoaded', function() {
            // Create toast container if it doesn't exist
            let toastContainer = document.querySelector('.toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
                document.body.appendChild(toastContainer);
            }
            
            // Function to create a toast notification
            function createToast(notification) {
                // Map notification level to Bootstrap class
                const levelMap = {
                    'success': 'bg-success text-white',
                    'info': 'bg-info text-white',
                    'warning': 'bg-warning text-dark',
                    'error': 'bg-danger text-white',
                    'debug': 'bg-secondary text-white'
                };
                
                // Get the appropriate class
                const bgClass = levelMap[notification.level] || 'bg-info text-white';
                
                // Create the toast element
                const toast = document.createElement('div');
                toast.className = `toast ${bgClass}`;
                toast.setAttribute('role', 'alert');
                toast.setAttribute('aria-live', 'assertive');
                toast.setAttribute('aria-atomic', 'true');
                toast.setAttribute('data-notification-id', notification.id);
                toast.setAttribute('data-bs-autohide', notification.dismissible ? 'true' : 'false');
                if (notification.duration) {
                    toast.setAttribute('data-bs-delay', notification.duration);
                }
                
                // Create the toast header
                const header = document.createElement('div');
                header.className = 'toast-header';
                
                const title = document.createElement('strong');
                title.className = 'me-auto';
                title.textContent = notification.title || 'Notification';
                
                const time = document.createElement('small');
                time.textContent = 'just now';
                
                const closeButton = document.createElement('button');
                closeButton.type = 'button';
                closeButton.className = 'btn-close';
                closeButton.setAttribute('data-bs-dismiss', 'toast');
                closeButton.setAttribute('aria-label', 'Close');
                
                header.appendChild(title);
                header.appendChild(time);
                header.appendChild(closeButton);
                
                // Create the toast body
                const body = document.createElement('div');
                body.className = 'toast-body';
                body.textContent = notification.message;
                
                // Add actions if any
                if (notification.actions && notification.actions.length > 0) {
                    const actionsDiv = document.createElement('div');
                    actionsDiv.className = 'd-flex justify-content-end mt-2 pt-2 border-top';
                    
                    notification.actions.forEach(action => {
                        const button = document.createElement('button');
                        button.type = 'button';
                        button.className = 'btn btn-sm btn-primary me-2';
                        button.textContent = action.label || 'Action';
                        button.addEventListener('click', function() {
                            // Send action to server
                            fetch('/api/notifications/action', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    notification_id: notification.id,
                                    action_id: action.id
                                }),
                            });
                        });
                        actionsDiv.appendChild(button);
                    });
                    
                    body.appendChild(actionsDiv);
                }
                
                // Assemble the toast
                toast.appendChild(header);
                toast.appendChild(body);
                
                // Add the toast to the container
                toastContainer.appendChild(toast);
                
                // Initialize and show the toast
                const bsToast = new bootstrap.Toast(toast);
                bsToast.show();
                
                // Return the toast element
                return toast;
            }
            
            // Function to create an alert notification
            function createAlert(notification) {
                // Map notification level to Bootstrap class
                const levelMap = {
                    'success': 'alert-success',
                    'info': 'alert-info',
                    'warning': 'alert-warning',
                    'error': 'alert-danger',
                    'debug': 'alert-secondary'
                };
                
                // Get the appropriate class
                const alertClass = levelMap[notification.level] || 'alert-info';
                
                // Create the alert element
                const alert = document.createElement('div');
                alert.className = `alert ${alertClass} alert-dismissible fade show`;
                alert.setAttribute('role', 'alert');
                alert.setAttribute('data-notification-id', notification.id);
                
                // Add title if provided
                if (notification.title) {
                    const title = document.createElement('h4');
                    title.className = 'alert-heading';
                    title.textContent = notification.title;
                    alert.appendChild(title);
                }
                
                // Add message
                const message = document.createElement('p');
                message.textContent = notification.message;
                alert.appendChild(message);
                
                // Add details if provided
                if (notification.details) {
                    const details = document.createElement('p');
                    details.className = 'mb-0';
                    details.textContent = notification.details;
                    alert.appendChild(details);
                }
                
                // Add close button if dismissible
                if (notification.dismissible) {
                    const closeButton = document.createElement('button');
                    closeButton.type = 'button';
                    closeButton.className = 'btn-close';
                    closeButton.setAttribute('data-bs-dismiss', 'alert');
                    closeButton.setAttribute('aria-label', 'Close');
                    alert.appendChild(closeButton);
                }
                
                // Add the alert to the page
                const alertContainer = document.querySelector('#alert-container');
                if (alertContainer) {
                    alertContainer.appendChild(alert);
                } else {
                    // If no container exists, add it to the top of the main content
                    const main = document.querySelector('main') || document.body;
                    main.insertBefore(alert, main.firstChild);
                }
                
                // Return the alert element
                return alert;
            }
            
            // Function to create a banner notification
            function createBanner(notification) {
                // Map notification level to Bootstrap class
                const levelMap = {
                    'success': 'alert-success',
                    'info': 'alert-info',
                    'warning': 'alert-warning',
                    'error': 'alert-danger',
                    'debug': 'alert-secondary'
                };
                
                // Get the appropriate class
                const alertClass = levelMap[notification.level] || 'alert-info';
                
                // Create the banner element
                const banner = document.createElement('div');
                banner.className = `alert ${alertClass} alert-dismissible fade show m-0 rounded-0`;
                banner.setAttribute('role', 'alert');
                banner.setAttribute('data-notification-id', notification.id);
                
                // Create a container for the content
                const container = document.createElement('div');
                container.className = 'container';
                
                // Add title and message
                let content = notification.message;
                if (notification.title) {
                    content = `<strong>${notification.title}</strong> ${content}`;
                }
                container.innerHTML = content;
                
                // Add close button if dismissible
                if (notification.dismissible) {
                    const closeButton = document.createElement('button');
                    closeButton.type = 'button';
                    closeButton.className = 'btn-close';
                    closeButton.setAttribute('data-bs-dismiss', 'alert');
                    closeButton.setAttribute('aria-label', 'Close');
                    container.appendChild(closeButton);
                }
                
                banner.appendChild(container);
                
                // Add the banner to the page
                const body = document.body;
                body.insertBefore(banner, body.firstChild);
                
                // Return the banner element
                return banner;
            }
            
            // Function to create a modal notification
            function createModal(notification) {
                // Create the modal element
                const modalId = `modal-${notification.id}`;
                const modal = document.createElement('div');
                modal.className = 'modal fade';
                modal.id = modalId;
                modal.setAttribute('tabindex', '-1');
                modal.setAttribute('aria-labelledby', `${modalId}-label`);
                modal.setAttribute('aria-hidden', 'true');
                modal.setAttribute('data-notification-id', notification.id);
                
                // Create the modal dialog
                const modalDialog = document.createElement('div');
                modalDialog.className = 'modal-dialog';
                
                // Create the modal content
                const modalContent = document.createElement('div');
                modalContent.className = 'modal-content';
                
                // Create the modal header
                const modalHeader = document.createElement('div');
                modalHeader.className = 'modal-header';
                
                const modalTitle = document.createElement('h5');
                modalTitle.className = 'modal-title';
                modalTitle.id = `${modalId}-label`;
                modalTitle.textContent = notification.title || 'Notification';
                
                const closeButton = document.createElement('button');
                closeButton.type = 'button';
                closeButton.className = 'btn-close';
                closeButton.setAttribute('data-bs-dismiss', 'modal');
                closeButton.setAttribute('aria-label', 'Close');
                
                modalHeader.appendChild(modalTitle);
                modalHeader.appendChild(closeButton);
                
                // Create the modal body
                const modalBody = document.createElement('div');
                modalBody.className = 'modal-body';
                modalBody.textContent = notification.message;
                
                if (notification.details) {
                    const details = document.createElement('p');
                    details.className = 'mt-3';
                    details.textContent = notification.details;
                    modalBody.appendChild(details);
                }
                
                // Create the modal footer
                const modalFooter = document.createElement('div');
                modalFooter.className = 'modal-footer';
                
                // Add actions if any
                if (notification.actions && notification.actions.length > 0) {
                    notification.actions.forEach(action => {
                        const button = document.createElement('button');
                        button.type = 'button';
                        button.className = 'btn btn-primary';
                        button.textContent = action.label || 'Action';
                        button.addEventListener('click', function() {
                            // Send action to server
                            fetch('/api/notifications/action', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    notification_id: notification.id,
                                    action_id: action.id
                                }),
                            });
                            
                            // Close the modal
                            const modalInstance = bootstrap.Modal.getInstance(modal);
                            if (modalInstance) {
                                modalInstance.hide();
                            }
                        });
                        modalFooter.appendChild(button);
                    });
                }
                
                // Add close button
                const closeModalButton = document.createElement('button');
                closeModalButton.type = 'button';
                closeModalButton.className = 'btn btn-secondary';
                closeModalButton.setAttribute('data-bs-dismiss', 'modal');
                closeModalButton.textContent = 'Close';
                modalFooter.appendChild(closeModalButton);
                
                // Assemble the modal
                modalContent.appendChild(modalHeader);
                modalContent.appendChild(modalBody);
                modalContent.appendChild(modalFooter);
                modalDialog.appendChild(modalContent);
                modal.appendChild(modalDialog);
                
                // Add the modal to the page
                document.body.appendChild(modal);
                
                // Initialize and show the modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
                
                // Return the modal element
                return modal;
            }
            
            // Function to create a snackbar notification
            function createSnackbar(notification) {
                // Create the snackbar element
                const snackbar = document.createElement('div');
                snackbar.className = 'snackbar';
                snackbar.setAttribute('data-notification-id', notification.id);
                
                // Map notification level to class
                const levelMap = {
                    'success': 'snackbar-success',
                    'info': 'snackbar-info',
                    'warning': 'snackbar-warning',
                    'error': 'snackbar-error',
                    'debug': 'snackbar-debug'
                };
                
                // Add level class
                snackbar.classList.add(levelMap[notification.level] || 'snackbar-info');
                
                // Add position class
                const positionMap = {
                    'top-left': 'snackbar-top-left',
                    'top-center': 'snackbar-top-center',
                    'top-right': 'snackbar-top-right',
                    'bottom-left': 'snackbar-bottom-left',
                    'bottom-center': 'snackbar-bottom-center',
                    'bottom-right': 'snackbar-bottom-right'
                };
                
                snackbar.classList.add(positionMap[notification.position] || 'snackbar-bottom-center');
                
                // Add message
                const message = document.createElement('div');
                message.className = 'snackbar-message';
                message.textContent = notification.message;
                snackbar.appendChild(message);
                
                // Add close button if dismissible
                if (notification.dismissible) {
                    const closeButton = document.createElement('button');
                    closeButton.className = 'snackbar-close';
                    closeButton.textContent = '×';
                    closeButton.addEventListener('click', function() {
                        snackbar.remove();
                    });
                    snackbar.appendChild(closeButton);
                }
                
                // Add the snackbar to the page
                document.body.appendChild(snackbar);
                
                // Show the snackbar
                setTimeout(() => {
                    snackbar.classList.add('show');
                }, 10);
                
                // Hide the snackbar after the duration
                if (notification.duration) {
                    setTimeout(() => {
                        snackbar.classList.remove('show');
                        setTimeout(() => {
                            snackbar.remove();
                        }, 300);
                    }, notification.duration);
                }
                
                // Return the snackbar element
                return snackbar;
            }
            
            // Function to display a notification
            function displayNotification(notification) {
                switch (notification.type) {
                    case 'toast':
                        return createToast(notification);
                    case 'alert':
                        return createAlert(notification);
                    case 'banner':
                        return createBanner(notification);
                    case 'modal':
                        return createModal(notification);
                    case 'snackbar':
                        return createSnackbar(notification);
                    default:
                        return createToast(notification);
                }
            }
            
            // Display notifications from the server
            const notifications = JSON.parse(document.getElementById('notifications-data').textContent || '[]');
            notifications.forEach(displayNotification);
            
            // Set up WebSocket for real-time notifications
            if (typeof io !== 'undefined') {
                const socket = io();
                
                socket.on('new_notification', function(notification) {
                    displayNotification(notification);
                });
                
                socket.on('update_notification', function(notification) {
                    // Remove the old notification
                    const oldElement = document.querySelector(`[data-notification-id="${notification.id}"]`);
                    if (oldElement) {
                        oldElement.remove();
                    }
                    
                    // Display the updated notification
                    displayNotification(notification);
                });
                
                socket.on('remove_notification', function(data) {
                    const element = document.querySelector(`[data-notification-id="${data.id}"]`);
                    if (element) {
                        element.remove();
                    }
                });
                
                socket.on('clear_notifications', function(data) {
                    if (data.type) {
                        // Clear notifications of the specified type
                        document.querySelectorAll(`[data-notification-type="${data.type}"]`).forEach(el => {
                            el.remove();
                        });
                    } else {
                        // Clear all notifications
                        document.querySelectorAll('[data-notification-id]').forEach(el => {
                            el.remove();
                        });
                    }
                });
                
                socket.on('mark_all_as_read', function() {
                    // Mark all notifications as read
                    document.querySelectorAll('[data-notification-id]').forEach(el => {
                        el.classList.add('read');
                    });
                });
            }
        });
        """
    
    @staticmethod
    def get_css() -> str:
        """
        Get the CSS code for styling notifications.
        
        Returns:
            The CSS code as a string
        """
        return """
        /* Snackbar styles */
        .snackbar {
            visibility: hidden;
            min-width: 250px;
            margin-left: -125px;
            background-color: #333;
            color: #fff;
            text-align: center;
            border-radius: 2px;
            padding: 16px;
            position: fixed;
            z-index: 1050;
            left: 50%;
            bottom: 30px;
            font-size: 17px;
            transition: visibility 0s 0.3s, opacity 0.3s linear;
            opacity: 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .snackbar.show {
            visibility: visible;
            opacity: 1;
            transition: opacity 0.3s linear;
        }
        
        .snackbar-success {
            background-color: #28a745;
        }
        
        .snackbar-info {
            background-color: #17a2b8;
        }
        
        .snackbar-warning {
            background-color: #ffc107;
            color: #212529;
        }
        
        .snackbar-error {
            background-color: #dc3545;
        }
        
        .snackbar-debug {
            background-color: #6c757d;
        }
        
        .snackbar-top-left {
            top: 30px;
            bottom: auto;
            left: 30px;
            margin-left: 0;
        }
        
        .snackbar-top-center {
            top: 30px;
            bottom: auto;
        }
        
        .snackbar-top-right {
            top: 30px;
            bottom: auto;
            left: auto;
            right: 30px;
            margin-left: 0;
        }
        
        .snackbar-bottom-left {
            bottom: 30px;
            left: 30px;
            margin-left: 0;
        }
        
        .snackbar-bottom-center {
            bottom: 30px;
        }
        
        .snackbar-bottom-right {
            bottom: 30px;
            left: auto;
            right: 30px;
            margin-left: 0;
        }
        
        .snackbar-message {
            flex-grow: 1;
        }
        
        .snackbar-close {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            margin-left: 10px;
            padding: 0;
            line-height: 1;
        }
        
        /* Toast container */
        .toast-container {
            z-index: 1050;
        }
        
        /* Notification read status */
        [data-notification-id].read {
            opacity: 0.7;
        }
        """