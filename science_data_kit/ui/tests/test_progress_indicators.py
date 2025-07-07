"""
Test script for Progress Indicators Component

This script demonstrates and validates the progress indicators component
for multi-step workflows in the Science Data Kit.
"""

import streamlit as st
import sys
import os
import time
from typing import List, Dict, Any

# Add the parent directory to the path so we can import the components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.progress_indicators import (
    ProgressIndicatorType,
    create_progress_indicator,
    add_progress_to_session,
    update_progress_in_session,
    render_progress_from_session
)

def main():
    """Main function to demonstrate progress indicators."""
    st.title("Progress Indicators Demo")
    st.write("This demo showcases different types of progress indicators for multi-step workflows.")
    
    # Initialize session state for tracking demo state
    if "demo_state" not in st.session_state:
        st.session_state.demo_state = {
            "current_demo": "linear",
            "current_step": 0,
            "steps_completed": 0
        }
    
    # Sidebar for navigation between demos
    st.sidebar.title("Navigation")
    demo_options = {
        "linear": "Linear Progress Bar",
        "circular": "Circular Progress Indicator",
        "step": "Step-based Progress Indicator",
        "dot": "Dot-based Progress Indicator",
        "interactive": "Interactive Workflow Demo"
    }
    
    selected_demo = st.sidebar.radio(
        "Select Demo",
        list(demo_options.keys()),
        format_func=lambda x: demo_options[x],
        index=list(demo_options.keys()).index(st.session_state.demo_state["current_demo"])
    )
    
    st.session_state.demo_state["current_demo"] = selected_demo
    
    # Display the selected demo
    if selected_demo == "linear":
        demo_linear_progress()
    elif selected_demo == "circular":
        demo_circular_progress()
    elif selected_demo == "step":
        demo_step_progress()
    elif selected_demo == "dot":
        demo_dot_progress()
    elif selected_demo == "interactive":
        demo_interactive_workflow()
    
    # Add documentation section
    st.markdown("---")
    st.header("Documentation")
    st.markdown("""
    ## Progress Indicators Component
    
    The Progress Indicators component provides standardized progress indicator components for use across the application
    to show progress in multi-step workflows.
    
    ### Types of Progress Indicators
    
    1. **Linear Progress Bar**: A simple horizontal progress bar showing percentage completion
    2. **Circular Progress Indicator**: A circular progress indicator showing percentage completion
    3. **Step-based Progress Indicator**: Numbered steps with labels and connecting lines
    4. **Dot-based Progress Indicator**: Dots connected by lines with labels
    
    ### Usage
    
    ```python
    from science_data_kit.ui.components.progress_indicators import create_progress_indicator, ProgressIndicatorType
    
    # Define your steps
    steps = [
        {"label": "Step 1", "description": "First step", "completed": True, "current": False},
        {"label": "Step 2", "description": "Second step", "completed": False, "current": True},
        {"label": "Step 3", "description": "Third step", "completed": False, "current": False}
    ]
    
    # Create and render a progress indicator
    create_progress_indicator(
        steps=steps,
        indicator_type=ProgressIndicatorType.STEP,
        show_labels=True,
        show_descriptions=True,
        show_percentage=True
    )
    ```
    
    ### Session State Integration
    
    For persistent tracking across pages, use the session state integration:
    
    ```python
    from science_data_kit.ui.components.progress_indicators import (
        add_progress_to_session,
        update_progress_in_session,
        render_progress_from_session
    )
    
    # Add progress steps to session state
    add_progress_to_session(steps, key="my_workflow_progress")
    
    # Update a specific step
    update_progress_in_session(1, completed=True, current=False, key="my_workflow_progress")
    
    # Render progress from session state
    render_progress_from_session(
        key="my_workflow_progress",
        indicator_type=ProgressIndicatorType.STEP
    )
    ```
    """)

def demo_linear_progress():
    """Demonstrate linear progress bar."""
    st.header("Linear Progress Bar")
    st.write("A simple horizontal progress bar showing percentage completion.")
    
    # Create steps with varying completion states
    steps = create_demo_steps(4)
    
    # Show examples with different completion states
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("25% Complete")
        steps_25 = steps.copy()
        steps_25[0]["completed"] = True
        create_progress_indicator(
            steps=steps_25,
            indicator_type=ProgressIndicatorType.LINEAR
        )
    
    with col2:
        st.subheader("50% Complete")
        steps_50 = steps.copy()
        steps_50[0]["completed"] = True
        steps_50[1]["completed"] = True
        create_progress_indicator(
            steps=steps_50,
            indicator_type=ProgressIndicatorType.LINEAR
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("75% Complete")
        steps_75 = steps.copy()
        steps_75[0]["completed"] = True
        steps_75[1]["completed"] = True
        steps_75[2]["completed"] = True
        create_progress_indicator(
            steps=steps_75,
            indicator_type=ProgressIndicatorType.LINEAR
        )
    
    with col4:
        st.subheader("100% Complete")
        steps_100 = steps.copy()
        for step in steps_100:
            step["completed"] = True
        create_progress_indicator(
            steps=steps_100,
            indicator_type=ProgressIndicatorType.LINEAR
        )
    
    # Show example with custom styling
    st.subheader("Custom Styling")
    create_progress_indicator(
        steps=steps_50,
        indicator_type=ProgressIndicatorType.LINEAR,
        container_style={"background-color": "#f5f5f5", "padding": "1rem", "border-radius": "8px"}
    )

def demo_circular_progress():
    """Demonstrate circular progress indicator."""
    st.header("Circular Progress Indicator")
    st.write("A circular progress indicator showing percentage completion.")
    
    # Create steps with varying completion states
    steps = create_demo_steps(5)
    
    # Show examples with different completion states
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("20% Complete")
        steps_20 = steps.copy()
        steps_20[0]["completed"] = True
        create_progress_indicator(
            steps=steps_20,
            indicator_type=ProgressIndicatorType.CIRCULAR
        )
    
    with col2:
        st.subheader("60% Complete")
        steps_60 = steps.copy()
        steps_60[0]["completed"] = True
        steps_60[1]["completed"] = True
        steps_60[2]["completed"] = True
        create_progress_indicator(
            steps=steps_60,
            indicator_type=ProgressIndicatorType.CIRCULAR
        )
    
    with col3:
        st.subheader("100% Complete")
        steps_100 = steps.copy()
        for step in steps_100:
            step["completed"] = True
        create_progress_indicator(
            steps=steps_100,
            indicator_type=ProgressIndicatorType.CIRCULAR
        )

def demo_step_progress():
    """Demonstrate step-based progress indicator."""
    st.header("Step-based Progress Indicator")
    st.write("Numbered steps with labels and connecting lines.")
    
    # Create steps with varying completion states
    steps = create_demo_steps(4, with_descriptions=True)
    
    # Show example with current step
    st.subheader("Current Step Highlighted")
    steps_current = steps.copy()
    steps_current[0]["completed"] = True
    steps_current[1]["current"] = True
    create_progress_indicator(
        steps=steps_current,
        indicator_type=ProgressIndicatorType.STEP,
        show_descriptions=True
    )
    
    # Show example with more completed steps
    st.subheader("Multiple Steps Completed")
    steps_multi = steps.copy()
    steps_multi[0]["completed"] = True
    steps_multi[1]["completed"] = True
    steps_multi[2]["current"] = True
    create_progress_indicator(
        steps=steps_multi,
        indicator_type=ProgressIndicatorType.STEP,
        show_descriptions=True
    )
    
    # Show example with custom styling
    st.subheader("Custom Styling")
    custom_step_style = {
        "border-radius": "20px",
        "padding": "0.7rem"
    }
    custom_completed_style = {
        "background-color": "#28a745",
        "border-radius": "20px",
        "padding": "0.7rem"
    }
    custom_current_style = {
        "background-color": "#007bff",
        "border-radius": "20px",
        "padding": "0.7rem"
    }
    create_progress_indicator(
        steps=steps_multi,
        indicator_type=ProgressIndicatorType.STEP,
        step_style=custom_step_style,
        completed_style=custom_completed_style,
        current_style=custom_current_style,
        show_descriptions=True
    )

def demo_dot_progress():
    """Demonstrate dot-based progress indicator."""
    st.header("Dot-based Progress Indicator")
    st.write("Dots connected by lines with labels.")
    
    # Create steps with varying completion states
    steps = create_demo_steps(5)
    
    # Show example with current step
    st.subheader("Current Step Highlighted")
    steps_current = steps.copy()
    steps_current[0]["completed"] = True
    steps_current[1]["current"] = True
    create_progress_indicator(
        steps=steps_current,
        indicator_type=ProgressIndicatorType.DOT
    )
    
    # Show example with more completed steps
    st.subheader("Multiple Steps Completed")
    steps_multi = steps.copy()
    steps_multi[0]["completed"] = True
    steps_multi[1]["completed"] = True
    steps_multi[2]["completed"] = True
    steps_multi[3]["current"] = True
    create_progress_indicator(
        steps=steps_multi,
        indicator_type=ProgressIndicatorType.DOT
    )
    
    # Show example without labels
    st.subheader("Without Labels")
    create_progress_indicator(
        steps=steps_multi,
        indicator_type=ProgressIndicatorType.DOT,
        show_labels=False
    )

def demo_interactive_workflow():
    """Demonstrate an interactive workflow with progress tracking."""
    st.header("Interactive Workflow Demo")
    st.write("This demo shows how to use progress indicators in an interactive multi-step workflow.")
    
    # Define the workflow steps
    workflow_steps = [
        {"label": "Upload Data", "description": "Upload your dataset", "completed": False, "current": False},
        {"label": "Configure", "description": "Configure analysis parameters", "completed": False, "current": False},
        {"label": "Process", "description": "Process the data", "completed": False, "current": False},
        {"label": "Visualize", "description": "Visualize the results", "completed": False, "current": False},
        {"label": "Export", "description": "Export the results", "completed": False, "current": False}
    ]
    
    # Initialize workflow state in session state if not already present
    if "workflow_state" not in st.session_state:
        st.session_state.workflow_state = {
            "current_step": 0,
            "steps_completed": 0,
            "data_uploaded": False,
            "configuration_done": False,
            "processing_done": False,
            "visualization_done": False,
            "export_done": False
        }
    
    # Update workflow steps based on current state
    current_step = st.session_state.workflow_state["current_step"]
    for i, step in enumerate(workflow_steps):
        if i < current_step:
            step["completed"] = True
            step["current"] = False
        elif i == current_step:
            step["completed"] = False
            step["current"] = True
        else:
            step["completed"] = False
            step["current"] = False
    
    # Add workflow steps to session state
    add_progress_to_session(workflow_steps, key="workflow_steps")
    
    # Display progress indicator
    st.subheader("Workflow Progress")
    render_progress_from_session(
        key="workflow_steps",
        indicator_type=ProgressIndicatorType.STEP,
        show_descriptions=True
    )
    
    # Display the current step content
    st.subheader(f"Step {current_step + 1}: {workflow_steps[current_step]['label']}")
    st.write(workflow_steps[current_step]['description'])
    
    # Step-specific content
    if current_step == 0:  # Upload Data
        display_upload_step()
    elif current_step == 1:  # Configure
        display_configure_step()
    elif current_step == 2:  # Process
        display_process_step()
    elif current_step == 3:  # Visualize
        display_visualize_step()
    elif current_step == 4:  # Export
        display_export_step()
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if current_step > 0:
            if st.button("Previous Step"):
                st.session_state.workflow_state["current_step"] -= 1
                st.experimental_rerun()
    
    with col2:
        if current_step < len(workflow_steps) - 1:
            # Check if current step is completed before allowing to proceed
            step_completed = False
            if current_step == 0:
                step_completed = st.session_state.workflow_state["data_uploaded"]
            elif current_step == 1:
                step_completed = st.session_state.workflow_state["configuration_done"]
            elif current_step == 2:
                step_completed = st.session_state.workflow_state["processing_done"]
            elif current_step == 3:
                step_completed = st.session_state.workflow_state["visualization_done"]
            
            next_button = st.button("Next Step", disabled=not step_completed)
            if next_button:
                st.session_state.workflow_state["current_step"] += 1
                st.session_state.workflow_state["steps_completed"] = max(
                    st.session_state.workflow_state["steps_completed"],
                    current_step + 1
                )
                st.experimental_rerun()
        elif current_step == len(workflow_steps) - 1 and st.session_state.workflow_state["export_done"]:
            if st.button("Restart Workflow"):
                # Reset workflow state
                st.session_state.workflow_state = {
                    "current_step": 0,
                    "steps_completed": 0,
                    "data_uploaded": False,
                    "configuration_done": False,
                    "processing_done": False,
                    "visualization_done": False,
                    "export_done": False
                }
                st.experimental_rerun()

def display_upload_step():
    """Display content for the upload data step."""
    st.write("Please upload your dataset:")
    
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "json"])
    
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        st.session_state.workflow_state["data_uploaded"] = True
    else:
        st.session_state.workflow_state["data_uploaded"] = False

def display_configure_step():
    """Display content for the configure step."""
    st.write("Configure your analysis parameters:")
    
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Statistical Analysis", "Machine Learning", "Data Visualization"]
    )
    
    if analysis_type == "Statistical Analysis":
        st.selectbox("Statistical Test", ["T-Test", "ANOVA", "Chi-Square", "Correlation"])
        st.slider("Significance Level", 0.01, 0.10, 0.05, 0.01)
    elif analysis_type == "Machine Learning":
        st.selectbox("Algorithm", ["Linear Regression", "Random Forest", "Neural Network"])
        st.slider("Train/Test Split", 0.1, 0.5, 0.2, 0.05)
    elif analysis_type == "Data Visualization":
        st.selectbox("Chart Type", ["Bar Chart", "Scatter Plot", "Line Chart", "Pie Chart"])
        st.color_picker("Primary Color", "#1f77b4")
    
    if st.button("Save Configuration"):
        st.success("Configuration saved successfully!")
        st.session_state.workflow_state["configuration_done"] = True

def display_process_step():
    """Display content for the process step."""
    st.write("Processing your data...")
    
    if st.button("Start Processing"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(101):
            progress_bar.progress(i)
            status_text.text(f"Processing: {i}% complete")
            time.sleep(0.05)
        
        st.success("Data processing completed successfully!")
        st.session_state.workflow_state["processing_done"] = True

def display_visualize_step():
    """Display content for the visualize step."""
    st.write("Visualizing your results:")
    
    chart_type = st.selectbox(
        "Select Visualization",
        ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"]
    )
    
    # Display a sample chart based on selection
    if chart_type == "Bar Chart":
        st.bar_chart({"Data": [3, 1, 4, 1, 5, 9, 2, 6]})
    elif chart_type == "Line Chart":
        st.line_chart({"Data": [3, 1, 4, 1, 5, 9, 2, 6]})
    elif chart_type == "Scatter Plot":
        st.scatter_chart({"Data": [3, 1, 4, 1, 5, 9, 2, 6]})
    elif chart_type == "Pie Chart":
        st.write("Pie chart visualization (placeholder)")
    
    if st.button("Save Visualization"):
        st.success("Visualization saved successfully!")
        st.session_state.workflow_state["visualization_done"] = True

def display_export_step():
    """Display content for the export step."""
    st.write("Export your results:")
    
    export_format = st.selectbox(
        "Export Format",
        ["CSV", "Excel", "JSON", "PDF", "PNG"]
    )
    
    include_options = st.multiselect(
        "Include in Export",
        ["Raw Data", "Processed Data", "Visualizations", "Analysis Report"],
        ["Processed Data", "Visualizations"]
    )
    
    if st.button("Export Results"):
        st.success(f"Results exported successfully as {export_format}!")
        st.balloons()
        st.session_state.workflow_state["export_done"] = True

def create_demo_steps(count: int, with_descriptions: bool = False) -> List[Dict[str, Any]]:
    """
    Create a list of demo steps.
    
    Args:
        count (int): Number of steps to create
        with_descriptions (bool): Whether to include descriptions
        
    Returns:
        List[Dict[str, Any]]: List of step dictionaries
    """
    steps = []
    for i in range(count):
        step = {
            "label": f"Step {i+1}",
            "completed": False,
            "current": False
        }
        if with_descriptions:
            step["description"] = f"Description for Step {i+1}"
        steps.append(step)
    return steps

if __name__ == "__main__":
    main()