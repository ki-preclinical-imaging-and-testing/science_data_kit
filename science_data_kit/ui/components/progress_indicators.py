"""
Progress Indicators Component for Science Data Kit

This module provides standardized progress indicator components for use across the application
to show progress in multi-step workflows.
"""

import streamlit as st
from typing import List, Dict, Optional, Union, Tuple, Any
from enum import Enum
import json
from .terminology import get_term
from .ui_constants import get_color

class ProgressIndicatorType(Enum):
    """Enum for different types of progress indicators."""
    LINEAR = "linear"
    CIRCULAR = "circular"
    STEP = "step"
    DOT = "dot"

class ProgressStep:
    """
    Represents a single step in a multi-step workflow.
    
    Attributes:
        label (str): The display label for the step
        description (str, optional): A longer description of the step
        completed (bool): Whether this step has been completed
        current (bool): Whether this is the current active step
        icon (str, optional): Icon to display with the step
        data (Any, optional): Additional data associated with the step
    """
    
    def __init__(
        self, 
        label: str, 
        description: Optional[str] = None,
        completed: bool = False,
        current: bool = False,
        icon: Optional[str] = None,
        data: Optional[Any] = None
    ):
        """
        Initialize a progress step.
        
        Args:
            label (str): The display label for the step
            description (str, optional): A longer description of the step
            completed (bool): Whether this step has been completed
            current (bool): Whether this is the current active step
            icon (str, optional): Icon to display with the step
            data (Any, optional): Additional data associated with the step
        """
        self.label = label
        self.description = description
        self.completed = completed
        self.current = current
        self.icon = icon
        self.data = data

class ProgressIndicator:
    """
    Manages a progress indicator for multi-step workflows.
    
    Attributes:
        steps (List[ProgressStep]): The list of steps in the workflow
        indicator_type (ProgressIndicatorType): The type of progress indicator to display
        container_style (Dict): CSS styles for the progress indicator container
        step_style (Dict): CSS styles for individual steps
        completed_style (Dict): CSS styles for completed steps
        current_style (Dict): CSS styles for the current step
        show_labels (bool): Whether to show step labels
        show_descriptions (bool): Whether to show step descriptions
        show_percentage (bool): Whether to show percentage completion
    """
    
    def __init__(
        self,
        indicator_type: ProgressIndicatorType = ProgressIndicatorType.LINEAR,
        container_style: Optional[Dict] = None,
        step_style: Optional[Dict] = None,
        completed_style: Optional[Dict] = None,
        current_style: Optional[Dict] = None,
        show_labels: bool = True,
        show_descriptions: bool = False,
        show_percentage: bool = True
    ):
        """
        Initialize a progress indicator.
        
        Args:
            indicator_type (ProgressIndicatorType): The type of progress indicator to display
            container_style (Dict, optional): CSS styles for the progress indicator container
            step_style (Dict, optional): CSS styles for individual steps
            completed_style (Dict, optional): CSS styles for completed steps
            current_style (Dict, optional): CSS styles for the current step
            show_labels (bool): Whether to show step labels
            show_descriptions (bool): Whether to show step descriptions
            show_percentage (bool): Whether to show percentage completion
        """
        self.steps: List[ProgressStep] = []
        self.indicator_type = indicator_type
        self.show_labels = show_labels
        self.show_descriptions = show_descriptions
        self.show_percentage = show_percentage
        
        # Default styles
        self.container_style = {
            "padding": "1rem 0",
            "margin-bottom": "1.5rem",
            "width": "100%"
        }
        
        self.step_style = {
            "color": get_color("text_secondary"),
            "background-color": get_color("background_secondary"),
            "border": f"1px solid {get_color('border')}",
            "padding": "0.5rem",
            "margin": "0 0.2rem",
            "border-radius": "4px",
            "text-align": "center"
        }
        
        self.completed_style = {
            "color": get_color("text_on_primary"),
            "background-color": get_color("success"),
            "border": f"1px solid {get_color('success')}",
            "padding": "0.5rem",
            "margin": "0 0.2rem",
            "border-radius": "4px",
            "text-align": "center"
        }
        
        self.current_style = {
            "color": get_color("text_on_primary"),
            "background-color": get_color("primary"),
            "border": f"1px solid {get_color('primary')}",
            "padding": "0.5rem",
            "margin": "0 0.2rem",
            "border-radius": "4px",
            "text-align": "center",
            "font-weight": "bold"
        }
        
        # Override with custom styles if provided
        if container_style:
            self.container_style.update(container_style)
            
        if step_style:
            self.step_style.update(step_style)
            
        if completed_style:
            self.completed_style.update(completed_style)
            
        if current_style:
            self.current_style.update(current_style)
    
    def add_step(
        self, 
        label: str, 
        description: Optional[str] = None,
        completed: bool = False,
        current: bool = False,
        icon: Optional[str] = None,
        data: Optional[Any] = None
    ) -> None:
        """
        Add a step to the progress indicator.
        
        Args:
            label (str): The display label for the step
            description (str, optional): A longer description of the step
            completed (bool): Whether this step has been completed
            current (bool): Whether this is the current active step
            icon (str, optional): Icon to display with the step
            data (Any, optional): Additional data associated with the step
        """
        step = ProgressStep(label, description, completed, current, icon, data)
        self.steps.append(step)
    
    def update_step(
        self,
        index: int,
        completed: Optional[bool] = None,
        current: Optional[bool] = None
    ) -> None:
        """
        Update the status of a step.
        
        Args:
            index (int): The index of the step to update
            completed (bool, optional): Whether the step is completed
            current (bool, optional): Whether the step is the current active step
        """
        if 0 <= index < len(self.steps):
            if completed is not None:
                self.steps[index].completed = completed
            if current is not None:
                self.steps[index].current = current
    
    def clear(self) -> None:
        """Clear all steps from the progress indicator."""
        self.steps = []
    
    def get_completion_percentage(self) -> float:
        """
        Calculate the percentage of completed steps.
        
        Returns:
            float: The percentage of completed steps (0-100)
        """
        if not self.steps:
            return 0.0
        
        completed_count = sum(1 for step in self.steps if step.completed)
        return (completed_count / len(self.steps)) * 100
    
    def render_linear_progress(self) -> str:
        """
        Render a linear progress bar.
        
        Returns:
            str: HTML for the linear progress bar
        """
        percentage = self.get_completion_percentage()
        
        html = f"""
        <div style="width: 100%; background-color: {get_color('background_secondary')}; 
                    height: 8px; border-radius: 4px; margin: 1rem 0;">
            <div style="width: {percentage}%; background-color: {get_color('primary')}; 
                        height: 8px; border-radius: 4px;"></div>
        </div>
        """
        
        if self.show_percentage:
            html += f"""
            <div style="text-align: center; font-size: 0.9rem; color: {get_color('text_secondary')};">
                {percentage:.0f}% {get_term('UI_TERMINOLOGY', 'Complete')}
            </div>
            """
        
        return html
    
    def render_circular_progress(self) -> str:
        """
        Render a circular progress indicator.
        
        Returns:
            str: HTML for the circular progress indicator
        """
        percentage = self.get_completion_percentage()
        
        # SVG for circular progress
        svg_size = 100
        circle_radius = 40
        circle_circumference = 2 * 3.14159 * circle_radius
        stroke_width = 8
        
        # Calculate the stroke-dasharray and stroke-dashoffset for the progress arc
        dasharray = circle_circumference
        dashoffset = circle_circumference * (1 - percentage / 100)
        
        html = f"""
        <div style="text-align: center;">
            <svg width="{svg_size}" height="{svg_size}" viewBox="0 0 {svg_size} {svg_size}">
                <circle cx="{svg_size/2}" cy="{svg_size/2}" r="{circle_radius}"
                        fill="none" stroke="{get_color('background_secondary')}" stroke-width="{stroke_width}"/>
                <circle cx="{svg_size/2}" cy="{svg_size/2}" r="{circle_radius}"
                        fill="none" stroke="{get_color('primary')}" stroke-width="{stroke_width}"
                        stroke-dasharray="{dasharray}" stroke-dashoffset="{dashoffset}"
                        transform="rotate(-90 {svg_size/2} {svg_size/2})"/>
                <text x="{svg_size/2}" y="{svg_size/2}" text-anchor="middle" dominant-baseline="middle"
                      fill="{get_color('text_primary')}" font-size="16">
                    {percentage:.0f}%
                </text>
            </svg>
        </div>
        """
        
        return html
    
    def render_step_progress(self) -> str:
        """
        Render a step-based progress indicator.
        
        Returns:
            str: HTML for the step-based progress indicator
        """
        html = '<div style="display: flex; justify-content: space-between; width: 100%;">'
        
        for i, step in enumerate(self.steps):
            # Determine style based on step status
            if step.current:
                style = self.current_style
            elif step.completed:
                style = self.completed_style
            else:
                style = self.step_style
                
            style_str = '; '.join([f'{k}: {v}' for k, v in style.items()])
            
            # Add step number and icon if provided
            step_number = i + 1
            icon_html = f'<i class="material-icons" style="font-size: 1rem; vertical-align: middle; margin-right: 0.2rem;">{step.icon}</i>' if step.icon else ''
            
            # Create step HTML
            html += f"""
            <div style="{style_str}; flex: 1; max-width: {100/len(self.steps)}%;">
                <div style="font-weight: bold;">{step_number}</div>
            """
            
            if self.show_labels:
                html += f'<div>{icon_html}{step.label}</div>'
                
            if self.show_descriptions and step.description:
                html += f'<div style="font-size: 0.8rem; margin-top: 0.3rem;">{step.description}</div>'
                
            html += '</div>'
            
            # Add connector line between steps
            if i < len(self.steps) - 1:
                connector_color = get_color('success') if step.completed else get_color('border')
                html += f'<div style="flex: 0.5; height: 2px; background-color: {connector_color}; align-self: center;"></div>'
        
        html += '</div>'
        return html
    
    def render_dot_progress(self) -> str:
        """
        Render a dot-based progress indicator.
        
        Returns:
            str: HTML for the dot-based progress indicator
        """
        html = '<div style="display: flex; justify-content: center; align-items: center; width: 100%;">'
        
        for i, step in enumerate(self.steps):
            # Determine style based on step status
            if step.current:
                dot_color = get_color('primary')
                dot_size = "12px"
            elif step.completed:
                dot_color = get_color('success')
                dot_size = "10px"
            else:
                dot_color = get_color('background_secondary')
                dot_size = "10px"
            
            # Create dot HTML
            html += f"""
            <div style="
                width: {dot_size}; 
                height: {dot_size}; 
                border-radius: 50%; 
                background-color: {dot_color}; 
                margin: 0 0.3rem;
                border: 1px solid {get_color('border')};
            "></div>
            """
            
            # Add connector line between dots
            if i < len(self.steps) - 1:
                connector_color = get_color('success') if step.completed else get_color('border')
                html += f'<div style="width: 20px; height: 2px; background-color: {connector_color};"></div>'
        
        html += '</div>'
        
        # Add labels below if needed
        if self.show_labels:
            html += '<div style="display: flex; justify-content: center; margin-top: 0.5rem; width: 100%;">'
            
            for step in self.steps:
                # Determine text color based on step status
                if step.current:
                    text_color = get_color('primary')
                    font_weight = "bold"
                elif step.completed:
                    text_color = get_color('success')
                    font_weight = "normal"
                else:
                    text_color = get_color('text_secondary')
                    font_weight = "normal"
                
                # Create label HTML
                html += f"""
                <div style="
                    color: {text_color}; 
                    font-weight: {font_weight};
                    text-align: center;
                    flex: 1;
                    font-size: 0.8rem;
                    max-width: {100/len(self.steps)}%;
                    padding: 0 0.2rem;
                ">{step.label}</div>
                """
            
            html += '</div>'
        
        return html
    
    def render(self) -> None:
        """Render the progress indicator in the Streamlit app."""
        if not self.steps:
            return
        
        # Create container for progress indicator
        container_html = f"""
        <div style="{'; '.join([f'{k}: {v}' for k, v in self.container_style.items()])}">
        """
        
        # Render the appropriate progress indicator type
        if self.indicator_type == ProgressIndicatorType.LINEAR:
            container_html += self.render_linear_progress()
        elif self.indicator_type == ProgressIndicatorType.CIRCULAR:
            container_html += self.render_circular_progress()
        elif self.indicator_type == ProgressIndicatorType.STEP:
            container_html += self.render_step_progress()
        elif self.indicator_type == ProgressIndicatorType.DOT:
            container_html += self.render_dot_progress()
        
        container_html += "</div>"
        
        # Render the HTML
        st.markdown(container_html, unsafe_allow_html=True)

def create_progress_indicator(
    steps: List[Dict[str, Union[str, bool, Any]]],
    indicator_type: Union[str, ProgressIndicatorType] = ProgressIndicatorType.LINEAR,
    container_style: Optional[Dict] = None,
    step_style: Optional[Dict] = None,
    completed_style: Optional[Dict] = None,
    current_style: Optional[Dict] = None,
    show_labels: bool = True,
    show_descriptions: bool = False,
    show_percentage: bool = True
) -> None:
    """
    Create and render a progress indicator from a list of step dictionaries.
    
    Args:
        steps (List[Dict]): List of dictionaries with keys 'label', 'description' (optional),
                           'completed' (optional), 'current' (optional), 'icon' (optional),
                           and 'data' (optional)
        indicator_type (str or ProgressIndicatorType): The type of progress indicator to display
        container_style (Dict, optional): CSS styles for the progress indicator container
        step_style (Dict, optional): CSS styles for individual steps
        completed_style (Dict, optional): CSS styles for completed steps
        current_style (Dict, optional): CSS styles for the current step
        show_labels (bool): Whether to show step labels
        show_descriptions (bool): Whether to show step descriptions
        show_percentage (bool): Whether to show percentage completion
    """
    # Convert string to enum if needed
    if isinstance(indicator_type, str):
        try:
            indicator_type = ProgressIndicatorType(indicator_type)
        except ValueError:
            indicator_type = ProgressIndicatorType.LINEAR
    
    indicator = ProgressIndicator(
        indicator_type, 
        container_style, 
        step_style, 
        completed_style, 
        current_style,
        show_labels,
        show_descriptions,
        show_percentage
    )
    
    for step in steps:
        label = step.get('label', '')
        description = step.get('description')
        completed = step.get('completed', False)
        current = step.get('current', False)
        icon = step.get('icon')
        data = step.get('data')
        
        indicator.add_step(label, description, completed, current, icon, data)
    
    indicator.render()

def add_progress_to_session(
    steps: List[Dict[str, Union[str, bool, Any]]],
    key: str = "progress_steps"
) -> None:
    """
    Add progress steps to the session state for persistent tracking.
    
    Args:
        steps (List[Dict]): List of dictionaries with step information
        key (str): Key to use in session state for storing progress steps
    """
    if key not in st.session_state:
        st.session_state[key] = []
    
    st.session_state[key] = steps

def get_progress_from_session(key: str = "progress_steps") -> List[Dict]:
    """
    Get progress steps from the session state.
    
    Args:
        key (str): Key used in session state for storing progress steps
        
    Returns:
        List[Dict]: List of dictionaries with step information
    """
    return st.session_state.get(key, [])

def update_progress_in_session(
    step_index: int,
    completed: Optional[bool] = None,
    current: Optional[bool] = None,
    key: str = "progress_steps"
) -> None:
    """
    Update a specific step in the session state progress.
    
    Args:
        step_index (int): Index of the step to update
        completed (bool, optional): Whether the step is completed
        current (bool, optional): Whether the step is the current active step
        key (str): Key used in session state for storing progress steps
    """
    steps = get_progress_from_session(key)
    
    if 0 <= step_index < len(steps):
        if completed is not None:
            steps[step_index]['completed'] = completed
        if current is not None:
            steps[step_index]['current'] = current
        
        add_progress_to_session(steps, key)

def render_progress_from_session(
    key: str = "progress_steps",
    indicator_type: Union[str, ProgressIndicatorType] = ProgressIndicatorType.LINEAR,
    container_style: Optional[Dict] = None,
    step_style: Optional[Dict] = None,
    completed_style: Optional[Dict] = None,
    current_style: Optional[Dict] = None,
    show_labels: bool = True,
    show_descriptions: bool = False,
    show_percentage: bool = True
) -> None:
    """
    Render progress indicator from the session state.
    
    Args:
        key (str): Key used in session state for storing progress steps
        indicator_type (str or ProgressIndicatorType): The type of progress indicator to display
        container_style (Dict, optional): CSS styles for the progress indicator container
        step_style (Dict, optional): CSS styles for individual steps
        completed_style (Dict, optional): CSS styles for completed steps
        current_style (Dict, optional): CSS styles for the current step
        show_labels (bool): Whether to show step labels
        show_descriptions (bool): Whether to show step descriptions
        show_percentage (bool): Whether to show percentage completion
    """
    steps = get_progress_from_session(key)
    if steps:
        create_progress_indicator(
            steps, 
            indicator_type, 
            container_style, 
            step_style, 
            completed_style, 
            current_style,
            show_labels,
            show_descriptions,
            show_percentage
        )