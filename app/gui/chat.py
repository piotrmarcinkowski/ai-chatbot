import streamlit as st

from gui.model import chatbot_instance

def draw_chat_ui():
    st.markdown("# 💬 Chat")
    chatbot = chatbot_instance()
    
    chat_container = st.container(height=600)
    with chat_container:
        for message in chatbot.get_chat_history():
            if message.type == "human":
                st.write(f"**You:** {message.content}")
            else:
                st.write(f"**AI:** {message.content}")

    with st.form(key="chat_form"):
        default_text = "Hello, introduce yourself"
        user_input = st.text_area("Type your message:", value=default_text, height=100, max_chars=500)
        submit_button = st.form_submit_button("Send", type="primary")

    if submit_button and user_input:
        with chat_container:
            print(f"> Human: {user_input}")
            st.write(f"**You:** {user_input}")
            response = chatbot.process_user_input(user_input)

            print(f"< AI: {response.content}")
            print(f"< AI response details: {response}")
            st.write(f"**AI:** {response.content}")
            

draw_chat_ui()
