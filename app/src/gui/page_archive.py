import streamlit as st

from model.chat_history import init_chat_archive
from gui.view_model import chatbot_instance

def draw_archive_ui():
    st.markdown("# 📜 Chat Archive")
    chat_archive = init_chat_archive()
    session_ids = chat_archive.get_archived_session_ids(limit=10)

    for session in session_ids:
        session_id = session['session_id']
        messages = chat_archive.get_chat_messages(session_id)
        first_message = messages[0].content if messages else "No messages found"

        with st.expander(first_message, expanded=False):
            st.write(f"**Session ID:** {session_id}")
            
            if st.button(label="Load Session", key=session_id, type="secondary"):
                print(f"ChatArchive.Loading session {session['session_id']}")
                chatbot = chatbot_instance()
                chatbot.load_chat(session_id)
                st.switch_page("gui/page_chat.py")

draw_archive_ui()
