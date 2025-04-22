import streamlit as st
from pathlib import Path
from about import about
from chat import chat

def menu():
    # st.sidebar.markdown("️️🖥️ **Science Data Toolkit**")
    pg = st.navigation([
        st.Page(Path("connect.py"), title=f"connect", icon="🌐"),
        st.Page(Path("survey.py"), title="survey", icon="🔭"),
        st.Page(Path("map.py"), title="map", icon="🗺"),
        st.Page(Path("explore.py"), title="explore", icon="🏞"),
        st.Page(chat, title="chat", icon="💬"),
        st.Page(about, title="learn", icon="📖")
    ])
    pg.run()
