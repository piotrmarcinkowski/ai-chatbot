import streamlit as st

st.set_page_config(page_title="AI Chatbot", layout="wide")

# Define the pages
chat_page = st.Page("gui/chat.py", title="Home", icon="💬")
history_page = st.Page("gui/history.py", title="History", icon="📜")

# Set up navigation
pg = st.navigation([chat_page, history_page])

# Run the selected page
pg.run()