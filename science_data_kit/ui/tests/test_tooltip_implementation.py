import streamlit as st
import pandas as pd
import numpy as np
from science_data_kit.ui.components.visualization_templates import create_bar_chart, render_visualization

def test_tooltip_functionality():
    """
    Test the tooltip functionality in the render_visualization function.
    """
    st.title("Tooltip Implementation Test")
    
    # Create a simple dataset
    data = pd.DataFrame({
        'Category': ['A', 'B', 'C', 'D', 'E'],
        'Value': [10, 25, 15, 30, 20]
    })
    
    # Create a bar chart
    img_data = create_bar_chart(
        data=data,
        x_column='Category',
        y_column='Value',
        title='Test Bar Chart',
        x_label='Category',
        y_label='Value'
    )
    
    st.subheader("Visualization with Tooltip")
    st.write("Hover over the chart to see the tooltip")
    
    # Render the visualization with a tooltip
    render_visualization(
        img_data=img_data,
        caption="Bar Chart with Tooltip",
        help="This is a test tooltip for the bar chart. It provides additional information about the visualization."
    )
    
    st.subheader("Visualization without Tooltip")
    
    # Render the visualization without a tooltip
    render_visualization(
        img_data=img_data,
        caption="Bar Chart without Tooltip"
    )
    
    # Test user preference toggle
    st.subheader("Toggle Tooltip Preference")
    
    # Get current preference
    show_tooltips = st.session_state.get("user_preferences", {}).get("show_tooltips", True)
    
    # Create a toggle
    new_preference = st.checkbox("Show Tooltips", value=show_tooltips, key="tooltip_toggle")
    
    # Update preference if changed
    if new_preference != show_tooltips:
        if "user_preferences" not in st.session_state:
            st.session_state["user_preferences"] = {}
        st.session_state["user_preferences"]["show_tooltips"] = new_preference
        st.experimental_rerun()
    
    st.write("Current tooltip preference:", show_tooltips)

if __name__ == "__main__":
    test_tooltip_functionality()