import streamlit as st

from gui.view_model import chatbot_instance

def draw_memory_ui():
    st.markdown("# 🔍 Bot memory")
    
    # Initialize the chatbot instance
    chatbot = chatbot_instance()

    st.button("Refresh vector store (costs tokens)", on_click=chatbot.refresh_vector_store, type="secondary")

    # Input form for user messages
    with st.form(key="vector_search_form", clear_on_submit=True, enter_to_submit=True):
        user_input = st.text_area("Search for related topics in vector store:", value=None, height=100, max_chars=500)
        submit_button = st.form_submit_button("Search", type="primary")

    results_container = st.container(height=600)
    
    # Handle form submission
    if submit_button and user_input:
        with results_container:
            print(f"GUI: > Search query: {user_input}")
            response = chatbot.search_memory_for_context(user_input, top_k=10)
            print(f"GUI: < Results found: {len(response)}")
            for message in response:
                print(f"GUI: {message}")
                st.write(message)
                # if message.type == "human":
                #     st.write(f"**You:** {message.content}")
                # else:
                #     st.write(f"**AI:** {message.content}")


draw_memory_ui()
