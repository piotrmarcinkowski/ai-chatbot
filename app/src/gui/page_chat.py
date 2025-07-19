import streamlit as st

from gui.view_model import chatbot_instance

def draw_chat_ui():
    st.markdown("# 💬 Chat")

    # Initialize the chatbot instance
    chatbot = chatbot_instance()

    # Add "New chat" button to the sidebar
    if st.sidebar.button("New chat"):
        chatbot.new_chat()

    # Main chat container
    chat_container = st.container(height=600)
    with chat_container:
        for message in chatbot.get_current_chat_messages():
            dispatch_message_draw(message, st=st)

    # Input form for user messages
    with st.form(key="chat_form", clear_on_submit=True, enter_to_submit=True):
        user_input = st.text_area("Type your message:", value=None, height=100, max_chars=500)
        submit_button = st.form_submit_button("Send", type="primary")

    # Handle form submission
    if submit_button and user_input:
        with chat_container:
            print(f"> Human: {user_input}")
            st.write(f"**You:** {user_input}")
            response = chatbot.process_user_input(user_input)

            response_content = response['messages'][-1].content if response['messages'] else "No response generated."
            print(f"< AI: {response_content}")
            print(f"< AI response details: {response}")
            st.write(f"**AI:** {response_content}")

def dispatch_message_draw(message, st):
    """
    Dispatches the rendering of a message based on its type.
    """
    if message.type == "human":
        render_human_message(message, st)
    elif message.type == "ai":
        render_ai_message(message, st)
    elif message.type == "tool":
        render_tool_message(message, st)
    else:
        st.write(f"**Unknown Message Type:** {message.type} - {message.content}")

def render_human_message(message, st):
    """
    Renders a human message in the chat UI.
    """
    st.write(f"**You:** {message.content}")

def render_ai_message(message, st):
    """
    Renders an AI message in the chat UI.
    """
    if hasattr(message, 'tool_calls') and message.tool_calls:
        with st.expander(label="Planned Tool Calls", expanded=False):
            for tool_call in message.tool_calls:
                with st.expander(label=f"Tool Call: {tool_call.get('name', '_')}", expanded=False):
                    st.write(tool_call)
    else:
        st.write(f"**AI:** {message.content}")

def render_tool_message(message, st):
    """
    Renders a tool message in the chat UI.
    """
    with st.expander(label=f"Tool Call: {message.name}", expanded=False):
        st.write(f"Tool name: {message.name}")
        st.write(f"Tool call_id: {message.tool_call_id}")
        st.write("Content:")
        with st.container(border=True):
            st.text(message.content)

draw_chat_ui()
