"""
Test script for assistive technologies compatibility in Science Data Kit.

This script tests the compatibility of various components with assistive technologies
such as screen readers and keyboard navigation. It includes tests for the user surveys
component, as well as other key components in the application.

Run this script with:
streamlit run science_data_kit/ui/tests/test_assistive_technologies.py
"""

import streamlit as st
import sys
import os
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple

# Add the parent directory to the path to import the components
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from science_data_kit.ui.components.screen_reader import (
    initialize_screen_reader_support,
    add_screen_reader_text,
    announce_page_load,
    add_aria_label,
    add_aria_live_region,
    update_live_region,
    make_table_accessible
)
from science_data_kit.ui.components.high_contrast import initialize_high_contrast_mode
from science_data_kit.ui.components.user_surveys import create_ui_experience_survey
from science_data_kit.ui.tests.accessibility_audit import AccessibilityAuditor

def test_keyboard_navigation() -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Test keyboard navigation for various components.
    
    Returns:
        Tuple containing:
        - Boolean indicating if all tests passed
        - List of issues found
    """
    st.subheader("Keyboard Navigation Test")
    st.write("This test checks if all interactive elements are accessible via keyboard.")
    
    issues = []
    all_passed = True
    
    # Create a test form with various interactive elements
    with st.form("keyboard_nav_test_form"):
        st.write("Try navigating through these elements using Tab key:")
        
        # Text input
        text_input = st.text_input("Text Input")
        
        # Select box
        select_option = st.selectbox(
            "Select Option",
            options=["Option 1", "Option 2", "Option 3"]
        )
        
        # Radio buttons
        radio_option = st.radio(
            "Radio Option",
            options=["Option A", "Option B", "Option C"]
        )
        
        # Checkbox
        checkbox_value = st.checkbox("Checkbox Option")
        
        # Slider
        slider_value = st.slider("Slider", min_value=0, max_value=100, value=50)
        
        # Submit button
        submit_button = st.form_submit_button("Submit Form")
    
    # Test results
    if submit_button:
        st.success("Form submitted successfully! All elements were keyboard accessible.")
        
        # Record form values for verification
        st.write("Form values:")
        st.json({
            "text_input": text_input,
            "select_option": select_option,
            "radio_option": radio_option,
            "checkbox_value": checkbox_value,
            "slider_value": slider_value
        })
    
    # Manual verification section
    st.write("### Manual Verification")
    st.write("Please verify the following:")
    
    tab_order_ok = st.checkbox("Tab order is logical and follows visual layout", key="tab_order")
    focus_visible = st.checkbox("Focus indicator is clearly visible on all elements", key="focus_visible")
    no_keyboard_traps = st.checkbox("No keyboard traps (can navigate away from all elements)", key="no_traps")
    all_interactive = st.checkbox("All interactive elements are reachable via keyboard", key="all_interactive")
    
    if st.button("Record Keyboard Navigation Results"):
        if not tab_order_ok:
            issues.append({
                "component": "Keyboard Navigation",
                "issue": "Tab order does not follow a logical sequence",
                "severity": "High"
            })
            all_passed = False
            
        if not focus_visible:
            issues.append({
                "component": "Keyboard Navigation",
                "issue": "Focus indicator not clearly visible on some elements",
                "severity": "High"
            })
            all_passed = False
            
        if not no_keyboard_traps:
            issues.append({
                "component": "Keyboard Navigation",
                "issue": "Keyboard traps detected - unable to navigate away from some elements",
                "severity": "Critical"
            })
            all_passed = False
            
        if not all_interactive:
            issues.append({
                "component": "Keyboard Navigation",
                "issue": "Some interactive elements not reachable via keyboard",
                "severity": "Critical"
            })
            all_passed = False
            
        if all_passed:
            st.success("All keyboard navigation tests passed!")
        else:
            st.error(f"Found {len(issues)} keyboard navigation issues.")
            
    return all_passed, issues

def test_screen_reader_compatibility() -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Test screen reader compatibility for various components.
    
    Returns:
        Tuple containing:
        - Boolean indicating if all tests passed
        - List of issues found
    """
    st.subheader("Screen Reader Compatibility Test")
    st.write("This test checks if components are properly announced by screen readers.")
    
    issues = []
    all_passed = True
    
    # Add screen reader only text
    st.markdown(add_screen_reader_text("This text is only visible to screen readers."), unsafe_allow_html=True)
    
    # Create a table with accessibility enhancements
    st.write("### Accessible Table Example")
    
    data = {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "Occupation": ["Engineer", "Designer", "Manager"]
    }
    df = pd.DataFrame(data)
    st.table(df)
    
    # Add ARIA live region for dynamic content
    add_aria_live_region("screen_reader_test_region")
    
    if st.button("Announce Dynamic Content"):
        update_live_region("Dynamic content has been updated. New information is available.", "screen_reader_test_region")
        st.write("An announcement was made to screen readers.")
    
    # Manual verification section
    st.write("### Manual Verification")
    st.write("Please verify the following with a screen reader:")
    
    headings_announced = st.checkbox("Headings are properly announced", key="headings")
    form_labels_announced = st.checkbox("Form labels are properly announced", key="form_labels")
    table_announced = st.checkbox("Table content is properly announced", key="table")
    live_regions_work = st.checkbox("ARIA live regions announce dynamic content", key="live_regions")
    images_have_alt = st.checkbox("Images have appropriate alt text", key="images_alt")
    
    if st.button("Record Screen Reader Results"):
        if not headings_announced:
            issues.append({
                "component": "Screen Reader Compatibility",
                "issue": "Headings are not properly announced by screen readers",
                "severity": "High"
            })
            all_passed = False
            
        if not form_labels_announced:
            issues.append({
                "component": "Screen Reader Compatibility",
                "issue": "Form labels are not properly announced by screen readers",
                "severity": "High"
            })
            all_passed = False
            
        if not table_announced:
            issues.append({
                "component": "Screen Reader Compatibility",
                "issue": "Table content is not properly announced by screen readers",
                "severity": "High"
            })
            all_passed = False
            
        if not live_regions_work:
            issues.append({
                "component": "Screen Reader Compatibility",
                "issue": "ARIA live regions do not announce dynamic content",
                "severity": "Medium"
            })
            all_passed = False
            
        if not images_have_alt:
            issues.append({
                "component": "Screen Reader Compatibility",
                "issue": "Images do not have appropriate alt text",
                "severity": "High"
            })
            all_passed = False
            
        if all_passed:
            st.success("All screen reader compatibility tests passed!")
        else:
            st.error(f"Found {len(issues)} screen reader compatibility issues.")
            
    return all_passed, issues

def test_user_surveys_accessibility() -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Test accessibility of the user surveys component.
    
    Returns:
        Tuple containing:
        - Boolean indicating if all tests passed
        - List of issues found
    """
    st.subheader("User Surveys Accessibility Test")
    st.write("This test checks if the user surveys component is accessible to assistive technologies.")
    
    issues = []
    all_passed = True
    
    # Show a sample survey
    if st.button("Show Sample Survey"):
        ui_survey = create_ui_experience_survey()
        survey_data = ui_survey.display()
        
        if survey_data:
            st.write("Survey data collected:")
            st.json(survey_data)
    
    # Manual verification section
    st.write("### Manual Verification")
    st.write("Please verify the following for the user surveys component:")
    
    survey_keyboard_nav = st.checkbox("Survey is fully navigable via keyboard", key="survey_keyboard")
    survey_screen_reader = st.checkbox("Survey elements are properly announced by screen readers", key="survey_sr")
    required_fields = st.checkbox("Required fields are properly indicated to screen readers", key="required_fields")
    error_messages = st.checkbox("Error messages are announced by screen readers", key="error_messages")
    logical_structure = st.checkbox("Survey has a logical structure and tab order", key="logical_structure")
    
    if st.button("Record User Surveys Accessibility Results"):
        if not survey_keyboard_nav:
            issues.append({
                "component": "User Surveys",
                "issue": "Survey is not fully navigable via keyboard",
                "severity": "Critical"
            })
            all_passed = False
            
        if not survey_screen_reader:
            issues.append({
                "component": "User Surveys",
                "issue": "Survey elements are not properly announced by screen readers",
                "severity": "High"
            })
            all_passed = False
            
        if not required_fields:
            issues.append({
                "component": "User Surveys",
                "issue": "Required fields are not properly indicated to screen readers",
                "severity": "High"
            })
            all_passed = False
            
        if not error_messages:
            issues.append({
                "component": "User Surveys",
                "issue": "Error messages are not announced by screen readers",
                "severity": "High"
            })
            all_passed = False
            
        if not logical_structure:
            issues.append({
                "component": "User Surveys",
                "issue": "Survey does not have a logical structure and tab order",
                "severity": "Medium"
            })
            all_passed = False
            
        if all_passed:
            st.success("All user surveys accessibility tests passed!")
        else:
            st.error(f"Found {len(issues)} user surveys accessibility issues.")
            
    return all_passed, issues

def test_high_contrast_mode() -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Test high contrast mode functionality.
    
    Returns:
        Tuple containing:
        - Boolean indicating if all tests passed
        - List of issues found
    """
    st.subheader("High Contrast Mode Test")
    st.write("This test checks if high contrast mode is properly implemented.")
    
    issues = []
    all_passed = True
    
    # Create some sample content to test with high contrast
    st.write("### Sample Content for High Contrast Testing")
    
    st.write("This is regular text that should be visible in high contrast mode.")
    
    st.info("This is an info box that should be visible in high contrast mode.")
    
    st.warning("This is a warning box that should be visible in high contrast mode.")
    
    st.error("This is an error box that should be visible in high contrast mode.")
    
    st.success("This is a success box that should be visible in high contrast mode.")
    
    # Create a button
    st.button("Test Button")
    
    # Create a chart
    chart_data = pd.DataFrame({
        "Category": ["A", "B", "C", "D"],
        "Value": [10, 25, 15, 30]
    })
    st.bar_chart(chart_data)
    
    # Manual verification section
    st.write("### Manual Verification")
    st.write("Please enable high contrast mode in the sidebar and verify the following:")
    
    text_visible = st.checkbox("All text is clearly visible", key="text_visible")
    controls_visible = st.checkbox("All controls (buttons, inputs) are clearly visible", key="controls_visible")
    charts_visible = st.checkbox("Charts and visualizations are clearly visible", key="charts_visible")
    sufficient_contrast = st.checkbox("There is sufficient contrast between elements", key="sufficient_contrast")
    no_info_lost = st.checkbox("No information is lost in high contrast mode", key="no_info_lost")
    
    if st.button("Record High Contrast Mode Results"):
        if not text_visible:
            issues.append({
                "component": "High Contrast Mode",
                "issue": "Some text is not clearly visible in high contrast mode",
                "severity": "High"
            })
            all_passed = False
            
        if not controls_visible:
            issues.append({
                "component": "High Contrast Mode",
                "issue": "Some controls are not clearly visible in high contrast mode",
                "severity": "High"
            })
            all_passed = False
            
        if not charts_visible:
            issues.append({
                "component": "High Contrast Mode",
                "issue": "Charts and visualizations are not clearly visible in high contrast mode",
                "severity": "High"
            })
            all_passed = False
            
        if not sufficient_contrast:
            issues.append({
                "component": "High Contrast Mode",
                "issue": "Insufficient contrast between elements in high contrast mode",
                "severity": "High"
            })
            all_passed = False
            
        if not no_info_lost:
            issues.append({
                "component": "High Contrast Mode",
                "issue": "Some information is lost in high contrast mode",
                "severity": "High"
            })
            all_passed = False
            
        if all_passed:
            st.success("All high contrast mode tests passed!")
        else:
            st.error(f"Found {len(issues)} high contrast mode issues.")
            
    return all_passed, issues

def main():
    """Main function to run assistive technology tests."""
    # Initialize accessibility features
    initialize_screen_reader_support()
    initialize_high_contrast_mode()
    
    # Announce page load to screen readers
    announce_page_load(
        "Assistive Technologies Test",
        "This page tests compatibility with assistive technologies like screen readers and keyboard navigation."
    )
    
    # Set up page title
    st.title("Assistive Technologies Compatibility Test")
    st.markdown("""
    This page tests the compatibility of various components with assistive technologies
    such as screen readers and keyboard navigation. It includes tests for the user surveys
    component, as well as other key components in the application.
    
    Please use this page with assistive technologies to verify compatibility.
    """)
    
    # Create tabs for different tests
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Keyboard Navigation",
        "Screen Reader",
        "User Surveys",
        "High Contrast",
        "Results Summary"
    ])
    
    # Track all issues
    all_issues = []
    test_results = {}
    
    # Keyboard Navigation Test
    with tab1:
        keyboard_passed, keyboard_issues = test_keyboard_navigation()
        test_results["Keyboard Navigation"] = keyboard_passed
        all_issues.extend(keyboard_issues)
    
    # Screen Reader Compatibility Test
    with tab2:
        screen_reader_passed, screen_reader_issues = test_screen_reader_compatibility()
        test_results["Screen Reader Compatibility"] = screen_reader_passed
        all_issues.extend(screen_reader_issues)
    
    # User Surveys Accessibility Test
    with tab3:
        surveys_passed, surveys_issues = test_user_surveys_accessibility()
        test_results["User Surveys Accessibility"] = surveys_passed
        all_issues.extend(surveys_issues)
    
    # High Contrast Mode Test
    with tab4:
        high_contrast_passed, high_contrast_issues = test_high_contrast_mode()
        test_results["High Contrast Mode"] = high_contrast_passed
        all_issues.extend(high_contrast_issues)
    
    # Results Summary
    with tab5:
        st.header("Assistive Technologies Test Results")
        
        # Display overall status
        all_tests_passed = all(test_results.values())
        if all_tests_passed:
            st.success("All assistive technology tests passed!")
        else:
            st.error(f"Found {len(all_issues)} assistive technology issues.")
        
        # Display test results
        st.subheader("Test Results by Category")
        for test_name, passed in test_results.items():
            if passed:
                st.write(f"✅ {test_name}: Passed")
            else:
                st.write(f"❌ {test_name}: Failed")
        
        # Display issues
        if all_issues:
            st.subheader("Issues Found")
            issues_df = pd.DataFrame(all_issues)
            st.table(issues_df)
            
            # Save issues to CSV
            if st.button("Save Issues to CSV"):
                os.makedirs("science_data_kit/ui/tests/results", exist_ok=True)
                issues_df.to_csv("science_data_kit/ui/tests/results/assistive_tech_issues.csv", index=False)
                st.success("Issues saved to science_data_kit/ui/tests/results/assistive_tech_issues.csv")
        
        # Recommendations
        st.subheader("Recommendations")
        st.write("""
        Based on the test results, here are some general recommendations for improving accessibility:
        
        1. Ensure all interactive elements are keyboard accessible
        2. Provide appropriate ARIA labels for all UI components
        3. Test with actual screen readers (NVDA, JAWS, VoiceOver)
        4. Ensure sufficient color contrast in all modes
        5. Provide text alternatives for all non-text content
        6. Ensure error messages are accessible to screen readers
        7. Test with actual users who rely on assistive technologies
        """)

if __name__ == "__main__":
    main()