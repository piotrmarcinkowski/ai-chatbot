import streamlit as st
from model.chatbot import Chatbot

def chatbot_instance():
    """
    Initializes the chatbot instance.
    """
    if "chatbot" not in st.session_state:
        new_chatbot = Chatbot()
        new_chatbot.start_new_chat()
        st.session_state.chatbot = new_chatbot
    return st.session_state.chatbot
