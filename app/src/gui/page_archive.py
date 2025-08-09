import streamlit as st
from datetime import datetime

from model.chat_history import init_chat_archive
from gui.view_model import chatbot_instance

def draw_archive_ui():
    st.markdown("# 📜 Chat Archive")
    chat_archive = init_chat_archive()
    sessions = chat_archive.get_session_list()
    for session in sessions:
        session_id = session['session_id']
        first_message = session['first_message'] if session['first_message'] else "<No messages>"
        timestamp = session['timestamp']
        formatted_date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S") if timestamp else "<Unknown time>"
                
        with st.expander(first_message, expanded=False):
            st.write(f"**Session ID:** {session_id}")
            st.write(f"**Date:** {formatted_date}")
            
            if st.button(label="Load Session", key=session_id, type="secondary"):
                print(f"ChatArchive.Loading session {session['session_id']}")
                chatbot = chatbot_instance()
                chatbot.load_chat(session_id)
                st.switch_page("gui/page_chat.py")

draw_archive_ui()
