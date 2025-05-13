import streamlit as st

from utils.sidebar import database_sidebar, jupyter_sidebar, neo4j_connector, neodash_sidebar, settings_sidebar

# Title and description
st.header("Data Resources")
st.markdown("""Spin up servers and connect to your data on this page.""")

server_dict = {
    'Servers': None,
    'Launch a Neo4j database to stage your adta': database_sidebar,
    'Run Jupyter Lab to work with your data': jupyter_sidebar,
    'Launch NeoDash for Neo4j visualization': neodash_sidebar,
    'Drivers': None,
    'Connect to a Neo4j database': neo4j_connector,
    'Settings': None,
    'Customize application appearance and behavior': settings_sidebar
}


row = {}
row_index = 0
for _text, _widget in server_dict.items():
    row[row_index] = st.columns(2)
    if _widget is None:
        with row[row_index][0]:
            st.divider()
        with row[row_index][1]:
            st.subheader(_text)
    else:
        with row[row_index][0]:
            _widget()
        with row[row_index][1]:
            st.markdown(f"*{_text}*")
    row_index += 1

st.divider()

with st.expander("API Documentation", expanded=False):
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

    # Define example function
    def example_function(param1, param2):
        """Example function for API demonstration"""
        return f"{param1} {param2}"

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
