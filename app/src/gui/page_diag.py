import streamlit as st

from gui.view_model import chatbot_instance

def draw_diag_ui():
    st.markdown("# 🔍 Bot diagnostics")
    # session_ids = init_chat_archive().get_archived_session_ids(limit=10)
    # session_ids
    
    # Initialize the chatbot instance
    chatbot = chatbot_instance()

    # Input form for user messages
    with st.form(key="vector_search_form", clear_on_submit=True, enter_to_submit=True):
        user_input = st.text_area("Search for related topics in full chat history:", value=None, height=100, max_chars=500)
        submit_button = st.form_submit_button("Search", type="primary")

    results_container = st.container(height=600)
    
    # Handle form submission
    if submit_button and user_input:
        with results_container:
            print(f"> Search query: {user_input}")
            response = chatbot.search_in_vector_store(user_input, limit=10)
            print(f"Results found: {len(response)}")
            for message in response:
                print(message)
                st.write(message.content)
                # if message.type == "human":
                #     st.write(f"**You:** {message.content}")
                # else:
                #     st.write(f"**AI:** {message.content}")


draw_diag_ui()
