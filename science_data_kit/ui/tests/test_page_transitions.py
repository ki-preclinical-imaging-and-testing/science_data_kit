"""
Test script for the Page Transitions component.

This script demonstrates the functionality of the page transitions component
by showing various transition effects, loading indicators, and state preservation.

Run this script with:
streamlit run science_data_kit/ui/tests/test_page_transitions.py
"""

import streamlit as st
import sys
import os
import time
import pandas as pd

# Add the parent directory to the path to import the components
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from science_data_kit.ui.components.page_transitions import (
    initialize_page_transitions,
    show_loading_spinner,
    hide_loading_spinner,
    show_progress_bar,
    complete_progress_bar,
    show_skeleton_screen,
    hide_skeleton_screen,
    preserve_state,
    get_preserved_state,
    clear_preserved_state,
    with_transition,
    lazy_load
)

def main():
    """Main function to demonstrate the page transitions component."""
    st.set_page_config(page_title="Page Transitions Test", layout="wide")
    
    # Initialize page transitions
    initialize_page_transitions()
    
    st.title("Page Transitions Component Test")
    st.write("This page demonstrates the functionality of the page transitions component.")
    
    # Create tabs for different features
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Fade Effects",
        "Loading Indicators",
        "Skeleton Screens",
        "State Preservation",
        "Practical Examples"
    ])
    
    with tab1:
        st.header("Fade Effects")
        st.write("""
        Page content fades in when loaded and fades out when navigating away.
        
        These effects are applied automatically to all pages that use the page transitions component.
        Try clicking on different tabs to see the fade effect in action.
        """)
        
        st.subheader("How It Works")
        st.code("""
        # In your Streamlit app
        from science_data_kit.ui.components.page_transitions import initialize_page_transitions
        
        # Initialize page transitions
        initialize_page_transitions()
        
        # The rest of your app code...
        """)
    
    with tab2:
        st.header("Loading Indicators")
        st.write("""
        Loading indicators provide visual feedback during long-running operations.
        The page transitions component provides two types of loading indicators:
        - Loading spinners
        - Progress bars
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Loading Spinner")
            if st.button("Show Loading Spinner", key="spinner_demo"):
                spinner = show_loading_spinner()
                progress_text = st.empty()
                
                for i in range(5):
                    progress_text.write(f"Loading... {i+1}/5")
                    time.sleep(0.5)
                
                hide_loading_spinner(spinner)
                progress_text.write("Loading complete!")
            
            st.code("""
            # Show a loading spinner
            spinner = show_loading_spinner()
            
            # Do some work...
            
            # Hide the spinner when done
            hide_loading_spinner(spinner)
            """)
        
        with col2:
            st.subheader("Progress Bar")
            if st.button("Show Progress Bar", key="progress_demo"):
                show_progress_bar()
                progress_text = st.empty()
                
                for i in range(5):
                    progress_text.write(f"Loading... {i+1}/5")
                    time.sleep(0.5)
                
                complete_progress_bar()
                progress_text.write("Loading complete!")
            
            st.code("""
            # Show a progress bar
            show_progress_bar()
            
            # Do some work...
            
            # Complete the progress bar when done
            complete_progress_bar()
            """)
    
    with tab3:
        st.header("Skeleton Screens")
        st.write("""
        Skeleton screens provide a preview of the content structure while it loads.
        They give users a better experience than spinners by showing the layout of the content before it's fully loaded.
        """)
        
        if st.button("Show Skeleton Screen", key="skeleton_demo"):
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
            st.button("Example Button", key="example_button")
        
        st.subheader("How It Works")
        st.code("""
        # Show a skeleton screen
        skeleton = show_skeleton_screen(
            num_text_lines=3,
            show_title=True,
            show_image=True,
            show_button=True
        )
        
        # Do some work...
        
        # Hide the skeleton screen when done
        hide_skeleton_screen(skeleton)
        
        # Show the actual content
        st.subheader("Actual Content")
        st.image("image.png")
        st.write("This is the actual content.")
        """)
    
    with tab4:
        st.header("State Preservation")
        st.write("""
        The page transitions component provides utilities for preserving state during page transitions.
        This is useful for maintaining context when navigating between pages.
        """)
        
        # Input field
        user_input = st.text_input("Enter some text to preserve across page transitions", key="state_input")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Save button
            if st.button("Save State", key="save_state"):
                preserve_state("user_input", user_input)
                st.success(f"State saved: '{user_input}'")
        
        with col2:
            # Load button
            if st.button("Load State", key="load_state"):
                loaded_value = get_preserved_state("user_input", "No saved state found")
                st.info(f"Loaded state: '{loaded_value}'")
        
        with col3:
            # Clear button
            if st.button("Clear State", key="clear_state"):
                clear_preserved_state("user_input")
                st.warning("State cleared")
        
        st.subheader("How It Works")
        st.code("""
        # Save state
        preserve_state("user_input", user_input)
        
        # Get preserved state
        loaded_value = get_preserved_state("user_input", "Default value")
        
        # Clear preserved state
        clear_preserved_state("user_input")
        """)
    
    with tab5:
        st.header("Practical Examples")
        st.write("""
        The page transitions component provides utilities that can be combined for practical use cases.
        Here are some examples:
        """)
        
        st.subheader("Decorator for Transitions")
        st.write("The `with_transition` decorator adds loading indicators to a function.")
        
        @with_transition
        def expensive_operation():
            time.sleep(2)
            return pd.DataFrame({
                "A": [1, 2, 3, 4, 5],
                "B": [10, 20, 30, 40, 50]
            })
        
        if st.button("Run Operation with Transition", key="decorator_demo"):
            df = expensive_operation()
            st.dataframe(df)
        
        st.code("""
        @with_transition
        def expensive_operation():
            # Do some expensive work...
            time.sleep(2)
            return pd.DataFrame(...)
        
        # Call the function
        df = expensive_operation()
        """)
        
        st.subheader("Lazy Loading")
        st.write("The `lazy_load` function shows a placeholder while content is loading.")
        
        def content_function():
            st.subheader("Lazy Loaded Content")
            st.write("This content was lazy loaded with a skeleton screen placeholder.")
            st.dataframe(pd.DataFrame({
                "Name": ["Alice", "Bob", "Charlie"],
                "Age": [25, 30, 35],
                "City": ["New York", "San Francisco", "Chicago"]
            }))
        
        if st.button("Lazy Load Content", key="lazy_load_demo"):
            lazy_load(content_function, delay=2)
        
        st.code("""
        def content_function():
            st.subheader("Lazy Loaded Content")
            st.write("This content was lazy loaded.")
            st.dataframe(...)
        
        # Lazy load the content
        lazy_load(content_function)
        """)

if __name__ == "__main__":
    main()