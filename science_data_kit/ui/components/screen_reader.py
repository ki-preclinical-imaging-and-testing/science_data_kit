"""
Screen Reader Support for Science Data Kit

This module provides utilities for making the application more accessible to screen readers.
It includes functions for adding ARIA attributes, screen reader-only text, and other
accessibility enhancements.
"""

import streamlit as st
from typing import Dict, Optional, List, Union

def add_screen_reader_text(text: str) -> str:
    """
    Create HTML for text that is only visible to screen readers.
    
    Args:
        text (str): The text to be read by screen readers
        
    Returns:
        str: HTML with the text styled to be invisible but accessible to screen readers
    """
    return f"""
    <span class="sr-only" style="position: absolute; width: 1px; height: 1px; padding: 0; 
    margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; 
    border-width: 0;">{text}</span>
    """

def add_aria_label(element_id: str, label: str) -> str:
    """
    Create JavaScript to add an ARIA label to an element.
    
    Args:
        element_id (str): The ID of the element to label
        label (str): The label text
        
    Returns:
        str: JavaScript to add the ARIA label
    """
    return f"""
    <script>
    (function() {{
        const element = document.getElementById("{element_id}");
        if (element) {{
            element.setAttribute("aria-label", "{label}");
        }}
    }})();
    </script>
    """

def add_aria_live_region(region_id: str = "aria-live-region", politeness: str = "polite") -> None:
    """
    Add an ARIA live region to the page for dynamic content updates.
    
    Args:
        region_id (str): The ID to give the live region
        politeness (str): The politeness level ('polite' or 'assertive')
    """
    html = f"""
    <div id="{region_id}" aria-live="{politeness}" style="position: absolute; width: 1px; 
    height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); 
    white-space: nowrap; border-width: 0;"></div>
    """
    st.markdown(html, unsafe_allow_html=True)

def update_live_region(message: str, region_id: str = "aria-live-region") -> None:
    """
    Update the content of an ARIA live region.
    
    Args:
        message (str): The message to announce
        region_id (str): The ID of the live region to update
    """
    js = f"""
    <script>
    (function() {{
        const region = document.getElementById("{region_id}");
        if (region) {{
            region.textContent = "{message}";
        }}
    }})();
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)

def add_skip_link(target_id: str, label: str = "Skip to main content") -> None:
    """
    Add a skip navigation link for keyboard users.
    
    Args:
        target_id (str): The ID of the element to skip to
        label (str): The label for the skip link
    """
    html = f"""
    <style>
    .skip-link {{
        position: absolute;
        top: -40px;
        left: 0;
        background: #000;
        color: white;
        padding: 8px;
        z-index: 100;
        transition: top 0.3s;
    }}
    
    .skip-link:focus {{
        top: 0;
    }}
    </style>
    
    <a href="#{target_id}" class="skip-link">{label}</a>
    
    <script>
    (function() {{
        // Ensure the target element has an ID and tabindex
        const target = document.getElementById("{target_id}");
        if (target) {{
            target.setAttribute("tabindex", "-1");
        }}
        
        // Add focus handling for the skip link
        const skipLink = document.querySelector(".skip-link");
        if (skipLink) {{
            skipLink.addEventListener("click", function(e) {{
                e.preventDefault();
                const target = document.getElementById("{target_id}");
                if (target) {{
                    target.focus();
                    // Scroll to the target if needed
                    target.scrollIntoView();
                }}
            }});
        }}
    }})();
    </script>
    """
    st.markdown(html, unsafe_allow_html=True)

def make_focusable(element_id: str) -> str:
    """
    Create JavaScript to make an element focusable.
    
    Args:
        element_id (str): The ID of the element to make focusable
        
    Returns:
        str: JavaScript to make the element focusable
    """
    return f"""
    <script>
    (function() {{
        const element = document.getElementById("{element_id}");
        if (element) {{
            element.setAttribute("tabindex", "0");
        }}
    }})();
    </script>
    """

def add_role(element_id: str, role: str) -> str:
    """
    Create JavaScript to add an ARIA role to an element.
    
    Args:
        element_id (str): The ID of the element
        role (str): The ARIA role to add
        
    Returns:
        str: JavaScript to add the ARIA role
    """
    return f"""
    <script>
    (function() {{
        const element = document.getElementById("{element_id}");
        if (element) {{
            element.setAttribute("role", "{role}");
        }}
    }})();
    </script>
    """

def add_aria_attributes(element_id: str, attributes: Dict[str, str]) -> str:
    """
    Create JavaScript to add multiple ARIA attributes to an element.
    
    Args:
        element_id (str): The ID of the element
        attributes (Dict[str, str]): Dictionary of ARIA attributes and values
        
    Returns:
        str: JavaScript to add the ARIA attributes
    """
    js_lines = []
    for attr, value in attributes.items():
        js_lines.append(f'element.setAttribute("aria-{attr}", "{value}");')
    
    attributes_js = "\n            ".join(js_lines)
    
    return f"""
    <script>
    (function() {{
        const element = document.getElementById("{element_id}");
        if (element) {{
            {attributes_js}
        }}
    }})();
    </script>
    """

def announce_page_load(title: str, description: Optional[str] = None) -> None:
    """
    Announce a page load to screen readers.
    
    Args:
        title (str): The title of the page
        description (Optional[str]): Optional description of the page
    """
    message = f"Page loaded: {title}"
    if description:
        message += f". {description}"
    
    # Create a live region if it doesn't exist
    add_aria_live_region("page-announcer", "assertive")
    
    # Update the live region with the message
    update_live_region(message, "page-announcer")

def make_table_accessible(table_id: str, caption: str, headers: List[str]) -> str:
    """
    Create JavaScript to make a table accessible to screen readers.
    
    Args:
        table_id (str): The ID of the table
        caption (str): The caption for the table
        headers (List[str]): List of header cell texts
        
    Returns:
        str: JavaScript to make the table accessible
    """
    return f"""
    <script>
    (function() {{
        const table = document.getElementById("{table_id}");
        if (table) {{
            // Add role
            table.setAttribute("role", "table");
            
            // Add caption
            let caption = document.createElement("caption");
            caption.textContent = "{caption}";
            table.prepend(caption);
            
            // Find header row and add appropriate attributes
            const headerRow = table.querySelector("thead tr");
            if (headerRow) {{
                headerRow.setAttribute("role", "row");
                const headerCells = headerRow.querySelectorAll("th");
                for (let i = 0; i < headerCells.length; i++) {{
                    headerCells[i].setAttribute("role", "columnheader");
                    headerCells[i].setAttribute("scope", "col");
                }}
            }}
            
            // Add attributes to data rows and cells
            const rows = table.querySelectorAll("tbody tr");
            for (let i = 0; i < rows.length; i++) {{
                rows[i].setAttribute("role", "row");
                const cells = rows[i].querySelectorAll("td");
                for (let j = 0; j < cells.length; j++) {{
                    cells[j].setAttribute("role", "cell");
                }}
            }}
        }}
    }})();
    </script>
    """

def initialize_screen_reader_support() -> None:
    """
    Initialize screen reader support for the application.
    
    This function adds necessary CSS and JavaScript for screen reader support.
    """
    # Add CSS for screen reader only elements
    css = """
    <style>
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
    }
    
    /* Focus styles for keyboard navigation */
    :focus {
        outline: 2px solid #4299e1;
        outline-offset: 2px;
    }
    
    /* High contrast focus styles */
    @media (forced-colors: active) {
        :focus {
            outline: 3px solid HighlightText;
        }
    }
    </style>
    """
    
    # Add global JavaScript for screen reader support
    js = """
    <script>
    (function() {
        // Add role="main" to the main content area
        const mainContent = document.querySelector(".main");
        if (mainContent) {
            mainContent.setAttribute("role", "main");
            mainContent.setAttribute("id", "main-content");
        }
        
        // Add role="navigation" to the sidebar
        const sidebar = document.querySelector(".sidebar");
        if (sidebar) {
            sidebar.setAttribute("role", "navigation");
            sidebar.setAttribute("aria-label", "Main Navigation");
        }
        
        // Add role="banner" to the header
        const header = document.querySelector("header");
        if (header) {
            header.setAttribute("role", "banner");
        }
        
        // Add role="contentinfo" to the footer
        const footer = document.querySelector("footer");
        if (footer) {
            footer.setAttribute("role", "contentinfo");
        }
        
        // Make all buttons and links accessible
        const buttons = document.querySelectorAll("button");
        for (let i = 0; i < buttons.length; i++) {
            if (!buttons[i].getAttribute("aria-label") && !buttons[i].textContent.trim()) {
                const prevText = buttons[i].previousElementSibling?.textContent.trim();
                if (prevText) {
                    buttons[i].setAttribute("aria-label", prevText);
                }
            }
        }
    })();
    </script>
    """
    
    # Add skip link
    add_skip_link("main-content")
    
    # Add the CSS and JavaScript
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(js, unsafe_allow_html=True)
    
    # Add a live region for announcements
    add_aria_live_region()