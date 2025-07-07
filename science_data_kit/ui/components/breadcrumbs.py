"""
Breadcrumbs Component for Science Data Kit

This module provides a standardized breadcrumb navigation component for use across the application
to improve navigation in complex workflows.
"""

import streamlit as st
from typing import List, Dict, Optional, Callable, Union
from .terminology import get_term

class Breadcrumb:
    """
    Represents a single breadcrumb in a navigation path.
    
    Attributes:
        label (str): The display label for the breadcrumb
        url (str, optional): The URL or path for the breadcrumb
        callback (callable, optional): Function to call when the breadcrumb is clicked
        active (bool): Whether this breadcrumb represents the current page
        icon (str, optional): Icon to display with the breadcrumb
    """
    
    def __init__(
        self, 
        label: str, 
        url: Optional[str] = None, 
        callback: Optional[Callable] = None,
        active: bool = False,
        icon: Optional[str] = None
    ):
        """
        Initialize a breadcrumb.
        
        Args:
            label (str): The display label for the breadcrumb
            url (str, optional): The URL or path for the breadcrumb
            callback (callable, optional): Function to call when the breadcrumb is clicked
            active (bool): Whether this breadcrumb represents the current page
            icon (str, optional): Icon to display with the breadcrumb
        """
        self.label = label
        self.url = url
        self.callback = callback
        self.active = active
        self.icon = icon

class BreadcrumbTrail:
    """
    Manages a trail of breadcrumbs for navigation.
    
    Attributes:
        breadcrumbs (List[Breadcrumb]): The list of breadcrumbs in the trail
        separator (str): The separator to display between breadcrumbs
        container_style (Dict): CSS styles for the breadcrumb container
        breadcrumb_style (Dict): CSS styles for individual breadcrumbs
        active_style (Dict): CSS styles for the active breadcrumb
    """
    
    def __init__(
        self,
        separator: str = ">",
        container_style: Optional[Dict] = None,
        breadcrumb_style: Optional[Dict] = None,
        active_style: Optional[Dict] = None
    ):
        """
        Initialize a breadcrumb trail.
        
        Args:
            separator (str): The separator to display between breadcrumbs
            container_style (Dict, optional): CSS styles for the breadcrumb container
            breadcrumb_style (Dict, optional): CSS styles for individual breadcrumbs
            active_style (Dict, optional): CSS styles for the active breadcrumb
        """
        self.breadcrumbs: List[Breadcrumb] = []
        self.separator = separator
        
        # Default styles
        self.container_style = {
            "padding": "0.5rem 0",
            "margin-bottom": "1rem",
            "font-size": "0.9rem"
        }
        
        self.breadcrumb_style = {
            "color": "#0066cc",
            "text-decoration": "none",
            "margin": "0 0.3rem"
        }
        
        self.active_style = {
            "color": "#333333",
            "font-weight": "bold",
            "margin": "0 0.3rem"
        }
        
        # Override with custom styles if provided
        if container_style:
            self.container_style.update(container_style)
            
        if breadcrumb_style:
            self.breadcrumb_style.update(breadcrumb_style)
            
        if active_style:
            self.active_style.update(active_style)
    
    def add_breadcrumb(
        self, 
        label: str, 
        url: Optional[str] = None, 
        callback: Optional[Callable] = None,
        active: bool = False,
        icon: Optional[str] = None
    ) -> None:
        """
        Add a breadcrumb to the trail.
        
        Args:
            label (str): The display label for the breadcrumb
            url (str, optional): The URL or path for the breadcrumb
            callback (callable, optional): Function to call when the breadcrumb is clicked
            active (bool): Whether this breadcrumb represents the current page
            icon (str, optional): Icon to display with the breadcrumb
        """
        breadcrumb = Breadcrumb(label, url, callback, active, icon)
        self.breadcrumbs.append(breadcrumb)
    
    def clear(self) -> None:
        """Clear all breadcrumbs from the trail."""
        self.breadcrumbs = []
    
    def render(self) -> None:
        """Render the breadcrumb trail in the Streamlit app."""
        if not self.breadcrumbs:
            return
        
        # Create container for breadcrumbs
        container_html = f"""
        <div style="{'; '.join([f'{k}: {v}' for k, v in self.container_style.items()])}">
        """
        
        # Add breadcrumbs with separators
        for i, breadcrumb in enumerate(self.breadcrumbs):
            # Determine style based on whether breadcrumb is active
            style = self.active_style if breadcrumb.active else self.breadcrumb_style
            style_str = '; '.join([f'{k}: {v}' for k, v in style.items()])
            
            # Add icon if provided
            icon_html = f'<i class="material-icons" style="font-size: 1rem; vertical-align: middle; margin-right: 0.2rem;">{breadcrumb.icon}</i>' if breadcrumb.icon else ''
            
            # Create breadcrumb HTML
            if breadcrumb.active:
                # Active breadcrumb is not clickable
                container_html += f'<span style="{style_str}">{icon_html}{breadcrumb.label}</span>'
            else:
                # Create a clickable breadcrumb with a unique key
                key = f"breadcrumb_{i}_{breadcrumb.label.replace(' ', '_').lower()}"
                container_html += f'<a href="#" id="{key}" style="{style_str}">{icon_html}{breadcrumb.label}</a>'
            
            # Add separator if not the last breadcrumb
            if i < len(self.breadcrumbs) - 1:
                container_html += f'<span style="margin: 0 0.3rem;">{self.separator}</span>'
        
        container_html += "</div>"
        
        # Render the HTML
        st.markdown(container_html, unsafe_allow_html=True)
        
        # Set up callbacks for clickable breadcrumbs
        for i, breadcrumb in enumerate(self.breadcrumbs):
            if not breadcrumb.active and (breadcrumb.url or breadcrumb.callback):
                key = f"breadcrumb_{i}_{breadcrumb.label.replace(' ', '_').lower()}"
                
                # Use JavaScript to handle clicks
                js = f"""
                <script>
                document.getElementById("{key}").addEventListener("click", function(e) {{
                    e.preventDefault();
                    {f'window.location.href = "{breadcrumb.url}";' if breadcrumb.url else ''}
                    {f'parent.postMessage({{type: "streamlit:callback", key: "{key}"}}, "*");' if breadcrumb.callback else ''}
                }});
                </script>
                """
                st.markdown(js, unsafe_allow_html=True)

def create_breadcrumb_trail(
    paths: List[Dict[str, Union[str, bool, Callable, None]]],
    separator: str = ">",
    container_style: Optional[Dict] = None,
    breadcrumb_style: Optional[Dict] = None,
    active_style: Optional[Dict] = None
) -> None:
    """
    Create and render a breadcrumb trail from a list of path dictionaries.
    
    Args:
        paths (List[Dict]): List of dictionaries with keys 'label', 'url' (optional),
                           'callback' (optional), 'active' (optional), and 'icon' (optional)
        separator (str): The separator to display between breadcrumbs
        container_style (Dict, optional): CSS styles for the breadcrumb container
        breadcrumb_style (Dict, optional): CSS styles for individual breadcrumbs
        active_style (Dict, optional): CSS styles for the active breadcrumb
    """
    trail = BreadcrumbTrail(separator, container_style, breadcrumb_style, active_style)
    
    for path in paths:
        label = path.get('label', '')
        url = path.get('url')
        callback = path.get('callback')
        active = path.get('active', False)
        icon = path.get('icon')
        
        trail.add_breadcrumb(label, url, callback, active, icon)
    
    trail.render()

def add_breadcrumbs_to_session(
    paths: List[Dict[str, Union[str, bool, Callable, None]]],
    key: str = "breadcrumbs"
) -> None:
    """
    Add breadcrumb paths to the session state for persistent navigation.
    
    Args:
        paths (List[Dict]): List of dictionaries with breadcrumb information
        key (str): Key to use in session state for storing breadcrumbs
    """
    if key not in st.session_state:
        st.session_state[key] = []
    
    st.session_state[key] = paths

def get_breadcrumbs_from_session(key: str = "breadcrumbs") -> List[Dict]:
    """
    Get breadcrumb paths from the session state.
    
    Args:
        key (str): Key used in session state for storing breadcrumbs
        
    Returns:
        List[Dict]: List of dictionaries with breadcrumb information
    """
    return st.session_state.get(key, [])

def render_breadcrumbs_from_session(
    key: str = "breadcrumbs",
    separator: str = ">",
    container_style: Optional[Dict] = None,
    breadcrumb_style: Optional[Dict] = None,
    active_style: Optional[Dict] = None
) -> None:
    """
    Render breadcrumbs from the session state.
    
    Args:
        key (str): Key used in session state for storing breadcrumbs
        separator (str): The separator to display between breadcrumbs
        container_style (Dict, optional): CSS styles for the breadcrumb container
        breadcrumb_style (Dict, optional): CSS styles for individual breadcrumbs
        active_style (Dict, optional): CSS styles for the active breadcrumb
    """
    paths = get_breadcrumbs_from_session(key)
    if paths:
        create_breadcrumb_trail(paths, separator, container_style, breadcrumb_style, active_style)