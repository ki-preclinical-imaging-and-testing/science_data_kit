"""
Page Transitions for Science Data Kit

This module provides utilities for creating smooth transitions between pages
in the Science Data Kit. It includes functions for fade effects, loading indicators,
and state preservation during page transitions.
"""

import streamlit as st
import time
from typing import Dict, Any, Optional, Callable, List
import json
import base64

def initialize_page_transitions() -> None:
    """
    Initialize page transitions for the application.
    
    This function adds necessary CSS and JavaScript for smooth page transitions.
    """
    # Add CSS for transitions
    css = """
    <style>
    /* Fade transition */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(-10px); }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-in-out forwards;
    }
    
    .fade-out {
        animation: fadeOut 0.3s ease-in-out forwards;
    }
    
    /* Loading indicators */
    .loading-spinner {
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 3px solid rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        border-top-color: #09f;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .progress-bar-container {
        width: 100%;
        height: 4px;
        background-color: #f0f0f0;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 1000;
    }
    
    .progress-bar {
        height: 100%;
        background-color: #09f;
        width: 0%;
        transition: width 0.3s ease-in-out;
    }
    
    /* Skeleton screens */
    .skeleton {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: 4px;
        height: 20px;
        margin-bottom: 8px;
    }
    
    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    .skeleton-text {
        width: 100%;
    }
    
    .skeleton-title {
        width: 70%;
        height: 30px;
    }
    
    .skeleton-image {
        width: 100%;
        height: 200px;
    }
    
    .skeleton-button {
        width: 120px;
        height: 40px;
    }
    </style>
    """
    
    # Add JavaScript for transitions
    js = """
    <script>
    // Function to handle page transitions
    function handlePageTransition() {
        // Store current scroll position
        sessionStorage.setItem('scrollPos', window.scrollY);
        
        // Add fade-out class to main content
        const main = document.querySelector('.main');
        if (main) {
            main.classList.add('fade-out');
        }
        
        // Show progress bar
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar-container';
        progressBar.innerHTML = '<div class="progress-bar" id="page-transition-progress"></div>';
        document.body.appendChild(progressBar);
        
        // Animate progress bar
        const bar = document.getElementById('page-transition-progress');
        let width = 0;
        const interval = setInterval(() => {
            if (width >= 90) {
                clearInterval(interval);
            } else {
                width += 5;
                bar.style.width = width + '%';
            }
        }, 50);
        
        // Store the interval ID to clear it when the page is fully loaded
        window._transitionInterval = interval;
    }
    
    // Function to handle page load completion
    function handlePageLoaded() {
        // Clear any existing transition interval
        if (window._transitionInterval) {
            clearInterval(window._transitionInterval);
            delete window._transitionInterval;
        }
        
        // Complete progress bar
        const bar = document.getElementById('page-transition-progress');
        if (bar) {
            bar.style.width = '100%';
            setTimeout(() => {
                const container = bar.parentNode;
                if (container) {
                    container.remove();
                }
            }, 300);
        }
        
        // Add fade-in class to main content
        const main = document.querySelector('.main');
        if (main) {
            main.classList.add('fade-in');
            setTimeout(() => {
                main.classList.remove('fade-in');
            }, 300);
        }
        
        // Restore scroll position if needed
        const scrollPos = sessionStorage.getItem('scrollPos');
        if (scrollPos && window.location.hash === '') {
            window.scrollTo(0, parseInt(scrollPos));
        }
    }
    
    // Add event listeners for page transitions
    document.addEventListener('DOMContentLoaded', () => {
        // Handle links for page transitions
        document.querySelectorAll('a').forEach(link => {
            if (link.href && link.href.startsWith(window.location.origin)) {
                link.addEventListener('click', () => {
                    handlePageTransition();
                });
            }
        });
        
        // Handle page load completion
        handlePageLoaded();
    });
    
    // Handle browser back/forward navigation
    window.addEventListener('popstate', () => {
        handlePageTransition();
    });
    </script>
    """
    
    # Add the CSS and JavaScript
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(js, unsafe_allow_html=True)
    
    # Add progress bar container for Streamlit operations
    progress_container = """
    <div id="streamlit-progress-container" style="display: none;">
        <div class="progress-bar-container">
            <div class="progress-bar" id="streamlit-progress-bar"></div>
        </div>
    </div>
    """
    st.markdown(progress_container, unsafe_allow_html=True)

def show_loading_spinner() -> None:
    """
    Display a loading spinner.
    
    This function shows a loading spinner while content is being loaded.
    """
    spinner_html = """
    <div style="display: flex; justify-content: center; margin: 20px 0;">
        <div class="loading-spinner"></div>
    </div>
    """
    spinner_container = st.empty()
    spinner_container.markdown(spinner_html, unsafe_allow_html=True)
    return spinner_container

def hide_loading_spinner(container) -> None:
    """
    Hide the loading spinner.
    
    Args:
        container: The container holding the spinner
    """
    container.empty()

def show_progress_bar(progress_id: str = "streamlit-progress-bar") -> None:
    """
    Show a progress bar for a long-running operation.
    
    Args:
        progress_id: The ID of the progress bar element
    """
    js = f"""
    <script>
    document.getElementById('streamlit-progress-container').style.display = 'block';
    const progressBar = document.getElementById('{progress_id}');
    let width = 0;
    const interval = setInterval(() => {{
        if (width >= 90) {{
            clearInterval(interval);
        }} else {{
            width += 2;
            progressBar.style.width = width + '%';
        }}
    }}, 100);
    window._progressInterval = interval;
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)

def complete_progress_bar(progress_id: str = "streamlit-progress-bar") -> None:
    """
    Complete the progress bar animation.
    
    Args:
        progress_id: The ID of the progress bar element
    """
    js = f"""
    <script>
    if (window._progressInterval) {{
        clearInterval(window._progressInterval);
        delete window._progressInterval;
    }}
    const progressBar = document.getElementById('{progress_id}');
    if (progressBar) {{
        progressBar.style.width = '100%';
        setTimeout(() => {{
            document.getElementById('streamlit-progress-container').style.display = 'none';
            progressBar.style.width = '0%';
        }}, 300);
    }}
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)

def show_skeleton_screen(
    num_text_lines: int = 5,
    show_title: bool = True,
    show_image: bool = False,
    show_button: bool = False
) -> None:
    """
    Show a skeleton screen while content is loading.
    
    Args:
        num_text_lines: Number of text line placeholders to show
        show_title: Whether to show a title placeholder
        show_image: Whether to show an image placeholder
        show_button: Whether to show a button placeholder
    """
    skeleton_html = "<div class='skeleton-container'>"
    
    if show_title:
        skeleton_html += "<div class='skeleton skeleton-title'></div>"
    
    if show_image:
        skeleton_html += "<div class='skeleton skeleton-image'></div>"
    
    for _ in range(num_text_lines):
        skeleton_html += "<div class='skeleton skeleton-text'></div>"
    
    if show_button:
        skeleton_html += "<div class='skeleton skeleton-button'></div>"
    
    skeleton_html += "</div>"
    
    skeleton_container = st.empty()
    skeleton_container.markdown(skeleton_html, unsafe_allow_html=True)
    return skeleton_container

def hide_skeleton_screen(container) -> None:
    """
    Hide the skeleton screen.
    
    Args:
        container: The container holding the skeleton screen
    """
    container.empty()

def preserve_state(key: str, value: Any) -> None:
    """
    Preserve state during page transitions.
    
    Args:
        key: The key to store the state under
        value: The value to store
    """
    # Convert value to JSON string
    if isinstance(value, (dict, list, str, int, float, bool)) or value is None:
        value_json = json.dumps(value)
    else:
        # For non-JSON serializable objects, convert to string
        value_json = json.dumps(str(value))
    
    # Encode as base64 to avoid issues with special characters
    value_b64 = base64.b64encode(value_json.encode()).decode()
    
    # Store in session state
    if 'page_transition_state' not in st.session_state:
        st.session_state.page_transition_state = {}
    
    st.session_state.page_transition_state[key] = value_b64

def get_preserved_state(key: str, default: Any = None) -> Any:
    """
    Get preserved state from a previous page.
    
    Args:
        key: The key the state was stored under
        default: Default value to return if the key doesn't exist
        
    Returns:
        The preserved state value, or the default if not found
    """
    if 'page_transition_state' not in st.session_state:
        return default
    
    if key not in st.session_state.page_transition_state:
        return default
    
    # Get base64 encoded value
    value_b64 = st.session_state.page_transition_state[key]
    
    try:
        # Decode from base64 and parse JSON
        value_json = base64.b64decode(value_b64.encode()).decode()
        value = json.loads(value_json)
        return value
    except:
        return default

def clear_preserved_state(key: Optional[str] = None) -> None:
    """
    Clear preserved state.
    
    Args:
        key: The specific key to clear, or None to clear all preserved state
    """
    if 'page_transition_state' not in st.session_state:
        return
    
    if key is None:
        st.session_state.page_transition_state = {}
    elif key in st.session_state.page_transition_state:
        del st.session_state.page_transition_state[key]

def with_transition(func: Callable) -> Callable:
    """
    Decorator to add page transition effects to a function.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function
    """
    def wrapper(*args, **kwargs):
        # Show loading indicators
        spinner = show_loading_spinner()
        show_progress_bar()
        
        # Execute the function
        result = func(*args, **kwargs)
        
        # Hide loading indicators
        hide_loading_spinner(spinner)
        complete_progress_bar()
        
        return result
    
    return wrapper

def lazy_load(
    content_function: Callable,
    placeholder_function: Optional[Callable] = None,
    delay: float = 0.1
) -> None:
    """
    Lazy load content with a placeholder.
    
    Args:
        content_function: Function that generates the actual content
        placeholder_function: Function that generates a placeholder (default: skeleton screen)
        delay: Artificial delay in seconds (for demonstration purposes)
    """
    # Create placeholder if not provided
    if placeholder_function is None:
        placeholder = show_skeleton_screen()
    else:
        placeholder = st.empty()
        placeholder_function(placeholder)
    
    # Add artificial delay (for demonstration purposes)
    time.sleep(delay)
    
    # Replace placeholder with actual content
    placeholder.empty()
    content_function()

# Example usage
if __name__ == "__main__":
    st.set_page_config(page_title="Page Transitions Demo", layout="wide")
    
    # Initialize page transitions
    initialize_page_transitions()
    
    st.title("Page Transitions Demo")
    st.write("This page demonstrates the page transitions component.")
    
    # Demo tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Fade Effects",
        "Loading Indicators",
        "Skeleton Screens",
        "State Preservation"
    ])
    
    with tab1:
        st.header("Fade Effects")
        st.write("Page content fades in when loaded and fades out when navigating away.")
        st.write("Try clicking on different tabs to see the fade effect.")
    
    with tab2:
        st.header("Loading Indicators")
        
        if st.button("Show Loading Spinner"):
            spinner = show_loading_spinner()
            progress_text = st.empty()
            
            for i in range(5):
                progress_text.write(f"Loading... {i+1}/5")
                time.sleep(0.5)
            
            hide_loading_spinner(spinner)
            progress_text.write("Loading complete!")
        
        if st.button("Show Progress Bar"):
            show_progress_bar()
            progress_text = st.empty()
            
            for i in range(5):
                progress_text.write(f"Loading... {i+1}/5")
                time.sleep(0.5)
            
            complete_progress_bar()
            progress_text.write("Loading complete!")
    
    with tab3:
        st.header("Skeleton Screens")
        
        if st.button("Show Skeleton Screen"):
            skeleton = show_skeleton_screen(
                num_text_lines=3,
                show_title=True,
                show_image=True,
                show_button=True
            )
            
            time.sleep(2)
            
            hide_skeleton_screen(skeleton)
            
            st.subheader("Actual Content")
            st.image("https://via.placeholder.com/600x200.png?text=Example+Image")
            st.write("This is the actual content that was loading.")
            st.write("Skeleton screens provide a better user experience than spinners.")
            st.write("They give users a preview of the content structure while it loads.")
            st.button("Example Button")
    
    with tab4:
        st.header("State Preservation")
        
        # Input field
        user_input = st.text_input("Enter some text to preserve across page transitions")
        
        # Save button
        if st.button("Save State"):
            preserve_state("user_input", user_input)
            st.success(f"State saved: '{user_input}'")
        
        # Load button
        if st.button("Load State"):
            loaded_value = get_preserved_state("user_input", "No saved state found")
            st.info(f"Loaded state: '{loaded_value}'")
        
        # Clear button
        if st.button("Clear State"):
            clear_preserved_state("user_input")
            st.warning("State cleared")