import streamlit as st
from chatbot import Chatbot

def draw_ui():
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = Chatbot()
    chatbot = st.session_state.chatbot
            
    st.set_page_config(page_title="AI Chatbot", layout="wide")

    with st.sidebar:
        st.header("Previous chats")
        st.write("- To be implemented")

    st.title("AI Chatbot")
    chat_container = st.container()

    with st.form(key="chat_form"):
        default_text = "Hello, introduce yourself"
        user_input = st.text_area("Type your message:", value=default_text, height=100, max_chars=500)
        submit_button = st.form_submit_button("Send")

    if submit_button and user_input:
        with chat_container:
            st.write(f"**You:** {user_input}")
            response = chatbot.search_local_knowledge(user_input)
            st.write(f"**Bot:** {response}")

draw_ui()