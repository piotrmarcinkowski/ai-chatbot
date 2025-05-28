import streamlit as st

from chat_history import chat_history

def draw_archive_ui():
    st.markdown("# 📜 Chat Archive")
    session_ids = chat_history.get_chat_session_ids(limit=10)
    session_ids

draw_archive_ui()
