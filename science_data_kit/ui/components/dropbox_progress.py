"""
Dropbox Progress Indicators Component for Science Data Kit

This module provides progress indicators for Dropbox file operations.
"""

import streamlit as st
import time
from typing import Dict, Any, Optional, List, Union, Callable
import threading
import queue

class DropboxProgressTracker:
    """
    Class for tracking progress of Dropbox file operations.
    
    This class provides methods for creating and updating progress bars
    for various Dropbox operations such as uploads, downloads, and synchronization.
    """
    
    def __init__(self):
        """Initialize the progress tracker."""
        self.operations = {}
        self.completed_operations = []
        self.operation_counter = 0
        self.message_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.background_thread = None
        
    def start_operation(self, operation_type: str, name: str, total_size: int = 0) -> int:
        """
        Start tracking a new operation.
        
        Args:
            operation_type: Type of operation (upload, download, sync)
            name: Name of the file or folder being operated on
            total_size: Total size of the file or folder in bytes
            
        Returns:
            Operation ID for tracking
        """
        operation_id = self.operation_counter
        self.operation_counter += 1
        
        self.operations[operation_id] = {
            "type": operation_type,
            "name": name,
            "total_size": total_size,
            "transferred_size": 0,
            "status": "in_progress",
            "progress": 0.0,
            "start_time": time.time(),
            "end_time": None,
            "speed": 0.0,
            "estimated_time": None
        }
        
        return operation_id
    
    def update_operation(self, operation_id: int, transferred_size: int) -> None:
        """
        Update the progress of an operation.
        
        Args:
            operation_id: ID of the operation to update
            transferred_size: Amount of data transferred so far in bytes
        """
        if operation_id not in self.operations:
            return
            
        operation = self.operations[operation_id]
        operation["transferred_size"] = transferred_size
        
        if operation["total_size"] > 0:
            operation["progress"] = transferred_size / operation["total_size"]
        else:
            operation["progress"] = 0.0
            
        # Calculate speed and estimated time
        elapsed_time = time.time() - operation["start_time"]
        if elapsed_time > 0:
            operation["speed"] = transferred_size / elapsed_time
            
            if operation["speed"] > 0 and operation["total_size"] > 0:
                remaining_size = operation["total_size"] - transferred_size
                operation["estimated_time"] = remaining_size / operation["speed"]
            else:
                operation["estimated_time"] = None
        
    def complete_operation(self, operation_id: int, success: bool = True) -> None:
        """
        Mark an operation as completed.
        
        Args:
            operation_id: ID of the operation to complete
            success: Whether the operation was successful
        """
        if operation_id not in self.operations:
            return
            
        operation = self.operations[operation_id]
        operation["status"] = "completed" if success else "failed"
        operation["end_time"] = time.time()
        
        if success:
            operation["progress"] = 1.0
            operation["transferred_size"] = operation["total_size"]
            
        # Move to completed operations
        self.completed_operations.append(operation)
        del self.operations[operation_id]
        
    def get_operation(self, operation_id: int) -> Dict[str, Any]:
        """
        Get information about an operation.
        
        Args:
            operation_id: ID of the operation to get
            
        Returns:
            Dictionary with operation information
        """
        if operation_id in self.operations:
            return self.operations[operation_id]
        
        # Check completed operations
        for operation in self.completed_operations:
            if operation.get("id") == operation_id:
                return operation
                
        return None
        
    def get_active_operations(self) -> List[Dict[str, Any]]:
        """
        Get all active operations.
        
        Returns:
            List of dictionaries with operation information
        """
        return list(self.operations.values())
        
    def get_completed_operations(self) -> List[Dict[str, Any]]:
        """
        Get all completed operations.
        
        Returns:
            List of dictionaries with operation information
        """
        return self.completed_operations
        
    def clear_completed_operations(self) -> None:
        """Clear the list of completed operations."""
        self.completed_operations = []
        
    def format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
            
    def format_time(self, seconds: float) -> str:
        """
        Format time in human-readable format.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        if seconds is None:
            return "Unknown"
            
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
            
    def format_speed(self, bytes_per_second: float) -> str:
        """
        Format speed in human-readable format.
        
        Args:
            bytes_per_second: Speed in bytes per second
            
        Returns:
            Formatted speed string
        """
        if bytes_per_second < 1024:
            return f"{bytes_per_second:.1f} B/s"
        elif bytes_per_second < 1024 * 1024:
            return f"{bytes_per_second / 1024:.1f} KB/s"
        elif bytes_per_second < 1024 * 1024 * 1024:
            return f"{bytes_per_second / (1024 * 1024):.1f} MB/s"
        else:
            return f"{bytes_per_second / (1024 * 1024 * 1024):.1f} GB/s"
            
    def add_message(self, message: str) -> None:
        """
        Add a message to the queue for display.
        
        Args:
            message: Message to display
        """
        self.message_queue.put({
            "text": message,
            "time": time.time()
        })
        
    def get_messages(self, max_messages: int = 10) -> List[Dict[str, Any]]:
        """
        Get messages from the queue.
        
        Args:
            max_messages: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        messages = []
        
        # Get all messages from the queue
        while not self.message_queue.empty() and len(messages) < max_messages:
            try:
                messages.append(self.message_queue.get_nowait())
            except queue.Empty:
                break
                
        return messages
        
    def start_background_thread(self, callback: Callable[[], None], interval: float = 0.5) -> None:
        """
        Start a background thread for updating progress.
        
        Args:
            callback: Function to call on each update
            interval: Time between updates in seconds
        """
        if self.background_thread is not None and self.background_thread.is_alive():
            return
            
        self.stop_event.clear()
        
        def update_loop():
            while not self.stop_event.is_set():
                callback()
                time.sleep(interval)
                
        self.background_thread = threading.Thread(target=update_loop)
        self.background_thread.daemon = True
        self.background_thread.start()
        
    def stop_background_thread(self) -> None:
        """Stop the background thread."""
        if self.background_thread is not None and self.background_thread.is_alive():
            self.stop_event.set()
            self.background_thread.join(timeout=1.0)
            self.background_thread = None


class DropboxProgressDisplay:
    """
    Class for displaying progress of Dropbox file operations in Streamlit.
    
    This class provides methods for rendering progress bars and status information
    for various Dropbox operations.
    """
    
    def __init__(self, tracker: DropboxProgressTracker):
        """
        Initialize the progress display.
        
        Args:
            tracker: DropboxProgressTracker instance
        """
        self.tracker = tracker
        self.progress_bars = {}
        self.status_elements = {}
        self.details_elements = {}
        
    def render_active_operations(self) -> None:
        """Render all active operations."""
        active_operations = self.tracker.get_active_operations()
        
        if not active_operations:
            st.info("No active operations")
            return
            
        st.subheader("Active Operations")
        
        for operation in active_operations:
            operation_id = operation.get("id")
            
            # Create progress bar if it doesn't exist
            if operation_id not in self.progress_bars:
                self.progress_bars[operation_id] = st.progress(0.0)
                self.status_elements[operation_id] = st.empty()
                self.details_elements[operation_id] = st.empty()
                
            # Update progress bar
            progress = operation["progress"]
            self.progress_bars[operation_id].progress(progress)
            
            # Update status
            status_text = f"{operation['type'].capitalize()}: {operation['name']}"
            if operation["total_size"] > 0:
                status_text += f" ({self.tracker.format_size(operation['transferred_size'])} / {self.tracker.format_size(operation['total_size'])})"
            self.status_elements[operation_id].text(status_text)
            
            # Update details
            details_text = ""
            if operation["speed"] > 0:
                details_text += f"Speed: {self.tracker.format_speed(operation['speed'])} | "
            if operation["estimated_time"] is not None:
                details_text += f"Estimated time remaining: {self.tracker.format_time(operation['estimated_time'])}"
            self.details_elements[operation_id].text(details_text)
            
    def render_completed_operations(self, max_operations: int = 5) -> None:
        """
        Render completed operations.
        
        Args:
            max_operations: Maximum number of operations to display
        """
        completed_operations = self.tracker.get_completed_operations()
        
        if not completed_operations:
            return
            
        st.subheader("Completed Operations")
        
        # Sort by end time (most recent first)
        completed_operations.sort(key=lambda op: op["end_time"] if op["end_time"] else 0, reverse=True)
        
        # Display only the most recent operations
        for operation in completed_operations[:max_operations]:
            status = "✅" if operation["status"] == "completed" else "❌"
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"{status} {operation['type'].capitalize()}: {operation['name']}")
                
            with col2:
                if operation["end_time"] and operation["start_time"]:
                    duration = operation["end_time"] - operation["start_time"]
                    st.write(f"Duration: {self.tracker.format_time(duration)}")
                    
    def render_messages(self, max_messages: int = 5) -> None:
        """
        Render messages.
        
        Args:
            max_messages: Maximum number of messages to display
        """
        messages = self.tracker.get_messages(max_messages)
        
        if not messages:
            return
            
        st.subheader("Messages")
        
        for message in messages:
            st.text(message["text"])
            
    def render_dashboard(self) -> None:
        """Render a complete dashboard with active operations, completed operations, and messages."""
        st.title("Dropbox Operations Dashboard")
        
        # Render active operations
        self.render_active_operations()
        
        # Render completed operations
        self.render_completed_operations()
        
        # Render messages
        self.render_messages()
        
        # Add a button to clear completed operations
        if self.tracker.get_completed_operations():
            if st.button("Clear Completed Operations"):
                self.tracker.clear_completed_operations()
                st.experimental_rerun()


# Create a singleton instance of the progress tracker
if "dropbox_progress_tracker" not in st.session_state:
    st.session_state["dropbox_progress_tracker"] = DropboxProgressTracker()

def get_progress_tracker() -> DropboxProgressTracker:
    """
    Get the singleton instance of the progress tracker.
    
    Returns:
        DropboxProgressTracker instance
    """
    return st.session_state["dropbox_progress_tracker"]

def render_progress_dashboard() -> None:
    """Render the progress dashboard."""
    tracker = get_progress_tracker()
    display = DropboxProgressDisplay(tracker)
    display.render_dashboard()