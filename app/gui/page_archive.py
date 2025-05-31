import streamlit as st

from model.chat_history import init_chat_archive

def draw_archive_ui():
    st.markdown("# 📜 Chat Archive")
    session_ids = init_chat_archive().get_archived_session_ids(limit=10)
    session_ids

draw_archive_ui()
