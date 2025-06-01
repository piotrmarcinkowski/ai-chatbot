import streamlit as st

print("Starting the AI Chatbot application...")
st.set_page_config(page_title="AI Chatbot", layout="wide")

# Define the pages
chat_page = st.Page("gui/page_chat.py", title="Chat", icon="💬")
archive_page = st.Page("gui/page_archive.py", title="Chat Archive", icon="📜")
diag_page = st.Page("gui/page_diag.py", title="Bot diagnostics", icon="🔍")

# Set up navigation
pg = st.navigation([chat_page, archive_page, diag_page])

# Run the selected page
pg.run()