import streamlit as st
from utils.format import format_date

from app.src.model.chat_history import init_chat_archive
from gui.view_model import chatbot_instance

def draw_archive_ui():
    st.markdown("# 📜 Chat Archive")
    chat_archive = init_chat_archive()
    sessions = chat_archive.get_session_list()
    for session in sessions:
        session_id = session['session_id']
        first_message = session['first_message'] if session['first_message'] else "<No messages>"
        timestamp = session['timestamp']
        formatted_date = format_date(timestamp) if timestamp else "<Unknown time>"
                
        with st.expander(first_message, expanded=False):
            st.write(f"**Session ID:** {session_id}")
            st.write(f"**Date:** {formatted_date}")
            
            col1, col2, _ = st.columns([1, 1, 8])

            with col1:
                if st.button(label=":green[Load Session]", key=session_id, type="secondary"):
                    print(f"ChatArchive.Loading session {session['session_id']}")
                    chatbot = chatbot_instance()
                    chatbot.load_chat(session_id)
                    st.switch_page("gui/page_chat.py")
            with col2:
                if st.button(label=":red[Delete Session]", key=f"delete_{session_id}", type="secondary"):
                    print(f"ChatArchive.Deleting session {session['session_id']}")
                    chat_archive.delete_session(session_id)
                    st.rerun()

draw_archive_ui()
