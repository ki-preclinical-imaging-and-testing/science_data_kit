import streamlit as st
from utils.sidebar import database_sidebar, jupyter_sidebar


st.set_page_config(
    page_title="Science Data Toolkit",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://adam-patch.mit.edu',
        'Report a bug': "https://adam-patch.mit.edu",
        'About': "# Science Data for Data Science!"
    }

)

jupyter_sidebar()
database_sidebar()

# Example API functions
def example_function(param1, param2):
    """
    An example function that demonstrates basic usage.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.

    Returns:
        str: A concatenated string.

    Example:
        >>> from science_data_kit import example_function
        >>> example_function(42, "hello")
        '42 hello'
    """
    return f"{param1} {param2}"

# Title and description
st.title("Integrate")
st.markdown("""
Explore the API and integrate it into your workflows. You can find documentation, explore the Python driver, and test examples interactively.
""")

# Links to Documentation
st.markdown("""
### Documentation Links
- [API Documentation](https://your-sphinx-docs-link.com)
- [GitHub Repository](https://github.com/your-repo-link)
""")

# Interactive API Tester
st.subheader("Try the API")
with st.form("api_form"):
    param1 = st.number_input("Parameter 1 (integer):", min_value=0, value=42)
    param2 = st.text_input("Parameter 2 (string):", value="hello")
    submitted = st.form_submit_button("Run Example")
    if submitted:
        result = example_function(param1, param2)
        st.success(f"Result: {result}")

# Display Inline Examples
st.subheader("Example Usage")
st.code("""
from science_data_kit import example_function

# Basic example
result = example_function(42, "hello")
print(result)  # Output: '42 hello'
""", language="python")

