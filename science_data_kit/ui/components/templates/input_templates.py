"""
Input Templates for Science Data Kit

This module provides standardized input templates for use across the application.
"""

import streamlit as st
from typing import Optional, Callable, Any, List, Union, Dict

def standard_text_input(label: str, value: str = "", key: Optional[str] = None, help: Optional[str] = None, placeholder: Optional[str] = None, disabled: bool = False, max_chars: Optional[int] = None) -> str:
    """
    Create a standardized text input.
    
    Args:
        label: The label to display above the input
        value: The initial value
        key: An optional key that uniquely identifies this input
        help: Optional tooltip shown when the input is hovered
        placeholder: Optional placeholder text shown when the input is empty
        disabled: Optional flag to disable the input
        max_chars: Optional maximum number of characters allowed
    
    Returns:
        The entered text
    """
    return st.text_input(
        label=label,
        value=value,
        key=key,
        help=help,
        placeholder=placeholder,
        disabled=disabled,
        max_chars=max_chars,
        label_visibility="visible"
    )

def standard_number_input(label: str, min_value: Optional[Union[int, float]] = None, max_value: Optional[Union[int, float]] = None, value: Optional[Union[int, float]] = None, step: Optional[Union[int, float]] = None, key: Optional[str] = None, help: Optional[str] = None, disabled: bool = False) -> Union[int, float]:
    """
    Create a standardized number input.
    
    Args:
        label: The label to display above the input
        min_value: The minimum value allowed
        max_value: The maximum value allowed
        value: The initial value
        step: The stepping interval
        key: An optional key that uniquely identifies this input
        help: Optional tooltip shown when the input is hovered
        disabled: Optional flag to disable the input
    
    Returns:
        The entered number
    """
    return st.number_input(
        label=label,
        min_value=min_value,
        max_value=max_value,
        value=value if value is not None else (min_value if min_value is not None else 0),
        step=step,
        key=key,
        help=help,
        disabled=disabled,
        label_visibility="visible"
    )

def standard_selectbox(label: str, options: List[Any], index: int = 0, key: Optional[str] = None, help: Optional[str] = None, disabled: bool = False) -> Any:
    """
    Create a standardized selectbox.
    
    Args:
        label: The label to display above the selectbox
        options: The options to select from
        index: The index of the selected option
        key: An optional key that uniquely identifies this selectbox
        help: Optional tooltip shown when the selectbox is hovered
        disabled: Optional flag to disable the selectbox
    
    Returns:
        The selected option
    """
    return st.selectbox(
        label=label,
        options=options,
        index=index,
        key=key,
        help=help,
        disabled=disabled,
        label_visibility="visible"
    )

def standard_file_uploader(label: str, type: Union[str, List[str]], key: Optional[str] = None, help: Optional[str] = None, accept_multiple_files: bool = False, disabled: bool = False) -> Any:
    """
    Create a standardized file uploader.
    
    Args:
        label: The label to display above the file uploader
        type: The file types to accept (e.g., "csv", ["csv", "txt"])
        key: An optional key that uniquely identifies this file uploader
        help: Optional tooltip shown when the file uploader is hovered
        accept_multiple_files: Optional flag to accept multiple files
        disabled: Optional flag to disable the file uploader
    
    Returns:
        The uploaded file(s)
    """
    return st.file_uploader(
        label=label,
        type=type,
        key=key,
        help=help,
        accept_multiple_files=accept_multiple_files,
        disabled=disabled,
        label_visibility="visible"
    )