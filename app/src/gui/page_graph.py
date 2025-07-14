import streamlit as st

from gui.view_model import chatbot_instance

@st.cache_data
def create_graph_image():
    chatbot = chatbot_instance()
    graph_image = chatbot.graph.get_graph().draw_mermaid_png()
    return graph_image

def draw_graph_ui():
    st.markdown("# 📊 State Graph View")
    graph_image = create_graph_image()
    st.image(graph_image)

draw_graph_ui()
