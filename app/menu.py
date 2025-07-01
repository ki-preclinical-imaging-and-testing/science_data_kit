import streamlit as st
from pathlib import Path
from about import about
from chat import chat

def menu():
    """
    Set up the navigation menu for the Streamlit application.

    This function creates a navigation menu with various pages including connect,
    survey, map, explore, chat, and learn. Each page is represented by a Path object
    or a function reference and has an associated icon.

    Returns:
        None
    """
    # st.sidebar.markdown("️️🖥️ **Science Data Toolkit**")
    pg = st.navigation([
        st.Page(Path("connect.py"), title=f"connect", icon="🌐"),
        st.Page(Path("survey.py"), title="survey", icon="🔭"),
        st.Page(Path("map.py"), title="map", icon="🗺"),
        st.Page(Path("explore.py"), title="explore", icon="🏞"),
        st.Page(Path("streamlit_isa_browser.py"), title="ontology", icon="🧬"),
        st.Page(chat, title="chat", icon="💬"),
        st.Page(about, title="learn", icon="📖")
    ])
    pg.run()
