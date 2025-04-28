import streamlit as st
from langchain.chains.question_answering import load_qa_chain
import os
import sys

from persistence import load_knowledge_vectors
from llm import load_llm

vectors = load_knowledge_vectors()

print("Creating llm instance")
llm = load_llm()
print("Creating chain")
chain = load_qa_chain(llm, chain_type="stuff")

st.set_page_config(page_title="AI Chatbot", layout="wide")

with st.sidebar:
    st.header("Previous chats")
    st.write("- To be implemented")

st.title("AI Chatbot")
chat_container = st.container()

with st.form(key="chat_form"):
    # user_input = st.text_area("Type your message:", height=100, max_chars=500)
    default_text = "Hello, introduce yourself"
    user_input = st.text_area("Type your message:", value=default_text, height=100, max_chars=500)
    submit_button = st.form_submit_button("Send")

if submit_button and user_input:
    with chat_container:
        st.write(f"**You:** {user_input}")
        match = vectors.similarity_search(user_input)
        response = chain.run(input_documents = match, question=user_input)
        st.write(f"**Bot:** {response}")

